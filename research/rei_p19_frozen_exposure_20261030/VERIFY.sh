#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m unittest discover -s tests -v
python code/exposure.py > /dev/null
python code/reference_mp.py > /dev/null
python code/plot_exposure.py > /dev/null
echo 'REI_P19_FROZEN_EXPOSURE_VERIFIED 12 PYTHON, 168 MP90, 0 IVP'
