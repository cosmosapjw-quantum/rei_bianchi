#!/usr/bin/env bash
# Extract the package at any location; run with the attached Rust 1.94.1 env
# sourced, or export CARGO/RUSTC directly. No network or NCP required.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$ROOT/.target_p4_s2}"
cd "$ROOT/rust/rei_iso_couple_p4_s2"
cargo --version
cargo test --offline --locked --all-targets
# Owner src/rate_table.rs has protected non-rustfmt historical bytes.
# Do not run full cargo fmt over immutable owner_src.
rustfmt --check --edition 2024 src/positive_birth_clock.rs tests/p4_birth_clock.rs \
  examples/p4_birth_clock_campaign.rs examples/p4_constant_opacity_oracle.rs
rustfmt --check --edition 2024 --config skip_children=true src/lib.rs
cargo clippy --offline --locked --all-targets -- -D warnings
cargo run --offline --locked --release --example p4_birth_clock_campaign > "$ROOT/evidence/p4_birth_clock_campaign.csv"
cargo run --offline --locked --release --example p4_constant_opacity_oracle > "$ROOT/evidence/p4_constant_opacity_oracle.csv"
python "$ROOT/scripts/validate_science.py"
