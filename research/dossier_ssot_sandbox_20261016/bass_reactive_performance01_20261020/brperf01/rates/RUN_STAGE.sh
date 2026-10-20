#!/usr/bin/env bash
set -euo pipefail
rate_unit_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$rate_unit_dir/../runtime/env.sh"
export CARGO_TARGET_DIR="$rate_unit_dir/target"
mkdir -p "$rate_unit_dir/evidence"
cargo fmt --manifest-path "$rate_unit_dir/Cargo.toml" -- --check
cargo test --offline --manifest-path "$rate_unit_dir/Cargo.toml"
cargo clippy --offline --manifest-path "$rate_unit_dir/Cargo.toml" --all-targets -- -D warnings
cargo run --release --offline --manifest-path "$rate_unit_dir/Cargo.toml" --example measure_rates -- probe "$rate_unit_dir/evidence"
python "$rate_unit_dir/validate_pchip.py"
# Invoke with --bench only when other units are not running timing workloads.
if [[ "${1:-}" == "--bench" ]]; then
  cargo run --release --offline --manifest-path "$rate_unit_dir/Cargo.toml" --example measure_rates -- bench "$rate_unit_dir/evidence"
  python "$rate_unit_dir/summarize_bench.py"
fi
