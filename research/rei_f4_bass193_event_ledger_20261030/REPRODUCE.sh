#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash VERIFY.sh
python code/build_atlas.py > results/RESULT_STDOUT.txt
bash VERIFY.sh
