"""Opt-in Eq.(56) geometry with indexed Sturm real anchors.

The complex spectral Newton, adaptive pair continuation and regularized Simpson
rule are inherited unchanged. This module does not alter or monkey-patch the
legacy geometry, expose a probability, or infer a physical support cutoff.
"""
from __future__ import annotations
from numbers import Integral
import numpy as np
from .geometry import _advance_pair, _energy
from .spectral import validate_pair_membership_certificate
from .sturm_anchor import bound_pair


def contour_geometry(ep: dict, rho: float, *, panels: int=32,
                     anchor_sizes=(40,56,72)) -> dict:
    """Compute a finite-CF straight-line action using ordinal real-state labels."""
    if not ep['certificate']['simple_fold']:
        raise ValueError('certified simple fold required')
    validate_pair_membership_certificate(ep)
    if (isinstance(rho,(bool,np.bool_)) or not np.isscalar(rho)
        or np.iscomplexobj(rho) or not np.isfinite(rho) or rho<0
        or isinstance(panels,(bool,np.bool_)) or not isinstance(panels,Integral)
        or panels<8 or panels%2):
        raise ValueError('finite real rho>=0 and even integer panels>=8 required')
    Rc=complex(ep['R'])
    if not np.isfinite(Rc) or Rc.real<=0 or Rc.imag<=0:
        raise ValueError('finite positive-Re upper-half-plane endpoint required')
    Xc=np.sqrt(Rc*Rc-rho*rho)
    if Xc.real<0: Xc=-Xc
    if Xc.imag<=0:raise ValueError('upper-half-plane geometry required')
    x0=float(Xc.real);R0=complex(np.sqrt(x0*x0+rho*rho))
    pair=bound_pair(ep['state_a'],ep['state_b'],R0.real,Z1=ep['Z1'],Z2=ep['Z2'],sizes=anchor_sizes)
    zs=[np.array([pair[key]['p'],pair[key]['separation_lambda']],complex) for key in ('a','b')]
    # Keep the old contour-level energy-gap threshold as well as joint identity.
    if abs(_energy(zs[0],R0)-_energy(zs[1],R0))<1e-7:
        raise RuntimeError('real anchor did not produce distinct energy sheets')
    stats=dict(max_spectral_residual=0.,minimum_normalized_sheet_gap=float('inf'),
               accepted_continuation_steps=0,bisected_continuation_steps=0)
    samples=[];f=[];prevR=R0
    for k in range(panels):
        s=k/panels;X=x0+1j*Xc.imag*(2*s-s*s)
        R=np.sqrt(X*X+rho*rho)
        if abs(R-prevR)>abs(-R-prevR):R=-R
        if k:zs=list(_advance_pair(prevR,zs[0],zs[1],R,ep,stats))
        gap=_energy(zs[1],R)-_energy(zs[0],R)
        f.append(gap*(2j*Xc.imag*(1-s)))
        samples.append(dict(s=s,R=R,gap=gap));prevR=R
    f.append(0j)
    val=(f[0]+f[-1]+4*sum(f[1:-1:2])+2*sum(f[2:-1:2]))/(3*panels)
    return dict(rho=float(rho),panels=int(panels),delta=float(abs(val.imag)),integral=val,
                endpoint_assumption='SIMPLE_FOLD_CERTIFICATE_REQUIRED',
                method='SIMPSON_IN_REGULARIZED_S_WITH_COUPLED_SHEET_TRACKING',
                source_model='STRAIGHT_LINE_STATIC_COULOMB_CURVES',
                real_anchor_backend='FIXED_TAU_INDEXED_STURM_GALERKIN',
                real_anchor=pair,samples=samples,**stats)
