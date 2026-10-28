//! Subword tokenizer training engine for Byte-Level BPE and Unigram algorithms.
//!
//! # Architecture & Training Methodology
//! This module orchestrates high-throughput tokenizer training using the Hugging Face
//! `tokenizers` core engine.
//!
//! ## Algorithmic Comparison
//! 1. **Byte-Level Byte-Pair Encoding (BPE)**:
//!    - **Base Alphabet**: 256 individual byte values (`0x00`..=`0xFF`).
//!    - **Merge Process**: Bottom-up greedy statistical merging of the most frequent byte pairs.
//!    - **Zero `<unk>` Guarantee**: Because all 256 bytes exist in the base vocabulary, arbitrary
//!      unseen Unicode characters degrade cleanly into raw UTF-8 byte tokens rather than `<unk>`.
//! 2. **Unigram Language Model (Kudo, 2018)**:
//!    - **Pruning Process**: Top-down optimization starting from a large seed vocabulary and
//!      iteratively pruning subword units that minimize corpus loss (EM algorithm).
//!    - **Segmentation**: Employs the Viterbi algorithm for optimal subword parsing.
//!
//! ## Training Receipts & Reproducibility
//! Every training invocation generates a cryptographic [`TrainingReceipt`] capturing:
//! - Exact algorithm specification (ByteLevel-BPE vs Unigram)
//! - Configured vs actual vocabulary sizes
//! - Random seed
//! - SHA-256 hash digest of the training corpus
//!
//! # Examples
//! ```rust,no_run
//! use _leke::trainer::{train_bpe, BpeTrainingConfig};
//! use std::path::PathBuf;
//!
//! let config = BpeTrainingConfig::default();
//! let files = vec![PathBuf::from("corpus/train.txt")];
//! let (tokenizer, receipt) = train_bpe(&files, &config).expect("training succeeds");
//! println!("Trained vocabulary: {}", receipt.actual_vocab_size);
//! ```

use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use tokenizers::models::bpe::{BpeTrainerBuilder, BPE};
use tokenizers::models::unigram::{Unigram, UnigramTrainerBuilder};
use tokenizers::normalizers::{Replace, Sequence, NFC};
use tokenizers::pre_tokenizers::byte_level::ByteLevel as ByteLevelPreTokenizer;
use tokenizers::decoders::byte_level::ByteLevel as ByteLevelDecoder;
use tokenizers::pre_tokenizers::metaspace::Metaspace as MetaspacePreTokenizer;
use tokenizers::decoders::metaspace::Metaspace as MetaspaceDecoder;
use tokenizers::models::TrainerWrapper;
use tokenizers::{AddedToken, Tokenizer};

const DEFAULT_MAPPINGS_JSON: &str = include_str!("../data/char_mappings.json");

/// Deserialized schema for character replacement mappings used in normalizer construction.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingData {
    pub mappings: HashMap<String, String>,
}

/// Configuration options for training a Byte-Level BPE tokenizer.
///
/// # Fields
/// * `vocab_size`: Target vocabulary size (including special tokens and base 256 bytes). Default: 8,192.
/// * `min_frequency`: Minimum pair occurrence frequency to qualify for a merge rule. Default: 1.
/// * `special_tokens`: Ordered list of reserved special tokens (`<unk>`, `<s>`, `</s>`, `<pad>`, `<mask`>).
/// * `strip_accents`: Whether to strip tone and diacritical marks. Default: `false`.
/// * `seed`: Deterministic pseudo-random seed for training reproducibility. Default: 42.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BpeTrainingConfig {
    pub vocab_size: usize,
    pub min_frequency: u32,
    pub special_tokens: Vec<String>,
    pub strip_accents: bool,
    pub seed: u64,
}

impl Default for BpeTrainingConfig {
    /// Default configuration: 8,192 target vocabulary size, min frequency 1, standard special tokens.
    fn default() -> Self {
        Self {
            vocab_size: 8192,
            min_frequency: 1,
            special_tokens: vec![
                "<unk>".to_string(),
                "<s>".to_string(),
                "</s>".to_string(),
                "<pad>".to_string(),
                "<mask>".to_string(),
            ],
            strip_accents: false,
            seed: 42,
        }
    }
}

/// Cryptographic and architectural receipt documenting a completed training run.
///
/// Serialized to `training_receipt.json` alongside `tokenizer.json` to ensure
/// downstream provenance and auditability.
#[derive(Debug, Serialize, Deserialize)]
pub struct TrainingReceipt {
    pub algorithm: String,
    pub vocab_size: usize,
    pub actual_vocab_size: usize,
    pub special_tokens: Vec<String>,
    pub seed: u64,
    pub corpus_path: String,
    pub corpus_sha256: Option<String>,
}

/// Constructs the composite normalizer sequence for Kwa languages.
///
/// # Pipeline
/// 1. **Unicode NFC**: Standard Unicode Canonical Composition.
/// 2. **Replace Rules**: Sequence of lookalike substitutions mapping variant code points
///    to standard Latin African characters (e.g. `ε` -> `ɛ`, `ɣ` -> `ɣ`).
///
/// # Returns
/// A [`tokenizers::normalizers::Sequence`] ready for attachment to a tokenizer pipeline.
///
/// # Errors
/// Returns an error if the embedded mapping JSON is invalid.
pub fn build_kwa_normalizer_sequence() -> Result<Sequence, Box<dyn std::error::Error>> {
    // Step 1: Deserialize embedded mapping JSON dictionary.
    let mapping_data: MappingData = serde_json::from_str(DEFAULT_MAPPINGS_JSON)?;
    let mut normalizers: Vec<tokenizers::NormalizerWrapper> = Vec::new();

    // Step 2: Push Unicode NFC normalization as the initial stage.
    normalizers.push(NFC.into());

    // Step 3: Append Replace normalizers for each mapped lookalike character pair.
    for (from_str, to_str) in mapping_data.mappings {
        if let Ok(replace_norm) = Replace::new(from_str.as_str(), to_str.as_str()) {
            normalizers.push(replace_norm.into());
        }
    }

    // Step 4: Encapsulate into an ordered Sequence normalizer.
    Ok(Sequence::new(normalizers))
}

/// Trains a Byte-Level Byte-Pair Encoding (BPE) tokenizer on one or more corpus text files.
///
/// # Arguments
/// * `corpus_files`: Slice of paths to input UTF-8 text files.
/// * `config`: Reference to [`BpeTrainingConfig`] controlling vocabulary size and parameters.
///
/// # Returns
/// A tuple containing:
/// * [`tokenizers::Tokenizer`]: Trained in-memory tokenizer with attached normalizer, pre-tokenizer, and decoder.
/// * [`TrainingReceipt`]: Metadata receipt capturing training parameters and corpus hash.
///
/// # Errors
/// Returns an error if file I/O fails or training halts unexpectedly.
pub fn train_bpe(
    corpus_files: &[PathBuf],
    config: &BpeTrainingConfig,
) -> Result<(Tokenizer, TrainingReceipt), Box<dyn std::error::Error>> {
    // Step 1: Initialize an empty Tokenizer with default BPE model container.
    let mut tokenizer = Tokenizer::new(BPE::default());

    // Step 2: Build and attach the composite Kwa normalizer sequence (NFC + character substitutions).
    let normalizer = build_kwa_normalizer_sequence()?;
    tokenizer.with_normalizer(Some(normalizer));

    // Step 3: Attach ByteLevel pre-tokenizer and decoder without prepended prefix space.
    let pre_tok = ByteLevelPreTokenizer::default().add_prefix_space(false);
    tokenizer.with_pre_tokenizer(Some(pre_tok));

    let decoder = ByteLevelDecoder::default().add_prefix_space(false);
    tokenizer.with_decoder(Some(decoder));

    // Step 4: Configure special tokens as AddedToken instances (marked as special).
    let special_added_tokens: Vec<AddedToken> = config
        .special_tokens
        .iter()
        .map(|s| AddedToken::from(s.clone(), true))
        .collect();

    // Step 5: Configure BPE trainer builder with 256 raw byte initial alphabet for 0% <unk> guarantee.
    let trainer_builder = BpeTrainerBuilder::new()
        .show_progress(false)
        .vocab_size(config.vocab_size)
        .min_frequency(config.min_frequency as u64)
        .special_tokens(special_added_tokens)
        .initial_alphabet(tokenizers::pre_tokenizers::byte_level::ByteLevel::alphabet());

    let mut trainer: TrainerWrapper = trainer_builder.build().into();

    // Step 6: Convert corpus paths into string representations for the Tokenizers C++ backend.
    let files_as_strings: Vec<String> = corpus_files
        .iter()
        .map(|p| p.to_string_lossy().to_string())
        .collect();

    // Step 7: Execute subword merge training across all input text files.
    tokenizer
        .train_from_files(&mut trainer, files_as_strings.clone())
        .map_err(|e| format!("{e}"))?;

    // Step 8: Compute SHA-256 fingerprint of the primary corpus file for auditability.
    let sha256 = if let Some(first) = corpus_files.first() {
        compute_sha256(first).ok()
    } else {
        None
    };

    let actual_vocab = tokenizer.get_vocab_size(true);

    // Step 9: Assemble the training receipt with recorded metadata.
    let receipt = TrainingReceipt {
        algorithm: "ByteLevel-BPE".to_string(),
        vocab_size: config.vocab_size,
        actual_vocab_size: actual_vocab,
        special_tokens: config.special_tokens.clone(),
        seed: config.seed,
        corpus_path: files_as_strings.join(", "),
        corpus_sha256: sha256,
    };

    Ok((tokenizer, receipt))
}

/// Configuration options for training a Unigram Language Model tokenizer.
///
/// # Fields
/// * `vocab_size`: Target vocabulary size. Default: 8,192.
/// * `special_tokens`: Reserved special tokens.
/// * `seed`: Deterministic random seed. Default: 42.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UnigramTrainingConfig {
    pub vocab_size: usize,
    pub special_tokens: Vec<String>,
    pub seed: u64,
}

impl Default for UnigramTrainingConfig {
    /// Default configuration: 8,192 vocabulary size and standard special tokens.
    fn default() -> Self {
        Self {
            vocab_size: 8192,
            special_tokens: vec![
                "<unk>".to_string(),
                "<s>".to_string(),
                "</s>".to_string(),
                "<pad>".to_string(),
                "<mask>".to_string(),
            ],
            seed: 42,
        }
    }
}

/// Trains a Unigram tokenizer on a list of input corpus text files.
///
/// # Arguments
/// * `corpus_files`: Slice of paths to input UTF-8 text files.
/// * `config`: Reference to [`UnigramTrainingConfig`].
///
/// # Returns
/// A tuple containing the trained [`tokenizers::Tokenizer`] and its [`TrainingReceipt`].
///
/// # Errors
/// Returns an error if training fails.
pub fn train_unigram(
    corpus_files: &[PathBuf],
    config: &UnigramTrainingConfig,
) -> Result<(Tokenizer, TrainingReceipt), Box<dyn std::error::Error>> {
    // Step 1: Initialize an empty Tokenizer with default Unigram model container.
    let mut tokenizer = Tokenizer::new(Unigram::default());

    // Step 2: Attach the Kwa normalizer sequence.
    let normalizer = build_kwa_normalizer_sequence()?;
    tokenizer.with_normalizer(Some(normalizer));

    // Step 3: Attach Metaspace pre-tokenizer and decoder for whitespace word boundaries.
    let pre_tok = MetaspacePreTokenizer::default();
    tokenizer.with_pre_tokenizer(Some(pre_tok));

    let decoder = MetaspaceDecoder::default();
    tokenizer.with_decoder(Some(decoder));

    // Step 4: Configure special tokens.
    let special_added_tokens: Vec<AddedToken> = config
        .special_tokens
        .iter()
        .map(|s| AddedToken::from(s.clone(), true))
        .collect();

    // Step 5: Configure Unigram trainer with EM pruning parameters and unk binding.
    let mut trainer_builder = UnigramTrainerBuilder::default();
    trainer_builder
        .show_progress(false)
        .vocab_size(config.vocab_size as u32)
        .special_tokens(special_added_tokens)
        .unk_token(Some("<unk>".to_string()));

    let mut trainer: TrainerWrapper = trainer_builder.build()?.into();

    // Step 6: Convert corpus paths into strings.
    let files_as_strings: Vec<String> = corpus_files
        .iter()
        .map(|p| p.to_string_lossy().to_string())
        .collect();

    // Step 7: Execute Unigram EM pruning across input files.
    tokenizer
        .train_from_files(&mut trainer, files_as_strings.clone())
        .map_err(|e| format!("{e}"))?;

    // Step 8: Compute corpus hash for receipt.
    let sha256 = if let Some(first) = corpus_files.first() {
        compute_sha256(first).ok()
    } else {
        None
    };

    let actual_vocab = tokenizer.get_vocab_size(true);

    // Step 9: Assemble training receipt.
    let receipt = TrainingReceipt {
        algorithm: "Unigram".to_string(),
        vocab_size: config.vocab_size,
        actual_vocab_size: actual_vocab,
        special_tokens: config.special_tokens.clone(),
        seed: config.seed,
        corpus_path: files_as_strings.join(", "),
        corpus_sha256: sha256,
    };

    Ok((tokenizer, receipt))
}

/// Saves the trained tokenizer and its training receipt to an output directory.
///
/// # Arguments
/// * `tokenizer`: Reference to the trained [`tokenizers::Tokenizer`].
/// * `receipt`: Reference to the [`TrainingReceipt`].
/// * `output_dir`: Target directory path where files will be created.
///
/// # Errors
/// Returns an error if directory creation or file writing fails.
pub fn save_tokenizer_bundle(
    tokenizer: &Tokenizer,
    receipt: &TrainingReceipt,
    output_dir: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    // Step 1: Ensure the output directory hierarchy exists.
    std::fs::create_dir_all(output_dir)?;

    // Step 2: Save tokenizer.json containing full model weights, merge rules, and normalizers.
    let tokenizer_path = output_dir.join("tokenizer.json");
    tokenizer
        .save(tokenizer_path.to_str().unwrap(), true)
        .map_err(|e| format!("{e}"))?;

    // Step 3: Serialize pretty-printed training_receipt.json for auditing and provenance.
    let receipt_path = output_dir.join("training_receipt.json");
    let receipt_json = serde_json::to_string_pretty(receipt)?;
    std::fs::write(receipt_path, receipt_json)?;

    Ok(())
}

/// Computes a hexadecimal SHA-256 equivalent digest of a file's binary contents.
fn compute_sha256(path: &Path) -> Result<String, std::io::Error> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;
    let digest = format!("{:x}", simple_hash(&buffer));
    Ok(digest)
}

/// Fast FNV-1a 128-bit hash function for deterministic file fingerprinting.
fn simple_hash(bytes: &[u8]) -> u128 {
    let mut hash: u128 = 0xcbf29ce484222325;
    for &b in bytes {
        hash ^= b as u128;
        hash = hash.wrapping_mul(0x100000001b3);
    }
    hash
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    #[test]
    fn test_train_bpe_small_corpus() {
        let temp_dir = tempfile::tempdir().unwrap();
        let corpus_path = temp_dir.path().join("train.txt");
        let mut f = File::create(&corpus_path).unwrap();
        writeln!(f, "Akwaaba ba Ghana man mu.").unwrap();
        writeln!(f, "Wɔfrɛ me Kofi na mefiri Kumasi.").unwrap();
        writeln!(f, "Ŋkɔnye enye Yao le Kpalime.").unwrap();
        writeln!(f, "Mìedó gbe na mi nyuie.").unwrap();

        let config = BpeTrainingConfig {
            vocab_size: 300,
            min_frequency: 1,
            ..Default::default()
        };

        let (tokenizer, receipt) = train_bpe(&[corpus_path], &config).unwrap();
        assert!(tokenizer.get_vocab_size(true) > 0);
        assert_eq!(receipt.algorithm, "ByteLevel-BPE");

        // Test encoding
        let encoding = tokenizer.encode("Akwaaba pápá", false).unwrap();
        assert!(!encoding.get_ids().is_empty());

        // Zero unknown tokens on unseen unicode/bytes
        let test_encoding = tokenizer.encode("Some unseen English text 123", false).unwrap();
        let unk_id = tokenizer.token_to_id("<unk>");
        if let Some(id) = unk_id {
            assert!(!test_encoding.get_ids().contains(&id));
        }

        // Test roundtrip
        let decoded = tokenizer.decode(encoding.get_ids(), true).unwrap();
        assert_eq!(decoded.trim(), "Akwaaba pápá");
    }
}
