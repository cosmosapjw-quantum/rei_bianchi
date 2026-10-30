#!/bin/sh
set -eu
cd "$(dirname "$0")"
python code/check_manifest.py
python -m unittest discover -s tests -v
python - <<'PY'
import hashlib,pathlib,subprocess,sys
p=pathlib.Path('results');names=['EMISSIONS_193.csv','FIRST_FLIGHT_KERNEL.csv','JOINT_OUTCOMES_4825.csv','ABSORPTION_ARRIVALS_192.csv','RESULT.json']
old={x:hashlib.sha256((p/x).read_bytes()).hexdigest() for x in names}
subprocess.run([sys.executable,'code/combine_chunks.py'],check=True,capture_output=True,text=True)
for x in names:
 assert hashlib.sha256((p/x).read_bytes()).hexdigest()==old[x],f'REPLAY_DIFFERENCE:{x}'
print('REGENERATED_OUTPUTS_EXACT_5/5_PASS')
PY
python -m compileall -q code tests
