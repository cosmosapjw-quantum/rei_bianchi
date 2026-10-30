#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${OPENBLAS_NUM_THREADS:=1}"
export OPENBLAS_NUM_THREADS
python code/verify_manifest.py
python -m unittest discover -s tests -p 'test_*.py' -q
python code/bridge.py > /tmp/rei_f4_193_replay.json
python code/plot_science.py > /tmp/rei_f4_193_plot_replay.log
python - <<'PY'
from pathlib import Path
import hashlib,json
root=Path('results'); o=json.loads(Path('OUTPUT_SHA256.json').read_text())
for n,h in o.items():
    assert hashlib.sha256((root/n).read_bytes()).hexdigest()==h,n
print('PASS deterministic replay',len(o),'/',len(o),'CSV/NPZ/JSON/PNG outputs; no IVP')
PY
