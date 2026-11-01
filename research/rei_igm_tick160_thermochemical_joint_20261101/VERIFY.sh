#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SOURCE="${REI_INPUT_ARCHIVE:-inputs/REI_PR320_ORIGINAL_TICK160_PHYSICS_20261101.zip}"
python - <<'PY'
import hashlib,json,pathlib
p=pathlib.Path('results/OUTPUT_SHA256_MANIFEST.json');j=json.loads(p.read_text())
for name,meta in j['outputs'].items():
 x=pathlib.Path('results')/name
 assert x.stat().st_size==meta['size'] and hashlib.sha256(x.read_bytes()).hexdigest()==meta['sha256'],name
print('EXISTING SCIENCE SHA/SIZE: 2/2 PASS')
PY
mkdir -p .verify_recompute
python code/thermochemical_closure.py --input "$SOURCE" --output .verify_recompute
REI_INPUT_ARCHIVE="$SOURCE" python -m unittest discover -s tests -v
python code/independent_audit.py --source-archive "$SOURCE" --candidate .verify_recompute/ORIGINAL_TICK160_46080_THERMOCHEMICAL_CLOSURE.csv.gz --output .verify_recompute/INDEPENDENT_AUDIT.json
python - <<'PY'
from pathlib import Path
import hashlib
for f in ('ORIGINAL_TICK160_46080_THERMOCHEMICAL_CLOSURE.csv.gz','SCIENTIFIC_SUMMARY.json'):
  a=Path('results')/f;b=Path('.verify_recompute')/f
  assert a.read_bytes()==b.read_bytes(),f
print('BYTE-EXACT SCIENCE RECOMPUTE: 2/2 PASS')
PY
