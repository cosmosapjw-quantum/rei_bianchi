#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/validate_ssot.py
export PATH="/mnt/data/rust-1.94.1-prefix/bin:$PATH"
export LD_LIBRARY_PATH="/mnt/data/rust-1.94.1-prefix/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1
rustc --version
cargo test --offline --locked --manifest-path rust/rei_ssot_reference/Cargo.toml