import numpy as np,json,hashlib
from pathlib import Path
from scipy.integrate import solve_ivp
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;J=json.loads((D.parent/'r118c2t_long_reactive/RESULTS.json').read_text());case=J['cases']['strong16'];parts=[];src={}
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for x in case['segments']:
 p=Path(x['raw_path'])/'history.csv';src[str(p)]=sha(p);assert src[str(p)]==x['hashes']['history.csv']
 parts.append(np.genfromtxt(p,names=True,delimiter=',',usecols=['a','source_U']))
r=np.concatenate([parts[0]]+[x[1:] for x in parts[1:]])
a0=1/21;af=.2;u=np.log(r['a']/a0);u[0]=0.;u[-1]=np.log(af/a0);um=(u[1:]+u[:-1])/2;dU=np.diff(r['source_U']);assert np.min(dU)>=0
# native background uses Simpson panels; independently integrate exact branch.
def H(a):return np.sqrt(.315/a**3+9.2e-5/a**4+1-.315-9.2e-5)
def rhs(u,b):
 a=a0*np.exp(u);s=-H(a0)*(a0/a)**3;return [s/np.hypot(H(a),s)]
sol=solve_ivp(rhs,(0,u[-1]),[0.],rtol=2e-13,atol=2e-15,dense_output=True);assert sol.success
bf=sol.y[0,-1];bmid=sol.sol(um)[0];am=a0*np.exp(um)
native_b=json.loads((D/'ANGULAR.json').read_text())['b_end'];assert abs(bf-native_b)<1e-7
def geom(mu,b,a):
 p=np.exp(b);z=np.exp(-2*b);g=np.sqrt(p*p*(1-mu*mu)+z*z*mu*mu)
 return a0/a*g,z*mu/g,1/g**3
def integrate(n,ratio,oracle=False):
 x,w=leggauss(n);w=w/2;num=den=0.
 for start in range(0,len(um),1024):
  sl=slice(start,start+1024);a=am[sl,None];b=bmid[sl,None];weight=dU[sl,None]
  if oracle:
   # Integrate in physical emission direction, not reference direction.
   # The final scale and angle use relative scale factors.
   p=np.exp(bf-b);z=np.exp(-2*(bf-b));g=np.sqrt(p*p*(1-x*x)+z*z*x*x)
   R=(a/af)*g;m=z*x/g;ww=w[None,:]
  else:
   dd=np.sqrt(1-x*x+ratio*ratio*x*x);mu=ratio*x/dd;wr=w*ratio/dd**3
   R0,_,jac=geom(mu,b,a);R1,m,_=geom(mu,bf,af)
   ww=wr*jac;ww/=ww.sum(axis=1,keepdims=True);R=R1/R0
  mass=weight*ww*R;den+=mass.sum();num+=(mass*(3*m*m-1)/2).sum()
 return np.array([den,num])
ref=integrate(256,1,True);ref2=integrate(128,1,True);assert max(abs(ref/ref2-1))<1e-12
rows=[]
for n in (8,16,32,64):
 for ratio in (1.,.5):
  v=integrate(n,ratio);row=dict(n=n,map_ratio=ratio,J0=float(v[0]),J2=float(v[1]),J0_relative=float(v[0]/ref[0]-1),J2_relative=float(v[1]/ref[1]-1));rows.append(row);print(row,flush=True)
(D/'SOURCE_ONLY.json').write_text(json.dumps(dict(status='SCOPED_UNABSORBED_ACTUAL_EMISSION_HISTORY',reference=ref.tolist(),reference_128=ref2.tolist(),background_end_error=float(bf-native_b),source_hashes=src,rows=rows,scope='same actual source energy history integrated without any absorption, so not coupled J2 prediction'),indent=2)+'\n')
