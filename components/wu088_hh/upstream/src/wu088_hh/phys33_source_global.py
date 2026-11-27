"""PHYS39 R5/C7B: rigorous global two-centre photon/atomic source correction.

For phi=e^-r/sqrt(pi), E=e^{-|r-R ez|}, R=7/10,
  ||(1-e^-E)phi||² = sum_(n>=2) (-1)^n(2^n-2)/n! J_n(R),
  J_n(R)= integral(phi² e^-n|r-R ez| d³r).
J_n is exactly a combination of rational terms times exp(-2R), exp(-nR),
except n=2 which is a polynomial times exp(-2R). All exponentials are
outward enclosed by exact positive rational Taylor/geometric remainder;
the infinite series tail is bounded by a positive factorial majorant.

This certificate is global in physical 3D space but ONLY concerns the
original source-correction factor. It is not a full PDE error/rate result.
"""
from __future__ import annotations

from fractions import Fraction as Q
from functools import lru_cache
from math import factorial
from pathlib import Path
import hashlib, json, time

from .phys33_coupled_source import exp_negative_bounds, outward_decimal
from .phys33_residual import ceil_sqrt_fixed
from .phys33_moments import _floor_sqrt_fixed

R=Q(7,10)
K2=Q(49,100)
PARENT_PHYS36_SHA256="f2cc27a97153b233bda8ae3146dacc8575bf83ec4df59de00cbcb184f484f6d2"


def _jn_coefficients(n:int) -> tuple[Q,Q]:
    """J_n=c2 exp(-2R)+cn exp(-nR), n!=2, exact rational coefficients."""
    if isinstance(n,bool) or not isinstance(n,int) or n<1 or n==2:
        raise ValueError("n must be a positive integer different from two")
    a=Q(n+2)
    c=Q(n-2)
    coeff2 = (
       (1+n*R)*(R/c-1/c**2)
       -n*(R**2/c-2*R/c**2+2/c**3)
       +(1-n*R)*(R/a+1/a**2)
       +n*(R**2/a+2*R/a**2+2/a**3)
    )
    coeffn = ((1+n*R)/c**2+2*n/c**3) - (
            (1+n*R)/a**2+2*n/a**3)
    pref=Q(2,n*n)/R
    return pref*coeff2,pref*coeffn


def _interval_linear(coeff:Q,low:Q,high:Q)->tuple[Q,Q]:
    return (coeff*low,coeff*high) if coeff>=0 else (coeff*high,coeff*low)


@lru_cache(maxsize=512)
def jn_interval(n:int,exp_terms:int=192)->tuple[Q,Q]:
    """Certified normalized whole-space angular+radial screened moment J_n."""
    if not isinstance(n,int) or isinstance(n,bool) or n<1:
        raise ValueError("positive integer n required")
    if not isinstance(exp_terms,int) or exp_terms<max(64,n):
        raise ValueError("insufficient positive exponential Taylor terms")
    el,eh=exp_negative_bounds(2*R,exp_terms)
    if n==2:
        coeff=(3+6*R+4*R*R)/24
        lo,hi=coeff*el,coeff*eh
    else:
        c2,cn=_jn_coefficients(n)
        nl,nh=exp_negative_bounds(n*R,exp_terms)
        al,ah=_interval_linear(c2,el,eh)
        bl,bh=_interval_linear(cn,nl,nh)
        lo,hi=al+bl,ah+bh
    if not Q(0)<lo<=hi<=Q(1):
        raise ArithmeticError(f"certified J_{n} is not in physical range")
    return lo,hi


def factorial_tail(nmax:int)->Q:
    """Sum_{n>N} (2^n-2)/n! J_n <=2^(N+1)/(N+1)! / (1-2/(N+2))."""
    if nmax<2:
        raise ValueError("series must include the leading n=2 term")
    first=Q(2**(nmax+1),factorial(nmax+1))
    return first/(1-Q(2,nmax+2))


def source_squared_certificate(nmax:int=32,exp_terms:int=192,
                               digits:int=15)->dict:
    if isinstance(nmax,bool) or not 8<=nmax<=64:
        raise ValueError("nmax in 8..64")
    if not 12<=digits<=20:
        raise ValueError("digits in 12..20")
    started=time.perf_counter()
    total_lo,total_hi=Q(0),Q(0)
    components=[]
    for n in range(2,nmax+1):
        lo,hi=jn_interval(n,exp_terms)
        factor=Q((-1)**n*(2**n-2),factorial(n))
        if factor>=0:
            total_lo+=factor*lo
            total_hi+=factor*hi
        else:
            total_lo+=factor*hi
            total_hi+=factor*lo
        if n in (2,3,4,8,16,32,64):
            components.append({"n":n,"J_n_lower":outward_decimal(lo,digits,False),
                                     "J_n_upper":outward_decimal(hi,digits,True)})
    tail=factorial_tail(nmax)
    low=max(Q(0),total_lo-tail)
    high=min(Q(1),total_hi+tail)
    if not Q(0)<low<=high<=Q(1):
        raise ArithmeticError("physical square norm enclosure invalid")
    L=_floor_sqrt_fixed(low,digits)
    H=ceil_sqrt_fixed(high,digits)
    return {
      "schema":"WU088_HH_PHYS39_GLOBAL_EXACT_SOURCE_CORRECTION_V1",
      "physical_R_a0":"7/10",
      "source_phi":"exp(-r)/sqrt(pi)",
      "source_factor":"1-exp(-exp(-s)), s=|r-R zhat|",
      "nmax":nmax,"exp_terms":exp_terms,
      "squared_L2_lower":outward_decimal(low,digits,False),
      "squared_L2_upper":outward_decimal(high,digits,True),
      "norm_L2_lower":L,
      "norm_L2_upper":H,
      "factorial_tail_squared_bound":outward_decimal(tail,digits,True),
      "selected_exact_moments":components,
      "status":"CERTIFIED_ALL_SPACE_TWO_CENTRE_SOURCE_ONLY",
      "seconds":time.perf_counter()-started,
      "not_claimed":["continuous low-Schur inverse","all terms of screened residual",
           "origin/outgoing PDE boundary","scattering intensity or thermal rate"],
    }


def improved_existing_broken_bound(phys36_result:str|Path,
                                   nmax:int=32,exp_terms:int=192,
                                   digits:int=15)->dict:
    data=Path(phys36_result).read_bytes()
    if hashlib.sha256(data).hexdigest()!=PARENT_PHYS36_SHA256:
        raise ValueError("frozen PHYS36 source/bulk certificate SHA mismatch")
    p=json.loads(data)
    if p["schema"]!="WU088_HH_PHYS36_C7_DIRECT_SOURCE_CANCELLATION_V1":
        raise ValueError("wrong residual parent schema")
    source=source_squared_certificate(nmax,exp_terms,digits)
    norm=p["norm_upper"]
    source_correction=Q(source["norm_L2_upper"])
    candidate=(Q(norm["radial_Coulomb_minus_bare_source"])
               +2*Q(norm["weighted_screened_gradient"])
               +2*Q(norm["weighted_screened_state"])
               +(1+K2)*source_correction)
    prev=Q(norm["screened_broken_bulk_admitted"])
    candidate_hi=Q(ceil_sqrt_fixed(candidate*candidate,digits))
    accepted=min(prev,candidate_hi)
    return {
       "schema":"WU088_HH_PHYS39_SHARPENED_ORIGINAL_BULK_SOURCE_V1",
       "input_sha256":p["input_sha256"],
       "parent_phys36_sha256":PARENT_PHYS36_SHA256,
       "new_source":source,
       "previous_broken_bulk_bound":str(prev),
       "new_broken_bulk_bound":outward_decimal(accepted,digits,True),
       "candidate_direct_source_bound":outward_decimal(candidate_hi,digits,True),
       "admitted":"direct_allspace_two_centre_source" if candidate_hi<prev else "legacy_C7A",
       "physical_operator":"same R=kappa=7/10, lambda=1, Ea=2I0",
       "boundary":"frozen broken domain 1e-4<r<20; correction norm is global 3D majorant",
       "not_claimed":["complete screened angular cross terms",
          "continuous low-Schur inverse","origin and outgoing boundary",
          "full scattering amplitude / reaction rate"],
    }


INTERFACE_PHYS38_SHA256="6760001d384dd39c7aab79a21f60ee78a96b36c0eed84402301787669a2f714d"


def improved_truncated_hminus1(phys36_result:str|Path,
                                phys38_interface:str|Path,
                                nmax:int=32,exp_terms:int=192,
                                digits:int=15)->dict:
    """Upgrade the PHYS38 annulus H^-1 bound without changing its interface.

    Original transformed differential expression D=Delta+kappa²+2/r+...;
    D's distributional jump from the second derivative is bound in H^-1.
    The complete source correction norm here was already bounded on all R³
    and hence also on the truncated annulus r0<r<20.
    """
    old=improved_existing_broken_bound(phys36_result,nmax,exp_terms,digits)
    raw=Path(phys38_interface).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=INTERFACE_PHYS38_SHA256:
        raise ValueError("frozen PHYS38 interface receipt SHA mismatch")
    interface=json.loads(raw)
    if (interface["schema"]!="WU088_HH_PHYS38_ALL_INTERFACES_HMINUS1_V1"
        or interface["input_sha256"]!=old["input_sha256"]
        or len(interface["interfaces"])!=5
        or not all(x["field_value_jump_exact_zero"]
                   for x in interface["interfaces"])):
        raise ValueError("unsafe or mismatched interface source")
    bulk=Q(old["new_broken_bulk_bound"])
    delta=Q(interface["full_broken_Laplacian_distribution_Hminus1_upper"])
    summed=bulk+delta
    upper=ceil_sqrt_fixed(summed*summed,digits)
    return {
      "schema":"WU088_HH_PHYS39_SHARPENED_ANNULUS_HMINUS1_V1",
      "source_input_sha256":old["input_sha256"],
      "phys36_parent_sha256":PARENT_PHYS36_SHA256,
      "phys38_interface_sha256":INTERFACE_PHYS38_SHA256,
      "broken_bulk_L2_upper":str(bulk),
      "five_interface_Djump_Hminus1_upper":str(delta),
      "annulus_Hminus1_transformed_D_upper":upper,
      "norm_test_space":"dual of H0^1(1e-4<r<20) with a0-dimensional gradient",
      "not_claimed":["excluded r<1e-4 origin", "outer outgoing DtN",
        "continuous low-Schur inverse", "physical scattering intensity or thermal rate"],
    }
