#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -v
python - <<'PY'
import hashlib, pathlib, subprocess, sys
p=pathlib.Path('results')
names=['FERRETT_DIRECT_R31_R32_BASS_EVENT_1158.csv','FERRETT_DIRECT_R31_R32_EPOCH_193.csv','FERRETT_TABLE_II_III_DIRECT_7.csv','RESULT.json']
h=lambda f:hashlib.sha256((p/f).read_bytes()).hexdigest()
before={s:h(s) for s in names}
r=subprocess.run([sys.executable,'code/direct_r31.py'],stdout=subprocess.DEVNULL)
assert r.returncode==0
assert before=={s:h(s) for s in names},'DETERMINISTIC_REPRODUCTION_BYTE_MISMATCH'
print('4/4 source-driven CSV/JSON output replay byte identity PASS')
PY
