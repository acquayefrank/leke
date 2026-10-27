# Phase 1: Kwa Normalizer & Character Mapping — Plan

Numbered task groups for Phase 1 implementation.

## 1. Character Mapping Data Asset (`data/char_mappings.json`)

- Create `data/char_mappings.json` containing:
  - Canonical representations:
    - `ɛ` (U+025B) and `Ɛ` (U+0190) (Open E / Latin Epsilon)
    - `ɔ` (U+0254) and `Ɔ` (U+0186) (Open O)
    - `ŋ` (U+014B) and `Ŋ` (U+014A) (Eng)
    - `ɖ` (U+0256) and `Ɖ` (U+0189) (D with tail)
    - `ɣ` (U+0263) and `Ɣ` (U+0194) (Gamma)
  - Mapping variant phonetic glyphs, Greek lookalikes (e.g., Greek epsilon `ε` U+03B5, Greek gamma `γ` U+03B3), Cyrillic lookalikes, and precomposed forms to standard African reference Latin codepoints.

## 2. Rust Normalizer Module (`src/normalizer.rs`)

- Define `KwaNormalizerConfig`:
  - `strip_accents: bool` (default `false`)
  - `collapse_whitespace: bool` (default `true`)
- Implement `KwaNormalizer`:
  - Embed default mapping data via `include_str!("../data/char_mappings.json")` with ability to load custom mapping files or JSON strings.
  - Implement normalization method `normalize(&self, text: &str) -> String`:
    1. Unicode NFC decomposition/recomposition.
    2. Character variant replacement.
    3. Diacritic / tone mark stripping if `strip_accents == true`.
    4. Whitespace collapsing and trimming if `collapse_whitespace == true`.
- Implement `tokenizers::normalizer::Normalizer` trait on `KwaNormalizer` so it plugs directly into Hugging Face `tokenizers` pipelines.

## 3. PyO3 Binding Integration

- Expose `KwaNormalizer` to Python:
  - `normalize(text: str) -> str`
  - Constructor accepting optional `strip_accents: bool` and optional `custom_mappings_path: Optional[str]`.
- Re-export `KwaNormalizer` in `python/leke/__init__.py`.

## 4. Test Suite Implementation

- Rust unit tests in `src/normalizer.rs`:
  - Test character variant replacement for each mapped character.
  - Test tone preservation vs stripping on accented Akan and Ewe phrases (e.g. `pápá` -> `pápá` vs `papa`).
  - Test whitespace collapsing.
  - Test idempotence property: `normalize(normalize(s)) == normalize(s)`.
- Python tests in `tests/test_normalizer.py`:
  - Test Python API equivalence and edge cases.

## 5. Validation Pass

- Run `cargo test` and `uv run pytest`. Fix any issues.

## 6. PR

- Push `kwa-normalizer` to origin, create PR via `gh pr create --fill`, merge to `main`.
