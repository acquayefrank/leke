# Phase 8: Packaging, Model Card & Hugging Face Release — Validation

Criteria to verify Phase 8 implementation.

## 1. Licensing & Audits

- `LICENSE` exists and contains Apache-2.0 terms.
- `specs/corpus_licenses.md` exists with attribution and license terms for all four sources.

## 2. Model Bundle Completeness

- `models/bpe-8k/` contains:
  - `tokenizer.json`
  - `tokenizer_config.json`
  - `special_tokens_map.json`
  - `training_receipt.json`
  - `README.md` (Hugging Face Model Card)
- `transformers.AutoTokenizer.from_pretrained("models/bpe-8k")` loads smoothly without warnings.

## 3. Release Wheel Verification

- `maturin build --release` produces compliant `.whl` in `target/wheels/`.

## 4. Documentation

- Root `README.md` is complete, beautifully formatted, and free of placeholders.

## Merge Criteria

All criteria verified. Open PR and merge to `main`.
