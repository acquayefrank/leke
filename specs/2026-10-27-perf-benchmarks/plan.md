# Phase 7: Performance Micro-benchmarks & Optimization — Plan

Numbered task groups for Phase 7 implementation.

## 1. Criterion Benchmark Harness (`benches/throughput.rs`)

- Add `[[bench]]` configuration to `Cargo.toml`.
- Create `benches/throughput.rs`:
  - `bench_normalizer`: Normalization speed on raw text.
  - `bench_bpe_encode`: Subword encoding speed.
  - `bench_bpe_decode`: Subword decoding speed.

## 2. Python Comparative Throughput Script (`scripts/benchmark_throughput.py`)

- Load `models/bpe-8k/tokenizer.json` in both `LekeTokenizer` and `tokenizers.Tokenizer`.
- Measure 1,000 encode and decode iterations over multi-sentence text.
- Compute throughput in sentences/sec, tokens/sec, and MB/sec.
- Verify Leke throughput is competitive ($\ge$ HF baseline).

## 3. Generate Benchmark Documentation (`specs/benchmarks.md`)

- Run benchmarks and record performance numbers.
- Publish `specs/benchmarks.md` with detailed tables and profiling observations.

## 4. Test Suite Execution

- Execute `cargo bench -- --test` to ensure bench targets compile and run cleanly.
- Run `uv run python scripts/benchmark_throughput.py`.

## 5. PR

- Commit, push `perf-benchmarks`, open PR, and merge into `main`.
