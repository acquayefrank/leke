import json
from pathlib import Path

from leke import LekeTokenizer, calculate_metrics, normalize
from leke.evaluate import LEKE_MODELS, load_measured_baselines
from tokenizers.pre_tokenizers import ByteLevel

ROOT = Path(__file__).resolve().parent.parent

# 1. Load char mappings
with open(ROOT / "data" / "char_mappings.json", "r", encoding="utf-8") as f:
    char_mappings_raw = json.load(f)

# 2. Load the default (16k) tokenizer.json for the live demo
with open(ROOT / "models" / "bpe-16k" / "tokenizer.json", "r", encoding="utf-8") as f:
    tok_json = json.load(f)

vocab = tok_json["model"]["vocab"]
merges = tok_json["model"]["merges"]
byte_alphabet = sorted(ByteLevel.alphabet())

# 3. Test sentences with real tokenization
tok = LekeTokenizer.from_file(str(ROOT / "models" / "bpe-16k" / "tokenizer.json"))

test_sentences = [
    {"lang": "twi", "name": "Akan / Twi", "text": "Akwaaba ba Ghana man mu."},
    {"lang": "ewe", "name": "Ewe", "text": "Ŋkɔnye enye Yao le Kpalime."},
    {"lang": "gaa", "name": "Ga", "text": "Te oyoo tɛŋŋ? Mi yɛ jogbaŋŋ."},
    {"lang": "fat", "name": "Fante", "text": "Wɔfrɛ me Kofi na mefiri Oguaa."},
    {
        "lang": "norm",
        "name": "Normalization Test (Lookalikes & Accents)",
        "text": "Wɔfrε no pápá! Mìedó gbe nε.",
    },
    {
        "lang": "oov",
        "name": "Byte Fallback (0.0% <unk> on Emojis/Unseen)",
        "text": "Hello 🌍 World! 123 #AI",
    },
]

samples = []
for s in test_sentences:
    cleaned = normalize(s["text"])
    enc = tok.encode(cleaned)
    samples.append(
        {
            "lang": s["lang"],
            "name": s["name"],
            "raw": s["text"],
            "normalized": cleaned,
            "tokens": enc.tokens,
            "ids": enc.ids,
            "offsets": enc.offsets,
        }
    )

# 4. Evaluation Leaderboard Data: Leke is scored live on the held-out test splits and
# baselines come from scripts/measure_baselines.py, measured on the same splits.
LANGUAGE_INFO = [
    (
        "twi",
        "Akan / Twi",
        "Primary release gate language (~10M speakers in Ghana and Côte d'Ivoire). High morphological affixation.",
    ),
    (
        "ewe",
        "Ewe",
        "Gbe group of Kwa (~7M speakers in Ghana, Togo, Benin). Tonal with phonemic diacritics.",
    ),
    (
        "gaa",
        "Ga",
        "Ga-Dangme branch (~2.5M speakers in Greater Accra region). Syllable-timed tone language.",
    ),
    (
        "fat",
        "Fante",
        "Central Akan dialect spoken in coastal Ghana. Closely related to Twi with distinct vowel harmony.",
    ),
]

baselines = load_measured_baselines(ROOT / "data" / "baselines" / "measured_baselines.json")


def leaderboard_row(name, vocab, metrics, is_leke, status):
    return {
        "name": name,
        "vocab": vocab,
        "fertility": metrics["fertility"],
        "splitRate": metrics["split_rate_gt2"],
        "unkRate": metrics["unk_rate"],
        "compression": metrics["compression_ratio"],
        "isLeke": is_leke,
        "status": status,
    }


leaderboard = []
for lang_code, lang_name, description in LANGUAGE_INFO:
    test_path = ROOT / "data" / "splits" / lang_code / "test.txt"
    test_lines = test_path.read_text(encoding="utf-8").splitlines()
    models = []
    for leke_name, leke_vocab, bundle in LEKE_MODELS:
        leke_tok = LekeTokenizer.from_file(str(ROOT / bundle / "tokenizer.json"))
        models.append(
            leaderboard_row(
                leke_name, leke_vocab, calculate_metrics(leke_tok, test_lines), True, "Leke"
            )
        )
    # Baseline deltas are relative to the default (16k) model.
    leke_metrics = calculate_metrics(tok, test_lines)
    lang_baselines = sorted(
        (b for b in baselines if b["lang"] == lang_code), key=lambda b: b["fertility"]
    )
    for b in lang_baselines:
        delta = (leke_metrics["fertility"] / b["fertility"] - 1.0) * 100.0
        status = f"Leke {delta:+.1f}% fertility"
        models.append(leaderboard_row(b["model"], b["vocab"], b, False, status))

    leaderboard.append(
        {"lang": lang_name, "code": lang_code, "description": description, "models": models}
    )

# 5. Throughput Benchmarks (single thread, from specs/benchmarks.md)
benchmarks = {
    "encode_speed": "~450,000 tokens/sec",
    "decode_speed": "~100,000 sentences/sec",
    "vocab_size": "16,384",
    "unk_rate": "0.00%",
    "languages": ["Akan / Twi", "Ewe", "Ga", "Fante"],
}

data_export = {
    "charMappings": char_mappings_raw["mappings"],
    "byteAlphabet": byte_alphabet,
    "samples": samples,
    "leaderboard": leaderboard,
    "benchmarks": benchmarks,
    "vocab": vocab,
    "merges": merges,
}

docs_dir = ROOT / "docs"
docs_dir.mkdir(exist_ok=True)

with open(docs_dir / "leke-data.js", "w", encoding="utf-8") as f:
    f.write("window.LEKE_DATA = " + json.dumps(data_export, ensure_ascii=False, indent=2) + ";\n")

print("Successfully exported docs/leke-data.js with byte alphabet")
