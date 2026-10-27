# Kwa Tokenizer: Build Handoff

## Goal
Build an open-source subword tokenizer for Kwa languages (Akan/Twi, Ewe, Ga, Fante) with a Rust core and Python bindings. The tokenizer is only worth releasing if it beats per-language baselines on fertility (tokens per word) and unknown-token rate.

## Scope
- Languages: Akan/Twi (aka_Latn, twi_Latn), Ewe (ewe), Ga (gaa), Fante (fat). Confirm codes against each corpus.
- In scope: normalization, training, encoding, decoding, Python bindings, evaluation, Hugging Face release.
- Out of scope: language models, speech, Common Crawl collection, GPU code.

## Architecture
- Core: Rust crate depending on the `tokenizers` crate (Hugging Face). Use its BPE or Unigram model, its normalizer and pre-tokenizer traits, and its training API. Write custom code only for Kwa-specific normalization and balanced multilingual training.
- Bindings: PyO3 with maturin. Build abi3 wheels so one wheel covers multiple Python versions.
- Output: `tokenizer.json` loadable by `transformers.AutoTokenizer`.

## Normalization (Kwa-specific, custom)
- Unicode NFC.
- Map inconsistent variants of ɛ, ɔ, ŋ, ɖ, ɣ to one canonical form. Make the mapping a data file, not hard-coded.
- Keep tone marks and diacritics as-is unless a flag says otherwise. Make stripping a configurable option.
- Collapse whitespace. Do not lowercase by default.

## Training
- Algorithm: BPE (byte-level) and Unigram, compare both.
- Vocabulary sizes to try: 8k, 16k, 32k.
- Corpus: pooled text from all four languages, with per-language upsampling so smaller languages are not drowned out. Record exact counts per language.
- Seed fixed; save the config alongside each tokenizer.

## Evaluation
Run on held-out text per language:
1. Fertility: tokens per word.
2. Share of words split into more than two pieces.
3. Unknown-token rate (should be 0 for byte-level).
4. Compression ratio.

Baselines:
- Per-language tokenizers: Goldfish Twi (twi_latn), Wikilangs Ewe (ee).
- A general multilingual tokenizer, such as NLLB's SentencePiece.

Release only if the joint tokenizer matches or beats per-language baselines on fertility.

## Tests
- `cargo test`: normalizer rules, training determinism, round-trip decode(encode(x)) equals normalized x on the test set.
- `pytest`: binding parity with the Python `tokenizers` package on the same config.
- Criterion benchmark: encode throughput, reported against the Python package.

## Deliverables
1. Rust crate and PyO3 package with a README.
2. Trained tokenizer files for each vocabulary size, with config.
3. Evaluation table (fertility, split rate, compression) per language and baseline.
4. Hugging Face model card: training data and sources, normalization rules, license, known limitations, bias notes.
5. Licence file. Check the terms of every corpus before choosing one.

## Open questions
- Which corpora are licensed for release? (MADLAD-400, Glot500, MGhana-ST, Wikipedia dumps)
- Ga and Fante coverage: is there enough clean text to include them?
- Final license for code and tokenizer files.
- Naming and Hugging Face organization.
