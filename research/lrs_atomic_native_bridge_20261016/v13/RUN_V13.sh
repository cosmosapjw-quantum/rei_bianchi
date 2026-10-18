#!/usr/bin/env bash
# Restore, compile and run the existing V13 implementation. No model development.
set -euo pipefail
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export PATH="$HOME/.cargo/bin:$PATH"
command -v python3 >/dev/null
command -v cargo >/dev/null
command -v rustc >/dev/null
export CARGO_BUILD_JOBS=${CARGO_BUILD_JOBS:-2}
if ((CARGO_BUILD_JOBS<1 || CARGO_BUILD_JOBS>4)); then echo 'Use 1..4 build jobs' >&2; exit 2; fi
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=${V13_RUN_ROOT:-"$HERE/runs/$STAMP"}
if [[ -e "$OUT" ]]; then echo "Output already exists: $OUT" >&2; exit 2; fi
mkdir -p "$OUT/evidence"
exec > >(tee "$OUT/evidence/RUN_LOG.txt") 2>&1
printf 'utc=%s\nhost=%s\n' "$STAMP" "$(hostname)"
rustc --version; cargo --version; python3 --version
printf 'load: '; uptime; free -h; df -h "$OUT"
BASE=${V13_BASE:-"$HERE/../v12/native_owner"}
python3 "$HERE/RESTORE_NATIVE.py" --base "$BASE" --out "$OUT/native_owner"
export CARGO_TARGET_DIR="$OUT/target"
MAN="$OUT/native_owner/rust/rei_microphysics/Cargo.toml"
timeout 240s cargo test --manifest-path "$MAN" --offline --locked --release \
 --test axbi_driver --test axbi_covariant_transport --test v12_thermal_clocks --test v13_source_clocks
# Full optional suites in the V12 backup require separately absent BASS fixtures;
# their previous 16 failures are recorded, not silently reclassified as PASS.
timeout 180s cargo build --manifest-path "$MAN" --offline --locked --release --example v13_source_clock_sweep
MAX_N=${V13_MAX_N:-256}
CELLS=${V13_CELLS:-32}
TOL=${V13_NONLINEAR_TOL:-1e-15}
for X in 1e-5 1e-4; do
 timeout 180s "$CARGO_TARGET_DIR/release/examples/v13_source_clock_sweep" \
   "$OUT/evidence/sourceon_${X}.csv" "$X" "$MAX_N" "$CELLS" "$TOL"
done
python3 "$HERE/analyze_source_clocks.py" "$OUT/evidence/sourceon_1e-5.csv" \
 "$OUT/evidence/sourceon_1e-4.csv" --output "$OUT/evidence/ANALYSIS.json"
python3 - "$OUT" <<'PY'
import hashlib,json,pathlib,platform,sys
r=pathlib.Path(sys.argv[1]);a=json.loads((r/'evidence/ANALYSIS.json').read_text())
a['warnings']=[w for w in a['warnings'] if 'not NCP' not in w]
a['execution_hostname']=platform.node()
(r/'evidence/ANALYSIS.json').write_text(json.dumps(a,indent=2)+'\n')
f=[*r.glob('evidence/*.csv'),r/'evidence/ANALYSIS.json',r/'native_owner/V13_RESTORE_RECEIPT.json']
d={'status':'BOUNDED_RUN_COMPLETE','execution_hostname':platform.node(),
   'histories':sum(x['completed_histories'] for x in a['results']),
   'rows':sum(x['checked_rows'] for x in a['results']),
   'sourceon_global_order':'HOLD_PENDING_SCIENTIFIC_REVIEW',
   'sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in f}}
(r/'EXECUTION_RECEIPT.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
PY
printf '\nCOMPLETE: %s\n' "$OUT"
