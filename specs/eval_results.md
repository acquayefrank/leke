# Leke Subword Tokenizer — Evaluation Leaderboard

This report compares Leke against baseline tokenizers (NLLB-200, Goldfish, Wikilangs) measured on the same text by `scripts/measure_baselines.py`.

## Held-Out Test Splits (in-domain)

Sentences held out from the same sources as the training data (`data/splits/<lang>/test.txt`). The Twi split is mostly Twi Wikipedia, which the Wikilangs and Goldfish tokenizers were likely trained on.

| Model                         | Vocab   | Language   | Fertility (tok/word)   | Split >2 (%)   | Unknown (%)   |   Compression (bytes/tok) | Leke fertility vs. baseline   |
|-------------------------------|---------|------------|------------------------|----------------|---------------|---------------------------|-------------------------------|
| **Leke BPE (16k)**            | 16k     | Akan / Twi | **1.38**               | 8.0%           | **0.0%**      |                      4.01 | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Akan / Twi | 1.24                   | 4.5%           | 0.11%         |                      4.46 | ⚠️ Baseline lower (+11.3%)    |
| Goldfish Twi (twi_latn_full)  | 50k     | Akan / Twi | 1.28                   | 5.4%           | 0.0%          |                      4.31 | ⚠️ Baseline lower (+7.8%)     |
| Goldfish Akan (aka_latn_full) | 50k     | Akan / Twi | 1.28                   | 5.2%           | 0.0%          |                      4.31 | ⚠️ Baseline lower (+7.8%)     |
| Wikilangs Twi (tw, 16k)       | 16k     | Akan / Twi | 1.28                   | 5.6%           | 0.1%          |                      4.33 | ⚠️ Baseline lower (+7.8%)     |
| Wikilangs Twi (tw, 8k)        | 8k      | Akan / Twi | 1.34                   | 7.4%           | 0.1%          |                      4.12 | ⚠️ Baseline lower (+3.0%)     |
| NLLB-200 (multilingual)       | 256k    | Akan / Twi | 1.55                   | 12.6%          | 0.26%         |                      3.57 | ✅ Leke lower (-11.0%)         |
| **Leke BPE (16k)**            | 16k     | Ewe        | **1.45**               | 10.4%          | **0.0%**      |                      4.03 | —                             |
| Wikilangs Ewe (ee, 32k)       | 32k     | Ewe        | 1.34                   | 7.7%           | 0.11%         |                      4.34 | ⚠️ Baseline lower (+8.2%)     |
| Goldfish Ewe (ewe_latn_full)  | 50k     | Ewe        | 1.35                   | 8.3%           | 0.03%         |                      4.32 | ⚠️ Baseline lower (+7.4%)     |
| Wikilangs Ewe (ee, 16k)       | 16k     | Ewe        | 1.38                   | 9.0%           | 0.11%         |                      4.22 | ⚠️ Baseline lower (+5.1%)     |
| Wikilangs Ewe (ee, 8k)        | 8k      | Ewe        | 1.44                   | 10.3%          | 0.11%         |                      4.07 | ⚠️ Baseline lower (+0.7%)     |
| NLLB-200 (multilingual)       | 256k    | Ewe        | 1.65                   | 15.9%          | 0.3%          |                      3.53 | ✅ Leke lower (-12.1%)         |
| **Leke BPE (16k)**            | 16k     | Ga         | **1.39**               | 7.9%           | **0.0%**      |                      4.39 | —                             |
| NLLB-200 (multilingual)       | 256k    | Ga         | 1.93                   | 25.1%          | 0.08%         |                      3.16 | ✅ Leke lower (-28.0%)         |
| **Leke BPE (16k)**            | 16k     | Fante      | **1.34**               | 6.2%           | **0.0%**      |                      4.11 | —                             |
| Wikilangs Fante (fat, 32k)    | 32k     | Fante      | 1.26                   | 5.0%           | 0.02%         |                      4.36 | ⚠️ Baseline lower (+6.3%)     |
| Wikilangs Fante (fat, 16k)    | 16k     | Fante      | 1.3                    | 6.2%           | 0.02%         |                      4.23 | ⚠️ Baseline lower (+3.1%)     |
| Wikilangs Fante (fat, 8k)     | 8k      | Fante      | 1.38                   | 8.5%           | 0.02%         |                      3.99 | ✅ Leke lower (-2.9%)          |
| Goldfish Akan (aka_latn_full) | 50k     | Fante      | 1.39                   | 8.1%           | 0.0%          |                      3.95 | ✅ Leke lower (-3.6%)          |
| Wikilangs Twi (tw, 32k)       | 32k     | Fante      | 1.51                   | 11.3%          | 0.05%         |                      3.64 | ✅ Leke lower (-11.3%)         |
| Wikilangs Twi (tw, 16k)       | 16k     | Fante      | 1.6                    | 13.9%          | 0.04%         |                      3.43 | ✅ Leke lower (-16.2%)         |
| NLLB-200 (multilingual)       | 256k    | Fante      | 1.7                    | 17.2%          | 0.61%         |                      3.24 | ✅ Leke lower (-21.2%)         |
| Wikilangs Twi (tw, 8k)        | 8k      | Fante      | 1.71                   | 16.5%          | 0.04%         |                      3.22 | ✅ Leke lower (-21.6%)         |

- **Akan / Twi**: Leke fertility 1.38, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher fertility than: Wikilangs Twi (tw, 32k), Goldfish Twi (twi_latn_full), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 16k), Wikilangs Twi (tw, 8k).
- **Ewe**: Leke fertility 1.45, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher fertility than: Wikilangs Ewe (ee, 32k), Goldfish Ewe (ewe_latn_full), Wikilangs Ewe (ee, 16k), Wikilangs Ewe (ee, 8k).
- **Ga**: Leke fertility 1.39, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual).
- **Fante**: Leke fertility 1.34, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Fante (fat, 8k), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 32k), Wikilangs Twi (tw, 16k), NLLB-200 (multilingual), Wikilangs Twi (tw, 8k). Higher fertility than: Wikilangs Fante (fat, 32k), Wikilangs Fante (fat, 16k).

## FLORES+ devtest (out-of-domain)

Professionally translated sentences (`openlanguagedata/flores_plus`, CC BY-SA 4.0) that none of the compared tokenizers were trained on. Covers Ewe and Twi (Asante, Akuapem); Ga and Fante are not included.

| Model                         | Vocab   | Language      | Fertility (tok/word)   | Split >2 (%)   | Unknown (%)   |   Compression (bytes/tok) | Leke fertility vs. baseline   |
|-------------------------------|---------|---------------|------------------------|----------------|---------------|---------------------------|-------------------------------|
| **Leke BPE (16k)**            | 16k     | Twi (Asante)  | **1.49**               | 10.6%          | **0.0%**      |                      3.67 | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Twi (Asante)  | 1.4                    | 8.5%           | 0.05%         |                      3.9  | ⚠️ Baseline lower (+6.4%)     |
| Goldfish Akan (aka_latn_full) | 50k     | Twi (Asante)  | 1.42                   | 9.1%           | 0.0%          |                      3.84 | ⚠️ Baseline lower (+4.9%)     |
| Goldfish Twi (twi_latn_full)  | 50k     | Twi (Asante)  | 1.43                   | 9.6%           | 0.0%          |                      3.81 | ⚠️ Baseline lower (+4.2%)     |
| Wikilangs Twi (tw, 16k)       | 16k     | Twi (Asante)  | 1.45                   | 10.0%          | 0.05%         |                      3.76 | ⚠️ Baseline lower (+2.8%)     |
| Wikilangs Twi (tw, 8k)        | 8k      | Twi (Asante)  | 1.53                   | 12.3%          | 0.05%         |                      3.57 | ✅ Leke lower (-2.6%)          |
| NLLB-200 (multilingual)       | 256k    | Twi (Asante)  | 1.59                   | 13.9%          | 1.52%         |                      3.42 | ✅ Leke lower (-6.3%)          |
| **Leke BPE (16k)**            | 16k     | Twi (Akuapem) | **1.44**               | 9.6%           | **0.0%**      |                      3.7  | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Twi (Akuapem) | 1.31                   | 6.4%           | 0.07%         |                      4.07 | ⚠️ Baseline lower (+9.9%)     |
| Goldfish Akan (aka_latn_full) | 50k     | Twi (Akuapem) | 1.32                   | 6.8%           | 0.0%          |                      4.02 | ⚠️ Baseline lower (+9.1%)     |
| Goldfish Twi (twi_latn_full)  | 50k     | Twi (Akuapem) | 1.33                   | 6.9%           | 0.0%          |                      4    | ⚠️ Baseline lower (+8.3%)     |
| Wikilangs Twi (tw, 16k)       | 16k     | Twi (Akuapem) | 1.37                   | 8.1%           | 0.07%         |                      3.9  | ⚠️ Baseline lower (+5.1%)     |
| Wikilangs Twi (tw, 8k)        | 8k      | Twi (Akuapem) | 1.44                   | 10.1%          | 0.07%         |                      3.7  | ⚠️ Baseline lower (+0.0%)     |
| NLLB-200 (multilingual)       | 256k    | Twi (Akuapem) | 1.47                   | 10.7%          | 0.92%         |                      3.63 | ✅ Leke lower (-2.0%)          |
| **Leke BPE (16k)**            | 16k     | Ewe           | **1.43**               | 9.3%           | **0.0%**      |                      3.94 | —                             |
| Goldfish Ewe (ewe_latn_full)  | 50k     | Ewe           | 1.33                   | 6.9%           | 2.74%         |                      4.22 | ⚠️ Baseline lower (+7.5%)     |
| Wikilangs Ewe (ee, 32k)       | 32k     | Ewe           | 1.39                   | 8.8%           | 2.66%         |                      4.03 | ⚠️ Baseline lower (+2.9%)     |
| Wikilangs Ewe (ee, 16k)       | 16k     | Ewe           | 1.44                   | 10.1%          | 2.57%         |                      3.91 | ✅ Leke lower (-0.7%)          |
| Wikilangs Ewe (ee, 8k)        | 8k      | Ewe           | 1.49                   | 11.5%          | 2.48%         |                      3.76 | ✅ Leke lower (-4.0%)          |
| NLLB-200 (multilingual)       | 256k    | Ewe           | 1.54                   | 12.7%          | 0.02%         |                      3.64 | ✅ Leke lower (-7.1%)          |

- **Twi (Asante)**: Leke fertility 1.49, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Twi (tw, 8k), NLLB-200 (multilingual). Higher fertility than: Wikilangs Twi (tw, 32k), Goldfish Akan (aka_latn_full), Goldfish Twi (twi_latn_full), Wikilangs Twi (tw, 16k).
- **Twi (Akuapem)**: Leke fertility 1.44, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher fertility than: Wikilangs Twi (tw, 32k), Goldfish Akan (aka_latn_full), Goldfish Twi (twi_latn_full), Wikilangs Twi (tw, 16k), Wikilangs Twi (tw, 8k).
- **Ewe**: Leke fertility 1.43, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Ewe (ee, 16k), Wikilangs Ewe (ee, 8k), NLLB-200 (multilingual). Higher fertility than: Goldfish Ewe (ewe_latn_full), Wikilangs Ewe (ee, 32k).
