# Phase 1: Kwa Normalizer & Character Mapping — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 1 — "Kwa Normalizer & Character Mapping". Phase 0 established the toolchain and workspace. Phase 1 implements the linguistic normalization rules required for Kwa languages before corpus ingestion and training.

**Branch:** `kwa-normalizer`, cut from `main` at commit `f074674`.

## Scope

In scope, per roadmap Phase 1:

1. Create canonical character mapping data file `data/char_mappings.json` defining standard mappings for `ɛ`, `ɔ`, `ŋ`, `ɖ`, `ɣ` (both lowercase and uppercase variants, including non-standard Unicode Latin/IPA variations) to canonical NFC codepoints.
2. Implement `KwaNormalizer` struct in Rust (`src/normalizer.rs`) with:
   - Unicode NFC canonicalization via `unicode_normalization`.
   - Table-driven character substitution loaded from mapping data.
   - Whitespace collapsing (`\s+` -> `' '`, leading/trailing trim).
   - Case preservation (casing is preserved, never lowercased by default).
   - Configurable tone/diacritic handling (`strip_accents: bool`, defaulting to `false`).
3. Expose `KwaNormalizer` to Python via PyO3 so Python callers can inspect and normalize text.
4. Comprehensive unit and property test suites verifying idempotency, character substitution, tone preservation, and stripping.

## Explicitly Out of Scope

1. Corpus scraping or dataset downloading (Phase 2: `corpus-pipeline`).
2. Subword tokenization and vocabulary training (Phase 3: `bpe-training`).
3. Unconditional lowercasing (invariant in `specs/mission.md`).

## Decisions (Confirmed via Project Constitution)

1. **Externalized Data**: All character mappings must be stored in `data/char_mappings.json`, not hardcoded in Rust source code.
2. **Tone Preservation**: Tone marks (acute, grave, circumflex, macron) are retained by default to maintain semantic distinctions in Akan/Twi and Ewe.
3. **Idempotence**: `normalize(normalize(text)) == normalize(text)` must hold for all inputs.

## Guardrails from mission.md / tech-stack.md

- **Normalization Architecture**: Follows `specs/tech-stack.md` Section 3 (NFC -> Variant Map -> Whitespace -> Configurable tone stripping).
- **Zero OOV Foundation**: Clean normalized text ensures consistent subwords without fragmenting character variants.
