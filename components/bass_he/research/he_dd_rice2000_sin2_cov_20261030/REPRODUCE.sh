#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m compileall -q src tests
python3 -m unittest discover -s tests -v
python3 src/rice_covariance.py
python3 src/verify_source_identity.py
