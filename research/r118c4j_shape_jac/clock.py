"""C4J source-knot aligned adaptive CF4, same actual C4I clock and reference."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;P=D.parent;I=P/'r118c4i_transport_jac'
old=(I/'clock.py').read_text();old=old[:old.index('results={};rows=[]')];g={'__file__':str(I/'clock.py'),'__name__':'prior'};exec(compile(old,str(I/'clock.py'),'exec'),g)
u,tau,inv,pp,N,cd,obs,advance,matrix,Y00,a1,a2,z1,z2=[g[k] for k in ['u','tau','inv','pp','N','cd','obs','advance','matrix','Y00','a1','a2','z1','z2']]
ref=np.load(I/'CLOCK_CF4.npz')['ref'];floor=np.maximum(np.array([np.linalg.norm(x) for x in obs(ref)]),1e-32)
def rel(y,x):return np.array([float(np.linalg.norm(a-b)/s) for a,b,s in zip(obs(y),obs(x),floor)])
def step(l,r,y,p):
 dt=r-l;A,B=matrix(l+z1*dt),matrix(l+z2*dt);U=dt*(a2*A+a1*B);V=dt*(a1*A+a2*B)
 return advance(V,advance(U,y,p),p)
# Use fixed knot segments plus maximum optical-depth cap. Local error allocated in ln a.
grid=np.unique(np.r_[u,inv(np.linspace(0,tau[-1],129))]);grid=grid[(grid>=u[0])&(grid<=u[-1])];assert grid[0]==u[0] and grid[-1]==u[-1]
rows=[];vals={}
for k in [0,2]:
 for tol in [1e-6,1e-8,1e-10,1e-12]:
  p=pp[k];y=np.zeros(N,cd);y[0]=Y00;rejected=accepted=trials=0;est_sum=np.zeros(3);mx=0.;sizes=[];t0=time.monotonic();maxdepth=0
  def adapt(l,r,y,depth=0):
   global rejected,accepted,trials,est_sum,mx,maxdepth
   trials+=1;coarse=step(l,r,y,p);m=(l+r)/2;fine=step(m,r,step(l,m,y,p),p)
   er=rel(fine,coarse)/15.;local=tol*(r-l)/(u[-1]-u[0]);q=float(max(er)/local)
   assert np.all(np.isfinite(fine)) and depth<30
   maxdepth=max(maxdepth,depth)
   if q<=1:
    accepted+=1;est_sum+=er;mx=max(mx,q);sizes.append(r-l);return fine
   rejected+=1;return adapt(m,r,adapt(l,m,y,depth+1),depth+1)
  for l,r in zip(grid[:-1],grid[1:]):y=adapt(l,r,y)
  err=rel(y,ref);row=dict(dim=len(p),tol=tol,accepted=accepted,rejected=rejected,trial_steps=trials,exponential_actions=6*trials,estimated_sum=est_sum.tolist(),reference_relative=err.tolist(),max_accepted_ratio=mx,min_step=float(min(sizes)),max_step=float(max(sizes)),max_depth=maxdepth,seconds=time.monotonic()-t0)
  rows.append(row);vals[f'{k}_{tol:g}']=y;print(row,flush=True)
# Same adaptive tolerance, compare reduced vs full to separate hierarchy truncation.
for row in rows:
 if row['dim']==48:row['matched_tolerance_hierarchy_gap']=rel(vals[f"0_{row['tol']:g}"],vals[f"2_{row['tol']:g}"]).tolist()
np.savez_compressed(D/'ADAPTIVE_CF4.npz',ref=ref,**vals)
(D/'ADAPTIVE_CF4.json').write_text(json.dumps(dict(rows=rows,clock_sha=hashlib.sha256((I/'CLOCK_CF4.npz').read_bytes()).hexdigest(),reference_steps=json.loads((I/'CLOCK_CF4.json').read_text())['reference_steps'],source_intervals=len(grid)-1,tau=float(tau[-1]),scale_floor=[float(x) for x in floor],scope='actual C4I prescribed REC opacity/BASS shear; CF4 step-doubling estimator 1/15, knot-aligned, finite reference scaling; reduced 48 vs full lmax6, no rigorous global certificate or full self-consistent REI'),indent=2)+'\n')
