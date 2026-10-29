#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python - <<'PY_MANIFEST'
from pathlib import Path
import json,hashlib
base=Path.cwd();mani=json.loads((base/'MANIFEST.json').read_text())
for entry in mani['files']:
    f=base/entry['path']
    if not f.exists() or f.stat().st_size!=entry['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=entry['sha256']:
        raise SystemExit('MANIFEST_SOURCE_MISMATCH:'+entry['path'])
print('MANIFEST PASS',len(mani['files']))
PY_MANIFEST
python -m unittest discover -s tests -v
python - <<'PY'
from code.highprecision_check import validate
from code.spectral_witness import seven_saved_witnesses
x=validate();y=seven_saved_witnesses()
assert len(x)==len(y['cases'])==7
assert all(v['support_size']==6 and v['max_rel_error']<1e-10 for v in y['cases'])
print('RESTORE: 7 positive spectra, Li primal/dual 75-digit, PASS_SCOPED; new IVP 0')
PY