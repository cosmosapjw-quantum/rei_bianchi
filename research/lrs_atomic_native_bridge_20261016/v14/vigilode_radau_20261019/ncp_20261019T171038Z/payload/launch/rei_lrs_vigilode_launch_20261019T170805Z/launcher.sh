#!/usr/bin/env bash
# Wrapper: runs the owner-supplied command block verbatim inside the existing LRS checkout.
cd /root/REI_LRS_CASEB_V4_20261016/repo
export PATH=/root/.cargo/bin:$PATH
LOG=/tmp/rei_lrs_vigilode_launch_20261019T170805Z
mkdir -p $LOG
date -u +%FT%T.%NZ > $LOG/START_UTC
bash -c '
set -euo pipefail

REI_REPO="$(git rev-parse --show-toplevel)"
REI_BRANCH="research/rei-lrs-v14-physical-birth-20261018"
REI_REL="research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019"

git -C "$REI_REPO" status --short
git -C "$REI_REPO" fetch origin "$REI_BRANCH"

REI_SOURCE_SHA="$(
  git -C "$REI_REPO" show     "origin/$REI_BRANCH:$REI_REL/stages/FINAL_DELIVERY.json" |
  python3 -c     "import json,sys; print(json.load(sys.stdin)[\"source_publication_sha\"])"
)"
echo "REI_REPO=$REI_REPO REI_SOURCE_SHA=$REI_SOURCE_SHA"

REI_JOB_ROOT="/tmp/rei_lrs_vigilode_$(date -u +%Y%m%dT%H%M%SZ)"
echo "REI_JOB_ROOT=$REI_JOB_ROOT"
mkdir -p "$REI_JOB_ROOT/input"

git -C "$REI_REPO" archive   "$REI_SOURCE_SHA" research/lrs_atomic_native_bridge_20261016 |
  tar -x -C "$REI_JOB_ROOT/input"

REI_INPUT_ROOT="$REI_JOB_ROOT/input/research/lrs_atomic_native_bridge_20261016"
REI_TASK_ROOT="$REI_INPUT_ROOT/v14/vigilode_radau_20261019"

python3 "$REI_TASK_ROOT/prepare_and_run.py"   --input-root "$REI_INPUT_ROOT"   --output-root "$REI_JOB_ROOT/run"   --cargo cargo --all
echo PREPARE_AND_RUN_EXIT=0

python3 "$REI_TASK_ROOT/analyze_matrix.py"   --receipts "$REI_JOB_ROOT/run/evidence"   --out "$REI_JOB_ROOT/analysis"
echo ANALYZE_EXIT=0
' > $LOG/stdout.log 2> $LOG/stderr.log
echo $? > $LOG/EXIT_CODE
date -u +%FT%T.%NZ > $LOG/END_UTC
