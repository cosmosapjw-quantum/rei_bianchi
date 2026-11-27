#!/usr/bin/env bash
# New references only. Existing HE28 transport/chemistry histories are not rerun.
set -euo pipefail
export PATH="$HOME/.cargo/bin:$PATH"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_DYNAMIC=FALSE
export OMP_PLACES=cores OMP_PROC_BIND=close
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
RESEARCH="$(dirname "$HERE")"
OWNER_SHA=f7830e2f55e7a1938bc3c98f61b60651f8dae474
WORK="${HE29_WORK_ROOT:-$HOME/HE29_REFERENCE_$(date -u +%Y%m%dT%H%M%SZ)}"
[[ ! -e "$WORK" ]] || { echo "HE29_FRESH_WORK_REQUIRED: $WORK" >&2; exit 10; }
mkdir -p "$WORK/build" "$WORK/logs"
finish() {
  rc=$?;trap - EXIT
  printf '%s\n' "$rc" > "$WORK/logs/EXIT_CODE.txt"
  # Archive is OUTSIDE the archived directory, preserving every failure too.
  tar -czf "$WORK.tar.gz" -C "$(dirname "$WORK")" "$(basename "$WORK")"
  sha256sum "$WORK.tar.gz" > "$WORK.tar.gz.sha256"
  printf 'HE29_WORK_ROOT=%s\nEXIT_CODE=%s\n' "$WORK" "$rc"
  exit "$rc"
}
trap finish EXIT
command -v python3 >/dev/null
command -v rustc >/dev/null || { echo HE29_NO_RUST >&2; exit 10; }
{ date -u +%FT%TZ; uname -a; rustc -Vv; nproc; free -h; df -h "$WORK"; } > "$WORK/logs/ENVIRONMENT.txt"
if [[ -n "${HE29_PYTHON:-}" ]]; then PY="$HE29_PYTHON"; else
  python3 -m venv "$WORK/venv";PY="$WORK/venv/bin/python"
  "$PY" -m pip install -r "$HERE/requirements.txt" > "$WORK/logs/DEPENDENCIES.log" 2>&1
fi
"$PY" -m pip freeze > "$WORK/logs/PYTHON_FREEZE.txt"
(cd "$HERE"; PYTHONPATH=src "$PY" -m pytest -q tests) > "$WORK/logs/TESTS.log" 2>&1
"$PY" "$HERE/src/reference_runner.py" preflight --out "$WORK/preflight" > "$WORK/logs/PREFLIGHT.log" 2>&1
OWNER="$WORK/owner"
if [[ -n "${HE29_OWNER_REPO:-}" ]]; then
  git -C "$HE29_OWNER_REPO" cat-file -e "$OWNER_SHA^{commit}"
  git clone --no-hardlinks --no-checkout "$HE29_OWNER_REPO" "$OWNER" > "$WORK/logs/OWNER_CLONE.log" 2>&1
else
  git clone --filter=blob:none --no-checkout https://github.com/cosmosapjw-quantum/rei_bianchi.git "$OWNER" > "$WORK/logs/OWNER_CLONE.log" 2>&1
fi
if ! git -C "$OWNER" cat-file -e "$OWNER_SHA^{commit}" 2>/dev/null; then
  git -C "$OWNER" fetch --depth=1 origin "$OWNER_SHA" >> "$WORK/logs/OWNER_CLONE.log" 2>&1
fi
git -C "$OWNER" sparse-checkout init --cone
git -C "$OWNER" sparse-checkout set rust/rei_microphysics docs/fastest_track_chat/REI-AXBI-GOAL-20261014 research/axbi_goal_20261014/scenario
git -C "$OWNER" checkout --detach "$OWNER_SHA" >> "$WORK/logs/OWNER_CLONE.log" 2>&1
[[ "$(git -C "$OWNER" rev-parse HEAD)" == "$OWNER_SHA" ]]
[[ -z "$(git -C "$OWNER" status --porcelain)" ]]
LIB="$WORK/build/librei_microphysics.rlib";BIN="$WORK/build/he29_owner_server"
SERVER="$RESEARCH/he25_proper_birth_20261016/src/owner_server.rs"
rustc --edition=2021 --crate-name rei_microphysics --crate-type rlib -C opt-level=2 \
  "$OWNER/rust/rei_microphysics/src/lib.rs" -o "$LIB" > "$WORK/logs/BUILD_OWNER.log" 2>&1
rustc --edition=2021 -C opt-level=2 -L dependency="$WORK/build" --extern "rei_microphysics=$LIB" \
  "$SERVER" -o "$BIN" > "$WORK/logs/BUILD_SERVER.log" 2>&1
"$PY" - "$OWNER_SHA" "$LIB" "$BIN" "$SERVER" "$WORK/build/RECEIPT.json" <<'PY'
from pathlib import Path
import json,hashlib,sys
owner,lib,binary,server,out=sys.argv[1:]
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
with Path(out).open('x') as f:json.dump(dict(owner_source=owner,rlib_sha256=h(lib),binary_sha256=h(binary),server_source_sha256=h(server),flags='edition2021 opt-level2 no-fast-math',native_run=False),f,indent=2)
PY
"$PY" "$HERE/src/reference_runner.py" campaign --binary "$BIN" --receipt "$WORK/build/RECEIPT.json" \
  --out "$WORK/references" --case-wall-s "${HE29_CASE_WALL_S:-3600}" > "$WORK/logs/CAMPAIGN.log" 2>&1
"$PY" "$HERE/src/analyze_references.py" --root "$WORK/references" --out "$WORK/REFERENCE_ANALYSIS.json" > "$WORK/logs/ANALYSIS.log" 2>&1
# No source-only success above is a full EoR/cosmic-spectrum admission.
