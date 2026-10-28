"""Tokenizer training orchestrator and CLI interface for Leke.

This module orchestrates the training of subword tokenizers on single or multi-language
Kwa text corpora. It provides Python functions and a command-line interface (CLI)
for two primary subword algorithms:
    1. **Byte-Level Byte-Pair Encoding (BPE)**:
       - Iteratively merges the most frequent adjacent byte or character pairs.
       - Employs a byte-level fallback to ensure that every single UTF-8 byte
         is represented, guaranteeing a 0% out-of-vocabulary (<unk>) rate.
    2. **Unigram Language Model**:
       - Starts from a large seed vocabulary and iteratively prunes subwords
         that minimize the loss in corpus likelihood via the Expectation-Maximization (EM) algorithm.

Provenance & Reproducibility:
    Every training run automatically generates two artifacts in the destination directory:
        - `tokenizer.json`: The complete Hugging Face-compatible serialized tokenizer.
        - `training_receipt.json`: A deterministic receipt containing SHA-256 checksums
          of the input training files, line counts, random seed, vocabulary size,
          and hyperparameter configurations.

Examples:
    >>> from leke.trainer import train_bpe
    >>> receipt = train_bpe(
    ...     corpus_paths="data/splits/pooled_train.txt",
    ...     output_dir="models/bpe-8k",
    ...     vocab_size=8192,
    ...     seed=42,
    ... )
    >>> print(receipt["algorithm"])
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import native Rust trainer bindings compiled via PyO3.
from leke._leke import train_bpe_model, train_unigram_model


def train_bpe(
    corpus_paths: Union[str, Path, List[Union[str, Path]]],
    output_dir: Union[str, Path],
    vocab_size: int = 8192,
    min_frequency: int = 1,
    special_tokens: Optional[List[str]] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """Trains a Byte-Level BPE tokenizer on input text file(s) and writes the bundle.

    Args:
        corpus_paths (Union[str, Path, List[Union[str, Path]]]): One or more file paths
            pointing to plain-text UTF-8 training corpora.
        output_dir (Union[str, Path]): Destination directory to save the trained tokenizer.
        vocab_size (int, optional): Target subword vocabulary size. Defaults to 8192.
        min_frequency (int, optional): Minimum occurrence count required for a merge. Defaults to 1.
        special_tokens (Optional[List[str]], optional): Custom special tokens to prepend to
            the vocabulary. If None, defaults to `["<pad>", "<s>", "</s>", "<unk>", "<mask>"]`.
        seed (int, optional): Random seed for deterministic vocabulary tie-breaking. Defaults to 42.

    Returns:
        Dict[str, Any]: A receipt dictionary containing training statistics and file hashes.

    Raises:
        FileNotFoundError: If any of the corpus paths do not exist.
        RuntimeError: If training fails inside the native Rust engine.

    Notes:
        1. Paths are converted into an array of string paths for the Rust C-bridge.
        2. The native Rust engine opens the corpus files with multi-threaded chunk readers.
        3. Initial character frequencies are counted, and the 256 basic byte tokens are populated.
        4. Successive merges are executed until `vocab_size` is reached.
        5. `tokenizer.json` and `training_receipt.json` are written to `output_dir`.
        6. The provenance metadata dictionary is returned to Python.

    Examples:
        >>> receipt = train_bpe("data/samples/twi.txt", "models/bpe-8k", vocab_size=8192)
    """
    # Step 1: Normalize input corpus path(s) into a list of absolute/relative string paths.
    if isinstance(corpus_paths, (str, Path)):
        # Wrap single string or Path instance into a single-element list.
        paths = [str(corpus_paths)]
    else:
        # Convert an iterable of paths into string representations.
        paths = [str(p) for p in corpus_paths]

    # Step 2: Normalize output directory to a string path.
    out_dir = str(output_dir)

    # Step 3: Invoke the high-performance native Rust training engine.
    receipt_json = train_bpe_model(
        corpus_paths=paths,
        output_dir=out_dir,
        vocab_size=vocab_size,
        min_frequency=min_frequency,
        special_tokens=special_tokens,
        seed=seed,
    )

    # Step 4: Parse the JSON provenance receipt returned by Rust into a Python dictionary.
    return json.loads(receipt_json)


def train_unigram(
    corpus_paths: Union[str, Path, List[Union[str, Path]]],
    output_dir: Union[str, Path],
    vocab_size: int = 8192,
    special_tokens: Optional[List[str]] = None,
    seed: int = 42,
) -> Dict[str, Any]:
    """Trains a Unigram tokenizer on input text file(s) and writes the bundle.

    Args:
        corpus_paths (Union[str, Path, List[Union[str, Path]]]): One or more file paths
            pointing to plain-text UTF-8 training corpora.
        output_dir (Union[str, Path]): Destination directory to save the trained tokenizer.
        vocab_size (int, optional): Target subword vocabulary size. Defaults to 8192.
        special_tokens (Optional[List[str]], optional): Custom special tokens. If None,
            defaults to `["<pad>", "<s>", "</s>", "<unk>", "<mask>"]`.
        seed (int, optional): Random seed for deterministic EM convergence. Defaults to 42.

    Returns:
        Dict[str, Any]: A receipt dictionary containing training statistics and file hashes.

    Raises:
        FileNotFoundError: If any of the corpus paths do not exist.
        RuntimeError: If training fails inside the native Rust engine.

    Notes:
        Unlike BPE, which builds subwords from the bottom up, Unigram starts with an
        overly large seed vocabulary and iteratively prunes symbols that contribute least
        to the likelihood of the corpus under an unigram language model.
        This provides probabilistic subword segmentation capability (subword regularization).

    Examples:
        >>> receipt = train_unigram("data/samples/ewe.txt", "models/unigram-8k", vocab_size=8192)
    """
    # Step 1: Normalize input corpus paths into a list of string paths.
    if isinstance(corpus_paths, (str, Path)):
        paths = [str(corpus_paths)]
    else:
        paths = [str(p) for p in corpus_paths]

    # Step 2: Normalize output directory to a string path.
    out_dir = str(output_dir)

    # Step 3: Invoke the native Rust Unigram training engine.
    receipt_json = train_unigram_model(
        corpus_paths=paths,
        output_dir=out_dir,
        vocab_size=vocab_size,
        special_tokens=special_tokens,
        seed=seed,
    )

    # Step 4: Parse and return the training receipt.
    return json.loads(receipt_json)


def main() -> None:
    """CLI entrypoint for training Kwa subword tokenizers.

    Notes:
        Parses command-line arguments to allow direct CLI training via:
        `python -m leke.trainer --algorithm bpe --corpus data/splits/pooled_train.txt ...`
    """
    # Step 1: Initialize the command-line argument parser with descriptive documentation.
    parser = argparse.ArgumentParser(description="Train tokenizer for Kwa languages.")

    # Step 2: Configure CLI flags and default values.
    parser.add_argument(
        "--algorithm",
        type=str,
        choices=["bpe", "unigram"],
        default="bpe",
        help="Algorithm to train (bpe or unigram)",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="data/splits/pooled_train.txt",
        help="Path to training corpus file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/bpe-8k",
        help="Output directory for tokenizer bundle",
    )
    parser.add_argument(
        "--vocab-size",
        type=int,
        default=8192,
        help="Target vocabulary size (default: 8192)",
    )
    parser.add_argument(
        "--min-frequency",
        type=int,
        default=1,
        help="Minimum token frequency for BPE (default: 1)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    # Step 3: Parse the command-line arguments.
    args = parser.parse_args()

    # Step 4: Route execution to the chosen algorithm.
    if args.algorithm == "unigram":
        # Train Unigram model.
        receipt = train_unigram(
            corpus_paths=args.corpus,
            output_dir=args.output_dir,
            vocab_size=args.vocab_size,
            seed=args.seed,
        )
    else:
        # Train Byte-Level BPE model (default).
        receipt = train_bpe(
            corpus_paths=args.corpus,
            output_dir=args.output_dir,
            vocab_size=args.vocab_size,
            min_frequency=args.min_frequency,
            seed=args.seed,
        )

    # Step 5: Log confirmation and pretty-print the provenance receipt.
    print(f"Training completed successfully! Saved to {args.output_dir}")
    print(json.dumps(receipt, indent=2))


# Execute CLI main if called directly as a script.
if __name__ == "__main__":
    main()
