#!/usr/bin/env bash
set -u
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd "$here/../.." && pwd)
root=$(cd "$repo/.." && pwd)
crate="$root/native/rust/rei_microphysics"
py="$root/venv/bin/python"
evidence="$here/evidence/native"
mkdir -p "$evidence"
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 8388608
# Immutable source bytes bind the complete tracked crate, not only called modules.
"$py" - "$repo" "$crate" "$here" "$evidence" <<'PY'
import hashlib,json,subprocess,sys
from pathlib import Path
repo,crate,here,out=map(Path,sys.argv[1:])
commit='0e25846433170d0f420c4cda44a0bedbf02cd177';prefix='rust/rei_microphysics/'
paths=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',commit,prefix],text=True).splitlines()
rows=[]
for path in paths:
    expected=subprocess.check_output(['git','-C',str(repo),'show',f'{commit}:{path}'])
    target=crate/path.removeprefix(prefix)
    actual=target.read_bytes() if target.exists() else None
    rows.append(dict(path=path,sha256=hashlib.sha256(expected).hexdigest(),byte_equal=actual==expected))
identical=(here/'c16b_native_parity.rs').read_bytes()==(crate/'examples/c16b_native_parity.rs').read_bytes()
result=dict(native_commit=commit,research_base='f8f26710e3961609acf4d7e7930bc7b2a95bd39c',actual_research_head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),tracked_crate_files=rows,example_copies_identical=identical)
(out/'source_identity.json').write_text(json.dumps(result,indent=2)+'\n')
assert paths and all(r['byte_equal'] for r in rows) and identical, 'immutable source/copy byte mismatch'
PY
identity_exit=$?
printf 'identity=%s\n' "$identity_exit" > "$evidence/exits.txt"
if [ "$identity_exit" -ne 0 ]; then exit "$identity_exit"; fi
printf '%s\n' "CARGO_BUILD_JOBS=2 cargo build --release --manifest-path $crate/Cargo.toml --example c16b_native_parity -j 2" "timeout 300s $crate/target/release/examples/c16b_native_parity" "timeout 300s $py $here/compare_native.py $evidence/native_points.jsonl --out $evidence" > "$evidence/invocation.txt"
/usr/bin/time -v -o "$evidence/build.time" cargo build --release --manifest-path "$crate/Cargo.toml" --example c16b_native_parity -j 2 > "$evidence/build.log" 2>&1
build_exit=$?
printf 'build=%s\n' "$build_exit" >> "$evidence/exits.txt"
if [ "$build_exit" -ne 0 ]; then exit "$build_exit"; fi
/usr/bin/time -v -o "$evidence/native.time" timeout 300s "$crate/target/release/examples/c16b_native_parity" > "$evidence/native_points.jsonl" 2> "$evidence/native.stderr"
native_exit=$?
printf 'native=%s\n' "$native_exit" >> "$evidence/exits.txt"
if [ "$native_exit" -ne 0 ]; then exit "$native_exit"; fi
/usr/bin/time -v -o "$evidence/comparator.time" timeout 300s "$py" "$here/compare_native.py" "$evidence/native_points.jsonl" --out "$evidence" > "$evidence/comparator.stdout" 2> "$evidence/comparator.stderr"
compare_exit=$?
printf 'compare=%s\n' "$compare_exit" >> "$evidence/exits.txt"
"$py" - "$here" "$evidence" <<'PY'
import hashlib,json,sys
from pathlib import Path
here,out=map(Path,sys.argv[1:]); paths=[here/'c16b_native_parity.rs',here/'compare_native.py',here/'run_native.sh',out/'native_points.jsonl',out/'checks.json',out/'summary.json']
(out/'artifact_hashes.json').write_text(json.dumps({str(p.relative_to(here)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()},indent=2)+'\n')
PY
cat "$evidence/comparator.stdout"
exit "$compare_exit"
