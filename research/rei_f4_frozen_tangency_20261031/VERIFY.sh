#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_package.py manifest
python code/build_physical_source.py >/dev/null
python -m unittest discover -s tests -p 'test_*.py' -v
python code/verify_package.py outputs
printf 'CLEAN_RESTORE=PASS; DAG=33/88,28/88,4/7; NEW_IVP=0; DISTINCT_R6_C9=NOT_RUN\n'
