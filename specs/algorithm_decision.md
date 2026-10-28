# Subword Architectural Selection — Byte-Level BPE vs. Unigram

This document records the empirical head-to-head comparison between **Byte-Level BPE** and **Unigram** models trained on identical multi-language Kwa corpora (`data/splits/pooled_train.txt`) with fixed seed 42 and evaluated on held-out test splits.

## Head-to-Head Benchmark Matrix

| Language   |   BPE Fertility |   Uni Fertility | BPE Split >2   | Uni Split >2   | BPE Unk (%)   | Uni Unk (%)   |   BPE Comp. |   Uni Comp. | Advantage   |
|------------|-----------------|-----------------|----------------|----------------|---------------|---------------|-------------|-------------|-------------|
| Akan / Twi |            1.48 |            1.59 | 10.9%          | 12.2%          | 0.0%          | 0.01%         |        3.73 |        3.47 | **BPE**     |
| Ewe        |            1.41 |            1.38 | 9.4%           | 8.7%           | 0.0%          | 0.04%         |        4.14 |        4.24 | **Unigram** |
| Ga         |            1.4  |            1.52 | 8.2%           | 11.6%          | 0.0%          | 0.0%          |        4.38 |        4.01 | **BPE**     |
| Fante      |            1.3  |            1.34 | 5.6%           | 5.9%           | 0.0%          | 0.0%          |        4.24 |        4.09 | **BPE**     |

## Summary Averages Across All Languages

| Metric | Byte-Level BPE | Unigram | Winner |
| :--- | :--- | :--- | :--- |
| **Mean Fertility (tokens/word)** | **1.4** | 1.46 | **Byte-Level BPE** |
| **Mean Excessive Split Rate (>2)** | **8.5%** | 9.6% | **Byte-Level BPE** |
| **Mean Unknown Token Rate** | **0.0%** | 0.01% | **Byte-Level BPE** |

## Architectural Decision & Conclusion

1. **Fertility & Fragmentation**:
   - **Byte-Level BPE** has lower fertility on 3 of 4 languages (mean 1.4 vs. 1.46 tokens/word), with a strict 0.0% unknown-token rate from its byte-level fallback.
   - Unigram has no byte fallback, so it can emit `<unk>` tokens on characters missing from its vocabulary (mean 0.01%).
   - This occurs because BPE greedily merges high-frequency adjacent syllable affixes (CV, CVC), perfectly aligning with Niger-Congo agglutinative and compound word morphology.
2. **Standard Ecosystem Interoperability**:
   - Byte-Level BPE is the standard subword architecture for state-of-the-art transformer LLMs (GPT-4, LLaMA-3, Mistral, Gemma).
   - Byte-level encoding natively handles any arbitrary binary byte sequence without out-of-vocabulary risk.
3. **Final Verdict**:
   - **Byte-Level BPE is selected as the default production algorithm for Leke.**
   - Unigram will remain supported in the training engine as a configurable option for downstream research workflows that specifically require probabilistic subword regularization.
