#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
M="$ROOT/rust/rei_iso_couple_reference/Cargo.toml"
: "${CARGO_TARGET_DIR:=$ROOT/.local_target}"
export CARGO_TARGET_DIR CARGO_BUILD_JOBS=1 CARGO_INCREMENTAL=0 RUST_BACKTRACE=0
python3 "$ROOT/scripts/verify_source_identity.py"
cargo test --offline --locked --manifest-path "$M"
cargo clippy --offline --locked --manifest-path "$M" --all-targets -- -D warnings
# Not cargo fmt: must never modify frozen #[path] original owner sources.
(cd "$ROOT/rust/rei_iso_couple_reference" && rustfmt --check --edition 2024 src/mixture_coupling.rs tests/iso_couple.rs examples/campaign.rs examples/savin_balance_scan.rs)
mkdir -p "$ROOT/evidence"
cargo run --release --offline --locked --manifest-path "$M" --example campaign > "$ROOT/evidence/convergence_campaign.csv"
cargo run --release --offline --locked --manifest-path "$M" --example savin_balance_scan > "$ROOT/evidence/savin_detailed_balance_diagnostic.csv"
python3 "$ROOT/scripts/validate_campaign.py"
python3 "$ROOT/scripts/verify_source_identity.py"
echo PASS_SCOPED_ISO_COUPLE
