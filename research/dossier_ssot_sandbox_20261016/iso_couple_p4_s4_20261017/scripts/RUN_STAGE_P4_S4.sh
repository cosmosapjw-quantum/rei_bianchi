#!/usr/bin/env bash
set -euo pipefail
R="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="${RUST_ROOT:-/mnt/data/rust-1.94.1-prefix}/bin:$PATH"
export LD_LIBRARY_PATH="${RUST_ROOT:-/mnt/data/rust-1.94.1-prefix}/lib:${LD_LIBRARY_PATH:-}"
export CARGO_BUILD_JOBS=1
python "$R/scripts/verify_owners.py"
cd "$R/rei_iso_couple_p4_s4"
mkdir -p "$R/reproduced"
cargo test --offline --locked --all-targets -q > "$R/reproduced/test.log" 2>&1
cargo clippy --offline --locked --all-targets -- -D warnings > "$R/reproduced/clippy.log" 2>&1
rustfmt --edition 2024 --check src/threshold_roots.rs src/retarded_transport_threshold.rs tests/p4_threshold.rs examples/p4_cache_benchmark.rs examples/p4_threshold_oracle.rs examples/p4_zero_compression.rs > "$R/reproduced/fmt.log" 2>&1
cargo run --release --offline --locked -q --example p4_threshold_oracle > "$R/reproduced/verner_threshold_error.csv"
cargo run --release --offline --locked -q --example p4_zero_compression > "$R/reproduced/age_exactzero_campaign_12.csv"
cargo run --release --offline --locked -q --example p4_cache_benchmark > "$R/reproduced/native_cache_benchmark.csv"
python "$R/scripts/scipy_verner_reference.py" > "$R/reproduced/scipy_verner_stdout.json"
python "$R/scripts/validate.py"
echo 'P4_S4_SCOPED_PASS'
