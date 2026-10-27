# Phase 5: Baseline Evaluation Harness — Plan

Numbered task groups for Phase 5 implementation.

## 1. Metrics Engine (`python/leke/evaluate.py`)

- Implement `calculate_metrics(tokenizer, lines: List[str]) -> Dict[str, float]`:
  - `fertility`: total subword tokens / total whitespace words.
  - `split_rate_gt2`: percentage of words splitting into $> 2$ tokens.
  - `unk_rate`: percentage of emitted tokens matching `<unk>` ID.
  - `compression_ratio`: total UTF-8 bytes / total tokens.

## 2. Baseline Models Adapter

- Implement `BaselineAdapter`:
  - Interface to load or mock:
    - `Goldfish-Twi`
    - `Wikilangs-Ewe`
    - `NLLB-200`
  - Cache baseline results for offline reproducibility.

## 3. Leaderboard Generator & Gate Check

- Implement `run_evaluation(test_dir, model_dir, baseline_dir) -> str`:
  - Computes metrics on `test.txt` splits for each language.
  - Compiles comparative table comparing Leke BPE-8k vs Baselines.
  - Performs release gate assertion for Akan/Twi and Ewe.
  - Saves table to `specs/eval_results.md`.

## 4. Test Suite Implementation (`tests/test_evaluation.py`)

- Test metric formulas on known synthetic inputs.
- Test zero `<unk>` rate assertion.
- Test evaluation runner outputs expected markdown format.

## 5. Validation Pass

- Run `uv run python -m leke.evaluate` to generate `specs/eval_results.md`.
- Run `uv run pytest`.

## 6. PR

- Commit, push `baseline-eval`, create PR, and merge into `main`.
