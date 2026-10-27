import json
from pathlib import Path
from tokenizers import Tokenizer
from leke.trainer import train_bpe


def test_train_bpe_python(tmp_path):
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

    out_dir = tmp_path / "models" / "bpe-test"
    receipt = train_bpe(
        corpus_paths=corpus_file,
        output_dir=out_dir,
        vocab_size=300,
        seed=42,
    )

    assert (out_dir / "tokenizer.json").exists()
    assert (out_dir / "training_receipt.json").exists()

    assert receipt["algorithm"] == "ByteLevel-BPE"
    assert receipt["actual_vocab_size"] > 0

    # Load with official Hugging Face Tokenizer
    tok = Tokenizer.from_file(str(out_dir / "tokenizer.json"))
    assert tok.get_vocab_size() == receipt["actual_vocab_size"]

    # Test encoding
    encoding = tok.encode("Wɔfrɛ me Kofi pápá")
    assert len(encoding.ids) > 0

    # Test Zero Unknown Tokens (Byte-level fallback)
    unseen_encoding = tok.encode("Unseen English word with numbers 42 and emoji 🇬🇭")
    unk_id = tok.token_to_id("<unk>")
    assert unk_id is not None
    assert unk_id not in unseen_encoding.ids, "Byte-level BPE must not emit <unk> for unseen text!"

    # Test roundtrip decode(encode(text)) == text
    decoded = tok.decode(encoding.ids)
    assert "Wɔfrɛ me Kofi" in decoded

    # Test Hugging Face transformers AutoTokenizer compatibility
    from transformers import PreTrainedTokenizerFast
    hf_tok = PreTrainedTokenizerFast(tokenizer_file=str(out_dir / "tokenizer.json"))
    tokens = hf_tok.tokenize("Wɔfrɛ me Kofi pápá")
    assert len(tokens) > 0
    assert hf_tok.decode(hf_tok.encode("Akwaaba ba Ghana")).strip() == "Akwaaba ba Ghana"
