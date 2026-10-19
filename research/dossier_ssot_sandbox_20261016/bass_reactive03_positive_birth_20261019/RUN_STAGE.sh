#!/usr/bin/env bash
# Execute only from a restored package. Source and archived evidence stay immutable.
set -Eeuo pipefail

REI_PACKAGE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REI_STAGE="${1:-all}"
if [[ $# -gt 0 ]]; then shift; fi
case "$REI_STAGE" in
    verify|test|frozen|native|all) ;;
    *) printf 'Usage: %s {verify|test|frozen|native|all} [native_case ...]\n' "$0" >&2; exit 2 ;;
esac

# REI_RUST_PREFIX can point at a preinstalled standalone Rust 1.94.1 prefix.
# The runner never installs a toolchain or resolves crates from the network.
if [[ -n "${REI_RUST_PREFIX:-}" ]]; then
    export PATH="$REI_RUST_PREFIX/bin:$PATH"
    export LD_LIBRARY_PATH="$REI_RUST_PREFIX/lib:${LD_LIBRARY_PATH:-}"
fi
if [[ -n "${REI_RUN_OUTPUT:-}" ]]; then
    if [[ -e "$REI_RUN_OUTPUT" ]]; then
        printf 'OUTPUT_ALREADY_EXISTS: %s\nChoose a new output directory.\n' "$REI_RUN_OUTPUT" >&2
        exit 2
    fi
    mkdir -p -- "$REI_RUN_OUTPUT"
else
    REI_RUN_OUTPUT="$(mktemp -d "${TMPDIR:-/tmp}/rei_positive_birth.XXXXXX")"
fi
REI_RUN_OUTPUT="$(cd -- "$REI_RUN_OUTPUT" && pwd -P)"
mkdir -- "$REI_RUN_OUTPUT/logs"
REI_CARGO_TARGET="${REI_CARGO_TARGET:-$REI_RUN_OUTPUT/target}"
export CARGO_TARGET_DIR="$REI_CARGO_TARGET"
REI_CARGO_JOBS="${REI_CARGO_JOBS:-2}"
REI_TEST_THREADS="${REI_TEST_THREADS:-2}"
REI_NATIVE_WORKERS="${REI_NATIVE_WORKERS:-1}"
REI_AP_MANIFEST="$REI_PACKAGE_ROOT/ap/Cargo.toml"
REI_CURRENT_STEP="bootstrap"

record_failure() {
    local exit_code=$?
    trap - ERR
    python3 - "$REI_RUN_OUTPUT/RUN_FAILURE.json" "$REI_STAGE" "$REI_CURRENT_STEP" "$exit_code" <<'PY' || true
import datetime, json, pathlib, sys
path,stage,step,code=sys.argv[1:]
pathlib.Path(path).write_text(json.dumps({
    "status":"REPRODUCTION_STEP_FAILED", "stage":stage, "step":step,
    "exit_code":int(code), "utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "interpretation":"Inspect this step's raw log. Compiler, artifact, work-budget and physics failures are different categories."
},indent=2)+"\n")
PY
    printf 'FAILED step=%s exit=%s. Raw evidence: %s\n' "$REI_CURRENT_STEP" "$exit_code" "$REI_RUN_OUTPUT" >&2
    exit "$exit_code"
}
trap record_failure ERR

run_logged() {
    local name=$1
    shift
    REI_CURRENT_STEP="$name"
    printf 'Running %s\n' "$name"
    python3 - "$REI_RUN_OUTPUT/logs/$name.command.json" "$@" <<'PY'
import json, pathlib, sys
pathlib.Path(sys.argv[1]).write_text(json.dumps({"argv":sys.argv[2:]},indent=2)+"\n")
PY
    "$@" > "$REI_RUN_OUTPUT/logs/$name.log" 2>&1
}

# An actual Python invocation runs before any runtime availability claim.
run_logged python_probe python3 -c 'import sys; print("PYTHON_PASS", sys.version)'
run_logged verify_before python3 "$REI_PACKAGE_ROOT/verify_manifest.py" --root "$REI_PACKAGE_ROOT"

if [[ "$REI_STAGE" != verify ]]; then
    run_logged rustc_version rustc --version --verbose
    run_logged cargo_version cargo --version
    run_logged version_gate python3 - "$REI_RUN_OUTPUT/logs/rustc_version.log" "$REI_RUN_OUTPUT/logs/cargo_version.log" <<'PY'
import pathlib,sys
for file,tool in zip(sys.argv[1:],["rustc","cargo"]):
    first=pathlib.Path(file).read_text().splitlines()[0].split()
    if len(first)<2 or first[0]!=tool or first[1]!="1.94.1":
        raise SystemExit(f"TOOLCHAIN_VERSION_MISMATCH: {tool} must be 1.94.1; got {first}")
print("TOOLCHAIN_VERSION_MATCH Rust and Cargo 1.94.1")
PY
fi

if [[ "$REI_STAGE" == test || "$REI_STAGE" == all ]]; then
    run_logged all_rust_tests cargo test --manifest-path "$REI_AP_MANIFEST" --offline --locked --all-targets --jobs "$REI_CARGO_JOBS" -- --test-threads "$REI_TEST_THREADS"
    run_logged strict_clippy cargo clippy --manifest-path "$REI_AP_MANIFEST" --offline --locked --all-targets --jobs "$REI_CARGO_JOBS" -- -D warnings
fi

if [[ "$REI_STAGE" == frozen || "$REI_STAGE" == native || "$REI_STAGE" == all ]]; then
    run_logged release_examples cargo build --manifest-path "$REI_AP_MANIFEST" --offline --locked --release --examples --jobs "$REI_CARGO_JOBS"
fi

if [[ "$REI_STAGE" == frozen || "$REI_STAGE" == all ]]; then
    mkdir -- "$REI_RUN_OUTPUT/frozen"
    run_logged frozen_oracle "$CARGO_TARGET_DIR/release/examples/ap_frozen_oracle" "$REI_RUN_OUTPUT/frozen"
fi

if [[ "$REI_STAGE" == native || "$REI_STAGE" == all ]]; then
    if [[ $# -eq 0 ]]; then set -- ap_n32_r2; fi
    run_logged selected_native python3 "$REI_PACKAGE_ROOT/scripts/run_native_matrix.py" "$REI_RUN_OUTPUT/native" "$@" --workers "$REI_NATIVE_WORKERS" --binary "$CARGO_TARGET_DIR/release/examples/ap_native_driver"
fi

# Verify that tests and reproduction did not alter any archived payload.
run_logged verify_after python3 "$REI_PACKAGE_ROOT/verify_manifest.py" --root "$REI_PACKAGE_ROOT"
REI_CURRENT_STEP=completion_receipt
python3 - "$REI_RUN_OUTPUT" "$REI_PACKAGE_ROOT" "$REI_STAGE" <<'PY'
import datetime,hashlib,json,pathlib,sys
out,root=map(pathlib.Path,sys.argv[1:3]);stage=sys.argv[3]
payload={}
for base in [out/"logs",out/"frozen",out/"native"]:
    if base.exists():
        for p in sorted(base.rglob("*")):
            if p.is_file():payload[str(p.relative_to(out))]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/"RUN_COMPLETION.json").write_text(json.dumps({
    "status":"REQUESTED_REPRODUCTION_STAGES_COMPLETED", "stage":stage,
    "package_root":str(root),"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "evidence_sha256":payload,
    "scope":"Reproduction stages only. An expected Cx(WorkLimit) record remains a work-budget outcome, not an admitted native solution."
},indent=2)+"\n")
print("Evidence directory:",out)
PY
