#!/usr/bin/env bash
set -euo pipefail
PKG=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
RUST_BIN=${RUST_BIN:-/mnt/data/rust-1.94.1-prefix/bin}
export PATH="$RUST_BIN:$PATH"
export LD_LIBRARY_PATH="$(dirname "$RUST_BIN")/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1
WORK=${1:-"$PKG/work_fresh"}
python3 "$PKG/scripts/restore_c9.py" \
  "$PKG/source/REI_FLRW_RATE_TABLE_ACCELERATION_20261016_C07_v1.zip" "$WORK" \
  "$PKG/source/joint_affine.rs" "$PKG/review/c9_independent_review.rs" "$PKG/source/Cargo.lock"
cargo test --release --offline --locked --manifest-path "$WORK/rust/rei_microphysics/Cargo.toml" --test c9_independent_review -- --nocapture
cargo test --release --offline --locked --manifest-path "$PKG/policy/Cargo.toml"
cargo fmt --all --manifest-path "$PKG/policy/Cargo.toml" -- --check
cargo clippy --release --offline --locked --manifest-path "$PKG/policy/Cargo.toml" --all-targets -- -D warnings
