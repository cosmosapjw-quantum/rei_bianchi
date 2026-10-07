"""Independent standard-library audit of frozen benchmark CSV and analytic oracle.

Does not run a PDE solver, change states, or introduce spatial resolutions.
This audit evaluates saved tables only; it does not integrate a history.
"""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
oracle = json.loads((ROOT / 'oracle.json').read_text())
epochs = {float(e['s']): e for e in oracle['epochs']}
rows = [{k: v if k == 'method' else float(v) for k, v in r.items()}
        for r in csv.DictReader((ROOT / 'results.csv').open())]
groups = defaultdict(list)
for row in rows:
    groups[(row['method'], int(row['n']), row['cfl'])].append(row)
assert len(rows) == 234 and len(groups) == 26
assert all([r['s'] for r in rs] == list(epochs) for rs in groups.values())
assert all(math.isfinite(v) for r in rows for k, v in r.items()
           if k not in ('method', 'min_density', 'L1_GL8', 'L1_GL16', 'stock_min_weight'))
U0 = float(oracle['U0'])

def simpson(f, a, b, tol=2e-13):
    if b <= a:
        return 0.0
    def rec(a, b, fa, fm, fb, old, eps, depth):
        m = (a+b)/2
        lm, rm = (a+m)/2, (m+b)/2
        fl, fr = f(lm), f(rm)
        left = (m-a)*(fa+4*fl+fm)/6
        right = (b-m)*(fm+4*fr+fb)/6
        change = left+right-old
        if abs(change) <= 15*eps or depth == 0:
            return left+right+change/15
        return rec(a,m,fa,fl,fm,left,eps/2,depth-1)+rec(m,b,fm,fr,fb,right,eps/2,depth-1)
    m = (a+b)/2
    fa, fm, fb = f(a), f(m), f(b)
    return rec(a,b,fa,fm,fb,(b-a)*(fa+4*fm+fb)/6,tol,25)

def raw(x):
    z = (x-.65)/.25
    return math.exp(-1/(1-z*z)) if abs(z)<1 else 0.0

C = 1/simpson(raw,.4,.9)
oracle_disagreement = {'normalization': abs(C-float(oracle['normalization']))}
for s, e in epochs.items():
    lo, hi = max(.4,s), min(.9,s)
    n = C*simpson(raw,lo,.9)
    no = C*simpson(raw,.4,hi)
    u = 13.6*math.exp(-s)*C*simpson(lambda x: math.exp(x)*raw(x),lo,.9)
    # Integrate trajectory losses directly, independently of N/U/ledger residual.
    w = 13.6*C*(simpson(lambda x: math.expm1(x)*raw(x),.4,hi)
          -math.expm1(-s)*simpson(lambda x: math.exp(x)*raw(x),lo,.9))
    oracle_disagreement[str(s)] = {k: abs(v-float(e[k])) for k,v in
                                  [('N',n),('Nout',no),('U',u),('Eout',13.6*no),('W',w)]}

summary = []
max_record_mismatch = 0.0
max_bin_mass_mismatch = 0.0
max_crossing_energy_mismatch = 0.0
limiter_mismatch = 0.0
for (method,n,cfl), rs in groups.items():
    nres, epre, epost, binerr, noerr, eoerr = [], [], [], [], [], []
    quadabs, quadrel = [], []
    for r in rs:
        nr = (r['N']+r['Nout']-r['N0'])/r['N0']
        ep = (r['U']+r['Eout']+r['W']-r['U0_pre'])/r['U0_pre']
        ea = (r['U']+r['Eout']+r['W']-r['U0_post'])/r['U0_post']
        max_record_mismatch = max(max_record_mismatch,abs(nr-r['Nres']),abs(ep-r['Eres_pre']),abs(ea-r['Eres_post']))
        nres.append(abs(nr)); epre.append(abs(ep)); epost.append(abs(ea))
        e = epochs[r['s']]
        binerr.append(math.fsum(abs(r[f'bin{j}']-float(e['bins'][j])) for j in range(32)))
        noerr.append(abs(r['Nout']-float(e['Nout'])))
        eoerr.append(abs(r['Eout']-float(e['Eout']))/U0)
        max_bin_mass_mismatch = max(max_bin_mass_mismatch,abs(math.fsum(r[f'bin{j}'] for j in range(32))-r['N']))
        max_crossing_energy_mismatch = max(max_crossing_energy_mismatch,abs(r['Eout']-13.6*r['Nout'])/U0)
        if method == 'dg_limited':
            limiter_mismatch = max(limiter_mismatch,abs(ep-(r['initial_du']+r['stage_du'])/r['U0_pre']),abs(ea-r['stage_du']/r['U0_post']))
        if method != 'stock':
            qabs = abs(r['L1_GL16']-r['L1_GL8'])
            quadabs.append(qabs)
            quadrel.append(qabs/max(abs(r['L1_GL16']),1e-12))
    summary.append(dict(method=method,n=n,cfl=cfl,max_number_residual=max(nres),
        max_energy_residual_pre=max(epre),max_energy_residual_post=max(epost),
        max_coarse_32bin_L1=max(binerr),max_outflow_number_error=max(noerr),
        max_outflow_energy_error_relative_true_U0=max(eoerr),
        initial_number_error=rs[0]['N0']-1,
        initial_energy_error_relative_true_U0=(rs[0]['U0_pre']-U0)/U0,
        initial_limiter_energy_change=rs[0]['initial_du'],
        final_stage_limiter_energy_change=rs[-1]['stage_du'],
        final_stage_absolute_limiter_energy_change=rs[-1]['stage_abs_du'],
        final_limiter_application_count=int(rs[-1]['lim_count']),
        min_density=None if method=='stock' else min(r['min_density'] for r in rs),
        min_stock_weight=min(r['stock_min_weight'] for r in rs) if method=='stock' else None,
        max_negative_mass=max(r['negative_mass'] for r in rs),
        max_continuous_L1_GL16=None if method=='stock' else max(r['L1_GL16'] for r in rs),
        max_GL8_GL16_absolute_difference=max(quadabs,default=0),
        max_GL8_GL16_relative_difference=max(quadrel,default=0),
        final_steps=int(rs[-1]['steps']),case_seconds=rs[-1]['case_seconds']))

hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [ROOT/'CONTRACT.md',ROOT/'ADDENDUM.md',ROOT/'bench.rs',ROOT/'tests.rs',ROOT/'oracle.py',ROOT/'oracle.json',ROOT/'results.csv']}
hashes['../pde-method-comparison/Bianchi_REI_conservative_transport_design.md'] = hashlib.sha256((ROOT/'../pde-method-comparison/Bianchi_REI_conservative_transport_design.md').read_bytes()).hexdigest()
output = dict(row_count=len(rows),case_count=len(groups),hashes=hashes,
              independent_oracle_disagreement=oracle_disagreement,
              max_recorded_residual_disagreement=max_record_mismatch,
              max_bin_mass_sum_disagreement=max_bin_mass_mismatch,
              max_crossing_energy_disagreement_relative_true_U0=max_crossing_energy_mismatch,
              max_limiter_accounting_disagreement=limiter_mismatch,cases=summary)
(ROOT/'INDEPENDENT_METRICS.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
print('rows',len(rows),'cases',len(groups))
print('residual field disagreement',max_record_mismatch,'bin mass sum disagreement',max_bin_mass_mismatch)
print('limiter accounting disagreement',limiter_mismatch)
print('independent Simpson oracle maximum scalar disagreement',max(v for x in oracle_disagreement.values() if isinstance(x,dict) for v in x.values()))
for r in summary:
    if r['cfl'] in (0,.075):
        print(r['method'],r['n'],'Nres',r['max_number_residual'],'Eres',r['max_energy_residual_pre'],
              'coarseL1',r['max_coarse_32bin_L1'],'outflow',r['max_outflow_number_error'],
              'L1',r['max_continuous_L1_GL16'],'q_abs',r['max_GL8_GL16_absolute_difference'],
              'q_rel',r['max_GL8_GL16_relative_difference'],'negative',r['max_negative_mass'])
assert max_record_mismatch < 5e-15
assert max_bin_mass_mismatch < 5e-12
assert max_crossing_energy_mismatch < 5e-12
assert limiter_mismatch < 5e-12
assert all(r['max_number_residual']<5e-12 for r in summary)
assert all(r['max_energy_residual_pre']<5e-12 for r in summary if r['method'] in ('stock','partial','dg'))
assert all(r['max_negative_mass']==0 for r in summary if r['method'] in ('stock','partial','fv','dg_limited'))
