"""Independent mp sign+Laplace-positivity check; does not import implementation."""
from pathlib import Path
import json, mpmath as mp
mp.mp.dps=85
root=Path(__file__).resolve().parents[1]
s=json.loads((root/'sources/GL2022_R18_EXACT_ROW.json').read_text())
r=json.loads((root/'results/CONDITIONAL_THRESHOLD_BOUND.json').read_text())
T=[mp.mpf(x) for x in s['rates']['temperature_K']]
q=[]
for token in s['rates']['printed_tokens']:
 a,b=token.split('(');q.append(mp.mpf(a)*mp.power(10,-int(b[:-1])))
kB=mp.mpf('1.380649e-23')/mp.mpf('1.602176634e-19')*1000
beta=[1/(kB*t) for t in T]
logf=[mp.log(x)-mp.mpf('1.5')*mp.log(z) for x,z in zip(q,beta)]
sec=[(logf[i+1]-logf[i])/(beta[i]-beta[i+1]) for i in range(9)]
claimed=[mp.mpf(v) for v in r['adjacent_theta_upper_meV']]
res=max(abs(x-y) for x,y in zip(sec,claimed))
qphysical=-mp.mpf(s['spectroscopic_external_Q_meV'])
ratio=mp.exp(-(qphysical-sec[0])*(beta[0]-beta[1]))
assert res<mp.mpf('1e-65'),res
assert abs(1/ratio-mp.mpf(r['nominal_15K_to_max_ratio']))<mp.mpf('1e-65')
print(json.dumps({'independent_algorithm':'mpmath log k - 3/2 log beta, no implementation imports',
                  'dps':85,'max_abs_secant_difference_meV':mp.nstr(res,19),
                  'tightest_bound_meV':mp.nstr(sec[0],22),
                  'nominal_to_max_lowT_ratio':mp.nstr(1/ratio,22),
                  'max_pair_sample_count':9,'science':'CONDITIONAL_ONLY'},indent=2))
