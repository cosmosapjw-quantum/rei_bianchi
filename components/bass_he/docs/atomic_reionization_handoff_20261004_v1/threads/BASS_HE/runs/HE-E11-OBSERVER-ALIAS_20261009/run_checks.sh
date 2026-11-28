#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ne 1 ]];then echo "USAGE bash run_checks.sh /ABSOLUTE/NEW_OUTPUT_DIR" >&2;exit 2;fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$1"
if [[ "$OUT" != /* ]] || [[ -e "$OUT" ]]; then echo "NEW_ABSOLUTE_OUTPUT_REQUIRED" >&2;exit 2;fi
cd "$ROOT"
sha256sum --check SHA256SUMS >/dev/null
export PYTHONPATH="$ROOT" PYTHONDONTWRITEBYTECODE=1
python -B -m unittest discover -s tests -v
mkdir -p "$OUT"
python -B -m e11.run_analysis "$ROOT/input" "$ROOT/e7" "$OUT/analysis"
python -B -m e11.run_budget "$ROOT/input" "$ROOT/e7" "$OUT/budget"
python -B -m e11.run_independent "$ROOT/input" "$ROOT/e7" "$OUT/independent"
for f in RESULTS.json OBSERVER_SOURCE.csv PAIRED_OBSERVER_ALIAS.csv;do cmp -s "$ROOT/canonical/analysis/$f" "$OUT/analysis/$f" || { echo "ANALYSIS_REPLAY_MISMATCH $f" >&2;exit 1;};done
for f in B_TOTAL_ONLY.csv BUDGET_RESULT.json;do cmp -s "$ROOT/canonical/budget/$f" "$OUT/budget/$f" || { echo "BUDGET_REPLAY_MISMATCH $f" >&2;exit 1;};done
cmp -s "$ROOT/canonical/independent/HIGH_PRECISION.json" "$OUT/independent/HIGH_PRECISION.json" || { echo "INDEPENDENT_REPLAY_MISMATCH" >&2;exit 1;}
cat > "$OUT/READY.json" <<'JSON'
{"task":"HE_E11_ANALYSIS_ONLY_REPRODUCTION","tests":18,"matched_outputs":6,"new_native_steps":0,"rust_candidate_compiled":false,"physical_admission":false,"owner_adoption":false}
JSON
printf 'E11_REPRODUCE_PASS test=18 canonical_files=6 new_native=0\n'
