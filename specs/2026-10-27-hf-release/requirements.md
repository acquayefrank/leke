# Phase 8: Packaging, Model Card & Hugging Face Release — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 8 — "Packaging, Model Card & Hugging Face Release". This is the final phase of the roadmap. Phases 0–7 completed the entire stack: normalizer, pipeline, training, bindings, evaluation, algorithm selection, and performance benchmarking. Phase 8 packages the production release artifacts, license audits, model cards, and distribution bundles.

**Branch:** `hf-release`, cut from `main` at commit `bb6e64a`.

## Scope

In scope, per roadmap Phase 8:

1. Create formal open-source license file `LICENSE` (Apache 2.0).
2. Create comprehensive corpus license audit in `specs/corpus_licenses.md` auditing license terms for Wikipedia, Glot500, MADLAD-400, and MGhana-ST.
3. Generate standard Hugging Face model repository files:
   - `models/bpe-8k/tokenizer_config.json`
   - `models/bpe-8k/special_tokens_map.json`
   - `models/bpe-8k/README.md` (Hugging Face Model Card with YAML frontmatter, dataset tags, language codes, and usage snippets).
4. Update root `README.md` with complete documentation, architecture diagram, Quickstart in Python and Rust, and benchmark summaries.
5. Create release upload tool `scripts/upload_hf.py` using `huggingface_hub.HfApi`.
6. Verify release wheel compilation via `uv run maturin build --release`.

## Explicitly Out of Scope

1. Direct production deployment to live PyPI / Hugging Face servers without human token secrets (script provided for execution).

## Decisions (Confirmed via Project Constitution)

1. **Licensing**: Open-source Apache 2.0.
2. **Standard HF Bundle**: Full bundle includes `tokenizer.json`, `tokenizer_config.json`, and `special_tokens_map.json` for seamless `AutoTokenizer.from_pretrained()` loading.

## Guardrails from mission.md / tech-stack.md

- Compliance with Hugging Face Hub specifications and complete transparency regarding training data and bias notes.
