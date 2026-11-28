"""Held-out scaled prescribed REC/BASS clocks; actual equal final-step goal refinement."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4k_moving_nodes';I=P/'r118c4i_transport_jac';J=P/'r118c4j_shape_jac'
old=(J/'clock.py').read_text();g={'__file__':str(J/'clock.py'),'__name__':'prior'};exec(compile(old[:old.index('rows=[];vals={}')],str(J/'clock.py'),'exec'),g)
u,tau,inv,pp,N,cd,obs,advance,Y00,a1,a2,z1,z2=[g[k] for k in ['u','tau','inv','pp','N','cd','obs','advance','Y00','a1','a2','z1','z2']]
# Original C4I function globals are the actual C4H interpolants and sparse generators.
mg=g['matrix'].__globals__;f,ops,C=mg['f'],mg['ops'],mg['C'];p=pp[2];initial=np.zeros(N,cd);initial[0]=Y00
O=np.stack([np.concatenate(obs(np.eye(N,dtype=cd)[:,j])) for j in range(N)],axis=1)
def adjexp(A,v):
 z=v.copy();q=v.copy();B=A.conj().T.tocsr()
 for k in range(1,23):q=B@q/k;z+=q
 return z
def adjact(ab,v):
 A,B=ab;return adjexp(A,adjexp(B,v))
def action(ab,y):
 A,B=ab;return advance(B,advance(A,y,p),p)
def grid(n):
 t=np.unique(np.r_[u,inv(np.linspace(0,tau[-1],n+1))]);return t[(t>=u[0])&(t<=u[-1])]
def choose(Q,k,kind,t):
 if kind=='signed':
  target=16/15*Q.sum(0);remaining=target.copy();chosen=[]
  for _ in range(k):
   r=np.sum(abs(remaining[None,:]-Q)**2,axis=1);r[chosen]=np.inf;j=int(np.argmin(r));chosen.append(j);remaining-=Q[j]
  return np.array(chosen)
 if kind=='adjoint_norm':return np.argsort(-np.linalg.norm(Q,axis=1),kind='stable')[:k]
 if kind=='largest_du':return np.argsort(-np.diff(t),kind='stable')[:k]
 return np.linspace(0,len(t)-2,k,dtype=int)
def refine(t,ids):return np.unique(np.r_[t,(t[ids]+t[ids+1])/2])
rows=[];arrays={}
for case,Sscale,Kscale in [('low_shear_high_opacity',.5,1.25),('high_shear_low_opacity',2.,.75)]:
 def matrix(t):
  v=f(t);return (sum(Sscale*x*op for x,op in zip(v[:5],ops))+Kscale*v[5]*C).tocsr().astype(cd)
 def mats(l,r):
  dt=r-l;A,B=matrix(l+z1*dt),matrix(l+z2*dt);return dt*(a2*A+a1*B),dt*(a1*A+a2*B)
 def run(t):
  y=initial.copy()
  for l,r in zip(t[:-1],t[1:]):y=action(mats(l,r),y)
  return y
 def defects(t):
  yc=initial.copy();yf=initial.copy();dd=[];ff=[];tm=time.monotonic()
  for l,r in zip(t[:-1],t[1:]):
   m=(l+r)/2;F1,F2=mats(l,m),mats(m,r);co=action(mats(l,r),yc);fi=action(F2,action(F1,yc))
   dd.append(fi-co);ff.append((F1,F2));yc=co;yf=action(F2,action(F1,yf))
  W=O.conj().T;Q=[]
  for z,(F1,F2) in zip(reversed(dd),reversed(ff)):
   Q.append(W.conj().T@z);W=adjact(F1,adjact(F2,W))
  Q=np.array(Q[::-1]);gap=Q.sum(0)-O@(yf-yc)
  floor=np.maximum(np.array([np.linalg.norm(a) for a in obs(yf)]),1e-32);scale=np.repeat(floor,[5,7,9])
  assert np.linalg.norm(gap/scale)<1e-12
  return yc,Q/scale[None,:],floor,time.monotonic()-tm,float(np.linalg.norm(gap/scale))
 tm=time.monotonic();r0=run(grid(8192));ref=run(grid(16384));sec=time.monotonic()-tm
 t=grid(128);yc,Q,floor,ds,gap=defects(t)
 def err(y):return np.array([float(np.linalg.norm(a-b)/s) for a,b,s in zip(obs(y),obs(ref),floor)])
 refgap=err(r0);base=err(yc);print(case,'ref',refgap.tolist(),'base',base.tolist(),flush=True)
 for kind in ['signed','adjoint_norm','largest_du','uniform','relinearized_signed']:
  extra=0.;extra_gap=None;tm=time.monotonic()
  if kind=='relinearized_signed':
   t1=refine(t,choose(Q,32,'signed',t));_,Q1,_,extra,extra_gap=defects(t1);t2=refine(t1,choose(Q1,32,'signed',t1))
  else:t2=refine(t,choose(Q,64,kind,t))
  assert len(t2)==len(t)+64;y=run(t2);e=err(y)
  row=dict(case=case,Sscale=Sscale,Kscale=Kscale,base_steps=len(t)-1,refined_steps=len(t2)-1,method=kind,base_error=base.tolist(),reference_error=e.tolist(),ratio=(e/np.maximum(base,1e-300)).tolist(),norm_ratio=float(np.linalg.norm(e)/np.linalg.norm(base)),reference_gap=refgap.tolist(),defect_identity_gap=gap,additional_defect_gap=extra_gap,reference_seconds=sec,initial_defect_seconds=ds,additional_defect_seconds=extra,selection_and_run_seconds=time.monotonic()-tm)
  rows.append(row);arrays[case+'_'+kind+'_grid']=t2;arrays[case+'_'+kind+'_y']=y;print(row,flush=True)
 arrays[case+'_ref']=ref;arrays[case+'_ref8192']=r0
np.savez_compressed(D/'HELDOUT_GOAL.npz',**arrays)
(D/'HELDOUT_GOAL.json').write_text(json.dumps(dict(rows=rows,source_sha=hashlib.sha256((I/'CLOCK_CF4.npz').read_bytes()).hexdigest(),scope='two preselected held-out prescribed shear/opacity scalings, finite lmax6, equal final integration step budget (+64 cells); one/two reverse defect analyses have different actual cost; independent 8192/16384 finite reference not used for selection, no universal efficiency claim'),indent=2,allow_nan=False)+'\n')
