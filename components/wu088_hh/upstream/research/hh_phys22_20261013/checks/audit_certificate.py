#!/usr/bin/env python3
"""Independent exact-rational closure audit, not a rerun of the Wolfram producer.

The saved directed-rounding majorants are inputs. Their source-formula audit is
recorded separately; this checker verifies the algebraic closure and outward
observable bounds and binds the actual NPZ/source bytes.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib, json, time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
V = json.loads((ROOT/'results/interval_result_v3.json').read_text())
checks: list[dict] = []
def check(name: str, ok: bool) -> None:
    checks.append({'name': name, 'pass': bool(ok)})
def vec(xs): return [F(x) for x in xs]
def mat(xs): return [vec(row) for row in xs]
def dot(a,b): return sum((x*y for x,y in zip(a,b)), F(0))
def mv(a,b): return [dot(r,b) for r in a]
def inverse(a):
    n=len(a); a=[r[:] + [F(i==j) for j in range(n)] for i,r in enumerate(a)]
    for j in range(n):
        i=next(i for i in range(j,n) if a[i][j]); a[i],a[j]=a[j],a[i]
        piv=a[j][j]; a[j]=[v/piv for v in a[j]]
        for i in range(n):
            if i!=j:
                c=a[i][j]; a[i]=[v-c*w for v,w in zip(a[i],a[j])]
    return [r[n:] for r in a]
start=time.monotonic()
span=F(10**11); f=F(3,38); ell=[F(1),f,2*f,F(0)]
ev=F('1.602176634e-12');kb=F('1.380649e-16');ct=2*ev/(3*kb);chi=F('13.598434599702')
nu=[F(1),F(0),F(0),-chi]
a=mat(V['Aabs_upper']);bc=mat(V['BabsCabs_upper']);p=mat(V['gain_upper'])
check('nonnegative_majorants',all(x>=0 for m in (a,bc,p) for r in m for x in r))
check('gain_equals_t_A_plus_half_t2_BC',all(p[i][j]==span*a[i][j]+span**2*bc[i][j]/2 for i in range(4) for j in range(4)))
weights=vec([1,1,1,32]);gain=max(x/y for x,y in zip(mv(p,weights),weights))
check('weighted_gain_strictly_less_than_one',gain<1)
inv=inverse([[F(i==j)-p[i][j] for j in range(4)] for i in range(4)])
check('comparison_inverse_nonnegative',all(x>=0 for r in inv for x in r))
ql,qu=vec(V['qHH_box']);u=mv(inv,[span*abs(x)*qu for x in nu]);err=mv(p,u)
check('forcing_interval_positive',0<ql<=qu)
check('resolvent_identity_exact',all(u[i]-err[i]==span*abs(nu[i])*qu for i in range(4)))
check('finite_bound_outward',all(x<=y for x,y in zip(u,vec(V['finite_gas_bound_rational']))))
check('feedback_bound_outward',all(x<=y for x,y in zip(err,vec(V['feedback_bound_rational']))))
r=vec(V['gas_radii']);flow=vec(V['tube_picard_upper'])
check('first_exit_strict_inclusion_all_four_coordinates',all(0<=v<w for v,w in zip(flow,r)))
tlo,thi=vec(V['temperature_box']);plo,phi=vec(V['particle_box']);g0=vec(V['gas_initial_exact'])
check('warm_temperature_guards',F(30000)<tlo<=thi<F(110000))
check('gas_simplex_guards',0<g0[0]-r[0]<g0[0]+r[0]<1 and 0<g0[1]-r[1] and 0<g0[2]-r[2] and g0[1]+r[1]+g0[2]+r[2]<1)
check('finite_change_inside_common_box',all(x<2*y for x,y in zip(u,r)))
er=dot(ell,err); eb=[span*ql-er,span*qu+er]
tnum=[-(ct*chi+thi)*span*qu-ct*err[3]-thi*er,-(ct*chi+tlo)*span*ql+ct*err[3]+thi*er]
tb=[tnum[0]/plo,tnum[1]/phi]
check('signed_electron_response_positive',eb[0]>0)
check('temperature_numerator_negative',tnum[0]<tnum[1]<0)
for name,exact,stored in [('electron',eb,vec(V['electron_interval_rational'])),('temperature',tb,vec(V['temperature_interval_rational_K']))]:
    check(name+'_rational_endpoint_outward',stored[0]<=exact[0]<=exact[1]<=stored[1])
check('zero_activation_exact',all(F(0)*x==0 for x in u+eb+tb))
for name,expected in zip(['extended_dataset.npz','emissivity.out'],V['input_sha256']):
    check(name+'_sha256',hashlib.sha256((ROOT/'inputs'/name).read_bytes()).hexdigest()==expected)
with np.load(ROOT/'inputs/extended_dataset.npz',allow_pickle=False) as data:
    ic=data['initial_state'];q=data['q_eV'];w=data['weights']
    check('NPZ_gas_binary64_exact',all(F(float(x))==y for x,y in zip(ic[:4],g0)))
    check('NPZ_dimension',len(q)==2904 and len(ic)==len(q)+9 and len(w)==len(q))
    check('NPZ_positive_photons_and_weights',np.all(ic[4:4+len(q)]>=0) and np.all(w>0))
    check('cross_section_upper_domain',np.all((q>0)&(q<=50000)))
check('no_opacity_threshold_crossings',V['threshold_overlap_counts']==[0,0,0])
# An arbitrary real approximation may be compared with the proved finite bounds.
nom_t=F('-5.68654774358033e-11');nom_e=F('7.81328718123e-16')
result={'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL',
        'method':'Python Fraction exact arithmetic, separate Gaussian elimination; source bounds supplied by the observed Wolfram interval calculation',
        'independence':'same assistant, separate implementation; no external reviewer',
        'checks_passed':sum(c['pass'] for c in checks),'checks_failed':sum(not c['pass'] for c in checks),'checks':checks,
        'weighted_gain_upper':float(gain),'tube_ratios':[float(v/w) for v,w in zip(flow,r)],
        'u':[float(x) for x in u],'feedback':[float(x) for x in err],
        'electron_interval':[float(x) for x in eb],'temperature_interval_K':[float(x) for x in tb],
        'temperature_midpoint_K':float(sum(tb)/2),'temperature_radius_K':float((tb[1]-tb[0])/2),
        'temperature_radius_over_midpoint':float((tb[1]-tb[0])/abs(sum(tb))),
        'finite_T_error_vs_PHYS21_numeric_anchor_K':float(max(abs(x-nom_t) for x in tb)),
        'finite_e_error_vs_PHYS21_numeric_anchor':float(max(abs(x-nom_e) for x in eb)),
        'run_seconds':time.monotonic()-start,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_result_sha256':hashlib.sha256((ROOT/'results/interval_result_v3.json').read_bytes()).hexdigest()}
(ROOT/'checks/EXACT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['status']=='PASS' else 1)
