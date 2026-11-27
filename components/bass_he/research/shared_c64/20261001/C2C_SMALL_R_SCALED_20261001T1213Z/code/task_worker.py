"""One preregistered C2c scientific task, isolated by the MPI resource wrapper."""
import argparse,hashlib,json,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code'),str(ROOT/'reference')]
from mpi_batch import atomic_create,json_bytes,code_identity,backend_identity

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def load_pair_reference(ref):
    from state_io import load_pair
    folder=(ROOT/ref['folder']).resolve()
    if not folder.is_relative_to(ROOT.resolve()):raise ValueError('state path outside package')
    result=folder/'RESULT.json'
    if result.is_symlink() or sha(result)!=ref['result_sha256']:raise RuntimeError('INPUT_RESULT_IDENTITY_MISMATCH')
    meta=json.loads(result.read_bytes());state=folder/meta['state_file']
    if state.name!='STATE.npz' or state.is_symlink() or state.stat().st_size!=meta['state_bytes'] or sha(state)!=meta['state_sha256'] or sha(state)!=ref['state_sha256']:
        raise RuntimeError('INPUT_STATE_IDENTITY_MISMATCH')
    if meta['status']!='PASS':raise RuntimeError('INPUT_EXECUTION_NOT_PASS')
    return load_pair(state)

def operators(g,b,direct_orders,force_orders,backend):
    import direct_stream,force_integral
    return {'direct':{str(q):direct_stream.direct(g,b,q,backend=backend) for q in direct_orders},
            'force':{str(q):force_integral.torque(g,b,q,backend=backend) for q in force_orders}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--task-json',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--backend',choices=['native','reference'],required=True);args=ap.parse_args()
    task_raw=args.task_json.read_bytes();task=json.loads(task_raw);p=task['parameters'];c=json.loads((ROOT/'CONTRACT.json').read_bytes())
    identity=code_identity();native=backend_identity(args.backend);backend='native' if args.backend=='native' else 'python'
    start=time.perf_counter();newstates=0;state_meta={}
    if p['kind']=='prolate':
        import numpy as np
        from spheroidal_tail import solve,SpheroidalConfig
        from state_io import pair_bytes
        import direct_stream
        cfg=p['configuration'];profile=p['profile'];tier=p['tier'];R=p['R']
        if R not in c['new_R'] or tier not in (0,1) or cfg!=c['profiles' if tier==0 else 'fallback_profiles'][profile]:raise ValueError('unregistered prolate configuration')
        edges=None
        if profile=='tail':
            n=64 if tier==0 else 128;k=16 if tier==0 else 32
            edges=np.r_[1+(60/R)*np.linspace(0,1,n+1)**2,1+(2/R)*np.linspace(30,40,k+1)[1:]]
        pair=tuple(solve(R,m=m,config=SpheroidalConfig(**cfg),radial_edges=edges) for m in (0,1));newstates=2
        for s in pair:
            if not np.isfinite(s.radial_coefficients).all() or not np.isfinite(s.angular_coefficients).all():raise ArithmeticError('nonfinite eigenstate')
            if max(s.residuals['radial_discrete_relative'],s.residuals['angular_discrete_relative'])>c['raw_criteria']['algebraic_residual_relative']:raise ArithmeticError('discrete residual failed')
        eig_seconds=time.perf_counter()-start
        path=args.output_dir/'STATE.npz';atomic_create(path,pair_bytes(pair))
        state_meta={'state_file':path.name,'state_bytes':path.stat().st_size,'state_sha256':sha(path)}
        value={'R':R,'energies':[s.energy for s in pair],'states':[s.metadata() for s in pair],
               'eigensolve_seconds':eig_seconds,**operators(*pair,c['operators']['direct_orders'],c['operators']['force_orders'],backend)}
        value['dark']={str(n):direct_stream.dark(*pair,c['operators']['dark_order'],phi_nodes=n,backend=backend) for n in c['operators']['phi_nodes']}
    elif p['kind']=='sphere':
        from sphere_adapter import solve_one
        cfg=p['configuration'];allowed=list(c['spherical_anchor']['configurations'].values())+list(c['spherical_anchor']['fallback_configurations'].values())
        if cfg.get('m') not in (0,1) or {k:v for k,v in cfg.items() if k!='m'} not in allowed:raise ValueError('unregistered spherical configuration')
        value=solve_one(cfg,args.output_dir,backend='native' if args.backend=='native' else 'numpy');newstates=1
        state_meta={k:value[k] for k in ('state_file','state_bytes','state_sha256')}
    elif p['kind']=='operator_refinement':
        pair=load_pair_reference(p['state'])
        if p['direct_orders'] not in ([],c['operators']['fallback_direct_orders']) or p['force_orders'] not in ([],c['operators']['fallback_force_orders']):raise ValueError('unregistered quadrature fallback')
        value={'R':pair[0].R,**operators(*pair,p['direct_orders'],p['force_orders'],backend)}
    elif p['kind']=='overlap':
        from overlap_integral import pair_overlap
        left=load_pair_reference(p['left']);right=load_pair_reference(p['right']);m=p['sector']
        if [left[0].R,right[0].R] not in c['continuation']['edges'] or m not in (0,1) or p['order'] not in c['continuation']['orders']+c['continuation']['fallback_orders']:raise ValueError('unregistered edge')
        value=pair_overlap(left[m],right[m],p['order'],backend=backend)
    elif p['kind']=='sphere_observe':
        from sphere_adapter import observe_pair
        for ref in (p['left'],p['right']):
            folder=(ROOT/ref['folder']).resolve()
            if not folder.is_relative_to(ROOT.resolve()) or sha(folder/'RESULT.json')!=ref['result_sha256'] or sha(folder/'STATE.npz')!=ref['state_sha256']:raise RuntimeError('SPHERICAL_REFERENCE_IDENTITY_MISMATCH')
        if p['orders'] not in (c['spherical_anchor']['operator_orders'],c['spherical_anchor']['fallback_operator_orders']):raise ValueError('unregistered spherical operator orders')
        value=observe_pair(ROOT/p['left']['folder'],ROOT/p['right']['folder'],orders=p['orders'])
    elif p['kind']=='parity':
        import direct_stream,force_integral
        case=p['case']
        if case not in c['parity_cases']:raise ValueError('unregistered parity case')
        if case['kind']=='overlap':
            from overlap_integral import pair_overlap
            l=load_pair_reference(p['left']);rr=load_pair_reference(p['right'])
            value=pair_overlap(l[case['sector']],rr[case['sector']],case['order'],backend='python')
        else:
            pair=load_pair_reference(p['state'])
            if pair[0].R!=case['R']:raise ValueError('parity R mismatch')
            if case['kind']=='direct':value=direct_stream.direct(*pair,case['order'],backend='native' if case['R']==.25 else 'python')
            else:value=force_integral.torque(*pair,case['order'],backend='python')
    else:raise ValueError('unregistered task kind')
    data={'task_id':task['task_id'],'parameters':p,'value':value,'new_eigenstates':newstates}
    path=args.output_dir/'DATA.json';atomic_create(path,json_bytes(data))
    if code_identity()!=identity or backend_identity(args.backend)!=native:raise RuntimeError('SOURCE_OR_NATIVE_CHANGED_DURING_TASK')
    result={'status':'PASS','task_id':task['task_id'],'input_sha256':hashlib.sha256(task_raw).hexdigest(),'parameters':p,
            'backend':args.backend,'selected_backend':native,'code_identity_sha256':identity['sha256'],
            'evidence_file':'DATA.json','evidence_bytes':path.stat().st_size,'evidence_sha256':sha(path),
            'elapsed_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'new_eigenstates':newstates,'claim_scope':'execution PASS only; raw/scaled scientific gates separately evaluated',**state_meta}
    atomic_create(args.output_dir/'RESULT.json',json_bytes(result));print(json.dumps({'task_id':task['task_id'],'seconds':result['elapsed_seconds'],'new_eigenstates':newstates}),flush=True)

if __name__=='__main__':main()
