pub mod normalizer;
pub mod py_tokenizer;
pub mod trainer;

use normalizer::KwaNormalizer;
use py_tokenizer::{PyEncoding, PyLekeTokenizer};
use trainer::{train_bpe, BpeTrainingConfig, save_tokenizer_bundle};
use std::path::{Path, PathBuf};
use pyo3::prelude::*;

/// Python wrapper for KwaNormalizer
#[pyclass(name = "KwaNormalizer")]
pub struct PyKwaNormalizer {
    inner: KwaNormalizer,
}

#[pymethods]
impl PyKwaNormalizer {
    #[new]
    #[pyo3(signature = (strip_accents=false, collapse_whitespace=true, custom_mappings_json=None))]
    fn new(
        strip_accents: bool,
        collapse_whitespace: bool,
        custom_mappings_json: Option<&str>,
    ) -> PyResult<Self> {
        let inner = if let Some(json_str) = custom_mappings_json {
            KwaNormalizer::from_json(json_str, strip_accents, collapse_whitespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Invalid mapping JSON: {e}")))?
        } else {
            KwaNormalizer::new(strip_accents, collapse_whitespace)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to initialize: {e}")))?
        };
        Ok(Self { inner })
    }

    /// Normalizes a single string according to Kwa normalization rules.
    fn normalize(&self, text: &str) -> String {
        self.inner.normalize_str(text)
    }

    /// Normalizes a batch of strings.
    fn normalize_batch(&self, texts: Vec<String>) -> Vec<String> {
        texts.into_iter().map(|t| self.inner.normalize_str(&t)).collect()
    }
}

/// Convenience standalone function for normalizing text.
#[pyfunction]
#[pyo3(signature = (text, strip_accents=false, collapse_whitespace=true))]
fn normalize(text: &str, strip_accents: bool, collapse_whitespace: bool) -> PyResult<String> {
    let norm = KwaNormalizer::new(strip_accents, collapse_whitespace)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    Ok(norm.normalize_str(text))
}

/// Returns the version string of the leke engine.
pub fn leke_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[pyfunction]
fn version() -> PyResult<&'static str> {
    Ok(leke_version())
}

/// Trains a Byte-Level BPE tokenizer on corpus files and saves tokenizer.json and training_receipt.json.
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
    let files: Vec<PathBuf> = corpus_paths.into_iter().map(PathBuf::from).collect();
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

    let (tok, receipt) = train_bpe(&files, &config)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Training failed: {e}")))?;

    let out_path = Path::new(&output_dir);
    save_tokenizer_bundle(&tok, &receipt, out_path)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Failed to save tokenizer: {e}")))?;

    let receipt_json = serde_json::to_string(&receipt)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;

    Ok(receipt_json)
}

#[pymodule]
fn _leke(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyKwaNormalizer>()?;
    m.add_class::<PyEncoding>()?;
    m.add_class::<PyLekeTokenizer>()?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(normalize, m)?)?;
    m.add_function(wrap_pyfunction!(train_bpe_model, m)?)?;
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
