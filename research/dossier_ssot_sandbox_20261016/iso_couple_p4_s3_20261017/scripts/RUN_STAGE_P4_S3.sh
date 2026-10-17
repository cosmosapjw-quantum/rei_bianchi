#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="${RUST_ROOT:-/mnt/data/rust-1.94.1-prefix}/bin:$PATH"
export CARGO_BUILD_JOBS=1
CRATE="$HERE/rei_iso_couple_p4_s3"
mkdir -p "$HERE/evidence/reproduced"
python "$HERE/scripts/verify_owners.py"
(cd "$CRATE" && cargo --offline --locked test --all-targets >"$HERE/evidence/reproduced/TESTS.log" 2>&1)
(cd "$CRATE" && cargo --offline --locked clippy --all-targets -- -D warnings >"$HERE/evidence/reproduced/CLIPPY.log" 2>&1)
(cd "$CRATE" && rustfmt --check --edition 2024 src/retarded_transport.rs src/positive_spectral.rs tests/p4_retarded.rs examples/p4_scalar_varying.rs examples/p4_retarded_campaign.rs)
(cd "$CRATE" && cargo --offline --locked run --release --example p4_scalar_varying > "$HERE/evidence/reproduced/scalar_manufactured.csv")
(cd "$CRATE" && cargo --offline --locked run --release --example p4_retarded_campaign > "$HERE/evidence/reproduced/native_retarded_campaign.csv")
cmp "$HERE/evidence/scalar_manufactured.csv" "$HERE/evidence/reproduced/scalar_manufactured.csv"
cmp "$HERE/evidence/native_retarded_campaign.csv" "$HERE/evidence/reproduced/native_retarded_campaign.csv"
python "$HERE/scripts/analyze_scalar.py"
python "$HERE/scripts/analyze_native.py"
echo P4_S3_BOUNDED_REPLAY_PASS
