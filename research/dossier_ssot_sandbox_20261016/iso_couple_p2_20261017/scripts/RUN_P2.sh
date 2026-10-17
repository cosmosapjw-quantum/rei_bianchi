#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CARGO_DIR="$ROOT/rust/rei_iso_couple_p2"
mkdir -p "$ROOT/evidence"
export CARGO_BUILD_JOBS=1 CARGO_INCREMENTAL=0
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$ROOT/.cargo-build-cache}"
python3 "$ROOT/scripts/verify_source.py" > "$ROOT/evidence/SOURCE_IDENTITY_REPLAY.json"
(
 cd "$CARGO_DIR"
 for f in src/full_network.rs src/igm_state.rs tests/iso_couple_p2.rs examples/p2_campaign.rs; do
  rustfmt --check --edition 2024 "$f"
 done
 cargo test --offline --locked > "$ROOT/evidence/RUST_TESTS_REPLAY.log" 2>&1
 cargo clippy --all-targets --offline --locked -- -D warnings > "$ROOT/evidence/CLIPPY_REPLAY.log" 2>&1
 cargo run --release --offline --locked --example p2_campaign > "$ROOT/evidence/P2_CAMPAIGN_REPLAY.csv" 2> "$ROOT/evidence/CAMPAIGN_REPLAY.log"
)
python3 "$ROOT/scripts/compare_campaign.py" > "$ROOT/evidence/CSV_COMPARISON_REPLAY.log"
python3 "$ROOT/scripts/analyze_campaign.py" > "$ROOT/evidence/ANALYSIS_REPLAY.log"
echo "P2_REPLAY_PASS: source10, rust tests, clippy, 45 histories, campaign parser"
