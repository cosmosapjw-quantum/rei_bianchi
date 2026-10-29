#!/usr/bin/env bash
# Clean-source standalone verification. No IVP, no network, no state mutation outside this unpacked unit.
set -euo pipefail
cd "$(dirname "$0")"
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
python3 -B code/make_reference.py
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
"${CXX:-g++}" -std=c++20 -O2 -Wall -Wextra -Werror code/reference.cpp -o "$scratch/reference"
"$scratch/reference" results/CPP_INPUT.tsv
