#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/src" OPENBLAS_NUM_THREADS=1
python3 src/check_manifest.py
python3 -m pytest -q tests/test_age_transport.py
python3 src/run_study.py
python3 src/make_figures.py
python3 - <<'PY'
import json
from pathlib import Path
r=json.loads(Path('evidence/SOURCE_AGE_NUMERICS.json').read_text())
assert len(r['signed_convergence'])==3 and len(r['adaptive_age'])==3
assert all(1.7<s['tail_orders'][-1]<2.25 for s in r['signed_convergence'])
assert all(a['relative_HeII_difference_from_DOP853']<1e-4 for a in r['adaptive_age'])
assert len(r['multicrossing']['event_roots_x'])==5
assert all(abs(a['energy_residual'])<1e-9 for a in r['adaptive_age'])
print('SOURCE_AGE_SCIENCE_CHECK_PASS')
PY
