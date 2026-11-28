#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 src/build_reconciliation.py --root .
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
