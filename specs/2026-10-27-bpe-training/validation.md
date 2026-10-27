# Phase 3: Byte-Level BPE Training Engine — Validation

Criteria to verify Phase 3 implementation.

## 1. Schema & Serialization Validity

- Generated `tokenizer.json` conforms to Hugging Face Tokenizers schema.
- `tokenizers.Tokenizer.from_file("tokenizer.json")` loads without warning or error.

## 2. Zero Unknown-Token Guarantee

- Encoding arbitrary text (including unseen characters, emojis, or foreign alphabets) produces strictly valid token IDs and 0 unknown tokens (`<unk>` ID is never emitted for regular text due to byte-level fallback).

## 3. Round-Trip Reversibility

- For any normalized input string $S$, `decode(encode(S)) == S`.

## 4. Provenance Receipt Verification

- `training_receipt.json` is generated alongside `tokenizer.json`.
- Contains valid vocabulary count, algorithm name, seed, and input corpus hash.

## 5. Test Suite

- `cargo test` passes all Rust trainer tests.
- `uv run pytest tests/test_trainer.py` passes all Python trainer tests.

## Merge Criteria

All criteria verified. Open PR and merge to `main`.
