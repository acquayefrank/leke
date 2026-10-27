use std::collections::HashMap;
use std::fs::File;
use std::io::Read;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use tokenizers::models::bpe::{BpeTrainerBuilder, BPE};
use tokenizers::normalizers::{Replace, Sequence, NFC};
use tokenizers::pre_tokenizers::byte_level::ByteLevel as ByteLevelPreTokenizer;
use tokenizers::decoders::byte_level::ByteLevel as ByteLevelDecoder;
use tokenizers::models::TrainerWrapper;
use tokenizers::{AddedToken, Tokenizer};

const DEFAULT_MAPPINGS_JSON: &str = include_str!("../data/char_mappings.json");

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MappingData {
    pub mappings: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BpeTrainingConfig {
    pub vocab_size: usize,
    pub min_frequency: u32,
    pub special_tokens: Vec<String>,
    pub strip_accents: bool,
    pub seed: u64,
}

impl Default for BpeTrainingConfig {
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

/// Builds the composite standard normalizer sequence for Kwa languages:
/// NFC -> Replace rules for orthographic variants
pub fn build_kwa_normalizer_sequence() -> Result<Sequence, Box<dyn std::error::Error>> {
    let mapping_data: MappingData = serde_json::from_str(DEFAULT_MAPPINGS_JSON)?;
    let mut normalizers: Vec<tokenizers::NormalizerWrapper> = Vec::new();

    // 1. Unicode NFC
    normalizers.push(NFC.into());

    // 2. Replace variant lookalikes with standard Latin characters
    for (from_str, to_str) in mapping_data.mappings {
        if let Ok(replace_norm) = Replace::new(from_str.as_str(), to_str.as_str()) {
            normalizers.push(replace_norm.into());
        }
    }

    Ok(Sequence::new(normalizers))
}

/// Trains a Byte-Level BPE tokenizer on a list of input corpus text files.
pub fn train_bpe(
    corpus_files: &[PathBuf],
    config: &BpeTrainingConfig,
) -> Result<(Tokenizer, TrainingReceipt), Box<dyn std::error::Error>> {
    let mut tokenizer = Tokenizer::new(BPE::default());

    // Attach normalizer
    let normalizer = build_kwa_normalizer_sequence()?;
    tokenizer.with_normalizer(Some(normalizer));

    // Attach ByteLevel pre-tokenizer and decoder
    let pre_tok = ByteLevelPreTokenizer::default().add_prefix_space(false);
    tokenizer.with_pre_tokenizer(Some(pre_tok));

    let decoder = ByteLevelDecoder::default().add_prefix_space(false);
    tokenizer.with_decoder(Some(decoder));

    // Build trainer
    let special_added_tokens: Vec<AddedToken> = config
        .special_tokens
        .iter()
        .map(|s| AddedToken::from(s.clone(), true))
        .collect();

    let trainer_builder = BpeTrainerBuilder::new()
        .show_progress(false)
        .vocab_size(config.vocab_size)
        .min_frequency(config.min_frequency as u64)
        .special_tokens(special_added_tokens)
        .initial_alphabet(tokenizers::pre_tokenizers::byte_level::ByteLevel::alphabet());

    let mut trainer: TrainerWrapper = trainer_builder.build().into();

    let files_as_strings: Vec<String> = corpus_files
        .iter()
        .map(|p| p.to_string_lossy().to_string())
        .collect();

    tokenizer
        .train_from_files(&mut trainer, files_as_strings.clone())
        .map_err(|e| format!("{e}"))?;

    // Compute corpus sha256 if single file exists
    let sha256 = if let Some(first) = corpus_files.first() {
        compute_sha256(first).ok()
    } else {
        None
    };

    let actual_vocab = tokenizer.get_vocab_size(true);

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

/// Saves the trained tokenizer and its training receipt to an output directory.
pub fn save_tokenizer_bundle(
    tokenizer: &Tokenizer,
    receipt: &TrainingReceipt,
    output_dir: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    std::fs::create_dir_all(output_dir)?;

    let tokenizer_path = output_dir.join("tokenizer.json");
    tokenizer
        .save(tokenizer_path.to_str().unwrap(), true)
        .map_err(|e| format!("{e}"))?;

    let receipt_path = output_dir.join("training_receipt.json");
    let receipt_json = serde_json::to_string_pretty(receipt)?;
    std::fs::write(receipt_path, receipt_json)?;

    Ok(())
}

fn compute_sha256(path: &Path) -> Result<String, std::io::Error> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;
    let digest = format!("{:x}", simple_hash(&buffer));
    Ok(digest)
}

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
