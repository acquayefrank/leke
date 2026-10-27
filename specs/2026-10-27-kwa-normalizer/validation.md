# Phase 1: Kwa Normalizer & Character Mapping — Validation

Criteria to verify Phase 1 implementation.

## 1. Character Substitutions

- Given text containing Greek epsilon `ε` or phonetic variants, `normalize` returns Latin Open E `ɛ` (U+025B).
- Given text containing Greek gamma `γ` or phonetic variants, `normalize` returns Latin Gamma `ɣ` (U+0263).
- Given text containing alternate Open O, Eng `ŋ`, or D with tail `ɖ`, `normalize` produces canonical Latin equivalents.
- Both uppercase and lowercase variants map symmetrically.

## 2. Diacritic & Tone Preservation

- Default behavior (`strip_accents: false`): `pápá` remains `pápá`, `mìedó gbe` remains `mìedó gbe`.
- Optional behavior (`strip_accents: true`): `pápá` produces `papa`, `mìedó gbe` produces `miedo gbe`.

## 3. Idempotence & Whitespace

- Double normalization test: for any string $s$, `normalize(normalize(s)) == normalize(s)`.
- Whitespace collapsing: `"  Me   pe   kasa   "` -> `"Me pe kasa"`.
- Casing preservation: `"Akan Twi Ewe Ga"` retains original capitalizations.

## 4. Test Suite Execution

- `cargo test` runs and passes all Rust normalizer tests.
- `uv run pytest` runs and passes all Python integration tests.

## Merge Criteria

All four criteria must pass without errors. Once validated, open a PR and merge into `main`.
