"""PHYS40: positive-volume finite strips away from spectator coalescence.

This bridges the new exact arbitrary-radius full coupled angular shell to
nearby radial points, on an original single Chebyshev panel. When
delta<|rho-R|, normalized spectator direction is *uniformly* Lipschitz:
 |n(r)-n(rho)| <=2|r-rho|/|rho-R|.
All other factors have explicit 1D derivative bounds obtained from the
frozen exact-dyadic radial polynomials.

Certified only on the stated finite-volume strips. Does NOT replace the
global r0..20 broken bulk, origin, interface or outgoing dual certificate.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import factorial,comb
from pathlib import Path
from time import perf_counter
import hashlib,json

from .phys33_residual import load_frozen,dyadic,interpolants,ceil_sqrt_fixed
from .phys33_coupled_source import outward_decimal
from .phys33_cusp_shell import _qrt_sqrt
from .phys33_full_coupled_shell import R,K2

def _local_taylor_physical(arr:list[F],nodes:list[F],rho:F)->list[F]:
    lo,hi=nodes[0],nodes[-1]
    mid,half=(lo+hi)/2,(hi-lo)/2
    scaled=[(x-mid)/half for x in nodes]
    basis=interpolants(scaled)
    coeff=[sum((v*p[k] for v,p in zip(arr,basis)),F(0))
           for k in range(len(arr))]
    shift=(rho-mid)/half
    return [sum((coeff[j]*comb(j,k)*shift**(j-k)
                 for j in range(k,len(coeff))),F(0))/half**k
            for k in range(len(coeff))]


def _poly_derivative_sup(a:list[F],delta:F,order:int)->F:
    return sum((abs(a[k])*F(factorial(k),factorial(k-order))*
                delta**(k-order) for k in range(order,len(a))),F(0))


def local_strip_certificate(frozen:str|Path, anchor_file:str|Path,
                            delta:F, digits:int=12)->dict:
    if not isinstance(delta,F) or delta<=0 or digits<8 or digits>18:
        raise ValueError("positive exact radial delta and supported digits")
    start=perf_counter()
    anchor_bytes=Path(anchor_file).read_bytes()
    anchor_hash=hashlib.sha256(anchor_bytes).hexdigest()
    cert=json.loads(anchor_bytes)
    if cert.get("schema")!="WU088_HH_PHYS40_FULL_COUPLED_FIXED_RADIUS_SHELL_V1":
        raise ValueError("anchor must be full coupled C7B angular cert")
    rho=F(cert["physical_r_a0"])
    if delta>=abs(rho-R):
        raise ValueError("this strip may not intersect the spectator cusp sphere")
    radial,u,sha=load_frozen(frozen,True)
    if sha!=cert["source_sha256"]:
        raise ValueError("source frozen identity disagrees with shell")
    j=cert["chosen_panel"]
    low,high=dyadic(radial[j,0]),dyadic(radial[j,-1])
    if not low<=rho-delta<rho<rho+delta<=high:
        raise ValueError("strip must be within original frozen radial panel")
    nodes=[dyadic(x) for x in radial[j]]
    minr=rho-delta
    b0=bp=grad=gradp=ap=F(0)
    for l in range(21):
        vals=[]
        for component in (u[l,j].real,u[l,j].imag):
            c=_local_taylor_physical([dyadic(float(x)) for x in component],nodes,rho)
            vals.append([_poly_derivative_sup(c,delta,k) for k in range(4)])
        v=[sum(x[k] for x in vals) for k in range(4)]
        normhi=_qrt_sqrt(2*l+1)[1]
        L=F(l*(l+1));alpha=1+L/2
        b0+=normhi*v[0]/minr
        bp+=normhi*(v[1]/minr+v[0]/minr**2)
        grad+=normhi*(v[1]/minr+alpha*v[0]/minr**2)
        gradp+=normhi*(v[2]/minr+(2+alpha)*v[1]/minr**2+
                         2*(1+alpha)*v[0]/minr**3)
        ap+=normhi*(v[3]/minr+v[2]/minr**2+
                       (K2/minr+2/minr**2+L/minr**3)*v[1]+
                       (K2/minr**2+4/minr**3+3*L/minr**4)*v[0])
    # Original U and its derivative satisfy |U|<=1, |U'|<=5 for s>=0.
    # E and exp(-E) are 1-Lipschitz; original l=0 source E^-r≤1.
    # The spectator unit vector is 2/|rho-R|-Lipschitz away from coalescence.
    scalar_slope=(ap+2*(grad+gradp)+2*(5*b0+bp)+4*(1+K2))
    extra_direction=4*grad/abs(rho-R)
    total_slope=scalar_slope+extra_direction
    shell0=F(cert["angular_norm_L2_upper"])
    sqrt_delta=F(ceil_sqrt_fixed(delta,digits))
    sqrt_delta3=F(ceil_sqrt_fixed(delta**3/F(3),digits))
    radial_Minkowski=shell0*sqrt_delta+total_slope*sqrt_delta3
    total_squared=2*(rho+delta)**2*radial_Minkowski**2
    return {
       "schema":"WU088_HH_PHYS40_NONCOALESCING_FULL_COUPLED_RADIAL_STRIP_V1",
       "original_source_sha256":sha,"anchor_receipt_sha256":anchor_hash,
       "anchor_radius_a0":str(rho),"delta_a0":str(delta),
       "actual_frozen_panel":j,
       "full_3D_broken_strong_residual_L2_upper":ceil_sqrt_fixed(total_squared,digits),
       "anchor_shell_L2_upper":str(shell0),
       "radial_slope_uniform_upper":outward_decimal(total_slope,digits,True),
       "spectator_direction_modulus":"|n(r)-n(rho)|<=2t/|rho-R|, all angles",
       "proof":"fixed-r rigorous original full PDE coupled shell + exact frozen polynomial derivative sup + radial Minkowski",
       "elapsed_s":perf_counter()-start,
       "scope":"finite strip [rho-delta,rho+delta] excluding spectator sphere, within one panel",
       "unresolved":["other radial panels","cusp strip merging into full radial continuum",
          "origin/outgoing boundary","continuous low Schur inverse","actual intensity/rate"]
    }
