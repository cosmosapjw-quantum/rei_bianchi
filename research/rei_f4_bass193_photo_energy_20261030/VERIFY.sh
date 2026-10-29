#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/verify_manifest.py
python -m unittest discover -s tests -v
printf 'NO_NEW_IVPS; ORIGINAL_DAG=33/88,28/88; F4_FAST=4/7; PRODUCTION_HOLD\n'
