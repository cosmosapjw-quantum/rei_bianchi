#!/usr/bin/env bash
# Opt-in local task copy; original failure remains failure.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
REPO=${1:?usage: run_moment_diagnostic.sh REPO NEW_SCRATCH [time8]}
SCRATCH=${2:?new diagnostic scratch required}
CASE=${3:-time8}
[[ "$CASE" == time8 ]] || { echo 'ONLY_TIME8_DIAGNOSTIC_AUTHORIZED' >&2; exit 2; }
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$SCRATCH"
bash "$ROOT/scripts/fetch_donor.sh"
python3 "$ROOT/src/prepare_native.py" --repo "$REPO" --archive "$ROOT/donors/REI_POSITIVE_NATIVE_C9_20261016_v1.zip" --dest "$SCRATCH/native" --moment-diagnostics
python3 "$ROOT/src/build_native.py" --prepared "$SCRATCH/native" --wall-s 60
set +e
python3 "$ROOT/src/run_refinement.py" --prepared "$SCRATCH/native" --out "$SCRATCH/results" --cases time8 --case-wall-s 120 --total-wall-s 120
RESULT=$?
set -e
python3 - "$SCRATCH" "$RESULT" <<'PY'
import json,sys
from pathlib import Path
root=Path(sys.argv[1]);records=[]
for path in sorted((root/'results').rglob('stderr.log')):
    for line in path.read_text().splitlines():
        if line.startswith('REI_MOMENT_DIAGNOSTIC '):
            records.append(dict(log=str(path.relative_to(root)),cell=json.loads(line.split(' ',1)[1])))
report=dict(schema='rei.moment_fit.failure_diagnostic.v1',original_process_exit=int(sys.argv[2]),
            diagnostic_status='AVAILABLE' if records else 'MISSING_DIAGNOSTIC',records=records,
            original_failure_preserved=True,scientific_admission='NOT_ISSUED')
(root/'MOMENT_DIAGNOSTIC_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
PY
exit "$RESULT"
