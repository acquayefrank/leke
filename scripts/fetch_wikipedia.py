"""Downloads and cleans Wikipedia text as extra training data for Twi, Ewe and Fante.

Uses the `wikimedia/wikipedia` 20231101 snapshot (CC BY-SA 4.0, plain text) for
Twi (`tw`), Ewe (`ee`) and Fante (`fat`):

    1. Splits articles into lines and normalizes them with `CorpusProcessor`
       (KwaNormalizer, 3-250 words, deduplication).
    2. Keeps only lines containing characters specific to the language's orthography,
       which drops lists, tables and English-only lines.
    3. Drops every article that contains a sentence from the held-out dev/test splits
       or FLORES+ (if downloaded). The Twi test split was itself drawn from Twi
       Wikipedia intros, so whole articles are removed to avoid near-duplicate leakage.

Output goes to the git-ignored `data/raw/wikipedia/<lang>.txt`; the text is only used
for training and is not redistributed.

Usage:
    uv run --with huggingface_hub,pyarrow python scripts/fetch_wikipedia.py
"""

import re
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from leke.corpus import CorpusProcessor

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "data" / "raw" / "wikipedia"
SPLITS_DIR = ROOT / "data" / "splits"
FLORES_DIR = ROOT / "data" / "eval" / "flores_plus"

SNAPSHOT = "20231101"

# Leke language -> (Wikipedia code, characters that must appear in a kept line)
SOURCES = {
    "twi": ("tw", "ɛɔƐƆ"),
    "ewe": ("ee", "ɖƒɣʋŋƉƑƔƲŊ"),
    "fat": ("fat", "ɛɔƐƆ"),
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def held_out_sentences(processor):
    """Normalized sentences from every dev/test split and FLORES+ file."""
    paths = list(SPLITS_DIR.glob("*/dev.txt")) + list(SPLITS_DIR.glob("*/test.txt"))
    paths += list(FLORES_DIR.glob("*/*.txt"))
    sentences = set()
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            for sent in SENTENCE_SPLIT.split(processor.normalizer.normalize(line)):
                if len(sent.split()) >= 3:
                    sentences.add(sent)
    return sentences


def main():
    processor = CorpusProcessor()
    held_out = held_out_sentences(processor)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for lang, (code, required_chars) in SOURCES.items():
        path = hf_hub_download(
            "wikimedia/wikipedia",
            f"{SNAPSHOT}.{code}/train-00000-of-00001.parquet",
            repo_type="dataset",
        )
        articles = pq.read_table(path, columns=["text"]).column("text").to_pylist()

        kept_lines = []
        dropped_articles = 0
        for text in articles:
            lines = [
                line
                for line in processor.process_lines(text.splitlines())
                if any(c in line for c in required_chars)
            ]
            if any(sent in held_out for line in lines for sent in SENTENCE_SPLIT.split(line)):
                dropped_articles += 1
                continue
            kept_lines.extend(lines)

        # Deduplicate across articles while preserving order.
        clean = list(dict.fromkeys(kept_lines))
        (OUTPUT_DIR / f"{lang}.txt").write_text("\n".join(clean) + "\n", encoding="utf-8")
        print(
            f"{lang} ({code}): {len(articles):,} articles, {dropped_articles:,} dropped for "
            f"overlapping dev/test/FLORES+ -> {len(clean):,} lines "
            f"({sum(len(line) for line in clean) / 1e6:.1f}M chars)"
        )


if __name__ == "__main__":
    main()
