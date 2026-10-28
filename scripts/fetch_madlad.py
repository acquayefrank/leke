"""Downloads and cleans MADLAD-400 text as extra training data for Twi and Ewe.

MADLAD-400 (allenai/MADLAD-400, ODC-By 1.0) provides document-level web text. This
script uses the `clean` subsets for Akan (`ak`, used for Twi) and Ewe (`ee`):

    1. Splits documents into lines and normalizes them with `CorpusProcessor`
       (KwaNormalizer, 3-250 words, deduplication).
    2. Keeps only lines containing characters specific to the language's orthography,
       which drops navigation menus, language lists and English boilerplate.
    3. Removes any line that contains a sentence from the held-out dev/test splits or
       from FLORES+ (if downloaded), so evaluation sets stay uncontaminated.

Output goes to the git-ignored `data/raw/madlad/<lang>.txt`; the text is only used
for training and is not redistributed.

Usage:
    uv run --with huggingface_hub python scripts/fetch_madlad.py
"""

import gzip
import json
import re
from pathlib import Path

from huggingface_hub import hf_hub_download
from leke.corpus import CorpusProcessor

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "data" / "raw" / "madlad"
SPLITS_DIR = ROOT / "data" / "splits"
FLORES_DIR = ROOT / "data" / "eval" / "flores_plus"

# Leke language -> (MADLAD-400 code, characters that must appear in a kept line)
SOURCES = {
    "twi": ("ak", "ɛɔƐƆ"),
    "ewe": ("ee", "ɖƒɣʋŋƉƑƔƲŊ"),
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
            "allenai/MADLAD-400", f"data/{code}/{code}_clean_0000.jsonl.gz", repo_type="dataset"
        )
        raw_lines = []
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for row in f:
                # MADLAD stores line breaks inside documents as a literal backslash-n.
                raw_lines.extend(json.loads(row)["text"].split("\\n"))

        lines = processor.process_lines(raw_lines)
        kept = [line for line in lines if any(c in line for c in required_chars)]
        clean = [
            line
            for line in kept
            if not any(sent in held_out for sent in SENTENCE_SPLIT.split(line))
        ]

        (OUTPUT_DIR / f"{lang}.txt").write_text("\n".join(clean) + "\n", encoding="utf-8")
        print(
            f"{lang} ({code}): {len(raw_lines):,} raw lines -> {len(lines):,} normalized -> "
            f"{len(kept):,} with {lang} orthography -> {len(clean):,} after removing "
            f"{len(kept) - len(clean):,} lines overlapping dev/test/FLORES+ "
            f"({sum(len(line) for line in clean) / 1e6:.1f}M chars)"
        )


if __name__ == "__main__":
    main()
