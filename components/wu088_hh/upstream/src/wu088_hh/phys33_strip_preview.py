"""Vectorized noncertifying 3D finite radial strip residual diagnostic.

Integrate angularly in spectator distance s rather than mu:
 mu=(r²+R²-s²)/(2rR), dmu=-s ds/(rR).
The independent float64 Gauss preview is intentionally NOT a proof of any
error radius. Actual rigorous upper: phys33_cusp_strip.strip_certificate.
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
from .phys33_cusp_shell import R


def preview_cusp_strip(filename: str|Path,delta:F,
                       radial_nodes:int=24,s_nodes:int=96)->dict:
    if not isinstance(delta,F) or not 0<delta<R:
        raise ValueError("exact rational delta in (0,R) required")
    if not 8<=radial_nodes<=512 or not 16<=s_nodes<=1024:
        raise ValueError("unsupported float preview quadrature size")
    tic=perf_counter()
    nodes,u,digest=load_frozen(filename,True)
    swap=nodes[1,-1]  # exact stored IEEE value, not float(.7) assumed mathematical R
    ends=[
        ("left",1,float(R-delta),float(swap)),
        ("right",2,float(swap),float(R+delta)),
    ]
    zr,wr=leggauss(radial_nodes);zs,ws=leggauss(s_nodes)
    tr=(zr+1)/2;wr=wr/2
    ts=(zs+1)/2;ws=ws/2
    ell=np.arange(21)
    alpha=np.sqrt((2*ell+1)/(4*np.pi))
    summ=0.
    values=[]
    for side,j,low,high in ends:
        rr=low+(high-low)*tr
        mids=(nodes[j,0]+nodes[j,-1])/2
        half=(nodes[j,-1]-nodes[j,0])/2
        colloc=(nodes[j]-mids)/half
        co=np.linalg.solve(chebvander(colloc,10),u[:,j,:].T)
        x=(rr-mids)/half
        v=chebval(x,co)
        dv=chebval(x,chebder(co,m=1,axis=0))/half
        ddv=chebval(x,chebder(co,m=2,axis=0))/half**2
        lower=np.abs(rr-float(R))
        upper=rr+float(R)
        s=lower[:,None]+(upper-lower)[:,None]*ts[None,:]
        mu=(rr[:,None]**2+float(R)**2-s*s)/(2*rr[:,None]*float(R))
        mu=np.clip(mu,-1,1)
        P=np.stack([eval_legendre(int(l),mu) for l in ell])
        Pprev=np.concatenate((np.ones_like(P[:1]),P[:-1]),axis=0)
        Y=alpha[:,None,None]*P
        T=alpha[:,None,None]*ell[:,None,None]*(Pprev-mu[None,:,:]*P)
        def projected(arr):
            return np.einsum("lr,lrs->rs",arr,Y,optimize=True)
        raw=projected(v/rr[None,:])
        radial=projected(dv/rr[None,:]-v/rr[None,:]**2)
        dual=(v/rr[None,:])
        tang=np.einsum("lr,lrs->rs",dual,T,optimize=True)
        diag=projected((ddv+(.49+2/rr[None,:]-
            ell[:,None]*(ell[:,None]+1)/rr[None,:]**2)*v)/rr[None,:])
        E=np.exp(-s)
        U=E*(-np.expm1(-s))/s-E/2-1.5*E*E
        shat=((rr[:,None]-float(R)*mu)/s)*radial-float(R)/(rr[:,None]*s)*tang
        src=1.49*np.exp(-rr)[:,None]/np.sqrt(np.pi)*np.exp(-E)
        strong=diag-2*E*shat-2*U*raw-src
        angular=np.sum(ws[None,:]*(upper-lower)[:,None]*
              s/(rr[:,None]*float(R))*np.abs(strong)**2,axis=1)
        integrated=2*np.pi*(high-low)*np.sum(wr*rr*rr*angular)
        summ+=integrated
        values.append({"side":side,"sampled_volume_L2":float(np.sqrt(max(0,integrated)))})
    return {"schema":"WU088_HH_PHYS38_S_SPECTATOR_COORDINATE_FLOAT_DIAGNOSTIC_V1",
            "input_sha256":digest,"delta":str(delta),"radial_nodes":radial_nodes,
            "spectator_distance_nodes":s_nodes,
            "whole_strip_sampled_L2":float(np.sqrt(max(summ,0))),
            "one_sided":values,"seconds":perf_counter()-tic,
            "status":"NONCERTIFYING_FLOAT64_DOUBLE_GAUSS_PREVIEW"}
