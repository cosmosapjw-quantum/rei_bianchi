"""Actual equal-budget cell refinement selected by transported vector defects, not terminal ref."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;ns={'__file__':str(D/'clock.py'),'__name__':'prior'}
s=(D/'clock.py').read_text();exec(compile(s[:s.index('oldref=')],str(D/'clock.py'),'exec'),ns)
initial,step,obs,inv=map(ns.get,['initial','step','obs','inv']);tau=ns['tau'];u=ns['u']
z=np.load(D/'GOAL_DEFECT.npz');ref=z['ref'];floor=np.maximum(np.array([np.linalg.norm(v) for v in obs(z['oldref'])]),1e-32)
# Use C4I reference only to scale observable components; C4K refined reference used only for evaluation.
scale=np.repeat(floor,[5,7,9]);rows=[]
for n in [64,128]:
 t=z[f'grid_{n}'];base=z[f'yc_{n}'];Q=z[f'contribution_{n}']/scale[None,:]
 # Defect D maps coarse to fine. Asymptotic coarse-to-exact correction = 16/15 sum Q.
 # Refinement of selected cells gives approximately sum selected Q. Greedy minimizes remaining vector norm.
 target=16/15*Q.sum(0);remaining=target.copy();chosen=[]
 for k in range(64):
  r=np.sum(abs(remaining[None,:]-Q)**2,axis=1);r[chosen]=np.inf;j=int(np.argmin(r));chosen.append(j);remaining-=Q[j]
 absrank=np.argsort(-np.linalg.norm(Q,axis=1),kind='stable')[:64]
 wide=np.argsort(-np.diff(t),kind='stable')[:64]
 unif=np.linspace(0,len(t)-2,64,dtype=int);assert len(set(unif))==64
 def err(v):return np.array([float(np.linalg.norm(a-b)/s) for a,b,s in zip(obs(v),obs(ref),floor)])
 e0=err(base)
 for name,ids in [('signed_greedy',chosen),('adjoint_norm',absrank),('largest_du',wide),('uniform_index',unif)]:
  ids=np.array(ids);grid=np.unique(np.r_[t,(t[ids]+t[ids+1])/2]);assert len(grid)==len(t)+64
  y=initial.copy();tm=time.monotonic()
  for l,r in zip(grid[:-1],grid[1:]):y=step(l,r,y)
  e=err(y);pred=target-Q[ids].sum(0)
  row=dict(optical_bins=n,baseline_steps=len(t)-1,refined_steps=len(grid)-1,method=name,selected=ids.tolist(),baseline_error=e0.tolist(),reference_error=e.tolist(),ratio=(e/e0).tolist(),predicted_scaled_residual=float(np.linalg.norm(pred)),actual_scaled_error=float(np.linalg.norm(e)),seconds=time.monotonic()-tm)
  rows.append(row);print(n,name,'ratio',row['ratio'],'actual',row['actual_scaled_error'],flush=True)
(D/'GOAL_REFINEMENT.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256((D/'GOAL_DEFECT.npz').read_bytes()).hexdigest(),scope='same actual prescribed clock and finite lmax6, 64 extra cells; selection uses only coarse/fine defect and prior normalization, not refined reference; signed linear prediction approximate for mixed map, actual independent integration assessed'),indent=2)+'\n')
