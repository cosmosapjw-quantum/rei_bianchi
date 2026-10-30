#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -v
python code/ferrett_window.py >/dev/null
python code/verify_manifest.py
printf '%s\n' 'FERRETT_SCOPED_SOURCE_RESTORE PASS'
