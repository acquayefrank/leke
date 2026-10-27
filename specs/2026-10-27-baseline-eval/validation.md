# Phase 5: Baseline Evaluation Harness — Validation

Criteria to verify Phase 5 implementation.

## 1. Metrics Correctness

- Fertility equals $\text{tokens} / \text{words}$.
- Excessive split rate captures proportion of words with $>2$ subwords.
- Zero `<unk>` rate holds for Leke BPE across all test splits.

## 2. Release Gate Verification

- Evaluated on held-out `test.txt` splits:
  - Akan/Twi: Leke fertility beats NLLB baseline and matches/beats Goldfish baseline.
  - Ewe: Leke fertility beats NLLB baseline and matches/beats Wikilangs baseline.

## 3. Leaderboard Artifact

- `specs/eval_results.md` is generated, containing a complete markdown table with columns for Model, Language, Fertility, Split Rate (>2), Unk Rate, and Compression Ratio.

## 4. Test Suite Execution

- `uv run pytest tests/test_evaluation.py` passes 100%.

## Merge Criteria

All criteria verified. Open PR and merge to `main`.
