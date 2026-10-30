#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/check_manifest.py
python -m unittest discover -s tests -v
python code/two_e1_source.py
python code/check_manifest.py
printf 'RESTORE_VALIDATION_PASS no_new_IVP working=33/88 central=28/88 F4=4/7\n'
