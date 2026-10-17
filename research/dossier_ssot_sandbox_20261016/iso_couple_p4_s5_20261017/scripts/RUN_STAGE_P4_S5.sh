#!/usr/bin/env bash
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="${RUST_ROOT:-/mnt/data/rust-1.94.1-prefix}/bin:$PATH"
export LD_LIBRARY_PATH="${RUST_ROOT:-/mnt/data/rust-1.94.1-prefix}/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$R/reproduced/target}"
mkdir -p "$R/reproduced"
python "$R/scripts/verify_owners.py"
cd "$R/rei_iso_couple_p4_s5"
cargo test --offline --locked --all-targets -- --test-threads=1 > "$R/reproduced/test.log" 2>&1
cargo clippy --offline --locked --all-targets -- -D warnings > "$R/reproduced/clippy.log" 2>&1
rustfmt --edition 2024 --check src/age_remainder.rs tests/p5_bounded_tail.rs examples/p5_tail_campaign.rs > "$R/reproduced/fmt.log" 2>&1
cargo run --offline --locked --release --example p5_tail_campaign > "$R/reproduced/p5_tail_campaign.csv" 2> "$R/reproduced/campaign_build.log"
python "$R/scripts/independent_direct_bound.py" > "$R/reproduced/P5_INDEPENDENT_SCIPY.json"
python "$R/scripts/validate_reproduced.py"
echo 'P4S5_NATIVE_RUST_SCOPED_PASS'
