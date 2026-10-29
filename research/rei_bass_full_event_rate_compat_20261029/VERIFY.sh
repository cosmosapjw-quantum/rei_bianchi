#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -B -m unittest discover -s tests -v
python3 -B code/run_once.py
g++ -std=c++20 -O2 -Wall -Wextra -Werror code/reference.cpp -o /tmp/rei_bass_event_ref
/tmp/rei_bass_event_ref results/RATES_11.tsv > results/CPP_STDOUT.txt
python3 -B code/verify_cross.py
printf 'PASS_SCOPED; 0 new IVPs; no physical tau claim\n'
