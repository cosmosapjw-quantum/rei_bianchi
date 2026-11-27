"""PHYS38: exact all-five-panel interface distribution certificate in H^-1.

For u(r,Omega)=sum_l u_l(r)Y_l0(Omega)/r, the physical field is
exactly continuous at each STORED IEEE binary64 common panel endpoint.
Only the jump in its first radial derivative produces a delta shell in Δu.
A dimensionless radial one-dimensional trace inequality gives an explicit
H^-1 bound. No inference about the remaining interior PDE bulk or solver
inverse is made.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from time import perf_counter

from .phys33_residual import (
    load_frozen,dyadic,interpolants,reconstruct,derivative,scale,value,
    ceil_sqrt_fixed
)
from .phys33_coupled_source import outward_decimal


def all_interface_certificate(filename:str|Path,digits:int=16)->dict:
    if not 8<=digits<=20:
        raise ValueError("must use a bounded output decimal precision")
    started=perf_counter()
    rr,u,source_sha=load_frozen(filename,True)
    traces=[]
    for panel in range(len(rr)):
        nodes=[dyadic(v) for v in rr[panel]]
        lo,hi=nodes[0],nodes[-1]
        mid,half=(lo+hi)/2,(hi-lo)/2
        basis=interpolants([(x-mid)/half for x in nodes])
        lower,upper=[],[]
        for ell in range(u.shape[0]):
            re,im=reconstruct(u[ell,panel],basis)
            dre=scale(derivative(re),1/half)
            dim=scale(derivative(im),1/half)
            lower.append((value(re,F(-1)),value(im,F(-1)),
                          value(dre,F(-1)),value(dim,F(-1))))
            upper.append((value(re,F(1)),value(im,F(1)),
                          value(dre,F(1)),value(dim,F(1))))
        traces.append((lower,upper))
    results=[]
    total_D=F(0)
    for j in range(1,len(rr)):
        b=dyadic(rr[j,0])
        left,right=traces[j-1][1],traces[j][0]
        value2,deriv2=F(0),F(0)
        for L,Q in zip(left,right):
            dv_re,dv_im=Q[0]-L[0],Q[1]-L[1]
            d_re=(Q[2]-L[2])/b-dv_re/b**2
            d_im=(Q[3]-L[3])/b-dv_im/b**2
            value2+=(dv_re**2+dv_im**2)/b**2
            deriv2+=d_re**2+d_im**2
        # If value has a jump the distribution contains δ' and would need
        # an H^-2 theory. Refuse to mislabel a nonzero value jump H^-1.
        if value2!=0:
            raise ArithmeticError("nonzero field-value jump precludes claimed H^-1-only delta bound")
        prev_left=dyadic(rr[j-1,0])
        width=min(b/F(4),(b-prev_left)/2,F(1,2))
        minr=b-width
        if minr<=0:
            raise ArithmeticError("trace collar intersects excluded origin")
        # In a 1-sided width interval:
        # ||v(b)||_S² <=2/width∫|v|²dr+2width∫|dr v|²dr
        # <=2 max(1/width,width)/minr² *||v||_H1².
        trc=F(ceil_sqrt_fixed(2*max(1/width,width),digits))/minr
        derivative_upper=F(ceil_sqrt_fixed(deriv2,digits))
        d_bound=b*b*trc*derivative_upper
        total_D+=d_bound
        results.append({
          "interface":j,"r_binary64_exact_rational":str(b),
          "tracing_collar_width_rational":str(width),
          "field_value_jump_exact_zero":True,
          "first_normal_derivative_jump_L2_upper":
                 outward_decimal(derivative_upper,digits,True),
          "laplacian_delta_Hminus1_upper":
                 outward_decimal(d_bound,digits,True),
        })
    return {
      "schema":"WU088_HH_PHYS38_ALL_INTERFACES_HMINUS1_V1",
      "input_sha256":source_sha,
      "interfaces":results,
      "dimensionless_domain":"a0 radii, fixed frozen r0..20",
      "Hminus1_test_norm":"(int_(r0..20)(|v|²+|grad v|²)r² dr dOmega)^1/2",
      "full_broken_Laplacian_distribution_Hminus1_upper":
                 outward_decimal(total_D,digits,True),
      "Schrodinger_minus_Delta_over_two_distribution_Hminus1_upper":
                 outward_decimal(total_D/2,digits,True),
      "wall_elapsed_s":perf_counter()-started,
      "claims_excluded":["full PDE bulk plus Hminus1 aggregation",
         "origin r<r0 and outgoing exterior","continuous low-Schur inverse",
         "two-centre intensity or rate"],
    }
