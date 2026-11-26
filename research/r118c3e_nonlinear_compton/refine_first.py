import numpy as np,json
from pathlib import Path
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from nonlinear import Kompaneets
D=Path(__file__).resolve().parent;rows=[]
for n in (128,256,512,1024):
 o=Kompaneets(np.geomspace(1e-3,40,n+1));N=o.equilibrium(1.,.2);scale=np.maximum(N,1e-20)
 for t in (.5,2.):
    ref=solve_ivp(lambda y,v:o.rhs(v*scale,t)/scale,(0,.01),N/scale,method='BDF',rtol=1e-11,atol=1e-13,jac_sparsity=diags([np.ones(n-1),np.ones(n),np.ones(n-1)],[-1,0,1]));assert ref.success
    q=ref.y[:,-1]*scale
    row=dict(n=n,theta=t,ref_energy=o.energy(q-N),ref_number=float(abs(q.sum()-N.sum())/N.sum()),ref_nfev=ref.nfev)
    if n<=512:
      k=8*n;s=o.advance(N,t,.01,k);row.update(steps=k,increment_relative=float(np.sum(abs(s-q))/np.sum(abs(q-N))),entropy_change=o.entropy(s,t)-o.entropy(N,t),energy=o.energy(s-N))
      assert row['increment_relative']<1e-5 and row['entropy_change']<0
    rows.append(row);print(row,flush=True)
(D/'REFINE.json').write_text(json.dumps(rows,indent=2)+'\n')
