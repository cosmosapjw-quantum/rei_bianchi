#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 src/run_duhamel_study.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 src/make_duhamel_figure.py
python3 - <<'PY'
import json
from pathlib import Path
p=Path('results/duhamel_diagnostics.json')
r=json.loads(p.read_text())
assert abs(r['exact_reference']['survived']-0.004727055831538651)<1e-11
assert r['original_native_diagnostic']['0']['native_constant_depth_fit_8to16'] != r['original_native_diagnostic']['0']['native_constant_depth_fit_16to32']
assert all(x['cut_relative_survival_error'] < x['undivided_relative_survival_error'] for x in r['fixed_work_comparison'])
print('RESTORE_SCIENCE_CONTROLS=PASS')
PY
