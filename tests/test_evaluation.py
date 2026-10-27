from pathlib import Path
from leke import LekeTokenizer, calculate_metrics, evaluate_all


class DummyTokenizer:
    def __init__(self):
        pass

    def encode(self, text):
        class DummyEnc:
            def __init__(self, ids):
                self.ids = ids
        # Returns 2 tokens per word
        words = text.split()
        return DummyEnc([1, 2] * len(words))

    def token_to_id(self, token):
        return 0


def test_calculate_metrics_formulas():
    tok = DummyTokenizer()
    lines = ["Akwaaba ba Ghana", "Medaase pii"]
    # 5 words total, 10 tokens total -> fertility = 2.0
    metrics = calculate_metrics(tok, lines)
    assert metrics["fertility"] == 2.0
    assert metrics["unk_rate"] == 0.0
    assert metrics["split_rate_gt2"] == 0.0  # exactly 2 tokens per word, not >2
    assert metrics["compression_ratio"] > 0.0


def test_evaluate_all_generates_report(tmp_path):
    model_path = Path("models/bpe-8k/tokenizer.json")
    if not model_path.exists():
        return

    report_path = tmp_path / "eval_results.md"
    report = evaluate_all(
        model_path=model_path,
        splits_dir=Path("data/splits"),
        output_report_path=report_path,
    )

    assert report_path.exists()
    assert "# Leke Subword Tokenizer — Evaluation Leaderboard" in report
    assert "Akan / Twi" in report
    assert "Ewe" in report
    assert "0.0%" in report
