# Phase 4: PyO3 Bindings & Python Package — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 4 — "PyO3 Bindings & Python Package". Phases 0–3 provided the toolchain, normalizer, data pipeline, and core BPE training engine. Phase 4 exposes a full-featured, idiomatic Python tokenizer class `LekeTokenizer` directly backed by the Rust engine, with encoding, decoding, batching, and Hugging Face interoperability.

**Branch:** `pyo3-bindings`, cut from `main` at commit `6bffb03`.

## Scope

In scope, per roadmap Phase 4:

1. Expose `LekeTokenizer` in Rust via PyO3:
   - `LekeTokenizer.from_file(path: str)`
   - `encode(text: str, add_special_tokens: bool = True) -> PyEncoding`
   - `encode_batch(texts: List[str], add_special_tokens: bool = True) -> List[PyEncoding]`
   - `decode(ids: List[int], skip_special_tokens: bool = True) -> str`
   - `decode_batch(batch_ids: List[List[int]], skip_special_tokens: bool = True) -> List[str]`
   - `token_to_id(token: str) -> Optional[int]`, `id_to_token(id: int) -> Optional[str]`
   - `vocab_size: int` property.
2. Expose `PyEncoding` representation containing:
   - `ids: List[int]`
   - `tokens: List[str]`
   - `offsets: List[Tuple[int, int]]`
3. High-level Python wrapper in `python/leke/tokenizer.py` providing seamless interop with Hugging Face `transformers.PreTrainedTokenizerFast` via `.to_transformers()`.
4. Unit and integration tests testing parity between `LekeTokenizer` and standard Hugging Face `tokenizers.Tokenizer` on identical `tokenizer.json` artifacts.

## Explicitly Out of Scope

1. Full evaluation leaderboard on baselines (Phase 5: `baseline-eval`).
2. Unigram training comparison (Phase 6: `unigram-comparison`).

## Decisions (Confirmed via Project Constitution)

1. **ABI3 Compatibility**: Built as abi3 wheel supporting Python 3.9+ without minor-version recompilation.
2. **Zero Overhead**: Direct Rust execution via PyO3 without unnecessary serialization/copying.
3. **Ecosystem Parity**: Output IDs and tokens must match official Hugging Face Tokenizers 100%.

## Guardrails from mission.md / tech-stack.md

- Standard tokenization methods must preserve Unicode NFC and canonical variants through the integrated normalizer pipeline.
