#!/usr/bin/env bash
# Source-locked HE22 native-NCP bootstrap. Invoke only in authorized NCP session.
# No global Rust/Git settings, no force pushes, no edits to existing worktrees.
set -euo pipefail
export PATH="${HOME}/.cargo/bin:${PATH}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
WORK="${HE22_WORK_ROOT:-/root/HE23_NCP_DENSITY_20261016}"
OWNER_SHA='f7830e2f55e7a1938bc3c98f61b60651f8dae474'
OWNER="${WORK}/source_rei_bianchi_${OWNER_SHA:0:8}"
BUILD="${WORK}/build"
# Enforce create-only execution before touching logs, binaries or receipts.
python3 - "$WORK" <<'VERIFY_EMPTY_WORK'
import pathlib,sys
p=pathlib.Path(sys.argv[1])
if p.exists() and (not p.is_dir() or any(p.iterdir())):
    raise SystemExit('HE23_WORK_ROOT_NOT_EMPTY: preserve prior evidence; select a new path')
VERIFY_EMPTY_WORK
mkdir -p "$WORK" "$BUILD" "$WORK/logs"
if ! command -v rustc >/dev/null; then echo 'BLOCKED_NO_RUST' >&2; exit 10; fi
if ! command -v git >/dev/null; then echo 'BLOCKED_NO_GIT' >&2; exit 10; fi
printf '%s\n' "host=$(hostname)" "rust=$(rustc -V)" "cores=$(nproc)" > "$WORK/logs/preflight.txt"
free -h >> "$WORK/logs/preflight.txt"
df -h "$WORK" >> "$WORK/logs/preflight.txt"
if test -e "$OWNER/.git"; then
  test "$(git -C "$OWNER" rev-parse HEAD)" = "$OWNER_SHA" || {
    echo 'BLOCKED_EXISTING_SOURCE_IDENTITY_MISMATCH' >&2; exit 10;
  }
else
  test ! -e "$OWNER" || { echo 'BLOCKED_EXISTING_NON_GIT_SOURCE_PATH' >&2; exit 10; }
  git -c credential.helper='!gh auth git-credential' clone -q --filter=blob:none --no-checkout \
    https://github.com/cosmosapjw-quantum/rei_bianchi.git "$OWNER"
  git -C "$OWNER" sparse-checkout init --cone
  git -C "$OWNER" sparse-checkout set rust/rei_microphysics \
    docs/fastest_track_chat/REI-AXBI-GOAL-20261014 \
    research/axbi_goal_20261014/scenario
  git -C "$OWNER" -c credential.helper='!gh auth git-credential' fetch -q --depth=1 origin "$OWNER_SHA"
  git -C "$OWNER" checkout -q --detach "$OWNER_SHA"
fi
SOURCE="$OWNER/rust/rei_microphysics/src/lib.rs"
LIB="$BUILD/librei_microphysics.rlib"
BIN="$BUILD/he22_owner_point"
test -f "$SOURCE" || { echo 'BLOCKED_ORIGINAL_SOURCE_MISSING' >&2; exit 10; }
printf '%s\n' "$OWNER_SHA" > "$WORK/logs/source_commit.txt"
rustc --crate-name rei_microphysics --crate-type rlib --edition=2021 \
  -C opt-level=2 "$SOURCE" -o "$LIB" 2>&1 | tee "$WORK/logs/build_original.log"
rustc --edition=2021 -C opt-level=2 -L dependency="$BUILD" \
  --extern "rei_microphysics=$LIB" "$ROOT/src/he22_owner_point.rs" \
  -o "$BIN" 2>&1 | tee "$WORK/logs/build_he22.log"
sha256sum "$SOURCE" "$LIB" "$BIN" "$ROOT/src/he22_owner_point.rs" \
   > "$WORK/logs/build_sha256.txt"
# The base NCP Python3.12 may have neither numpy nor pytest. Never install to system.
if test -n "${HE22_PYTHON:-}"; then
  PY="$HE22_PYTHON"
else
  if test ! -x "$WORK/venv/bin/python"; then
    python3 -m venv "$WORK/venv"
  fi
  PY="$WORK/venv/bin/python"
  "$PY" -m pip install --disable-pip-version-check 'numpy>=2.0,<3' 'pytest>=8,<10' \
      2>&1 | tee "$WORK/logs/venv_install.log"
fi
"$PY" -c 'import numpy,pytest; print(numpy.__version__,pytest.__version__)' \
  > "$WORK/logs/python_deps.txt"
(cd "$ROOT" && HE23_NATIVE_BIN="$BIN" PYTHONPATH=src "$PY" -m pytest -q -p no:cacheprovider tests/test_he21.py \
  tests/test_he22_contract.py tests/test_he22_coupled.py \
  tests/test_he22_native_client.py tests/test_he23_density.py) 2>&1 | tee "$WORK/logs/pytest.txt"
# Strict one-case pilot first, preserve existing successful scientific receipt.
mkdir -p "$WORK/pilot"
if test -f "$WORK/pilot/SUMMARY.json"; then
  "$PY" - "$WORK/pilot/SUMMARY.json" "$OWNER_SHA" "$BIN" <<'VERIFY_PILOT'
import hashlib,json,sys
p,source,binary=sys.argv[1:]
a=json.load(open(p))
sha=hashlib.sha256(open(binary,'rb').read()).hexdigest()
if not (a['all_pass'] is True and a['source_commit']==source and
        a['native_binary_sha256']==sha):
    raise SystemExit('BLOCKED_PRIOR_PILOT_IDENTITY_OR_ACCEPTANCE_MISMATCH')
print('REUSED_VERIFIED_PREVIOUS_PILOT',p)
VERIFY_PILOT
else
  PYTHONPATH="$ROOT/src" timeout --signal=TERM --kill-after=10s 1200s \
    "$PY" "$ROOT/src/run_native.py" --binary "$BIN" \
    --source-sha "$OWNER_SHA" --output "$WORK/pilot" --stage pilot \
    --workers 1 --max-case-wall-s 600. 2>&1 | tee "$WORK/logs/pilot.log"
  test "$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["all_pass"])' "$WORK/pilot/SUMMARY.json")" = True || exit 12
fi
# Matrix is opt-in through exact env flag; run independently scoped cases.
if test "${HE22_RUN_MATRIX:-0}" = 1; then
  mkdir -p "$WORK/matrix"
  PYTHONPATH="$ROOT/src" timeout --signal=TERM --kill-after=10s 7200s \
    "$PY" "$ROOT/src/run_native.py" --binary "$BIN" \
    --source-sha "$OWNER_SHA" --output "$WORK/matrix" --stage matrix \
    --workers "${HE22_MATRIX_WORKERS:-8}" --max-case-wall-s 1200. \
    2>&1 | tee "$WORK/logs/matrix.log"
fi
# Preserve exact immutable snapshot and source lock; no remote cloud success claim here.
ARCH="$WORK/HE23_NCP_RESULTS_${OWNER_SHA:0:8}.tar.gz"
tar --sort=name --mtime='UTC 2026-10-16' --owner=0 --group=0 --numeric-owner \
  -czf "$ARCH" -C "$WORK" logs pilot $(test -d "$WORK/matrix" && printf 'matrix' || true)
sha256sum "$ARCH" > "$ARCH.sha256"
printf 'ARCHIVE=%s\n' "$ARCH"
cat "$ARCH.sha256"
