#!/usr/bin/env bash
# Run on authorized NCP or another supported POSIX research host, never production.
set -euo pipefail
export PATH="$HOME/.cargo/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
RESEARCH="$(dirname "$HERE")"
OWNER_SHA=f7830e2f55e7a1938bc3c98f61b60651f8dae474
WORK="${HE28_WORK_ROOT:-$HOME/HE28_RUN_$(date -u +%Y%m%dT%H%M%SZ)}"
# Avoid overwriting a successful result, failed pilot or unrelated working tree.
if [[ -e "$WORK" ]]; then echo "HE28_FRESH_WORK_REQUIRED: $WORK" >&2; exit 10; fi
mkdir -p "$WORK/build" "$WORK/logs"
status=1
finish() {
  code=$?
  trap - EXIT
  printf '%s\n' "$code" > "$WORK/logs/EXIT_CODE.txt"
  tar -czf "$WORK/HE28_RUN_EVIDENCE.tar.gz" -C "$WORK" logs \
      $(test -d "$WORK/pilot" && printf 'pilot' || true) \
      $(test -d "$WORK/preflight" && printf 'preflight' || true)
  sha256sum "$WORK/HE28_RUN_EVIDENCE.tar.gz" > "$WORK/HE28_RUN_EVIDENCE.tar.gz.sha256"
  printf 'HE28_WORK_ROOT=%s\nEXIT=%s\n' "$WORK" "$code"
  exit "$code"
}
trap finish EXIT
command -v rustc >/dev/null || { echo HE28_NO_RUST >&2; exit 10; }
command -v python3 >/dev/null || exit 10
{ date -u +%FT%TZ; hostname; rustc -Vv; nproc; free -h; df -h "$WORK"; } > "$WORK/logs/ENVIRONMENT.txt"
OWNER="$WORK/owner"
# Read-only donor snapshot; no original user checkout reset/clean operations.
if [[ -n "${HE28_OWNER_REPO:-}" ]]; then
  git -C "$HE28_OWNER_REPO" cat-file -e "$OWNER_SHA^{commit}"
  git clone --no-hardlinks --no-checkout "$HE28_OWNER_REPO" "$OWNER" > "$WORK/logs/OWNER_CLONE.log" 2>&1
else
  git clone --filter=blob:none --no-checkout https://github.com/cosmosapjw-quantum/rei_bianchi.git \
      "$OWNER" > "$WORK/logs/OWNER_CLONE.log" 2>&1
fi
if ! git -C "$OWNER" cat-file -e "$OWNER_SHA^{commit}" 2>/dev/null; then
  git -C "$OWNER" fetch --depth=1 origin "$OWNER_SHA" >> "$WORK/logs/OWNER_CLONE.log" 2>&1
fi
# Include compile-time docs referenced by include_str!, rather than changing code.
git -C "$OWNER" sparse-checkout init --cone
git -C "$OWNER" sparse-checkout set rust/rei_microphysics \
    docs/fastest_track_chat/REI-AXBI-GOAL-20261014 research/axbi_goal_20261014/scenario
git -C "$OWNER" checkout --detach "$OWNER_SHA" >> "$WORK/logs/OWNER_CLONE.log" 2>&1
[[ "$(git -C "$OWNER" rev-parse HEAD)" == "$OWNER_SHA" ]]
[[ -z "$(git -C "$OWNER" status --porcelain)" ]]
if [[ -n "${HE28_PYTHON:-}" ]]; then PY="$HE28_PYTHON"; else
  python3 -m venv "$WORK/venv"
  PY="$WORK/venv/bin/python"
  "$PY" -m pip install -r "$HERE/requirements.txt" > "$WORK/logs/DEPENDENCIES.log" 2>&1
fi
"$PY" -m pip freeze > "$WORK/logs/PYTHON_ENV.txt"
PYTHONPATH="$HERE/src" "$PY" - "$HERE" <<'PY'
import json,sys
from pathlib import Path
from execution import verify_manifest
h=Path(sys.argv[1]);verify_manifest(json.loads((h/'provenance/PARENT_SHA256.json').read_text()),h.parents[1])
PY
LIB="$WORK/build/librei_microphysics.rlib"
BIN="$WORK/build/he28_owner_server"
rustc --edition=2021 --crate-name rei_microphysics --crate-type rlib -C opt-level=2 \
    "$OWNER/rust/rei_microphysics/src/lib.rs" -o "$LIB" > "$WORK/logs/BUILD_OWNER.log" 2>&1
rustc --edition=2021 -C opt-level=2 -L dependency="$WORK/build" --extern "rei_microphysics=$LIB" \
    "$RESEARCH/he25_proper_birth_20261016/src/owner_server.rs" -o "$BIN" > "$WORK/logs/BUILD_SERVER.log" 2>&1
PYTHONPATH="$HERE/src" "$PY" - "$OWNER_SHA" "$LIB" "$BIN" "$WORK/build/RECEIPT.json" <<'PY'
import sys
from execution import atomic_json,digest
atomic_json(sys.argv[4],{'owner_source':sys.argv[1],'rlib_sha256':digest(sys.argv[2]),'binary_sha256':digest(sys.argv[3]),'flags':'edition2021 opt-level2 no-fast-math','new_native_run':False})
PY
(cd "$HERE"; PYTHONPATH=src "$PY" -m pytest -q tests) > "$WORK/logs/TESTS.log" 2>&1
"$PY" "$HERE/src/he28_run.py" preflight --out "$WORK/preflight" > "$WORK/logs/PREFLIGHT.log" 2>&1
"$PY" "$HERE/src/he28_run.py" campaign --stage pilot --binary "$BIN" \
    --build-receipt "$WORK/build/RECEIPT.json" --out "$WORK/pilot" \
    --case-wall-s "${HE28_CASE_WALL_S:-3600}" > "$WORK/logs/PILOT.log" 2>&1
# Subsequent 'study' execution uses he28_run.py campaign, the accepted pilot path,
# and a NEW output directory. Never interpret process exit as global convergence.
