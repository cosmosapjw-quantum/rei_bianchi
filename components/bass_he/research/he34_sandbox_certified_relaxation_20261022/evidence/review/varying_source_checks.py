"""Two new sign-changing controls for the implementation, no saved background.

Independent full two-eigenpressure Radau reference, segmented at knots.
Sampling corroborates the analytic continuum derivation, not its proof.
"""
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import solve_ivp

sys.dont_write_bytecode=True
UNIT=Path('/tmp/he32_resume_20261022/repos/BASS_HE/research/he34_sandbox_certified_relaxation_20261022')
sys.path.insert(0,str(UNIT/'src'))
from certified_relaxation import solve_reduced

rows=[]
for case in [dict(N=[0.,.07,.19,.4],S=[.12,-.04,.18,-.09],chi=60.,r0=.12),
             dict(N=[0.,.025,.12,.3],S=[-.06,.11,-.08,.015],chi=3000.,r0=-.2)]:
    N,S,chi,r0=case['N'],case['S'],case['chi'],case['r0']
    actual=solve_reduced(N,S,chi,r0=r0)
    assert actual.certificate_valid and actual.approximation_valid and actual.quadrature_converged
    state=np.array([1-r0,1+2*r0])
    dr=[];du=[];ratio_margins=[];u_margins=[];nfev=0;residual_fractions=[]
    for j,(left,right,sa,sb) in enumerate(zip(N[:-1],N[1:],S[:-1],S[1:])):
        h=right-left;slope=(sb-sa)/h
        def operator(t):
            s=sa+slope*t
            return np.array([[2*s-chi/3,chi/3],[2*chi/3,-4*s-2*chi/3]])
        ref=solve_ivp(lambda t,w:operator(t)@w,(0,h),state,method='Radau',
                      jac=lambda t,w:operator(t),rtol=3e-12,atol=3e-14,dense_output=True)
        assert ref.success
        tau=np.unique(np.r_[np.linspace(0,h,17),min(.25/chi,h),min(1/chi,h),min(4/chi,h)])
        full=ref.sol(tau);p=(2*full[0]+full[1])/3
        rref=(full[1]-full[0])/(3*p);uref=np.log(p)
        dense=actual.evaluate(left+tau)
        e_r=np.abs(rref-dense.r);e_u=np.abs(uref-dense.u)
        assert np.all(e_r<=dense.ratio_error_bound+5e-11)
        assert np.all(e_u<=dense.logp_error_bound+dense.quadrature_error_estimate+dense.omitted_layer_tail_bound+5e-11)
        dr.extend(e_r.tolist());du.extend(e_u.tolist())
        ratio_margins.extend((dense.ratio_error_bound-e_r).tolist())
        u_margins.extend((dense.logp_error_bound-e_u).tolist())
        rec=actual.intervals[j]
        for t in tau:
            s=sa+slope*t;D=math.sqrt(chi*chi+4*chi*s+36*s*s)
            b=-4*s/(chi+2*s+D)
            layer=rec.delta0*math.exp(-rec.D0*t)/(1-rec.c*(1-math.exp(-rec.D0*t)))
            bprime=(4*b*b-2*b-2)*slope/D
            rho=bprime+(D-rec.D0)*layer+4*(sa-s)*layer*layer
            residual_fractions.append(abs(rho)/rec.residual_bound)
        state=ref.y[:,-1];nfev+=ref.nfev
    assert max(residual_fractions)<=1+1e-12
    rows.append(dict(**case,sampled_points=len(dr),max_ratio_error=max(dr),max_logp_error=max(du),
                     min_bound_minus_ratio_error=min(ratio_margins),min_bound_minus_logp_error=min(u_margins),
                     max_sampled_residual_over_analytic_bound=max(residual_fractions),reference_nfev=nfev,
                     cone_methods=[r.cone_method for r in actual.intervals],
                     certificate_valid=actual.certificate_valid,certified=actual.certified))
out=dict(unit='HE34-SCR',source_sha256=hashlib.sha256((UNIT/'src/certified_relaxation.py').read_bytes()).hexdigest(),
         reference='Independent full two-eigenpressure Radau, rtol3e-12/atol3e-14, knot segmented',
         cases=rows,old_HE32_background_runs=0,old_HE33_suite_runs=0,
         qualification='Finite sampling corroborates the separately reviewed analytic continuum inequalities.')
Path('/tmp/he34_scope_review/VARYING_SOURCE_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
