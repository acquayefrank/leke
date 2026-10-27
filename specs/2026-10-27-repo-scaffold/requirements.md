# Phase 0: Workspace & Toolchain Scaffold — Requirements

**Roadmap source:** `specs/roadmap.md`, Phase 0 — "Workspace & Toolchain Scaffold". This is the first unbuilt phase; the repository currently contains only the specs constitution and context handoff, with no build manifests, source files, or virtual environments present.

**Branch:** `repo-scaffold`, cut from baseline `main` at commit `9e3bca8`.

## Scope

In scope, per roadmap Phase 0:

1. Create comprehensive `.gitignore` covering Rust build targets, Python bytecode, virtual environments, maturin build artifacts, and system cache files.
2. Initialize root `Cargo.toml` configuring the `leke` Rust crate with both `rlib` and `cdylib` crate types, depending on `pyo3` (with `abi3-py39` feature) and `tokenizers`.
3. Create `pyproject.toml` using `maturin` as the build backend, configuring Python packaging metadata for `leke` and defining core dependencies (`tokenizers`, `transformers`, `pytest`).
4. Implement minimal `src/lib.rs` establishing the PyO3 module `_leke` and pure Python package wrapper `python/leke/__init__.py`.
5. Provide a verification script `scripts/dev-check.sh` that checks toolchains, compiles the extension via `uv run maturin develop`, and tests basic import.

## Explicitly Out of Scope

1. Kwa-specific normalization logic and character tables (deferred to Phase 1: `kwa-normalizer`).
2. Training datasets and corpus ingestion pipelines (deferred to Phase 2: `corpus-pipeline`).
3. Training engine and subword models (deferred to Phase 3: `bpe-training` and Phase 6: `unigram-comparison`).

## Decisions (Confirmed via Project Constitution)

1. **Toolchain**: Use `uv` and `maturin` targeting `abi3-py39` to provide fast, deterministic Python virtualenv resolution and single-wheel cross-Python compatibility.
2. **Dual Crate Layout**: Configure both `cdylib` (for Python extension) and `rlib` (for internal Rust benchmarking and unit testing) in `Cargo.toml`.
3. **Execution Environment**: Execute build, lint, test, and git commands via WSL Ubuntu where Rust and uv are fully configured.

## Guardrails from mission.md / tech-stack.md

- **Tech Stack Architecture**: Must follow the two-layer architecture defined in `specs/tech-stack.md` (Rust core engine + Python wrapper).
- **Standards Compliance**: The packaging structure must produce a drop-in importable Python package `leke`.
