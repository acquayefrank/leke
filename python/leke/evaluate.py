"""Evaluation harness for fertility, split rate, unknown-token rate, and compression ratio.

Evaluating a subword tokenizer requires structural linguistic metrics rather than
downstream model scores (like BLEU or accuracy). This module computes four primary
benchmarks across held-out evaluation corpora:

1. **Fertility (Tokens per Word)**:
   - Formula: Total Tokens / Total Words
   - Interpretation: In subword tokenization, **lower fertility is superior**.
     When a tokenizer has low fertility (e.g. 1.8 vs 3.2), each word is represented
     by fewer subword units. This directly conserves the model's sequence length context
     window and accelerates generation speed during autoregressive decoding.

2. **Word Fragmentation Rate (Split > 2)**:
   - Formula: (Count of words with > 2 subwords) / (Total Words) * 100%
   - Interpretation: High fragmentation indicates severe over-segmentation where
     morphemes are shattered into individual characters or byte tokens. A lower split
     rate indicates that the tokenizer aligns well with natural syllabic affixes (CV/CVC).

3. **Unknown Token Rate (<unk> Rate)**:
   - Formula: (Count of <unk> tokens) / (Total Tokens) * 100%
   - Hard Release Gate: Must be **0.00%** on arbitrary text via byte-level fallback.

4. **Compression Ratio (Bytes per Token)**:
   - Formula: Total UTF-8 Bytes / Total Tokens
   - Interpretation: Measures information density. Higher bytes/token indicates
     that tokens represent larger linguistic chunks on average.

Baselines:
    Baseline tokenizers (NLLB-200, Goldfish, Wikilangs) are measured on the same
    held-out test splits by `scripts/measure_baselines.py`, which writes
    `data/baselines/measured_baselines.json`. This module reads that file so every
    row in the leaderboard is scored on identical text with identical metrics.

Examples:
    >>> from leke.evaluate import calculate_metrics
    >>> from leke.tokenizer import LekeTokenizer
    >>> tok = LekeTokenizer.from_file("models/bpe-16k/tokenizer.json")
    >>> metrics = calculate_metrics(tok, ["Akwaaba ba Ghana man mu."])
    >>> print("Fertility:", metrics["fertility"])
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from tabulate import tabulate

from leke.tokenizer import LekeTokenizer

# Target Kwa language codes evaluated by the benchmark harness.
LANGUAGES: List[str] = ["twi", "ewe", "gaa", "fat"]

# Human-readable linguistic display names for leaderboard tables.
LANGUAGE_NAMES: Dict[str, str] = {
    "twi": "Akan / Twi",
    "ewe": "Ewe",
    "gaa": "Ga",
    "fat": "Fante",
}

# Display name and vocabulary size of the default Leke model in leaderboards.
LEKE_MODEL_NAME = "Leke BPE (16k)"
LEKE_VOCAB = "16k"

# Baseline metrics measured on the held-out test splits by scripts/measure_baselines.py.
DEFAULT_BASELINES_PATH = Path("data/baselines/measured_baselines.json")

# FLORES+ devtest files fetched by scripts/fetch_flores.py (git-ignored).
DEFAULT_FLORES_DIR = Path("data/eval/flores_plus/devtest")
FLORES_NAMES: Dict[str, str] = {
    "twi_asante": "Twi (Asante)",
    "twi_akuapem": "Twi (Akuapem)",
    "ewe": "Ewe",
}


def load_measured_baselines(
    path: Path = DEFAULT_BASELINES_PATH, eval_set: str = "test_split"
) -> List[Dict[str, Any]]:
    """Loads baseline rows measured by `scripts/measure_baselines.py`.

    Args:
        path (Path, optional): Path to `measured_baselines.json`.
        eval_set (str, optional): Evaluation set to return (`test_split` or
            `flores_devtest`).

    Returns:
        List[Dict[str, Any]]: Baseline rows (Leke rows excluded), each with `model`,
            `vocab`, `lang`, `fertility`, `split_rate_gt2`, `unk_rate`, and
            `compression_ratio`. Empty if the file does not exist.
    """
    if not path.exists():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [
        r
        for r in rows
        if not r["model"].startswith("Leke") and r.get("eval_set", "test_split") == eval_set
    ]


def calculate_metrics(tokenizer: Any, lines: List[str]) -> Dict[str, float]:
    """Calculates evaluation metrics over a collection of text lines.

    Args:
        tokenizer (Any): Either a LekeTokenizer, native Tokenizer, or Hugging Face
            PreTrainedTokenizerFast instance.
        lines (List[str]): Collection of text sentences from evaluation sets.

    Returns:
        Dict[str, float]: Dictionary containing:
            - `fertility` (float): Average tokens per word.
            - `split_rate_gt2` (float): Percentage of words broken into >2 subwords.
            - `unk_rate` (float): Percentage of emitted tokens that are <unk>.
            - `compression_ratio` (float): Average UTF-8 bytes per token.

    Notes:
        1. Strips lines and filters empty records.
        2. Detects the numerical ID for `<unk>` if present in the tokenizer vocabulary.
        3. Iterates over sentences:
           - Encodes the full line to measure total token count and byte length.
           - Iterates over each individual whitespace-separated word to measure
             isolated word fragmentation (detecting words broken into >2 subwords).
        4. Calculates fertility, split rate (>2 pieces), unknown token percentage,
           and compression ratio.

    Examples:
        >>> m = calculate_metrics(tok, ["Akwaaba ba Ghana"])
        >>> print(m["unk_rate"])
        0.0
    """
    # Step 1: Clean input lines, omitting empty strings.
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    if not cleaned_lines:
        return {
            "fertility": 0.0,
            "split_rate_gt2": 0.0,
            "unk_rate": 0.0,
            "compression_ratio": 0.0,
        }

    # Step 2: Initialize accumulators for metric calculation.
    total_words = 0
    total_tokens = 0
    total_bytes = 0
    words_gt2 = 0
    unk_tokens = 0

    # Step 3: Discover the unknown token ID (<unk>) dynamically across tokenizer types.
    unk_id = getattr(tokenizer, "token_to_id", lambda t: None)("<unk>")

    # Step 4: Iterate through each text line in the evaluation corpus.
    for line in cleaned_lines:
        # Split line on whitespace to obtain baseline lexical words.
        words = line.split()
        # Measure raw UTF-8 byte length of the line.
        line_bytes = len(line.encode("utf-8"))
        total_words += len(words)
        total_bytes += line_bytes

        # Step 4a: Encode the line using the active tokenizer interface.
        if hasattr(tokenizer, "encode"):
            enc = tokenizer.encode(line)
            # Support both Leke Encoding objects and raw ID lists.
            ids = getattr(enc, "ids", enc)
        else:
            # Fallback for Hugging Face PreTrainedTokenizer callable.
            ids = tokenizer(line)["input_ids"]

        total_tokens += len(ids)

        # Step 4b: Count occurrences of the unknown token symbol.
        if unk_id is not None:
            unk_tokens += sum(1 for i in ids if i == unk_id)

        # Step 4c: Calculate isolated word fragmentation. Words are encoded with a
        # leading space so byte-level BPE sees the same "Ġword" form it sees
        # mid-sentence; Metaspace/SentencePiece tokenizers are unaffected.
        for word in words:
            if hasattr(tokenizer, "encode"):
                w_enc = tokenizer.encode(" " + word)
                w_ids = getattr(w_enc, "ids", w_enc)
            else:
                w_ids = tokenizer(" " + word)["input_ids"]
            # Flag words that fragment into 3 or more subwords.
            if len(w_ids) > 2:
                words_gt2 += 1

    # Step 5: Compute final ratios with zero-division protection.
    fertility = total_tokens / total_words if total_words > 0 else 0.0
    split_rate = (words_gt2 / total_words * 100.0) if total_words > 0 else 0.0
    unk_rate = (unk_tokens / total_tokens * 100.0) if total_tokens > 0 else 0.0
    compression = (total_bytes / total_tokens) if total_tokens > 0 else 0.0

    # Step 6: Return neatly rounded metrics dictionary.
    return {
        "fertility": round(fertility, 2),
        "split_rate_gt2": round(split_rate, 1),
        "unk_rate": round(unk_rate, 2),
        "compression_ratio": round(compression, 2),
    }


def _comparison_section(
    tokenizer: Any, eval_sets: List[Any], baselines: List[Dict[str, Any]]
) -> Any:
    """Builds a Markdown comparison table and summary for one evaluation set.

    Args:
        tokenizer (Any): The Leke tokenizer under evaluation.
        eval_sets (List[Any]): `(lang_key, display_name, path)` tuples.
        baselines (List[Dict[str, Any]]): Measured baseline rows for this evaluation set.

    Returns:
        Tuple[str, str]: The Markdown table and a bullet-list summary.
    """
    table_data = []
    summary_items = []
    for lang, label, path in eval_sets:
        metrics = calculate_metrics(tokenizer, path.read_text(encoding="utf-8").splitlines())

        # Leke row first, then baselines measured on the same text, best first.
        table_data.append(
            [
                f"**{LEKE_MODEL_NAME}**",
                LEKE_VOCAB,
                label,
                f"**{metrics['fertility']}**",
                f"{metrics['split_rate_gt2']}%",
                f"**{metrics['unk_rate']}%**",
                f"{metrics['compression_ratio']}",
                "—",
            ]
        )
        lang_baselines = sorted(
            (b for b in baselines if b["lang"] == lang), key=lambda b: b["fertility"]
        )
        for b_metrics in lang_baselines:
            delta = (metrics["fertility"] / b_metrics["fertility"] - 1.0) * 100.0
            status = "✅ Leke lower" if delta < 0 else "⚠️ Baseline lower"
            table_data.append(
                [
                    b_metrics["model"],
                    b_metrics["vocab"],
                    label,
                    f"{b_metrics['fertility']}",
                    f"{b_metrics['split_rate_gt2']}%",
                    f"{b_metrics['unk_rate']}%",
                    f"{b_metrics['compression_ratio']}",
                    f"{status} ({delta:+.1f}%)",
                ]
            )

        # Summarize where Leke wins and loses on fertility.
        beaten = [b["model"] for b in lang_baselines if metrics["fertility"] < b["fertility"]]
        ahead = [b["model"] for b in lang_baselines if b["fertility"] <= metrics["fertility"]]
        line = (
            f"- **{label}**: Leke fertility {metrics['fertility']}, "
            f"`<unk>` rate {metrics['unk_rate']}%."
        )
        if beaten:
            line += f" Lower fertility than: {', '.join(beaten)}."
        if ahead:
            line += f" Higher fertility than: {', '.join(ahead)}."
        summary_items.append(line)

    headers = [
        "Model",
        "Vocab",
        "Language",
        "Fertility (tok/word)",
        "Split >2 (%)",
        "Unknown (%)",
        "Compression (bytes/tok)",
        "Leke fertility vs. baseline",
    ]
    return tabulate(table_data, headers=headers, tablefmt="github"), "\n".join(summary_items)


def evaluate_all(
    model_path: Path = Path("models/bpe-16k/tokenizer.json"),
    splits_dir: Path = Path("data/splits"),
    output_report_path: Optional[Path] = Path("specs/eval_results.md"),
    baselines_path: Path = DEFAULT_BASELINES_PATH,
    flores_dir: Path = DEFAULT_FLORES_DIR,
) -> str:
    """Runs evaluation across all target languages on held-out test splits.

    Args:
        model_path (Path, optional): Path to the tokenizer.json file.
        splits_dir (Path, optional): Directory containing language split folders.
        output_report_path (Optional[Path], optional): File to save markdown leaderboard.
        baselines_path (Path, optional): Measured baseline metrics JSON.
        flores_dir (Path, optional): Directory of FLORES+ devtest files from
            `scripts/fetch_flores.py`; the FLORES+ section is skipped if absent.

    Returns:
        str: Formatted Markdown leaderboard report.

    Notes:
        1. Loads the specified model bundle into `LekeTokenizer`.
        2. Loads each `test.txt` split and any FLORES+ devtest files in `flores_dir`.
        3. Computes metrics and compares against baselines measured on the same
           splits (NLLB-200, Goldfish, Wikilangs) from `baselines_path`.
        4. Formats a GitHub-flavored Markdown table comparing fertility, split rate,
           unknown token rate, and compression.
        5. Saves the leaderboard report to `output_report_path` and returns markdown text.
    """
    # Step 1: Load tokenizer and measured baselines from disk.
    tokenizer = LekeTokenizer.from_file(model_path)

    # Step 2: Collect in-domain test splits and, if downloaded, FLORES+ devtest files.
    split_sets = []
    for lang in LANGUAGES:
        test_file = splits_dir / lang / "test.txt"
        if test_file.exists():
            split_sets.append((lang, LANGUAGE_NAMES[lang], test_file))
    flores_sets = [
        (name, label, flores_dir / f"{name}.txt")
        for name, label in FLORES_NAMES.items()
        if (flores_dir / f"{name}.txt").exists()
    ]

    # Step 3: Build a comparison table and summary for each evaluation set.
    split_table, split_summary = _comparison_section(
        tokenizer, split_sets, load_measured_baselines(baselines_path, "test_split")
    )
    report = f"""# Leke Subword Tokenizer — Evaluation Leaderboard

This report compares Leke against baseline tokenizers (NLLB-200, Goldfish, Wikilangs) measured on the same text by `scripts/measure_baselines.py`.

## Held-Out Test Splits (in-domain)

Sentences held out from the same sources as the training data (`data/splits/<lang>/test.txt`). The Twi split is mostly Twi Wikipedia, which the Wikilangs and Goldfish tokenizers were likely trained on.

{split_table}

{split_summary}
"""
    if flores_sets:
        flores_table, flores_summary = _comparison_section(
            tokenizer, flores_sets, load_measured_baselines(baselines_path, "flores_devtest")
        )
        report += f"""
## FLORES+ devtest (out-of-domain)

Professionally translated sentences (`openlanguagedata/flores_plus`, CC BY-SA 4.0) that none of the compared tokenizers were trained on. Covers Ewe and Twi (Asante, Akuapem); Ga and Fante are not included.

{flores_table}

{flores_summary}
"""

    # Step 4: Save markdown leaderboard report to disk if path is provided.
    if output_report_path:
        output_report_path.parent.mkdir(parents=True, exist_ok=True)
        output_report_path.write_text(report, encoding="utf-8")

    # Step 5: Return the report string.
    return report


def main() -> None:
    """CLI entrypoint for running evaluation benchmarks."""
    # Step 1: Configure command-line parser.
    parser = argparse.ArgumentParser(description="Evaluate Leke tokenizer against baselines.")
    parser.add_argument(
        "--model",
        type=str,
        default="models/bpe-16k/tokenizer.json",
        help="Path to tokenizer.json",
    )
    parser.add_argument(
        "--splits-dir",
        type=str,
        default="data/splits",
        help="Directory containing language splits",
    )
    parser.add_argument(
        "--report-out",
        type=str,
        default="specs/eval_results.md",
        help="Path to write markdown leaderboard",
    )

    # Step 2: Parse arguments and run evaluation.
    args = parser.parse_args()
    report = evaluate_all(
        model_path=Path(args.model),
        splits_dir=Path(args.splits_dir),
        output_report_path=Path(args.report_out),
    )

    # Step 3: Print report to console.
    print(report)


# Execute main if called directly.
if __name__ == "__main__":
    main()
