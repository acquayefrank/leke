# Leke Subword Tokenizer — Evaluation Leaderboard

This report compiles the official evaluation benchmarks across held-out test splits for Kwa languages (`twi`, `ewe`, `gaa`, `fat`), testing adherence to the release gates defined in `specs/mission.md`.

## Held-Out Test Evaluation

| Model                       | Language   | Fertility (tok/word)   | Split >2 (%)   | Unknown (%)   |   Compression (bytes/tok) | Status                    |
|-----------------------------|------------|------------------------|----------------|---------------|---------------------------|---------------------------|
| **Leke BPE (8k)**           | Akan / Twi | **1.48**               | 21.5%          | **0.0%**      |                      3.75 | ✅ Target Evaluated        |
| Goldfish Twi (monolingual)  | Akan / Twi | 1.62                   | 16.8%          | 0.4%          |                      4.12 | ✅ Matched/Beat (Baseline) |
| NLLB-200 (multilingual)     | Akan / Twi | 2.92                   | 38.4%          | 0.0%          |                      2.45 | ✅ Leke Superior           |
| **Leke BPE (8k)**           | Ewe        | **1.37**               | 16.5%          | **0.0%**      |                      4.27 | ✅ Target Evaluated        |
| Wikilangs Ewe (monolingual) | Ewe        | 1.71                   | 19.3%          | 0.6%          |                      3.95 | ✅ Matched/Beat (Baseline) |
| NLLB-200 (multilingual)     | Ewe        | 3.15                   | 44.1%          | 0.0%          |                      2.28 | ✅ Leke Superior           |
| **Leke BPE (8k)**           | Ga         | **1.41**               | 17.7%          | **0.0%**      |                      4.33 | ✅ Target Evaluated        |
| NLLB-200 (multilingual)     | Ga         | 3.2                    | 46.2%          | 0.0%          |                      2.2  | ✅ Leke Superior           |
| **Leke BPE (8k)**           | Fante      | **1.34**               | 15.4%          | **0.0%**      |                      4.11 | ✅ Target Evaluated        |
| NLLB-200 (multilingual)     | Fante      | 2.98                   | 39.5%          | 0.0%          |                      2.4  | ✅ Leke Superior           |

## Release Gate Analysis

1. **Akan / Twi Gate**:
   - Leke BPE-8k achieves low fertility with 0.0% unknown tokens, beating the multilingual NLLB baseline and the monolingual Goldfish Twi baseline on fertility.
2. **Ewe Gate**:
   - Leke BPE-8k achieves compact subword representation with 0.0% unknown tokens, outperforming both NLLB and the monolingual Wikilangs Ewe baseline on fertility.
3. **Zero OOV Guarantee**:
   - Zero `<unk>` tokens emitted across 100% of the held-out evaluation text due to byte-level fallback.
4. **Secondary Languages (Ga and Fante)**:
   - Both secondary languages exhibit low fertility and 0% unknown tokens.
