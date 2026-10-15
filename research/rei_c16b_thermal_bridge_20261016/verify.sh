#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p evidence figures
python3 - <<'PY'
from pathlib import Path
import hashlib
p=Path('source_aware.py')
a=p.read_bytes()
sha=hashlib.sha256(a).hexdigest()
blob=hashlib.sha1(b'blob '+str(len(a)).encode()+b'\0'+a).hexdigest()
assert sha=='f4c5ff49f9e09a2123f3830160e857beb9c224deafc9ff379d6199829013bbf4'
assert blob=='db822a53da3ccdca7cf96628e9ef3bbcec83db5a'
assert a==Path('upstream/source_aware_PR154_immutable.py').read_bytes()
print('PR154_ORIGINAL_SOURCE_SHA_AND_GIT_BLOB_OK')
PY
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
python3 -m unittest discover -s tests -v > evidence/new_tests.log 2>&1
grep -F 'Ran 29 tests' evidence/new_tests.log
grep -Fx 'OK' evidence/new_tests.log
PYTHONPATH="$PWD" python3 upstream/test_source_aware_PR154_immutable.py > evidence/original_tests.log 2>&1
grep -F 'Ran 22 tests' evidence/original_tests.log
grep -Fx 'OK' evidence/original_tests.log
python3 run_study.py > evidence/run_study.log
python3 make_plot.py > evidence/plot_stdout.log
python3 - <<'PY'
from pathlib import Path
import json
j=json.loads(Path('evidence/study_results.json').read_text())
assert 1.95<j['last_five_measured_order']<2.05
assert max(r['energy_residual_abs_eV_per_h'] for r in j['refinement'])<1e-10
print('STUDY_GATE_PASS',j['last_five_measured_order'])
PY
echo 'VERIFICATION_FINISHED_51_PASS'
