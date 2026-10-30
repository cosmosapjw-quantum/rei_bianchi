#!/bin/sh
set -eu
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -v
python - <<'PY'
import hashlib
from pathlib import Path
import subprocess,sys
r=Path('results')
names=['PAIR_EPOCH_193.csv','PAIR_OUTCOMES_4825.csv','RESULTS.json']
before={x:hashlib.sha256((r/x).read_bytes()).hexdigest() for x in names}
proc=subprocess.run([sys.executable,'code/pair_joint.py'],check=True,capture_output=True,text=True)
for x in names:
  after=hashlib.sha256((r/x).read_bytes()).hexdigest()
  assert after==before[x],f'DATA_REGEN_FAIL:{x}'
print('DATA_REGEN_3/3_PASS')
PY
