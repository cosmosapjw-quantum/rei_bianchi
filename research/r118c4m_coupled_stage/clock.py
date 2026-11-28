"""Cost-accounted actual held-out CF4 clock and joint retained hierarchy refinement."""
from pathlib import Path
import numpy as np,json,time,hashlib
D=Path(__file__).resolve().parent;P=D.parent;L=P/'r118c4l_implicit_branch'
source=(L/'clock.py').read_text();ns={'__file__':str(L/'clock.py'),'__name__':'prior'}
tm=time.monotonic();exec(compile(source[:source.index('rows=[];arrays={}')],str(L/'clock.py'),'exec'),ns)
u,tau,inv,pp,N,cd,obs,initial,O,f,ops,C,a1,a2,z1,z2=[ns[k] for k in ['u','tau','inv','pp','N','cd','obs','initial','O','f','ops','C','a1','a2','z1','z2']]
grid,choose,refine,adjact=map(ns.get,['grid','choose','refine','adjact'])
pre=time.monotonic()-tm;data=np.load(L/'HELDOUT_GOAL.npz')
def ex(A,y):
 z=y.copy();v=y.copy()
 for k in range(1,23):v=A@v/k;z+=v
 return z
def native_ops(p):
 return [A[p][:,p].tocsr().astype(cd) for A in [*ops,C]]
def run(t,p,scale,opacity):
 t0=time.monotonic();q=native_ops(p);y=initial[p].copy()
 def matrix(t):
  v=f(t);return (sum(scale*x*A for x,A in zip(v[:5],q[:5]))+opacity*v[5]*q[5]).tocsr()
 for l,r in zip(t[:-1],t[1:]):
  dt=r-l;A,B=matrix(l+z1*dt),matrix(l+z2*dt)
  y=ex(dt*(a1*A+a2*B),ex(dt*(a2*A+a1*B),y))
 out=np.zeros(N,cd);out[p]=y
 return out,time.monotonic()-t0
def signed(t,Sscale,Kscale):
 tm=time.monotonic();q=native_ops(pp[2])
 def mat(t):
  v=f(t);return (sum(Sscale*x*A for x,A in zip(v[:5],q[:5]))+Kscale*v[5]*q[5]).tocsr()
 def mats(l,r):
  dt=r-l;A,B=mat(l+z1*dt),mat(l+z2*dt);return dt*(a2*A+a1*B),dt*(a1*A+a2*B)
 def action(ab,y):return ex(ab[1],ex(ab[0],y))
 yc=initial.copy();yf=initial.copy();dd=[];ff=[]
 for l,r in zip(t[:-1],t[1:]):
  m=(l+r)/2;F1,F2=mats(l,m),mats(m,r);co=action(mats(l,r),yc);fi=action(F2,action(F1,yc));dd.append(fi-co);ff.append((F1,F2));yc=co;yf=action(F2,action(F1,yf))
 W=O.conj().T;Q=[]
 for z,(F1,F2) in zip(reversed(dd),reversed(ff)):
  Q.append(W.conj().T@z);W=adjact(F1,adjact(F2,W))
 Q=np.array(Q[::-1]);floor=np.maximum(np.array([np.linalg.norm(a) for a in obs(yf)]),1e-32);sc=np.repeat(floor,[5,7,9]);gap=float(np.linalg.norm((Q.sum(0)-O@(yf-yc))/sc))
 assert gap<1e-12
 t2=refine(t,choose(Q/sc[None,:],64,'signed',t));return t2,time.monotonic()-tm,gap
rows=[];arr={};comparisons=[]
for case,ss,kk in [('low_shear_high_opacity',.5,1.25),('high_shear_low_opacity',2.,.75)]:
 ref=data[case+'_ref'];ref2=data[case+'_ref8192'];floor=np.maximum(np.array([np.linalg.norm(a) for a in obs(ref)]),1e-32)
 def err(y,x=ref):return np.array([float(np.linalg.norm(a-b)/s) for a,b,s in zip(obs(y),obs(x),floor)])
 def row(method,p,n,t,y,sec,select=0):
  e=err(y);r=dict(case=case,method=method,dim=len(p),optical_bins=n,steps=len(t)-1,seconds=sec,selection_seconds=select,total_seconds=sec+select,errors=e.tolist(),norm=float(np.linalg.norm(e)),reference_gap=err(ref2).tolist());rows.append(r);arr[f'{case}_{method}_{len(p)}_{n}']=y;print(r,flush=True);return r
 t=grid(128);ts,sel,gap=signed(t,ss,kk);y,sec=run(ts,pp[2],ss,kk);rs=row('signed',pp[2],128,ts,y,sec,sel);rs['defect_gap']=gap
 # Calibration by actual measured cost (all source knots retained), no assumed equal-time speedup.
 # Uniform refinement can spend the entire selection cost on direct propagation.
 for n in [128,256,512,1024,2048,4096,8192]:
  t=grid(n);y,sec=run(t,pp[2],ss,kk);r=row('uniform',pp[2],n,t,y,sec)
  if n>=2048 and sec>rs['total_seconds']*1.2:break
 # Reduced sector real sparse matrices, compare each to full finite reference and to its own refined endpoint.
 for p in pp[:2]:
  for n in [128,512,2048,8192]:
   t=grid(n);y,sec=run(t,p,ss,kk);row('uniform',p,n,t,y,sec)
  yref=arr[f'{case}_uniform_{len(p)}_8192']
  for r in rows:
   if r['case']==case and r['dim']==len(p):r['same_sector_temporal_gap']=err(arr[f"{case}_uniform_{len(p)}_{r['optical_bins']}"],yref).tolist();r['sector_ref_gap']=err(yref).tolist()
 eligible=[r for r in rows if r['case']==case and r['method']=='uniform' and r['total_seconds']<=rs['total_seconds']]
 best=min(eligible,key=lambda r:r['norm']) if eligible else None
 comparisons.append(dict(case=case,signed=rs,best_uniform_measured_under_signed_cost=best,ratio=best['norm']/rs['norm'] if best else None,scope='one measured timing per candidate on same host; not identical CPU load or exact wallclock budget; reference finite, smaller-than-reference errors not certified'))
np.savez_compressed(D/'COST_JOINT.npz',**arr)
(D/'COST_JOINT.json').write_text(json.dumps(dict(rows=rows,comparisons=comparisons,common_setup_seconds=pre,reference_sha=hashlib.sha256((L/'HELDOUT_GOAL.npz').read_bytes()).hexdigest(),scope='actual held-out prescribed clocks from C4L; timed full signed defect selection and integration, uniform full/reduced sparse propagation, joint temporal and finite hierarchy errors. No continuum or autonomous REI claim.'),indent=2,allow_nan=False)+'\n')
