# Leke Subword Tokenizer — Evaluation Leaderboard

This report compares the Leke models (16k and 32k vocabularies, same training data) against baseline tokenizers (NLLB-200, Goldfish, Wikilangs) measured on the same text by `scripts/measure_baselines.py`.

## Held-Out Test Splits (in-domain)

Sentences held out from the same sources as the training data (`data/splits/<lang>/test.txt`). The Twi split is mostly Twi Wikipedia, which the Wikilangs and Goldfish tokenizers were likely trained on.

| Model                         | Vocab   | Language   | Fertility (tok/word)   | Split >2 (%)   | Unknown (%)   |   Compression (bytes/tok) | Leke fertility vs. baseline   |
|-------------------------------|---------|------------|------------------------|----------------|---------------|---------------------------|-------------------------------|
| **Leke BPE (16k)**            | 16k     | Akan / Twi | **1.38**               | 8.0%           | **0.0%**      |                      4.01 | —                             |
| **Leke BPE (32k)**            | 32k     | Akan / Twi | **1.29**               | 5.8%           | **0.0%**      |                      4.27 | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Akan / Twi | 1.24                   | 4.5%           | 0.11%         |                      4.46 | ⚠️ 16k +11.3%, ⚠️ 32k +4.0%   |
| Goldfish Twi (twi_latn_full)  | 50k     | Akan / Twi | 1.28                   | 5.4%           | 0.0%          |                      4.31 | ⚠️ 16k +7.8%, ⚠️ 32k +0.8%    |
| Goldfish Akan (aka_latn_full) | 50k     | Akan / Twi | 1.28                   | 5.2%           | 0.0%          |                      4.31 | ⚠️ 16k +7.8%, ⚠️ 32k +0.8%    |
| Wikilangs Twi (tw, 16k)       | 16k     | Akan / Twi | 1.28                   | 5.6%           | 0.1%          |                      4.33 | ⚠️ 16k +7.8%, ⚠️ 32k +0.8%    |
| Wikilangs Twi (tw, 8k)        | 8k      | Akan / Twi | 1.34                   | 7.4%           | 0.1%          |                      4.12 | ⚠️ 16k +3.0%, ✅ 32k -3.7%     |
| NLLB-200 (multilingual)       | 256k    | Akan / Twi | 1.55                   | 12.6%          | 0.26%         |                      3.57 | ✅ 16k -11.0%, ✅ 32k -16.8%    |
| **Leke BPE (16k)**            | 16k     | Ewe        | **1.45**               | 10.4%          | **0.0%**      |                      4.03 | —                             |
| **Leke BPE (32k)**            | 32k     | Ewe        | **1.34**               | 7.4%           | **0.0%**      |                      4.37 | —                             |
| Wikilangs Ewe (ee, 32k)       | 32k     | Ewe        | 1.34                   | 7.7%           | 0.11%         |                      4.34 | ⚠️ 16k +8.2%, ⚠️ 32k +0.0%    |
| Goldfish Ewe (ewe_latn_full)  | 50k     | Ewe        | 1.35                   | 8.3%           | 0.03%         |                      4.32 | ⚠️ 16k +7.4%, ✅ 32k -0.7%     |
| Wikilangs Ewe (ee, 16k)       | 16k     | Ewe        | 1.38                   | 9.0%           | 0.11%         |                      4.22 | ⚠️ 16k +5.1%, ✅ 32k -2.9%     |
| Wikilangs Ewe (ee, 8k)        | 8k      | Ewe        | 1.44                   | 10.3%          | 0.11%         |                      4.07 | ⚠️ 16k +0.7%, ✅ 32k -6.9%     |
| NLLB-200 (multilingual)       | 256k    | Ewe        | 1.65                   | 15.9%          | 0.3%          |                      3.53 | ✅ 16k -12.1%, ✅ 32k -18.8%    |
| **Leke BPE (16k)**            | 16k     | Ga         | **1.39**               | 7.9%           | **0.0%**      |                      4.39 | —                             |
| **Leke BPE (32k)**            | 32k     | Ga         | **1.29**               | 4.8%           | **0.0%**      |                      4.75 | —                             |
| NLLB-200 (multilingual)       | 256k    | Ga         | 1.93                   | 25.1%          | 0.08%         |                      3.16 | ✅ 16k -28.0%, ✅ 32k -33.2%    |
| **Leke BPE (16k)**            | 16k     | Fante      | **1.34**               | 6.2%           | **0.0%**      |                      4.11 | —                             |
| **Leke BPE (32k)**            | 32k     | Fante      | **1.25**               | 3.9%           | **0.0%**      |                      4.41 | —                             |
| Wikilangs Fante (fat, 32k)    | 32k     | Fante      | 1.26                   | 5.0%           | 0.02%         |                      4.36 | ⚠️ 16k +6.3%, ✅ 32k -0.8%     |
| Wikilangs Fante (fat, 16k)    | 16k     | Fante      | 1.3                    | 6.2%           | 0.02%         |                      4.23 | ⚠️ 16k +3.1%, ✅ 32k -3.8%     |
| Wikilangs Fante (fat, 8k)     | 8k      | Fante      | 1.38                   | 8.5%           | 0.02%         |                      3.99 | ✅ 16k -2.9%, ✅ 32k -9.4%      |
| Goldfish Akan (aka_latn_full) | 50k     | Fante      | 1.39                   | 8.1%           | 0.0%          |                      3.95 | ✅ 16k -3.6%, ✅ 32k -10.1%     |
| Wikilangs Twi (tw, 32k)       | 32k     | Fante      | 1.51                   | 11.3%          | 0.05%         |                      3.64 | ✅ 16k -11.3%, ✅ 32k -17.2%    |
| Wikilangs Twi (tw, 16k)       | 16k     | Fante      | 1.6                    | 13.9%          | 0.04%         |                      3.43 | ✅ 16k -16.2%, ✅ 32k -21.9%    |
| NLLB-200 (multilingual)       | 256k    | Fante      | 1.7                    | 17.2%          | 0.61%         |                      3.24 | ✅ 16k -21.2%, ✅ 32k -26.5%    |
| Wikilangs Twi (tw, 8k)        | 8k      | Fante      | 1.71                   | 16.5%          | 0.04%         |                      3.22 | ✅ 16k -21.6%, ✅ 32k -26.9%    |

- **Akan / Twi, Leke BPE (16k)**: fertility 1.38, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Twi (tw, 32k), Goldfish Twi (twi_latn_full), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 16k), Wikilangs Twi (tw, 8k).
- **Akan / Twi, Leke BPE (32k)**: fertility 1.29, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Twi (tw, 8k), NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Twi (tw, 32k), Goldfish Twi (twi_latn_full), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 16k).
- **Ewe, Leke BPE (16k)**: fertility 1.45, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Ewe (ee, 32k), Goldfish Ewe (ewe_latn_full), Wikilangs Ewe (ee, 16k), Wikilangs Ewe (ee, 8k).
- **Ewe, Leke BPE (32k)**: fertility 1.34, `<unk>` rate 0.0%. Lower fertility than: Goldfish Ewe (ewe_latn_full), Wikilangs Ewe (ee, 16k), Wikilangs Ewe (ee, 8k), NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Ewe (ee, 32k).
- **Ga, Leke BPE (16k)**: fertility 1.39, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual).
- **Ga, Leke BPE (32k)**: fertility 1.29, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual).
- **Fante, Leke BPE (16k)**: fertility 1.34, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Fante (fat, 8k), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 32k), Wikilangs Twi (tw, 16k), NLLB-200 (multilingual), Wikilangs Twi (tw, 8k). Higher or equal fertility: Wikilangs Fante (fat, 32k), Wikilangs Fante (fat, 16k).
- **Fante, Leke BPE (32k)**: fertility 1.25, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Fante (fat, 32k), Wikilangs Fante (fat, 16k), Wikilangs Fante (fat, 8k), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 32k), Wikilangs Twi (tw, 16k), NLLB-200 (multilingual), Wikilangs Twi (tw, 8k).

## FLORES+ devtest (out-of-domain)

Professionally translated sentences (`openlanguagedata/flores_plus`, CC BY-SA 4.0) that none of the compared tokenizers were trained on. Covers Ewe and Twi (Asante, Akuapem); Ga and Fante are not included.

| Model                         | Vocab   | Language      | Fertility (tok/word)   | Split >2 (%)   | Unknown (%)   |   Compression (bytes/tok) | Leke fertility vs. baseline   |
|-------------------------------|---------|---------------|------------------------|----------------|---------------|---------------------------|-------------------------------|
| **Leke BPE (16k)**            | 16k     | Twi (Asante)  | **1.49**               | 10.6%          | **0.0%**      |                      3.67 | —                             |
| **Leke BPE (32k)**            | 32k     | Twi (Asante)  | **1.4**                | 8.3%           | **0.0%**      |                      3.89 | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Twi (Asante)  | 1.4                    | 8.5%           | 0.05%         |                      3.9  | ⚠️ 16k +6.4%, ⚠️ 32k +0.0%    |
| Goldfish Akan (aka_latn_full) | 50k     | Twi (Asante)  | 1.42                   | 9.1%           | 0.0%          |                      3.84 | ⚠️ 16k +4.9%, ✅ 32k -1.4%     |
| Goldfish Twi (twi_latn_full)  | 50k     | Twi (Asante)  | 1.43                   | 9.6%           | 0.0%          |                      3.81 | ⚠️ 16k +4.2%, ✅ 32k -2.1%     |
| Wikilangs Twi (tw, 16k)       | 16k     | Twi (Asante)  | 1.45                   | 10.0%          | 0.05%         |                      3.76 | ⚠️ 16k +2.8%, ✅ 32k -3.4%     |
| Wikilangs Twi (tw, 8k)        | 8k      | Twi (Asante)  | 1.53                   | 12.3%          | 0.05%         |                      3.57 | ✅ 16k -2.6%, ✅ 32k -8.5%      |
| NLLB-200 (multilingual)       | 256k    | Twi (Asante)  | 1.59                   | 13.9%          | 1.52%         |                      3.42 | ✅ 16k -6.3%, ✅ 32k -11.9%     |
| **Leke BPE (16k)**            | 16k     | Twi (Akuapem) | **1.44**               | 9.6%           | **0.0%**      |                      3.7  | —                             |
| **Leke BPE (32k)**            | 32k     | Twi (Akuapem) | **1.36**               | 7.7%           | **0.0%**      |                      3.92 | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Twi (Akuapem) | 1.31                   | 6.4%           | 0.07%         |                      4.07 | ⚠️ 16k +9.9%, ⚠️ 32k +3.8%    |
| Goldfish Akan (aka_latn_full) | 50k     | Twi (Akuapem) | 1.32                   | 6.8%           | 0.0%          |                      4.02 | ⚠️ 16k +9.1%, ⚠️ 32k +3.0%    |
| Goldfish Twi (twi_latn_full)  | 50k     | Twi (Akuapem) | 1.33                   | 6.9%           | 0.0%          |                      4    | ⚠️ 16k +8.3%, ⚠️ 32k +2.3%    |
| Wikilangs Twi (tw, 16k)       | 16k     | Twi (Akuapem) | 1.37                   | 8.1%           | 0.07%         |                      3.9  | ⚠️ 16k +5.1%, ✅ 32k -0.7%     |
| Wikilangs Twi (tw, 8k)        | 8k      | Twi (Akuapem) | 1.44                   | 10.1%          | 0.07%         |                      3.7  | ⚠️ 16k +0.0%, ✅ 32k -5.6%     |
| NLLB-200 (multilingual)       | 256k    | Twi (Akuapem) | 1.47                   | 10.7%          | 0.92%         |                      3.63 | ✅ 16k -2.0%, ✅ 32k -7.5%      |
| **Leke BPE (16k)**            | 16k     | Ewe           | **1.43**               | 9.3%           | **0.0%**      |                      3.94 | —                             |
| **Leke BPE (32k)**            | 32k     | Ewe           | **1.33**               | 6.8%           | **0.0%**      |                      4.21 | —                             |
| Goldfish Ewe (ewe_latn_full)  | 50k     | Ewe           | 1.33                   | 6.9%           | 2.74%         |                      4.22 | ⚠️ 16k +7.5%, ⚠️ 32k +0.0%    |
| Wikilangs Ewe (ee, 32k)       | 32k     | Ewe           | 1.39                   | 8.8%           | 2.66%         |                      4.03 | ⚠️ 16k +2.9%, ✅ 32k -4.3%     |
| Wikilangs Ewe (ee, 16k)       | 16k     | Ewe           | 1.44                   | 10.1%          | 2.57%         |                      3.91 | ✅ 16k -0.7%, ✅ 32k -7.6%      |
| Wikilangs Ewe (ee, 8k)        | 8k      | Ewe           | 1.49                   | 11.5%          | 2.48%         |                      3.76 | ✅ 16k -4.0%, ✅ 32k -10.7%     |
| NLLB-200 (multilingual)       | 256k    | Ewe           | 1.54                   | 12.7%          | 0.02%         |                      3.64 | ✅ 16k -7.1%, ✅ 32k -13.6%     |

- **Twi (Asante), Leke BPE (16k)**: fertility 1.49, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Twi (tw, 8k), NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Twi (tw, 32k), Goldfish Akan (aka_latn_full), Goldfish Twi (twi_latn_full), Wikilangs Twi (tw, 16k).
- **Twi (Asante), Leke BPE (32k)**: fertility 1.4, `<unk>` rate 0.0%. Lower fertility than: Goldfish Akan (aka_latn_full), Goldfish Twi (twi_latn_full), Wikilangs Twi (tw, 16k), Wikilangs Twi (tw, 8k), NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Twi (tw, 32k).
- **Twi (Akuapem), Leke BPE (16k)**: fertility 1.44, `<unk>` rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Twi (tw, 32k), Goldfish Akan (aka_latn_full), Goldfish Twi (twi_latn_full), Wikilangs Twi (tw, 16k), Wikilangs Twi (tw, 8k).
- **Twi (Akuapem), Leke BPE (32k)**: fertility 1.36, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Twi (tw, 16k), Wikilangs Twi (tw, 8k), NLLB-200 (multilingual). Higher or equal fertility: Wikilangs Twi (tw, 32k), Goldfish Akan (aka_latn_full), Goldfish Twi (twi_latn_full).
- **Ewe, Leke BPE (16k)**: fertility 1.43, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Ewe (ee, 16k), Wikilangs Ewe (ee, 8k), NLLB-200 (multilingual). Higher or equal fertility: Goldfish Ewe (ewe_latn_full), Wikilangs Ewe (ee, 32k).
- **Ewe, Leke BPE (32k)**: fertility 1.33, `<unk>` rate 0.0%. Lower fertility than: Wikilangs Ewe (ee, 32k), Wikilangs Ewe (ee, 16k), Wikilangs Ewe (ee, 8k), NLLB-200 (multilingual). Higher or equal fertility: Goldfish Ewe (ewe_latn_full).
