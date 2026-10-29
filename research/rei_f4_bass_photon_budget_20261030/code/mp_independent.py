"""Independent 75-digit primal/dual reconstructed from stored binary64 8x71 LP.
Not a directed enclosure of underlying real atomic cross-section fit parameters.
"""
import numpy as np
import mpmath as mp
from . import budget_cone as bc
mp.mp.dps=75

def val(x):
    a,b=float(x).as_integer_ratio()
    return mp.mpf(a)/mp.mpf(b)

def certify(z,net,E,M,sigma):
    target=bc.sw.target_six(z);N,W,_=bc.budgets(net,E,z)
    A,b=bc.constraints(E,M,target,N,W)
    c=np.asarray(sigma[13])*bc.sw.FLUX_UNIT/bc.RATE_SCALE
    proofs=[]
    for kind in ('min','max'):
        got=bc.solve(A,b,c,kind); active=got['active']; sign=1 if kind=='min' else -1
        B=mp.matrix([[val(A[i,j]) for j in active] for i in range(8)])
        rhs=mp.matrix([val(k) for k in b]); cbase=mp.matrix([val(sign*c[j]) for j in active])
        primal=mp.lu_solve(B,rhs);dual=mp.lu_solve(B.T,cbase)
        res=max(abs(v) for v in B*primal-rhs)
        dual_violation=max(sum(val(A[i,j])*dual[i] for i in range(8))-val(sign*c[j]) for j in range(71))
        dual_gap=abs(sum(val(sign*c[active[k]])*primal[k] for k in range(8))-sum(dual[i]*rhs[i] for i in range(8)))
        min_flux=min(primal)
        if min_flux<=0 or res>mp.mpf('1e-60') or dual_gap>mp.mpf('1e-60') or dual_violation>mp.mpf('1e-40'):
            raise AssertionError(f'NOT_CERTIFIED_{z}_{kind}: {mp.nstr(min_flux,9)} {mp.nstr(res,9)} {mp.nstr(dual_gap,9)} {mp.nstr(dual_violation,9)}')
        gamma=sum(val(c[active[k]])*primal[k] for k in range(8))*val(bc.RATE_SCALE)
        proofs.append({'kind':kind,'gamma_liI_s_75':mp.nstr(gamma,55),
            'max_primal_residual_75':str(res),'max_dual_slack_75':str(dual_violation),
            'primal_dual_gap_75':str(dual_gap),'smallest_active_bin':str(min_flux),
            'active_bin_index':active})
    return {'z':z,'certificates':proofs}

def run():
    net,E,M,sigma,rows=bc.inputs()
    return [certify(float(row['z']),net,E,M,sigma) for row in rows]
