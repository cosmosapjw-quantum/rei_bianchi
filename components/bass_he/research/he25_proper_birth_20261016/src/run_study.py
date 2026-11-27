"""Create-only bounded HE25 runs; no full Cartesian product or silent replay."""
import sys,os,json,time,hashlib,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from native import NativeOwner
from physics import Model
from transport import solve_transport
BINARY='/root/HE25_NCP_BIRTH_20261016/build/he25_owner_server'

def atomic(path,obj):
    path=Path(path);temp=path.with_suffix(path.suffix+'.partial')
    with temp.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
    os.link(temp,path);temp.unlink();fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

def run_case(args):
    root,q,m,n,angles=args;out=Path(root)/f'q{q:+.4f}_m{m}_n{n}_a{angles}';out.mkdir(exist_ok=False)
    src=Path(__file__).parent
    identity={'source':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(src.glob('*')) if p.is_file()},
              'binary_sha256':hashlib.sha256(Path(BINARY).read_bytes()).hexdigest(),
              'owner_source':'f7830e2f55e7a1938bc3c98f61b60651f8dae474','q':q,'m':m,'n':n,'angles':angles}
    atomic(out/'IDENTITY.json',identity)
    try:
        with NativeOwner(BINARY,evidence_path=out/'native.jsonl.gz') as owner:
            model=Model(owner,m=m,angles=angles,q=q)
            result=solve_transport(model,n=n,cohort_path=out/'birth_cohorts.npz')
        rec={'status':'NATIVE_VERIFIED_SCOPED','result':result}
    except Exception as exc:rec={'status':'HOLD_FIRST_FAILURE','error':str(exc),'traceback':traceback.format_exc()}
    atomic(out/'RESULT.json',rec)
    return dict(case=out.name,**rec)

def run_cases(out,cases,workers=2):
    out=Path(out);out.mkdir(exist_ok=False)
    atomic(out/'DESIGN.json',{'cases':cases,'workers':workers,'temporal_budget_K':1e-8,'gas_fraction_budget':1e-11,
          'reference_stability_budget_K':1e-9,'note':'budgets for this conditional short interval; not EoR certification'})
    start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(run_case,(str(out),*c)) for c in cases]
        records=[]
        for f in futures:
            r=f.result(timeout=1200);records.append(r)
    atomic(out/'SUMMARY.json',{'elapsed_s':time.perf_counter()-start,'case_count':len(records),
                               'all_pass':all(r['status'].startswith('NATIVE') for r in records)})
    return records
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--mode',choices=['pilot','temporal','resolution'],required=True);a=p.parse_args()
    if a.mode=='pilot':cases=[(0.,4,16,4)]
    elif a.mode=='temporal':cases=[(0.,4,n,4) for n in [32,64,128,256]]
    else:
        cases=[(q,4,128,ang) for q in [-.005,.005] for ang in [4,8,16,32]]+[(0.,m,128,4) for m in [8,16]]
    print(json.dumps(run_cases(a.out,cases,workers=2),indent=2))
