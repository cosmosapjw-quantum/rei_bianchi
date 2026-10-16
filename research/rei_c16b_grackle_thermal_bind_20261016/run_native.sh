#!/usr/bin/env bash
set -u
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd "$here/../.." && pwd)
native_root=${NATIVE_ROOT:-/root/REI_C16B_GRACKLE_SCRATCH_20261016/native}
crate="$native_root/rust/rei_microphysics"
py=${PYTHON:-/root/REI_C16B_NATIVE_20261016/venv/bin/python}
mode=${1:-campaign}
out="$here/evidence/native/$mode"
mkdir -p "$out" "$crate/examples/c16b_grackle"
cp "$here/native_bind.rs" "$crate/examples/c16b_grackle/native_bind.rs"
cp "$here/native_campaign.rs" "$crate/examples/native_campaign.rs"
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 8388608
"$py" - "$repo" "$crate" "$out" <<'PY'
import hashlib,json,subprocess,sys
from pathlib import Path
repo,crate,out=map(Path,sys.argv[1:]);commit='a42fd7c9849306074a9f7a262628cd852ce34dea';prefix='rust/rei_microphysics/'
paths=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',commit,prefix],text=True).splitlines();rows=[]
for path in paths:
 expected=subprocess.check_output(['git','-C',str(repo),'show',f'{commit}:{path}']);p=crate/path[len(prefix):];rows.append(dict(path=path,sha256=hashlib.sha256(expected).hexdigest(),byte_equal=p.exists() and p.read_bytes()==expected))
assert paths and all(v['byte_equal'] for v in rows),'original native source mismatch'
(out/'source_identity.json').write_text(json.dumps(dict(native_commit=commit,files=rows),indent=2)+'\n')
PY
identity_exit=$?
printf 'identity=%s\n' "$identity_exit" > "$out/exits.txt"
if [ "$identity_exit" -ne 0 ]; then exit "$identity_exit"; fi
printf '%s\n' "CARGO_BUILD_JOBS=2 cargo build --release --manifest-path $crate/Cargo.toml --example native_campaign -j 2" "timeout 300s $crate/target/release/examples/native_campaign $mode $out" > "$out/invocation.txt"
/usr/bin/time -v -o "$out/build.time" cargo build --release --manifest-path "$crate/Cargo.toml" --example native_campaign -j 2 > "$out/build.log" 2>&1
build_exit=$?
printf 'build=%s\n' "$build_exit" >> "$out/exits.txt"
if [ "$build_exit" -ne 0 ]; then exit "$build_exit"; fi
/usr/bin/time -v -o "$out/run.time" timeout 300s "$crate/target/release/examples/native_campaign" "$mode" "$out" > "$out/stdout.log" 2> "$out/stderr.log"
run_exit=$?
printf 'run=%s\n' "$run_exit" >> "$out/exits.txt"
exit "$run_exit"
