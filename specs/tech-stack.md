# Leke (Kwa Tokenizer) — Technology Stack & Architecture

## System Architecture Overview

Leke is structured as a dual-language project consisting of a high-performance **Rust core engine** and idiomatic **Python bindings** with a comprehensive evaluation harness.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Python Layer (uv workspace)                     │
│  - Training orchestrator & dataset sampling                            │
│  - Baseline evaluation harness (fertility, split rate, unk rate)       │
│  - Hugging Face transformers.AutoTokenizer integration                 │
└────────────────────────────────────▲───────────────────────────────────┘
                                     │ PyO3 / maturin (abi3)
┌────────────────────────────────────▼───────────────────────────────────┐
│                           Rust Core (leke crate)                       │
│  - Custom Normalizer trait (Unicode NFC, canonical character mapping)  │
│  - Tokenizers crate integration (BPE / Unigram models, trainers)       │
│  - Serialization engine (tokenizer.json + training metadata receipt)   │
│  - High-throughput encode/decode API                                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Core Technologies & Tooling

### 1. Rust Core Engine
- **Language / Edition**: Rust 2021 edition (or latest stable).
- **Primary Dependencies**:
  - `tokenizers`: Hugging Face's Rust library providing core subword algorithms (BPE, Unigram), pre-tokenizers, decoders, and trainers.
  - `pyo3`: High-level bindings between Rust and Python, targeting the stable `abi3` C-API.
  - `unicode-normalization`: Fast, standard-compliant Unicode normalization (NFC/NFD).
  - `serde` & `serde_json`: Serialization and deserialization of normalizer character mapping tables, training configurations, and tokenizer artifacts.
  - `criterion`: Statistical micro-benchmarking framework for encode and decode throughput.

### 2. Python Environment & Packaging
- **Package & Environment Manager**: `uv`
  - High-speed virtual environment creation, dependency resolution, lockfile pinning (`uv.lock`), and script execution (`uv run`).
- **Build Backend**: `maturin`
  - Configured in `pyproject.toml` to build PyO3 C-extensions as `abi3` wheels (compatible across Python 3.9+ without per-minor-version compilation).
- **Core Python Dependencies**:
  - `tokenizers`: Official Hugging Face Python library (used for parity testing and comparison).
  - `transformers`: To validate `AutoTokenizer` compatibility with generated `tokenizer.json`.
  - `pytest`: Python unit test and integration test harness.
  - `polars` / `pandas`: Tabulation of evaluation metrics (fertility, split rate, compression).
  - `tabulate`: Formatting markdown tables for evaluation reports.

---

## Normalization Architecture

The normalizer pipeline enforces linguistic correctness across Kwa orthographies before subword segmentation:

1. **Unicode Canonical Normalization**: Standard Unicode NFC to resolve precomposed vs. decomposed codepoint anomalies.
2. **Externalized Variant Mapping**:
   - Inconsistent orthographic characters (e.g., phonetic glyph variations of `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ɣ`) mapped to standardized canonical Unicode codepoints.
   - Storage format: `data/char_mappings.json` loaded into Rust at initialization, ensuring rules can be tuned without recompiling code.
3. **Tone & Diacritic Preservation**:
   - Combining acute/grave/macron accents preserved by default to protect tonal meaning.
   - Optional configurable flag (`strip_accents: bool`) for downstream tasks requiring unaccented text.
4. **Whitespace & Casing**:
   - Whitespace collapsed (`\s+` -> `' '`), leading/trailing trimmed.
   - Casing preserved by default (no unconditional lowercasing) to support named entity recognition and proper noun capitalization.

---

## Training & Model Architecture

- **Subword Algorithms**:
  - Primary Slice: Byte-Level BPE (`ByteLevel` pre-tokenizer with byte fallback to guarantee 0% unknown tokens).
  - Comparison Architecture: Unigram with byte-level fallback.
- **Target Vocabulary Sizes**: 8,192 (8k), 16,384 (16k), and 32,768 (32k).
- **Corpus Sampling**:
  - Multi-language pooling with per-language upsampling / Dirichlet temperature sampling:
    $$P(L_i) \propto (\text{Count}(L_i))^\alpha \quad (\alpha \in [0.3, 0.7])$$
  - Prevents high-resource Akan/Twi corpora from starving Ewe, Ga, and Fante vocabulary allocation.
- **Provenance & Determinism**:
  - Fixed RNG seed (`seed: 42`).
  - Output bundle: `tokenizer.json` accompanied by `training_receipt.json` (logging exact input corpus checksums, line counts, language weights, and hyper-parameters).

---

## Evaluation & Testing Stack

| Layer | Tool | Focus | Verification Criterion |
| :--- | :--- | :--- | :--- |
| **Rust Unit Tests** | `cargo test` | Normalizer character mappings, tone preservation, determinism | `decode(encode(text)) == normalized(text)` |
| **Python Parity** | `pytest` | PyO3 bindings vs native Rust, HF `transformers` loading | Identical tokens and IDs across languages |
| **Micro-benchmarks** | `cargo criterion` | Encode and decode throughput (tokens/sec, MB/sec) | Throughput $\ge$ HF Python `tokenizers` baseline |
| **Fertility & OOV** | Custom CLI / `uv run` | Held-out test set evaluation | Fertility $\le$ Goldfish Twi & Wikilangs Ewe; 0% `<unk>` |

---

## Distribution & Release Artifacts

1. **Rust Crate**: Published to `crates.io` with documentation on `docs.rs`.
2. **Python Wheels**: ABI3 wheels distributed on PyPI via `maturin publish`.
3. **Model Weights / Tokenizers**: Published to Hugging Face Hub containing:
   - `tokenizer.json`
   - `tokenizer_config.json`
   - `special_tokens_map.json`
   - Model Card (`README.md`) with corpus provenance, evaluation tables, and usage snippets.
