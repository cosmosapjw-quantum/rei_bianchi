#!/usr/bin/env bash
# Fail closed; restores/consumes only a new output path. No 3x384 replay.
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 || "$1" != /* ]]; then
  echo 'USAGE: bash run_checks.sh /ABSOLUTE/NEW_OUTPUT [--native-pilot]' >&2
  exit 2
fi
NATIVE=false
if [[ $# -eq 2 ]]; then
  [[ "$2" == '--native-pilot' ]] || { echo 'UNKNOWN_FLAG' >&2; exit 2; }
  NATIVE=true
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$1"
[[ ! -e "$OUT" ]] || { echo 'CREATE_ONLY_OUTPUT_EXISTS' >&2; exit 2; }
mkdir -p "$OUT"
cd "$ROOT"
python3 -W error -m unittest discover -s tests -v > "$OUT/PYTHON_TESTS.log" 2>&1
python3 -B code/accepted_step_balance.py parent/full --output "$OUT/STEP_BALANCE.json"
python3 -B - "$OUT" <<'PY'
import json,sys
from pathlib import Path
sys.path.insert(0,'code')
from independent_decimal import check_decimal,check_stage_summary
from stage_witness_reader import validate_stage_rows,read_stage_rows
out=Path(sys.argv[1]);inp=Path('parent/full')
other={'decimal':check_decimal(inp),'stage':check_stage_summary(inp)}
(out/'DECIMAL_AND_STAGE.json').write_text(json.dumps(other,indent=2)+'\n')
checks={}
for mode in ('OFF','KF','GM'):
 b=Path('evidence/pilot_final')/mode
 checks[mode]=validate_stage_rows(read_stage_rows(b/'OWNER_STAGE_INPUTS.csv'),b/'OWNER_SELECTED_RCT.csv',b/'OWNER_INTERNAL_5.csv')
(out/'STAGE_PILOT_VALIDATION.json').write_text(json.dumps(checks,indent=2)+'\n')
PY
for name in STEP_BALANCE.json DECIMAL_AND_STAGE.json STAGE_PILOT_VALIDATION.json; do
 cmp "evidence/$name" "$OUT/$name" || { echo "REPRODUCE_BYTES_FAIL $name" >&2; exit 1; }
done
if $NATIVE; then
  command -v rustc >/dev/null || { echo 'RUSTC_NOT_INSTALLED' >&2; exit 3; }
  command -v cargo >/dev/null || { echo 'CARGO_NOT_INSTALLED' >&2; exit 3; }
  [[ "$(rustc --version)" == rustc\ 1.94.1* ]] || { echo 'RUST_TOOLCHAIN_UNPINNED' >&2; exit 3; }
  cp -a stage_candidate "$OUT/stage_candidate"
  C="$OUT/stage_candidate/research/transport_20261007/short-hhe-midpoint"
  (cd "$C" && RUSTFLAGS='-D warnings' cargo build --offline --locked --release --example e13_stage_inputs > "$OUT/NATIVE_BUILD.log" 2>&1 && cargo test --offline --locked --test e10_native_mode > "$OUT/RUST_TESTS.log" 2>&1)
  for mode in OFF KF GM; do
    "$C/target/release/examples/e13_stage_inputs" "$C/e9_common_domain.cfg" "$mode" "$OUT/NATIVE_$mode" 2 > "$OUT/NATIVE_${mode}.stdout" 2> "$OUT/NATIVE_${mode}.stderr"
  done
  python3 -B - "$OUT" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0,'code')
from stage_witness_reader import read_stage_rows,validate_stage_rows
root=Path(sys.argv[1])
for mode in ('OFF','KF','GM'):
 b=root/('NATIVE_'+mode)
 validate_stage_rows(read_stage_rows(b/'OWNER_STAGE_INPUTS.csv'),b/'OWNER_SELECTED_RCT.csv',b/'OWNER_INTERNAL_5.csv')
 print('NATIVE_STAGE_SOURCE_PASS',mode)
PY
fi
printf 'E13A_REPRODUCE_PASS output=%s native=%s\n' "$OUT" "$NATIVE"
