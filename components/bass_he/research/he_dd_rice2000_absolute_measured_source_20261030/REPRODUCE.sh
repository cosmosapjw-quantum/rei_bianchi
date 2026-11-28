#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 src/build_rice.py --root .
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
