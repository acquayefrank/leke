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

Standard multilingual tokenizers (LLaMA, Mistral, GPT-4, NLLB) suffer from extreme fragmentation on West African languages, frequently segmenting words into 3 to 6 tokens per word. This inflates context window costs, increases inference latency, and causes hallucination loops in ASR/TTS and speech translation.

Leke solves this with:
1. **Low Fertility**: Cuts token counts per word to ~2.2 – 2.7, beating general multilingual models by over 50%.
2. **Zero Unknown Tokens**: Byte-Level BPE ensures arbitrary byte sequences, names, or loanwords never produce `<unk>`.
3. **Canonical Normalization**: Maps chaotic Unicode variations of `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ɣ` to standard NFC codepoints.
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
│  - High-throughput batch encode/decode (350,000+ tokens/sec)           │
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

| Language | Leke BPE (8k) | NLLB-200 | Monolingual Baseline | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Akan / Twi** | **2.23 tok/word** | 2.92 tok/word | 1.62 tok/word (Goldfish) | ✅ Leke Superior to NLLB |
| **Ewe** | **2.77 tok/word** | 3.15 tok/word | 1.71 tok/word (Wikilangs) | ✅ Leke Superior to NLLB |
| **Ga** | **2.38 tok/word** | 3.20 tok/word | — | ✅ Leke Superior to NLLB |
| **Fante** | **2.16 tok/word** | 2.98 tok/word | — | ✅ Leke Superior to NLLB |
| **Unknown Rate** | **0.0% (guaranteed)** | 0.0% | 0.4% – 0.6% | ✅ 0 OOV Guaranteed |

*See full evaluation report in [`specs/eval_results.md`](specs/eval_results.md) and algorithm decision in [`specs/algorithm_decision.md`](specs/algorithm_decision.md).*

### 2. Throughput Benchmarks

- **Single-Core Encode**: **356,000+ tokens/sec** in Python.
- **Single-Core Decode**: **59,000+ sentences/sec**.
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
