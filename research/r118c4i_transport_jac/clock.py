"""Actual early REC-clock convergence, fourth-order commutator-free vs midpoint."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;P=D.parent;H=P/'r118c4h_stage_jacobian'
old=(H/'early.py').read_text();old=old[:old.index(';rows=[]')];g={'__file__':str(H/'early.py'),'__name__':'prior'};exec(compile(old,str(H/'early.py'),'exec'),g)
# f and inverse are the exact C4H interpolants (actual clock, prescribed shear).
f,inv,tau,u,ops,C,N,pp,cd,obs,relative,proj,taylor=[g[k] for k in ['f','inv','tau','u','ops','C','N','pp','cd','obs','relative','proj','taylor']]
Y00=g['g']['Y00'];a1=(3-2*np.sqrt(3))/12;a2=(3+2*np.sqrt(3))/12;z1=.5-np.sqrt(3)/6;z2=.5+np.sqrt(3)/6
assert abs(a1+a2-.5)<1e-15
def matrix(t):
 v=f(t);return (sum(x*op for x,op in zip(v[:5],ops))+v[5]*C).tocsr().astype(cd)
def advance(A,y,p):
 z=proj(y,p);v=z.copy()
 for k in range(1,23):v=proj(A@v,p)/k;z+=v
 return z
def run(n,split=False,methods=('mid','cf4'),sectors=(0,1,2)):
 grid=inv(np.linspace(0,tau[-1],n+1))
 if split:grid=np.unique(np.r_[grid,u[(u>=grid[0])&(u<=grid[-1])]])
 vals={(m,k):np.zeros(N,cd) for m in methods for k in sectors}
 for y in vals.values():y[0]=Y00
 mx=0.;tm=time.monotonic()
 for l,r in zip(grid[:-1],grid[1:]):
  dt=r-l
  if 'mid' in methods:M=dt*matrix((l+r)/2)
  if 'cf4' in methods:
   A,B=matrix(l+z1*dt),matrix(l+z2*dt)
   # Right (earliest) exponential weights A more heavily; left weights B.
   U=dt*(a2*A+a1*B);V=dt*(a1*A+a2*B)
   mx=max(mx,float(np.max(np.asarray(abs(U).sum(axis=1)))),float(np.max(np.asarray(abs(V).sum(axis=1)))))
  for (m,k),y in vals.items():vals[m,k]=advance(M,y,pp[k]) if m=='mid' else advance(V,advance(U,y,pp[k]),pp[k])
 return vals,len(grid)-1,time.monotonic()-tm,mx
results={};rows=[]
# Independent refined reference with all actual interpolation knots included.
ref,nref,sec,norm=run(4096,True,('cf4',),(2,));ref=ref['cf4',2];ref2,nref2,sec2,norm2=run(8192,True,('cf4',),(2,));ref2=ref2['cf4',2]
refgap=relative(ref-ref2,ref2)
for n in [128,256,512,1024,2048]:
 for split in [False,True] if n in [128,512] else [False]:
  x,nact,sec,mx=run(n,split)
  for m in ['mid','cf4']:
   for k in [0,1,2]:
    y=x[m,k];errors={name:float(np.linalg.norm(v-w)/max(np.linalg.norm(w),1e-32)) for name,v,w in zip(['E2','B3','E4'],obs(y),obs(ref2))}
    trunc={name:float(np.linalg.norm(v-w)/max(np.linalg.norm(w),1e-32)) for name,v,w in zip(['E2','B3','E4'],obs(y),obs(x[m,2]))}
    rows.append(dict(n=n,steps=nact,source_knot_split=split,method=m,dimension=len(pp[k]),error=errors,truncation=trunc,seconds_all=sec,max_cf4_exponent_norm=mx))
    results[f'{n}_{int(split)}_{m}_{len(pp[k])}']=y
  print(n,split,nact,[(r['method'],r['error']) for r in rows[-6:] if r['dimension']==147],flush=True)
np.savez_compressed(D/'CLOCK_CF4.npz',ref=ref2,**results)
(D/'CLOCK_CF4.json').write_text(json.dumps(dict(rows=rows,tau_total=float(tau[-1]),reference_steps=nref2,coarse_reference_steps=nref,reference_relative_gap=float(refgap),reference_seconds=sec2,clock_sha=hashlib.sha256(g['clock'].read_bytes()).hexdigest(),shear_sha=hashlib.sha256(g['jet'].read_bytes()).hexdigest(),scope='same C4H actual scalar REC clock, BASS prescribed shear; full finite lmax6 vs retained fixed sectors, extended Taylor22 exponential, CF4 chronological ordering; knot split actual interpolation grid, finite reference not continuum certificate'),indent=2)+'\n')
