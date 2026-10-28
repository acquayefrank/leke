# Subword Architectural Selection — Byte-Level BPE vs. Unigram

This document records the empirical head-to-head comparison between **Byte-Level BPE** and **Unigram** models trained on identical multi-language Kwa corpora (`data/splits/pooled_train.txt`) with fixed seed 42 and evaluated on held-out test splits.

## Head-to-Head Benchmark Matrix

| Language   |   BPE Fertility |   Uni Fertility | BPE Split >2   | Uni Split >2   | BPE Unk (%)   | Uni Unk (%)   |   BPE Comp. |   Uni Comp. | Advantage   |
|------------|-----------------|-----------------|----------------|----------------|---------------|---------------|-------------|-------------|-------------|
| Akan / Twi |            1.38 |            1.45 | 8.0%           | 8.8%           | 0.0%          | 0.0%          |        4.01 |        3.81 | **BPE**     |
| Ewe        |            1.45 |            1.42 | 10.4%          | 9.9%           | 0.0%          | 0.04%         |        4.03 |        4.12 | **Unigram** |
| Ga         |            1.39 |            1.5  | 7.9%           | 11.0%          | 0.0%          | 0.0%          |        4.39 |        4.06 | **BPE**     |
| Fante      |            1.34 |            1.36 | 6.2%           | 7.0%           | 0.0%          | 0.0%          |        4.11 |        4.03 | **BPE**     |

## Summary Averages Across All Languages

| Metric | Byte-Level BPE | Unigram | Winner |
| :--- | :--- | :--- | :--- |
| **Mean Fertility (tokens/word)** | **1.39** | 1.43 | **Byte-Level BPE** |
| **Mean Excessive Split Rate (>2)** | **8.1%** | 9.2% | **Byte-Level BPE** |
| **Mean Unknown Token Rate** | **0.0%** | 0.01% | **Byte-Level BPE** |

## Architectural Decision & Conclusion

1. **Fertility & Fragmentation**:
   - **Byte-Level BPE** has lower fertility on 3 of 4 languages (mean 1.39 vs. 1.43 tokens/word), with a strict 0.0% unknown-token rate from its byte-level fallback.
   - Unigram has no byte fallback, so it can emit `<unk>` tokens on characters missing from its vocabulary (mean 0.01%).
   - This occurs because BPE greedily merges high-frequency adjacent syllable affixes (CV, CVC), perfectly aligning with Niger-Congo agglutinative and compound word morphology.
2. **Standard Ecosystem Interoperability**:
   - Byte-Level BPE is the standard subword architecture for state-of-the-art transformer LLMs (GPT-4, LLaMA-3, Mistral, Gemma).
   - Byte-level encoding natively handles any arbitrary binary byte sequence without out-of-vocabulary risk.
3. **Final Verdict**:
   - **Byte-Level BPE is selected as the default production algorithm for Leke.**
   - Unigram will remain supported in the training engine as a configurable option for downstream research workflows that specifically require probabilistic subword regularization.
