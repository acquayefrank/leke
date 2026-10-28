"""Downloads FLORES+ evaluation sentences for the Kwa languages it covers.

FLORES+ (openlanguagedata/flores_plus, CC BY-SA 4.0) provides professionally
translated sentences that none of the compared tokenizers were trained on, so it
serves as an out-of-domain, uncontaminated test set alongside `data/splits/`.
It covers Ewe and two Twi varieties (Asante, Akuapem); Ga and Fante are not included.

The dataset is gated: accept its terms at
https://huggingface.co/datasets/openlanguagedata/flores_plus and log in with
`huggingface-cli login` first. The maintainers ask that the text not be
republished in plain form, so the output directory is git-ignored.

Usage:
    uv run --with huggingface_hub python scripts/fetch_flores.py
"""

import json
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "data" / "eval" / "flores_plus"

# FLORES+ file stem -> Leke evaluation name
FLORES_FILES = {
    "twi_Latn_asan1239": "twi_asante",
    "twi_Latn_akua1239": "twi_akuapem",
    "ewe_Latn": "ewe",
}
SPLITS = ["dev", "devtest"]


def main():
    for split in SPLITS:
        out_dir = OUTPUT_DIR / split
        out_dir.mkdir(parents=True, exist_ok=True)
        for stem, name in FLORES_FILES.items():
            path = hf_hub_download(
                "openlanguagedata/flores_plus", f"{split}/{stem}.jsonl", repo_type="dataset"
            )
            with open(path, encoding="utf-8") as f:
                lines = [json.loads(row)["text"].strip() for row in f if row.strip()]
            (out_dir / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"{split}/{name}.txt: {len(lines)} sentences")


if __name__ == "__main__":
    main()
