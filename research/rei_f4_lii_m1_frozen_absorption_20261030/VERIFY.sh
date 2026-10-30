#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
python code/verify_manifest.py
python code/m1_absorption.py >/dev/null
python -m unittest discover -s tests -v
python - <<'PY'
import json,hashlib,pathlib
p=pathlib.Path('results'); j=json.loads(pathlib.Path('MANIFEST.json').read_text())
for f in ('results/M1_ABSORPTION_EPOCH_193.csv','results/M1_ABSORPTION_SPECIES_4053.csv','results/RESULTS.json'):
 assert hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()==j['files'][f],f
print('REGENERATED_PHYSICS_3/3_SHA_PASS')
PY
