# Phase 6: Unigram Algorithm & Dual-Model Comparison — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 6 — "Unigram Algorithm & Dual-Model Comparison". Following the vertical slice strategy agreed upon in the project constitution, Phases 0–5 built and benchmarked the Byte-Level BPE pipeline. Phase 6 introduces the Unigram subword algorithm into the Rust engine and performs a head-to-head architectural bake-off.

**Branch:** `unigram-comparison`, cut from `main` at commit `450a0f2`.

## Scope

In scope, per roadmap Phase 6:

1. Extend `src/trainer.rs` with `train_unigram`:
   - Wrapping `tokenizers::models::unigram::{Unigram, UnigramTrainerBuilder}`.
   - Employing `Metaspace` or byte-level pre-tokenization with byte fallback to ensure 0% `<unk>`.
   - Incorporating `KwaNormalizer`.
   - Emitting standard `tokenizer.json` and `training_receipt.json` with algorithm `Unigram`.
2. Python interface `train_unigram` exposed via `python/leke/trainer.py` and CLI flag `--algorithm {bpe,unigram}`.
3. Train Unigram model on `data/splits/pooled_train.txt` saving to `models/unigram-8k`.
4. Head-to-head benchmark evaluation between BPE-8k and Unigram-8k across all 4 Kwa languages on held-out test splits.
5. Publish decision matrix and architectural selection in `specs/algorithm_decision.md`.

## Explicitly Out of Scope

1. High-throughput criterion micro-benchmarking (Phase 7: `perf-benchmarks`).
2. Final Hugging Face Hub upload packaging (Phase 8: `hf-release`).

## Decisions (Confirmed via Project Constitution)

1. **Direct Comparison**: Both models are trained on the exact same pooled training corpus with the same seed (42).
2. **Selection Bar**: The algorithm with lower fertility, lower excessive split rate (>2 pieces), and zero `<unk>` rate is crowned as the primary production release default.

## Guardrails from mission.md / tech-stack.md

- Must ensure zero unknown tokens (`unk_rate: 0.0%`) regardless of algorithm choice.
