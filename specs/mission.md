# Leke (Kwa Tokenizer) — Mission & Constitution

## Vision & Problem Statement

Subword tokenization is foundational to modern natural language processing and large language models. However, standard multilingual tokenizers (such as those in LLaMA, Mistral, and even massively multilingual models like NLLB) suffer from severe token fragmentation on African languages. For Niger-Congo languages—specifically the Kwa branch spoken across Ghana, Togo, Benin, and Côte d'Ivoire—existing tokenizers yield excessive fertility rates (tokens per word), diluting contextual attention, inflating inference latency and cost, and harming downstream representation quality.

**Leke** is a dedicated, production-grade, open-source subword tokenizer engineered specifically for Kwa languages. Built with a high-performance Rust core and idiomatic Python bindings, Leke delivers compact, balanced, and linguistically sound token representations that match or outperform monolingual baselines while remaining drop-in compatible with standard transformer architectures.

---

## Target Languages

The initial project scope focuses on four key Kwa languages:

| Language | ISO 639-3 / BCP-47 | Orthography / Script | Release Gate Tier |
| :--- | :--- | :--- | :--- |
| **Akan / Twi** | `aka_Latn`, `twi_Latn` | Latin with extended vowels (`ɛ`, `ɔ`) | **Primary (Hard Gate)** |
| **Ewe** | `ewe` | Latin with extended consonants/vowels (`ɖ`, `ŋ`, `ɣ`, `ɛ`, `ɔ`) | **Primary (Hard Gate)** |
| **Ga** | `gaa` | Latin with extended characters (`ŋ`, `ɛ`, `ɔ`) | **Secondary (Corpus Dependent)** |
| **Fante** | `fat` | Latin dialectal Akan orthography | **Secondary (Corpus Dependent)** |

### Tiered Language Gate Decision
Because clean digital text corpora are abundant for Akan/Twi and Ewe but comparatively scarce for Ga and Fante:
- **Primary Tier (Hard Gate):** Akan/Twi and Ewe are mandatory for the v1 release. The tokenizer must demonstrate superior or competitive fertility against dedicated per-language baselines on held-out text for both languages.
- **Secondary Tier (Best-Effort):** Ga and Fante will be incorporated into balanced training if clean, licensed corpus volume permits. If corpus scarcity or quality prevents achieving parity, their inclusion will not block the v1 release of the primary pair, and dedicated data expansion will follow.

---

## Core Objectives & Release Gate

1. **Beating Single-Language Baselines**: The tokenizer is only worth releasing if the joint multilingual tokenizer matches or beats dedicated per-language baselines on held-out evaluation text:
   - Akan/Twi: Beat or match Goldfish Twi (`twi_latn`).
   - Ewe: Beat or match Wikilangs Ewe (`ee`).
   - Multilingual: Outperform general multilingual tokenizers (e.g., NLLB SentencePiece).
2. **Zero Unknown-Token Rate**: Guarantee a 0% out-of-vocabulary (`<unk>`) rate across all input text using byte-level fallback.
3. **High Encode/Decode Throughput**: Provide near-zero-overhead tokenization in Rust with PyO3 bindings matching or exceeding standard Hugging Face `tokenizers` throughput.
4. **Standard Ecosystem Interoperability**: Produce serializable `tokenizer.json` artifacts immediately consumable via Hugging Face `transformers.AutoTokenizer.from_file()` and `tokenizers.Tokenizer.from_file()`.

---

## Explicit Non-Goals (Out of Scope)

To maintain sharp focus, the following areas are strictly out of scope:
- **Language Model Training**: No model weights, pre-training, fine-tuning, or embedding matrices are trained here; this project delivers only tokenizers.
- **Speech & Audio**: No automatic speech recognition (ASR) acoustic models or speech tokenizers.
- **Web Crawling from Scratch**: No uncurated Common Crawl scraping or spidering. Ingestion relies exclusively on verified, ethically sourced open corpora (MADLAD-400, Glot500, MGhana-ST, Wikipedia dumps).
- **GPU Acceleration**: Tokenization is strictly CPU-bound; no CUDA, ROCm, or custom GPU kernel development is in scope.

---

## Design Invariants & Architectural Principles

1. **Canonical Normalization via External Data Tables**:
   - Orthographic variants (e.g., inconsistent Unicode representations of `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ɣ`) must be deterministically mapped to canonical NFC forms.
   - Character mapping tables must live in external data files (e.g., JSON/YAML data assets), never hard-coded in Rust source files.
   - Case preservation by default (no lowercase stripping unless explicitly configured).
   - Tone marks and diacritics must be preserved by default; stripping tone marks must be an explicit, configurable opt-in flag.
2. **Deterministic & Reproducible Training**:
   - Random seeds must be pinned for all subword vocabulary training runs.
   - Every released tokenizer artifact must serialize with an accompanying metadata receipt recording the exact training config, commit hash, corpus hashes, and per-language sampling weights.
3. **Multilingual Sampling Discipline**:
   - Multi-language corpus pooling must employ per-language temperature upsampling (e.g., exponential or Dirichlet scaling) to prevent dominant language text (such as Akan) from monopolizing subword vocabulary allocation over lower-resource sister languages (Ewe, Ga, Fante).
4. **Drop-in Standards Compliance**:
   - The primary serialization format must remain vanilla `tokenizer.json`, compatible with standard Rust `tokenizers` and Python `transformers` tooling without requiring custom downstream C extensions or proprietary deserializers.
