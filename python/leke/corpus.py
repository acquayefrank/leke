"""Corpus ingestion, normalization filtering, stratified splitting, and temperature upsampling.

High-quality subword tokenizers require clean, balanced, and strictly isolated corpora.
This module provides the complete dataset preprocessing pipeline for Kwa languages:

1. **Corpus Ingestion & Normalization**:
   - Cleans raw text lines, standardizes Unicode codepoints (NFC), replaces non-standard
     phonetic glyph variants (e.g., standardizing open-e / open-o), and collapses whitespace.
   - Filters out noise (e.g., lines with fewer than 3 words or greater than 250 words).
   - Performs exact string deduplication while preserving chronological document order.

2. **Stratified Splitting (80/10/10)**:
   - Deterministically partitions each language's corpus into Train (80%), Dev (10%),
     and Test (10%) splits using a seeded random generator (seed=42).
   - Enforces strict mathematical isolation: asserts 0% data leakage across sets.

3. **Temperature-Scaled Upsampling**:
   - Combines individual language splits into a unified `pooled_train.txt`.
   - High-resource languages (e.g., Akan/Twi) naturally have larger text corpora than
     lower-resource languages (Ga, Fante). Standard pooling would cause high-resource
     languages to monopolize vocabulary capacity.
   - We employ temperature upsampling where language sampling probability is scaled:
         P(L_i) ~ (Count(L_i))^alpha
     Setting alpha=0.5 (square-root scaling) dampens high-resource dominance while
     boosting low-resource representation.

4. **Data Manifest & Checksums**:
   - Computes cryptographic SHA-256 digests for every generated split, recording line counts
     and tiers into `data/data_manifest.json` for reproducible provenance.

Examples:
    >>> from leke.corpus import run_pipeline
    >>> manifest = run_pipeline()
    >>> print(manifest["pooled"]["sentences"])
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Attempt to load the native Rust KwaNormalizer from the compiled extension.
try:
    from leke._leke import KwaNormalizer
except ImportError:
    # Fallback to python/leke/__init__.py stub if uncompiled.
    from leke import KwaNormalizer  # type: ignore

# Target Kwa languages categorized into release tiers.
DEFAULT_LANGUAGES: List[str] = ["twi", "ewe", "gaa", "fat"]
PRIMARY_LANGUAGES: Set[str] = {"twi", "ewe"}


def sha256_of_file(filepath: Path) -> str:
    """Computes the cryptographic SHA-256 checksum of a file on disk.

    Args:
        filepath (Path): Path to the target file.

    Returns:
        str: Hexadecimal SHA-256 digest string.

    Notes:
        Reads the file in streaming 64-kilobyte chunks rather than loading the entire
        file into memory, ensuring low RAM utilization even on large corpora.

    Examples:
        >>> digest = sha256_of_file(Path("data/samples/twi.txt"))
        >>> len(digest)
        64
    """
    # Step 1: Initialize the SHA-256 hashing context from hashlib.
    h = hashlib.sha256()

    # Step 2: Open the binary file stream.
    with open(filepath, "rb") as f:
        # Step 3: Stream 65,536-byte (64 KB) blocks until EOF.
        while chunk := f.read(65536):
            # Update the hash accumulator with the chunk bytes.
            h.update(chunk)

    # Step 4: Return the finalized hexadecimal digest.
    return h.hexdigest()


class CorpusProcessor:
    """Cleans, normalizes, and filters raw text lines for Kwa tokenization.

    Attributes:
        normalizer (KwaNormalizer): Instance of the normalization engine.
        min_words (int): Minimum whitespace-delimited tokens required to keep a line.
        max_words (int): Maximum allowable tokens per line before filtering.
    """

    def __init__(
        self,
        normalizer: Optional[KwaNormalizer] = None,
        min_words: int = 3,
        max_words: int = 250,
    ) -> None:
        """Initializes the processor with normalizer and length filtering constraints.

        Args:
            normalizer (Optional[KwaNormalizer], optional): Native normalizer instance.
                If None, instantiates a default KwaNormalizer.
            min_words (int, optional): Minimum word count filter. Defaults to 3.
            max_words (int, optional): Maximum word count filter. Defaults to 250.
        """
        # Assign or instantiate the native Kwa normalizer.
        self.normalizer = normalizer or KwaNormalizer()
        # Set the lower word-count boundary to reject headers, dates, and noise.
        self.min_words = min_words
        # Set the upper word-count boundary to reject merged documents or OCR runaways.
        self.max_words = max_words

    def clean_line(self, line: str) -> Optional[str]:
        """Normalizes and validates a single line.

        Args:
            line (str): Raw input sentence or paragraph.

        Returns:
            Optional[str]: The normalized line, or None if rejected.

        Notes:
            1. Strips leading and trailing whitespace.
            2. Rejects empty lines immediately.
            3. Passes text to `KwaNormalizer` to enforce Unicode NFC, standardize
               variant glyphs, and collapse consecutive whitespace.
            4. Splits line into words to verify word-count boundaries.
            5. Returns the cleaned text, or None if the line is filtered out.

        Examples:
            >>> proc = CorpusProcessor()
            >>> proc.clean_line("  Akwaaba   ba Ghana  ")
            'Akwaaba ba Ghana'
        """
        # Step 1: Strip outer whitespace characters.
        text = line.strip()

        # Step 2: Discard empty lines.
        if not text:
            return None

        # Step 3: Execute native Unicode NFC and variant orthographic normalization.
        normalized = self.normalizer.normalize(text)

        # Step 4: Calculate word count on normalized text.
        words = normalized.split()

        # Step 5: Filter out lines that fail word-count sanity bounds.
        if len(words) < self.min_words or len(words) > self.max_words:
            return None

        # Step 6: Return the validated normalized line.
        return normalized

    def process_lines(self, lines: List[str]) -> List[str]:
        """Deduplicates and normalizes a sequence of lines preserving original document order.

        Args:
            lines (List[str]): Sequence of raw text strings.

        Returns:
            List[str]: Cleaned, normalized, and deduplicated list of lines.

        Notes:
            Deduplication is critical in tokenizer training because repeated sentences
            artificially inflate subword counts, causing frequent phrases to be merged
            into monolithic single tokens. We use a set for O(1) membership checks while
            maintaining a list to preserve deterministic document ordering.
        """
        # Maintain a hash set of observed lines for fast O(1) deduplication.
        seen: Set[str] = set()
        # Maintain an ordered list to collect unique, normalized lines.
        cleaned: List[str] = []

        # Iterate sequentially through each raw line.
        for line in lines:
            # Clean and validate the line.
            cleaned_line = self.clean_line(line)

            # If the line passed filtering and has not been encountered yet:
            if cleaned_line and cleaned_line not in seen:
                # Mark as seen in the hash set.
                seen.add(cleaned_line)
                # Append to the final ordered output list.
                cleaned.append(cleaned_line)

        # Return the processed lines.
        return cleaned


def split_dataset(
    lines: List[str],
    train_ratio: float = 0.8,
    dev_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> Tuple[List[str], List[str], List[str]]:
    """Deterministically splits lines into train, dev, and test sets with 0% overlap.

    Args:
        lines (List[str]): Cleaned list of text lines.
        train_ratio (float, optional): Proportion for training set. Defaults to 0.8.
        dev_ratio (float, optional): Proportion for validation set. Defaults to 0.1.
        test_ratio (float, optional): Proportion for held-out test set. Defaults to 0.1.
        seed (int, optional): Fixed seed for deterministic shuffling. Defaults to 42.

    Returns:
        Tuple[List[str], List[str], List[str]]: (train_lines, dev_lines, test_lines).

    Raises:
        AssertionError: If ratios do not sum to 1.0 or if data contamination occurs.

    Notes:
        1. Validates that ratios sum to 1.0 within floating point precision.
        2. Copies the list and shuffles using a seeded PRNG (`random.Random(seed)`).
        3. Computes exact split boundaries.
        4. Slices lines into train, dev, and test sets.
        5. Performs mathematical set intersection assertions to guarantee zero
           contamination between train, development, and test evaluations.
    """
    # Step 1: Validate partition ratios.
    assert abs(train_ratio + dev_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"

    # Step 2: Make a shallow copy of lines so the caller's list is not mutated.
    shuffled = list(lines)

    # Step 3: Instantiate an isolated PRNG with fixed seed for determinism.
    rng = random.Random(seed)

    # Step 4: Shuffle lines in-place.
    rng.shuffle(shuffled)

    # Step 5: Compute partition indices.
    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_dev = int(n * dev_ratio)

    # Step 6: Slice the shuffled array into dedicated partitions.
    train_lines = shuffled[:n_train]
    dev_lines = shuffled[n_train : n_train + n_dev]
    test_lines = shuffled[n_train + n_dev :]

    # Step 7: Enforce zero-leakage assertions.
    assert len(set(train_lines) & set(dev_lines)) == 0, "Train and Dev overlap detected!"
    assert len(set(train_lines) & set(test_lines)) == 0, "Train and Test overlap detected!"
    assert len(set(dev_lines) & set(test_lines)) == 0, "Dev and Test overlap detected!"

    # Step 8: Return the three partitions.
    return train_lines, dev_lines, test_lines


def temperature_upsample(
    lang_train_lines: Dict[str, List[str]],
    alpha: float = 0.5,
    total_samples: Optional[int] = None,
    seed: int = 42,
) -> List[str]:
    """Generates a balanced pooled training dataset using temperature upsampling.

    Args:
        lang_train_lines (Dict[str, List[str]]): Dictionary mapping language code to training lines.
        alpha (float, optional): Temperature exponent in [0.0, 1.0]. Defaults to 0.5.
        total_samples (Optional[int], optional): Total lines in pooled output.
            If None, defaults to the sum of all input language lines.
        seed (int, optional): Fixed seed for deterministic sampling. Defaults to 42.

    Returns:
        List[str]: Balanced, temperature-upsampled list of lines for pooled training.

    Notes:
        When training a multilingual tokenizer across high-resource languages (e.g. Twi)
        and lower-resource languages (e.g. Ga or Fante), naive concatenation leads
        to vocabulary bias. Temperature sampling modifies the probability of drawing
        from language L_i according to:
            P(L_i) = (Count(L_i))^alpha / sum_j (Count(L_j))^alpha

        - alpha = 1.0: Natural distribution (proportional to raw corpus size).
        - alpha = 0.0: Perfectly uniform distribution across all languages.
        - alpha = 0.5: Sub-linear square-root scaling (standard in modern multilingual models).
    """
    # Step 1: Count valid lines per language.
    counts = {lang: len(lines) for lang, lines in lang_train_lines.items() if len(lines) > 0}
    if not counts:
        return []

    # Step 2: Apply temperature exponent alpha to each language's sentence count.
    powered = {lang: count**alpha for lang, count in counts.items()}

    # Step 3: Compute normalizing partition sum.
    total_powered = sum(powered.values())

    # Step 4: Compute normalized sampling probabilities.
    probs = {lang: p / total_powered for lang, p in powered.items()}

    # Step 5: Default total sample size to original corpus size if unspecified.
    if total_samples is None:
        total_samples = sum(counts.values())

    # Step 6: Initialize isolated PRNG.
    rng = random.Random(seed)
    langs = list(probs.keys())
    weights = [probs[lang] for lang in langs]

    pooled: List[str] = []

    # Step 7: Sample languages proportionally to computed temperature weights.
    for _ in range(total_samples):
        # Choose a language using weighted lottery selection.
        chosen_lang = rng.choices(langs, weights=weights, k=1)[0]
        # Choose a random sentence from that language with replacement.
        chosen_line = rng.choice(lang_train_lines[chosen_lang])
        pooled.append(chosen_line)

    # Step 8: Return the pooled dataset.
    return pooled


def run_pipeline(
    raw_dir: Path = Path("data/samples"),
    output_dir: Path = Path("data/splits"),
    manifest_path: Path = Path("data/data_manifest.json"),
    alpha: float = 0.5,
    seed: int = 42,
    extra_train_dirs: Optional[List[Path]] = None,
    pooled_path: Optional[Path] = None,
    total_samples: Optional[int] = None,
) -> Dict[str, Any]:
    """Executes the complete corpus ingestion, splitting, upsampling, and manifest generation.

    Args:
        raw_dir (Path, optional): Directory containing raw sample files. Defaults to Path("data/samples").
        output_dir (Path, optional): Output directory for split files. Defaults to Path("data/splits").
        manifest_path (Path, optional): Path to write the JSON manifest. Defaults to Path("data/data_manifest.json").
        alpha (float, optional): Temperature sampling factor. Defaults to 0.5.
        seed (int, optional): Fixed random seed. Defaults to 42.
        extra_train_dirs (Optional[List[Path]], optional): Directories of `<lang>.txt`
            files whose lines are added to that language's training lines only (never to
            dev/test), e.g. MADLAD-400 text from `scripts/fetch_madlad.py`. Defaults to None.
        pooled_path (Optional[Path], optional): Where to write the pooled training file.
            Defaults to `output_dir / "pooled_train.txt"`.
        total_samples (Optional[int], optional): Lines to draw for the pooled file.
            Defaults to the total number of training lines.

    Returns:
        Dict[str, Any]: Complete provenance manifest dictionary.

    Notes:
        1. Iterates over target Kwa languages (`twi`, `ewe`, `gaa`, `fat`).
        2. Ingests raw text files from `raw_dir`.
        3. Cleans, normalizes, and deduplicates lines via `CorpusProcessor`.
        4. Partitions lines into 80/10/10 train/dev/test splits.
        5. Writes split files into `data/splits/<lang>/`.
        6. Computes SHA-256 hashes of all written files for provenance.
        7. Performs temperature upsampling (alpha=0.5) to produce `data/splits/pooled_train.txt`.
        8. Serializes all statistics, line counts, and checksums to `data_manifest.json`.
    """
    # Step 1: Initialize corpus processor and ensure output directories exist.

    processor = CorpusProcessor()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Initialize metadata structure for the data manifest.
    manifest: Dict[str, Any] = {
        "version": "1.0.0",
        "seed": seed,
        "temperature_alpha": alpha,
        "languages": {},
        "pooled": {},
    }

    # Dictionary to collect training lines across languages for pooled dataset creation.
    train_lines_by_lang: Dict[str, List[str]] = {}

    # Step 3: Process each target language individually.
    for lang in DEFAULT_LANGUAGES:
        sample_file = raw_dir / f"{lang}.txt"
        if not sample_file.exists():
            continue

        # Read all raw lines using UTF-8 encoding.
        with open(sample_file, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        # Clean and deduplicate lines.
        cleaned_lines = processor.process_lines(raw_lines)

        # Split into 80/10/10 partitions.
        train, dev, test = split_dataset(cleaned_lines, seed=seed)

        # Store training lines for pooled upsampling, plus any extra training-only text.
        pool_lines = list(train)
        seen = set(train) | set(dev) | set(test)
        for extra_dir in extra_train_dirs or []:
            extra_file = extra_dir / f"{lang}.txt"
            if not extra_file.exists():
                continue
            with open(extra_file, "r", encoding="utf-8") as f:
                extra = [
                    line for line in processor.process_lines(f.readlines()) if line not in seen
                ]
            seen.update(extra)
            pool_lines.extend(extra)
        train_lines_by_lang[lang] = pool_lines

        # Create language-specific output directory.
        lang_dir = output_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        train_path = lang_dir / "train.txt"
        dev_path = lang_dir / "dev.txt"
        test_path = lang_dir / "test.txt"

        # Write partitioned text files.
        train_path.write_text("\n".join(train) + "\n", encoding="utf-8")
        dev_path.write_text("\n".join(dev) + "\n", encoding="utf-8")
        test_path.write_text("\n".join(test) + "\n", encoding="utf-8")

        # Record file metadata and SHA-256 digests in manifest.
        manifest["languages"][lang] = {
            "tier": "primary" if lang in PRIMARY_LANGUAGES else "secondary",
            "total_cleaned_sentences": len(cleaned_lines),
            "train_sentences": len(train),
            "dev_sentences": len(dev),
            "test_sentences": len(test),
            "extra_train_sentences": len(pool_lines) - len(train),
            "hashes": {
                "train_sha256": sha256_of_file(train_path),
                "dev_sha256": sha256_of_file(dev_path),
                "test_sha256": sha256_of_file(test_path),
            },
        }

    # Step 4: Generate balanced pooled training dataset across languages.
    pooled_train = temperature_upsample(
        train_lines_by_lang, alpha=alpha, total_samples=total_samples, seed=seed
    )
    pooled_path = pooled_path or output_dir / "pooled_train.txt"
    pooled_path.write_text("\n".join(pooled_train) + "\n", encoding="utf-8")

    # Step 5: Record pooled corpus statistics and cryptographic hash.
    manifest["pooled"] = {
        "sentences": len(pooled_train),
        "sha256": sha256_of_file(pooled_path),
    }

    # Step 6: Write JSON manifest to disk.
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Step 7: Return manifest dictionary.
    return manifest


# Execute pipeline directly if run as a script.
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build splits and the pooled training file.")
    parser.add_argument("--alpha", type=float, default=0.5, help="Temperature exponent")
    parser.add_argument(
        "--extra-train-dir",
        type=Path,
        nargs="+",
        default=None,
        help="Directories of <lang>.txt training-only text (e.g. data/raw/madlad)",
    )
    parser.add_argument("--pooled-out", type=Path, default=None, help="Pooled output path")
    parser.add_argument("--manifest-out", type=Path, default=Path("data/data_manifest.json"))
    parser.add_argument(
        "--total-samples", type=int, default=None, help="Lines to draw for the pooled file"
    )
    args = parser.parse_args()
    m = run_pipeline(
        manifest_path=args.manifest_out,
        alpha=args.alpha,
        extra_train_dirs=args.extra_train_dir,
        pooled_path=args.pooled_out,
        total_samples=args.total_samples,
    )
    print("Corpus pipeline finished successfully. Manifest:")
    print(json.dumps(m, indent=2))
