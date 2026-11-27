"""Log/linear coordinate refinement of conditional transverse DSF."""
import json,numpy as np
from pathlib import Path
from scipy.special import wofz
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def calc(beta,Q,n):
 z,w=leggauss(n);x0=min(Q*Q,1.)
 x=(1+z)*x0/2
 y0=np.log(x0);ys=np.linspace(y0,np.log(8.),max(2,int(np.ceil(np.log(8./x0)))+1))
 xx=[x];ww=[w*x0/2]
 for a,b in zip(ys[:-1],ys[1:]):
  xx.append(np.exp((a+b)/2+(b-a)/2*z));ww.append(w*(b-a)/2*xx[-1])
 x=np.concatenate(xx);w=np.concatenate(ww)
 Om=Q*beta*x;Z=1j*np.sqrt(np.pi)*wofz(x/np.sqrt(2));a=Q*Q-Om*Om;den=a-x*Z/np.sqrt(2)
 f=2*np.exp(-x*x/2)/np.sqrt(2*np.pi)
 return np.array([np.dot(w,f*abs(a/den)**2),beta**2*np.dot(w,f*abs(Q*(1+a)/den)**2)])
def run():
 old=json.loads((D/'CURRENT_DSF.json').read_text());out=[]
 for r in old['rows']:
  b,Q=r['beta'],r['Qc_over_wp'];x=calc(b,Q,32);y=calc(b,Q,64)
  err=np.max(abs(x-y)/abs(y));assert err<1e-10
  out.append(dict(beta=b,Q=Q,current=float(y[0]),vorticity=float(y[1]),quadrature_rel=float(err),asymptotic_current_rel=float(abs(y[0]-Q*Q/(1+Q*Q))/(Q*Q/(1+Q*Q))),old_current_relative=float(abs(y[0]-r['current_power_factor'])/y[0])))
 (D/'CURRENT_DSF_REFINED.json').write_text(json.dumps(dict(rows=out,scope='conditional electron-only collisionless dressing, finite frequency range, log-resolved narrow magnetostatic region'),indent=2)+'\n')
 print(out)
if __name__=='__main__':run()
