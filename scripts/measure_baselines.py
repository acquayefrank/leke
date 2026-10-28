"""Measures baseline tokenizers on Leke's own held-out test splits.

Every tokenizer (Leke and baselines) is scored with the same `calculate_metrics`
function on the same text, with special tokens disabled, so the resulting numbers
are directly comparable. Two evaluation sets are used:

    - `test_split`: the held-out `data/splits/<lang>/test.txt` files (in-domain).
    - `flores_devtest`: FLORES+ devtest for Ewe and Twi (Asante, Akuapem), fetched
      by `scripts/fetch_flores.py`; skipped if not downloaded.

Baselines:
    - NLLB-200 (facebook/nllb-200-distilled-600M, 256k SentencePiece)
    - Goldfish monolingual models (goldfish-models/*_latn_full, SentencePiece)
    - Wikilangs monolingual SentencePiece tokenizers (wikilangs/<code>, 8k and 32k)

Usage:
    uv run --with sentencepiece,huggingface_hub python scripts/measure_baselines.py
"""

import json
from pathlib import Path

import sentencepiece as spm
from huggingface_hub import hf_hub_download
from leke import LekeTokenizer, calculate_metrics
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent.parent
SPLITS_DIR = ROOT / "data" / "splits"
OUTPUT_FILE = ROOT / "data" / "baselines" / "measured_baselines.json"
FLORES_DIR = ROOT / "data" / "eval" / "flores_plus" / "devtest"

LANGUAGES = ["twi", "ewe", "gaa", "fat"]

# FLORES+ evaluation name -> Leke language whose baselines apply to it
FLORES_LANGS = {"twi_asante": "twi", "twi_akuapem": "twi", "ewe": "ewe"}


class HFTokenizer:
    """Adapts a `tokenizers.Tokenizer` to the `calculate_metrics` interface."""

    def __init__(self, path: str, unk_token: str):
        self._tok = Tokenizer.from_file(path)
        self._unk_token = unk_token

    def encode(self, text: str):
        return self._tok.encode(text, add_special_tokens=False).ids

    def token_to_id(self, token: str):
        return self._tok.token_to_id(self._unk_token) if token == "<unk>" else None


class SPTokenizer:
    """Adapts a raw SentencePiece model to the `calculate_metrics` interface."""

    def __init__(self, path: str):
        self._sp = spm.SentencePieceProcessor(model_file=path)

    def encode(self, text: str):
        return self._sp.encode(text)

    def token_to_id(self, token: str):
        return self._sp.unk_id() if token == "<unk>" else None


def nllb():
    path = hf_hub_download("facebook/nllb-200-distilled-600M", "tokenizer.json")
    return HFTokenizer(path, "<unk>")


def goldfish(model: str):
    path = hf_hub_download(f"goldfish-models/{model}", "tokenizer.json")
    return HFTokenizer(path, "<unk>")


def wikilangs(code: str, size: str):
    path = hf_hub_download(f"wikilangs/{code}", f"models/tokenizer/{code}_tokenizer_{size}.model")
    return SPTokenizer(path)


# (display name, vocab size, factory, languages evaluated)
BASELINES = [
    ("NLLB-200 (multilingual)", "256k", nllb, LANGUAGES),
    ("Goldfish Twi (twi_latn_full)", "50k", lambda: goldfish("twi_latn_full"), ["twi"]),
    ("Goldfish Akan (aka_latn_full)", "50k", lambda: goldfish("aka_latn_full"), ["twi", "fat"]),
    ("Goldfish Ewe (ewe_latn_full)", "50k", lambda: goldfish("ewe_latn_full"), ["ewe"]),
    ("Wikilangs Twi (tw, 8k)", "8k", lambda: wikilangs("tw", "8k"), ["twi", "fat"]),
    ("Wikilangs Twi (tw, 16k)", "16k", lambda: wikilangs("tw", "16k"), ["twi", "fat"]),
    ("Wikilangs Twi (tw, 32k)", "32k", lambda: wikilangs("tw", "32k"), ["twi", "fat"]),
    ("Wikilangs Ewe (ee, 8k)", "8k", lambda: wikilangs("ee", "8k"), ["ewe"]),
    ("Wikilangs Ewe (ee, 16k)", "16k", lambda: wikilangs("ee", "16k"), ["ewe"]),
    ("Wikilangs Ewe (ee, 32k)", "32k", lambda: wikilangs("ee", "32k"), ["ewe"]),
    ("Wikilangs Fante (fat, 8k)", "8k", lambda: wikilangs("fat", "8k"), ["fat"]),
    ("Wikilangs Fante (fat, 16k)", "16k", lambda: wikilangs("fat", "16k"), ["fat"]),
    ("Wikilangs Fante (fat, 32k)", "32k", lambda: wikilangs("fat", "32k"), ["fat"]),
]


def load_eval_sets():
    """Returns (eval_set, eval_lang, baseline_lang, lines) for every available test set."""
    sets = [
        (
            "test_split",
            lang,
            lang,
            (SPLITS_DIR / lang / "test.txt").read_text(encoding="utf-8").splitlines(),
        )
        for lang in LANGUAGES
    ]
    for name, base_lang in FLORES_LANGS.items():
        path = FLORES_DIR / f"{name}.txt"
        if path.exists():
            sets.append(
                ("flores_devtest", name, base_lang, path.read_text(encoding="utf-8").splitlines())
            )
        else:
            print(f"[skip] {path} not found; run scripts/fetch_flores.py")
    return sets


def main():
    eval_sets = load_eval_sets()

    results = []
    leke = LekeTokenizer.from_file(ROOT / "models" / "bpe-8k" / "tokenizer.json")
    for eval_set, eval_lang, _, lines in eval_sets:
        metrics = calculate_metrics(leke, lines)
        results.append(
            {"model": "Leke BPE (8k)", "vocab": "8k", "eval_set": eval_set, "lang": eval_lang}
            | metrics
        )

    for name, vocab, factory, langs in BASELINES:
        tok = factory()
        for eval_set, eval_lang, base_lang, lines in eval_sets:
            if base_lang in langs:
                metrics = calculate_metrics(tok, lines)
                results.append(
                    {"model": name, "vocab": vocab, "eval_set": eval_set, "lang": eval_lang}
                    | metrics
                )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")

    for eval_set, eval_lang, _, _ in eval_sets:
        print(f"\n== {eval_set} / {eval_lang}")
        rows = [r for r in results if r["eval_set"] == eval_set and r["lang"] == eval_lang]
        for r in sorted(rows, key=lambda r: r["fertility"]):
            print(
                f"  {r['model']:<32} {r['vocab']:>5}  fert={r['fertility']:<5} "
                f"split>2={r['split_rate_gt2']:<5}% unk={r['unk_rate']:<5}% "
                f"bytes/tok={r['compression_ratio']}"
            )


if __name__ == "__main__":
    main()
