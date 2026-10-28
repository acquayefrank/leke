from leke import KwaNormalizer, normalize


def test_standalone_normalize():
    # Greek epsilon -> Latin Open E (ɛ)
    assert normalize("ε") == "ɛ"
    # Greek gamma -> Latin Gamma (ɣ)
    assert normalize("γ") == "ɣ"
    # Cyrillic ie -> Latin Open E (ɛ)
    assert normalize("є") == "ɛ"
    # Textbook lookalikes: Greek reversed lunate sigma, mathematical superset, Greek phi
    assert normalize("yɛbͻhwɛ") == "yɛbɔhwɛ"
    assert normalize("Ͻsᴐ") == "Ɔsɔ"
    assert normalize("⊃no") == "ɔno"
    assert normalize("Kofi φo nɔvia") == "Kofi ƒo nɔvia"


def test_normalizer_tone_preservation_by_default():
    norm = KwaNormalizer()
    twi = "Wɔfrɛ no pápá."
    assert norm.normalize(twi) == "Wɔfrɛ no pápá."
    assert normalize(twi) == "Wɔfrɛ no pápá."

    ewe = "Mìedó gbe na wo."
    assert norm.normalize(ewe) == "Mìedó gbe na wo."


def test_normalizer_tone_stripping():
    norm = KwaNormalizer(strip_accents=True)
    twi = "Wɔfrɛ no pápá."
    assert norm.normalize(twi) == "Wɔfrɛ no papa."

    ewe = "Mìedó gbe na wo."
    assert norm.normalize(ewe) == "Miedo gbe na wo."


def test_whitespace_collapsing():
    norm = KwaNormalizer()
    raw = "   Wo   ho   te   sɛn?   "
    assert norm.normalize(raw) == "Wo ho te sɛn?"


def test_batch_normalization():
    norm = KwaNormalizer()
    items = ["  ε  ", "  γ  ", "  pápá  "]
    assert norm.normalize_batch(items) == ["ɛ", "ɣ", "pápá"]


def test_idempotence():
    norm = KwaNormalizer()
    text = "Wɔfrɛ no pápá! Mìedó gbe."
    once = norm.normalize(text)
    twice = norm.normalize(once)
    assert once == twice
