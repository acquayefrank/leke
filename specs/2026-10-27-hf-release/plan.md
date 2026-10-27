# Phase 8: Packaging, Model Card & Hugging Face Release — Plan

Numbered task groups for Phase 8 implementation.

## 1. Project License (LICENSE)

- Write official Apache License Version 2.0.

## 2. Corpus Licensing Audit (`specs/corpus_licenses.md`)

- Document license terms, commercial use permissions, and attribution for all ingested corpora:
  - Wikipedia Dumps (CC BY-SA 4.0)
  - Glot500 (CC BY-SA / Apache 2.0 / research terms)
  - MADLAD-400 (ODC-BY)
  - MGhana-ST (Creative Commons / research terms)

## 3. Hugging Face Model Bundle Configuration

- Generate `models/bpe-8k/tokenizer_config.json` with `clean_up_tokenization_spaces: false`.
- Generate `models/bpe-8k/special_tokens_map.json` mapping `<unk>`, `<s>`, `</s>`, `<pad>`, `<mask`.
- Generate `models/bpe-8k/README.md` (Hugging Face Model Card) containing:
  - YAML tags (`languages: [aka, ewe, gaa, fat]`, `license: apache-2.0`).
  - Model description, normalization pipeline, evaluation tables, and Python code snippets.

## 4. Root Documentation (README.md)

- Update root `README.md` to be production-grade:
  - Project vision and badges.
  - Quickstart guide (Python and Rust).
  - Benchmark highlights from `specs/benchmarks.md` and `specs/eval_results.md`.
  - Architecture breakdown and citation instructions.

## 5. Hub Release Script (`scripts/upload_hf.py`)

- Implement `scripts/upload_hf.py` to upload the bundle to Hugging Face Hub using `huggingface_hub.HfApi`.

## 6. Binary Wheel Release Build

- Run `uv run maturin build --release` and verify produced abi3 `.whl` in `target/wheels/`.

## 7. Validation Pass & Final PR

- Verify full test suite passes.
- Open PR, merge into `main`.
