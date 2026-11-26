"""Nonlinear finite-volume Kompaneets on a finite reflecting frequency interval."""
import numpy as np
from scipy.special import xlogy
class Kompaneets:
 def __init__(self,edges):
    self.edges=np.asarray(edges,float)
    if self.edges.ndim!=1 or len(self.edges)<3 or min(self.edges)<=0 or not np.isfinite(self.edges).all() or np.any(np.diff(self.edges)<=0):raise ValueError("grid")
    self.x=np.sqrt(self.edges[:-1]*self.edges[1:])
    self.c=np.diff(self.edges**3)/3
    self.dx=np.diff(self.x);self.faces=self.edges[1:-1]
 def eqf(self,t,mu):
    if t<=0 or np.min(self.x/t+mu)<=0:raise ValueError("equilibrium")
    return 1/np.expm1(self.x/t+mu)
 def equilibrium(self,t,mu):return self.c*self.eqf(t,mu)
 def coeff(self,t):
    if not np.isfinite(t) or t<=0:raise ValueError("temperature")
    d=self.dx/t;q=np.exp(-d);b=-np.expm1(-d)
    return q,b,self.faces**4*d/(self.dx*b)
 def rhs(self,N,t):
    q,b,g=self.coeff(t);f=N/self.c;J=g*(f[1:]-q*f[:-1]+b*f[1:]*f[:-1]);return np.r_[J,0]-np.r_[0,J]
 def entropy(self,N,t):
    f=N/self.c
    return float(np.sum(self.c*(xlogy(f,f)-xlogy(1+f,1+f)+self.x/t*f)))
 def energy(self,N):return float(self.x@N)
 def sweep(self,N,t,dt,parity):
    q,b,g=self.coeff(t);i=np.arange(parity,len(N)-1,2)
    a=N[i];M=a+N[i+1];ci=self.c[i];cj=self.c[i+1];Q=q[i];B0=b[i];G=g[i]
    A=G*B0/(ci*cj);B=G*(-1/cj-Q/ci+B0*M/(ci*cj));C=G*M/cj
    disc=np.sqrt(B*B+4*A*C)
    # Avoid subtracting roots of nearly equal magnitude. M=0 pairs are exact zeros.
    rp=np.where(B>=0,(B+disc)/(2*A),2*C/np.maximum(disc-B,np.finfo(float).tiny))
    z=-np.expm1(-disc*dt);den=disc+A*(a-rp)*z
    f=a/ci;v=(M-a)/cj;J=G*(v-Q*f+B0*f*v)
    da=np.divide(J*z,den,out=np.zeros_like(a),where=den>0)
    new=a+da
    # Roundoff-sized corrections only; no positivity projection of an invalid flow.
    tol=32*np.finfo(float).eps*M
    if np.any(new < -tol) or np.any(new>M+tol):raise ValueError("pair flow")
    new=np.minimum(M,np.maximum(0,new));N[i]=new;N[i+1]=M-new
 def advance(self,N,t,y,steps=1):
    N=np.array(N,float,copy=True)
    if N.shape!=self.x.shape or not np.isfinite(N).all() or min(N)<0 or not np.isfinite(y) or y<0 or steps<1:raise ValueError("state")
    for _ in range(steps):
      d=y/steps;self.sweep(N,t,d/2,0);self.sweep(N,t,d,1);self.sweep(N,t,d/2,0)
    return N
