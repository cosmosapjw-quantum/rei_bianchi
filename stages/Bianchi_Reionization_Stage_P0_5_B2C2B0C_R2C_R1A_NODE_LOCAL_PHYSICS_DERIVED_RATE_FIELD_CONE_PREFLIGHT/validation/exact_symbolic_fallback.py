#!/usr/bin/env python3
from __future__ import annotations
import json
from decimal import Decimal, getcontext
from pathlib import Path
import sympy as sp
import mpmath as mp

getcontext().prec = 90
n, dt, q, r, u, t = sp.symbols('n dt q r u t', positive=True)
x0 = sp.symbols('x0', nonnegative=True)
A = sp.Matrix([[-u, r], [u, -r]])
Cdt = n/dt + r
Cref = q*n/dt + r
checks = {
    'column_conservation': sp.simplify(sp.ones(1,2)*A) == sp.zeros(1,2),
    'metzler_offdiagonal': bool(A[0,1] == r and A[1,0] == u),
    'capacity_refinement_identity': sp.simplify(Cref-Cdt-(q-1)*n/dt) == 0,
    'integrated_budget_identity': sp.simplify(dt*Cdt-(n+dt*r)) == 0,
    'common_equilibrium_extrapolation_symbolic': sp.simplify((1/(1-sp.exp(-u*dt))-1) - sp.exp(-u*dt)/(1-sp.exp(-u*dt))) == 0,
    'common_equilibrium_extrapolation_positive': sp.simplify(1/(1-sp.exp(-u*dt))-1 - 1/(sp.exp(u*dt)-1)) == 0,
}
# High-precision numerical replay of the worst q=8 covariance row.
N = Decimal('6.859678e65') * (Decimal(1)-Decimal('0.992193'))
DT = Decimal('11.726292') * Decimal('1000000') * Decimal('365.25') * Decimal('86400')
R = Decimal('2.427755e50')
C1 = N/DT + R
C8 = Decimal(8)*N/DT + R
num = {
    'C1': str(C1), 'C8': str(C8),
    'identity_residual': str((C8-C1)-Decimal(7)*N/DT),
    'relative_change': str((C8-C1)/C1),
}
mp.mp.dps=100
u0=mp.mpf('0.3'); r0=mp.mpf('0.1'); t0=mp.mpf('2.0'); e=mp.e**(-(u0+r0)*t0)
P=[[ (r0+u0*e)/(u0+r0), r0*(1-e)/(u0+r0)], [u0*(1-e)/(u0+r0), (u0+r0*e)/(u0+r0)]]
mp_checks={
 'gamma_3_over_2': abs(mp.gamma(mp.mpf('1.5'))-mp.sqrt(mp.pi)/2) < mp.mpf('1e-95'),
 'positive_semigroup_entries': all(v>=0 for row in P for v in row),
 'semigroup_column_sums': max(abs(P[0][j]+P[1][j]-1) for j in range(2)) < mp.mpf('1e-95'),
 'equilibrium_multiplier_gt_one': 1/(1-mp.e**(-mp.mpf('0.7'))) > 1,
}
result = {'classification':'R2C_R1A_EXACT_SYMBOLIC_FALLBACK','checks':checks,'numeric_90_digit':num,'mpmath_100_digit':{**mp_checks,'max_column_sum_residual':str(max(abs(P[0][j]+P[1][j]-1) for j in range(2)))},'pass':all(checks.values()) and all(mp_checks.values()) and Decimal(num['identity_residual'])==0}
out = Path(__file__).resolve().parents[1]/'data'/'exact_symbolic_fallback_report.json'
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(0 if result['pass'] else 1)
