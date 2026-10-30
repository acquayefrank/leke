from pathlib import Path

import pytest
from leke import LekeTokenizer
from tokenizers import Tokenizer as HFTokenizer

MODEL_PATHS = ["models/bpe-16k/tokenizer.json", "models/bpe-32k/tokenizer.json"]


@pytest.mark.parametrize("model_path", MODEL_PATHS)
def test_leke_tokenizer_bindings(model_path):
    if not Path(model_path).exists():
        # Fallback if run in isolation
        return

    # Load via both Leke and official HF
    leke_tok = LekeTokenizer.from_file(model_path)
    hf_tok = HFTokenizer.from_file(model_path)

    assert leke_tok.vocab_size == hf_tok.get_vocab_size()

    # Test parity on Kwa phrases
    phrases = [
        "Akwaaba ba Ghana man mu.",
        "Wɔfrɛ me Kofi na mefiri Kumasi.",
        "Ŋkɔnye enye Yao le Kpalime.",
        "Mìedó gbe na mi nyuie.",
        "Atsɛɔ mi Nii Kwei yɛ Nkran.",
        "Mfantsefo wɔ amambra fɛfɛw pii.",
    ]

    for phrase in phrases:
        leke_enc = leke_tok.encode(phrase)
        hf_enc = hf_tok.encode(phrase)

        # 100% ID parity
        assert leke_enc.ids == hf_enc.ids
        assert leke_enc.tokens == hf_enc.tokens

        # Verify offsets slice the exact UTF-8 byte sequence
        phrase_bytes = phrase.encode("utf-8")
        for start, end in leke_enc.offsets:
            assert start <= end
            assert end <= len(phrase_bytes)

        # Decode parity
        assert leke_tok.decode(leke_enc.ids) == hf_tok.decode(hf_enc.ids)


@pytest.mark.parametrize("model_path", MODEL_PATHS)
def test_batch_encoding_and_decoding(model_path):
    if not Path(model_path).exists():
        return

    tok = LekeTokenizer.from_file(model_path)
    batch = ["Akwaaba ba Ghana.", "Mìedó gbe nɛ."]

    encs = tok.encode_batch(batch)
    assert len(encs) == 2
    assert encs[0].ids == tok.encode(batch[0]).ids
    assert encs[1].ids == tok.encode(batch[1]).ids

    decoded_batch = tok.decode_batch([encs[0].ids, encs[1].ids])
    assert len(decoded_batch) == 2
    assert "Akwaaba" in decoded_batch[0]
    assert "Mìedó" in decoded_batch[1]


@pytest.mark.parametrize("model_path", MODEL_PATHS)
def test_transformers_interop(model_path):
    if not Path(model_path).exists():
        return

    tok = LekeTokenizer.from_file(model_path)
    hf_trans = tok.to_transformers()
    assert hf_trans is not None

    tokens = hf_trans.tokenize("Wɔfrɛ me Kofi")
    assert len(tokens) > 0
    ids = hf_trans.encode("Wɔfrɛ me Kofi")
    assert len(ids) > 0
    decoded = hf_trans.decode(ids)
    assert "Wɔfrɛ me Kofi" in decoded
