# Phase 5: Baseline Evaluation Harness — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 5 — "Baseline Evaluation Harness". Phases 0–4 delivered the end-to-end BPE tokenizer and bindings. Phase 5 constructs the rigorous evaluation harness and measures Leke against the release gate baselines defined in `specs/mission.md`.

**Branch:** `baseline-eval`, cut from `main` at commit `bc7eaeb`.

## Scope

In scope, per roadmap Phase 5:

1. Core evaluation metrics engine (`python/leke/evaluate.py`):
   - **Fertility**: Average subword tokens per whitespace-separated word.
   - **Split Rate (>2)**: Percentage of words split into more than two subword pieces.
   - **Unknown Token Rate**: Percentage of unknown (`<unk>`) tokens.
   - **Compression Ratio**: Ratio of input raw bytes to output tokens ($\text{bytes} / \text{tokens}$).
2. Test split evaluation across all target languages:
   - Akan/Twi (`data/splits/twi/test.txt`)
   - Ewe (`data/splits/ewe/test.txt`)
   - Ga (`data/splits/gaa/test.txt`)
   - Fante (`data/splits/fat/test.txt`)
3. Baseline evaluation adapters:
   - Monolingual baselines: Goldfish Twi (`twi_latn`), Wikilangs Ewe (`ee`).
   - Multilingual baseline: NLLB-200 SentencePiece (Meta).
   - Mock/offline baseline fallbacks when executing without live Hugging Face Hub connectivity.
4. Leaderboard generator outputting markdown table and verifying the **Release Gate**:
   - Akan/Twi fertility $\le$ Goldfish Twi baseline.
   - Ewe fertility $\le$ Wikilangs Ewe baseline.
   - 0.0% `<unk>` rate across all evaluation text.
5. Leaderboard committed to `specs/eval_results.md`.

## Explicitly Out of Scope

1. Unigram subword model training (deferred to Phase 6: `unigram-comparison`).
2. High-throughput criterion micro-benchmarks (Phase 7: `perf-benchmarks`).

## Decisions (Confirmed via Project Constitution)

1. **Held-out Quarantining**: Evaluation must strictly run against the `test.txt` splits created in Phase 2.
2. **Release Gate Threshold**: Akan/Twi and Ewe serve as mandatory hard gates; Ga and Fante are reported with coverage notes.

## Guardrails from mission.md / tech-stack.md

- Must implement the exact metrics defined in `specs/mission.md#Core-Objectives-&-Release-Gate`.
