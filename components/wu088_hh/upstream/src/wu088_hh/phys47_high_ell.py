"""Source-locked exact rational high angular momentum coupling coefficients.

Original S(s)=(1+1/s)*exp(-2s), s²=r²+R²-2rR*mu, R=7/10.
The bound on Q_{ell>L+N} S P_{ell<=L} follows by analytic continuation
to Bernstein ellipse E_rho and Chebyshev polynomial selection rules.
This bounds direct potential coupling, NOT the propagated exterior wave.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt
from multiprocessing import get_context
from pathlib import Path
from time import perf_counter
import hashlib

from .phys33_coupled_source import exp_negative_bounds

R=F(7,10)
B=F(20)
L=20
SOURCE_SHA="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
SCHEMA="WU088_HH_PHYS47_INFINITE_ELL_DIRECT_SCREENED_SOURCE_TRANSFER_V1"


def scientific_up(x:F,digits:int=20)->str:
    """Ceil positive exact rational to scientific decimal digits."""
    if not isinstance(x,F) or x<=0 or type(digits) is not int or not 4<=digits<=30:
        raise ValueError("positive Fraction and 4..30 digits")
    e=len(str(x.numerator))-len(str(x.denominator))
    while x<F(10)**e:e-=1
    while x>=F(10)**(e+1):e+=1
    y=x*F(10)**(digits-1-e)
    mant=(y.numerator+y.denominator-1)//y.denominator
    if mant>=10**digits:
        mant//=10
        e+=1
    s=str(mant).rjust(digits,"0")
    return f"{s[0]}.{s[1:]}e{e:+d}"


def sqrt_down(x:F,digits:int=14)->F:
    """An exact rational downward enclosure of sqrt(x)."""
    if not isinstance(x,F) or x<0 or not 10<=digits<=20:
        raise ValueError("nonnegative rational and controlled digits")
    p=10**digits
    return F(isqrt(x.numerator*p*p//x.denominator),p)


@lru_cache(maxsize=40)
def ellipse(rho:int,root_digits:int=14)->dict:
    if type(rho) is not int or not 3<=rho<=28:
        raise ValueError("Bernstein ellipse integer parameter 3..28")
    rr=F(rho)
    chi=(rr+1/rr)/2
    epsilon=R/B
    delta=2*epsilon*chi+epsilon**2
    if delta>=1:raise ValueError("complex sqrt branch unsafe")
    gamma=sqrt_down(1-delta,root_digits)
    if gamma<=0:raise ArithmeticError("nonpositive sqrt lower")
    numerator=2*R*chi+R*R/B
    shift=numerator/(1+gamma)
    if not R<shift<B:raise ValueError("invalid global ellipse shift")
    assert gamma**2<=1-delta and shift*(1+gamma)>=numerator
    return {"rho":rho,"chi":chi,"branch_deviation":delta,
            "sqrt_lower":gamma,"shift":shift,"complex_s_lower":B-shift}


@lru_cache(maxsize=64)
def rho_prefactor(rho:int,terms:int=192,root_digits:int=14)->tuple[F,dict]:
    """Exact upper C_rho for radial L1 coupling to ell>20+N.

    Let delta denote a rigorous upper |s-r| on all E_rho for all r>=20.
    Then |S(s)| <= [1+1/(20-delta)] exp[-2(r-delta)].
    Chebyshev degree-N discarded sup <= 2 M(r) rho^(-N)/(rho-1).
    Integrating the original radial +2S coupling gives C_rho*rho^-N.
    """
    if type(terms) is not int or not 128<=terms<=384:
        raise ValueError("sufficient positive exp Taylor order required")
    g=ellipse(rho,root_digits)
    shift=g["shift"]
    z=2*(B-shift)
    if z<=0 or z>=terms:raise ValueError("nonpositive exterior bound exponent")
    _,hi=exp_negative_bounds(z,terms)
    coefficient=2*(1+1/(B-shift))*hi/F(rho-1)
    if coefficient<=0:raise ArithmeticError("bad positive screened coupling")
    return coefficient,g


def _candidate(job:tuple)->dict:
    rho,terms,root_digits=job
    coefficient,g=rho_prefactor(rho,terms,root_digits)
    return {
        "rho":rho,
        "shift_exact":str(g["shift"]),
        "sqrt_lower_exact":str(g["sqrt_lower"]),
        "branch_deviation_exact":str(g["branch_deviation"]),
        "_coefficient":coefficient,
    }


def high_ell_transfer(frozen:str|Path,
                      Ns:tuple[int,...]=(0,4,8,12,16,20,24,28,32,40),
                      rhos:tuple[int,...]=tuple(range(4,29)),
                      workers:int=1,terms:int=192,
                      root_digits:int=14,digits:int=20)->dict:
    h=hashlib.sha256(Path(frozen).read_bytes()).hexdigest()
    if h!=SOURCE_SHA:raise ValueError("original immutable frozen source mismatch")
    if not Ns or len(set(Ns))!=len(Ns) or any(type(n) is not int or not 0<=n<=80 for n in Ns):
        raise ValueError("unique nonnegative 0..80 omitted multipole orders")
    if not rhos or len(set(rhos))!=len(rhos) or any(type(r) is not int or not 3<=r<=28 for r in rhos):
        raise ValueError("unique valid integer Bernstein ellipses")
    if workers not in (1,2,3,4) or not 12<=digits<=26:
        raise ValueError("bounded worker or outward precision")
    t0=perf_counter()
    jobs=[(rho,terms,root_digits) for rho in rhos]
    if workers==1:
        rows=list(map(_candidate,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context("forkserver")) as pool:
            rows=list(pool.map(_candidate,jobs))
    wins=[]
    for n in Ns:
        best=min(rows,key=lambda row:(row["_coefficient"]*F(row["rho"])**(-n),row["rho"]))
        exact=best["_coefficient"]*F(best["rho"])**(-n)
        wins.append({
            "N":n,
            "input_maximum_ell":L,
            "first_output_ell":L+n+1,
            "optimal_candidate_rho":best["rho"],
            "complex_s_shift_upper":scientific_up(F(best["shift_exact"]),digits),
            "radial_original_plus2S_P20_to_Q_high_ell_L1_upper":
                scientific_up(exact,digits),
        })
    return {
        "schema":SCHEMA,
        "original_frozen_source_SHA256":h,
        "physical_model":"H-H: h=-Delta/2-1/r-(1+1/s)exp(-2s), R=kappa=7/10",
        "exterior_radius_a0":"20",
        "physical_sector":"all m and ell output; source retained P_{ell<=20}",
        "complex_ellipse_rule":"mu=(rho exp(i theta)+rho^-1 exp(-i theta))/2, all theta",
        "complex_shift_rule":"|s-r| <= (2 R chi+R²/20)/(1+sqrt_lower(1-delta))",
        "complex_branch_rule":"delta=2(R/20)chi+(R/20)^2 <1, principal analytic sqrt",
        "uniform_potential":"|S(s)| <= [1+1/(20-shift)] exp(-2(r-shift)), r>=20",
        "Chebyshev_polynomial_error":"||S-p_N||infinity <= 2M rho^-N/(rho-1)",
        "angular_selection_rule":"Q_{ell>20+N} p_N(cos theta) P_{ell<=20}=0 for every m",
        "radial_original_plus2S_operator":"2 integral_20^infinity ||Q_{ell>20+N} S(r,mu) P_{ell<=20}|| dr",
        "complete_proof_scope":"rigorous direct high-ell source coupling only; not the propagated Green/Jost or scattering solution",
        "candidate_rhos":list(rhos),
        "studied_Ns":list(Ns),
        "best_bounds":wins,
        "all_candidate_ellipse_geometries":[
            {"rho":row["rho"],"shift_exact":row["shift_exact"],
             "branch_deviation_exact":row["branch_deviation_exact"]}
            for row in rows],
        "exp_taylor_terms":terms,"sqrt_lower_digits":root_digits,
        "scientific_significant_digits":digits,
        "workers":workers,"elapsed_s":perf_counter()-t0,
        "not_certified":[
            "uniform high-ell Coulomb centrifugal Green resolvent and propagated wave",
            "full infinite-dimensional outgoing DtN or original incident xi=F*y-phi",
            "driven regular origin, incoming adjoint or scattering sigma(E)",
            "Maxwellian physical k_HH(T) or rei_bianchi HH_R10 source",
        ],
    }
