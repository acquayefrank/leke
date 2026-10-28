# Subword Architectural Selection — Byte-Level BPE vs. Unigram

This document records the empirical head-to-head comparison between **Byte-Level BPE** and **Unigram** models trained on identical multi-language Kwa corpora (`data/splits/pooled_train.txt`) with fixed seed 42 and evaluated on held-out test splits.

## Head-to-Head Benchmark Matrix

| Language   |   BPE Fertility |   Uni Fertility | BPE Split >2   | Uni Split >2   | BPE Unk (%)   | Uni Unk (%)   |   BPE Comp. |   Uni Comp. | Advantage   |
|------------|-----------------|-----------------|----------------|----------------|---------------|---------------|-------------|-------------|-------------|
| Akan / Twi |            1.48 |            1.52 | 21.5%          | 11.6%          | 0.0%          | 0.05%         |        3.75 |        3.63 | **BPE**     |
| Ewe        |            1.37 |            1.39 | 16.5%          | 6.5%           | 0.0%          | 0.06%         |        4.27 |        4.21 | **BPE**     |
| Ga         |            1.41 |            1.48 | 17.7%          | 9.9%           | 0.0%          | 0.0%          |        4.33 |        4.11 | **BPE**     |
| Fante      |            1.34 |            1.38 | 15.4%          | 7.0%           | 0.0%          | 0.0%          |        4.11 |        3.99 | **BPE**     |

## Summary Averages Across All Languages

| Metric | Byte-Level BPE | Unigram | Winner |
| :--- | :--- | :--- | :--- |
| **Mean Fertility (tokens/word)** | **1.4** | 1.44 | **Byte-Level BPE** |
| **Mean Excessive Split Rate (>2)** | 17.8% | **8.8%** | **Unigram** |
| **Mean Unknown Token Rate** | **0.0%** | 0.03% | **Byte-Level BPE** |

## Architectural Decision & Conclusion

1. **Fertility & Fragmentation**:
   - **Byte-Level BPE** achieves lower tokens-per-word fertility and higher byte compression across all four target Kwa languages (Akan/Twi, Ewe, Ga, and Fante), with a strict 0.0% unknown-token rate.
   - Unigram spreads its splits more evenly, so fewer words break into more than two pieces (lower >2 split rate), but it emits a small number of `<unk>` tokens and produces longer sequences overall.
   - This occurs because BPE greedily merges high-frequency adjacent syllable affixes (CV, CVC), perfectly aligning with Niger-Congo agglutinative and compound word morphology.
2. **Standard Ecosystem Interoperability**:
   - Byte-Level BPE is the standard subword architecture for state-of-the-art transformer LLMs (GPT-4, LLaMA-3, Mistral, Gemma).
   - Byte-level encoding natively handles any arbitrary binary byte sequence without out-of-vocabulary risk.
3. **Final Verdict**:
   - **Byte-Level BPE is selected as the default production algorithm for Leke.**
   - Unigram will remain supported in the training engine as a configurable option for downstream research workflows that specifically require probabilistic subword regularization.
