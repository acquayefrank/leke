# Phase 3: Byte-Level BPE Training Engine — Plan

Numbered task groups for Phase 3 implementation.

## 1. Rust Trainer Core (`src/trainer.rs`)

- Implement `BpeTrainingConfig`:
  - `vocab_size: usize`
  - `min_frequency: u32`
  - `special_tokens: Vec<String>`
  - `strip_accents: bool`
  - `seed: u64`
- Implement `train_bpe_tokenizer`:
  - Setup `TokenizerImpl` with empty `BPE` model.
  - Attach `KwaNormalizer` as the normalizer.
  - Attach `ByteLevel` pre-tokenizer.
  - Attach `ByteLevel` decoder.
  - Configure `BpeTrainerBuilder` with vocabulary target, min frequency, and special tokens (`<unk>`, `<s>`, `</s>`, `<pad>`, `<mask>`).
  - Train model on input corpus file paths.

## 2. Receipt Generation & Artifact Bundle

- Implement `TrainingReceipt`:
  - Record metadata: vocab size, algorithm, timestamp, corpus checksum, hyperparameters.
- Method to save output bundle:
  - `tokenizer.json`
  - `training_receipt.json`

## 3. Python Training Bridge & CLI

- Expose `train_bpe(corpus_path, output_dir, vocab_size=8192, ...)` via Python in `python/leke/trainer.py`.
- Add CLI runner: `python -m leke.trainer --corpus data/splits/pooled_train.txt --vocab-size 8192 --output-dir models/bpe-8k`.

## 4. Test Suite Implementation

- Rust unit tests in `src/trainer.rs`:
  - Train a small BPE tokenizer on sample lines.
  - Assert zero unknown tokens when encoding arbitrary Kwa text.
  - Verify round-trip decode(encode(text)) produces normalized text.
- Python tests in `tests/test_trainer.py`:
  - Test end-to-end training and receipt serialization.
  - Verify `tokenizer.json` loadable via Hugging Face `tokenizers.Tokenizer.from_file()`.

## 5. Validation Pass

- Run `cargo test` and `uv run pytest`.

## 6. PR

- Commit, push `bpe-training`, create PR, and merge into `main`.
