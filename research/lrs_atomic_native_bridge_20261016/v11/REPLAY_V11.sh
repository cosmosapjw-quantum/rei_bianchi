#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
cd "$ROOT"
python - <<'PY'
from pathlib import Path
import json,hashlib
r=Path('research/lrs_atomic_native_bridge_20261016/v11')
m=json.loads((r/'V11_SOURCE_MANIFEST.json').read_text())
for rel,expected in m['files'].items():
    got=hashlib.sha256(Path(rel).read_bytes()).hexdigest()
    if got!=expected: raise SystemExit('SOURCE_HASH_FAIL:'+rel)
print('MANIFEST_OK',len(m['files']))
PY
python -m pytest -q "$HERE/tests/test_ci_thermal_clock.py"
python "$HERE/regenerate_case_views.py"
python - <<'PY'
from pathlib import Path
import hashlib
p=Path('research/lrs_atomic_native_bridge_20261016/v11/evidence/C8_MATRIX_144.json')
print('C8_AGGREGATE_BEFORE_SHA256',hashlib.sha256(p.read_bytes()).hexdigest())
PY
python "$HERE/merge_study.py"
python - <<'PY'
from pathlib import Path
import hashlib,json,math
p=Path('research/lrs_atomic_native_bridge_20261016/v11/evidence/C8_MATRIX_144.json')
s=json.loads(Path('research/lrs_atomic_native_bridge_20261016/v11/evidence/C8_SUMMARY.json').read_text())
a=json.loads(p.read_text()); assert len(a['rows'])==144
assert len(set((r['case'],r['mode'],r['steps']) for r in a['rows']))==144
assert max(r['energy_ledger_abs_eV_H'] for r in a['rows'])<5e-12
print('C8_144_ROW_STORED_EVIDENCE_VERIFIED',hashlib.sha256(p.read_bytes()).hexdigest())
print('SCOPED_VALIDATION_COMPLETE, native_Rust=NOT_RUN')
PY
