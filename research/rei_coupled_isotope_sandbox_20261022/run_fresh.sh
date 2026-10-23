#!/usr/bin/env bash
# Replay a source artifact in a fresh /tmp copy; this is not a Git checkout.
set -eu
UNIT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PREPARE_ONLY=0
TARGET_DIR=
while [ "$#" -gt 0 ]; do
    case "$1" in
        --help|-h)
            echo 'Usage: bash run_fresh.sh [--prepare-only] [new_/tmp_directory]'
            echo 'Copy this small unit; preserve recorded evidence; run unchanged run.sh then two targeted onset checks.'
            exit 0 ;;
        --prepare-only) PREPARE_ONLY=1 ;;
        --*) echo 'Unknown option' >&2; exit 2 ;;
        *)
            if [ -n "$TARGET_DIR" ]; then echo 'Only one target directory is accepted' >&2; exit 2; fi
            TARGET_DIR=$1 ;;
    esac
    shift
done
if [ -n "$TARGET_DIR" ]; then
    case "$TARGET_DIR" in /tmp/*) ;; *) echo 'Requested replay copy must be a new path under /tmp/' >&2; exit 2;; esac
    if [ -e "$TARGET_DIR" ]; then echo 'Target already exists; no files overwritten' >&2; exit 2; fi
    mkdir -- "$TARGET_DIR"
else
    TARGET_DIR=$(mktemp -d /tmp/rei-isotope-sandbox.XXXXXXXX)
fi
cp -a -- "$UNIT_DIR/." "$TARGET_DIR/"
if [ -d "$TARGET_DIR/recorded_evidence" ] || [ -d "$TARGET_DIR/recorded_figures" ]; then
    echo 'Source already contains a replay; choose the original delivered unit as source' >&2
    exit 2
fi
if [ -d "$TARGET_DIR/evidence" ]; then mv -- "$TARGET_DIR/evidence" "$TARGET_DIR/recorded_evidence"; fi
if [ -d "$TARGET_DIR/figures" ]; then mv -- "$TARGET_DIR/figures" "$TARGET_DIR/recorded_figures"; fi
python - "$UNIT_DIR" "$TARGET_DIR" "$PREPARE_ONLY" <<'PY'
import json,sys
from pathlib import Path
source,target,prepare=sys.argv[1:]
value={'source_unit':source,'fresh_artifact_copy':target,'not_git_clone_or_worktree':True,
       'preserved_evidence':'recorded_evidence/','preserved_figures':'recorded_figures/',
       'prepare_only':prepare=='1','scientific_execution_started':prepare!='1',
       'commands':[['bash',target+'/run.sh'],[sys.executable,target+'/code/check_source_onset.py']],
       'run_accounting':'156 baseline checks in one new invocation, then 2 targeted checks in a separate invocation'}
Path(target,'FRESH_COPY.json').write_text(json.dumps(value,indent=2)+'\n')
print('Fresh artifact copy: '+target)
PY
if [ "$PREPARE_ONLY" -eq 1 ]; then
    echo 'Prepared only; no scientific command executed.'
    exit 0
fi
export MPLCONFIGDIR="$TARGET_DIR/evidence/matplotlib_cache"
bash "$TARGET_DIR/run.sh"
python "$TARGET_DIR/code/check_source_onset.py"
