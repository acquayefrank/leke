# Phase 3: Byte-Level BPE Training Engine — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 3 — "Byte-Level BPE Training Engine". Phase 2 created the normalized, stratified dataset splits. Phase 3 implements the core training engine in Rust and Python to train Byte-Level BPE tokenizers with deterministic provenance receipts.

**Branch:** `bpe-training`, cut from `main` at commit `115e0f6`.

## Scope

In scope, per roadmap Phase 3:

1. Rust training engine in `src/trainer.rs` wrapping Hugging Face's `tokenizers` library with:
   - `BPE` model builder.
   - `BpeTrainerBuilder` configured with custom special tokens (`<unk>`, `<s>`, `</s>`, `<pad>`, `<mask>`).
   - Normalizer stage using `KwaNormalizer`.
   - `ByteLevel` pre-tokenizer and decoder with `add_prefix_space: false` and `trim_offsets: true`.
   - Byte-level fallback guaranteeing 0% unknown tokens.
2. CLI / Trainer routine supporting configurable vocabulary targets (8,192, 16,384, 32,768, plus test targets).
3. Serialization of `tokenizer.json` loadable by Hugging Face `tokenizers.Tokenizer` and `transformers.AutoTokenizer`.
4. Emission of `training_receipt.json` capturing:
   - Vocabulary size, special tokens, algorithm (`BPE-ByteLevel`).
   - Input corpus path and SHA-256 checksums from `data/data_manifest.json`.
   - Random seed (default 42).
   - Training duration and final vocabulary counts.

## Explicitly Out of Scope

1. Python PyO3 bindings for end-to-end tokenizer encoding (Phase 4: `pyo3-bindings`).
2. Unigram tokenizer model (Phase 6: `unigram-comparison`).
3. Comparative baseline evaluation harness against Goldfish/NLLB (Phase 5: `baseline-eval`).

## Decisions (Confirmed via Project Constitution)

1. **Algorithm**: Byte-Level BPE is the primary vertical slice algorithm.
2. **Zero OOV Guarantee**: Byte-level representation ensures any byte sequence can be represented without generating `<unk>`.
3. **Artifact Compliance**: Output artifact is standard Hugging Face `tokenizer.json`.

## Guardrails from mission.md / tech-stack.md

- **Reproducibility**: Training receipt must record random seed and input corpus checksums.
- **Normalizer Integration**: Training pipeline must incorporate `KwaNormalizer` so the learned subwords are based on canonical orthography.
