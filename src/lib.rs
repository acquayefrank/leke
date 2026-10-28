//! High-performance subword tokenizer and linguistic normalizer for Kwa languages.
//!
//! # Architecture & Crate Overview
//! Leke is an optimized, production-grade tokenization engine specifically engineered
//! for the Niger-Congo Kwa language family (Akan/Twi, Ewe, Ga, and Fante).
//!
//! ## Submodules
//! - [`normalizer`]: Unicode NFC normalization, canonical character lookalike replacement,
//!   and diacritic management.
//! - [`trainer`]: High-throughput Byte-Level BPE and Unigram model training via Hugging Face
//!   `tokenizers`.
//! - [`py_tokenizer`]: Zero-copy PyO3 bindings exposing fast encoding and decoding to Python.
//!
//! ## PyO3 Python Extension
//! Compiled as a native Python extension module (`_leke`) using Maturin and PyO3 with
//! stable ABI (`abi3-py39`).

pub mod normalizer;
pub mod py_tokenizer;
pub mod trainer;

use normalizer::KwaNormalizer;
use py_tokenizer::{PyEncoding, PyLekeTokenizer};
use trainer::{train_bpe, BpeTrainingConfig, save_tokenizer_bundle};
use std::path::{Path, PathBuf};
use pyo3::prelude::*;

/// Python wrapper class for [`KwaNormalizer`].
///
/// Exposed to Python as `_leke.KwaNormalizer`.
#[pyclass(name = "KwaNormalizer")]
pub struct PyKwaNormalizer {
    inner: KwaNormalizer,
}

#[pymethods]
impl PyKwaNormalizer {
    /// Creates a new `PyKwaNormalizer` instance.
    ///
    /// # Arguments
    /// * `strip_accents`: If `true`, strips phonemic tone accents and diacritical marks.
    /// * `collapse_whitespace`: If `true`, collapses repeated whitespace into a single space.
    /// * `custom_mappings_json`: Optional JSON string containing custom replacement rules.
    #[new]
    #[pyo3(signature = (strip_accents=false, collapse_whitespace=true, custom_mappings_json=None))]
    fn new(
        strip_accents: bool,
        collapse_whitespace: bool,
        custom_mappings_json: Option<&str>,
    ) -> PyResult<Self> {
        // Step 1: Initialize inner KwaNormalizer using custom JSON if provided, otherwise defaults.
        let inner = if let Some(json_str) = custom_mappings_json {
            KwaNormalizer::from_json(json_str, strip_accents, collapse_whitespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid mapping JSON: {e}")))?
        } else {
            KwaNormalizer::new(strip_accents, collapse_whitespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to initialize: {e}")))?
        };
        // Step 2: Return Python-wrapped struct.
        Ok(Self { inner })
    }

    /// Normalizes a single string according to Kwa normalization rules.
    fn normalize(&self, text: &str) -> String {
        // Step 1: Delegate normalization to inner Rust KwaNormalizer.
        self.inner.normalize_str(text)
    }

    /// Normalizes a batch of strings concurrently.
    fn normalize_batch(&self, texts: Vec<String>) -> Vec<String> {
        // Step 1: Map normalization across input text vector.
        texts.into_iter().map(|t| self.inner.normalize_str(&t)).collect()
    }
}

/// Convenience standalone function for normalizing text in Python.
///
/// # Arguments
/// * `text`: Input text string to normalize.
/// * `strip_accents`: Whether to strip tone accents. Default: `false`.
/// * `collapse_whitespace`: Whether to collapse runs of whitespace. Default: `true`.
///
/// # Returns
/// Normalized string.
#[pyfunction]
#[pyo3(signature = (text, strip_accents=false, collapse_whitespace=true))]
fn normalize(text: &str, strip_accents: bool, collapse_whitespace: bool) -> PyResult<String> {
    // Step 1: Instantiate temporary KwaNormalizer with specified configuration.
    let norm = KwaNormalizer::new(strip_accents, collapse_whitespace)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    // Step 2: Execute normalization pipeline on input text.
    Ok(norm.normalize_str(text))
}

/// Returns the compile-time Cargo package version string of the engine.
///
/// # Examples
/// ```
/// use _leke::leke_version;
///
/// assert_eq!(leke_version(), "0.1.0");
/// ```
pub fn leke_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Python-exposed version query function.
#[pyfunction]
fn version() -> PyResult<&'static str> {
    Ok(leke_version())
}

/// Trains a Byte-Level BPE tokenizer on corpus files and saves tokenizer.json and training_receipt.json.
///
/// # Arguments
/// * `corpus_paths`: Vector of file paths to training corpora.
/// * `output_dir`: Directory path where `tokenizer.json` and `training_receipt.json` will be written.
/// * `vocab_size`: Target vocabulary size. Default: 8,192.
/// * `min_frequency`: Minimum pair frequency threshold. Default: 1.
/// * `special_tokens`: Optional custom special token list.
/// * `seed`: Random seed for training determinism. Default: 42.
///
/// # Returns
/// Serialized JSON string of the [`TrainingReceipt`].
#[pyfunction]
#[pyo3(signature = (corpus_paths, output_dir, vocab_size=8192, min_frequency=1, special_tokens=None, seed=42))]
fn train_bpe_model(
    corpus_paths: Vec<String>,
    output_dir: String,
    vocab_size: usize,
    min_frequency: u32,
    special_tokens: Option<Vec<String>>,
    seed: u64,
) -> PyResult<String> {
    // Step 1: Convert path strings to PathBuf instances.
    let files: Vec<PathBuf> = corpus_paths.into_iter().map(PathBuf::from).collect();

    // Step 2: Build BpeTrainingConfig.
    let config = BpeTrainingConfig {
        vocab_size,
        min_frequency,
        special_tokens: special_tokens.unwrap_or_else(|| {
            vec![
                "<unk>".to_string(),
                "<s>".to_string(),
                "</s>".to_string(),
                "<pad>".to_string(),
                "<mask>".to_string(),
            ]
        }),
        strip_accents: false,
        seed,
    };

    // Step 3: Run Byte-Level BPE training routine.
    let (tok, receipt) = train_bpe(&files, &config)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Training failed: {e}")))?;

    // Step 4: Save tokenizer bundle to target directory.
    let out_path = Path::new(&output_dir);
    save_tokenizer_bundle(&tok, &receipt, out_path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to save tokenizer: {e}")))?;

    // Step 5: Serialize receipt to JSON string and return to caller.
    let receipt_json = serde_json::to_string(&receipt)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    Ok(receipt_json)
}

/// Trains a Unigram tokenizer on corpus files and saves tokenizer.json and training_receipt.json.
///
/// # Arguments
/// * `corpus_paths`: Vector of file paths to training corpora.
/// * `output_dir`: Directory path where bundle files will be saved.
/// * `vocab_size`: Target vocabulary size. Default: 8,192.
/// * `special_tokens`: Optional custom special token list.
/// * `seed`: Random seed. Default: 42.
///
/// # Returns
/// Serialized JSON string of the [`TrainingReceipt`].
#[pyfunction]
#[pyo3(signature = (corpus_paths, output_dir, vocab_size=8192, special_tokens=None, seed=42))]
fn train_unigram_model(
    corpus_paths: Vec<String>,
    output_dir: String,
    vocab_size: usize,
    special_tokens: Option<Vec<String>>,
    seed: u64,
) -> PyResult<String> {
    // Step 1: Convert path strings to PathBuf instances.
    let files: Vec<PathBuf> = corpus_paths.into_iter().map(PathBuf::from).collect();

    // Step 2: Build UnigramTrainingConfig.
    let config = trainer::UnigramTrainingConfig {
        vocab_size,
        special_tokens: special_tokens.unwrap_or_else(|| {
            vec![
                "<unk>".to_string(),
                "<s>".to_string(),
                "</s>".to_string(),
                "<pad>".to_string(),
                "<mask>".to_string(),
            ]
        }),
        seed,
    };

    // Step 3: Run Unigram EM training routine.
    let (tok, receipt) = trainer::train_unigram(&files, &config)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Unigram training failed: {e}")))?;

    // Step 4: Save tokenizer bundle to target directory.
    let out_path = Path::new(&output_dir);
    save_tokenizer_bundle(&tok, &receipt, out_path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to save tokenizer: {e}")))?;

    // Step 5: Serialize receipt to JSON string and return to caller.
    let receipt_json = serde_json::to_string(&receipt)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    Ok(receipt_json)
}

/// PyO3 module initialization function registering classes and functions into `_leke`.
#[pymodule]
fn _leke(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyKwaNormalizer>()?;
    m.add_class::<PyEncoding>()?;
    m.add_class::<PyLekeTokenizer>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(normalize, m)?)?;
    m.add_function(wrap_pyfunction!(train_bpe_model, m)?)?;
    m.add_function(wrap_pyfunction!(train_unigram_model, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert_eq!(leke_version(), "0.1.0");
    }
}
