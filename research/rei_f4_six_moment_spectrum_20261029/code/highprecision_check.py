"""Independent exact-binary64-as-rational 75-digit primal/dual check."""
from __future__ import annotations
import mpmath as mp
import numpy as np
from scipy.optimize import linprog
from . import spectral_witness as sw
mp.mp.dps=75

def exact(x):
    num,den=float(x).as_integer_ratio()
    return mp.mpf(num)/mp.mpf(den)

def validate():
    net=sw.parent.new_native_network()
    e,M,s=sw.six_moment_matrix(net)
    rows=sw.parent.json.loads((sw.parent.SRC/'REI_SAVED7.json').read_text())['rows']
    out=[]
    for row in rows:
        target=sw.target_six(float(row['z']))
        A=M*(sw.FLUX_UNIT/target[:,None]);c=s[13]*sw.FLUX_UNIT/1e-13
        lp=linprog(c,A_eq=A,b_eq=np.ones(6),bounds=(0,None),method='highs')
        active=np.flatnonzero(lp.x>1e-9)
        if not lp.success or len(active)!=6:raise ValueError('LP_NONBASIC_OR_FAIL')
        B=mp.matrix(6,6)
        for i in range(6):
            for j,k in enumerate(active):B[i,j]=exact(A[i,k])
        x=mp.lu_solve(B,mp.matrix([1]*6))
        dual=mp.lu_solve(B.T,mp.matrix([exact(c[k]) for k in active]))
        prime=max(abs(y-1) for y in B*x)
        minphi=min(x)
        dual_slacks=[sum(exact(A[i,j])*dual[i] for i in range(6))-exact(c[j]) for j in range(A.shape[1])]
        largest_violation=max(dual_slacks)
        objective_primal=sum(exact(c[active[j]])*x[j] for j in range(6))
        objective_dual=sum(dual)
        result=dict(z=float(row['z']),primal_mp_max_residual=str(prime),
                    active_min_bin_unit_flux_mp=str(minphi),
                    worst_dual_slack_mp=str(largest_violation),
                    duality_gap_mp=str(objective_primal-objective_dual),
                    liI_min_rate_s=str(objective_primal*mp.mpf('1e-13')))
        if prime>mp.mpf('1e-60') or minphi<=0 or largest_violation>mp.mpf('1e-45') or abs(objective_primal-objective_dual)>mp.mpf('1e-60'):
            raise AssertionError('MP75_EXACT_BINARY64_LP_CERTIFICATE_FAILED '+str(result))
        out.append(result)
    return out
