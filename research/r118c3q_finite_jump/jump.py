"""Classical reversible finite-rate log-frequency jump, conditional Thomson model."""
import numpy as np
from scipy.special import ndtr
from numpy.polynomial.legendre import leggauss
def proposal(y,sigma):
 # Symmetric translation-invariant Gaussian center-to-cell probabilities.
 # Reject out-of-domain proposals. Cut at 8 sigma; no renormalization.
 dy=y[1]-y[0];kmax=min(len(y)-1,int(np.ceil(8*sigma/dy+.5)))
 if sigma==0:return [(0,1.)]
 k=np.arange(kmax+1);p=ndtr((k+.5)*dy/sigma)-ndtr((k-.5)*dy/sigma)
 return [(int(i),float(v)) for i,v in zip(k,p) if v>0]
def ray_grid(nmu):
 mu,w=leggauss(nmu);m,ph=np.meshgrid(mu,np.arange(2*nmu)*np.pi/nmu,indexing='ij')
 n=np.stack([np.sqrt(1-m*m)*np.cos(ph),np.sqrt(1-m*m)*np.sin(ph),m],axis=-1).reshape(-1,3)
 return n,np.repeat(w/(4*nmu),2*nmu)
def kernel(x,n,w,theta,Tratio,F,R):
 # Signed dN per unit Thomson optical depth; no physical density factor.
 # Detailed balance conductance built with symmetric proposals and actual
 # cell capacities, using stable full-minus-reference paired flux.
 x=np.asarray(x);y=np.log(x);dy=y[1]-y[0];assert max(abs(np.diff(y)-dy))<1e-10*dy
 nr=len(w);C=w[:,None]*x**3*dy;d=F-R
 out=np.zeros_like(d);full=np.zeros_like(d);ref=np.zeros_like(d);loss=np.zeros_like(d)
 Q=0.;absflux=0.
 for i in range(nr):
  for j in range(i,nr):
   mu=float(np.clip(n[i]@n[j],-1,1));K=.75*(1+mu*mu);sigma=np.sqrt(2*theta*max(0.,1-mu))
   for kk,p in proposal(y,sigma):
    for k in ([0] if kk==0 else [-kk,kk]):
     if i==j and k<=0:continue
     a=slice(max(0,-k),min(len(x),len(x)-k));b=slice(max(0,k),min(len(x),len(x)+k))
     u,v=x[a],x[b];dg=(v-u)/Tratio
     # directed rate capped by Gaussian proposal * Thomson angular probability.
     logratio=3*np.log(v/u)-dg
     rate=K*p*w[i]*w[j]*np.minimum(u**3,v**3*np.exp(-dg))*dy
     back=rate*np.exp(dg)
     # c_i R_ij = rate, c_j R_ji = back; physical finite total rate.
     fa,fb=F[i,a],F[j,b];ra,rb=R[i,a],R[j,b];da,db=d[i,a],d[j,b]
     # exact full/reference difference without subtracting full fluxes
     z=rate*(da*(1+rb)+ra*db+da*db)-back*(db*(1+ra)+rb*da+db*da)
     # for small dg use expm1 to avoid Bose cancellation.
     z=rate*(da-db-np.expm1(dg)*(db*(1+ra)+rb*da+da*db))
     # identity: f_a(1+f_b)-f_b(1+f_a)=f_a-f_b.
     q=rate*(fa-fb-np.expm1(dg)*fb*(1+fa))
     r=rate*(ra-rb-np.expm1(dg)*rb*(1+ra))
     out[i,a]-=z;out[j,b]+=z;full[i,a]-=q;full[j,b]+=q;ref[i,a]-=r;ref[j,b]+=r
     loss[i,a]+=rate/C[i,a];loss[j,b]+=back/C[j,b]
     Q+=float(np.sum((v-u)*z));absflux+=float(np.sum(abs(z)))
 return out,full,ref,dict(number=float(out.sum()),energy=float(np.sum(out*x)),pair_energy=Q,absflux=absflux,max_rate=float(loss.max()))
def test():
 x=np.exp(np.linspace(-1,1,192));n,w=ray_grid(2);T=.7;f=1/np.expm1(x/T+.15);F=np.broadcast_to(f,(len(w),len(x))).copy();R=np.zeros_like(F)
 y,full,ref,a=kernel(x,n,w,.002,T,F,R)
 assert a['max_rate']<=1+1e-13 and abs(y.sum())<1e-14 and np.max(abs(y))<1e-14
 return a
if __name__=='__main__':print(test())
