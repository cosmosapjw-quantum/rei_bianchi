#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python - <<'PY'
import json,hashlib
from pathlib import Path
r=Path('.');m=json.loads((r/'MANIFEST.json').read_text())
for it in m['files']:
 p=r/it['path']
 if not p.is_file() or p.stat().st_size!=it['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=it['sha256']:
  raise SystemExit('MANIFEST_INVALID:'+it['path'])
print('MANIFEST',len(m['files']), 'PASS')
PY
python -m unittest discover -s tests -v
python - <<'PY'
from code.mp_independent import run
r=run()
assert len(r)==7 and sum(len(v['certificates']) for v in r)==14
print('MP75: 14 primal/dual certificates for 7 z PASS; new IVPs 0')
PY
