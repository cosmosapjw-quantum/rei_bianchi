#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -v
python code/positive_cone.py > /dev/null
python - <<'EOF'
import hashlib,json,pathlib
p=pathlib.Path('results')
m=json.loads(pathlib.Path('MANIFEST.json').read_text())['files']
files=['results/CONE_EPOCH_193.csv','results/CONE_CHANNEL_4825.csv','results/CONE_GENERATORS_7720.csv','results/RESULTS.json']
for f in files:
 observed=hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
 if observed!=m[f]: raise SystemExit('REGENERATED_SHA_FAIL:'+f)
print('REGENERATED_SCIENCE=4/4_SHA_PASS')
EOF
