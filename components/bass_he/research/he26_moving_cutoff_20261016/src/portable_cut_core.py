"""HE26 source-only moving-cut donor. No native gas or existing photons changed."""
from math import exp, sqrt
import numpy as np

def geometry(x, q, nu):
    a=exp(-(1.+q)*x); b=exp(-(1.-2.*q)*x)
    g=sqrt(a*a*(1.-nu*nu)+b*b*nu*nu)
    return g,a*a*b/(g*g)

def angular_cuts(x,q,eref,thresholds):
    a=exp(-2*(1.+q)*x); b=exp(-2*(1.-2.*q)*x)
    if abs(b-a)<1e-17:return (-1.,1.)
    edges=[-1.,1.]
    for chi in thresholds:
        if not (np.isfinite(chi) and chi>0):raise ValueError('threshold')
        y=((chi/eref)**2-a)/(b-a)
        if 0<y<1:
            u=sqrt(y);edges.extend([-u,u])
    return tuple(sorted(set(edges)))

def children_of_cell(lo,hi,x,q,nu,angle_weight,source_lo,source_hi,
                     fit_cuts,binding_ev,shape,sigma,order=8):
    """Return positive source-child raw N/U and all species event/heat kernels.

    Source-only; `shape(E)` is spectral number weight and `sigma(E)` returns
    3 physical cm^2 values. Supports are in HE25 fixed reference energy eV.
    Counts and first moment are not inferred from original parent moments.
    """
    g,j=geometry(x,q,nu)
    left=max(lo,source_lo/g);right=min(hi,source_hi/g)
    if right<=left:return []
    cut=sorted(set([left,right]+[float(t/g) for t in fit_cuts if left<t/g<right]))
    z,w=np.polynomial.legendre.leggauss(order)
    out=[]
    for l,r in zip(cut[:-1],cut[1:]):
        energy_ref=(l+r)/2+(r-l)*z/2
        physical=energy_ref*g
        nvec=(r-l)/2*angle_weight*j*w*shape(physical)
        sig=sigma(physical)
        n=float(nvec.sum());u=float(np.dot(nvec,physical))
        photo=np.sum(nvec[:,None]*sig,axis=0)
        heat=np.sum(nvec[:,None]*sig*(physical[:,None]-binding_ev),axis=0)
        if not (n>0 and l*g-3e-12<=u/n<=r*g+3e-12):
            raise ArithmeticError('HE26_CHILD_SUPPORT')
        if np.any(photo<0) or np.any(heat<0):
            raise ArithmeticError('HE26_NEGATIVE_CHILD_RATE')
        if any(l*g<t-4e-12 and r*g>t+4e-12 for t in fit_cuts):
            raise ArithmeticError('HE26_UNSPLIT_CHILD')
        out.append(dict(low_ev=l*g,high_ev=r*g,n=n,u_ev=u,
                        photo_cm2=photo.tolist(),heat_ev_cm2=heat.tolist()))
    return out
