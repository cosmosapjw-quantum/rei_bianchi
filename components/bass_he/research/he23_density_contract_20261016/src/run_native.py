"""Bounded HE22 NCP native H/He runs. Refuses to substitute fake physics.

This script was NOT executed against the original Rust provider in ChatGPT.
Each case is independently checkpointed. A failure is retained as evidence.
"""
import argparse, hashlib, itertools, json, os, pathlib, sys, time
from concurrent.futures import ProcessPoolExecutor

from he21_photo import temperature
from he22_coupled import run_coupled
from he22_native_client import NativeRustPoint, NativeDensityProvider, OWNER_SOURCE_SHA


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def run_case(args):
    binary,m,steps,q,timeout_s,evidence_dir,source_sha = args
    start=time.perf_counter()
    class Native:
        def __init__(self):
            self.calls=[]
            self.provider=NativeDensityProvider(binary,source_sha,evidence_dir=evidence_dir)
        def density(self,a,x):return self.provider(a,x).nh
        def make(self,a,x):
            import math
            instance=NativeRustPoint(binary,a,self.density(a,x),timeout_s=timeout_s,evidence_dir=evidence_dir)
            self.calls.append(instance)
            return instance
    adapter=Native()
    r=run_coupled(adapter.make,m=int(m),steps=int(steps),q=float(q),density_provider=adapter.density)
    if (r['max_support_crossing']!=0 or abs(r['number_defect'])>3e-15 or
        abs(r['energy_defect'])>3e-12 or
        max(abs(v) for v in r['chemical_species_defect'])>3e-12 or
        any(v < 0 for v in r['absorbed']) or not (r['gas_final'][3]>0)):
        raise AssertionError('HE22_GATE_FAIL: '+str((m,steps,q,r)))
    r.update(temperature_final_K=temperature(r['gas_final']),elapsed_s=time.perf_counter()-start,
             native_subprocess_count=sum(i.calls for i in adapter.calls),
             owner_source_evidence='one original Rust native eval per residual')
    return r


def atomic_json(path,record):
    if path.exists():raise FileExistsError('HE23_CREATE_ONLY: '+str(path))
    tmp=path.with_suffix('.partial')
    with open(tmp,'w',encoding='utf-8') as f:
        json.dump(record,f,indent=2,sort_keys=True,allow_nan=False)
        f.flush();os.fsync(f.fileno())
    os.link(tmp,path);tmp.unlink()
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--binary',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--stage',choices=['pilot','matrix'],required=True)
    ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--max-case-wall-s',type=float,default=300.)
    ap.add_argument('--source-sha',required=True,help='exact original rei_bianchi SHA pinned at build')
    a=ap.parse_args()
    if not (pathlib.Path(a.binary).is_file() and a.workers>=1 and 0<a.max_case_wall_s<=3600):
        raise ValueError('HE22_NCP_PRECHECK')
    out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise FileExistsError('HE23_OUTPUT_NOT_EMPTY')
    if a.source_sha!=OWNER_SOURCE_SHA:raise ValueError('HE23_OWNER_SOURCE_MISMATCH')
    # Runtime source identity is captured before dispatch, independent of branch movement.
    source_dir=pathlib.Path(__file__).resolve().parent
    identity={'owner_source_commit':a.source_sha,'native_binary_sha256':digest(a.binary),
              'python_version':sys.version,'source_files':{
                  p.name:digest(p) for p in sorted(source_dir.iterdir())
                  if p.is_file() and p.suffix in ('.py','.rs')}}
    atomic_json(out/'EXECUTION_IDENTITY.json',identity)
    cases=([(4,2,0.)] if a.stage=='pilot' else
           list(itertools.product([4,8],[2,4],[-.005,0.,.005])))
    # Limit stage to a finite, isolated number of original Rust evaluations.
    jobs=[(str(pathlib.Path(a.binary).resolve()),m,steps,q,20.,str(out/f'raw_q{q:+.4f}_m{m}_n{steps}'),a.source_sha) for m,steps,q in cases]
    import time
    started=time.monotonic()
    receipts=[]
    workers=min(a.workers,len(jobs))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(run_case,j) for j in jobs]
        for idx,(j,future) in enumerate(zip(jobs,futures)):
            name=f'q{j[3]:+.4f}_m{j[1]}_n{j[2]}'
            try:
                r=future.result(timeout=a.max_case_wall_s)
                status={'status':'NUMERICALLY_CHECKED_NATIVE_PROVIDER_NOT_GLOBAL',
                        'case':name,'result':r}
            except Exception as exc:
                status={'status':'HOLD_FIRST_FAILURE','case':name,
                        'exception_type':type(exc).__name__,'exception':str(exc),'traceback':__import__('traceback').format_exc()}
            atomic_json(out/(name+'.json'),status)
            receipts.append(status)
            if status['status']=='HOLD_FIRST_FAILURE':
                # No silent repeated retries or continuation after first bad physical case.
                break
    final={'schema':'bass_he.he23.native.casea.v1','stage':a.stage,
           'source_commit':a.source_sha,'native_binary_sha256':digest(a.binary),
           'record_count':len(receipts),'requested_cases':len(cases),
           'execution_identity_sha256':digest(out/'EXECUTION_IDENTITY.json'),
           'all_pass':all(x['status'].startswith('NUMERICALLY') for x in receipts)
                      and len(receipts)==len(cases),
           'runtime_s':time.monotonic()-started,
           'model_scope':('HE21 prescribed source; original native cold Case A point micro, '
                          'not the time-calibrated FLRW/Bianchi or observational history'),
           'scientific_admission':'HOLD_FULL_EOR_AND_OBSERVER_CMB'}
    atomic_json(out/'SUMMARY.json',final)
    print(json.dumps(final,indent=2))
    if not final['all_pass']:sys.exit(1)

if __name__=='__main__':main()
