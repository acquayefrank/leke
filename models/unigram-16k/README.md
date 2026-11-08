# Leke Unigram-16k (experiment, not published)

A Unigram language-model tokenizer with a 16,384-token vocabulary, trained on the same pool as [`bpe-16k`](../bpe-16k/) (`data/raw/pooled_train_extended.txt`, seed 42; see `training_receipt.json`). It exists only for the head-to-head algorithm comparison in [`specs/algorithm_decision.md`](../../specs/algorithm_decision.md), which `scripts/compare_algorithms.py` regenerates from this file.

It is not published to the Hugging Face Hub and is not a supported model. On the held-out curriculum test splits it averages 1.43 tokens per word against 1.39 for `bpe-16k`, winning only on Ewe (1.42 vs 1.45), and with no byte fallback it can emit `<unk>`. Use `bpe-16k` or `bpe-32k` instead.

The folder holds only `tokenizer.json` and `training_receipt.json`, without the `tokenizer_config.json` and `special_tokens_map.json` that `transformers` needs.
