# Phase 2: Corpus Ingestion & Stratified Splits — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 2 — "Corpus Ingestion & Stratified Splits". Phase 1 established the KwaNormalizer. Phase 2 implements dataset ingestion, normalization filtering, strictly isolated train/dev/test splits, multilingual upsampling, and data provenance manifests.

**Branch:** `corpus-pipeline`, cut from `main` at commit `b2f9310`.

## Scope

In scope, per roadmap Phase 2:

1. Corpus preparation and ingestion pipeline supporting target Kwa languages:
   - Primary: Akan/Twi (`twi`), Ewe (`ewe`).
   - Secondary: Ga (`gaa`), Fante (`fat`).
2. Inclusion of curated, high-quality benchmark and seed datasets for local deterministic execution, plus remote ingestion adapters (Hugging Face Datasets / Wikipedia / Glot500).
3. Normalization pass using `KwaNormalizer` to clean raw corpus lines, eliminate duplicates, and filter out low-quality/corrupted records.
4. Stratified splitting: 80% train, 10% dev, 10% test with deterministic hashing to guarantee 0% data leakage across splits.
5. Multilingual pooling with temperature-based upsampling ($\alpha \in [0.3, 0.7]$) to produce balanced training streams.
6. Generation of `data_manifest.json` recording SHA-256 checksums, line counts, byte sizes, and language sampling ratios.

## Explicitly Out of Scope

1. Subword vocabulary training and tokenizer serialization (Phase 3: `bpe-training`).
2. Downstream model evaluation calculations (Phase 5: `baseline-eval`).

## Decisions (Confirmed via Project Constitution)

1. **Tiered Scope**: Akan/Twi and Ewe are mandatory for full split requirements; Ga and Fante are integrated based on available data with audit logs.
2. **Strict Split Isolation**: Held-out test sets are strictly quarantined for Phase 5 baseline evaluation.
3. **Reproducibility**: Splits must be completely deterministic using fixed random seeds.

## Guardrails from mission.md / tech-stack.md

- **Multilingual Sampling Discipline**: Upweight under-represented languages via temperature scaling:
  $$P(L_i) \propto (\text{Count}(L_i))^\alpha$$
- **Provenance Logging**: Record corpus hashes in `data_manifest.json` for embedding in training receipts.
