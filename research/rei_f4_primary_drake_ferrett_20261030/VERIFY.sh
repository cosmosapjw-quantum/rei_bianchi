#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/check_manifest.py
python -m unittest discover -s tests -v
python code/primary_spin.py > /dev/null
python code/check_manifest.py
python - <<'PY'
import json,hashlib,pathlib
r=pathlib.Path('results');m=json.loads(pathlib.Path('MANIFEST.json').read_text())['files']
a=[p for p in m if p.startswith('results/') and p.endswith(('.csv','.json'))]
for name in a:
 assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()==m[name],name
print(f'DETERMINISTIC_SCIENCE_REGEN={len(a)}/{len(a)}_PASS')
PY
