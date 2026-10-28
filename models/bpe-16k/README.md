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

# Leke BPE-16k: Subword Tokenizer for Kwa Languages

**Leke** is a Byte-Level BPE tokenizer for the Kwa languages **Akan/Twi**, **Ewe**, **Ga**, and **Fante**, with one 16,384-token vocabulary shared across all four, Kwa-specific Unicode normalization, and a guaranteed **0.0% unknown-token rate**.

---

## Key Highlights

- **Fertility**: 1.43 – 1.49 tokens/word on out-of-domain FLORES+ Twi and Ewe; 1.34 – 1.45 on held-out curriculum text for all four languages.
- **Zero Out-of-Vocabulary**: byte-level fallback means arbitrary text, emojis, or rare characters never become `<unk>`.
- **Normalization**: Unicode NFC plus mapping of lookalike characters (e.g. Greek `ͻ` → `ɔ`, `ε` → `ɛ`, Hebrew `ט` → `ʋ`) and removal of zero-width characters.
- **Tone Preservation**: tonal diacritics are kept by default.

---

## Evaluation

Fertility (tokens per word, lower is better). All tokenizers are scored with the same code on the same text. FLORES+ devtest is out-of-domain text none of these tokenizers were trained on; it has no Ga or Fante, so those rows use held-out curriculum test splits.

| Model | Twi Asante (FLORES+) | Twi Akuapem (FLORES+) | Ewe (FLORES+) | Ga (curriculum) | Fante (curriculum) | Unknown rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Leke BPE (16k)** | 1.49 | 1.44 | **1.43** | **1.39** | 1.34 | **0.0%** |
| NLLB-200 (256k) | 1.59 | 1.47 | 1.54 | 1.93 | 1.70 | 0.02% – 1.52% |
| Wikilangs, single language (16k) | **1.45** | **1.37** | 1.44 | — | **1.30** | 0.02% – 2.57% |

Dedicated Twi tokenizers remain 3–5% more compact on Twi at the same vocabulary size, and larger single-language tokenizers (32k–50k) reach lower fertility on the languages they cover. Full results: [`specs/eval_results.md`](https://github.com/acquayefrank/leke/blob/main/specs/eval_results.md).

---

## Quickstart

### 1. Using Hugging Face `transformers`

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("acquayefrank/leke-bpe-16k")

text = "Akwaaba ba Ghana man mu! Wɔfrɛ me Kofi na mefiri Kumasi."
print("Tokens:", tokenizer.tokenize(text))

encoding = tokenizer(text)
print("Input IDs:", encoding["input_ids"])
print("Decoded:", tokenizer.decode(encoding["input_ids"]))
```

### 2. Using the Python `leke` package

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

- **Corpus**: about 9,000 training sentences of Ghanaian curriculum text and Twi Wikipedia intros (all four languages), plus MADLAD-400 `clean` web text for Akan (~94k lines, used for Twi) and Ewe (~125k lines), and Wikipedia (20231101 snapshot) for Twi (~21k lines), Ewe (~4k) and Fante (~5.6k). MADLAD lines overlapping any dev/test or FLORES+ sentence were removed, as was every Wikipedia article containing one.
- **Sampling**: temperature upsampling with $\alpha = 0.2$ (chosen on FLORES+ dev and curriculum dev splits) to 500,000 pooled lines.
- **Algorithm**: Byte-Level BPE, vocabulary 16,384, seed 42.
- **Provenance**: `training_receipt.json` records the SHA-256 of the pooled training file.

## Citation

```bibtex
@misc{acquaye2026leke,
  title={Leke: High-Performance Subword Tokenization for Kwa Languages},
  author={Acquaye, Frank},
  year={2026},
  howpublished={\url{https://github.com/acquayefrank/leke}}
}
```
