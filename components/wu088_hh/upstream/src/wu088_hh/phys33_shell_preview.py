"""Fast NON-CERTIFYING x=s/(2R) shell quadrature.

Special coordinates eliminate the sqrt cusp for r=R and expose the
one-sided polynomial radial second-derivative jump. Separate from exact
Fraction/Taylor enclosure in phys33_cusp_shell.py.
"""
from __future__ import annotations
from pathlib import Path
from time import perf_counter
import numpy as np
from numpy.polynomial import chebyshev as ch
from numpy.polynomial.legendre import leggauss
from scipy.special import eval_legendre
from .phys33_residual import load_frozen


def cusp_shell_preview(filename:str|Path,side:str,nx:int=64)->dict:
    if side not in ("left","right") or not 20<=nx<=1024:
        raise ValueError("one-sided radial trace and angular nodes required")
    tic=perf_counter()
    r,u,sha=load_frozen(filename,True)
    j=1 if side=="left" else 2
    lo,hi=r[j,0],r[j,-1]
    mid,half=(lo+hi)/2,(hi-lo)/2
    coeff=np.linalg.solve(ch.chebvander((r[j]-mid)/half,10),u[:,j,:].T)
    xx=(.7-mid)/half
    radial=ch.chebval(xx,coeff)
    p1=ch.chebval(xx,ch.chebder(coeff,m=1,axis=0))/half
    p2=ch.chebval(xx,ch.chebder(coeff,m=2,axis=0))/half**2
    y,w=leggauss(nx)
    y=(y+1)/2;w=w/2
    mu=1-2*y*y
    s=1.4*y
    ell=np.arange(21)
    polys=np.stack([eval_legendre(int(v),mu) for v in ell])
    prev=np.vstack([np.ones(nx),polys[:-1]])
    norm=np.sqrt((2*ell+1)/(4*np.pi))[:,None]
    harm=norm*polys
    yval=(radial/.7)@harm
    radial_der=(p1/.7-radial/.7**2)@harm
    diag=(p2+(.49+2/.7-ell*(ell+1)/(.7**2))*radial)/.7@harm
    tang=(radial/.7)@(norm*ell[:,None]*(prev-mu[None,:]*polys))
    E=np.exp(-s)
    U=E*(-np.expm1(-s))/s-E/2-1.5*E*E
    H=y*radial_der-tang/s
    source=1.49*np.exp(-.7)/np.sqrt(np.pi)*np.exp(-E)
    full=diag-2*E*H-2*U*yval-source
    # Physical L2(S²)=2pi ∫_-1^1 |f(mu)|² dmu
    #       =8pi ∫_0^1 x |f(x)|² dx.
    norm2=8*np.pi*np.dot(w,y*np.abs(full)**2)
    return {"schema":"WU088_HH_PHYS37_NONCERTIFIED_CUSP_X_GAUSS_V1",
            "source_sha256":sha,"side":side,"radial_panel":j,
            "nx":nx,"sampled_L2":float(np.sqrt(norm2)),
            "elapsed_s":perf_counter()-tic,
            "status":"FLOAT64_X_GAUSS_SHELL_DIAGNOSTIC_NOT_CERTIFIED"}
