#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/rust/rei_iso_eos_reference/Cargo.toml"
command -v cargo >/dev/null || { echo 'CARGO_UNAVAILABLE' >&2; exit 13; }
export CARGO_BUILD_JOBS=1 CARGO_INCREMENTAL=0
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$ROOT/target}"
python3 "$ROOT/scripts/validate_source_identity.py"
cargo test --offline --locked --manifest-path "$MANIFEST"
cargo clippy --offline --locked --manifest-path "$MANIFEST" --all-targets -- -D warnings
cargo run --offline --locked --manifest-path "$MANIFEST" --bin eos_probe
cargo run --offline --locked --manifest-path "$MANIFEST" --bin eos_sweep
# All rustfmt operations MUST skip the #[path]-imported owner modules.
(cd "$ROOT/rust/rei_iso_eos_reference" && rustfmt --check --edition 2024 src/mixture_eos.rs src/bin/eos_probe.rs src/bin/eos_sweep.rs tests/iso_eos.rs)
