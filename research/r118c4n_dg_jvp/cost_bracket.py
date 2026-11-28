"""Cost-aware low-order local observable estimator on real C4L held-out clocks."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;P=D.parent;K=P/'r118c4m_coupled_stage';L=P/'r118c4l_implicit_branch'
src=(K/'clock.py').read_text();ns={'__file__':str(K/'clock.py'),'__name__':'prior'};exec(compile(src[:src.index('rows=[];arr={};comparisons=[]')],str(K/'clock.py'),'exec'),ns)
u,pp,N,cd,obs,initial,O,f,ops,C,a1,a2,z1,z2=[ns[k] for k in ['u','pp','N','cd','obs','initial','O','f','ops','C','a1','a2','z1','z2']]
grid,choose,refine,ex,run,native_ops=[ns[k] for k in ['grid','choose','refine','ex','run','native_ops']]
data=np.load(L/'HELDOUT_GOAL.npz')
def local(t,p,ss,kk):
 tm=time.monotonic();q=native_ops(p);y=initial[p].copy();Q=[]
 def mat(t):
  v=f(t);return (sum(ss*x*A for x,A in zip(v[:5],q[:5]))+kk*v[5]*q[5]).tocsr()
 def step(l,r,y):
  dt=r-l;A,B=mat(l+z1*dt),mat(l+z2*dt);return ex(dt*(a1*A+a2*B),ex(dt*(a2*A+a1*B),y))
 for l,r in zip(t[:-1],t[1:]):
  m=(l+r)/2;c=step(l,r,y);z=step(m,r,step(l,m,y));Q.append(O[:,p]@(z-c));y=z
 out=np.zeros(N,cd);out[p]=y;scale=np.repeat(np.maximum([np.linalg.norm(x) for x in obs(out)],1e-32),[5,7,9]);return np.array(Q)/scale[None,:],time.monotonic()-tm
rows=[];arrays={};compare=[]
for case,ss,kk in [('low_shear_high_opacity',.5,1.25),('high_shear_low_opacity',2.,.75)]:
 ref=data[case+'_ref'];ref2=data[case+'_ref8192'];floor=np.maximum([np.linalg.norm(x) for x in obs(ref)],1e-32)
 def err(y):return np.array([float(np.linalg.norm(a-b)/s) for a,b,s in zip(obs(y),obs(ref),floor)])
 def test(method,p,t,sel=0):
  y,sec=run(t,p,ss,kk);r=dict(case=case,method=method,dim=len(p),steps=len(t)-1,selection_seconds=sel,integrate_seconds=sec,total_seconds=sel+sec,error=err(y).tolist(),norm=float(np.linalg.norm(err(y))),ref_gap=err(ref2).tolist());rows.append(r);arrays[f'{case}_{method}_{len(p)}_{len(t)-1}']=y;print(r,flush=True);return r
 t=grid(128);q,sel=local(t,pp[0],ss,kk)
 for kind in ['adjoint_norm']:
  tt=refine(t,choose(q,64,kind,t));test('local_projected_norm',pp[0],tt,sel)
 for p in [pp[0]]:
  for n in [512,768,1024,1280,1536,1792,2048]:test('uniform',p,grid(n))
 a=[x for x in rows if x['case']==case and x['method'].startswith('local')];b=[x for x in rows if x['case']==case and x['method']=='uniform'];best=[]
 for x in a:
  cand=[r for r in b if r['total_seconds']<=x['total_seconds']]
  best.append(dict(adaptive=x,uniform=min(cand,key=lambda q:q['norm']) if cand else None))
 compare.extend(best)
np.savez_compressed(D/'COST_BRACKET.npz',**arrays)
(D/'COST_BRACKET.json').write_text(json.dumps(dict(rows=rows,comparisons=compare,source_sha=hashlib.sha256((L/'HELDOUT_GOAL.npz').read_bytes()).hexdigest(),scope='denser uniform cost bracket; local observable-projected CF4 step doubling in 48 dimensions, no global adjoint/transport of defect; actual selection cost included, reduced/full final propagation and matched-or-lower cost uniform comparisons; one timing per candidate, finite reference and same previous heldout conditions'),indent=2,allow_nan=False)+'\n')
