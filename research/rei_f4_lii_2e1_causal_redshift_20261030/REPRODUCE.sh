#!/bin/sh
set -eu
cd "$(dirname "$0")"
for pair in '0 32' '32 64' '64 96' '96 128' '128 160' '160 193'; do
  set -- $pair
  python code/chunk_run.py --start "$1" --stop "$2" --order 16 --substeps 4
done
python code/combine_chunks.py
python code/convergence.py
python code/plot_science.py
