import csv, json, math
from pathlib import Path
import scipy.integrate as si
r=Path(__file__).resolve().parents[1]
data=list(csv.DictReader((r/'evidence/scalar_manufactured.csv').open()))
ans={}
for case in ('linear_kappa','smooth_kappa_j','constant','zero'):
    def integrated_k(t):
        if case=='linear_kappa':return 0.3*(1-t)+1.1*(1-t*t)/2
        if case=='smooth_kappa_j':return 0.3*(1-t)+1.1*(1-t*t)/2+0.7*(1-t**3)/3
        if case=='constant':return 0.3*(1-t)
        return 0.
    def src(t):return 1.7*(1+0.25*t*t) if case=='smooth_kappa_j' else 1.7
    exact=2.3*math.exp(-integrated_k(0))+si.quad(lambda t:src(t)*math.exp(-integrated_k(t)),0,1,epsabs=1e-13,epsrel=1e-13)[0]
    ans[case]={'independent_scipy_quad_survivors':exact,'runs':[]}
    for row in data:
        if row['case'] != case: continue
        N=int(row['steps']);q=int(row['birth_gl']);m=int(row['opacity_substeps'])
        surv=float(row['survivors']);error=abs(surv-exact)/abs(exact)
        ans[case]['runs'].append({'N':N,'q':q,'m':m,'survivors':surv,'error':error,'ledger':float(row['number_residual'])})
    for mode in [(2,1),(4,1),(4,4),(4,8)]:
        recs=sorted((x for x in ans[case]['runs'] if (x['q'],x['m'])==mode),key=lambda x:x['N'])
        orders=[]
        for a,b in zip(recs,recs[1:]):
            if a['error']>1e-14 and b['error']>1e-14:orders.append(math.log(a['error']/b['error'],2))
        ans[case][f'orders_{mode[0]}_{mode[1]}']=orders
        ans[case][f'last_{mode[0]}_{mode[1]}']=recs[-1]['error']
    print(case,'quad_ref',format(exact,'.15g'),'last-N-errors',[(m,ans[case][f'last_{m[0]}_{m[1]}'])for m in [(2,1),(4,1),(4,4),(4,8)]])
(r/'evidence/scalar_independent_check.json').write_text(json.dumps(ans,indent=2)+'\n')
# 64-step sequential floating additions admit O(N*eps) roundoff; observed max 3.33e-15.
assert max(row['ledger'] for group in ans.values() for row in group['runs']) < 6e-15
assert ans['linear_kappa']['last_4_8'] < 2e-13
assert ans['smooth_kappa_j']['last_4_8'] < 5e-7
