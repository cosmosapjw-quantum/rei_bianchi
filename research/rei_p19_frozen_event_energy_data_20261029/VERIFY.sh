#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python code/physical_data.py >/dev/null
python -m unittest discover -s tests -v
PYTHONPATH=code python code/independent_reference.py
python code/plot_physical.py
