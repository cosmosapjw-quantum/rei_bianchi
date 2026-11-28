#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p private_native
python - <<'PY'
import zipfile,hashlib
z='source_r38/source_original/084307_1_supplements.zip'
assert hashlib.sha256(open(z,'rb').read()).hexdigest()=='a781d3b6f7d3cdffc210f2e8abd436e7378eb3716af80eb96b102a542eaba304'
with zipfile.ZipFile(z) as f:f.extractall('private_native')
assert hashlib.sha256(open('private_native/h3plus.f','rb').read()).hexdigest()=='8dbf8b7e3852d02504ba92317f79593051d689f1357263ac0891a3a24084ed8c'
PY
gfortran -std=legacy -O2 -fPIC -ffixed-line-length-none -shared private_native/h3plus.f -llapack -lblas -o private_native/libh3plus.so 2> replay_build_stderr.log
python generate.py --native-f private_native/h3plus.f --lib private_native/libh3plus.so --r38-master source_r38/WU_R38_VELILLA_BO_R37_RECONCILIATION_20261031_SOURCE.zip --out replay_results > replay_stdout.json
python -m unittest test_science -q
python -O -m unittest test_science -q
python - <<'PY'
from pathlib import Path
import hashlib
for file in Path('results').glob('*.csv'):
 old=hashlib.sha256(file.read_bytes()).hexdigest()
 new=hashlib.sha256((Path('replay_results')/file.name).read_bytes()).hexdigest()
 assert old==new,(file.name,old,new)
print('replayed CSV files exact:',len(list(Path('results').glob('*.csv'))))
PY
