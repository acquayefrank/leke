"""Corpus ingestion, normalization filtering, stratified splitting, and temperature upsampling."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from leke import KwaNormalizer

DEFAULT_LANGUAGES = ["twi", "ewe", "gaa", "fat"]
PRIMARY_LANGUAGES = {"twi", "ewe"}


def sha256_of_file(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class CorpusProcessor:
    """Cleans, normalizes, and filters raw text lines."""

    def __init__(self, normalizer: Optional[KwaNormalizer] = None, min_words: int = 3, max_words: int = 250):
        self.normalizer = normalizer or KwaNormalizer()
        self.min_words = min_words
        self.max_words = max_words

    def clean_line(self, line: str) -> Optional[str]:
        """Normalizes and validates a single line. Returns None if filtered out."""
        text = line.strip()
        if not text:
            return None

        normalized = self.normalizer.normalize(text)
        words = normalized.split()
        if len(words) < self.min_words or len(words) > self.max_words:
            return None

        return normalized

    def process_lines(self, lines: List[str]) -> List[str]:
        """Deduplicates and normalizes a sequence of lines preserving order."""
        seen = set()
        cleaned = []
        for line in lines:
            cleaned_line = self.clean_line(line)
            if cleaned_line and cleaned_line not in seen:
                seen.add(cleaned_line)
                cleaned.append(cleaned_line)
        return cleaned


def split_dataset(
    lines: List[str],
    train_ratio: float = 0.8,
    dev_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> Tuple[List[str], List[str], List[str]]:
    """Deterministically splits lines into train, dev, and test sets with 0% overlap."""
    assert abs(train_ratio + dev_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"

    # Deterministic shuffle
    shuffled = list(lines)
    rng = random.Random(seed)
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_dev = int(n * dev_ratio)

    train_lines = shuffled[:n_train]
    dev_lines = shuffled[n_train : n_train + n_dev]
    test_lines = shuffled[n_train + n_dev :]

    # Assert no contamination
    assert len(set(train_lines) & set(dev_lines)) == 0, "Train and Dev overlap detected!"
    assert len(set(train_lines) & set(test_lines)) == 0, "Train and Test overlap detected!"
    assert len(set(dev_lines) & set(test_lines)) == 0, "Dev and Test overlap detected!"

    return train_lines, dev_lines, test_lines


def temperature_upsample(
    lang_train_lines: Dict[str, List[str]],
    alpha: float = 0.5,
    total_samples: Optional[int] = None,
    seed: int = 42,
) -> List[str]:
    """Generates a balanced pooled training dataset using temperature upsampling: P(L_i) ~ (Count(L_i))^alpha."""
    counts = {lang: len(lines) for lang, lines in lang_train_lines.items() if len(lines) > 0}
    if not counts:
        return []

    powered = {lang: count**alpha for lang, count in counts.items()}
    total_powered = sum(powered.values())
    probs = {lang: p / total_powered for lang, p in powered.items()}

    if total_samples is None:
        total_samples = sum(counts.values())

    rng = random.Random(seed)
    langs = list(probs.keys())
    weights = [probs[lang] for lang in langs]

    pooled: List[str] = []
    # Sample languages proportionally to weights, with replacement per line
    for _ in range(total_samples):
        chosen_lang = rng.choices(langs, weights=weights, k=1)[0]
        chosen_line = rng.choice(lang_train_lines[chosen_lang])
        pooled.append(chosen_line)

    return pooled


def run_pipeline(
    raw_dir: Path = Path("data/samples"),
    output_dir: Path = Path("data/splits"),
    manifest_path: Path = Path("data/data_manifest.json"),
    alpha: float = 0.5,
    seed: int = 42,
) -> Dict:
    """Executes the complete corpus ingestion, splitting, upsampling, and manifest generation."""
    processor = CorpusProcessor()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "version": "1.0.0",
        "seed": seed,
        "temperature_alpha": alpha,
        "languages": {},
        "pooled": {},
    }

    train_lines_by_lang: Dict[str, List[str]] = {}

    for lang in DEFAULT_LANGUAGES:
        sample_file = raw_dir / f"{lang}.txt"
        if not sample_file.exists():
            continue

        with open(sample_file, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        cleaned_lines = processor.process_lines(raw_lines)
        train, dev, test = split_dataset(cleaned_lines, seed=seed)

        train_lines_by_lang[lang] = train

        lang_dir = output_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        train_path = lang_dir / "train.txt"
        dev_path = lang_dir / "dev.txt"
        test_path = lang_dir / "test.txt"

        train_path.write_text("\n".join(train) + "\n", encoding="utf-8")
        dev_path.write_text("\n".join(dev) + "\n", encoding="utf-8")
        test_path.write_text("\n".join(test) + "\n", encoding="utf-8")

        manifest["languages"][lang] = {
            "tier": "primary" if lang in PRIMARY_LANGUAGES else "secondary",
            "total_cleaned_sentences": len(cleaned_lines),
            "train_sentences": len(train),
            "dev_sentences": len(dev),
            "test_sentences": len(test),
            "hashes": {
                "train_sha256": sha256_of_file(train_path),
                "dev_sha256": sha256_of_file(dev_path),
                "test_sha256": sha256_of_file(test_path),
            },
        }

    # Generate pooled training dataset
    pooled_train = temperature_upsample(train_lines_by_lang, alpha=alpha, seed=seed)
    pooled_path = output_dir / "pooled_train.txt"
    pooled_path.write_text("\n".join(pooled_train) + "\n", encoding="utf-8")

    manifest["pooled"] = {
        "sentences": len(pooled_train),
        "sha256": sha256_of_file(pooled_path),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    m = run_pipeline()
    print("Corpus pipeline finished successfully. Manifest:")
    print(json.dumps(m, indent=2))
