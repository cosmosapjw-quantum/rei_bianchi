"""PHYS38: a continuous finite-width radial-strip bound from exact cusp-shell data.

Given the same frozen binary64-input Lagrange polynomial on each side of r=R,
this module certifies a nonzero-volume shell r in [R-delta,R+delta].

The estimate uses a rigorously integrated modulus of continuity of the
spectator direction unit vector on the fixed R sphere.  It avoids falsely
treating the off-centre cusp as globally Lipschitz.

SCOPE: piecewise strong transformed PDE bulk only. The interface distribution,
origin, exterior boundary and continuous inverse remain separate.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
from time import perf_counter
import json
import hashlib

from .phys33_residual import load_frozen, dyadic, interpolants, reconstruct, ceil_sqrt_fixed
from .phys33_cusp_shell import R, _qrt_sqrt
from .phys33_moments import log_ratio_bounds
from .phys33_coupled_source import outward_decimal

K2 = F(49,100)
MAX_L = 20
PARENT_SHELL_SHA256 = "a942df8c66f5d8c3817b3e41dc11329420d2cfef9800e827c27c5381a42f1be7"


def _taylor_at_R(arr: list[F], nodes: list[F]) -> list[F]:
    """Exact coefficients of u(R+t), rational-dyadic physical radius."""
    lo,hi=nodes[0],nodes[-1]
    mid,half=(lo+hi)/2,(hi-lo)/2
    x=[(r-mid)/half for r in nodes]
    basis=interpolants(x)
    coeff=[sum((v*b[i] for v,b in zip(arr,basis)),F(0))
           for i in range(len(nodes))]
    x0=(R-mid)/half
    return [sum((coeff[k]*comb(k,j)*x0**(k-j) for k in range(j,len(coeff))),F(0))
            /half**j
            for j in range(len(coeff))]


def _max_abs_derivative(a:list[F],delta:F,degree:int)->F:
    if degree<0 or degree>3:raise ValueError("derivative bound degree in 0..3")
    return sum((abs(c)*F(factorial(j),factorial(j-degree))*delta**(j-degree)
                for j,c in enumerate(a) if j>=degree),F(0))


def _derivative_magnitudes(filename:str|Path, side:str,delta:F)->tuple[list, str]:
    radial, values, digest=load_frozen(filename,True)
    if side not in ('left','right'):raise ValueError("expected a one-sided frozen trace")
    j=1 if side=='left' else 2
    r=[dyadic(z) for z in radial[j]]
    magnitudes=[]
    for l in range(MAX_L+1):
        comps=[]
        for z in (values[l,j].real,values[l,j].imag):
            coeff=_taylor_at_R([dyadic(v) for v in z],r)
            comps.append([_max_abs_derivative(coeff,delta,n) for n in range(4)])
        mags=[comps[0][n]+comps[1][n] for n in range(4)]
        magnitudes.append(mags)
    return magnitudes,digest


def _modulus_bounds(filename:str|Path,side:str,delta:F)->dict:
    """Uniform certified coefficient bounds on [R-delta,R+delta]."""
    if not F(0)<delta<R:
        raise ValueError("require 0<delta<R, excluding the Coulomb origin")
    magnitudes,digest=_derivative_magnitudes(filename,side,delta)
    minr=R-delta
    b0=bp=grad=gp=ap=F(0)
    for l,(u0,u1,u2,u3) in enumerate(magnitudes):
        alpha=_qrt_sqrt(2*l+1)[1]
        L=F(l*(l+1))
        c=1+L/2
        b0+=alpha*u0/minr
        bp+=alpha*(u1/minr+u0/minr**2)
        grad+=alpha*(u1/minr+c*u0/minr**2)
        gp+=alpha*(u2/minr+(2+c)*u1/minr**2+2*(1+c)*u0/minr**3)
        ap+=alpha*(u3/minr+u2/minr**2+
                (K2/minr+2/minr**2+L/minr**3)*u1+
                (K2/minr**2+4/minr**3+3*L/minr**4)*u0)
    # Bounds: U(s)=E(s)*q(s)-E(s)/2-3 E(s)^2/2.
    # q(s)=int_0^1 exp(-s*t)dt -> |q|<=1, |q'|<=1/2;
    # |U|<=E<=1 and |dU/ds|<=1+1/2+1/2+3=5.
    slope=ap+2*(grad+gp)+2*(5*b0+bp)+4*(1+K2)
    return {"source_sha256":digest, "B0":b0,"Bp":bp,"Grad":grad,
            "Gradp":gp,"Ap":ap,"slope":slope}


def strip_certificate(filename:str|Path, parent_both:str|Path,
                      delta:F, digits:int=12)->dict:
    """Certified L2 physical 3D norm of broken transformed residual on strip.

    Uses actual two one-sided certified shell norms and exact rational frozen
    interpolation coefficient majorants.  The result is intentionally broad:
    pointwise angular cancellation remains unexploited away from r=R.
    """
    tic=perf_counter()
    if not isinstance(delta,F):
        raise ValueError("delta must be an exact Fraction, never an implicit float")
    if not F(0)<delta<R or not 8<=digits<=18:
        raise ValueError("require a strictly positive small rational width")
    parent_bytes=Path(parent_both).read_bytes()
    if hashlib.sha256(parent_bytes).hexdigest()!=PARENT_SHELL_SHA256:
        raise ValueError("parent cusp-shell certificate byte identity mismatch")
    shell=json.loads(parent_bytes)
    if shell.get("schema")!="WU088_HH_PHYS37_BOTH_RADIAL_TRACES_V1":
        raise ValueError("wrong frozen cusp-shell certificate")
    sides={x['side']:x for x in shell['results']}
    if set(sides)!={'left','right'}:
        raise ValueError("two separate radial traces required")
    # Fixed-sphere normalized direction-vector change:
    # I(delta)=1/(4pi)int_|n(r)-n(R)|² dOmega
    #  <=(delta/R)^2[1+2 log(2R/delta)].
    llo,lhi=log_ratio_bounds(delta,2*R,96)
    angular_d2_hi=delta**2/R**2*(1+2*lhi)
    direction_upper=F(ceil_sqrt_fixed(angular_d2_hi,digits))
    total_sq_hi=F(0)
    integrated_sq_hi=F(0)
    panels=[]
    for side in ('left','right'):
        cert=sides[side]
        source=_modulus_bounds(filename,side,delta)
        digest=source["source_sha256"]
        if cert.get('source_sha256')!=digest:
            raise ValueError("certified parent and frozen file identities differ")
        q0=F(cert['certified_true_shell_L2_upper'])
        # At fixed angles, U is Lipschitz in s with constant 5;
        # E is Lipschitz 1; exp(-E) is Lipschitz <=1; radial e^-r <=1.
        local_hi=q0+delta*source['slope']+2*source['Grad']*direction_upper
        # Separate one-sided radial width <=delta and r<=R+delta.
        interval_sq_hi=delta*(R+delta)**2*local_hi**2
        total_sq_hi+=interval_sq_hi
        # Minkowski in radial t=|r-R| replaces a full-strip supremum by
        # exact elementary integrals of t^2 and t^2 log(2R/t):
        # int_0^delta t²(1+2 log(2R/t))dt
        #    =delta³(5/9+2/3 log(2R/delta)).
        radial_u=F(ceil_sqrt_fixed(delta,digits))
        slope_u=F(ceil_sqrt_fixed(delta**3/F(3),digits))
        orientation_u=F(ceil_sqrt_fixed(delta**3*(F(5,9)+F(2,3)*lhi),digits))
        integral_radial_l2=(q0*radial_u+source['slope']*slope_u+
                2*source['Grad']/R*orientation_u)**2
        integrated_sq_hi+=integral_radial_l2
        panels.append({
            "side":side,"shell_bound":str(q0),
            "direction_change_rms_upper":outward_decimal(direction_upper,digits,True),
            "radial_modulus_slope_upper":outward_decimal(source['slope'],digits,True),
            "one_sided_shell_L2_upper":outward_decimal(local_hi,digits,True),
            "one_sided_volume_L2_uniform_upper":ceil_sqrt_fixed(interval_sq_hi,digits),
            "one_sided_radial_Minkowski_integral_upper":
                ceil_sqrt_fixed(integral_radial_l2,digits),
            "coeff_bounds":{k:outward_decimal(v,digits,True)
                            for k,v in source.items() if isinstance(v,F)},
        })
    # Actual stored radial switch is a dyadic just below R. For the left
    # physical panel its valid piece is [R-delta,r_switch], shorter than
    # delta; for right [r_switch,R+delta], slightly LONGER than delta.
    # The sum of two widths is 2delta; account for extra dyadic mismatch.
    radial,_,digest=load_frozen(filename,True)
    switch=dyadic(radial[1,-1])
    mismatch=abs(R-switch)
    if mismatch>=delta:
        raise ValueError("actual floating interface lies outside requested strip")
    # Both one-sided lengths are <=delta +mismatch. Preserve the common
    # per-side upper if the dyadic boundary is not exactly R.
    factor=(delta+mismatch)/delta
    total_sq_hi*=factor
    # The actual right polynomial is active over [switch,R+delta], which
    # straddles the exact R by a dyadic mismatch. The extra tiny interval
    # contributes <=mismatch*(maximum one-sided shell bound)^2. Use the
    # same safe extra allowance for both sides to keep the contract simple.
    for row in panels:
        bound=F(row['one_sided_shell_L2_upper'])
        integrated_sq_hi+=mismatch*bound**2
    integrated_sq_hi*=(R+delta)**2
    upper_uniform=F(ceil_sqrt_fixed(total_sq_hi,digits))
    upper_integrated=F(ceil_sqrt_fixed(integrated_sq_hi,digits))
    chosen=min(upper_uniform,upper_integrated)
    left_len=delta+(switch-R)
    right_len=delta+(R-switch)
    result={
        "schema":"WU088_HH_PHYS38_C7B_FINITE_RADIAL_STRIP_V1",
        "input_sha256":digest,
        "parent_shell_sha256":PARENT_SHELL_SHA256,
        "radius_a0":"7/10","delta_a0":str(delta),
        "actual_frozen_interface_rational":str(switch),
        "interface_deviation_from_R":str(mismatch),
        "actual_one_sided_strip_widths":[str(left_len),str(right_len)],
        "unit_vector_angular_rms_upper":outward_decimal(direction_upper,digits,True),
        "total_3D_broken_strong_residual_L2_upper":outward_decimal(chosen,digits,True),
        "conservative_uniform_sup_bound":outward_decimal(upper_uniform,digits,True),
        "improved_radial_integrated_bound":outward_decimal(upper_integrated,digits,True),
        "admitted_method": "radial_Minkowski_log_moment" if upper_integrated<upper_uniform else "uniform_sup",
        "side_evidence":panels,
        "radial_domain":["R-delta","R+delta"],
        "excluded":["delta-like distributional interface residual",
          "origin and all other radial panels","screened exterior boundary",
          "continuous low-Schur inverse","physical scattering amplitude and rate"],
        "proof":"exact polynomial Taylor bounds plus logarithmic angular modulus; "
                "radial integrals bounded by shell supremum; not a collocation Gauss convergence claim",
        "elapsed_s":perf_counter()-tic
    }
    return result
