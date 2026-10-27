# Phase 6: Unigram Algorithm & Dual-Model Comparison — Plan

Numbered task groups for Phase 6 implementation.

## 1. Rust Unigram Trainer Integration (`src/trainer.rs`)

- Add `UnigramTrainingConfig`:
  - `vocab_size: usize`
  - `special_tokens: Vec<String>`
  - `seed: u64`
- Implement `train_unigram`:
  - Setup `Tokenizer::new(Unigram::default())`.
  - Normalizer: `build_kwa_normalizer_sequence()`.
  - Pre-tokenizer & Decoder: `Metaspace` or byte-level fallback.
  - Build `UnigramTrainerBuilder` and train from corpus files.

## 2. Python Bridge & CLI Update (`src/lib.rs`, `python/leke/trainer.py`)

- Expose `train_unigram_model` in PyO3.
- Update `python/leke/trainer.py` to add `train_unigram` and `--algorithm {bpe,unigram}` CLI option.

## 3. Train Unigram Model and Comparative Evaluation

- Train `models/unigram-8k` on `data/splits/pooled_train.txt`.
- Run evaluation harness on both `models/bpe-8k` and `models/unigram-8k`.
- Write comparative decision document `specs/algorithm_decision.md`.

## 4. Test Suite Implementation (`tests/test_unigram.py`)

- Test Unigram model training, tokenization, and roundtrip decoding.
- Verify 0% `<unk>` rate.

## 5. Validation Pass

- Run `cargo test` and `uv run pytest`.

## 6. PR

- Commit, push `unigram-comparison`, open PR, and merge into `main`.
