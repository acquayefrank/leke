# Phase 2: Corpus Ingestion & Stratified Splits — Validation

Criteria to verify Phase 2 implementation.

## 1. Split Isolation & Contamination Check

- Verify 0% sentence overlap between train, dev, and test splits for every language:
  $$\text{Train} \cap \text{Test} = \emptyset, \quad \text{Dev} \cap \text{Test} = \emptyset$$
- Hashing and sampling must be 100% deterministic given seed 42.

## 2. Normalization Cleanliness

- Every sentence in the generated splits must be in canonical normalized form:
  `sentence == normalizer.normalize(sentence)`.
- No duplicate lines within any single split.

## 3. Multilingual Sampling Verification

- `pooled_train.txt` incorporates text from all targeted languages according to temperature scaling.
- Sampling ratios correctly increase the relative weight of smaller corpora.

## 4. Manifest Integrity

- `data/data_manifest.json` exists, is valid JSON, and matches on-disk file checksums and line counts.
- Akan/Twi and Ewe are flagged as primary tier; Ga and Fante coverage documented.

## 5. Test Suite

- `uv run pytest tests/test_corpus.py` passes all unit tests.

## Merge Criteria

All five validation checks pass. Once verified, open a PR and merge to `main`.
