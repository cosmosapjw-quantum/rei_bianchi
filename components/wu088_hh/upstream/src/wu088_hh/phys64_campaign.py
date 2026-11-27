"""Bounded, resumable PHYS64 campaign. No SSH or credential discovery.

Every case is a separate OS process with a wall timeout and VM ceiling.
Existing attempts are retained. Resume requires source/config/runtime and
both result-file hashes to match. A local run is never relabelled NCP.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import contextlib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE='research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
SOURCE_SHA='f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
CODE=['src/wu088_hh/'+n+'.py' for n in (
    'phys63_lap_contract','phys63_scaled_riccati','phys64_born_contract',
    'phys64_born_hierarchy','phys64_campaign')]+['scripts/phys64_ncp.py']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def atomic_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
    os.replace(tmp,path)


def case_specs(profile):
    def one(ells,m=0,T=39.,nodes=128,tol=2e-11,step=.25):
        return dict(ells=list(ells),m=m,outer=T,orders=3,nodes=nodes,rtol=tol,max_step=step)
    if profile=='smoke':return [one([0,1],T=33.),one([20,21])]
    if profile!='extended':raise ValueError('profile must be smoke or extended')
    cases=[one(range(L+1),T=T) for L in (21,28,40,64) for T in (35.,39.,43.)]
    cases += [one(range(m,L+1),m=m) for m in (1,2) for L in (28,40)]
    cases += [one(range(29),nodes=n,tol=2e-12,step=.125) for n in (192,256)]
    return cases


def preflight(root=ROOT):
    root=Path(root)
    if sha(root/SOURCE)!=SOURCE_SHA:raise ValueError('original NPZ SHA mismatch')
    versions={n:importlib.metadata.version(n) for n in ('numpy','scipy','mpmath')}
    hashes={p:sha(root/p) for p in CODE}
    raw=json.dumps({'source':SOURCE_SHA,'code':hashes,'versions':versions,'python':sys.version},sort_keys=True).encode()
    try:
        head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):head=None
    return dict(schema='PHYS64_RUNTIME_V1',fingerprint=hashlib.sha256(raw).hexdigest(),
                source_sha256=SOURCE_SHA,code_sha256=hashes,versions=versions,
                python=sys.version,host=platform.node(),cpu_count=os.cpu_count(),
                platform=platform.platform(),git_head=head,
                execution_host='NCP_HOSTNAME_MATCH_REQUIRES_HARDWARE_REVIEW' if platform.node()=='s1a0e5abed09' else 'CURRENT_HOST_NOT_ASSERTED_NCP')


def case_key(spec,fingerprint):
    return hashlib.sha256(json.dumps({'spec':spec,'fingerprint':fingerprint},sort_keys=True,allow_nan=False).encode()).hexdigest()


def resumable(case_dir,key):
    case_dir=Path(case_dir)
    try:
        receipt=json.loads((case_dir/'SUCCESS.json').read_text())
        if receipt.get('key')!=key or receipt.get('status')!='NUMERICAL_CASE_COMPLETE':return False
        if len(receipt.get('payloads',{}))!=2:return False
        for rel,digest in receipt['payloads'].items():
            path=(case_dir/rel).resolve()
            if not path.is_relative_to(case_dir.resolve()) or sha(path)!=digest:return False
        return True
    except (OSError,ValueError,KeyError,TypeError):return False


def worker(request_path):
    import resource
    request=json.loads(Path(request_path).read_text())
    limit=request['memory_gib']*1024**3
    resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
    os.nice(10)
    from .phys64_born_hierarchy import solve_orders,summary,coefficient_quadrature
    import numpy as np
    root=Path(request['root']);runtime=preflight(root)
    if runtime['fingerprint']!=request['fingerprint']:raise ValueError('worker code/runtime identity changed')
    spec=request['spec'];spec['ells']=tuple(spec['ells'])
    result=solve_orders(root/SOURCE,**spec)
    data=summary(result)
    quadrature=coefficient_quadrature(result,2,80)
    residual=float(np.linalg.norm(quadrature-result['coefficients'][1])/max(np.linalg.norm(quadrature),1e-300))
    symmetry=max(t['transpose_symmetry_defect'] for t in data['terms'])
    if residual>2e-7 or symmetry>1e-10:raise ArithmeticError('independent coefficient/symmetry check failed')
    data.update(second_coefficient_quadrature_relative=residual,runtime=runtime,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    folder=Path(request_path).parent
    np.savez_compressed(folder/'COEFFICIENTS.npz',coefficients=result['coefficients'],contributions=result['contributions'])
    atomic_json(folder/'RESULT.json',data)


def run_case(root,out,spec,runtime,timeout,memory_gib,resume):
    key=case_key(spec,runtime['fingerprint']);case_dir=Path(out)/'cases'/key
    case_dir.mkdir(parents=True,exist_ok=True)
    if resume and resumable(case_dir,key):return dict(key=key,status='REUSED_VERIFIED',spec=spec)
    attempt=case_dir/('attempt_'+time.strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8])
    attempt.mkdir()
    request=dict(root=str(root),fingerprint=runtime['fingerprint'],spec=spec,memory_gib=memory_gib)
    atomic_json(attempt/'REQUEST.json',request)
    env=dict(os.environ)
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[name]='1'
    env['PYTHONPATH']=str(Path(root)/'src')
    cmd=[sys.executable,str(Path(root)/'scripts/phys64_ncp.py'),'--worker-request',str(attempt/'REQUEST.json')]
    started=time.perf_counter();error=None;code=None
    with (attempt/'stdout.txt').open('w') as stdout,(attempt/'stderr.txt').open('w') as stderr:
        try:code=subprocess.run(cmd,stdout=stdout,stderr=stderr,env=env,timeout=timeout,check=False).returncode
        except subprocess.TimeoutExpired:error='WALL_TIMEOUT'
    record=dict(key=key,spec=spec,exit_code=code,error=error,wall_seconds=time.perf_counter()-started,
                status='FAILED',attempt=str(attempt.relative_to(case_dir)))
    if code==0:
        payloads={str((attempt/n).relative_to(case_dir)):sha(attempt/n) for n in ('RESULT.json','COEFFICIENTS.npz')}
        record.update(status='NUMERICAL_CASE_COMPLETE',payloads=payloads)
        atomic_json(case_dir/'SUCCESS.json',record)
    atomic_json(attempt/'EXECUTION.json',record)
    return record


def pack(root,out):
    root=Path(root);out=Path(out);dest=out/'SOURCE_RESULTS.zip'
    payload=[(root/p,'source/'+p) for p in CODE+[SOURCE]]
    payload += [(p,'results/'+str(p.relative_to(out))) for p in sorted(out.rglob('*'))
                if p.is_file() and p.name not in ('SOURCE_RESULTS.zip','SHA256SUMS','.campaign.lock') and not p.name.endswith('.tmp')]
    manifest={name:sha(p) for p,name in payload}
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p,name in payload:z.write(p,name)
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise IOError('archive CRC failed')
        for name,digest in manifest.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=digest:raise IOError('archive payload mismatch')
    (out/'SHA256SUMS').write_text(sha(dest)+'  SOURCE_RESULTS.zip\n')
    return dict(archive=str(dest),sha256=sha(dest),entries=len(manifest),state='LOCAL_ARCHIVED_VERIFIED')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',choices=['smoke','extended'],default='smoke')
    p.add_argument('--out',type=Path,default=ROOT/'research/hh_phys64_20261018/ncp_results')
    p.add_argument('--workers',type=int,default=1)
    p.add_argument('--timeout',type=int,default=180)
    p.add_argument('--memory-gib',type=int,default=4)
    p.add_argument('--resume',action='store_true')
    p.add_argument('--preflight-only',action='store_true')
    p.add_argument('--worker-request',type=Path)
    a=p.parse_args(argv)
    if a.worker_request:worker(a.worker_request);return 0
    if not 1<=a.workers<=8 or not 30<=a.timeout<=900 or not 1<=a.memory_gib<=16:
        p.error('workers 1..8, timeout 30..900, memory-gib 1..16')
    if a.workers*a.memory_gib>32:p.error('aggregate declared VM budget exceeds 32 GiB')
    import fcntl
    import compileall
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    with (out/'.campaign.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        runtime=preflight()
        if not all(compileall.compile_file(str(ROOT/n),quiet=1) for n in CODE):raise RuntimeError('Python compilation failed')
        atomic_json(out/'PREFLIGHT.json',runtime)
        if a.preflight_only:print(json.dumps(runtime,indent=2));return 0
        specs=case_specs(a.profile)
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            jobs=[pool.submit(run_case,ROOT,out,s,runtime,a.timeout,a.memory_gib,a.resume) for s in specs]
            records=[job.result() for job in jobs]
        success=all(r['status'] in ('NUMERICAL_CASE_COMPLETE','REUSED_VERIFIED') for r in records)
        result=dict(schema='PHYS64_CAMPAIGN_V1',runtime=runtime,profile=a.profile,cases=records,
                    status='NUMERICAL_CASES_COMPLETE' if success else 'PARTIAL_FAILED',
                    all_angular_or_error_certificate=False,HH_R10='OFF',cloud_backup='NOT_ATTEMPTED_BY_RUNNER')
        atomic_json(out/'CAMPAIGN.json',result)
        archive=pack(ROOT,out)
        print(json.dumps(dict(status=result['status'],cases=len(records),archive=archive),indent=2))
        return 0 if success else 2

if __name__=='__main__':sys.exit(main())
