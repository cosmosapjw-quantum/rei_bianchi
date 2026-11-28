"""Noncertifying independent NumPy/SciPy s-coordinate shell preview for PHYS40.

Does NOT inherit Fraction interval arithmetic, exact Taylor polynomials or
the physical error budget. It evaluates the ORIGINAL complete transformed
operator directly on the same archived radial nodal field.
"""
from __future__ import annotations

from fractions import Fraction as F
from pathlib import Path
from time import perf_counter
import numpy as np
from numpy.polynomial.chebyshev import chebvander,chebval,chebder
from numpy.polynomial.legendre import leggauss
from scipy.special import eval_legendre

from .phys33_residual import load_frozen


def preview_fixed_r(filename:str|Path,r:F,side:str|None=None,nodes:int=160)->dict:
    if not isinstance(r,F) or r<=0 or not 20<=nodes<=2048:
        raise ValueError("positive exact Fraction radius and sensible quadrature required")
    if side not in (None,"left","right"):
        raise ValueError("one-sided choice is left/right/None")
    tic=perf_counter()
    rr,u,digest=load_frozen(filename,True)
    idx=[j for j in range(6) if float(rr[j,0])<=float(r)<=float(rr[j,-1])]
    if r==F(7,10):
        j=1 if side=="left" else 2
    elif len(idx)==2:
        j=min(idx) if side=="left" else max(idx)
    elif idx:j=idx[0]
    else:raise ValueError("outside archived radial panels")
    lo,hi=float(rr[j,0]),float(rr[j,-1])
    center=(lo+hi)/2;half=(hi-lo)/2
    coord=(rr[j]-center)/half
    co=np.linalg.solve(chebvander(coord,10),u[:,j,:].T)
    x=(float(r)-center)/half
    val=chebval(x,co)
    d=chebval(x,chebder(co,m=1,axis=0))/half
    d2=chebval(x,chebder(co,m=2,axis=0))/half**2
    ell=np.arange(21)
    q,w=leggauss(nodes)
    R=.7;rv=float(r)
    a=abs(rv-R);b=rv+R
    s=a+(b-a)*(q+1)/2
    w=w*(b-a)/2
    mu=(rv*rv+R*R-s*s)/(2*rv*R)
    P=np.stack([eval_legendre(int(i),mu) for i in ell])
    prev=np.concatenate([np.ones_like(P[:1]),P[:-1]],axis=0)
    norm=np.sqrt(2*ell+1)[:,None]
    A=((d2+(.49+2/rv-ell*(ell+1)/rv**2)*val)/rv)@(norm*P)
    B=(val/rv)@(norm*P)
    C=(d/rv-val/rv**2)@(norm*P)
    T=(val/rv)@(norm*ell[:,None]*(prev-mu[None,:]*P))
    E=np.exp(-s)
    U=E*(-np.expm1(-s))/s-E/2-1.5*E*E
    H=(rv-R*mu)*C-(R/rv)*T
    G=A-2*E*H/s-2*U*B-2*(1+.49)*np.exp(-rv)*np.exp(-E)
    norm2=np.dot(w,s*np.abs(G)**2)/(2*rv*R)
    return {
       "schema":"WU088_HH_PHYS40_NONCERTIFIED_DIRECT_COUPLED_S_GAUSS_V1",
       "radius_a0":str(r),"side":side,"panel":j,
       "input_sha256":digest,"angular_nodes":nodes,
       "sampled_angular_L2":float(np.sqrt(norm2)),
       "elapsed_s":perf_counter()-tic,
       "status":"NONCERTIFYING_INDEPENDENT_FLOAT64_DIRECT_STRONG_PDE_GAUSS"
    }
