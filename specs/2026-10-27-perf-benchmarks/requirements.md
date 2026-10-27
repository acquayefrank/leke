# Phase 7: Performance Micro-benchmarks & Optimization — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 7 — "Performance Micro-benchmarks & Optimization". Phases 0–6 completed the tokenizer architecture, vertical slice, and algorithm selection. Phase 7 measures and verifies raw encoding and decoding throughput in Rust and Python to guarantee production-ready speed.

**Branch:** `perf-benchmarks`, cut from `main` at commit `7249346`.

## Scope

In scope, per roadmap Phase 7:

1. Rust micro-benchmark suite (`benches/throughput.rs`) utilizing `criterion`:
   - Benchmarking `KwaNormalizer::normalize_str` on short and paragraph-length Kwa texts.
   - Benchmarking `Tokenizer::encode` and `Tokenizer::decode` throughput.
2. Python throughput benchmark harness (`scripts/benchmark_throughput.py`):
   - Comparing `LekeTokenizer` against Hugging Face `tokenizers.Tokenizer` on identical held-out Kwa corpora.
   - Reporting sentences/sec, MB/sec, and tokens/sec.
3. Verification that `LekeTokenizer` achieves throughput $\ge$ Hugging Face Python tokenizers baseline.
4. Summary benchmark report committed to `specs/benchmarks.md`.

## Explicitly Out of Scope

1. Final model card and release publishing (Phase 8: `hf-release`).
2. GPU/CUDA acceleration (explicit non-goal in `specs/mission.md`).

## Decisions (Confirmed via Project Constitution)

1. **Benchmarking Target**: Benchmark on the selected production algorithm (Byte-Level BPE-8k).
2. **Criterion Framework**: Use standard Rust `criterion = "0.5"` statistical harness.

## Guardrails from mission.md / tech-stack.md

- Target: Near-zero PyO3 overhead; throughput must match or exceed standard Hugging Face tokenizers.
