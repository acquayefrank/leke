# Phase 0: Workspace & Toolchain Scaffold — Plan

Numbered task groups for Phase 0 implementation.

## 1. Git and Workspace Hygiene (.gitignore)

- Add comprehensive `.gitignore` ignoring:
  - `target/`
  - `.venv/`, `venv/`, `env/`
  - `__pycache__/`, `*.py[cod]`
  - `*.so`, `*.pyd`, `*.dylib`
  - `dist/`, `build/`, `*.egg-info/`
  - `.pytest_cache/`, `.coverage`
  - `data/raw/`, `data/processed/` (data directory tracking discipline)

## 2. Rust Crate Configuration (Cargo.toml)

- Create root `Cargo.toml` with:
  - Package name `leke`, version `0.1.0`, edition `2021`.
  - Crate types `["cdylib", "rlib"]`.
  - Core dependencies: `pyo3` with `features = ["extension-module", "abi3-py39"]`, `tokenizers`, `unicode-normalization`, `serde`, `serde_json`.

## 3. Python Packaging and Environment (pyproject.toml)

- Create `pyproject.toml` with:
  - `build-system`: `requires = ["maturin>=1.7,<2.0"]`, `build-backend = "maturin"`.
  - `[project]`: name `leke`, version `0.1.0`, `requires-python = ">=3.9"`.
  - Dependencies: `pytest`, `tokenizers`, `transformers`, `tabulate`.
  - Maturin config: `module-name = "leke._leke"`, `python-source = "python"`.

## 4. Rust Core Stub and Python Bridge

- Create `src/lib.rs`:
  - Define native function `leke_version() -> &'static str`.
  - Define PyO3 module `_leke` exposing `version()`.
- Create Python package layout:
  - `python/leke/__init__.py` re-exporting `__version__` and stub functions.
  - `python/leke/py.typed` marker.

## 5. Developer Verification Script

- Create executable script `scripts/dev-check.sh` testing:
  - Rust compilation (`cargo check`, `cargo test`).
  - Python environment setup and build (`uv sync`, `uv run maturin develop`).
  - Python import verification (`uv run python -c "import leke; print(leke.version())"`).

## 6. Validation Pass

- Run the checks in `validation.md`. Fix any failures.

## 7. PR

- Open a PR from `repo-scaffold` into `main` using `gh pr create`.
- Confirm PR description links Phase 0 requirements and validation results.
