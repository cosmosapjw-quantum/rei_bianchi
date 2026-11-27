"""Targeted independent code checks against the pre-existing 80-digit oracle.

Writes only this review directory. Does not import or run old scientific suites.
"""
import hashlib
import json
from pathlib import Path
import sys
import mpmath as mp

sys.dont_write_bytecode=True
UNIT=Path('/tmp/he32_resume_20261022/repos/BASS_HE/research/he34_sandbox_certified_relaxation_20261022')
sys.path.insert(0,str(UNIT/'src'))
import certified_relaxation as cr
import neutral_transport as nt

mp.mp.dps=80
rows=[]
cases=[(0.,3.,1.,.4),(.3,10.,-.5,.1),(-.8,.1,.4,.7),(.25,100.,.9,1.),(1e-20,1.,0.,2.),(.4,1e8,.8,.1)]
for s,chi,r0,h in cases:
    actual=cr.solve_reduced([0.,h],[s,s],chi,r0=r0)
    ss,cc,rr,hh=map(mp.mpf,(s,chi,r0,h))
    matrix=mp.matrix([[2*ss-cc/3,cc/3],[2*cc/3,-4*ss-2*cc/3]])
    state=mp.expm(hh*matrix)*mp.matrix([1-rr,1+2*rr])
    pressure=(2*state[0]+state[1])/3
    ratio=(state[1]-state[0])/(3*pressure)
    logp=mp.log(pressure)
    er=abs(mp.mpf(actual.r[-1])-ratio)
    eu=abs(mp.mpf(actual.u[-1])-logp)
    assert actual.approximation_valid
    assert er<mp.mpf('1e-14') and eu<mp.mpf('1e-14')
    rows.append(dict(S=s,chi=chi,r0=r0,h=h,ratio_abs_error=str(er),logp_abs_error=str(eu),
                     status=actual.status,quadrature_converged=actual.quadrature_converged))

data=json.loads((UNIT/'data/NEUTRAL_H_HE_TRANSPORT_SUBSET.json').read_text())
transport=[]
for row in data['fits']:
    a=list(map(lambda x:mp.mpf(str(x)),row['coefficients']))
    for T in (50.,300.,20000.,50000.):
        z=mp.log(T); e1=mp.exp((z-a[2])/a[3]);e2=mp.exp((z-a[5])/a[6])
        expected=mp.pi*mp.mpf('1e-20')*((a[0]+a[1]*z)*e1/(e1+1/e1)+a[4]*e2/(e2+1/e2))
        actual=nt.collision_integral(T,row['pair'],row['kind'])
        err=abs(mp.mpf(actual)/expected-1)
        assert err<mp.mpf('5e-14')
        transport.append(dict(pair=row['pair'],kind=row['kind'],T_K=T,relative_error=str(err)))

result={'unit':'HE34-SCR','reviewer_role':'independent physics and math-code review',
        'source_sha256':{p:hashlib.sha256((UNIT/p).read_bytes()).hexdigest() for p in ('src/certified_relaxation.py','src/neutral_transport.py')},
        'constant_candidate_vs_80digit_independent_matrix':rows,
        'collision_integral_vs_80digit_direct_source_formula':transport,
        'old_background_runs':0,'old_HE33_suite_runs':0}
Path('/tmp/he34_scope_review/IMPLEMENTATION_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
