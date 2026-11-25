import json,hashlib
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator
D=Path(__file__).resolve().parent;P=D.parent/'r118c2t_long_reactive';j=json.loads((P/'RESULTS.json').read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
# exact endpoint b from all segment receipts; actual C2T b(a) not in history, reconstruct
# physical-density branch d b/d ln a=q_ref H_FLRW(a_ref)/H(a) (a_ref/a)^3
from scipy.integrate import solve_ivp
a0=1/21;end=np.log(21/5);om=.315;orr=9.2e-5;ol=1-om-orr
def h(a):return np.sqrt(om/a**3+orr/a**4+ol)
s0=-h(a0)
def rhs(u,y):
 a=a0*np.exp(u);s=s0*(a0/a)**3;return [s/np.hypot(h(a),s)]
sol=solve_ivp(rhs,(0,end),[0.],rtol=1e-12,atol=1e-14,dense_output=True)
# use actual endpoint b for each legacy result as authoritative, not this approximation
ck=Path(j['cases']['strong16']['segments'][-1]['raw_path'])/'checkpoint.txt';assert sha(ck)==j['cases']['strong16']['segments'][-1]['hashes']['checkpoint.txt'];b_end=float(ck.read_text().splitlines()[1].split()[2])
# Here b spans exact endpoint range; no approximate background needed for instantaneous diagnostics.
bs=np.linspace(b_end,0,257)
def grid(n,r):
 x,w=leggauss(n);den=np.sqrt(1-x*x+r*r*x*x);mu=r*x/den;jac=r/den**3
 return mu,w/2*jac
def calc(n,r):
 mu,w=grid(n,r);v=[]
 for b in bs:
  p=np.exp(b);z=np.exp(-2*b);R=np.sqrt(p*p*(1-mu*mu)+z*z*mu*mu)
  m=z*mu/R;jac=1/R**3
  a=w*jac;norm=a.sum();v.append([norm-1,(a@((3*m*m-1)/2))/norm])
 return np.array(v)
rows=[]
for n in (8,16,32,64,128):
 for r in (1.,.7,.5,.35,.25):
  v=calc(n,r);row=dict(n=n,map_ratio=r,max_area_error=float(max(abs(v[:,0]))),max_birth_J2=float(max(abs(v[:,1]))),terminal_area_error=float(v[0,0]),terminal_birth_J2=float(v[0,1]),initial_area_error=float(v[-1,0]),initial_birth_J2=float(v[-1,1]))
  rows.append(row);print(row,flush=True)
# independent legacy terminal angular integration
old={}
for n in (8,16):
 r=j['cases']['strong'+str(n)];p=Path(r['segments'][-1]['raw_path'])/'checkpoint.txt';assert sha(p)==r['segments'][-1]['hashes']['checkpoint.txt']
 ls=p.read_text().splitlines();a,_,b=map(float,ls[1].split()[:3]);mu,w=leggauss(n);R=a0/a*np.sqrt((1-mu*mu)*np.exp(2*b)+mu*mu*np.exp(-4*b));m=mu*np.exp(-2*b)*a0/a/R
 U=sum(np.fromstring(ls[k],sep=' ').reshape(n,35).sum(axis=1) for k in (5,9,12,16,20))*R;J2=U@((3*m*m-1)/2)
 assert abs(J2-r['terminal']['J2'])<1e-11
 old[str(n)]=dict(b=b,J0=float(U.sum()),J2=float(J2),energy_by_ray=U.tolist(),mu=m.tolist(),checkpoint_sha=sha(p))
out=dict(status='SCOPED_ANGULAR_SOURCE_DIAGNOSTIC',b_end=b_end,rows=rows,legacy=old,scope='isotropic source quadrature instantaneously, not full absorption trajectory. Reference-mu map fixed in time, positive weights.')
(D/'ANGULAR.json').write_text(json.dumps(out,indent=2)+'\n')
