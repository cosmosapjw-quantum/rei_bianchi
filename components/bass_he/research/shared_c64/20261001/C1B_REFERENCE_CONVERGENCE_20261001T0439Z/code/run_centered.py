"""One R=2 centered pair per create-only invocation; identities and state bytes saved."""
import os,sys,time,json,resource,argparse,io
from pathlib import Path
import numpy as np
import scipy
import partialwave_centered as pw
from force_projected import torque_observables
from evidence_io import atomic_json,atomic_bytes,sha256
ROOT=Path(__file__).resolve().parents[1]
from parent_inputs import resolve_parent
PARENT=resolve_parent(ROOT)

def save_state(path,s):
    data=io.BytesIO()
    np.savez_compressed(data,ls=s.ls,boundaries=s.boundaries,coefficients=s.coefficients)
    atomic_bytes(path,data.getvalue())
    return {'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'bytes':path.stat().st_size}

def load_pair(tag):
    x=json.loads((ROOT/f'evidence/{tag}.json').read_text());states=[]
    if x['identities']['code_sha256']['partialwave_centered.py']!=sha256(pw.__file__):
        raise ValueError('cached solver identity mismatch')
    if x['config']['R']!=2 or x['config']['center']!='B' or len(x['states'])!=2:
        raise ValueError('incompatible cached physical configuration')
    for m,r in enumerate(x['states']):
        array=ROOT/r['array_file']['path']
        if array.stat().st_size!=r['array_file']['bytes'] or sha256(array)!=r['array_file']['sha256']:
            raise ValueError('cached state byte identity mismatch')
        if r['metadata']['origin_center']!='B' or r['metadata']['nuclear_positions']!=[-2.,0.]:
            raise ValueError('incompatible cached origin')
        with np.load(array,allow_pickle=False) as z:
            if z['boundaries'][-1]!=x['config']['rmax']:
                raise ValueError('cached outer boundary mismatch')
            states.append(pw.PartialWaveState(2.,1.,2.,m,z['ls'],z['boundaries'],x['config']['degree'],z['coefficients'],r['energy'],r['residual'],r['mass_norm'],r['phase_probe'],r['metadata']))
    return states

def run(tag,lmax,elements=56,degree=4,rmax=24.,quadrature=14,tail_base=None):
    out=ROOT/f'evidence/{tag}.json'
    if out.exists() or any((ROOT/f'evidence/{tag}_m{m}.npz').exists() for m in (0,1)):
        raise FileExistsError('existing evidence retained')
    start=time.perf_counter();boundaries=None
    if tail_base:
        states=load_pair(tail_base)
        boundaries=np.r_[states[0].boundaries,np.linspace(states[0].boundaries[-1],rmax,9)[1:]]
    cfg={'R':2.,'lmax':lmax,'elements':elements,'degree':degree,'rmax':rmax,'quadrature':quadrature,'center':'B','nroots':2}
    states=[pw.solve(m=m,boundaries=boundaries,**cfg) for m in (0,1)]
    g,b=states
    d=pw.direct_observables(g,b,quadrature=14)
    dq=pw.direct_observables(g,b,quadrature=22)
    tq=[torque_observables(g,b,quadrature=q) for q in (14,22,30)]
    gap=b.energy-g.energy;target=json.loads((PARENT/'evidence/C1_SINGLE_POINT_PILOT.json').read_text())['spheroidal'][-1]
    inv={'direct_torque_O_abs':abs(dq['L_O_over_minus_i_hbar']-tq[-1]['L_O_bar']),
         'direct_torque_B_abs':abs(dq['L_center_over_minus_i_hbar']-tq[-1]['L_B_bar']),
         'momentum_commutator_abs':abs(dq['p_x_over_minus_i_hbar']-gap*dq['dipole_x']),
         'momentum_force_abs':abs(dq['p_x_over_minus_i_hbar']-tq[-1]['p_x_force_bar']),
         'force_q22_to30_abs':abs(tq[1]['L_O_bar']-tq[2]['L_O_bar']),
         'force_q14_to22_abs':abs(tq[0]['L_O_bar']-tq[1]['L_O_bar']),
         'direct_q14_to22_abs':abs(d['L_O_over_minus_i_hbar']-dq['L_O_over_minus_i_hbar'])}
    ss=[]
    for m,s in enumerate(states):
        array=save_state(ROOT/f'evidence/{tag}_m{m}.npz',s)
        ss.append({'energy':s.energy,'residual':s.residual,'mass_norm':s.mass_norm,'phase_probe':s.phase_probe,'metadata':s.metadata,'array_file':array})
    x={'tag':tag,'config':cfg,'tail_base':tail_base,'states':ss,'direct':dq,'torque':tq[-1],'invariants':inv,
       'vs_C1_prolate':{'energy_abs':[abs(s.energy-target[k]['energy']) for s,k in zip(states,('g','b'))],
                       'L_O_abs':abs(dq['L_O_over_minus_i_hbar']-target['direct']['L_O_bar'])},
       'elapsed_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'identities':{'contract_sha256':sha256(ROOT/'NUMERICAL_CONTRACT.json'),'force_contract_sha256':sha256(ROOT/'FORCE_IMPLEMENTATION_CONTRACT.json'),
                     'code_sha256':{n:sha256(Path(__file__).parent/n) for n in ('partialwave_centered.py','force_projected.py','run_centered.py','evidence_io.py')}},
       'runtime':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},
       'certificate':'EMPIRICAL_DISCRETIZATION_EVIDENCE; no continuum enclosure'}
    atomic_json(out,x)
    print(json.dumps({k:x[k] for k in ('tag','config','direct','torque','invariants','vs_C1_prolate','elapsed_seconds','max_rss_kib')}),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('tag');ap.add_argument('--lmax',type=int,required=True);ap.add_argument('--elements',type=int,default=56);ap.add_argument('--degree',type=int,default=4);ap.add_argument('--rmax',type=float,default=24);ap.add_argument('--quadrature',type=int,default=14);ap.add_argument('--tail-base')
    args=ap.parse_args();resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    run(**vars(args))
