# Leke (Kwa Tokenizer)

[![CI](https://github.com/acquayefrank/leke/actions/workflows/ci.yml/badge.svg)](https://github.com/acquayefrank/leke)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blueviolet.svg)](https://acquayefrank.github.io/leke/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)
[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](Cargo.toml)

**Leke** is a high-performance, open-source subword tokenizer engineered specifically for Kwa languages: **Akan / Twi**, **Ewe**, **Ga**, and **Fante**. Built with a Rust core and Python bindings via PyO3, Leke delivers compact subword fertility, linguistic orthographic normalization, tone preservation, and a guaranteed **0.0% unknown-token rate**.

> 🌐 **Interactive Showcase & Documentation**: Test live in-browser tokenization, inspect benchmark leaderboards, and view API guides at [https://acquayefrank.github.io/leke/](https://acquayefrank.github.io/leke/).

---

## Why Leke?

Standard multilingual tokenizers (LLaMA, Mistral, GPT-4, NLLB) are built around high-resource languages and fragment West African words into more subword pieces than necessary. This inflates context window costs, increases inference latency, and causes hallucination loops in ASR/TTS and speech translation.

Leke solves this with:
1. **Low Fertility**: **1.34 – 1.48** tokens per word (mean **1.40**) from a single 8k vocabulary shared across Twi, Ewe, Ga, and Fante: **5–27% fewer tokens than NLLB-200** (256k), and fewer than same-size (8k) monolingual Wikilangs tokenizers on Ewe and Fante.
2. **Zero Unknown Tokens**: Byte-Level BPE ensures arbitrary byte sequences, names, or loanwords never produce `<unk>`.
3. **Canonical Normalization**: Maps chaotic Unicode variations of `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ƒ`, `ɣ` (including textbook lookalikes `ͻ`, `Ͻ`, `ↄ`, `ᴐ`, `⊃`, `φ`, `ε`, `γ`, `ð`) to standard NFC codepoints.
4. **Tone Preservation**: Tone marks are preserved by default, protecting phonemic pitch distinctions for Kwa speech and language AI.
5. **Drop-in Ecosystem Support**: Serializes to standard `tokenizer.json`, immediately consumable by Hugging Face `transformers.AutoTokenizer`.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Python API (uv / maturin)                       │
│  - LekeTokenizer: High-level Python wrapper                            │
│  - .to_transformers() -> PreTrainedTokenizerFast                       │
│  - Automated evaluation harness & temperature upsampler                │
└────────────────────────────────────▲───────────────────────────────────┘
                                     │ PyO3 (abi3-py39)
┌────────────────────────────────────▼───────────────────────────────────┐
│                           Rust Core (leke crate)                       │
│  - Custom Normalizer trait (Unicode NFC, canonical character mapping)  │
│  - Byte-Level BPE & Unigram training engines                           │
│  - High-throughput batch encode/decode (170,000+ tokens/sec)           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+ and [`uv`](https://github.com/astral-sh/uv)
- Rust toolchain (`cargo`, `rustc` 1.75+)

### Quick Build
```bash
# Clone the repository
git clone https://github.com/acquayefrank/leke.git
cd leke

# Set up environment and compile extension
uv sync
uv run maturin develop
```

### Reproducing the Corpus & Training from Raw PDFs
The 13 reference curriculum manuals and textbooks are not distributed with this repository. Place the PDFs listed in `scripts/extract_pdf_corpora.py` in `data/raw/pdfs/` (git-ignored), then extract and normalize the sentences, generate the 80/10/10 splits, and retrain `bpe-8k`:

```bash
# 1. Extract normalized corpora from the PDFs in data/raw/pdfs/
uv run --with pypdf python scripts/extract_pdf_corpora.py

# 2. Build stratified splits (80/10/10) and temperature-upsampled pooled_train.txt
uv run python -m leke.corpus

# 3. Train Byte-Level BPE (8,192 vocab) and run evaluation
uv run python -m leke.trainer --algorithm bpe --corpus data/splits/pooled_train.txt --output-dir models/bpe-8k --vocab-size 8192
uv run python -m leke.evaluate
```

---

## Quickstart

### Python

```python
from leke import LekeTokenizer, normalize

# 1. Linguistic Normalization
cleaned = normalize("Wɔfrɛ me Kofi na mefiri Kumasi.")
print("Normalized:", cleaned)

# 2. Tokenization with LekeTokenizer
tok = LekeTokenizer.from_file("models/bpe-8k/tokenizer.json")
enc = tok.encode("Akwaaba ba Ghana man mu!")

print("IDs:", enc.ids)
print("Tokens:", enc.tokens)
print("Decoded:", tok.decode(enc.ids))

# 3. Direct Hugging Face Transformers Integration
hf_tok = tok.to_transformers()
hf_tokens = hf_tok.tokenize("Mìedó gbe na mi nyuie.")
print("HF Tokens:", hf_tokens)
```

### Rust

```rust
use _leke::normalizer::KwaNormalizer;
use tokenizers::Tokenizer;

fn main() {
    let norm = KwaNormalizer::default();
    let cleaned = norm.normalize_str("  Wɔfrɛ   me   Kofi.  ");
    println!("Cleaned: {}", cleaned);

    let tokenizer = Tokenizer::from_file("models/bpe-8k/tokenizer.json").unwrap();
    let encoding = tokenizer.encode("Akwaaba pápá", false).unwrap();
    println!("Token IDs: {:?}", encoding.get_ids());
}
```

---

## Benchmark Highlights

### 1. Fertility & Fragmentation on Held-out Test Splits

Fertility (tokens per word, lower is better). Every tokenizer is scored with the same metric code on the same held-out test splits (`scripts/measure_baselines.py`).

| Language | Leke BPE (8k, 4 languages) | NLLB-200 (256k) | Wikilangs monolingual (8k) | Best monolingual (any size) |
| :--- | :--- | :--- | :--- | :--- |
| **Akan / Twi** | 1.48 | 1.55 (Leke −5%) | **1.34** | 1.24 (Wikilangs 32k) |
| **Ewe** | **1.37** | 1.65 (Leke −17%) | 1.44 | 1.34 (Wikilangs 32k) |
| **Ga** | **1.41** | 1.93 (Leke −27%) | — | — |
| **Fante** | **1.34** | 1.70 (Leke −21%) | 1.38 | 1.26 (Wikilangs 32k) |
| **Unknown Rate** | **0.0% (guaranteed)** | 0.08% – 0.61% | 0.02% – 0.11% | 0.0% – 0.11% |

Leke beats NLLB-200 on all four languages and same-size monolingual tokenizers on Ewe and Fante. Larger monolingual tokenizers (32k–50k, one language each) still achieve lower fertility, and Twi is Leke's weakest language. The test splits come from the same textbooks as the training data, so these are in-domain results.

*See full evaluation report in [`specs/eval_results.md`](specs/eval_results.md) and algorithm decision in [`specs/algorithm_decision.md`](specs/algorithm_decision.md).*

### 2. Throughput Benchmarks

- **Single-Core Encode**: **173,000+ tokens/sec** in Python.
- **Single-Core Decode**: **51,000+ sentences/sec**.
- *See Criterion statistical profiles in [`specs/benchmarks.md`](specs/benchmarks.md).*

---

## Project Structure

```
leke/
├── benches/               # Criterion statistical benchmarks (throughput.rs)
├── data/
│   ├── char_mappings.json # Externalized canonical Unicode mapping tables
│   ├── samples/           # Curated seed corpora (twi, ewe, gaa, fat)
│   ├── splits/            # Stratified train/dev/test splits
│   └── data_manifest.json # Provenance manifest with SHA-256 hashes
├── models/
│   ├── bpe-8k/            # Production Byte-Level BPE tokenizer bundle
│   └── unigram-8k/        # Unigram comparison model bundle
├── python/leke/           # Python package wrapper (tokenizer, trainer, corpus, evaluate)
├── specs/                 # Project Constitution & feature specifications
├── src/                   # Rust core engine (lib.rs, normalizer.rs, trainer.rs, py_tokenizer.rs)
├── tests/                 # Comprehensive test suite (pytest & cargo test)
├── Cargo.toml             # Rust crate manifest
└── pyproject.toml         # Maturin & uv package configuration
```

---

## Testing

```bash
# Run Rust unit tests
cargo test

# Run Criterion benchmarks
cargo bench -- --test

# Run full Python test suite
uv run pytest
```

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
Corpus licensing audit details are documented in [specs/corpus_licenses.md](specs/corpus_licenses.md).
