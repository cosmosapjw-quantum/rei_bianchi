"""Fast vectorised *diagnostic* of frozen PHYS34 radial polynomial components.

The NumPy Chebyshev batch route is useful for finding radial hot spots and
choosing a rigorous bound, but floating Gauss quadrature is NOT a certificate.
Exact-rational sci certifier remains phys33_moments.py.
"""
from __future__ import annotations

from pathlib import Path
import time

import numpy as np
from numpy.polynomial import chebyshev as ch
from numpy.polynomial.legendre import leggauss

from .phys33_residual import load_frozen, L_MAX, PANEL_COUNT, DEGREE


def preview_components(filename: str | Path, quadrature_nodes: int=96) -> dict:
    if quadrature_nodes < 16 or quadrature_nodes > 1024:
        raise ValueError("quadrature_nodes in [16,1024]")
    ts=time.perf_counter()
    radial,u,identity=load_frozen(filename,True)
    u=u.reshape(L_MAX+1,PANEL_COUNT,DEGREE+1)
    nodes,weights=leggauss(quadrature_nodes)
    diagonal,gradient,mass,wgradient,wmass=0.,0.,0.,0.,0.
    per_panel=[]
    modes=np.arange(L_MAX+1)[:,None]
    for j in range(PANEL_COUNT):
        left,right=radial[j,0],radial[j,-1]
        half=(right-left)/2.
        mid=(right+left)/2.
        x=(radial[j]-mid)/half
        # Batch all 21 modes in one linear solve; this is true NumPy BLAS vectorisation.
        vand=ch.chebvander(x,DEGREE)
        coeff=np.linalg.solve(vand,u[:,j,:].T)  # (11,21)
        z=nodes
        val=ch.chebval(z,coeff,tensor=True)
        dval=ch.chebval(z,ch.chebder(coeff,m=1,axis=0),tensor=True)/half
        ddval=ch.chebval(z,ch.chebder(coeff,m=2,axis=0),tensor=True)/half**2
        r=mid+half*z
        dist=np.abs(r-0.7)
        screen=np.exp(-2*dist)
        D=ddval+(0.49+2/r[None,:]-modes*(modes+1)/r[None,:]**2)*val
        diag=np.sum(np.abs(D)**2,axis=0)
        grad=np.sum((np.abs(r[None,:]*dval-val)**2+
                     modes*(modes+1)*np.abs(val)**2)/r[None,:]**2,axis=0)
        state=np.sum(np.abs(val)**2,axis=0)
        local=[float(half*np.dot(weights,x)) for x in
               (diag,grad,state,screen*grad,screen*state)]
        diagonal+=local[0];gradient+=local[1];mass+=local[2]
        wgradient+=local[3];wmass+=local[4]
        per_panel.append({"panel":j,"r":[float(left),float(right)],
                          "D_l2_sampled":float(np.sqrt(local[0])),
                          "screened_grad_l2_sampled":float(np.sqrt(local[3])),
                          "screened_state_l2_sampled":float(np.sqrt(local[4]))})
    D,WG,WM=np.sqrt(diagonal),np.sqrt(wgradient),np.sqrt(wmass)
    return {
      "schema":"WU088_HH_PHYS35_VECTORISED_DIAGNOSTIC_V1",
      "input_sha256":identity,"quadrature_nodes":quadrature_nodes,
      "norms_sampled":{
          "coulomb_diagonal":float(D),
          "state_gradient":float(np.sqrt(gradient)),
          "state":float(np.sqrt(mass)),
          "screened_gradient":float(WG),
          "screened_state":float(WM),
          "screened_broken_bulk_triangle":float(D+2*WG+2*WM+1.49),
      },
      "panels":per_panel,"elapsed_s":time.perf_counter()-ts,
      "status":"INDEPENDENT_BATCHED_CHEBYSHEV_GAUSS_DIAGNOSTIC_NOT_CERTIFIED",
    }
