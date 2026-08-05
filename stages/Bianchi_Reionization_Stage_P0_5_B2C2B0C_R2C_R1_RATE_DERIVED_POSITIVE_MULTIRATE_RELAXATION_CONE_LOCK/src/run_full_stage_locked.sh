#!/usr/bin/env bash
set -euo pipefail
REPO=${1:?repo}
STAGE_REL=${2:?stage_rel}
STATE_INPUT=${3:?state_input}
GROUP_INPUT=${4:?group_input}
STAGE="$REPO/$STAGE_REL"
exec 9>"$STAGE/logs/full_run.lock"
if ! flock -n 9; then
  echo 73 > "$STAGE/logs/full_run.exit"
  echo "another full run holds the execution lock" > "$STAGE/logs/full_run.launch_error.log"
  exit 73
fi
for f in dual_farkas_kkt_certificates.jsonl trajectory_certificates.jsonl macro_case_results.csv selected_rate_solutions.csv refinement_audit.csv violated_cases.csv exact_zero_audit.csv summary.json; do
  rm -f "$STAGE/data/$f"
done
rm -f "$STAGE/logs/full_run.stdout.log" "$STAGE/logs/full_run.time.stderr.log" "$STAGE/logs/full_run.exit" "$STAGE/logs/full_run.done"
cd "$REPO"
set +e
/usr/bin/time -v python "$STAGE_REL/src/run_positive_multirate_cone.py" \
  --repo . --stage "$STAGE_REL" --state-input "$STATE_INPUT" --group-input "$GROUP_INPUT" \
  > "$STAGE/logs/full_run.stdout.log" 2> "$STAGE/logs/full_run.time.stderr.log"
status=$?
set -e
printf '%s\n' "$status" > "$STAGE/logs/full_run.exit"
date -u +%Y-%m-%dT%H:%M:%SZ > "$STAGE/logs/full_run.done"
exit "$status"
