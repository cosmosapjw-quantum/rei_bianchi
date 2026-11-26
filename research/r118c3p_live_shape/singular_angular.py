"""Diagnose singular angular mixing in adjacent-frequency cross-angle closure.
The test is about the conditional discrete kernel, not physical Compton scattering.
"""
import numpy as np,json
from pathlib import Path
from numpy.polynomial.legendre import leggauss
D=Path(__file__).resolve().parent
def run():
 mu,w=leggauss(8);w=w/2
 # axisymmetric azimuth average of 3/4(1+c²)(1-c).
 ph=np.arange(64)*2*np.pi/64
 cs=mu[:,None,None]*mu[None,:,None]+np.sqrt(1-mu[:,None,None]**2)*np.sqrt(1-mu[None,:,None]**2)*np.cos(ph)[None,None,:]
 K=np.mean(.75*(1+cs*cs)*(1-cs),axis=2);M=w[:,None]*w[None,:]*K
 assert max(abs(M.sum(axis=1)-w))<1e-14
 P2=(3*mu*mu-1)/2;assert max(abs(M@P2-.1*w*P2))<1e-14
 rows=[]
 for n in [128,256,512,1024]:
  dl=np.log(60/1e-3)/n;x=1e-3*np.exp((np.arange(n)+.5)*dl);f0=1/np.expm1(x);theta=.4
  # Smooth compact-ish log-Gaussian with negligible endpoint occupation.
  v=1e-3*np.exp(-.5*(np.log(x)/.6)**2)
  delta=P2[:,None]*v[None,:];s=np.zeros_like(delta);sing=s.copy()
  dx=np.diff(x);b=-np.expm1(-dx/theta);q=np.exp(-dx/theta);g=(x[:-1]*x[1:])**2/(theta*b)
  for j in range(n-1):
   U,V=delta[:,j],delta[:,j+1]
   t=M*g[j]*((1+b[j]*f0[j])*V[None,:]+(-q[j]+b[j]*f0[j+1])*U[:,None]+b[j]*U[:,None]*V[None,:])
   s[:,j]+=t.sum(axis=1);s[:,j+1]-=t.sum(axis=0)
  s-=w[:,None]*s.sum(axis=0)
  gs=np.r_[0,g]+np.r_[g,0]
  sing=(M@delta-w[:,None]*delta)*gs[None,:]
  residual=s-sing
  l1=lambda v:float(np.sum(abs(v)))
  rows.append(dict(bins=n,dl=dl,full_l1=l1(s),singular_l1=l1(sing),residual_l1=l1(residual),singular_fraction=l1(sing)/l1(s),residual_fraction=l1(residual)/l1(s),full_scaled_dl2=l1(s)*dl*dl,energy_res_relative=float(abs(np.sum(s*x))/np.sum(abs(s)*x))))
 assert rows[-1]['residual_fraction']<rows[0]['residual_fraction'] and rows[-1]['full_l1']/rows[-2]['full_l1']>3.8
 o=dict(rows=rows,scope='manufactured smooth pure quadrupole on fixed physical frequency domain; adjacent-bin conditional angular-energy closure has artificial same-frequency angular diffusion scaling dl^-2; subtraction diagnostic, not proposed positive physical kernel')
 (D/'SINGULAR_ANGULAR.json').write_text(json.dumps(o,indent=2)+'\n');print(o,flush=True)
if __name__=='__main__':run()
