#!/usr/bin/env bash
# Offline fresh-source restoration: no Git checkout or previous executable.
set -eu
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
py=${PYTHON:-python3}
native_root=${NATIVE_ROOT:-$(mktemp -d "${TMPDIR:-/tmp}/c16b_grackle_restore.XXXXXX")}
out=${EVIDENCE_OUT:-$native_root/restore_evidence}
mkdir -p "$native_root"
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 8388608
"$py" - "$here" "$native_root" "$out" <<'PY'
from pathlib import Path
import hashlib,json,shutil,sys,tarfile
here,root,out=map(Path,sys.argv[1:]);root=root.resolve();out=out.resolve()
if any(root.iterdir()):raise SystemExit('NATIVE_ROOT must be a new or empty directory for a fresh build')
manifest=json.loads((here/'intake/native_source_manifest.json').read_text());archive=here/'intake'/manifest['archive']
if hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['archive_sha256']:raise SystemExit('source archive hash mismatch')
with tarfile.open(archive,'r:gz') as tf:tf.extractall(root)
verified=[]
for rel,expected in manifest['files'].items():
 p=root/rel;actual=hashlib.sha256(p.read_bytes()).hexdigest();ok=actual==expected['sha256'] and p.stat().st_size==expected['bytes'];verified.append(dict(path=rel,byte_equal=ok,sha256=actual))
 if not ok:raise SystemExit('restored source mismatch: '+rel)
crate=root/'rust/rei_microphysics';(crate/'examples/c16b_grackle').mkdir(parents=True,exist_ok=True)
shutil.copy2(here/'native_bind.rs',crate/'examples/c16b_grackle/native_bind.rs');shutil.copy2(here/'native_campaign.rs',crate/'examples/native_campaign.rs')
out.mkdir(parents=True,exist_ok=True)
(out/'source_identity.json').write_text(json.dumps(dict(native_commit=manifest['head'],archive_sha256=manifest['archive_sha256'],verified_files=verified,research_source_sha256={name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in ['native_bind.rs','native_campaign.rs']}),indent=2)+'\n')
PY
crate="$native_root/rust/rei_microphysics"
export CARGO_TARGET_DIR="$native_root/fresh_target"
printf '%s\n' "CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR=$CARGO_TARGET_DIR cargo build --offline --release --manifest-path $crate/Cargo.toml --example native_campaign -j 2" > "$out/invocation.txt"
set +e
/usr/bin/time -v -o "$out/build.time" cargo build --offline --release --manifest-path "$crate/Cargo.toml" --example native_campaign -j 2 > "$out/build.log" 2>&1
code=$?
printf 'build=%s\n' "$code" > "$out/exits.txt"
if [ "$code" -ne 0 ]; then exit "$code"; fi
for mode in tests retry_test essential; do
  mkdir -p "$out/$mode"
  printf '%s\n' "timeout 300s $CARGO_TARGET_DIR/release/examples/native_campaign $mode $out/$mode" >> "$out/invocation.txt"
  /usr/bin/time -v -o "$out/$mode/run.time" timeout 300s "$CARGO_TARGET_DIR/release/examples/native_campaign" "$mode" "$out/$mode" > "$out/$mode/stdout.log" 2> "$out/$mode/stderr.log"
  code=$?
  printf '%s=%s\n' "$mode" "$code" >> "$out/exits.txt"
  if [ "$code" -ne 0 ]; then exit "$code"; fi
done
set -e
"$py" - "$out" <<'PY'
from pathlib import Path
import json,math,sys
out=Path(sys.argv[1]);rollback=json.loads((out/'tests/rollback.json').read_text());recovery=json.loads((out/'retry_test/retry_recovery.json').read_text());controls=[json.loads(v) for v in (out/'tests/isolated_event_controls.jsonl').read_text().splitlines()];history=[json.loads(v) for v in (out/'essential/mixed1e4_n32.jsonl').read_text().splitlines()];summary=json.loads((out/'essential/mixed1e4_n32.summary.json').read_text())
checks=dict(rollback=all(rollback[k] for k in ['invalid_dt_rejected','invalid_no_rhs','native_failure_after_source','accepted_state_bitwise_unchanged']),recovery=all(recovery[k] for k in ['test_only_reject_after_native_success','old_state_bitwise_unchanged','recovered_equal_clean_half_steps','no_duplicate_source']),native_event_controls=len(controls)==12 and all(v['energy_normalized']<=1 for v in controls),full_native_trajectory=len(history)==33 and all(1<=v['temperature']<=1e6 and v['w']>0 and all(n>=0 and math.isfinite(n) for n in v['photons']) for v in history),ledger=summary['max_invariant_normalized']<=1)
receipt=dict(status='PASS' if all(checks.values()) else 'HOLD',checks=checks,fresh_source_build=True,native_full_physics_steps=summary['accepted'],native_rhs_evaluations=summary['rhs_evaluations'],max_invariant_normalized=summary['max_invariant_normalized'],scope='offline source restoration, fresh Rust build, essential controls and full-native trajectory; independent scientific campaign is separate')
(out/'RESTORE_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));sys.exit(0 if receipt['status']=='PASS' else 1)
PY
