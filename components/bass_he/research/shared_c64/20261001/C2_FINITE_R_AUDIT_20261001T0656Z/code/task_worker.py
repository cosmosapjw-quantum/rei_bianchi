"""Bounded C2 prolate solve pair; scientific gates are evaluated separately."""
import argparse,hashlib,json,os,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'));sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--task-json',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--backend',choices=['native','reference'],required=True);a=ap.parse_args()
    raw=a.task_json.read_bytes();task=json.loads(raw);params=task['parameters']
    if set(params)!={'R','configuration','tail','operators'}:raise ValueError('unexpected C2 task parameters')
    import numpy as np
    from spheroidal_tail import solve,SpheroidalConfig
    from state_io import pair_bytes
    import prolate_fast as fast
    from coupling import invariants
    from mpi_batch import backend_identity
    selected=backend_identity(a.backend)
    cfg=SpheroidalConfig(**params['configuration']);R=params['R'];edges=None
    if params['tail']:
        # Exact original inner knot calculation, followed by an outer extension.
        edges=np.r_[1+(60/R)*np.linspace(0,1,65)**2,1+(2/R)*np.linspace(30,40,17)[1:]]
    start=time.perf_counter();g=solve(R,m=0,config=cfg,radial_edges=edges);b=solve(R,m=1,config=cfg,radial_edges=edges)
    eig_seconds=time.perf_counter()-start
    for s in (g,b):
        if not np.isfinite(s.radial_coefficients).all() or not np.isfinite(s.angular_coefficients).all():raise ArithmeticError('nonfinite state')
        if max(s.residuals['radial_discrete_relative'],s.residuals['angular_discrete_relative'])>1e-9:raise ArithmeticError('discrete residual gate failed')
    state=a.output_dir/'STATE.npz';atomic_create(state,pair_bytes((g,b)))
    ops={}
    if params['operators']:
        backend='native' if a.backend=='native' else 'python'
        ops['direct']={str(q):fast.direct(g,b,q,backend=backend) for q in (16,24)}
        ops['torque']={str(q):fast.torque(g,b,q,backend=backend) for q in (20,28)}
        ops['dark']={str(n):fast.dark(g,b,24,phi_nodes=n,backend=backend) for n in (32,64)}
        ops['invariants']=invariants(g,b,ops['direct']['24'],ops['torque']['28'])
    files={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for sub in ('code','reference') for f in (ROOT/sub).glob('*.py')}
    result={'status':'PASS','task_id':task['task_id'],'input_sha256':hashlib.sha256(raw).hexdigest(),'parameters':params,'backend':a.backend,'energies':[g.energy,b.energy],'states':[g.metadata(),b.metadata()],'operators':ops,'metadata':{'native_library':selected if a.backend=='native' else None},'elapsed_seconds':time.perf_counter()-start,'eigensolve_seconds':eig_seconds,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'state_file':state.name,'state_bytes':state.stat().st_size,'state_sha256':hashlib.sha256(state.read_bytes()).hexdigest(),'code_sha256':files,'claim_scope':'execution PASS only; finite-grid scientific gates pending'}
    atomic_create(a.output_dir/'RESULT.json',json_bytes(result));print(json.dumps({'task_id':task['task_id'],'energies':result['energies'],'seconds':result['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
