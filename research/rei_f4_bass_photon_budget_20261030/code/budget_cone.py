"""Conditional finite 8-moment photon budget LP on frozen BASS photon grid.

No IVP; no claim the hypothetical P19-compatible source is BASS's original
power-law spectrum or is a source-qualified radiation transfer solution.
"""
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from . import spectral_witness as sw

ROOT=Path(__file__).resolve().parents[1]
PIN='8cb59a51e2d7c26ccb4589c0fbd723fa0bbd315db2405e7c9c576a165214b783'
RATE_SCALE=1e-13  # s^-1

def inputs():
    sw.parent.source_manifest_check()
    assert hashlib.sha256((ROOT/'source/PR270_IMMUTABLE_FULL.zip').read_bytes()).hexdigest()==PIN
    net=sw.parent.new_native_network()
    E,M,sigma=sw.six_moment_matrix(net)
    assert M.shape==(6,71)
    rows=json.loads((ROOT/'source/REI_SAVED7.json').read_text())['rows']
    return net,E,M,sigma,rows

def budgets(net,E,z):
    _,uv=sw.parent.original_bass_bath_at_z(z)
    phi=np.asarray(net.photon_flux_bins_base)*uv
    return float(phi.sum()),float(phi@E),phi

def constraints(E,M,targets,N,W):
    if not all([N>0,W>0,np.all(np.isfinite(targets)),np.all(targets>0)]):
        raise ValueError('INVALID_POSITIVE_BUDGET')
    A=np.vstack([M*(sw.FLUX_UNIT/targets[:,None]),
         np.ones((1,len(E)))*(sw.FLUX_UNIT/N),
         E[None,:]*(sw.FLUX_UNIT/W)])
    assert A.shape==(8,71)
    return A,np.ones(8)

def solve(A,b,c,kind):
    sign={'min':1,'max':-1}[kind]
    result=linprog(sign*c,A_eq=A,b_eq=b,bounds=(0,None),method='highs',
            options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    if not result.success:raise ArithmeticError(f'NO_BUDGET_WITNESS_{kind}:{result.message}')
    x=np.asarray(result.x)
    active=np.flatnonzero(x>1e-9)
    residual=np.max(abs(A@x-b)); dualgap=abs(result.fun-result.eqlin.marginals@b)
    dualslack=max(A.T@result.eqlin.marginals-sign*c)
    if len(active)!=8 or min(x)<-1e-12 or residual>2e-9 or dualslack>1e-8 or dualgap>1e-8:
        raise ArithmeticError((kind,active,residual,dualslack,dualgap))
    return {'gamma_s':float(c@x*RATE_SCALE),'active':active.tolist(),
            'flux_active_m2_s':(x[active]*sw.FLUX_UNIT).tolist(),
            'scaled_primal_residual':float(residual),
            'scaled_dual_gap':float(dualgap),'scaled_dual_violation':float(dualslack)}

def solve_at_z(z,net,E,M,sigma):
    t=sw.target_six(float(z));N,W,orig=budgets(net,E,z)
    A,b=constraints(E,M,t,N,W)
    c=np.asarray(sigma[13])*sw.FLUX_UNIT/RATE_SCALE
    low=solve(A,b,c,'min');high=solve(A,b,c,'max')
    if not low['gamma_s']<high['gamma_s']:raise ArithmeticError('INVALID_LI_ORDER')
    return {'z':float(z),'original_BASS_N_m2_s':N,'original_BASS_W_eV_m2_s':W,
        'original_BASS_LiI_rate_s':float(orig@sigma[13]),
        'P19_six_targets':t.tolist(),'unconstrained_min_N_m2_s':sw.nonnegative_witness(M,t)['flux_total'],
        'LiI_min':low,'LiI_max':high,'feasible':True}

def run():
    net,E,M,sigma,rows=inputs()
    result=[solve_at_z(row['z'],net,E,M,sigma) for row in rows]
    return {'schema':'REI_F4_BASS_PHOTON_BUDGET_V1','source_PR270_SHA256':PIN,
         'interpretation':'conditional original BASS scalar number/energy flux budgets, NOT original spectral shape or P19 true budget',
         'N_constraints':8,'N_bins':71,'new_IVPs':0,'working':'33/88','central':'28/88','physical_fast':'4/7','cases':result}
