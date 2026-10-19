#!/usr/bin/env bash
# BR04 reproduction: read source/evidence, write every new result outside it.
set -Eeuo pipefail
REI_PACKAGE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REI_STAGE="${1:-light}"
if [[ $# -gt 0 ]]; then shift; fi
case "$REI_STAGE" in
  verify|light|test|native|all) ;;
  *) printf 'Usage: %s {verify|light|test|native|all} [ap_n16_r4|ap_n64_r4 ...]\n' "$0" >&2; exit 2 ;;
esac
if [[ -n "${REI_RUST_PREFIX:-}" ]]; then
  export PATH="$REI_RUST_PREFIX/bin:$PATH"
  export LD_LIBRARY_PATH="$REI_RUST_PREFIX/lib:${LD_LIBRARY_PATH:-}"
fi
if [[ -n "${REI_RUN_OUTPUT:-}" ]]; then
  if [[ -e "$REI_RUN_OUTPUT" ]]; then
    printf 'OUTPUT_ALREADY_EXISTS: %s\n' "$REI_RUN_OUTPUT" >&2; exit 2
  fi
  mkdir -p -- "$REI_RUN_OUTPUT"
else
  REI_RUN_OUTPUT="$(mktemp -d "${TMPDIR:-/tmp}/rei_br04_run.XXXXXX")"
fi
REI_RUN_OUTPUT="$(cd -- "$REI_RUN_OUTPUT" && pwd -P)"
mkdir -- "$REI_RUN_OUTPUT/logs"
export CARGO_TARGET_DIR="${REI_CARGO_TARGET:-$REI_RUN_OUTPUT/target}"
export PYTHONDONTWRITEBYTECODE=1
REI_MANIFEST="$REI_PACKAGE_ROOT/br04/Cargo.toml"
REI_CURRENT_STEP=bootstrap
REI_CARGO_JOBS="${REI_CARGO_JOBS:-2}"
REI_TEST_THREADS="${REI_TEST_THREADS:-2}"
record_failure() {
  local code=$?
  trap - ERR
  python3 - "$REI_RUN_OUTPUT/RUN_FAILURE.json" "$REI_STAGE" "$REI_CURRENT_STEP" "$code" <<'PY' || true
import datetime,json,pathlib,sys
p,stage,step,code=sys.argv[1:]
pathlib.Path(p).write_text(json.dumps({"status":"REPRODUCTION_STEP_FAILED","stage":stage,"step":step,"exit_code":int(code),"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"classification":"Inspect raw log; execution, work limit, representation limit and physical failure are separate."},indent=2)+'\n')
PY
  printf 'FAILED step=%s exit=%s; logs=%s\n' "$REI_CURRENT_STEP" "$code" "$REI_RUN_OUTPUT" >&2
  exit "$code"
}
trap record_failure ERR
run_logged() {
  local name=$1; shift
  REI_CURRENT_STEP="$name"
  printf 'Running %s\n' "$name"
  python3 - "$REI_RUN_OUTPUT/logs/$name.command.json" "$@" <<'PY'
import json,pathlib,sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({"argv":sys.argv[2:]},indent=2)+'\n')
PY
  "$@" > "$REI_RUN_OUTPUT/logs/$name.log" 2>&1
}
run_logged verify_before python3 "$REI_PACKAGE_ROOT/verify_manifest.py" --root "$REI_PACKAGE_ROOT"
if [[ "$REI_STAGE" != verify ]]; then
  run_logged rustc_version rustc --version --verbose
  run_logged cargo_version cargo --version
  run_logged version_gate python3 - "$REI_RUN_OUTPUT/logs/rustc_version.log" "$REI_RUN_OUTPUT/logs/cargo_version.log" <<'PY'
import pathlib,sys
for p,tool in zip(sys.argv[1:],["rustc","cargo"]):
    words=pathlib.Path(p).read_text().splitlines()[0].split()
    assert words[:2]==[tool,"1.94.1"],(tool,words)
print("Rust/Cargo 1.94.1 identity matched")
PY
fi
if [[ "$REI_STAGE" == test || "$REI_STAGE" == all ]]; then
  run_logged all_rust_tests cargo test --manifest-path "$REI_MANIFEST" --offline --locked --all-targets --jobs "$REI_CARGO_JOBS" -- --test-threads "$REI_TEST_THREADS"
  run_logged strict_clippy cargo clippy --manifest-path "$REI_MANIFEST" --offline --locked --all-targets --jobs "$REI_CARGO_JOBS" -- -D warnings
fi
if [[ "$REI_STAGE" == light ]]; then
  run_logged new_diagnostic_tests cargo test --manifest-path "$REI_MANIFEST" --offline --locked --test birth_age_certificate --jobs "$REI_CARGO_JOBS" -- --test-threads "$REI_TEST_THREADS"
fi
if [[ "$REI_STAGE" == light || "$REI_STAGE" == all ]]; then
  run_logged build_studies cargo build --manifest-path "$REI_MANIFEST" --offline --locked --release --example birth_age_study --example birth_age_source_study --jobs "$REI_CARGO_JOBS"
  mkdir -- "$REI_RUN_OUTPUT/age_study"
  run_logged scalar_study "$CARGO_TARGET_DIR/release/examples/birth_age_study" "$REI_RUN_OUTPUT/age_study"
  run_logged source_study "$CARGO_TARGET_DIR/release/examples/birth_age_source_study" "$REI_PACKAGE_ROOT/inputs/AP_FROZEN_SOURCE_INPUTS.csv" "$REI_RUN_OUTPUT/age_study"
  run_logged independent_age python3 "$REI_PACKAGE_ROOT/scripts/verify_age_certificate.py" "$REI_RUN_OUTPUT/age_study" "$REI_RUN_OUTPUT/independent_age" --include-source --include-edges --source-inputs "$REI_PACKAGE_ROOT/inputs/AP_FROZEN_SOURCE_INPUTS.csv"
  run_logged independent_native python3 "$REI_PACKAGE_ROOT/scripts/analyze_time_age.py" --br03-root "$REI_PACKAGE_ROOT/reused_br03" --extra-native "$REI_PACKAGE_ROOT/evidence/native" --output-dir "$REI_RUN_OUTPUT/native_analysis"
  run_logged python_tests python3 -m unittest discover -s "$REI_PACKAGE_ROOT/scripts" -p 'test_*.py'
fi
if [[ "$REI_STAGE" == native || "$REI_STAGE" == all ]]; then
  run_logged build_native cargo build --manifest-path "$REI_PACKAGE_ROOT/ap/Cargo.toml" --offline --locked --release --example ap_native_driver --jobs "$REI_CARGO_JOBS"
  if [[ $# -eq 0 ]]; then set -- ap_n16_r4 ap_n64_r4; fi
  run_logged selected_native python3 "$REI_PACKAGE_ROOT/scripts/run_cross_native.py" --binary "$CARGO_TARGET_DIR/release/examples/ap_native_driver" --output "$REI_RUN_OUTPUT/new_native" "$@"
fi
run_logged verify_after python3 "$REI_PACKAGE_ROOT/verify_manifest.py" --root "$REI_PACKAGE_ROOT"
python3 - "$REI_RUN_OUTPUT/RUN_COMPLETE.json" "$REI_STAGE" <<'PY'
import datetime,json,pathlib,sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({"status":"COMPLETED","stage":sys.argv[2],"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Read raw per-step logs. light reproduces diagnostic studies and analyses; test runs all224 Rust tests and strictClippy; native runs only the two selected existing-driver configurations."},indent=2)+'\n')
PY
printf 'COMPLETED stage=%s output=%s\n' "$REI_STAGE" "$REI_RUN_OUTPUT"
