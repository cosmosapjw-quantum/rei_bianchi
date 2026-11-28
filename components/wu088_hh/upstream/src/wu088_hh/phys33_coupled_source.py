"""PHYS36 C7: certified radial Coulomb-source cancellation and exact angular source norm.

The bound is on the *broken transformed PDE bulk* for the archived rational
Lagrange interpolant r0<r<20, all angles. It retains the original one-centre
Coulomb operator and full two-centre screened cusp transformation.

This is NOT a full coupled angular residual exact norm, an interface/origin
certificate, or a continuous inverse/amplitude certificate.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_all_start_methods, get_context
from math import comb, factorial
from pathlib import Path
import hashlib

from .phys33_residual import (
    KAPPA_SQUARED, ceil_sqrt_fixed, dyadic, derivative, interpolants,
    load_frozen, reconstruct,
)
from .phys33_moments import bound_weighted_moments


@lru_cache(maxsize=512)
def exp_negative_bounds(x: F, terms: int = 256) -> tuple[F,F]:
    """Rational outward [lo,hi] for exp(-x), x>=0.

    Positive exp(x) Taylor partial sum with bounded geometric tail. This avoids
    catastrophic alternating-series cancellation and is exact for x=0.
    """
    if x<0 or isinstance(terms,bool) or not isinstance(terms,int) or terms<1:
        raise ValueError("nonnegative x and positive integer terms required")
    if x==0:
        return F(1),F(1)
    if x>=terms+2:
        raise ValueError("Taylor tail ratio is not controlled")
    summ=F(1); term=F(1)
    for j in range(1,terms+1):
        term*=x/j
        summ+=term
    missing=term*x/(terms+1)
    tail=missing/(1-x/F(terms+2))
    return F(1)/(summ+tail), F(1)/summ


def poly_to_radius_x(coeff: list[F], mid:F, half:F)->list[F]:
    """P((r-mid)/half) as an exact polynomial in r."""
    out=[F(0)]*len(coeff)
    for n,c in enumerate(coeff):
        scalar=c/half**n
        for j in range(n+1):
            out[j]+=scalar*comb(n,j)*(-mid)**(n-j)
    return out


def _moment_exp_one(n:int,left:F,right:F,terms:int)->tuple[F,F]:
    """Certified integral of r^n exp(-r) dr, n nonnegative."""
    if n<0 or not 0<=left<right:
        raise ValueError("positive moment with ordered nonnegative endpoints")
    def sum_factor(x):
        term=F(1); acc=term
        for j in range(1,n+1):
            term*=x/j
            acc+=term
        return factorial(n)*acc
    a0,a1=exp_negative_bounds(left,terms)
    b0,b1=exp_negative_bounds(right,terms)
    pa,pb=sum_factor(left),sum_factor(right)
    return pa*a0-pb*b1, pa*a1-pb*b0


def _source_sq_interval(left:F,right:F,terms:int)->tuple[F,F]:
    """Norm^2 of S0=(1+k^2)phi, restricted to [left,right]."""
    if left<0 or left>=right:
        raise ValueError("source radial endpoints")
    def f(x):return 1+2*x+2*x*x
    a0,a1=exp_negative_bounds(2*left,terms)
    b0,b1=exp_negative_bounds(2*right,terms)
    scale=(1+KAPPA_SQUARED)**2
    lo=scale*(f(left)*a0-f(right)*b1)
    hi=scale*(f(left)*a1-f(right)*b0)
    return max(F(0),lo),hi


def outward_decimal(x: F, digits: int, upper: bool) -> str:
    """Exact rational -> outward fixed decimal, including negative numbers.

    Avoid formatting unbounded-size intermediate Fraction denominators.
    """
    if not 0 <= digits <= 24:
        raise ValueError("unsupported decimal precision")
    scaled=x.numerator * (10**digits)
    n=-((-scaled)//x.denominator) if upper else scaled//x.denominator
    sign="-" if n<0 else ""
    whole,decimal=divmod(abs(n),10**digits)
    return sign+(str(whole) if digits==0 else f"{whole}.{decimal:0{digits}d}")


def _source_panel(job: tuple[int,list, list,int,int]) -> dict:
    j, radial, nodal, digits, exp_terms = job
    left,right=dyadic(radial[0]),dyadic(radial[-1])
    half,mid=(right-left)/2,(right+left)/2
    nodes=[(dyadic(x)-mid)/half for x in radial]
    basis=interpolants(nodes)
    real,imag=reconstruct(nodal,basis)
    up=poly_to_radius_x(real,mid,half)
    deriv2=derivative(derivative(up))
    mixed=[F(0)]+deriv2
    term_r=[F(0)]+up
    coeff=[F(0)]*max(len(mixed),len(term_r),len(up))
    for k,v in enumerate(mixed): coeff[k]+=v
    for k,v in enumerate(term_r): coeff[k]+=KAPPA_SQUARED*v
    for k,v in enumerate(up): coeff[k]+=2*v
    moment_cache=[_moment_exp_one(n,left,right,exp_terms) for n in range(len(coeff))]
    sublo,subhi=F(0),F(0)
    for c,(mlo,mhi) in zip(coeff,moment_cache):
        if c>=0:
            sublo+=c*mlo;subhi+=c*mhi
        else:
            sublo+=c*mhi;subhi+=c*mlo
    c0=2*(1+KAPPA_SQUARED)
    s0,s1=_source_sq_interval(left,right,exp_terms)
    return {"panel":j,"r":[str(float(left)),str(float(right))],
            "inner_lower_exact":c0*sublo,"inner_upper_exact":c0*subhi,
            "source_sq_lower_exact":s0,"source_sq_upper_exact":s1,
            "inner_lower":outward_decimal(c0*sublo,digits,False),
            "inner_upper":outward_decimal(c0*subhi,digits,True),
            "source_squared_upper":outward_decimal(s1,digits,True)}


def radial_source_cancellation(frozen: str|Path, *,
                               digits:int=12,exp_terms:int=256,
                               workers:int=1)->dict:
    """Exact l=0 source overlap using reproducible independent radial jobs."""
    if not 8<=digits<=20 or exp_terms<64 or workers not in (1,2,3,4,6):
        raise ValueError("invalid precision or process count")
    rr,uu,sha=load_frozen(frozen,True)
    jobs=[(j,list(rr[j]),list(uu[0,j]),digits,exp_terms)
          for j in range(rr.shape[0])]
    if workers==1:
        partial=[_source_panel(x) for x in jobs]
    else:
        method="forkserver" if "forkserver" in get_all_start_methods() else "spawn"
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context(method)) as pool:
            partial=list(pool.map(_source_panel,jobs))
    partial.sort(key=lambda x:x["panel"])
    inner_lower=sum((x["inner_lower_exact"] for x in partial),F(0))
    inner_upper=sum((x["inner_upper_exact"] for x in partial),F(0))
    source_lower=sum((x["source_sq_lower_exact"] for x in partial),F(0))
    source_upper=sum((x["source_sq_upper_exact"] for x in partial),F(0))
    if source_lower>source_upper or inner_lower>inner_upper:
        raise ArithmeticError("inconsistent rational source enclosure")
    public=[{k:v for k,v in x.items() if not k.endswith("_exact")}
            for x in partial]
    return {"input_sha256":sha,"exp_terms":exp_terms,"workers":workers,
            "overlap_lower":inner_lower,"overlap_upper":inner_upper,
            "source_squared_lower":source_lower,
            "source_squared_upper":source_upper,"panels":public}


def bound_coupled_source(frozen: str|Path, *,
                         workers:int=4,screen_cells:int=8,
                         digits:int=12,exp_terms:int=256)->dict:
    """Certified angular-source cancellation with rigorous screened remainder.

    Write D y -2E shat.grad y -2U y -(1+k^2)F^-1 phi as
      [D y -(1+k^2)phi] -2E shat.grad y -2U y
                                +(1+k^2)(1-F^-1)phi.
    The first norm is directly computed using exact l0 radial cross moments.
    The last norm is bounded using the EXACT all-space angular integral
      ||E phi||²=((3+6R+4R²)/24) exp(-2R), R=7/10.
    The E*grad and E*y terms use previous rigorous radial weight envelopes.
    """
    old=bound_weighted_moments(frozen,workers=workers,
                              screen_cells=screen_cells,digits=digits)
    source=radial_source_cancellation(frozen,digits=digits,exp_terms=exp_terms,
                                      workers=workers)
    dsqhi=F(old["norm_upper"]["coulomb_diagonal"])**2
    radicand=dsqhi+source["source_squared_upper"]-2*source["overlap_lower"]
    if radicand < 0: raise ArithmeticError("source cancellation gives negative upper square")
    cancelled=ceil_sqrt_fixed(radicand,digits)
    R=F(7,10)
    square_of_Ephi=(3+6*R+4*R*R)*F(1,24)
    elow,ehi=exp_negative_bounds(2*R,exp_terms)
    ephi_hi=ceil_sqrt_fixed(square_of_Ephi*ehi,digits)
    weighted_grad=F(old["norm_upper"]["screened_weighted_gradient"])
    weighted_state=F(old["norm_upper"]["screened_weighted_state"])
    total=F(cancelled)+2*weighted_grad+2*weighted_state+(1+KAPPA_SQUARED)*F(ephi_hi)
    direct=F(old["norm_upper"]["broken_transformed_bulk_residual"])
    if total>=direct:
        # Correct conservative fallback, never worsen an admitted certificate.
        final=direct
        chosen="legacy_screened_triangle"
    else:
        final=total;chosen="direct_coulomb_source_overlap"
    return {
        "schema":"WU088_HH_PHYS36_C7_DIRECT_SOURCE_CANCELLATION_V1",
        "input_sha256":old["input_sha256"],
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "chosen":chosen,
        "norm_upper":{
            "radial_Coulomb_minus_bare_source":cancelled,
            "weighted_screened_gradient":str(weighted_grad),
            "weighted_screened_state":str(weighted_state),
            "global_E_phi":ephi_hi,
            "screened_broken_bulk_previous":str(direct),
            "screened_broken_bulk_with_direct_source":ceil_sqrt_fixed(total*total,digits),
            "screened_broken_bulk_admitted":ceil_sqrt_fixed(final*final,digits)
        },
        "overlap_interval": [outward_decimal(source["overlap_lower"],digits,False),
                             outward_decimal(source["overlap_upper"],digits,True)],
        "source_squared_interval":[outward_decimal(source["source_squared_lower"],digits,False),
                                   outward_decimal(source["source_squared_upper"],digits,True)],
        "global_E_phi_squared_exact_factor":"((3+6R+4R^2)/24)*exp(-2R)",
        "global_E_phi_R":"7/10",
        "source_integral_panels":source["panels"],
        "workers":workers,"screen_cells":screen_cells,"digits":digits,
        "exp_terms":exp_terms,
        "evidence_scope":"certified all-angle source overlap and bounded screened coupling; broken PDE bulk on r0<r<20",
        "NOT_CERTIFIED":[
            "full angular cross-term cancellation between screened derivative and D",
            "r<1e-4 origin regularity",
            "distributional interface jump",
            "correct full-screened outgoing boundary residual",
            "continuous low-Schur inverse and physical amplitude/rate"
        ]
    }
