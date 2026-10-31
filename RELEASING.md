# Releasing Leke

Python releases are built and published by `.github/workflows/release.yml` when a `v*` tag is pushed. Tokenizer bundles reach the Hugging Face Hub separately, through `.github/workflows/publish-hf.yml`, whenever `models/bpe-16k/` or `models/bpe-32k/` changes on `main`.

## One-time setup

1. On PyPI, add a pending trusted publisher for the project `leke` (Account settings → Publishing):
   - Owner `acquayefrank`, repository `leke`
   - Workflow `release.yml`
   - Environment `pypi`
2. On GitHub, create the `pypi` environment (Settings → Environments). Restricting it to `v*` tags and requiring your approval is recommended.

## Checklist

1. Bump the version in **both** `pyproject.toml` and `Cargo.toml`, and the expected string in the `test_version` unit test in `src/lib.rs`. Run `uv lock` and `cargo check` so the lock files follow.
2. Make sure `specs/eval_results.md`, the model cards in `models/*/README.md` and the README benchmark tables match the shipped models.
3. Dry run: **Actions → Release → Run workflow** on `main`. It builds every wheel and the sdist and installs them on Linux, macOS and Windows, without publishing.
4. Merge the version bump to `main`, then tag and push:
   ```bash
   git tag -a v0.1.0 -m "Leke v0.1.0"
   git push origin v0.1.0
   ```
5. The workflow checks that the tag matches both version strings, runs the tests, builds and installs the wheels, publishes to PyPI, then creates the GitHub release with the wheels and sdist attached.
6. Check that the release works: `pip install leke==<version>` in a fresh environment, then `python -c "import leke; print(leke.__version__)"`.

A version can only be uploaded to PyPI once. If something is wrong after publishing, fix it and release a new patch version.
