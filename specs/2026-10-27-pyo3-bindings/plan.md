# Phase 4: PyO3 Bindings & Python Package — Plan

Numbered task groups for Phase 4 implementation.

## 1. Rust PyO3 Tokenizer Wrapper (`src/lib.rs` / `src/py_tokenizer.rs`)

- Implement `PyEncoding`:
  - `ids: Vec<u32>`
  - `tokens: Vec<String>`
  - `offsets: Vec<(usize, usize)>`
- Implement `PyLekeTokenizer`:
  - Wrap internal `tokenizers::Tokenizer`.
  - Static constructor `from_file(path: &str)`.
  - `encode(&self, text: &str, add_special_tokens: bool)`
  - `encode_batch(&self, texts: Vec<String>, add_special_tokens: bool)`
  - `decode(&self, ids: Vec<u32>, skip_special_tokens: bool)`
  - `decode_batch(&self, batch_ids: Vec<Vec<u32>>, skip_special_tokens: bool)`
  - `token_to_id(&self, token: &str) -> Option<u32>`
  - `id_to_token(&self, id: u32) -> Option<String>`
  - `get_vocab_size(&self) -> usize`

## 2. High-Level Python Wrapper (`python/leke/tokenizer.py`)

- Create `LekeTokenizer` class extending the PyO3 class with convenience helpers:
  - `to_transformers() -> transformers.PreTrainedTokenizerFast`
  - Context manager and string formatting `__repr__`.

## 3. Integration & Parity Test Suite (`tests/test_bindings.py`)

- Test `LekeTokenizer.from_file`:
  - Verify `encode` produces exact IDs matching `tokenizers.Tokenizer.from_file`.
  - Verify `decode` reversibility.
  - Verify `encode_batch` and `decode_batch`.
  - Verify `.to_transformers()` produces functional Hugging Face tokenizer.

## 4. Validation Pass

- Rebuild extension with `uv run maturin develop`.
- Run `uv run pytest`.

## 5. PR

- Commit, push `pyo3-bindings`, open PR, and merge into `main`.
