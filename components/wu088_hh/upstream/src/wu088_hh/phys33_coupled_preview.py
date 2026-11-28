"""Independent NumPy/SciPy batched *diagnostic* of full angular PHYS36 residual.

No quadrature, special-function, interpolation, or roundoff certificate is
claimed here. Exact bounds are exclusively in phys33_coupled_source.py.
"""
from __future__ import annotations
from pathlib import Path
from time import perf_counter
import numpy as np
from numpy.polynomial import chebyshev as ch
from numpy.polynomial.legendre import leggauss
from scipy.special import eval_legendre

from .phys33_residual import DEGREE,L_MAX,load_frozen


def coupled_residual_preview(path: str|Path, nr:int=80, nmu:int=128,
                             lam:float=1.0)->dict:
    if not 24<=nr<=1024 or not 24<=nmu<=2048 or not 0<=lam<=1:
        raise ValueError("bad diagnostic radial/angular nodes or coupling")
    begin=perf_counter()
    rnodes,unodes,digest=load_frozen(path,True)
    rnodes=rnodes.reshape(6,11)
    unodes=unodes.reshape(L_MAX+1,6,11)
    x,wx=leggauss(nr)
    mu,wmu=leggauss(nmu)
    ell=np.arange(L_MAX+1)
    P=np.stack([eval_legendre(int(l),mu) for l in ell])
    Pprev=np.vstack((np.ones_like(mu),P[:-1]))
    ynorm=np.sqrt((2*ell+1)/(4*np.pi))
    Y=ynorm[:,None]*P
    deriv_sin2=ynorm[:,None]*ell[:,None]*(Pprev-mu[None,:]*P)
    subtotal=0.0
    split=np.zeros((2,),dtype=np.float64)
    panels=[]
    R=.7
    for j in range(6):
        left,right=rnodes[j,0],rnodes[j,-1]
        h=(right-left)/2.
        mid=(right+left)/2.
        node=(rnodes[j]-mid)/h
        coefficients=np.linalg.solve(ch.chebvander(node,DEGREE),
                                     unodes[:,j,:].T)
        v=ch.chebval(x,coefficients)
        dv=ch.chebval(x,ch.chebder(coefficients,m=1,axis=0))/h
        ddv=ch.chebval(x,ch.chebder(coefficients,m=2,axis=0))/h**2
        r=(mid+h*x)
        src0=(1+.49)*np.exp(-r)/np.sqrt(np.pi)
        Du=ddv+(.49+2/r[None,:]-
                (ell*(ell+1))[:,None]/r[None,:]**2)*v
        Yraw=(v/r[None,:]).T@Y
        Yrad=(dv/r[None,:]-v/r[None,:]**2).T@Y
        Dy=(Du/r[None,:]).T@Y
        Yang=(v/r[None,:]).T@deriv_sin2
        s=np.sqrt((r[:,None]-R*mu[None,:])**2+
                  (R*R)*(1-mu[None,:]**2))
        E=np.exp(-s)
        ratio=-np.expm1(-s)/s
        U=lam*E*ratio-lam*E/2-(lam+lam*lam/2)*E*E
        shat_grad=E*((r[:,None]-R*mu[None,:])/s*Yrad
                    -R/(s*r[:,None])*Yang)
        full=Dy-2*lam*shat_grad-2*U*Yraw-(src0[:,None]*np.exp(-lam*E))
        direct=Dy-src0[:,None]
        def norm2(a):
            integrated=2*np.pi*np.sum(
                wx[:,None]*wmu[None,:]*r[:,None]**2*np.abs(a)**2)
            return float(h*integrated)
        a=norm2(full);b=norm2(direct)
        subtotal+=a;split[0]+=b
        panels.append({"panel":j,"radial":[float(left),float(right)],
                       "full_angular_residual_sampled_l2":float(np.sqrt(a)),
                       "D_minus_bare_source_sampled_l2":float(np.sqrt(b))})
    return {"schema":"WU088_HH_PHYS36_COUPLED_ANGULAR_PREVIEW_V1",
            "source_sha256":digest,"nr":nr,"nmu":nmu,"lambda":lam,
            "sampled_coupled_l2":float(np.sqrt(subtotal)),
            "sampled_D_minus_source_l2":float(np.sqrt(split[0])),
            "panels":panels,"elapsed_s":perf_counter()-begin,
            "status":"FLOAT64_FULL_SCREENED_ANGULAR_PDE_DIAGNOSTIC_NOT_CERTIFIED"}
