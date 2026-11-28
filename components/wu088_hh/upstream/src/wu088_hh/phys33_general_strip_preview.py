"""Fast independent float64 3D s-Gauss diagnostic for a non-cusp radial strip.

Numerical diagnostic ONLY; rigorous result is phys33_full_radial_strip.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.special import eval_legendre
from numpy.polynomial.chebyshev import chebvander,chebval,chebder
from numpy.polynomial.legendre import leggauss

from .phys33_residual import load_frozen


def preview_general_strip(frozen:str|Path,anchor:F,delta:F,
                           nr:int=40,ns:int=128)->dict:
    if not isinstance(anchor,F) or not isinstance(delta,F) or not (anchor>delta>0):
        raise ValueError("exact positive anchor and strip width required")
    if not 12<=nr<=1024 or not 24<=ns<=2048:
        raise ValueError("diagnostic Gauss grid outside useful range")
    tic=perf_counter()
    radii,us,digest=load_frozen(frozen,True)
    low,high=float(anchor-delta),float(anchor+delta)
    panels=[j for j in range(6) if low>=radii[j,0] and high<=radii[j,-1]]
    if len(panels)!=1:
        raise ValueError("strip must remain in exactly one actual frozen panel")
    j=panels[0]
    lo,hi=radii[j,0],radii[j,-1]
    mid,half=(lo+hi)/2,(hi-lo)/2
    co=np.linalg.solve(chebvander((radii[j]-mid)/half,10),us[:,j,:].T)
    zr,wr=leggauss(nr); zs,ws=leggauss(ns)
    rr=(low+high)/2+(high-low)*zr/2
    v=chebval((rr-mid)/half,co)
    dv=chebval((rr-mid)/half,chebder(co,m=1,axis=0))/half
    d2v=chebval((rr-mid)/half,chebder(co,m=2,axis=0))/half**2
    ell=np.arange(21)
    R=.7
    sa=np.abs(rr-R);sb=rr+R
    ss=sa[:,None]+(sb-sa)[:,None]*(zs[None,:]+1)/2
    ww=(sb-sa)[:,None]*ws[None,:]/2
    mu=(rr[:,None]**2+R**2-ss**2)/(2*rr[:,None]*R)
    mu=np.clip(mu,-1,1)
    P=np.stack([eval_legendre(int(l),mu) for l in ell])
    prev=np.concatenate([np.ones_like(P[:1]),P[:-1]],axis=0)
    Yn=np.sqrt((2*ell+1)/(4*np.pi))[:,None,None]
    Y=Yn*P
    T=Yn*ell[:,None,None]*(prev-mu[None,:,:]*P)
    def proj(arr):return np.einsum("lr,lrs->rs",arr,Y,optimize=True)
    raw=proj(v/rr[None,:])
    rad=proj(dv/rr[None,:]-v/rr[None,:]**2)
    D=proj((d2v+(.49+2/rr[None,:]-ell[:,None]*(ell[:,None]+1)/rr[None,:]**2)*v)/rr[None,:])
    tang=np.einsum("lr,lrs->rs",v/rr[None,:],T,optimize=True)
    E=np.exp(-ss)
    U=E*(-np.expm1(-ss))/ss-E/2-1.5*E*E
    h=(rr[:,None]-R*mu)/ss*rad-R/(rr[:,None]*ss)*tang
    source=1.49*np.exp(-rr)[:,None]/np.sqrt(np.pi)*np.exp(-E)
    residual=D-2*E*h-2*U*raw-source
    integral=2*np.pi*(high-low)/2 * np.sum(
        wr[:,None]*ww*ss*rr[:,None]/R*np.abs(residual)**2)
    return {
        "schema":"WU088_HH_PHYS40_NONCERTIFIED_ARBITRARY_RADIUS_STRIP_GAUSS_V1",
        "anchor":str(anchor),"delta":str(delta),"panel":j,
        "input_sha256":digest,"nr":nr,"ns":ns,
        "sampled_volume_L2":float(np.sqrt(integral)),
        "seconds":perf_counter()-tic,
        "status":"NONCERTIFYING_FLOAT64_3D_COUPLED_GAUSS"
    }
