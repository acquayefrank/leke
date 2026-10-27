# Phase 6: Unigram Algorithm & Dual-Model Comparison — Validation

Criteria to verify Phase 6 implementation.

## 1. Unigram Model Validity

- `models/unigram-8k/tokenizer.json` and `training_receipt.json` exist and validate.
- `LekeTokenizer.from_file("models/unigram-8k/tokenizer.json")` encodes and decodes sample phrases with 0 errors.

## 2. Comparative Matrix & Decision Doc

- `specs/algorithm_decision.md` exists, containing side-by-side comparison tables across all 4 Kwa languages evaluating:
  - Fertility
  - Excessive split rate (>2)
  - Unknown rate
  - Compression ratio
- Clear architectural conclusion logged selecting the winner for the final production release.

## 3. Test Suite Execution

- `cargo test` and `uv run pytest tests/test_unigram.py` pass 100%.

## Merge Criteria

All criteria verified. Open PR and merge to `main`.
