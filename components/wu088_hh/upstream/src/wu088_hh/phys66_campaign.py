"""PHYS66 direct-current-host long-tail campaign; no SSH, no old NCP reruns.

Each case runs in a separate bounded process. Resume binds source, all
implementation bytes, numerical config and runtime; two result files must
match their recorded hashes. Certificate components remain separate from
uncertified integration/roundoff/omitted angular errors.
"""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,importlib.metadata,json,os
from pathlib import Path
import platform,subprocess,sys,time,uuid,zipfile
from .phys66_radial_budget import certificate,to_jsonable
ROOT=Path(__file__).resolve().parents[2]
SOURCE='research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz'
CODE=['src/wu088_hh/'+s+'.py' for s in ('phys63_lap_contract','phys63_scaled_riccati',
      'phys64_born_hierarchy','phys65_exterior_bounds','phys66_radial_budget',
      'phys66_endpoint','phys66_campaign')]+['scripts/phys66_ncp.py']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def atomic_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(to_jsonable(data),indent=2,sort_keys=True,allow_nan=False)+'\n')
    os.replace(temp,path)

def case_specs(profile):
    def one(ells,T):return dict(ells=list(ells),m=0,outer=float(T),join=39.,
                               orders=3,nodes=128,rtol=2e-11,max_step=.25)
    if profile=='smoke':return [one((0,1),45),one((20,21),55)]
    if profile=='longtail':return [one(range(L+1),T) for L in (28,64) for T in (55,65,75)]
    raise ValueError('profile smoke or longtail only; old extended18 is not a profile')

def preflight(root=ROOT):
    root=Path(root);c=certificate(root/SOURCE,64,'65',3)
    versions={n:importlib.metadata.version(n) for n in ('numpy','scipy','mpmath')}
    hashes={p:sha(root/p) for p in CODE}
    raw=json.dumps({'source':c['source_sha256'],'code':hashes,'versions':versions,'python':sys.version},sort_keys=True).encode()
    try:head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):head=None
    return dict(schema='PHYS66_RUNTIME_V1',fingerprint=hashlib.sha256(raw).hexdigest(),
                source_sha256=c['source_sha256'],code_sha256=hashes,versions=versions,
                python=sys.version,host=platform.node(),cpu_count=os.cpu_count(),
                platform=platform.platform(),git_head=head,
                host_label='NCP_HOSTNAME_REQUIRES_HARDWARE_CONFIRMATION' if platform.node()=='s1a0e5abed09' else 'NOT_ASSERTED_NCP')

def case_key(spec,fingerprint):
    return hashlib.sha256(json.dumps({'spec':spec,'fingerprint':fingerprint},sort_keys=True,allow_nan=False).encode()).hexdigest()

def resumable(folder,key):
    folder=Path(folder)
    try:
        r=json.loads((folder/'SUCCESS.json').read_text())
        if r['key']!=key or r['status']!='NUMERICAL_CASE_COMPLETE' or r['exit_code']!=0:return False
        payload=r['payloads']
        if len(payload)!=2:return False
        for rel,h in payload.items():
            path=(folder/rel).resolve()
            if not path.is_relative_to(folder.resolve()) or sha(path)!=h:return False
        return True
    except (ValueError,KeyError,TypeError,OSError):return False

def worker(request_file):
    import resource,numpy as np
    from .phys66_endpoint import solve_endpoint
    from .phys64_born_hierarchy import summary,coefficient_quadrature
    req=json.loads(Path(request_file).read_text())
    limit=req['memory_gib']*1024**3
    resource.setrlimit(resource.RLIMIT_AS,(limit,limit));os.nice(10)
    runtime=preflight(req['root'])
    if runtime['fingerprint']!=req['fingerprint']:raise ValueError('worker fingerprint changed')
    spec=dict(req['spec']);spec['ells']=tuple(spec['ells'])
    result=solve_endpoint(Path(req['root'])/SOURCE,**spec)
    data=summary(result);q=coefficient_quadrature(result,2,128)
    residual=float(np.linalg.norm(q-result['coefficients'][1])/max(np.linalg.norm(q),1e-300))
    symmetry=max(t['transpose_symmetry_defect'] for t in data['terms'])
    if residual>2e-7 or symmetry>1e-10:raise ArithmeticError('coefficient/symmetry diagnostic failed')
    data.update(join=result['join'],runtime=runtime,second_coefficient_quadrature_relative=residual,
                analytic_radial_components=result['analytic_radial_components'],
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                total_error_certified=False,HH_R10='OFF')
    folder=Path(request_file).parent
    np.savez_compressed(folder/'COEFFICIENTS.npz',coefficients=result['coefficients'],
                        contributions=result['contributions'],join_state=result['join_state'])
    atomic_json(folder/'RESULT.json',data)

def run_case(root,out,spec,runtime,timeout,memory_gib,resume):
    key=case_key(spec,runtime['fingerprint']);folder=Path(out)/'cases'/key;folder.mkdir(parents=True,exist_ok=True)
    if resume and resumable(folder,key):return dict(key=key,status='REUSED_VERIFIED',spec=spec)
    attempt=folder/('attempt_'+time.strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:8]);attempt.mkdir()
    atomic_json(attempt/'REQUEST.json',dict(root=str(root),fingerprint=runtime['fingerprint'],spec=spec,memory_gib=memory_gib))
    env=dict(os.environ,PYTHONPATH=str(Path(root)/'src'))
    for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[n]='1'
    cmd=[sys.executable,str(Path(root)/'scripts/phys66_ncp.py'),'--worker-request',str(attempt/'REQUEST.json')]
    begin=time.perf_counter();rc=None;error=None
    with (attempt/'stdout.txt').open('w') as stdout,(attempt/'stderr.txt').open('w') as stderr:
        try:rc=subprocess.run(cmd,stdout=stdout,stderr=stderr,env=env,timeout=timeout,check=False).returncode
        except subprocess.TimeoutExpired:error='WALL_TIMEOUT'
    r=dict(key=key,spec=spec,status='FAILED',exit_code=rc,error=error,
           wall_seconds=time.perf_counter()-begin,attempt=attempt.name)
    if rc==0:
        r.update(status='NUMERICAL_CASE_COMPLETE',payloads={str((attempt/n).relative_to(folder)):sha(attempt/n) for n in ('RESULT.json','COEFFICIENTS.npz')})
        atomic_json(folder/'SUCCESS.json',r)
    atomic_json(attempt/'EXECUTION.json',r)
    return r

def pack(root,out):
    root=Path(root);out=Path(out);dest=out/'SOURCE_RESULTS.zip'
    payload=[(root/n,'source/'+n) for n in CODE+[SOURCE]]
    payload += [(p,'results/'+str(p.relative_to(out))) for p in sorted(out.rglob('*'))
                if p.is_file() and p.name not in ('SOURCE_RESULTS.zip','SHA256SUMS','.campaign.lock') and not p.name.endswith('.tmp')]
    manifest={n:sha(p) for p,n in payload}
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p,n in payload:z.write(p,n)
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise IOError('archive CRC')
        for n,h in manifest.items():
            if hashlib.sha256(z.read(n)).hexdigest()!=h:raise IOError('archive content hash')
    (out/'SHA256SUMS').write_text(sha(dest)+'  SOURCE_RESULTS.zip\n')
    return dict(archive=str(dest),sha256=sha(dest),manifest_payloads=len(manifest),status='LOCAL_ARCHIVED_VERIFIED')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',choices=['smoke','longtail'],default='smoke')
    p.add_argument('--out',type=Path,default=ROOT/'research/hh_phys66_20261018/ncp_run')
    p.add_argument('--workers',type=int,default=2);p.add_argument('--memory-gib',type=int,default=4)
    p.add_argument('--timeout',type=int,default=180);p.add_argument('--resume',action='store_true')
    p.add_argument('--preflight-only',action='store_true');p.add_argument('--worker-request',type=Path)
    a=p.parse_args(argv)
    if a.worker_request:worker(a.worker_request);return 0
    if not 1<=a.workers<=8 or not 1<=a.memory_gib<=16 or not 30<=a.timeout<=900:
        p.error('workers1..8 memory1..16GiB timeout30..900s')
    if a.workers*a.memory_gib>32:p.error('aggregate VM limit32GiB')
    import fcntl,py_compile
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    with (out/'.campaign.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        runtime=preflight()
        for path in CODE:py_compile.compile(str(ROOT/path),doraise=True)
        atomic_json(out/'PREFLIGHT.json',runtime)
        if a.preflight_only:print(json.dumps(runtime,indent=2));return 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            jobs=[pool.submit(run_case,ROOT,out,s,runtime,a.timeout,a.memory_gib,a.resume) for s in case_specs(a.profile)]
            records=[job.result() for job in jobs]
        ok=all(r['status'] in ('NUMERICAL_CASE_COMPLETE','REUSED_VERIFIED') for r in records)
        campaign=dict(schema='PHYS66_CAMPAIGN_V1',runtime=runtime,profile=a.profile,cases=records,
             new_case_count=sum(r['status']=='NUMERICAL_CASE_COMPLETE' for r in records),
             reused_count=sum(r['status']=='REUSED_VERIFIED' for r in records),
             status='NUMERICAL_CASES_COMPLETE' if ok else 'PARTIAL_FAILED',
             total_numerical_error_certified=False,HH_R10='OFF')
        atomic_json(out/('CAMPAIGN_'+a.profile+'.json'),campaign)
        archive=pack(ROOT,out)
        print(json.dumps(dict(status=campaign['status'],new=campaign['new_case_count'],reused=campaign['reused_count'],archive=archive),indent=2))
        return 0 if ok else 2
if __name__=='__main__':sys.exit(main())
