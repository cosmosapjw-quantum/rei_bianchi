"""Source-born potential recrossings without absorption, exact ray extrema."""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.integrate import solve_ivp,cumulative_trapezoid
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq,minimize_scalar
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent;j=json.loads((D/'gas_n16.json').read_text())
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
parts=[]
for p,h in j['sources'].items():
 assert sha(p)==h;parts.append(np.genfromtxt(p,names=True,delimiter=',',usecols=['a','source_N']))
t=np.concatenate([parts[0]]+[x[1:] for x in parts[1:]])
a0=1/21;end=np.log(21/5);u=np.log(t['a']/a0);u[0]=0.;u[-1]=end
birth=PchipInterpolator(u,t['source_N']).derivative()
def H(a):return np.sqrt(.315/a**3+9.2e-5/a**4+1-.315-9.2e-5)
def x(u):
 a=a0*np.exp(u);s=H(a0)*np.exp(-3*u);return s/np.hypot(H(a),s)
sol=solve_ivp(lambda t,y:[-x(t)],(0,end),[0.],rtol=2e-13,atol=2e-15,dense_output=True);assert sol.success
def geom(u,m):
 b=sol.sol(u)[0];g=np.sqrt((1-m*m)*np.exp(2*b)+m*m*np.exp(-4*b));return np.exp(-u)*g,m*np.exp(-2*b)/g,1/g**3
def rate(u,m):
 R,mu,j=geom(u,m);return -1+x(u)*(3*mu*mu-1)
# Planck photon-number CDF for source interval (dense independent quadrature).
e=np.linspace(13.6,100,20001);f=e*e/np.expm1(e/(8.617333262145e-5*50000))
c=cumulative_trapezoid(f,e,initial=0);cdf=PchipInterpolator(e,c/c[-1])
def frac(l,h):
 l=np.maximum(l,13.6);h=np.minimum(h,100);return np.where(h>l,cdf(np.clip(h,13.6,100))-cdf(np.clip(l,13.6,100)),0.)
# focus angular interval where two roots occur; identify bounds using max rate.
scan=np.linspace(0,end,257);mu=np.linspace(0,1,2001);rates=np.array([rate(v,mu) for v in scan])
mask=(rates[0]<0)&(rates.max(axis=0)>0)&(rates[-1]<0)
print('sampled double-extremum range',mu[mask].min() if mask.any() else None,mu[mask].max() if mask.any() else None,flush=True)
rows=[]
for n in (256,512,1024):
 xx,ww=leggauss(n);ms=(xx+1)/2;ws=ww/2;tot=np.zeros(3);count=0;maxdip=0.;minmu=1.;maxmu=0.
 gx,gw=leggauss(128)
 for m,w in zip(ms,ws):
  vals=rate(scan,m);ix=np.flatnonzero(vals[:-1]*vals[1:]<0)
  if len(ix)<2:continue
  roots=[brentq(lambda v:rate(v,m),scan[k],scan[k+1],xtol=2e-14) for k in ix]
  if not (len(roots)==2 and vals[0]<0 and vals[-1]<0):continue
  l,h=roots;rl=geom(l,m)[0];rh=geom(h,m)[0];assert rh>rl
  v=(gx+1)*l/2;ww0=gw*l/2;R,_,jac=geom(v,m);db=birth(v)*jac*ww0*w
  for k,T in enumerate((13.6,24.59,54.42)):
   lower=np.maximum(T,T*R/rh);upper=T*R/rl
   tot[k]+=db@frac(lower,upper)
  count+=1;maxdip=max(maxdip,float(rh/rl-1));minmu=min(minmu,m);maxmu=max(maxmu,m)
 row=dict(nmu=n,double_extrema_nodes=count,mu_range=[minmu,maxmu],max_rebound=maxdip,upper_counts_per_H=tot.tolist());rows.append(row);print(row,flush=True)
# Refine directly over narrow nonmonotone angular support. Peak rate is
# monotone in reference mu at fixed u. Root and extrema are independently
# located on either side of the interior peak, not uniform angular scan.
def peak(m):
 r=minimize_scalar(lambda v:-rate(v,m),bounds=(0,end),method='bounded',options={'xatol':1e-13})
 return r.x,-r.fun
lo=brentq(lambda m:peak(m)[1],.88,.89,xtol=2e-14)
hi=np.sqrt((1+1/x(0))/3)
focused=[]
for n in (16,32,64,128):
 xx,ww=leggauss(n);ms=lo+(hi-lo)*(xx+1)/2;ws=ww*(hi-lo)/2;tot=np.zeros(3)
 for m,w in zip(ms,ws):
  p,rr=peak(m);assert rr>0 and rate(0,m)<0 and rate(end,m)<0
  l=brentq(lambda t:rate(t,m),0,p,xtol=2e-14);h=brentq(lambda t:rate(t,m),p,end,xtol=2e-14)
  rl,rh=geom(l,m)[0],geom(h,m)[0]
  v=(gx+1)*l/2;R,_,jac=geom(v,m);db=birth(v)*jac*gw*l/2*w
  for k,T in enumerate((13.6,24.59,54.42)):tot[k]+=db@frac(np.maximum(T,T*R/rh),T*R/rl)
 row=dict(nmu=n,upper_counts_per_H=tot.tolist());focused.append(row);print('focused',lo,hi,row,flush=True)
(D/'RECROSS.json').write_text(json.dumps(dict(status='SCOPED_UNABSORBED_POTENTIAL_RECROSS',rows=rows,focused=focused,angular_bounds=[float(lo),float(hi)],source_hashes=j['sources'],scope='source born above threshold, later below and then above; unabsorbed characteristic count is a potential upper bound for the same prescribed birth history, not actual surviving count. Sampling is not continuum certified.'),indent=2)+'\n')
