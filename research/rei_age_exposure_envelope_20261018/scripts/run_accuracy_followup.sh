#!/usr/bin/env bash
# One named opt-in accuracy follow-up; never an implicit multi-case campaign.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
REPO=${1:?usage: run_accuracy_followup.sh REPO NEW_SCRATCH mode}
SCRATCH=${2:?new follow-up scratch required}
MODE=${3:?mode: age64-block-max or time8-subnormal-count}
case "$MODE" in
    age64-block-max) CASE=age64; CAP=1800; PREPARE_FLAGS=(); RUN_FLAGS=(--error-norm block-max --rpc-mode binary64) ;;
    time8-subnormal-count) CASE=time8; CAP=120; PREPARE_FLAGS=(--moment-diagnostics --moment-rounding subnormal-count); RUN_FLAGS=() ;;
    *) echo 'UNKNOWN_FOLLOWUP_MODE' >&2; exit 2 ;;
esac
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$SCRATCH"
# The bundled frozen manifest makes git-object restoration independent of ZIPs.
python3 "$ROOT/src/prepare_native.py" --repo "$REPO" --fetch-missing --dest "$SCRATCH/native" "${PREPARE_FLAGS[@]}"
python3 "$ROOT/src/build_native.py" --prepared "$SCRATCH/native"
set +e
python3 "$ROOT/src/run_refinement.py" --prepared "$SCRATCH/native" --out "$SCRATCH/results" --cases "$CASE" --case-wall-s "$CAP" --total-wall-s "$CAP" "${RUN_FLAGS[@]}"
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
