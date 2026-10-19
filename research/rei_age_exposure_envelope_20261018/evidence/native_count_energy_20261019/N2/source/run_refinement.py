"""Bounded serial refinement campaign; no source/physics changes or auto-admission.

Each completed result is reused only with identical scientific configuration,
source/binary/interpreter identity, and matching output byte hashes. Interrupted
or failed cases stop the default path; --retry-failed allocates a NEW attempt.
"""
from pathlib import Path
import argparse, hashlib, json, math, os, platform, re, signal, subprocess, sys, time

NATIVE_SHA='35d9747a0bbedcafdb568467ce7c1e7a25f965b6'

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def canonical(x) -> bytes:
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def effective_transport_threads(value: str|None) -> int:
    if value is None or re.fullmatch(r'\+?[0-9]+',value) is None:
        return 1
    try:
        parsed=int(value)
    except ValueError:
        return 1
    # Match Rust's parse::<usize>().unwrap_or(1).clamp(1, 48).
    return min(48,max(1,parsed)) if parsed<=sys.maxsize*2+1 else 1

def read_json(p: Path):
    def reject(x): raise ValueError('NONFINITE_JSON: '+x)
    return json.loads(p.read_text(),parse_constant=reject)

def save(p: Path, value) -> None:
    p.parent.mkdir(exist_ok=True,parents=True)
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
    os.replace(tmp,p)

def plan() -> dict:
    base=dict(q=0.,birth_panels=32,n_mu=8,source_subdivisions=8,
              transport_cells=16,common_birth_levels=[8,16,32,64],time_factor=1)
    result={'age64':dict(base,name='age64',kind='reference',birth_panels=64)}
    for f in (8,16,32): result[f'time{f}']=dict(base,name=f'time{f}',kind='native',time_factor=f)
    result['spectral128']=dict(base,name='spectral128',kind='reference',q=.1,birth_panels=8,transport_cells=128)
    return result

def command(c: dict, binary: Path, solver: Path, out: Path, cap: float, rhs: int) -> list[str]:
    if c['kind']=='native':
        return [str(binary),'native_refine',str(c['q']),str(out),str(c['birth_panels']),
                str(c['n_mu']),str(c['source_subdivisions']),str(c['transport_cells']),
                ','.join(map(str,c['common_birth_levels'])),str(c['time_factor'])]
    result=[sys.executable,str(solver),str(binary),str(out),'--q',str(c['q']),
            '--birth-panels',str(c['birth_panels']),'--n-mu',str(c['n_mu']),
            '--source-subdivisions',str(c['source_subdivisions']),
            '--transport-cells',str(c['transport_cells']),'--max-wall-s',str(cap),
            '--max-rhs',str(rhs)]
    if c.get('tight'): result.append('--tight')
    result.extend(['--rpc-mode',c.get('rpc_mode','text')])
    result.extend(['--error-norm',c.get('error_norm','rms')])
    return result

def run_process(argv: list[str], out: Path, cap: float) -> dict:
    if not math.isfinite(cap) or cap<=0: raise ValueError('positive wall cap required')
    out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic(); timed=False
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
        proc=subprocess.Popen(argv,stdout=stdout,stderr=stderr,start_new_session=True,env=env)
        try: code=proc.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            timed=True
            try: os.killpg(proc.pid,signal.SIGTERM)
            except ProcessLookupError: pass
            try: proc.wait(timeout=.5)
            except subprocess.TimeoutExpired:
                try: os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait(timeout=5)
            code=124
    if code != 0:
        # The failed Python controller may have exited before its native server.
        # Only this task-created process group is targeted.
        try: os.killpg(proc.pid,signal.SIGTERM)
        except ProcessLookupError: pass
        time.sleep(.05)
        try: os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError: pass
    return dict(command=argv,exit_code=code,timed_out=timed,wall_s=time.monotonic()-started,
                peak_rss='NOT_MEASURED_BY_CONTROLLER; reference has its own ru_maxrss')

def reusable(receipt: dict, identity: str, root: Path) -> bool:
    hashes=receipt.get('outputs')
    return (receipt.get('status')=='COMPLETE' and receipt.get('fingerprint')==identity
            and isinstance(hashes,dict) and bool(hashes)
            and all((root/n).is_file() and sha(root/n)==h for n,h in hashes.items()))

def all_finite(v) -> bool:
    if isinstance(v,dict): return all(all_finite(x) for x in v.values())
    if isinstance(v,list): return all(all_finite(x) for x in v)
    return not isinstance(v,float) or math.isfinite(v)

def validate_outputs(c: dict, root: Path) -> None:
    endpoint=read_json(root/'endpoint.json')
    if not all_finite(endpoint): raise ValueError('NONFINITE_ENDPOINT')
    for key in ('N','U'):
        if not isinstance(endpoint.get(key),(int,float)) or endpoint[key]<0:
            raise ValueError('NEGATIVE_OR_MISSING_ENDPOINT_'+key)
    for key in ('flat','ledgers','Gamma_s','heat_erg_per_absorber_s','cohorts'):
        if key not in endpoint: raise ValueError('MISSING_ENDPOINT_'+key)
    if c['kind']=='reference':
        r=read_json(root/'solver_return.json')
        if r.get('error_norm','rms')!=c.get('error_norm','rms'):
            raise ValueError('REFERENCE_ERROR_NORM_MISMATCH')
        for key in ('q','birth_panels','n_mu','source_subdivisions','transport_cells'):
            if r[key]!=c[key]: raise ValueError('REFERENCE_CONFIG_MISMATCH_'+key)
        if r['status']!='SCOPED_NUMERICAL_EXECUTION_COMPLETE' or r['server_exit']!=0:
            raise ValueError('REFERENCE_DID_NOT_COMPLETE')
        ledger=read_json(root/'ledgers.json')
        if any(ledger[k]>1e-8 or ledger[k]<0 for k in ('energy_normalized','photon_normalized')):
            raise ValueError('ORIGINAL_REFERENCE_LEDGER_GATE')
    else:
        cfg=read_json(root/'refinement_config.json')
        for key in ('q','birth_panels','n_mu','source_subdivisions','transport_cells','time_factor','common_birth_levels'):
            if cfg[key]!=c[key]: raise ValueError('NATIVE_CONFIG_MISMATCH_'+key)
        if read_json(root/'native_return.json')['status']!='SCOPED_NUMERICAL_EXECUTION_COMPLETE':
            raise ValueError('NATIVE_DID_NOT_COMPLETE')

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared',type=Path,required=True)
    p.add_argument('--binary',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--cases',default=','.join(plan()))
    p.add_argument('--case-wall-s',type=float,default=1800.)
    p.add_argument('--total-wall-s',type=float,default=5400.)
    p.add_argument('--max-rhs',type=int,default=200000)
    p.add_argument('--tight',action='store_true')
    p.add_argument('--rpc-mode',choices=('text','binary64'),default='text')
    p.add_argument('--error-norm',choices=('rms','block-max'),default='rms')
    p.add_argument('--retry-failed',action='store_true')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if (not all(math.isfinite(v) and v>0 for v in (a.case_wall_s,a.total_wall_s)) or a.max_rhs<=0):
        p.error('positive finite resource bounds required')
    cases=plan();names=a.cases.split(',')
    if len(set(names))!=len(names) or any(n not in cases for n in names): p.error('unknown/duplicate case name')
    configs=[dict(cases[n],tight=a.tight,rpc_mode=a.rpc_mode) for n in names]
    for config in configs:
        if config['kind']=='reference':
            config['error_norm']=a.error_norm
    if a.dry_run:
        print(json.dumps(configs,indent=2));return
    native=a.prepared.resolve();solver=native/'positive_solver_refined.py'
    binary=(a.binary or native/'rust/rei_microphysics/target/release/examples/positive_native').resolve()
    prepared=read_json(native/'PREPARED_IDENTITY.json')
    if prepared['native_sha']!=NATIVE_SHA: raise ValueError('WRONG_NATIVE_SHA')
    for n,h in prepared['outputs'].items():
        if sha(native/n)!=h: raise ValueError('PREPARED_SOURCE_CHANGED: '+n)
    build=read_json(native/'BUILD_RECEIPT.json')
    if build['exit_code']!=0 or build['binary_sha256']!=sha(binary): raise ValueError('BUILD_IDENTITY_MISMATCH')
    if build['prepared_identity_sha256']!=sha(native/'PREPARED_IDENTITY.json'): raise ValueError('BUILD_SOURCE_MISMATCH')
    import numpy, scipy
    identity=dict(native_sha=NATIVE_SHA,binary_sha=sha(binary),solver_sha=sha(solver),
                  source_sha=sha(native/'PREPARED_IDENTITY.json'),python=platform.python_version(),
                  numpy=numpy.__version__,scipy=scipy.__version__,
                  transport_threads=effective_transport_threads(os.environ.get('REI_TRANSPORT_THREADS')),
                  rpc_mode=a.rpc_mode)
    a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
    lock=a.out/'.campaign.lock';fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    start=time.monotonic();records=[]
    try:
        for c in configs:
            fingerprint=hashlib.sha256(canonical(dict(config=c,identity=identity))).hexdigest()
            dest=a.out/c['name'];dest.mkdir(exist_ok=True)
            attempts=sorted(dest.glob('attempt[0-9][0-9][0-9]'))
            if attempts:
                prior=attempts[-1];receipt=read_json(prior/'RECEIPT.json') if (prior/'RECEIPT.json').exists() else {}
                if reusable(receipt,fingerprint,prior):
                    records.append(dict(name=c['name'],status='VERIFIED_EXISTING_RESULT_REUSED',path=str(prior)));continue
                if not a.retry_failed: raise RuntimeError('UNFINISHED_CHANGED_OR_FAILED_CASE: '+str(prior))
            cap=min(a.case_wall_s,a.total_wall_s-(time.monotonic()-start))
            if cap<=0: raise TimeoutError('TOTAL_CAMPAIGN_BUDGET_EXHAUSTED')
            trial=dest/f'attempt{len(attempts)+1:03d}';trial.mkdir()
            out=trial/'data';out.mkdir()
            receipt=dict(config=c,identity=identity,fingerprint=fingerprint,status='RUNNING',
                         resource_bounds=dict(case_wall_s=cap,max_rhs=a.max_rhs))
            save(trial/'RECEIPT.json',receipt)
            try:
                result=run_process(command(c,binary,solver,out,cap,a.max_rhs),trial,cap+2)
                receipt['execution']=result
                if result['exit_code']!=0: raise RuntimeError('CHILD_EXIT_'+str(result['exit_code']))
                validate_outputs(c,out)
                receipt['outputs']={str(f.relative_to(trial)):sha(f) for f in sorted(out.rglob('*')) if f.is_file()}
                receipt['status']='COMPLETE';receipt['scientific_accuracy']='NOT_ADMITTED_BY_EXECUTION'
            except BaseException as e:
                receipt['status']='FAILED';receipt['failure']=repr(e);raise
            finally:
                save(trial/'RECEIPT.json',receipt)
                records.append(dict(name=c['name'],status=receipt['status'],path=str(trial)))
                save(a.out/'MATRIX_EXECUTION.json',records)
    finally:
        save(a.out/'MATRIX_EXECUTION.json',records)
        lock.unlink()
if __name__=='__main__': main()
