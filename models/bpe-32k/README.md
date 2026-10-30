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

# Leke BPE-32k: Subword Tokenizer for Kwa Languages

**Leke** is a Byte-Level BPE tokenizer for the Kwa languages **Akan/Twi**, **Ewe**, **Ga**, and **Fante**, with one 32,768-token vocabulary shared across all four, Kwa-specific Unicode normalization, and a guaranteed **0.0% unknown-token rate**.

It is trained on the same data as [Leke BPE-16k](https://huggingface.co/acquayefrank/leke-bpe-16k) with a vocabulary twice the size. It uses about 6–8% fewer tokens per word than BPE-16k, at the cost of a 32k-row embedding table. Choose 16k for small models trained on little data and 32k when sequence length matters more than model size.

---

## Key Highlights

- **Fertility**: 1.33 – 1.40 tokens/word on out-of-domain FLORES+ Twi and Ewe; 1.25 – 1.34 on held-out curriculum text for all four languages.
- **Zero Out-of-Vocabulary**: byte-level fallback means arbitrary text, emojis, or rare characters never become `<unk>`.
- **Normalization**: Unicode NFC plus mapping of lookalike characters (e.g. Greek `ͻ` → `ɔ`, `ε` → `ɛ`, Hebrew `ט` → `ʋ`) and removal of zero-width characters.
- **Tone Preservation**: tonal diacritics are kept by default.

---

## Evaluation

Fertility (tokens per word, lower is better). All tokenizers are scored with the same code on the same text. FLORES+ devtest is out-of-domain text none of these tokenizers were trained on; it has no Ga or Fante, so those rows use held-out curriculum test splits.

| Model | Twi Asante (FLORES+) | Twi Akuapem (FLORES+) | Ewe (FLORES+) | Ga (curriculum) | Fante (curriculum) | Unknown rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Leke BPE (32k)** | **1.40** | 1.36 | **1.33** | **1.29** | **1.25** | **0.0%** |
| Leke BPE (16k) | 1.49 | 1.44 | 1.43 | 1.39 | 1.34 | 0.0% |
| NLLB-200 (256k) | 1.59 | 1.47 | 1.54 | 1.93 | 1.70 | 0.02% – 1.52% |
| Wikilangs, single language (16k) | 1.45 | 1.37 | 1.44 | none | 1.30 | 0.02% – 2.57% |
| Best single language (32k–50k) | **1.40** | **1.31** | **1.33** | none | 1.26 | 0.0% – 2.74% |

With one vocabulary shared by four languages, it matches or beats every single-language tokenizer on FLORES+ Twi Asante and Ewe and on Fante. It still trails them on Twi Akuapem (by 4%) and on the Wikipedia-heavy Twi test split. Full results: [`specs/eval_results.md`](https://github.com/acquayefrank/leke/blob/main/specs/eval_results.md).

---

## Quickstart

### 1. Using Hugging Face `transformers`

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("acquayefrank/leke-bpe-32k")

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
- **Algorithm**: Byte-Level BPE, vocabulary 32,768, seed 42.
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
