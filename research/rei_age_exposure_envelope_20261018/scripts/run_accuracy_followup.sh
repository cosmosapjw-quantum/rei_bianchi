#!/usr/bin/env bash
# One named opt-in accuracy follow-up; never an implicit multi-case campaign.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
REPO=${1:?usage: run_accuracy_followup.sh REPO NEW_SCRATCH mode}
SCRATCH=${2:?new follow-up scratch required}
MODE=${3:?mode: age64-block-max, age32-block-max-diagnostics, or time8-subnormal-count}
case "$MODE" in
    age64-block-max) CASE=age64; CAP=1800; PREPARE_FLAGS=(); RUN_FLAGS=(--error-norm block-max --rpc-mode binary64) ;;
    age32-block-max-diagnostics) CASE=age32; CAP=1800; PREPARE_FLAGS=(); RUN_FLAGS=(--error-norm block-max --rpc-mode binary64 --reference-diagnostics) ;;
    time8-subnormal-count) CASE=time8; CAP=120; PREPARE_FLAGS=(--moment-diagnostics --moment-rounding subnormal-count); RUN_FLAGS=() ;;
    *) echo 'UNKNOWN_FOLLOWUP_MODE' >&2; exit 2 ;;
esac
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$SCRATCH"
PREPARED="$SCRATCH/native"
PREPARATION_ROUTE=fresh_prepare
KNOWN_NCP_BASE=/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/run/native
if [[ "$MODE" == age32-block-max-diagnostics ]]; then
    if [[ -n "${REI_PREPARED_BASE:-}" ]]; then
        PREPARED="$REI_PREPARED_BASE"
        [[ -f "$PREPARED/PREPARED_IDENTITY.json" && -f "$PREPARED/BUILD_RECEIPT.json" ]] || { echo 'REQUESTED_PREPARED_BASE_MISSING' >&2; exit 2; }
        PREPARATION_ROUTE=explicit_prepared_base
    elif [[ -f "$KNOWN_NCP_BASE/PREPARED_IDENTITY.json" && -f "$KNOWN_NCP_BASE/BUILD_RECEIPT.json" ]]; then
        PREPARED="$KNOWN_NCP_BASE"
        PREPARATION_ROUTE=known_completed_age64_base
    fi
fi
if [[ "$PREPARATION_ROUTE" != fresh_prepare ]]; then
    BASE_CANDIDATE="$PREPARED"
    if ! python3 "$ROOT/src/reference_base.py" --check-complete "$PREPARED"; then
        PREPARED="$SCRATCH/native"
        python3 "$ROOT/src/prepare_native.py" --repo "$REPO" --fetch-missing --dest "$PREPARED"
        if python3 "$ROOT/src/reference_base.py" --base "$BASE_CANDIDATE" --prepared "$PREPARED" --scratch "$SCRATCH"; then
            PREPARATION_ROUTE=compact_base_exact_reconstruction
            RUN_FLAGS+=(--binary "$SCRATCH/positive_native.bin")
        else
            PREPARATION_ROUTE=compact_base_fresh_build_fallback
            python3 "$ROOT/src/build_native.py" --prepared "$PREPARED"
        fi
    elif [[ ! -f "$PREPARED/rust/rei_microphysics/target/release/examples/positive_native" ]]; then
        if python3 "$ROOT/src/reference_base.py" --base "$BASE_CANDIDATE" --prepared "$PREPARED" --scratch "$SCRATCH"; then
            PREPARATION_ROUTE=compact_binary_exact_binding
            RUN_FLAGS+=(--binary "$SCRATCH/positive_native.bin")
        else
            echo 'PREPARED_BASE_BINARY_UNAVAILABLE_OR_MISMATCHED' >&2
            exit 2
        fi
    fi
fi
# The bundled frozen manifest makes git-object restoration independent of ZIPs.
if [[ "$PREPARATION_ROUTE" == fresh_prepare ]]; then
    python3 "$ROOT/src/prepare_native.py" --repo "$REPO" --fetch-missing --dest "$PREPARED" "${PREPARE_FLAGS[@]}"
    python3 "$ROOT/src/build_native.py" --prepared "$PREPARED"
fi
python3 - "$PREPARED" "$KNOWN_NCP_BASE" "$SCRATCH" "$PREPARATION_ROUTE" <<'PY'
import json,sys
from pathlib import Path
from run_refinement import read_json,save
prepared,known,scratch=map(Path,sys.argv[1:4])
build=read_json(prepared/'BUILD_RECEIPT.json')
expected=read_json(known/'BUILD_RECEIPT.json').get('binary_sha256') if (known/'BUILD_RECEIPT.json').is_file() else None
save(scratch/'PREPARATION_COMPARISON.json',dict(route=sys.argv[4],prepared=str(prepared),
    binary_sha256=build.get('binary_sha256'),completed_age64_binary_sha256=expected,
    binary_comparison='MATCH' if expected and expected==build.get('binary_sha256') else 'MISMATCH' if expected else 'MISSING_COMPLETED_BINARY_IDENTITY'))
PY
set +e
python3 "$ROOT/src/run_refinement.py" --prepared "$PREPARED" --out "$SCRATCH/results" --cases "$CASE" --case-wall-s "$CAP" --total-wall-s "$CAP" "${RUN_FLAGS[@]}"
RESULT=$?
set -e
python3 - "$SCRATCH" "$MODE" "$RESULT" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);diagnostics=[];corrections=[]
for path in sorted((root/'results').rglob('stderr.log')):
    for line in path.read_text().splitlines():
        for prefix,items in [('REI_MOMENT_DIAGNOSTIC ',diagnostics),('REI_SUBNORMAL_COUNT_CORRECTION ',corrections)]:
            if line.startswith(prefix):items.append(dict(log=str(path.relative_to(root)),value=json.loads(line[len(prefix):])))
(root/'FOLLOWUP_RESULT.json').write_text(json.dumps(dict(mode=sys.argv[2],process_exit=int(sys.argv[3]),
    first_corrections=corrections,first_failures=diagnostics,statistics_scope='FIRST_EVENTS_ONLY',
    scientific_admission='NOT_ISSUED'),indent=2)+'\n')
PY
exit "$RESULT"
