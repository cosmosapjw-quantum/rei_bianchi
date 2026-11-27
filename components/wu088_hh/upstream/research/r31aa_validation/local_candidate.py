from __future__ import annotations
import hashlib, math
from numbers import Real
from pathlib import Path
import numpy as np
from scipy.linalg import norm

EXPECTED='565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'


def _pos(x,name='value'):
    if isinstance(x,(bool,np.bool_)) or not isinstance(x,Real) or not math.isfinite(float(x)) or float(x)<=0:
        raise ValueError(name+' must be positive finite real')
    return float(x)


def _n2(x):
    a=np.asarray(x)
    return float(abs(a)) if a.ndim==0 else float(norm(a,2))


def _lin(a,b,u): return (1-u)*np.asarray(a)+u*np.asarray(b)


def cubic(v0,v1,d0,d1,h,u):
    h=_pos(h,'h');u=float(u)
    if not math.isfinite(u):raise ValueError('finite u required')
    h00=2*u**3-3*u**2+1; h10=u**3-2*u**2+u
    h01=-2*u**3+3*u**2; h11=u**3-u**2
    dh00=6*u*u-6*u; dh10=3*u*u-4*u+1
    dh01=-6*u*u+6*u; dh11=3*u*u-2*u
    val=h00*np.asarray(v0)+h*h10*np.asarray(d0)+h01*np.asarray(v1)+h*h11*np.asarray(d1)
    dot=(dh00*np.asarray(v0)+h*dh10*np.asarray(d0)+dh01*np.asarray(v1)+h*dh11*np.asarray(d1))/h
    return val,dot


def local_candidate(values,derivatives,ks,interval,s):
    if len(values)!=3 or len(derivatives)!=3 or len(ks)!=3:raise ValueError('three-node data required')
    T=_pos(interval,'interval');s=float(s)
    if not math.isfinite(s) or not 0<=s<=1:raise ValueError('s in [0,1] required')
    if s<=.5:
        i,j,u=0,1,2*s
    else:
        i,j,u=1,2,2*s-1
    O,dot=cubic(values[i],values[j],derivatives[i],derivatives[j],T/2,u)
    K=_lin(ks[i],ks[j],u)
    Dc=dot/2+K
    Dr=(dot/2-K).conj().T
    return O,dot,Dc,Dr,K


def connection_error_bounds(dot_error,dcol_error,drow_error):
    e=_pos(dot_error,'dot_error');a=_pos(dcol_error,'dcol_error');b=_pos(drow_error,'drow_error')
    lower=max(0.,a-e/2,b-e/2,abs(a-b)/2)
    upper=(a+b)/2
    return {'lower':lower,'upper':upper,'lower_over_dotO':lower/e,
            'connection_sector_dominates':bool(lower>e),
            'derivation':'DeltaDc=DeltaDot/2+DeltaK; DeltaDr^dagger=DeltaDot/2-DeltaK'}


def replay(path):
    p=Path(path);raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise ValueError('snapshot SHA mismatch')
    with np.load(p,allow_pickle=False) as f:d={k:f[k] for k in f.files}
    v=_pos(float(d['velocity']),'velocity');T=4/v
    O=[np.array(d['z0_od_O'],complex),np.array(d['direct_O'][:47,47:],complex),np.array(d['z4_od_O'],complex)]
    dot=[np.array(d['z0_j_dotO'],complex),np.array(d['direct_dotO'][:47,47:],complex),np.array(d['z4_j_dotO'],complex)]
    Dc=[np.array(d['z0_od_D_col'],complex),np.array(d['direct_D'][:47,47:],complex),np.array(d['z4_od_D_col'],complex)]
    Dr=[np.array(d['z0_od_D_row'],complex),np.array(d['direct_D'][47:,:47],complex),np.array(d['z4_od_D_row'],complex)]
    K=[(c-r.conj().T)/2 for c,r in zip(Dc,Dr)]
    eo=ed=ec=er=em=0.
    for i,s in enumerate((0.,.5,1.)):
        op,dp,cp,rp,kp=local_candidate(O,dot,K,T,s)
        eo=max(eo,_n2(op-O[i]));ed=max(ed,_n2(dp-dot[i]));ec=max(ec,_n2(cp-Dc[i]));er=max(er,_n2(rp-Dr[i]))
    for s in np.linspace(0,1,65):
        op,dp,cp,rp,kp=local_candidate(O,dot,K,T,float(s))
        em=max(em,_n2(dp-cp-rp.conj().T))
    b=connection_error_bounds(.07262393465956431,.3073893478614785,.3192667733603847)
    return {'schema':'WU088_R31AA_LOCAL_CANDIDATE_V1','input_sha256':EXPECTED,'interval_ta':T,
            'candidate':'PIECEWISE_CUBIC_HERMITE_O_PLUS_PIECEWISE_LINEAR_K',
            'max_O_node_error_2norm':eo,'max_dotO_node_error_2norm':ed,
            'max_D_col_node_error_2norm':ec,'max_D_row_node_error_2norm':er,
            'max_metric_identity_grid_2norm':em,'grid_probe_count':65,
            'z3_global_candidate_diagnosis':{'dotO_error':.07262393465956431,'D_col_error':.3073893478614785,'D_row_error':.3192667733603847,'K_error_bounds':b},
            'z3_status':'CONSUMED_DIAGNOSTIC_NOT_FUTURE_VALIDATION',
            'z1_status':'NEW_INDEPENDENT_VALIDATION_REQUIRED',
            'local_candidate_z3_comparison':'PENDING_NCP_EXISTING_ARCHIVE_REPLAY_POST_HOC_DIAGNOSTIC',
            'full_cell_bound':False,'physical_transition_error_bound':False,
            'native_evaluations':0,'new_heavy_scientific_nodes':0,'production_admitted':False,
            'input_unchanged':hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED}
