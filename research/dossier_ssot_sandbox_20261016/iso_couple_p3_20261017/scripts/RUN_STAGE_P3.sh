#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${RUST_ROOT:-}" ]]; then
 export PATH="$RUST_ROOT/bin:$PATH"
 export LD_LIBRARY_PATH="$RUST_ROOT/lib:${LD_LIBRARY_PATH:-}"
fi
: "${CARGO_BUILD_JOBS:=1}"
export CARGO_BUILD_JOBS CARGO_INCREMENTAL=0 RUST_BACKTRACE=0
command -v rustc >/dev/null || { echo 'MISSING_OFFLINE_RUST_TOOLCHAIN: set RUST_ROOT' >&2; exit 41; }
python "$ROOT/scripts/verify_owner.py"
crate="$ROOT/rust/rei_iso_couple_p3"
cd "$crate"
cargo test --offline --locked > "$ROOT/evidence/REPLAY_UNIT_TESTS.log" 2>&1
cargo clippy --all-targets --offline --locked -- -D warnings > "$ROOT/evidence/REPLAY_CLIPPY.log" 2>&1
rustfmt --check --edition 2024 --config skip_children=true src/lib.rs src/source_age.rs src/positive_age.rs tests/p3_positive_age.rs tests/p3_source_age.rs examples/p3_positive_campaign.rs examples/p3_campaign.rs examples/p3_deep_refinement.rs examples/p3_geometric_age.rs examples/p3_spectral_scan.rs > "$ROOT/evidence/REPLAY_FMT.log" 2>&1
cargo run --release --offline --locked --example p3_positive_campaign > "$ROOT/evidence/REPLAY_POSITIVE_CAMPAIGN.csv" 2> "$ROOT/evidence/REPLAY_POSITIVE_BUILD.log"
cargo run --release --offline --locked --example p3_geometric_age > "$ROOT/evidence/REPLAY_GEOMETRY.csv" 2> "$ROOT/evidence/REPLAY_GEOMETRY_BUILD.log"
python "$ROOT/scripts/validate_replay.py"
echo 'PASS_SCOPED_REPRODUCIBLE_ISO_COUPLE_P3'
