"""Fixed T_e=T_gamma linearized Kompaneets: finite volume, reflecting ends."""
import numpy as np
from scipy.sparse import diags
from scipy.linalg import eigh_tridiagonal
from numpy.polynomial.legendre import leggauss
class LinearKompaneets:
 def __init__(self,edges):
    e=np.asarray(edges,dtype=float)
    if len(e)<3 or min(e)<=0 or np.any(np.diff(e)<=0) or not np.isfinite(e).all():raise ValueError('edges')
    self.e=e;self.x=np.sqrt(e[:-1]*e[1:]);self.fp=1/np.expm1(self.x);self.m=self.fp*(1+self.fp)
    z,w=leggauss(8);q=(e[:-1,None]+e[1:,None])/2+np.diff(e)[:,None]*z/2
    f=1/np.expm1(q);m=f*(1+f)
    self.cap=np.sum(w*q*q*m,axis=1)*np.diff(e)/2
    q=e[1:-1];f=1/np.expm1(q)
    self.g=q**4*f*(1+f)/np.diff(self.x)
    self.d=-np.r_[self.g,0]-np.r_[0,self.g]
    self.matrix=diags([self.g/self.cap[:-1],self.d/self.cap,self.g/self.cap[1:]],[-1,0,1],format='csr')
    self.sqrt=np.sqrt(self.cap)
    self.eig,self.v=eigh_tridiagonal(self.d/self.cap,self.g/(self.sqrt[:-1]*self.sqrt[1:]))
    if max(self.eig)>1e-8:raise ValueError('positive eigenvalue')
 def direct(self,N):
    p=N/self.cap;F=self.g*np.diff(p);return np.r_[F,0]-np.r_[0,F]
 def energy_norm(self,N):return float(.5*np.sum(N*N/self.cap))
 def advance(self,N,y):
    N=np.asarray(N,dtype=float)
    if N.shape!=self.x.shape or not np.isfinite(N).all() or not np.isfinite(y) or y<0:raise ValueError('state')
    # Preserve exact null mode and evolve nonconstant signed increment.
    mean=N.sum()/self.cap.sum();n=N-mean*self.cap
    return mean*self.cap+self.sqrt*(self.v@(np.exp(self.eig*y)*(self.v.T@(n/self.sqrt))))
