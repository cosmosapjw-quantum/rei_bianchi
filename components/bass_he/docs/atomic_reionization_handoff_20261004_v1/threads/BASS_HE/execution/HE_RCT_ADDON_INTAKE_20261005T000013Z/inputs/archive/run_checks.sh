#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PREFIX=${RUST_1_94_1_PREFIX:-/mnt/data/rust-1.94.1-prefix}
export PATH="$PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$PREFIX/lib:${LD_LIBRARY_PATH:-}"
export RUST_BACKTRACE=0
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/bass-he-rct-addon.XXXXXXXX")}
mkdir -p -- "$OUT"
OUT=$(cd -- "$OUT" && pwd)
if [[ -e "$OUT/started.json" ]]; then echo "Output already used: $OUT" >&2;exit 78;fi
printf '{"scope":"standalone_addon_not_owner_production"}\n' > "$OUT/started.json"
python -B "$ROOT/verify_inputs.py" > "$OUT/input_identity.log"
export CARGO_TARGET_DIR="$OUT/target"
{ rustc -Vv; cargo -Vv; } > "$OUT/toolchain.log"
cargo test --manifest-path "$ROOT/addon/Cargo.toml" --locked --offline -- --test-threads=1 > "$OUT/tests.log" 2>&1
cargo run --manifest-path "$ROOT/addon/Cargo.toml" --locked --offline --example step_probe > "$OUT/step_probe.jsonl" 2> "$OUT/probe_build.log"
python -B -W error "$ROOT/oracle/check_endpoint.py" --input "$OUT/step_probe.jsonl" --output "$OUT/independent_endpoint.json" > "$OUT/independent.log"
python -B "$ROOT/verify_inputs.py" > "$OUT/input_identity_after.log"
printf 'Checks finished. Evidence directory: %s\n' "$OUT"
