# Phase 4: PyO3 Bindings & Python Package — Validation

Criteria to verify Phase 4 implementation.

## 1. Direct Binding Parity

- `LekeTokenizer.from_file(path).encode(text).ids` produces identical token IDs as `tokenizers.Tokenizer.from_file(path).encode(text).ids` on Akan/Twi, Ewe, Ga, and Fante text.

## 2. Batch Encoding & Decoding

- `encode_batch([s1, s2])` matches `[encode(s1), encode(s2)]`.
- `decode_batch([ids1, ids2])` matches `[decode(ids1), decode(ids2)]`.

## 3. Hugging Face Transformers Interoperability

- `tok.to_transformers()` produces a `PreTrainedTokenizerFast` instance that can tokenize, encode, decode, and generate attention masks without error.

## 4. Test Suite Execution

- `uv run pytest tests/test_bindings.py` passes 100%.

## Merge Criteria

All criteria verified. Open PR and merge to `main`.
