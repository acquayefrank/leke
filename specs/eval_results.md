# Leke Subword Tokenizer — Evaluation Leaderboard

This report compiles the official evaluation benchmarks across held-out test splits for Kwa languages (`twi`, `ewe`, `gaa`, `fat`), comparing Leke against baseline tokenizers measured on the same splits by `scripts/measure_baselines.py`.

## Held-Out Test Evaluation

| Model                         | Vocab   | Language   | Fertility (tok/word)   | Split >2 (%)   | Unknown (%)   |   Compression (bytes/tok) | Leke fertility vs. baseline   |
|-------------------------------|---------|------------|------------------------|----------------|---------------|---------------------------|-------------------------------|
| **Leke BPE (8k)**             | 8k      | Akan / Twi | **1.48**               | 11.5%          | **0.0%**      |                      3.75 | —                             |
| Wikilangs Twi (tw, 32k)       | 32k     | Akan / Twi | 1.24                   | 4.5%           | 0.11%         |                      4.46 | ⚠️ Baseline lower (+19.4%)    |
| Goldfish Twi (twi_latn_full)  | 50k     | Akan / Twi | 1.28                   | 5.4%           | 0.0%          |                      4.31 | ⚠️ Baseline lower (+15.6%)    |
| Goldfish Akan (aka_latn_full) | 50k     | Akan / Twi | 1.28                   | 5.2%           | 0.0%          |                      4.31 | ⚠️ Baseline lower (+15.6%)    |
| Wikilangs Twi (tw, 8k)        | 8k      | Akan / Twi | 1.34                   | 7.4%           | 0.1%          |                      4.12 | ⚠️ Baseline lower (+10.4%)    |
| NLLB-200 (multilingual)       | 256k    | Akan / Twi | 1.55                   | 12.6%          | 0.26%         |                      3.57 | ✅ Leke lower (-4.5%)          |
| **Leke BPE (8k)**             | 8k      | Ewe        | **1.37**               | 8.3%           | **0.0%**      |                      4.27 | —                             |
| Wikilangs Ewe (ee, 32k)       | 32k     | Ewe        | 1.34                   | 7.7%           | 0.11%         |                      4.34 | ⚠️ Baseline lower (+2.2%)     |
| Goldfish Ewe (ewe_latn_full)  | 50k     | Ewe        | 1.35                   | 8.3%           | 0.03%         |                      4.32 | ⚠️ Baseline lower (+1.5%)     |
| Wikilangs Ewe (ee, 8k)        | 8k      | Ewe        | 1.44                   | 10.3%          | 0.11%         |                      4.07 | ✅ Leke lower (-4.9%)          |
| NLLB-200 (multilingual)       | 256k    | Ewe        | 1.65                   | 15.9%          | 0.3%          |                      3.53 | ✅ Leke lower (-17.0%)         |
| **Leke BPE (8k)**             | 8k      | Ga         | **1.41**               | 8.3%           | **0.0%**      |                      4.33 | —                             |
| NLLB-200 (multilingual)       | 256k    | Ga         | 1.93                   | 25.1%          | 0.08%         |                      3.16 | ✅ Leke lower (-26.9%)         |
| **Leke BPE (8k)**             | 8k      | Fante      | **1.34**               | 7.1%           | **0.0%**      |                      4.11 | —                             |
| Wikilangs Fante (fat, 32k)    | 32k     | Fante      | 1.26                   | 5.0%           | 0.02%         |                      4.36 | ⚠️ Baseline lower (+6.3%)     |
| Wikilangs Fante (fat, 8k)     | 8k      | Fante      | 1.38                   | 8.5%           | 0.02%         |                      3.99 | ✅ Leke lower (-2.9%)          |
| Goldfish Akan (aka_latn_full) | 50k     | Fante      | 1.39                   | 8.1%           | 0.0%          |                      3.95 | ✅ Leke lower (-3.6%)          |
| Wikilangs Twi (tw, 32k)       | 32k     | Fante      | 1.51                   | 11.3%          | 0.05%         |                      3.64 | ✅ Leke lower (-11.3%)         |
| NLLB-200 (multilingual)       | 256k    | Fante      | 1.7                    | 17.2%          | 0.61%         |                      3.24 | ✅ Leke lower (-21.2%)         |
| Wikilangs Twi (tw, 8k)        | 8k      | Fante      | 1.71                   | 16.5%          | 0.04%         |                      3.22 | ✅ Leke lower (-21.6%)         |

## Comparison Summary

- **Akan / Twi**: Leke fertility 1.48, <unk> rate 0.0%. Lower fertility than: NLLB-200 (multilingual). Higher fertility than: Wikilangs Twi (tw, 32k), Goldfish Twi (twi_latn_full), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 8k).
- **Ewe**: Leke fertility 1.37, <unk> rate 0.0%. Lower fertility than: Wikilangs Ewe (ee, 8k), NLLB-200 (multilingual). Higher fertility than: Wikilangs Ewe (ee, 32k), Goldfish Ewe (ewe_latn_full).
- **Ga**: Leke fertility 1.41, <unk> rate 0.0%. Lower fertility than: NLLB-200 (multilingual).
- **Fante**: Leke fertility 1.34, <unk> rate 0.0%. Lower fertility than: Wikilangs Fante (fat, 8k), Goldfish Akan (aka_latn_full), Wikilangs Twi (tw, 32k), NLLB-200 (multilingual), Wikilangs Twi (tw, 8k). Higher fertility than: Wikilangs Fante (fat, 32k).
