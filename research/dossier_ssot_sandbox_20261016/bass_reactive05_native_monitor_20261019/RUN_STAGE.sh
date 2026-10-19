#!/usr/bin/env bash
set -euo pipefail
rei_unit_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
rei_mode="${1:-verify}"
rei_python="${REI_BR05_PYTHON:-python3}"
"$rei_python" "$rei_unit_dir/scripts/verify_identity.py" --root "$rei_unit_dir"
if [[ "$rei_mode" == verify ]]; then exit 0; fi
rei_output="${REI_BR05_OUTPUT:-$(mktemp -d /tmp/rei-br05-replay-XXXXXXXX)}"
mkdir -p -- "$rei_output"
export CARGO_TARGET_DIR="${REI_BR05_TARGET:-$rei_output/cargo-target}"
rei_manifest="$rei_unit_dir/br05/Cargo.toml"
case "$rei_mode" in
  test)
    cargo test --offline --locked --manifest-path "$rei_manifest" --all-targets --jobs 2
    cargo clippy --offline --locked --manifest-path "$rei_manifest" --all-targets --jobs 2 -- -D warnings
    rustfmt --edition 2021 --check --config skip_children=true \
      "$rei_unit_dir/crate/br05_lib.rs" "$rei_unit_dir/crate/monitored_midpoint.rs" \
      "$rei_unit_dir/crate/native_birth_monitor.rs" "$rei_unit_dir/crate/native_monitor_csv.rs" \
      "$rei_unit_dir/crate/native_birth_monitor_driver.rs" "$rei_unit_dir/crate/tests/native_birth_monitor.rs"
    ;;
  light)
    cargo test --offline --locked --manifest-path "$rei_manifest" --test native_birth_monitor --jobs 2
    (cd -- "$rei_unit_dir/scripts" && "$rei_python" -m unittest -v test_br05_pair test_monitor_reference)
    cargo build --offline --locked --release --manifest-path "$rei_manifest" --example native_birth_monitor_driver --jobs 2
    "$CARGO_TARGET_DIR/release/examples/native_birth_monitor_driver" \
      SIGNED_MINUS 121 1 0 1e9 false false 2 4 1e-12 1 "$rei_output/sample_monitor" \
      > "$rei_output/sample.csv" 2> "$rei_output/sample.stderr"
    "$rei_python" "$rei_unit_dir/scripts/audit_native_monitor.py" \
      --monitor "$rei_output/sample_monitor" --native "$rei_output/sample.csv" --output "$rei_output/sample_audit"
    ;;
  analyze)
    "$rei_python" "$rei_unit_dir/scripts/analyze_br05_pair.py" --root "$rei_unit_dir" --output "$rei_output/pair"
    "$rei_python" "$rei_unit_dir/scripts/audit_native_monitor.py" \
      --monitor "$rei_unit_dir/evidence/native/monitor_n16_r8" \
      --native "$rei_unit_dir/evidence/native/ap_n16_r8.csv" --output "$rei_output/monitor"
    "$rei_python" "$rei_unit_dir/evidence/theory/verify_native_panels.py" \
      --monitor-dir "$rei_unit_dir/evidence/native/monitor_n16_r8" --out-dir "$rei_output/panels"
    ;;
  native)
    cargo build --offline --locked --release --manifest-path "$rei_manifest" --example native_birth_monitor_driver --jobs 2
    rei_binary="$CARGO_TARGET_DIR/release/examples/native_birth_monitor_driver"
    rei_binary_sha="$("$rei_python" -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$rei_binary")"
    "$rei_python" "$rei_unit_dir/scripts/run_single_native.py" --binary "$rei_binary" \
      --unit-root "$rei_unit_dir" --output "$rei_output/native" --monitor-output "$rei_output/monitor" \
      --expected-binary-sha256 "$rei_binary_sha" --timeout 600
    ;;
  *) printf '%s\n' 'Usage: bash RUN_STAGE.sh {verify|test|light|analyze|native}' >&2; exit 64 ;;
esac
printf 'Replay output: %s\n' "$rei_output"
