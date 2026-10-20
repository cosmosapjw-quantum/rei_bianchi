#!/usr/bin/env bash
set -euo pipefail
# Activate the supplied isolated Rust toolchain before invoking this script.
# This subunit needs only Rust std and Python stdlib; no network/download step.
ATOMIC_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ATOMIC_EVIDENCE=${1:-"$ATOMIC_ROOT/evidence"}
mkdir -p "$ATOMIC_EVIDENCE"
python "$ATOMIC_ROOT/generate_catalog.py" > "$ATOMIC_EVIDENCE/PARSER_RUN.log" 2>&1
cargo fmt --manifest-path "$ATOMIC_ROOT/catalog/Cargo.toml"
cargo fmt --check --manifest-path "$ATOMIC_ROOT/catalog/Cargo.toml" > "$ATOMIC_EVIDENCE/RUSTFMT.log" 2>&1
cargo test --offline --locked --manifest-path "$ATOMIC_ROOT/catalog/Cargo.toml" > "$ATOMIC_EVIDENCE/RUST_TESTS.log" 2>&1
cargo clippy --offline --locked --all-targets --manifest-path "$ATOMIC_ROOT/catalog/Cargo.toml" -- -D warnings > "$ATOMIC_EVIDENCE/CLIPPY.log" 2>&1
cargo run --release --offline --locked --manifest-path "$ATOMIC_ROOT/catalog/Cargo.toml" --example validate_catalog -- "$ATOMIC_EVIDENCE" > "$ATOMIC_EVIDENCE/RUST_EXPERIMENT.log" 2>&1
python "$ATOMIC_ROOT/validate_independent.py" "$ATOMIC_EVIDENCE" > "$ATOMIC_EVIDENCE/PYTHON_ORACLE.log" 2>&1
printf 'Atomic catalog: source parser, Rust tests, strict Clippy, rustfmt, release experiment and Python Decimal60 oracle completed.\n'
