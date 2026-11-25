import json,hashlib,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import PchipInterpolator
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw/Downloads')
name='map32';prior=json.loads((D.parent/'r118c2v_mapped32/RESULTS.json').read_text())['case']
paths=[Path(r['raw_path']) for r in prior['segments']]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
rows=[];src={}
for p in paths:
 f=p/'history.csv';src[str(f)]=sha(f);assert src[str(f)]==next(r['hashes']['history.csv'] for r in prior['segments'] if r['raw_path']==str(p));rows.append(np.genfromtxt(f,names=True,delimiter=','))
t=np.concatenate([rows[0]]+[r[1:] for r in rows[1:]])
assert t['zbar'][0]==20 and t['zbar'][-1]==4
u=np.log(21*t['a']);u[0]=0.;u[-1]=np.log(21/5)
a0=1/21
def Hf(a):return np.sqrt(.315/a**3+9.2e-5/a**4+1-.315-9.2e-5)
def rhs(u,y):
 a=a0*np.exp(u);s=-Hf(a0)*(a0/a)**3;return [s/np.hypot(Hf(a),s)]
sol=solve_ivp(rhs,(0,u[-1]),[0.],rtol=2e-13,atol=2e-15,dense_output=True)
assert sol.success
# actual accepted histories, interpolated in ln a; exact cumulative births
for nt in (1024,2048,4096):
 ue=np.linspace(0,u[-1],nt+1);mid=(ue[:-1]+ue[1:])/2;am=a0*np.exp(mid);bm=sol.sol(mid)[0]
 def f(k,x):return PchipInterpolator(u,t[k])(x)
 dt=np.diff(f('time_s',ue));birth=np.diff(f('source_N',ue));nh=f('nH_proper_cm3',mid);he=.2454/(4*(1-.2454))
 x=nh*(1-f('x_HII',mid));y=nh*he*(1-f('x_HeII',mid)-f('x_HeIII',mid));z=nh*he*f('x_HeII',mid)
 # PCHIP may yield roundoff of xHeII+xHeIII near one; reject negative.
 assert min(x.min(),y.min(),z.min(),dt.min(),birth.min())>=0
 np.savetxt(D/f'gas_{name}_{nt}.txt',np.stack([am,bm,dt,birth,x,y,z],axis=1),fmt='%.17e')
for n in (16,32,64):
 x,w=leggauss(n);r=.5;v=np.sqrt(1-x*x+r*r*x*x);mu=r*x/v;ww=w/2*r/v**3
 np.savetxt(D/f'angle_{n}.txt',np.stack([mu,ww],axis=1),fmt='%.17e')
out=dict(name=name,sources=src,b_end=float(sol.y[0,-1]),terminal={k:float(t[k][-1]) for k in ('J0','J2','source_N','source_U','x_HeIII','temperature_K')})
(D/f'gas_{name}.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
