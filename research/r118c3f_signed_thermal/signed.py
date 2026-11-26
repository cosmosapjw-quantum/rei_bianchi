"""Stable signed perturbation about Planck, nonlinear finite reflecting FV."""
import numpy as np
from pathlib import Path
from scipy.interpolate import RegularGridInterpolator
from scipy.integrate import simpson
class SignedKompaneets:
 def __init__(self,edges):
    self.edges=np.asarray(edges,float)
    if len(self.edges)<3 or min(self.edges)<=0 or np.any(np.diff(self.edges)<=0):raise ValueError("grid")
    self.x=np.sqrt(self.edges[:-1]*self.edges[1:]);self.c=np.diff(self.edges**3)/3;self.dx=np.diff(self.x);self.faces=self.edges[1:-1];self.f0=1/np.expm1(self.x)
 def coeff(self,t):
    d=self.dx/t;q=np.exp(-d);b=-np.expm1(-d);G=self.faces**4*d/(self.dx*b)
    # baseline J evaluated without cancellation; exact zero at theta=1
    J0=-G*self.f0[:-1]*(1+self.f0[1:])*np.exp(-self.dx)*np.expm1(self.dx*(1-1/t))
    return q,b,G,J0
 def flux(self,d,t):
    q,b,g,j=self.coeff(t);u=d/self.c;f=self.f0
    return j+g*((1+b*f[:-1])*u[1:]+(-q+b*f[1:])*u[:-1]+b*u[:-1]*u[1:])
 def rhs(self,d,t):
    J=self.flux(d,t);return np.r_[J,0]-np.r_[0,J]
 def sweep(self,d,t,dt,parity):
    q,b,G,J0=self.coeff(t);i=np.arange(parity,len(d)-1,2)
    ci,cj=self.c[i],self.c[i+1];fi,fj=self.f0[i],self.f0[i+1];u=d[i]/ci;v=d[i+1]/cj
    Q,B0,g=q[i],b[i],G[i];J=J0[i]+g*((1+B0*fi)*v+(-Q+B0*fj)*u+B0*u*v)
    fi=fi+u;fj=fj+v;M=ci*fi+cj*fj
    A=g*B0/(ci*cj);B=g*(-(1+B0*fi)/cj+(-Q+B0*fj)/ci)
    # Equivalent non-cancelling discriminant evaluated in total-stock variables.
    Btot=g*(-1/cj-Q/ci+B0*M/(ci*cj));C=g*M/cj
    disc=np.sqrt(Btot**2+4*A*C);z=-np.expm1(-disc*dt)
    den=disc*(2-z)-B*z
    da=np.divide(2*J*z,den,out=np.zeros_like(J),where=den>0)
    if np.any(den<=0):raise ValueError("pair discriminant")
    lo=-ci*fi;hi=cj*fj;tol=64*np.finfo(float).eps*M
    if np.any(da<lo-tol) or np.any(da>hi+tol):raise ValueError("pair domain")
    da=np.minimum(hi,np.maximum(lo,da))
    d[i]+=da;d[i+1]-=da
    return float(-self.dx[i]@da)
 def advance(self,d,t,y,steps=1):
    d=np.array(d,float,copy=True)
    if not np.isfinite(t) or t<=0 or not np.isfinite(y) or y<0 or d.shape!=self.x.shape or not np.isfinite(d).all() or min(self.f0+d/self.c)<0 or steps<1:raise ValueError("state")
    U=0.
    for _ in range(steps):
      h=y/steps;U+=self.sweep(d,t,h/2,0);U+=self.sweep(d,t,h,1);U+=self.sweep(d,t,h/2,0)
    return d,U
class FreeFree:
 def __init__(self,path,grid):
    self.grid=grid
    r=np.array([list(map(float,l.split('#')[0].split())) for l in Path(path).read_text().splitlines() if len(l.split('#')[0].split())==81][:146])
    self.interp=RegularGridInterpolator((-16+.2*np.arange(146),-6+.2*np.arange(81)),r)
    self.X=np.geomspace(1e-10,60,4097)
 def g(self,u,t,f):
    a=np.log10(u);b=np.log10(13.605693122994/(8.617333262145e-5*t))
    return (1-f)*self.interp(np.c_[a,np.full_like(a,b)])+f*self.interp(np.c_[a,np.full_like(a,b+np.log10(4.))])
 def norm(self,t,f):return simpson(self.g(self.X,t,f)*np.exp(-self.X)*self.X,x=np.log(self.X))
 def advance(self,d,t,tc,frac,birth,bb):
    s=self.grid;x=s.x;v=x*tc/t;G=self.norm(t,frac);scale=bb*15/np.pi**4
    amp=birth*tc/t*self.g(v,t,frac)*np.diff(s.edges)/G
    P=scale*x*s.c;tau=amp*(-np.expm1(-v))/P
    fe=1/np.expm1(v);fp=s.f0;eq=fe-fp
    a=-np.expm1(-tau);inc=(s.c*eq-d)*a
    dn=d+inc
    if min(fp+dn/s.c)<-1e-12:raise ValueError("FF domain")
    return dn,float(scale*(x@inc)),float(inc.sum()),float(np.max(tau))
