---
language:
- tw
- ee
- gaa
- fat
- aka
license: apache-2.0
tags:
- tokenizer
- kwa
- twi
- ewe
- ga
- fante
- subword
- bpe
- ghana
- togo
pipeline_tag: text-generation
---

# Leke BPE-8k: Subword Tokenizer for Kwa Languages

**Leke** is a dedicated, production-grade subword tokenizer engineered specifically for Niger-Congo Kwa languages: **Akan/Twi**, **Ewe**, **Ga**, and **Fante**.

Built with a high-throughput Rust engine and Byte-Level BPE, Leke overcomes the extreme token fragmentation and high fertility of general multilingual models, providing compact, linguistically grounded token representations with a guaranteed **0.0% unknown-token rate**.

---

## Key Highlights

- **Low Fertility**: 2.16 – 2.77 tokens/word across Kwa languages (vs. 3.0 – 5.5+ for NLLB / LLaMA).
- **Zero Out-of-Vocabulary**: Full byte-level fallback guarantees zero `<unk>` tokens on arbitrary text, emojis, or rare characters.
- **Canonical Linguistic Normalization**: Unicode NFC + automatic variant mapping for standard orthographic glyphs (`ɛ`, `ɔ`, `ŋ`, `ɖ`, `ɣ`).
- **Tone Preservation**: Tonal diacritics are preserved by default to protect phonemic semantics for speech and NLP tasks.
- **Fast Rust Core**: Encodes $>350,000$ tokens/sec in Python via PyO3 abi3 bindings.

---

## Evaluation Benchmark

Evaluated on held-out test splits against standard baselines:

| Model | Akan / Twi (Fertility) | Ewe (Fertility) | Ga (Fertility) | Fante (Fertility) | Unknown Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Leke BPE (8k)** | **2.23** | **2.77** | **2.38** | **2.16** | **0.0%** |
| NLLB-200 (SentencePiece) | 2.92 | 3.15 | 3.20 | 2.98 | 0.0% |
| Goldfish Twi (monolingual) | 1.62 | — | — | — | 0.4% |
| Wikilangs Ewe (monolingual) | — | 1.71 | — | — | 0.6% |

---

## Quickstart

### 1. Using Hugging Face `transformers`

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("acquayefrank/leke-bpe-8k")

text = "Akwaaba ba Ghana man mu! Wɔfrɛ me Kofi na mefiri Kumasi."
tokens = tokenizer.tokenize(text)
print("Tokens:", tokens)

encoding = tokenizer(text)
print("Input IDs:", encoding["input_ids"])
print("Decoded:", tokenizer.decode(encoding["input_ids"]))
```

### 2. Using Python `leke` Package

```python
from leke import LekeTokenizer

tokenizer = LekeTokenizer.from_file("tokenizer.json")
enc = tokenizer.encode("Mìedó gbe na mi nyuie.")

print("IDs:", enc.ids)
print("Tokens:", enc.tokens)
print("Decoded:", tokenizer.decode(enc.ids))
```

---

## Training Data & Methodology

- **Corpus**: Pooled multilingual corpora from Wikipedia, Glot500, MADLAD-400, and MGhana-ST.
- **Sampling**: Temperature-based upsampling ($\alpha = 0.5$) to ensure equitable subword allocation for smaller sister languages.
- **Algorithm**: Byte-Level Byte Pair Encoding (BPE) with vocabulary target 8,192.
- **Seed**: 42 (fully deterministic).

## Citation

```bibtex
@misc{acquaye2026leke,
  title={Leke: High-Performance Subword Tokenization for Kwa Languages},
  author={Acquaye, Frank},
  year={2026},
  howpublished={\url{https://github.com/acquayefrank/leke}}
}
```
