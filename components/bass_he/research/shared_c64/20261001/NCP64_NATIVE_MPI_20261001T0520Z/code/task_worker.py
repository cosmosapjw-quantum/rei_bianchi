"""One isolated eigenstate task. MPI orchestration owns task/process budgets."""
import argparse,hashlib,json,os,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
sys.path.insert(0,str(ROOT/'code'))

def atomic_json(path, value):
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    try:os.link(temp,path)
    finally:temp.unlink()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--task-json',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--backend',choices=['native','reference','numpy'],required=True);a=ap.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    target=a.output_dir/'RESULT.json'
    if target.exists():raise FileExistsError(target)
    raw=a.task_json.read_bytes();task=json.loads(raw)
    # Import after environment is frozen by the launcher. No backend fallback.
    import numpy as np
    if a.backend=='reference':
        import partialwave_centered as solver
        call={}
    else:
        import optimized_solver as solver
        call={'backend':a.backend}
    start=time.perf_counter();g=solver.solve(**task['parameters'],**call)
    if (not np.isfinite([g.energy,g.residual,g.mass_norm]).all()
            or not np.isfinite(g.coefficients).all()
            or g.residual>1e-9 or abs(g.mass_norm-1)>1e-10):
        raise ArithmeticError('fixed norm/residual acceptance failed')
    states=a.output_dir/'STATE.npz'
    with states.open('xb') as f:
        np.savez_compressed(f,coefficients=g.coefficients,ls=g.ls,boundaries=g.boundaries)
        f.flush();os.fsync(f.fileno())
    files={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for sub in ['code','reference'] for f in (ROOT/sub).glob('*.py')}
    result={'status':'PASS','task_id':task['task_id'],'input_sha256':hashlib.sha256(raw).hexdigest(),'parameters':task['parameters'],'backend':a.backend,'energy':g.energy,'residual':g.residual,'mass_norm':g.mass_norm,'metadata':g.metadata,'elapsed_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'state_file':states.name,'state_bytes':states.stat().st_size,'state_sha256':hashlib.sha256(states.read_bytes()).hexdigest(),'code_sha256':files,'threads':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},'native_identity':g.metadata.get('native_library'),'claim_scope':'implementation/performance task; no continuum certificate or new C2 closure'}
    atomic_json(target,result)
    print(json.dumps({'task_id':task['task_id'],'status':'PASS','energy':g.energy,'seconds':result['elapsed_seconds']}))
if __name__=='__main__':main()
