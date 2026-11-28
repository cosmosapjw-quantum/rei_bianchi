"""PHYS45 R5/C5: exact-rational two-centre screened exterior angular coupling.

At every rational r>R=7/10,
 V_lm(r) = integral_{S2} Y_l0 V(s) Y_m0 dOmega,
 V(s)=(1+1/s)e^{-2s}, s=sqrt(r²+R²-2rR mu).
The substitution mu=(r²+R²-s²)/(2rR) gives
 V_lm = sqrt((2l+1)(2m+1))/(2rR)
        int_{r-R}^{r+R} P_l(mu(s))P_m(mu(s))*(1+s)*exp(-2s) ds.

Original 21-mode angular matrix is CERTIFIED using exact rational polynomial
moments with strict outward exponential Taylor/positive-tail brackets. The
central Coulomb reference remains the separate PHYS44 DtN, not a full
screened-coupled outgoing inverse. This module provides independent exterior
potential and high-angular-leakage L1 envelopes, not a resolvent norm.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Q
from multiprocessing import get_context
from pathlib import Path
from functools import lru_cache
from time import perf_counter
import hashlib

from .phys33_angular_kernel import legendre_in_s2, power_exponential_moment, _mul
from .phys33_cusp_shell import _qrt_sqrt
from .phys33_coupled_source import exp_negative_bounds, outward_decimal

R=Q(7,10)
FROZEN_ID="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
SCHEMA="WU088_HH_PHYS45_YUKAWA_COUPLED_EXTERIOR_V1"
MAX_L=20


def _moments(r:Q,terms:int)->tuple[tuple[Q,Q],...]:
    a,b=r-R,r+R
    if a<=0:raise ValueError("outside spectator coalescence only")
    return tuple(
        (power_exponential_moment(2*j,2,a,b,terms)[0]
         + power_exponential_moment(2*j+1,2,a,b,terms)[0],
         power_exponential_moment(2*j,2,a,b,terms)[1]
         + power_exponential_moment(2*j+1,2,a,b,terms)[1])
        for j in range(2*MAX_L+1)
    )


@lru_cache(maxsize=2)
def _legendre_at_r20()->tuple:
    return tuple(tuple(legendre_in_s2(l,Q(20))) for l in range(MAX_L+1))


def _matrix_pairs(job:tuple)->list[tuple[int,int,Q,Q]]:
    source_file,r,pairs,terms=job
    if hashlib.sha256(Path(source_file).read_bytes()).hexdigest()!=FROZEN_ID:
        raise ArithmeticError("original immutable source SHA changed")
    # Each worker memoizes physical exp-moments over the SAME exact s range.
    polys=(_legendre_at_r20() if r==20 else
           tuple(tuple(legendre_in_s2(l,r)) for l in range(MAX_L+1)))
    moments=_moments(r,terms)
    ans=[]
    for ell,m in pairs:
        prod=_mul(polys[ell],polys[m])
        lo=hi=Q(0)
        for j,c in enumerate(prod):
            if not c:continue
            ml,mh=moments[j]
            lo+=c*(ml if c>0 else mh)
            hi+=c*(mh if c>0 else ml)
        if lo>hi:raise ArithmeticError("inverted signed original screened integral")
        alpha_lo,alpha_hi=_qrt_sqrt((2*ell+1)*(2*m+1))
        lower=lo*(alpha_lo if lo>=0 else alpha_hi)/(2*r*R)
        upper=hi*(alpha_hi if hi>=0 else alpha_lo)/(2*r*R)
        if lower>upper:raise ArithmeticError("inverted angular normalized interval")
        ans.append((ell,m,lower,upper))
    return ans


def exterior_tail_envelopes(radius:Q=Q(20),terms:int=320,digits:int=24)->dict:
    """Certified analytic infinite-radial-integral bounds, no Green resolvent."""
    if not isinstance(radius,Q) or radius<=R or not 1<=digits<=24:
        raise ValueError("positive exact radius beyond fixed spectator")
    d=radius-R
    exp2hi=exp_negative_bounds(2*d,terms)[1]
    exp_at_B_lo=exp_negative_bounds(2*radius,terms)[0]
    abs_s=(1+1/d)*exp2hi
    derivative=R*(2+2/d+1/d**2)*exp2hi
    # V(s)=(1+1/s)e^-2s is positive, decreasing and CONVEX:
    # V''(s)=e^-2s(4+4/s+4/s²+2/s³)>0.
    # Hence ||V(s(r,mu))-V(r)||sup = V(r-R)-V(r)
    # (larger than V(r)-V(r+R)).  Its integrated upper is
    #   2∫[V(r-R)-V(r)]dr
    #   <= (1+1/d)*e^-2d -e^-2B,
    # using V(r)>=e^-2r and a monotone rational prefactor.
    improved_offcenter=abs_s-exp_at_B_lo
    if improved_offcenter<0:
        raise ArithmeticError("invalid convex offcentre tail proof")
    # The older pointwise Lipschitz integral also remains a valid
    # independently derived backup enclosure; select their minimum.
    offcentral_integral=min(improved_offcenter,derivative)
    near_at_B=(1+1/d)*exp2hi
    central_lo=(1+1/radius)*exp_at_B_lo
    offcentral_pointwise=near_at_B-central_lo
    if offcentral_pointwise<0:
        raise ArithmeticError("invalid convex pointwise range")
    return {
        "outer_radius_a0":str(radius),
        "spectator_R_a0":str(R),
        "screened_V_pointwise_sup_at_B":outward_decimal(abs_s,digits,True),
        "full_screened_plus_2V_radial_L1_upper":outward_decimal(abs_s,digits,True),
        "V_minus_central_diagonal_operator_pointwise_bound_at_B":outward_decimal(offcentral_pointwise,digits,True),
        "full_plus_2V_off_central_diagonal_radial_L1_upper":outward_decimal(offcentral_integral,digits,True),
        "ell_gt20_off_central_source_L1_operator_upper":outward_decimal(offcentral_integral,digits,True),
        "older_crude_lipschitz_tail_bound":outward_decimal(derivative,digits,True),
        "improved_convex_symmetric_difference_tail_bound":outward_decimal(improved_offcenter,digits,True),
        "tail_full_angular_certificate":"all ell and m sectors, scalar multiplication Lipschitz and orthogonal projection; no assumed hard angular cutoff",
        "Green_resolvent_norm":None,
        "full_screened_DtN_perturbation":None,
    }


def screened_coupling_matrix(frozen:str|Path,radius:Q=Q(20),lmax:int=20,
                             terms:int=320,digits:int=24,workers:int=1)->dict:
    if not isinstance(radius,Q) or radius<=R or not 0<=lmax<=MAX_L:
        raise ValueError("exact rational physical exterior radius, lmax <=20")
    if type(terms) is not int or not 256<=terms<=512 or terms<=2*(radius+R):
        raise ValueError("sufficient positive exponential order 256..512")
    if workers not in (1,2,3,4) or not 16<=digits<=24:
        raise ValueError("supported digit/worker contract")
    filename=str(frozen)
    source_hash=hashlib.sha256(Path(filename).read_bytes()).hexdigest()
    if source_hash!=FROZEN_ID:raise ValueError("wrong original frozen 1386 source")
    begin=perf_counter()
    pairs=[(i,j) for i in range(lmax+1) for j in range(i,lmax+1)]
    jobs=[(filename,radius,pairs[w::workers],terms) for w in range(workers)]
    if workers==1:
        batches=[_matrix_pairs(jobs[0])]
    else:
        with ProcessPoolExecutor(max_workers=workers,mp_context=get_context("forkserver")) as pool:
            batches=list(pool.map(_matrix_pairs,jobs))
    assembled={(i,j):(low,high) for batch in batches for i,j,low,high in batch}
    if len(assembled)!=len(pairs):raise ArithmeticError("missing exact angular pairs")
    vals=[]
    for i in range(lmax+1):
        row=[]
        for j in range(lmax+1):
            lower,upper=assembled[min(i,j),max(i,j)]
            row.append([outward_decimal(lower,digits,False),
                        outward_decimal(upper,digits,True)])
        vals.append(row)
    assert all(vals[i][j]==vals[j][i] for i in range(lmax+1) for j in range(lmax+1))
    lo_S=exp_negative_bounds(2*(radius+R),terms)[0]*(1+1/(radius+R))
    hi_S=exp_negative_bounds(2*(radius-R),terms)[1]*(1+1/(radius-R))
    central_lo,central_hi=exp_negative_bounds(2*radius,terms)
    central_lo*=1+1/radius
    central_hi*=1+1/radius
    finite_dev_rows=[]
    for i,row in enumerate(vals):
        total=Q(0)
        for j,(lo,hi) in enumerate(row):
            lower=Q(lo)-(central_hi if i==j else 0)
            upper=Q(hi)-(central_lo if i==j else 0)
            total+=max(abs(lower),abs(upper))
        finite_dev_rows.append(total)
    finite_dev_upper=max(finite_dev_rows)
    for ell in range(lmax+1):
        if Q(vals[ell][ell][0])<0:
            raise ArithmeticError("diagonal potential positivity unresolved; increase Taylor order")
    tails=exterior_tail_envelopes(radius,terms,digits)
    # Exact rational componentwise row-sum upper for symmetric matrix
    row_norm=max(
        sum(max(abs(Q(x[0])),abs(Q(x[1]))) for x in row)
        for row in vals
    )
    # Norms of multiplication operator bounded by extrema of V(s), irrespective
    # of dimension. These bounds remain true for all missing higher ell.
    return {
        "schema":SCHEMA,"original_source_sha256":source_hash,
        "same_original_model":"h=-Delta/2-1/r-(1+1/s)e^-2s; R=kappa=7/10",
        "radius_a0":str(radius),"lmax":lmax,
        "matrix_sector":"m=0, normalized Y_l0; all (l,m) in 0..lmax",
        "meaning":"V_lj=int Y_l0 (1+1/s)e^-2s Y_j0 dOmega; original reduced radial PDE coupling is +2V",
        "exact_s_coordinate":"mu=(r²+R²-s²)/(2rR), dmu=-s ds/(rR)",
        "source_term":"(s+1)exp(-2s) P_l(mu(s))P_j(mu(s))",
        "certified_V_matrix_interval":vals,
        "symmetric_exact":True,"positive_definite_by_positive_multiplication":True,
        "finite_angular_compression_lower_eigen_bound":outward_decimal(lo_S,digits,False),
        "finite_angular_compression_upper_eigen_bound":outward_decimal(hi_S,digits,True),
        "gershgorin_operator_norm_upper":outward_decimal(row_norm,digits,True),
        "finite_matrix_central_deviation_gershgorin_upper":outward_decimal(finite_dev_upper,digits,True),
        "all_angular_operator_norm_upper":outward_decimal(hi_S,digits,True),
        "tails":tails,"terms":terms,"digits":digits,"workers":workers,
        "evaluated_distinct_pairs":len(pairs),"elapsed_s":perf_counter()-begin,
        "NOT_CERTIFIED":[
          "Green/resolvent kernel and Volterra contraction",
          "full noncentral screened outgoing Coulomb DtN and l>20 propagated wave",
          "driven regular origin and continuous low-Schur inverse",
          "physical cross section and Maxwellian thermal k_HH(T)",
          "rei_bianchi consumer source activation or ionization history",
        ]
    }
