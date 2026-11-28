"""Exact discrete signed defect transport on C4J actual knot clock plus refined CF4 reference."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;P=D.parent;J=P/'r118c4j_shape_jac';I=P/'r118c4i_transport_jac'
old=(J/'clock.py').read_text();g={'__file__':str(J/'clock.py'),'__name__':'prior'};exec(compile(old[:old.index('rows=[];vals={}')],str(J/'clock.py'),'exec'),g)
u,tau,inv,pp,N,cd,obs,advance,matrix,Y00,a1,a2,z1,z2,grid=[g[k] for k in ['u','tau','inv','pp','N','cd','obs','advance','matrix','Y00','a1','a2','z1','z2','grid']]
p=pp[2];initial=np.zeros(N,cd);initial[0]=Y00
def mats(l,r):
 dt=r-l;A,B=matrix(l+z1*dt),matrix(l+z2*dt);return dt*(a2*A+a1*B),dt*(a1*A+a2*B)
def action(ab,y):
 A,B=ab;return advance(B,advance(A,y,p),p)
def step(l,r,y):return action(mats(l,r),y)
def refined(n):
 t=np.unique(np.r_[u,inv(np.linspace(0,tau[-1],n+1))]);t=t[(t>=u[0])&(t<=u[-1])];y=initial.copy();tm=time.monotonic()
 for i,(l,r) in enumerate(zip(t[:-1],t[1:]),1):
  y=step(l,r,y)
  if i%4096==0:print('refined',n,i,flush=True)
 return y,len(t)-1,time.monotonic()-tm
oldref=np.load(I/'CLOCK_CF4.npz')['ref'];ref,nref,sec=refined(16384);floor=np.maximum(np.array([np.linalg.norm(x) for x in obs(ref)]),1e-32)
def norms(x):return np.array([float(np.linalg.norm(a)/b) for a,b in zip(obs(x),floor)])
print('reference',nref,sec,'old_ref_error',norms(ref-oldref).tolist(),flush=True)
rows=[];arrays={'ref':ref,'oldref':oldref}
for n in [64,128,256,512]:
 t=np.unique(np.r_[u,inv(np.linspace(0,tau[-1],n+1))]);t=t[(t>=u[0])&(t<=u[-1])];yc=initial.copy();yf=initial.copy();d=np.zeros(N,cd);local=np.zeros(3);tm=time.monotonic()
 # Store actual full vectors for a reverse adjoint projection of the terminal channels.
 defects=[];factors=[]
 for l,r in zip(t[:-1],t[1:]):
  m=(l+r)/2;C=mats(l,r);F1,F2=mats(l,m),mats(m,r)
  co=action(C,yc);fi=action(F2,action(F1,yc));z=fi-co;defects.append(z);local+=norms(z)
  d=action(F2,action(F1,d))+z;yc=co;yf=action(F2,action(F1,yf))
  factors.append((F1,F2))
 # 19 complex observable components; independent reverse transport of the actual linear map.
 O=np.stack([np.concatenate(obs(np.eye(N,dtype=cd)[:,j])) for j in range(N)],axis=1);W=O.conj().T
 def adjexp(A,v):
  # Taylor22 of conjugate-transpose; same finite polynomial as forward action.
  z=v.copy();q=v.copy();B=A.conj().T.tocsr()
  for k in range(1,23):q=B@q/k;z+=q
  return z
 def adjact(ab,v):
  A,B=ab;return adjexp(A,adjexp(B,v))
 contributions=[]
 for z,(F1,F2) in zip(reversed(defects),reversed(factors)):
  contributions.append(W.conj().T@z);W=adjact(F1,adjact(F2,W))
 contributions=np.array(contributions[::-1]);pred=contributions.sum(0)
 direct=np.concatenate(obs(yf-yc));forward=np.concatenate(obs(d))
 ar=np.array([np.linalg.norm(x) for x in np.split(pred,[5,12])],float)/floor.astype(float)
 adjgap=np.array([np.linalg.norm(x) for x in np.split(pred-forward,[5,12])],float)/floor.astype(float)
 forwardgap=norms(d-(yf-yc));ref_co=norms(yc-ref);ref_fi=norms(yf-ref)
 sum_abs=np.array([np.linalg.norm(x,axis=1).sum() for x in np.split(contributions,[5,12],axis=1)],float)/floor.astype(float)
 # Explicitly report reference-limited accuracy instead of asserting asymptotic estimates are exact.
 row=dict(optical_bins=n,steps=len(t)-1,coarse_error=ref_co.tolist(),fine_error=ref_fi.tolist(),propagated_defect=ar.tolist(),naive_local_defect_sum=local.tolist(),adjoint_absolute_sum=sum_abs.tolist(),fine_error_estimate=(ar/15).tolist(),forward_telescoping_gap=forwardgap.tolist(),adjoint_gap=adjgap.tolist(),coarse_fine_gap=norms(yf-yc).tolist(),seconds=time.monotonic()-tm)
 assert max(adjgap)<1e-13 and max(forwardgap)<1e-12,(n,row)
 rows.append(row);arrays[f'grid_{n}']=t;arrays[f'yc_{n}']=yc;arrays[f'yf_{n}']=yf;arrays[f'contribution_{n}']=contributions;print(row,flush=True)
np.savez_compressed(D/'GOAL_DEFECT.npz',**arrays)
(D/'GOAL_DEFECT.json').write_text(json.dumps(dict(rows=rows,reference_steps=nref,reference_seconds=sec,old_reference_relative=norms(ref-oldref).tolist(),source_sha=hashlib.sha256((I/'CLOCK_CF4.npz').read_bytes()).hexdigest(),scope='actual prescribed C4I BASS/REC clock, full finite lmax6, exact discrete CF4 coarse/fine defect recurrence and reverse observable projection with Taylor22; fine-step /15 estimator asymptotic, not certified continuum or self-consistent REI'),indent=2)+'\n')
