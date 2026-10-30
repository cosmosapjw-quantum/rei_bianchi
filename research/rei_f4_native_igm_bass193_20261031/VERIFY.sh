#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_package.py manifest
python code/build_cases.py
python code/plot_science.py
python code/summarize_science.py >/dev/null
python -W error -m unittest discover -s tests -v
python code/verify_package.py output
printf 'CLEAN_LOCAL_PYTHON=PASS; NATIVE_RUST=REFER_TO_EXACT_GITHUB_CI_HEAD; REI_FULL17=HOLD\n'
