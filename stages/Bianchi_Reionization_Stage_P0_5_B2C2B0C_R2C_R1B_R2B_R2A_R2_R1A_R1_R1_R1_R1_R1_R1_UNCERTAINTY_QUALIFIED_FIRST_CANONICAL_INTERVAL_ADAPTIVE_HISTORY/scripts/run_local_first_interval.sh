#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "usage: $0 RUN_DIR [--resume] [--max-accepted N] [--max-attempts N]" >&2
  exit 64
fi
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
STAGE_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)
RUN_DIR=$(realpath -m -- "$1")
shift
resume_flag=0
max_accepted=()
max_attempts=()
while (( $# )); do
  case "$1" in
    --resume)
      if (( resume_flag )); then
        echo "duplicate --resume" >&2
        exit 64
      fi
      resume_flag=1
      shift
      ;;
    --max-accepted|--max-attempts)
      option=$1
      if (( $# < 2 )) || [[ ! $2 =~ ^[1-9][0-9]*$ ]]; then
        echo "$option requires a positive integer" >&2
        exit 64
      fi
      if [[ $option == --max-accepted ]]; then
        if (( ${#max_accepted[@]} )); then echo "duplicate $option" >&2; exit 64; fi
        max_accepted=("$option" "$2")
      else
        if (( ${#max_attempts[@]} )); then echo "duplicate $option" >&2; exit 64; fi
        max_attempts=("$option" "$2")
      fi
      shift 2
      ;;
    --run-dir|--workers|--worker-timeout)
      echo "launcher owns controller option $1" >&2
      exit 64
      ;;
    *)
      echo "unsupported option: $1" >&2
      exit 64
      ;;
  esac
done
mkdir -p -- "$RUN_DIR"
if [[ -L "$RUN_DIR/RUN_OWNER.json" ]]; then
  echo "refusing symlinked run ownership marker: $RUN_DIR/RUN_OWNER.json" >&2
  exit 73
fi
owned_run=0
reuse_preflight=0
if [[ -f "$RUN_DIR/RUN_OWNER.json" ]]; then
  owned_run=1
  if (( ! resume_flag )); then
    echo "owned run requires --resume" >&2
    exit 64
  fi
  if [[ -L "$RUN_DIR/preflight.json" || ! -f "$RUN_DIR/preflight.json" ]]; then
    echo "owned run lacks a regular immutable preflight: $RUN_DIR/preflight.json" >&2
    exit 73
  fi
else
  if (( resume_flag )); then
    echo "--resume requires an owned run" >&2
    exit 73
  fi
  shopt -s nullglob dotglob
  run_entries=("$RUN_DIR"/*)
  shopt -u nullglob dotglob
  for entry in "${run_entries[@]}"; do
    case "${entry##*/}" in
      .RUN.lock)
        if [[ -L "$entry" || ! -f "$entry" ]]; then
          echo "refusing invalid pre-owner run lock: $entry" >&2
          exit 73
        fi
        ;;
      preflight.json)
        if [[ -L "$entry" || ! -f "$entry" ]]; then
          echo "refusing invalid pre-owner preflight: $entry" >&2
          exit 73
        fi
        reuse_preflight=1
        ;;
      *)
        echo "refusing nonempty unowned run directory: $RUN_DIR" >&2
        exit 73
        ;;
    esac
  done
fi
export BLIS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export PYTHONHASHSEED=0
export XLA_FLAGS="--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1"
PREFLIGHT_TMP=$(mktemp -- "${RUN_DIR}.preflight.XXXXXX")
trap 'rm -f -- "$PREFLIGHT_TMP"' EXIT
python "$STAGE_DIR/analysis/preflight.py" --output "$PREFLIGHT_TMP"
if (( owned_run )); then
  rm -f -- "$PREFLIGHT_TMP"
elif (( reuse_preflight )); then
  if ! cmp -s -- "$PREFLIGHT_TMP" "$RUN_DIR/preflight.json"; then
    echo "pre-owner preflight differs from the current validated receipt" >&2
    exit 73
  fi
  rm -f -- "$PREFLIGHT_TMP"
else
  ln -- "$PREFLIGHT_TMP" "$RUN_DIR/preflight.json"
  rm -f -- "$PREFLIGHT_TMP"
fi
trap - EXIT
resume_args=()
if (( resume_flag )); then resume_args=(--resume); fi
exec python "$STAGE_DIR/analysis/run_adaptive_history.py" \
  --run-dir "$RUN_DIR" \
  --workers "${REI_BIANCHI_WORKERS:-3}" \
  --worker-timeout "${REI_BIANCHI_WORKER_TIMEOUT:-1200}" \
  "${resume_args[@]}" \
  "${max_accepted[@]}" \
  "${max_attempts[@]}"
