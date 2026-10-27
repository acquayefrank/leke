#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Checking Rust toolchain ==="
cargo check
cargo test

echo "=== 2. Checking Python environment with uv & maturin ==="
uv sync
uv run maturin develop

echo "=== 3. Testing Python package import ==="
uv run python -c "import leke; print('Successfully imported leke, version:', leke.version())"

echo "=== Dev check passed successfully! ==="
