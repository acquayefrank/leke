# Leke (Kwa Tokenizer) — Implementation Roadmap

This roadmap organizes the development of Leke into small, sequential, verifiable phases. Following the agreed vertical-slice strategy, Phases 0 through 5 construct a complete, end-to-end working pipeline with Byte-Level BPE before Phase 6 introduces Unigram comparison.

---

## Roadmap Overview

```
Phase 0: Workspace & Toolchain Scaffold (`repo-scaffold`)
   ↓
Phase 1: Kwa Normalizer & Character Mapping (`kwa-normalizer`)
   ↓
Phase 2: Corpus Ingestion & Stratified Splits (`corpus-pipeline`)
   ↓
Phase 3: Byte-Level BPE Training Engine (`bpe-training`)
   ↓
Phase 4: PyO3 Bindings & Python Package (`pyo3-bindings`)
   ↓
Phase 5: Baseline Evaluation Harness (`baseline-eval`)
   ↓
Phase 6: Unigram Algorithm & Dual-Model Comparison (`unigram-comparison`)
   ↓
Phase 7: Performance Micro-benchmarks & Optimization (`perf-benchmarks`)
   ↓
Phase 8: Packaging, Model Card & Hugging Face Release (`hf-release`)
```

---

## Phases of Work

### Phase 0: Workspace & Toolchain Scaffold
- **Branch Slug**: `repo-scaffold`
- **Objective**: Establish the dual-language project structure (Rust core + Python bindings) with `uv` and `maturin`.
- **Deliverables**:
  - Git repository initialization and `.gitignore` configured for Rust and Python.
  - Root `Cargo.toml` configuring the `leke` Rust crate.
  - `pyproject.toml` configured with `maturin` (targeting `abi3`) and `uv` dependencies.
  - Minimal Rust dummy function exposed via PyO3 to verify the bridge.
  - Local verification script (`scripts/dev-check.sh` / powershell equivalent).
- **Definition of Done**:
  - `cargo check` and `cargo test` run with 0 errors.
  - `uv run maturin develop` compiles the extension into the virtual environment.
  - `uv run python -c "import leke; print(leke.__file__)"` executes successfully.

---

### Phase 1: Kwa Normalizer & Character Mapping
- **Branch Slug**: `kwa-normalizer`
- **Objective**: Implement the linguistic normalization engine in Rust with externalized character mapping tables.
- **Deliverables**:
  - Externalized mapping file (`data/char_mappings.json`) mapping orthographic variants of `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ɣ` to standard NFC forms.
  - Custom Normalizer struct implementing `tokenizers::normalizer::Normalizer`.
  - Normalization pipeline: Unicode NFC -> Variant Map -> Whitespace Collapsing -> Optional tone mark stripping (defaulting to preserving tones).
  - Exhaustive unit test suite covering character variants, accented tokens, and mixed casing.
- **Definition of Done**:
  - `cargo test` tests all character substitutions defined in `char_mappings.json`.
  - Tone marks are verified preserved by default, and verified stripped when `strip_accents: true`.
  - Round-trip invariant verified: normalizing an already-normalized string is idempotent.

---

### Phase 2: Corpus Ingestion & Stratified Splits
- **Branch Slug**: `corpus-pipeline`
- **Objective**: Implement corpus downloading, cleaning, language-stratified train/dev/test splits, and temperature-based upsampling.
- **Deliverables**:
  - Ingestion modules for target corpora (Wikipedia dumps, Glot500, MADLAD-400, MGhana-ST) for Akan/Twi, Ewe, and available Ga/Fante text.
  - Stratified split generator producing isolated `train`, `dev`, and `test` splits per language to prevent evaluation contamination.
  - Multilingual pooling routine with configurable temperature upsampling ($\alpha \in [0.3, 0.7]$).
  - Data manifest generator recording exact line counts, byte sizes, and SHA-256 checksums per language.
- **Definition of Done**:
  - Verified non-overlapping train/dev/test splits written to disk.
  - Data manifest JSON generated with exact per-language token and sentence statistics.
  - Primary languages (Akan/Twi and Ewe) verified to meet minimum volume thresholds; secondary languages (Ga and Fante) logged with coverage audit notes.

---

### Phase 3: Byte-Level BPE Training Engine
- **Branch Slug**: `bpe-training`
- **Objective**: Build the core Rust training routine for Byte-Level BPE tokenizers across multiple vocabulary sizes.
- **Deliverables**:
  - Rust training interface wrapping `tokenizers::models::bpe::BpeTrainer` with `ByteLevel` pre-tokenization and decoding.
  - Fixed-seed deterministic training configuration.
  - CLI / orchestration script supporting 8k, 16k, and 32k vocabulary targets.
  - Output bundle generator saving `tokenizer.json` alongside a `training_receipt.json` (recording random seed, vocab size, hyperparameters, and corpus manifest hashes).
- **Definition of Done**:
  - Training runs complete successfully for 8k, 16k, and 32k Byte-Level BPE models on the training split.
  - All generated `tokenizer.json` files validate against Hugging Face tokenizer schemas.
  - Invariant verified: Byte-level fallback guarantees 0 unknown tokens on arbitrary byte sequences.

---

### Phase 4: PyO3 Bindings & Python Package
- **Branch Slug**: `pyo3-bindings`
- **Objective**: Expose the trained tokenizer and normalizer through an idiomatic, high-performance Python package built with `maturin`.
- **Deliverables**:
  - PyO3 wrapper classes for `LekeTokenizer` and `LekeNormalizer`.
  - ABI3 wheel build configuration in `pyproject.toml`.
  - Integration with standard Hugging Face `transformers`: verify that saved `tokenizer.json` loads directly via `transformers.AutoTokenizer.from_file()`.
  - Pytest suite testing encode, decode, batch encoding, and parity with native Rust outputs.
- **Definition of Done**:
  - `uv run pytest` passes 100% of binding unit and integration tests.
  - Direct output parity: `LekeTokenizer.encode()` produces identical token IDs, tokens, and offsets as the native Rust crate.
  - `transformers.AutoTokenizer.from_file()` loads the 8k/16k/32k tokenizers and executes round-trip encode/decode without error.

---

### Phase 5: Baseline Evaluation Harness
- **Branch Slug**: `baseline-eval`
- **Objective**: Build the rigorous evaluation harness and benchmark the trained BPE tokenizers against per-language and multilingual baselines.
- **Deliverables**:
  - Evaluation engine calculating:
    1. **Fertility**: Average subword tokens per whitespace word.
    2. **Excessive Split Rate**: Percentage of words fragmented into $>2$ subword pieces.
    3. **Unknown Token Rate**: Percentage of unknown tokens (asserted at 0.0%).
    4. **Compression Ratio**: Input bytes per output token.
  - Baseline adapters for Goldfish Twi (`twi_latn`), Wikilangs Ewe (`ee`), and NLLB SentencePiece.
  - Automated Markdown evaluation report generator comparing Leke models against baselines on the held-out `test` splits.
- **Definition of Done**:
  - Evaluation suite executes on all held-out language test sets.
  - Release Gate Verification: Akan/Twi and Ewe results evaluated against Goldfish and Wikilangs baselines; gate check clearly documented.
  - Full comparative markdown leaderboard produced and committed to `specs/eval_results.md`.

---

### Phase 6: Unigram Algorithm & Dual-Model Comparison
- **Branch Slug**: `unigram-comparison`
- **Objective**: Implement Unigram subword training and execute a head-to-head comparison against Byte-Level BPE.
- **Deliverables**:
  - Unigram training integration in the Rust training engine using `tokenizers::models::unigram::UnigramTrainer`.
  - Trained 8k, 16k, and 32k Unigram models using identical corpus splits, seeds, and normalizer rules.
  - Comparative evaluation update running Phase 5 evaluation harness on Unigram models.
  - Decision document selecting the final production algorithm (BPE vs. Unigram) based on fertility, split rate, and compression metrics.
- **Definition of Done**:
  - 8k, 16k, and 32k Unigram tokenizers trained and validated.
  - Comparative BPE vs. Unigram matrix published across all four target languages.
  - Architecture selection signed off and logged in the spec.

---

### Phase 7: Performance Micro-benchmarks & Optimization
- **Branch Slug**: `perf-benchmarks`
- **Objective**: Benchmark encoding and decoding throughput in Rust and Python, optimizing hot paths.
- **Deliverables**:
  - Criterion benchmark suite in Rust (`benches/throughput.rs`) measuring encode/decode throughput in sentences/sec and MB/sec.
  - Python throughput comparison script measuring Leke vs. official Hugging Face Python `tokenizers` on identical corpora.
  - Memory profiling and optimization of normalizer string allocations and mapping lookups.
- **Definition of Done**:
  - `cargo bench` executes and establishes statistical baselines.
  - Python binding encode throughput meets or exceeds baseline Hugging Face Python `tokenizers` throughput.
  - Benchmark summary table added to documentation.

---

### Phase 8: Packaging, Model Card & Hugging Face Release
- **Branch Slug**: `hf-release`
- **Objective**: Finalize documentation, licensing audits, distribution wheels, and Hugging Face Hub release artifacts.
- **Deliverables**:
  - Model Card (`README.md` / `HF_CARD.md`) covering training data sources, license terms, normalizer rules, evaluation tables, and known limitations.
  - Corpus licensing audit verifying terms for all ingested data.
  - Open-source license file (e.g., Apache 2.0 / MIT).
  - Hub publication script uploading `tokenizer.json`, `tokenizer_config.json`, and model card to the Hugging Face organization.
  - Maturin wheel packaging verified ready for PyPI distribution.
- **Definition of Done**:
  - Hugging Face Hub test upload validates and loads via `AutoTokenizer.from_pretrained()`.
  - All corpus licenses verified and recorded in the model card.
  - Clean `uv run maturin build --release` produces compliant ABI3 binary wheels.
