#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_package.py manifest
python code/build_joint.py >/dev/null
python code/plot_science.py
python code/build_stages.py
python -m unittest discover -s tests -v
python code/verify_package.py outputs
printf '%s\n' 'CLEAN_REPLAY=PASS; SCIENCE=CONDITIONAL; DAG=33/88,28/88,4/7; NO_IVP=TRUE; PRODUCTION=HOLD; NATIVE_REI17=NOT_RUN'
