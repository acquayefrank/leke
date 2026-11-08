"""Downloads out-of-domain evaluation text for Ga and Fante, which FLORES+ lacks.

    - Ga: Google SMOL (`google/smol`, CC BY 4.0), the Ga side of the professionally
      translated SmolSent sentences and SmolDoc documents (`en_gaa`).
    - Fante: Google WAXAL (`google/WaxalNLP`, `fat_tts`, CC BY 4.0, provided by the
      University of Ghana), the transcripts of the phonetically balanced scripts read
      for text-to-speech, all splits. The scripts mark numbers with bracketed digits
      next to the spelled-out word ("ehinanan [2] ebien"); those markers are removed.

Neither dataset existed when Glot500 and MADLAD-400 were collected, and the script
checks that no evaluation sentence appears verbatim in the training corpus. Output goes
to the git-ignored `data/eval/smol/gaa.txt` and `data/eval/waxal/fat.txt`.

Usage:
    uv run --with huggingface_hub,pyarrow python scripts/fetch_ga_fante_eval.py
"""

import json
import re
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem, hf_hub_download

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = ROOT / "data" / "eval"
TRAIN_CORPUS = ROOT / "data" / "raw" / "pooled_train_extended.txt"

BRACKET_MARKER = re.compile(r"\s*\[[^\]]*\]")


def smol_ga():
    """Returns the Ga side of SmolSent and SmolDoc, one sentence per line."""
    lines = []
    path = hf_hub_download("google/smol", "smolsent/en_gaa.jsonl", repo_type="dataset")
    with open(path, encoding="utf-8") as f:
        lines += [json.loads(row)["trg"] for row in f if row.strip()]
    path = hf_hub_download("google/smol", "smoldoc/en_gaa.jsonl", repo_type="dataset")
    with open(path, encoding="utf-8") as f:
        lines += [sent for row in f if row.strip() for sent in json.loads(row)["trgs"]]
    return lines


def waxal_fante():
    """Returns the Fante TTS script transcripts, reading only the text column."""
    fs = HfFileSystem()
    files = sorted(fs.glob("datasets/google/WaxalNLP/data/TTS/fat/*.parquet"))
    if not files:
        raise SystemExit("No WAXAL Fante parquet files found")
    lines = []
    for path in files:
        table = pq.read_table(path, columns=["text"], filesystem=fs)
        lines += [BRACKET_MARKER.sub("", t) for t in table.column("text").to_pylist()]
    return lines


def main():
    train = set()
    if TRAIN_CORPUS.exists():
        with open(TRAIN_CORPUS, encoding="utf-8") as f:
            train = {line.strip() for line in f if line.strip()}
    else:
        print(f"[warn] {TRAIN_CORPUS} not found; skipping the training-overlap check")

    for name, fetch, out_path in [
        ("SMOL Ga", smol_ga, EVAL_DIR / "smol" / "gaa.txt"),
        ("WAXAL Fante", waxal_fante, EVAL_DIR / "waxal" / "fat.txt"),
    ]:
        lines = [" ".join(line.split()) for line in fetch()]
        lines = [line for line in lines if line]
        overlap = sum(line in train for line in lines)
        if overlap:
            raise SystemExit(f"{name}: {overlap} sentences also appear in the training corpus")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{out_path.relative_to(ROOT)}: {len(lines)} sentences, 0 in training corpus")


if __name__ == "__main__":
    main()
