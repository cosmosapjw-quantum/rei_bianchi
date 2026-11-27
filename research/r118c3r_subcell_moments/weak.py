"""Continuous-pair weak moments on coarse log-frequency cells.
Symmetric finite Doppler jump proposal; exact pair detailed balance.
Integrate source/target boundaries separately, keep energy within same cell.
"""
import numpy as np,json
from numpy.polynomial.legendre import leggauss
from numpy.polynomial.hermite import hermgauss
from scipy.interpolate import PchipInterpolator
def moments(edges,n,w,theta,tr,delta,reference,neta=8,ny=3,full=False):
 # delta, reference: callables(y)-> [nr,N]; reference(y) includes normalized directional Planck.
 # Integrate positive eta, all ordered angle pairs, plus eta=0 elastic limit.
 nr=len(w);nc=len(edges)-1;xc=np.exp((edges[:-1]+edges[1:])/2)
 N=np.zeros((nr,nc),np.longdouble);U=np.zeros_like(N);E=np.longdouble(0);l1=np.longdouble(0);sameE=np.longdouble(0);num_rate=0.
 z,v=hermgauss(neta);v/=np.sqrt(np.pi);gz,gw=leggauss(ny)
 # Group identical angle cosines for efficiency; only approximate for machine precision duplicates.
 mu=np.clip(n@n.T,-1,1);groups={}
 for i in range(nr):
  for j in range(nr):
   if mu[i,j]>=1-1e-14:continue
   groups.setdefault(round(float(mu[i,j]),13),[]).append((i,j))
 for m,pairs in groups.items():
  ii,jj=np.array(pairs).T;K=.75*(1+m*m);sig=np.sqrt(2*theta*(1-m))
  for k in range(neta):
   if z[k]<=0:continue
   eta=float(np.sqrt(2)*sig*z[k]);lo=edges[0];hi=edges[-1]-eta
   if hi<=lo:continue
   split=np.unique(np.r_[edges[(edges>=lo)&(edges<=hi)],(edges-eta)[(edges-eta>=lo)&(edges-eta<=hi)],lo,hi])
   left,right=split[:-1],split[1:];mid=(left+right)/2;span=right-left
   y=(mid[:,None]+.5*span[:,None]*gz).ravel();qy=(.5*span[:,None]*gw).ravel()
   b=y+eta;xx=np.exp(y);yy=np.exp(b);dx=xx*np.expm1(eta);dg=dx/tr
   A=np.searchsorted(edges,y,side='right')-1;B=np.searchsorted(edges,b,side='right')-1
   da,db=delta(y)[ii],delta(b)[jj];ra,rb=reference(y)[ii],reference(b)[jj]
   C=(K*v[k]*w[ii]*w[jj])[:,None]*(qy*np.minimum(xx**3,yy**3*np.exp(-dg)))[None,:]
   if full:
    fa=ra+da;fb=rb+db;flux=C*(fa-fb-np.expm1(dg)*fb*(1+fa))
   else:flux=C*(da-db-np.expm1(dg)*(db*(1+ra)+rb*da+da*db))
   flux=flux.astype(np.longdouble);dx=dx.astype(np.longdouble)
   for r,(i,j) in enumerate(pairs):
    t=flux[r];np.add.at(N[i],A,-t);np.add.at(N[j],B,t)
    np.add.at(U[i],A,-t*(xx-xc[A]));np.add.at(U[j],B,t*(yy-xc[B]))
   E+=np.sum(flux*dx);sameE+=np.sum(flux[:,A==B]*dx[A==B]);l1+=np.sum(abs(flux))
 # zero-width forward direction has i=j only and cancels. With theta>0 all
 # non-forward angles covered by half-Gaussian and symmetric ordered pairs.
 total=U+N*xc
 # independently reconstruct total moment. Centered U carries subcell transfer.
 err=float(abs(np.sum(total)-E));assert abs(N.sum())<1e-11*max(l1,1e-300) and err<1e-10*max(l1*xc.max(),1e-300)
 P=(n.T*np.sum(total,axis=1))@n;Pi=P-np.eye(3)*np.trace(P)/3
 return N,U,dict(N_res=float(N.sum()),energy=float(E),energy_reconstructed=float(total.sum()),energy_res=err,same_cell_energy=float(sameE),L1=float(np.sum(abs(N))),Pi=float(np.sqrt(np.sum(Pi*Pi))),absflux=float(l1))
def test():
 from numpy.polynomial.legendre import leggauss
 mu,w=leggauss(3);n=np.stack([np.sqrt(1-mu*mu),mu*0,mu],axis=1);w=w/2
 # use actual symmetric ray grid instead of meridian-only grid.
 import sys
 from pathlib import Path
 sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'r118c3q_finite_jump'))
 from jump import ray_grid
 n,w=ray_grid(3);tr=.7
 R=lambda y:np.broadcast_to(1/np.expm1(np.exp(y)/tr+.2),(len(n),len(y)))
 d=lambda y:np.zeros((len(n),len(y)))
 a,b,q=moments(np.linspace(-2,1,33),n,w,1e-4,tr,d,R,8,3,True)
 assert q['L1']<1e-14 and abs(q['energy'])<1e-14
 return q
if __name__=='__main__':print(test())
