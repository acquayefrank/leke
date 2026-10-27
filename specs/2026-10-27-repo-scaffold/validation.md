# Phase 0: Workspace & Toolchain Scaffold — Validation

Criteria to confirm Phase 0 is complete and ready to merge into `main`.

## 1. Rust Toolchain and Compilation

- `cargo check` succeeds with 0 warnings or errors.
- `cargo test` executes and passes all Rust unit tests.

## 2. Maturin & Python Packaging

- `uv sync` resolves dependencies without conflict.
- `uv run maturin develop` compiles the PyO3 extension module `_leke` without error.
- Python import verification:
  ```bash
  uv run python -c "import leke; print('Leke version:', leke.version())"
  ```
  outputs `Leke version: 0.1.0`.

## 3. Hygiene & Cleanliness

- `.gitignore` properly suppresses generated build folders (`target/`, `.venv/`, `*.so`).
- `git status` reports only intentional source files tracked.

## Merge Criteria

All checks above must pass without workarounds. Once verified, push the `repo-scaffold` branch and open a pull request to `main`.
