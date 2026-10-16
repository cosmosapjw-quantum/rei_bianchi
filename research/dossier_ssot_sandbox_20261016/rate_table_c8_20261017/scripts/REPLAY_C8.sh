#!/bin/bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
ARCHIVE=${1:-"$HERE/upstream/REI_FLRW_RATE_TABLE_ACCELERATION_20261016_C07_v1.zip"}
OUT=${2:-"$HERE/replay_work"}
RUST_BIN=${RUST_BIN:-/mnt/data/rust-1.94.1-prefix/bin}
export PATH="$RUST_BIN:$PATH"
export LD_LIBRARY_PATH="$(dirname "$RUST_BIN")/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1
python3 "$HERE/scripts/restore_source.py" "$ARCHIVE" "$OUT" "$HERE/input_metadata/joint_affine.restored.rs" "$HERE/tests/c8_rate_study.rs" "$HERE/input_metadata/Cargo.lock"
cd "$OUT"
cargo test --release --offline --locked --manifest-path rust/rei_microphysics/Cargo.toml --test c8_rate_study -- --nocapture
