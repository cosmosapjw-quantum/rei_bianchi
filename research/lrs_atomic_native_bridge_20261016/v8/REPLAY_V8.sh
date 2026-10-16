#!/usr/bin/env bash
set -euo pipefail
# Run from a complete rei_bianchi Git checkout or self-contained V8 ZIP extraction.
cd "$(dirname "${BASH_SOURCE[0]}")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 -m pytest -q test_rrdr_sourcefree_v8.py
python3 run_refinement_v8.py
python3 run_stiff_v8.py
python3 - <<'PY'
import json
from pathlib import Path
r=Path('evidence')
d=json.loads((r/'C8_REFINEMENT.json').read_text())
s=json.loads((r/'C8_STIFF.json').read_text())
assert len(d['cases'])==5 and sum(len(z['rows']) for z in d['cases'])==25
assert len(s['rows'])==8
print('V8_REPLAY_COMPLETED: 21 tests, 25 direct Radau rows, 8 stiff rows')
PY
