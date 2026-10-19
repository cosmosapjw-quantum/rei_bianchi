#!/usr/bin/env bash
# Usage: RUN_PROJECTION_DIAGNOSTIC.sh [RESTORED_V14_NATIVE_ROOT|-] [FRESH_OUTPUT_DIR]
# With no native root (or '-'), use sibling ../RESTORE_V14.py to reconstruct exact V14.
# Requires rustc/cargo on PATH. Runs only this new example, never old tests or sweeps.
set -euo pipefail
TASK_HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 - "$TASK_HERE" "$@" <<'PY'
from pathlib import Path
import datetime, hashlib, importlib.util, json, os, platform, shutil, socket, subprocess, sys, tempfile, time
here=Path(sys.argv[1]);args=sys.argv[2:]
if len(args)>2:raise SystemExit('Usage: RUN_PROJECTION_DIAGNOSTIC.sh [RESTORED_V14_NATIVE_ROOT|-] [FRESH_OUTPUT_DIR]')
if len(args)==2:
    out=Path(args[1]).resolve()
    if out.exists():raise SystemExit('Refusing existing output directory: '+str(out))
    out.mkdir(parents=True)
else:out=Path(tempfile.mkdtemp(prefix='projection_run_',dir=here))
receipt={'schema':'rei.v14.projection.runner.1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'output':str(out),'hostname':socket.gethostname(),'platform':platform.platform(),'python':sys.version,'build_timeout_s':180,'diagnostic_timeout_s':60,'stages':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stage(name,command,cwd=None,timeout=None,env=None):
    t=time.monotonic()
    try:
        r=subprocess.run(command,cwd=cwd,capture_output=True,text=True,timeout=timeout,env=env)
        rc=r.returncode;stdout=r.stdout;stderr=r.stderr
    except subprocess.TimeoutExpired as e:
        rc=124
        stdout=e.stdout.decode() if isinstance(e.stdout,bytes) else (e.stdout or '')
        stderr=e.stderr.decode() if isinstance(e.stderr,bytes) else (e.stderr or '')
        stderr+='\nBOUNDED_TIMEOUT\n'
    (out/(name+'.stdout.log')).write_text(stdout);(out/(name+'.stderr.log')).write_text(stderr)
    receipt['stages'].append({'name':name,'command':command,'exit':rc,'elapsed_s':time.monotonic()-t})
    (out/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if rc:raise RuntimeError(f'{name} failed exit={rc}; logs in {out}')
    return stdout
try:
    if args and args[0]!='-':native=Path(args[0]).resolve()
    else:
        native=out/'native'
        stage('restore',[sys.executable,str(here.parent/'RESTORE_V14.py'),'--out',str(native)])
    # Import the analyzer's fixed identity table; verify existing restored source before copying.
    spec=importlib.util.spec_from_file_location('projection_analysis',here/'analyze_projection_diagnostic.py')
    analyzer=importlib.util.module_from_spec(spec);spec.loader.exec_module(analyzer)
    identity=native/'V14_RESTORE_RECEIPT.json'
    native_receipt=json.loads(identity.read_text())
    if native_receipt.get('schema')!='rei.v14.restore.1' or native_receipt.get('parent_sha')!='7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e' or native_receipt.get('sha256')!=analyzer.EXPECTED_NATIVE:
        raise RuntimeError('Unexpected native restore identity')
    for rel,h in analyzer.EXPECTED_NATIVE.items():
        if sha(native/rel)!=h:raise RuntimeError('Native source mismatch: '+rel)
    payload=here/'native_files/examples/v14_projection_diagnostic.rs'
    expected='868a4f8e28acebce0f1d78ff62f0adaf6a5d411c6896ea0b528afb8a16a0085f'
    if sha(payload)!=expected:raise RuntimeError('Diagnostic payload source mismatch')
    crate=native/'rust/rei_microphysics';source=crate/'examples/v14_projection_diagnostic.rs'
    if source.exists() and sha(source)!=expected:raise RuntimeError('Refusing to overwrite a different diagnostic example')
    if source.resolve()!=payload.resolve():shutil.copyfile(payload,source)
    receipt.update({'native_root':str(native),'source_sha256':sha(source),'native_identity_receipt_sha256':sha(identity)})
    receipt['rustc']=stage('rustc_version',['rustc','--version','--verbose'])
    receipt['cargo']=stage('cargo_version',['cargo','--version','--verbose'])
    env=os.environ.copy();env['CARGO_TARGET_DIR']=str(out/'target')
    stage('build',['cargo','build','--offline','--locked','--release','--example','v14_projection_diagnostic','--jobs','2'],cwd=crate,env=env,timeout=180)
    csv=out/'projection_diagnostic.csv'
    stage('diagnostic',[str(out/'target/release/examples/v14_projection_diagnostic'),str(csv)],timeout=60)
    command=[sys.executable,str(here/'analyze_projection_diagnostic.py'),'--csv',str(csv),'--identity',str(identity),
             '--native-root',str(native),'--source',str(source),'--out',str(out/'evidence/PROJECTION_ANALYSIS.json')]
    if importlib.util.find_spec('matplotlib') is not None:command+=['--figures',str(out/'figures')]
    stage('analysis',command)
    receipt['status']='COMPLETE';receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt['output_sha256']={str(p.relative_to(out)):sha(p) for p in [csv,Path(str(csv)+'.cells.csv'),out/'evidence/PROJECTION_ANALYSIS.json']}
except Exception as e:
    receipt['status']='FAILED';receipt['error']=str(e)
    (out/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
    raise
(out/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('COMPLETE '+str(out))
PY
