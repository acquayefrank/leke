# Phase 2: Corpus Ingestion & Stratified Splits — Plan

Numbered task groups for Phase 2 implementation.

## 1. Corpus Data Layout and Seed Datasets

- Create directory structure under `data/`:
  - `data/samples/` containing curated, representative seed sentences for Akan/Twi, Ewe, Ga, and Fante.
  - Structure `data/splits/<language>/{train,dev,test}.txt`.

## 2. Ingestion & Filtering Engine (`python/leke/corpus.py`)

- Implement `CorpusProcessor`:
  - Loading from raw line-delimited text or Hugging Face dataset sources.
  - Normalization through `KwaNormalizer`.
  - Quality filters: min length (>= 3 words), max length (<= 250 words), non-empty.
  - Deduplication across lines.

## 3. Stratified Split Generator

- Implement deterministic train / dev / test splitting (`split_corpus`):
  - Fixed seed (default 42).
  - 80% train, 10% dev, 10% test.
  - Verification that `set(train) & set(test) == empty` and `set(dev) & set(test) == empty`.

## 4. Temperature Upsampling & Balanced Pooled Dataset

- Implement `TemperatureSampler`:
  - Calculates language frequencies.
  - Applies temperature exponent $\alpha$ (default 0.5).
  - Emits balanced pooled training stream `data/splits/pooled_train.txt`.

## 5. Manifest & Metadata Generator

- Output `data/data_manifest.json` recording:
  - SHA-256 hashes of all generated split files.
  - Exact sentence counts, word counts, and language distribution percentages.
  - Audit status for primary vs secondary languages.

## 6. CLI Entry Point & Automated Tests

- Add `python -m leke.corpus` CLI command for pipeline generation.
- Add `tests/test_corpus.py` testing deduplication, split isolation, upsampling weights, and manifest generation.

## 7. Validation Pass

- Run `uv run pytest` and verify generated splits and manifest.

## 8. PR

- Open PR from `corpus-pipeline` into `main`, merge upon validation.
