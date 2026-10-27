"""Tokenizer training orchestrator and CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from leke._leke import train_bpe_model


def train_bpe(
    corpus_paths: Union[str, Path, List[Union[str, Path]]],
    output_dir: Union[str, Path],
    vocab_size: int = 8192,
    min_frequency: int = 1,
    special_tokens: Optional[List[str]] = None,
    seed: int = 42,
) -> Dict:
    """Trains a Byte-Level BPE tokenizer on input text file(s) and writes the bundle."""
    if isinstance(corpus_paths, (str, Path)):
        paths = [str(corpus_paths)]
    else:
        paths = [str(p) for p in corpus_paths]

    out_dir = str(output_dir)
    receipt_json = train_bpe_model(
        corpus_paths=paths,
        output_dir=out_dir,
        vocab_size=vocab_size,
        min_frequency=min_frequency,
        special_tokens=special_tokens,
        seed=seed,
    )
    return json.loads(receipt_json)


def main():
    parser = argparse.ArgumentParser(description="Train Byte-Level BPE tokenizer for Kwa languages.")
    parser.add_argument("--corpus", type=str, default="data/splits/pooled_train.txt", help="Path to training corpus")
    parser.add_argument("--output-dir", type=str, default="models/bpe-8k", help="Output directory for tokenizer bundle")
    parser.add_argument("--vocab-size", type=int, default=8192, help="Target vocabulary size")
    parser.add_argument("--min-frequency", type=int, default=1, help="Minimum token frequency")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()
    receipt = train_bpe(
        corpus_paths=args.corpus,
        output_dir=args.output_dir,
        vocab_size=args.vocab_size,
        min_frequency=args.min_frequency,
        seed=args.seed,
    )
    print(f"Training completed successfully! Saved to {args.output_dir}")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
