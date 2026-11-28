"""PHYS26: finite-momentum direct vertex in the declared S65 model.

All microscopic distances and momenta are dimensionless: R/a0, a0*p/hbar.
This is a research quadrature, not a calibrated physical cross-section provider.
Reported floating-point values are not automatically interval certificates.
"""
from functools import lru_cache
import numpy as np
from scipy.special import roots_legendre, gammainc

A0_M=5.29177210544e-11
I_EV=13.605693122990
KB=1.380649e-23
EVJ=1.602176634e-19
MH=1.67262192369e-27
T_BOX=(49999.63846,50000.36154)

@lru_cache(None)
def gauss(n):
    if n < 2: raise ValueError('Gauss order must be >= 2')
    return roots_legendre(n)

def potential(r, spin):
    r=np.asarray(r)
    if spin=='triplet':
        u=3.6*np.exp(-1.48*r); return u,-1.48*u
    if spin=='singlet':
        z=np.exp(-1.08*(r-1.5)); return .35*(z*z-2*z),.756*(z-z*z)
    raise ValueError('Unknown spin')

def turning(e,spin):
    if not 1 <= e <= 2: raise ValueError('Source domain is 1 <= E/I <= 2')
    if spin=='triplet': return np.log(3.6/e)/1.48
    if spin=='singlet': return 1.5-np.log1p(np.sqrt(1+e/.35))/1.08
    raise ValueError('Unknown spin')

def screen(r):
    r=np.asarray(r);return (1+1/r)*np.exp(-2*r)

def c0(r):
    r=np.asarray(r)
    return np.exp(-r)*(7/18-11/(27*r))+np.exp(-2*r)*(1/9+11/(27*r))

def parameter_density(y,k,r):
    """Nonnegative real Feynman density on y in [0,1]."""
    lam=np.sqrt(4-3*y+y*(1-y)*k*k)
    z=lam*r
    return np.exp(-z)*(y*(1+z)/(4*lam**3)+y*(1-y)*(3+3*z+z*z)/(2*lam**5))

def vertex(k,r,mu,ny=48):
    if not 0 <= k <= 1: raise ValueError('Source k range is [0,1]')
    r=np.atleast_1d(r).astype(float);mu=np.atleast_1d(mu).astype(float)
    if np.any(r<=0) or np.any(abs(mu)>1):raise ValueError('R>0 and |mu|<=1 required')
    yy,ww=gauss(ny); y=(yy+1)/2; w=ww/2
    g=parameter_density(y[None,:],k,r[:,None])*w[None,:]
    z=np.exp(-1j*k*r[:,None,None]*y[None,:,None]*mu[None,None,:])
    return np.einsum('ry,rym->rm',g,z)

def amplitude_average(k,r,ny=48,nmu=24,restore=True):
    r=np.atleast_1d(r)
    a=screen(r)/(1+k*k)**2
    if not restore:return a*a
    mu,w=gauss(nmu)
    c=vertex(k,r,mu,ny)
    return np.sum(abs(a[:,None]-c)**2*w[None,:]/2,axis=1)

def sigma(e,spin='unpolarized',nk=40,nr=96,ny=48,nmu=24,Rmax=20.,restore=True):
    if not 1<=e<=2:raise ValueError('No tail extrapolation')
    if e==1:return 0.
    if spin=='unpolarized':return (sigma(e,'singlet',nk,nr,ny,nmu,Rmax,restore)+3*sigma(e,'triplet',nk,nr,ny,nmu,Rmax,restore))/4
    x,w=gauss(nk);ks=(x+1)*np.sqrt(e-1)/2;wk=w*np.sqrt(e-1)/2
    xr,wr=gauss(nr);rmin=turning(e,spin);rs=rmin+(xr+1)*(Rmax-rmin)/2;wr=wr*(Rmax-rmin)/2
    u,up=potential(rs,spin);j=1-(u+rs*up/2)/e
    if np.min(j)<=0:raise ArithmeticError('nonpositive path Jacobian')
    return 256*sum(wki*ki**2/(1+ki*ki)**2*np.sum(wr*rs*j*amplitude_average(ki,rs,ny,nmu,restore)) for ki,wki in zip(ks,wk))

def maxwell_energy_weight(q,e0,v):
    """Integral_e0^2 (e-v) exp(-q e) de, positive and cancellation-aware."""
    d=np.maximum(0.,2-e0);x=q*d
    return np.exp(-q*e0)*((e0-v)*(-np.expm1(-x))/q+gammainc(2,x)/q**2)

def partial_rate(T,spin='unpolarized',nk=40,nr=80,ny=48,nmu=24,Rmax=20.,restore=True):
    if T<=0:raise ValueError('T must be positive')
    if spin=='unpolarized':return (partial_rate(T,'singlet',nk,nr,ny,nmu,Rmax,restore)+3*partial_rate(T,'triplet',nk,nr,ny,nmu,Rmax,restore))/4
    theta=KB*T/EVJ;q=I_EV/theta
    pref=100*np.sqrt(8*EVJ/(np.pi*(MH/2)))*theta**(-1.5)*(100*A0_M)**2*I_EV**2*256
    x,w=gauss(nk);ks=(x+1)/2;wk=w/2
    xr,wr=gauss(nr);r0=turning(2.,spin);total=0.
    for k,wk0 in zip(ks,wk):
        split=turning(1+k*k,spin);acc=0.
        for lo,hi in ((r0,split),(split,Rmax)):
            r=lo+(xr+1)*(hi-lo)/2;weight=wr*(hi-lo)/2
            u,up=potential(r,spin);v=u+r*up/2;e0=np.maximum(1+k*k,u)
            mw=maxwell_energy_weight(q,e0,v)
            acc+=np.sum(weight*r*mw*amplitude_average(k,r,ny,nmu,restore))
        total+=wk0*k*k/(1+k*k)**2*acc
    return pref*total

if __name__=='__main__':
    import json,time,pathlib
    t=time.monotonic(); rows=[]
    for n in [16,24,32,48]:
        s=partial_rate(50000.,'singlet',nk=n,nr=2*n,ny=n,nmu=max(12,n//2))
        tr=partial_rate(50000.,'triplet',nk=n,nr=2*n,ny=n,nmu=max(12,n//2))
        rows.append(dict(n=n,singlet=s,triplet=tr,unpolarized=(s+3*tr)/4))
        print(rows[-1],flush=True)
    out=dict(refinement=rows,elapsed_s=time.monotonic()-t,
       scope='numerical quadrature; no rigorous outer discretization or roundoff certificate yet')
    pathlib.Path(__file__).with_name('results').joinpath('REFINEMENT.json').write_text(json.dumps(out,indent=2))
    print(out['elapsed_s'])
