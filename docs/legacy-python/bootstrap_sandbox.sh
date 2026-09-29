#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
PYTHON=${PYTHON:-python3}
if [[ ! -d .venv ]]; then "$PYTHON" -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e .
python scripts/verify_repo.py
printf '
Sandbox ready. Current handoff:
%s
' "$ROOT/handoff/CURRENT_HANDOFF_PROMPT.md"
