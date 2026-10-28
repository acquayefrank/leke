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

# Leke BPE-8k (legacy)

This is the earlier 8,192-token Leke tokenizer, trained only on about 9,000 sentences of Ghanaian curriculum text and Twi Wikipedia. It has been superseded by [`bpe-16k`](../bpe-16k/), which adds MADLAD-400 training text and performs better on out-of-domain text.

Measured on the same test sets as `bpe-16k`: 1.66 / 1.60 / 1.66 tokens per word on FLORES+ Asante Twi / Akuapem Twi / Ewe (higher than NLLB-200), and 1.48 / 1.37 / 1.41 / 1.34 on held-out curriculum Twi / Ewe / Ga / Fante. Its normalizer predates the `Đ`, `ט` and zero-width mappings.
