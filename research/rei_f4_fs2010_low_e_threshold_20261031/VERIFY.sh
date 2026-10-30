#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -v
python code/verify_outputs.py
python - <<'PY'
import sys
sys.path.insert(0,'code')
import thresholds
thresholds.check_sources()
print('SOURCE_LOCK_PASS',4)
PY
