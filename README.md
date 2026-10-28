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
1. **Low Fertility**: one 16k vocabulary shared across Twi, Ewe, Ga, and Fante gives **1.30 – 1.48** tokens per word on held-out curriculum text (4–28% fewer than NLLB-200) and **1.41 – 1.52** on out-of-domain FLORES+ text (up to 8% fewer than NLLB-200). Dedicated single-language tokenizers still do better on Twi; see [Benchmark Highlights](#benchmark-highlights).
2. **Zero Unknown Tokens**: Byte-Level BPE ensures arbitrary byte sequences, names, or loanwords never produce `<unk>`.
3. **Canonical Normalization**: Maps chaotic Unicode variations of `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ƒ`, `ɣ` (including textbook lookalikes `ͻ`, `Ͻ`, `ↄ`, `ᴐ`, `⊃`, `φ`, `ε`, `γ`, `ð`, `Đ`, `ט`) to standard NFC codepoints, and strips zero-width characters.
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
│  - Batch encode/decode (~450k tokens/sec per thread, release build)    │
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
uv run maturin develop --release
```

### Reproducing the Corpus & Training
The 13 reference curriculum manuals and textbooks are not distributed with this repository. Place the PDFs listed in `scripts/extract_pdf_corpora.py` in `data/raw/pdfs/` (git-ignored), then:

```bash
# 1. Extract normalized curriculum corpora from the PDFs in data/raw/pdfs/
uv run --with pypdf python scripts/extract_pdf_corpora.py

# 2. Download MADLAD-400 Akan and Ewe text (training only, git-ignored in data/raw/madlad/)
uv run --with huggingface_hub python scripts/fetch_madlad.py

# 3. Build 80/10/10 curriculum splits plus a temperature-upsampled pool with MADLAD-400
uv run python -m leke.corpus --alpha 0.3 --extra-train-dir data/raw/madlad \
  --pooled-out data/raw/pooled_train_madlad.txt --total-samples 500000

# 4. Train Byte-Level BPE (16,384 vocab) and run evaluation
uv run python -m leke.trainer --algorithm bpe --corpus data/raw/pooled_train_madlad.txt \
  --output-dir models/bpe-16k --vocab-size 16384
uv run python -m leke.evaluate
```

MADLAD-400 text is used only for training; dev/test splits contain curriculum text only, and any MADLAD line overlapping a dev/test or FLORES+ sentence is removed. `models/bpe-16k/training_receipt.json` records the SHA-256 of the pooled training file, which matches `data/data_manifest.json`.

---

## Quickstart

### Python

```python
from leke import LekeTokenizer, normalize

# 1. Linguistic Normalization
cleaned = normalize("Wɔfrɛ me Kofi na mefiri Kumasi.")
print("Normalized:", cleaned)

# 2. Tokenization with LekeTokenizer
tok = LekeTokenizer.from_file("models/bpe-16k/tokenizer.json")
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

    let tokenizer = Tokenizer::from_file("models/bpe-16k/tokenizer.json").unwrap();
    let encoding = tokenizer.encode("Akwaaba pápá", false).unwrap();
    println!("Token IDs: {:?}", encoding.get_ids());
}
```

---

## Benchmark Highlights

Fertility is tokens per word (lower is better). Every tokenizer is scored with the same metric code on the same text (`scripts/measure_baselines.py`). Leke uses one 16k vocabulary for all four languages; each Wikilangs and Goldfish tokenizer covers a single language.

### 1. Out-of-domain: FLORES+ devtest

Professionally translated sentences that none of the compared tokenizers were trained on. FLORES+ has no Ga or Fante.

| Language | Leke BPE (16k) | NLLB-200 (256k) | Wikilangs (16k) | Best monolingual (any size) |
| :--- | :--- | :--- | :--- | :--- |
| **Twi (Asante)** | 1.52 | 1.59 (Leke −4%) | **1.45** | 1.40 (Wikilangs 32k) |
| **Twi (Akuapem)** | 1.47 | 1.47 (tie) | **1.37** | 1.31 (Wikilangs 32k) |
| **Ewe** | **1.41** | 1.54 (Leke −8%) | 1.44 | 1.33 (Goldfish 50k) |
| **Unknown rate** | **0.0%** | 0.02% – 1.52% | 0.05% – 2.57% | 0.0% – 2.74% |

On Ewe, Leke beats NLLB-200 and the same-size 16k monolingual tokenizer. Ewe monolingual tokenizers lose 2.5–2.7% of tokens to `<unk>`, mostly the Greek lookalike `ͻ` used for `ɔ` in FLORES+, which Leke normalizes. On Twi, dedicated Twi tokenizers are still 5–7% more compact at the same vocabulary size.

### 2. In-domain: held-out curriculum test splits

Sentences held out from the same sources as the curriculum training text. The Twi split is mostly Twi Wikipedia, which the Wikilangs and Goldfish tokenizers were likely trained on.

| Language | Leke BPE (16k) | NLLB-200 (256k) | Wikilangs (16k) | Best monolingual (any size) |
| :--- | :--- | :--- | :--- | :--- |
| **Akan / Twi** | 1.48 | 1.55 (Leke −5%) | **1.28** | 1.24 (Wikilangs 32k) |
| **Ewe** | 1.41 | 1.65 (Leke −15%) | **1.38** | 1.34 (Wikilangs 32k) |
| **Ga** | **1.40** | 1.93 (Leke −28%) | — | — |
| **Fante** | **1.30** | 1.70 (Leke −24%) | **1.30** | 1.26 (Wikilangs 32k) |
| **Unknown rate** | **0.0%** | 0.08% – 0.61% | 0.02% – 0.11% | 0.0% – 0.11% |

*See full evaluation report in [`specs/eval_results.md`](specs/eval_results.md) and algorithm decision in [`specs/algorithm_decision.md`](specs/algorithm_decision.md).*

### 2. Throughput Benchmarks

Measured from Python on the 1,151 held-out test sentences with `models/bpe-16k` (median of 7 runs, release build, 8-core x86_64 Linux). Absolute numbers vary by roughly 2× with machine load: an idle machine reached ~450,000 tokens/sec on 1 thread with the earlier 8k model, while the latest run under load measured:

- **Encode**: ~240,000 tokens/sec on 1 thread; ~950,000 tokens/sec on 8 threads.
- **Decode**: ~60,000 sentences/sec on 1 thread; ~235,000 sentences/sec on 8 threads.
- **Overhead**: on par with the raw Hugging Face `tokenizers` library running the same `tokenizer.json` (0.75×–1.7× across runs, within run-to-run noise).
- Build with `maturin develop --release`; a debug build is roughly 7–10× slower. Reproduce with `uv run python scripts/benchmark_throughput.py` (results in [`specs/benchmarks.md`](specs/benchmarks.md)).

---

## Project Structure

```
leke/
├── benches/               # Criterion statistical benchmarks (throughput.rs)
├── data/
│   ├── char_mappings.json # Externalized canonical Unicode mapping tables
│   ├── samples/           # Curated seed corpora (twi, ewe, gaa, fat)
│   ├── splits/            # Stratified train/dev/test splits
│   ├── baselines/         # Baseline tokenizer metrics on the same test sets
│   └── data_manifest.json # Provenance manifest with SHA-256 hashes
├── models/
│   ├── bpe-16k/           # Production Byte-Level BPE tokenizer bundle (curriculum + MADLAD-400)
│   ├── unigram-16k/       # Unigram comparison model bundle
│   └── bpe-8k/            # Legacy 8k model (curriculum text only)
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
