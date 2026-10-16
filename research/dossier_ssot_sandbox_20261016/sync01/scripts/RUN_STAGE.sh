#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="${RUST_PREFIX:-/mnt/data/rust-1.94.1-prefix}/bin:$PATH"
export CARGO_BUILD_JOBS=1
M="$HERE/rust/rei_pr104_geom/Cargo.toml"
cargo test --offline --locked --manifest-path "$M"
cargo fmt --manifest-path "$M" --all -- --check
cargo clippy --offline --locked --manifest-path "$M" --all-targets -- -D warnings
cargo run --offline --locked --quiet --manifest-path "$M"
