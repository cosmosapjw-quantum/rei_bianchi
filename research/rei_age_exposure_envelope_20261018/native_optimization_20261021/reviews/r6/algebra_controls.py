#!/usr/bin/env python3
"""Independent exact-arithmetic R6 controls; not a trajectory or proof by sampling."""
import json, math, random
from fractions import Fraction as F

eta=math.ulp(0.0)
rows=[]
n=10*eta; u=245*eta; q=24.5
assert F(q)*F(n)==F(u)
assert q*n==u
rows.append({"id":"N4_EXACT_ONE_ATOM", "status":"PASS", "n_bits":n.hex(), "u_bits":u.hex(), "q_bits":q.hex(), "exact_energy_residual_ticks":"0"})
n=10*eta; u=246*eta; q=u/n
assert q*n==u
residual=(F(q)*F(n)-F(u))/F(eta)
assert residual!=0
rows.append({"id":"ROUNDED_GATE_IS_NOT_REAL_MOMENT_EQUALITY", "status":"PASS", "q_bits":q.hex(), "rounded_energy_defect":0, "exact_energy_residual_ticks":str(residual)})
a,b=24.1,24.2; n=eta; u=24*eta
assert a*n==u==b*n
assert F(u)/F(n)<F(a)
rows.append({"id":"ROUNDED_ENDPOINT_CONE_IS_NOT_EXACT_CONE", "status":"PASS", "lo":a, "hi":b, "exact_mean":24, "rounded_endpoint_products_equal_u":True})
# f=x^2, mu=(delta_0+delta_2)/2, m=q=1: the C2 variance bound is sharp.
points=[(F(0),F(1,2)),(F(2),F(1,2))]
N=sum(w for x,w in points); m=sum(x*w for x,w in points)/N; q=m
lhs=abs(sum(w*x*x for x,w in points)-N*q*q)
rhs=abs(2*m)*N*abs(q-m)+N*(2-m)*(m-0)+N*(q-m)**2
assert lhs==rhs==1
rows.append({"id":"C2_ENDPOINT_VARIANCE_SHARPNESS", "status":"PASS", "lhs":str(lhs), "rhs":str(rhs)})
weights=[F(eta),F(2*eta),F(1),F(2)]
denoms=[F(1),F(1),F(2),F(4)]
Q=sum(weights); S=sum(w/d for w,d in zip(weights,denoms))
assert Q/max(denoms)<=S<=Q/min(denoms)
assert sum(w/F(1) for w in weights)==Q
rows.append({"id":"STORED_DENOMINATOR_BE_AND_ZERO_HAZARD", "status":"PASS", "positive_nodes":len(weights), "min_d":1, "max_d":4})
steps=[(F(5),F(6),F(3),F(13,4)),(F(13,4),F(13,4),F(13,16),F(3,4))]
product=F(1)
for before,Q,S,after in steps:
 kappa=Q/before; rho=after/S; d_eff=Q/S
 assert after/before==kappa*rho/d_eff
 product*=kappa*rho/d_eff
assert product==steps[-1][-1]/steps[0][0]==F(3,20)
rows.append({"id":"CUMULATIVE_EFFECTIVE_DENOMINATOR_WITH_RESIDUALS", "status":"PASS", "exact_ratio":str(product)})
rng=random.Random(20261021); c=29979245800.0; example=None
for i in range(64):
 dt=math.ldexp(1+rng.random(),rng.randrange(-30,31))
 opacity=math.ldexp(1+rng.random(),rng.randrange(-50,-10))
 original=1.0+(dt*c)*opacity
 reassociated=1.0+dt*(c*opacity)
 if original!=reassociated:
  example={"dt_hex":dt.hex(),"c_hex":c.hex(),"opacity_hex":opacity.hex(),"original_d_hex":original.hex(),"reassociated_d_hex":reassociated.hex(),"candidates_checked":i+1}
  break
assert example is not None
rows.append({"id":"DENOMINATOR_ASSOCIATION_CAN_CHANGE_STORED_VALUE", "status":"PASS", **example})
print(json.dumps({"status":"PASS", "controls":rows, "control_count":len(rows), "scope":"Exact arithmetic examples accompany independent symbolic derivations; no native trajectory."},indent=2))
