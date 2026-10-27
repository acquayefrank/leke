from pathlib import Path
from leke import LekeTokenizer, train_unigram


def test_train_unigram(tmp_path):
    corpus_file = tmp_path / "corpus.txt"
    corpus_file.write_text(
        "Akwaaba ba Ghana man mu.\n"
        "Wɔfrɛ me Kofi na mefiri Kumasi.\n"
        "Ŋkɔnye enye Yao le Kpalime.\n"
        "Mìedó gbe na mi nyuie.\n"
        "Atsɛɔ mi Nii Kwei yɛ Nkran.\n"
        "Mfantsefo wɔ amambra fɛfɛw pii.\n",
        encoding="utf-8",
    )

    out_dir = tmp_path / "models" / "unigram-test"
    receipt = train_unigram(
        corpus_paths=corpus_file,
        output_dir=out_dir,
        vocab_size=300,
        seed=42,
    )

    assert (out_dir / "tokenizer.json").exists()
    assert (out_dir / "training_receipt.json").exists()
    assert receipt["algorithm"] == "Unigram"
    assert receipt["actual_vocab_size"] > 0

    tok = LekeTokenizer.from_file(out_dir / "tokenizer.json")
    enc = tok.encode("Akwaaba ba Ghana")
    assert len(enc.ids) > 0

    decoded = tok.decode(enc.ids)
    assert "Akwaaba" in decoded
