#!/usr/bin/env bash
# Actual original native source/gas code with new opt-in physical-birth adapter.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export PATH="$HOME/.cargo/bin:$PATH"
command -v python3 >/dev/null
command -v cargo >/dev/null
command -v rustc >/dev/null
export CARGO_BUILD_JOBS=${CARGO_BUILD_JOBS:-2}
if ((CARGO_BUILD_JOBS<1 || CARGO_BUILD_JOBS>4)); then echo 'Use 1..4 build jobs' >&2; exit 2; fi
OUT=${V14_RUN_ROOT:-"$HERE/runs/$(date -u +%Y%m%dT%H%M%SZ)"}
[[ ! -e "$OUT" ]] || { echo 'Output already exists' >&2; exit 2; }
mkdir -p "$OUT/evidence"
exec > >(tee "$OUT/evidence/RUN_LOG.txt") 2>&1
trap 'rc=$?; printf "exit_code=%s\n" "$rc" > "$OUT/evidence/EXIT_STATUS.txt"' EXIT
printf 'utc=%s\nhost=%s\n' "$(date -u +%FT%TZ)" "$(hostname)"
rustc --version; cargo --version; python3 --version
uptime; free -h; df -h "$OUT"
ARGS=()
if [[ -n ${V14_BASE:-} ]]; then ARGS+=(--base "$V14_BASE"); fi
python3 "$HERE/RESTORE_V14.py" "${ARGS[@]}" --out "$OUT/native_owner"
export CARGO_TARGET_DIR="$OUT/target"
MAN="$OUT/native_owner/rust/rei_microphysics/Cargo.toml"
timeout 300s cargo test --manifest-path "$MAN" --offline --locked --release \
 --test axbi_driver --test axbi_covariant_transport --test v12_thermal_clocks --test v13_source_clocks --test v14_physical_birth
# Inherited full crate's absent BASS/signed fixtures are not a targeted PASS.
timeout 180s cargo build --manifest-path "$MAN" --offline --locked --release --example v14_physical_birth_sweep
for X in 1e-5 1e-4; do
 timeout 300s "$CARGO_TARGET_DIR/release/examples/v14_physical_birth_sweep" \
  "$OUT/evidence/birth_${X}.csv" "$X" "${V14_MAX_N:-256}" "${V14_CELLS:-16}" "${V14_NONLINEAR_TOL:-1e-13}"
done
python3 - "$HERE" "$OUT" "${V14_MAX_N:-256}" <<'CHECK'
import pathlib, sys
sys.path.insert(0,sys.argv[1])
from birth_record_guard import validate_matrix
for tag in ('1e-5','1e-4'):
    validate_matrix(pathlib.Path(sys.argv[2])/'evidence'/f'birth_{tag}.csv',int(sys.argv[3]))
print('REQUESTED_MATRIX_COMPLETE')
CHECK
python3 "$HERE/analyze_v14.py" "$OUT/evidence/birth_1e-5.csv" "$OUT/evidence/birth_1e-4.csv" --out "$OUT/evidence/ANALYSIS.json" > "$OUT/evidence/ANALYSIS_STDOUT.txt"
python3 - "$OUT" <<'PY'
import hashlib,json,pathlib,platform,sys,datetime
r=pathlib.Path(sys.argv[1]);data=json.loads((r/'evidence/ANALYSIS.json').read_text())
receipt={'schema':'rei.v14.execution.1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'host':platform.node(),'histories':sum(x['histories'] for x in data['results']),
 'rows':sum(x['rows'] for x in data['results']),'native_tests':'ACTUAL_TARGETED_COMMAND_EXIT_ZERO',
 'source_on_p2':'HOLD','files':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.glob('evidence/*.csv')}}
(r/'EXECUTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
PY
printf 'V14_RUN_COMPLETE %s\n' "$OUT"
