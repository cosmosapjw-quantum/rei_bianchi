"""PHYS49: rigorous infinite-high-ell ORIGINAL screened Dirichlet collar block.

Original central Coulomb radial baseline q_l=k^2+2/r-l(l+1)/r^2,
k=7/10. The original actual off-centre screened positive
S(s)=(1+1/s)exp(-2s), R=7/10 and original l<=20 trial SHA preserved.

For fixed [B,T]=[20,27] a0 with ZERO Dirichlet traces at both ends,
the infinite projected high operator
 A_H=Q_{l>=21}[-d_r^2 + l(l+1)/r^2-2/r-k²-2S(s)]Q
is uniformly coercive by Poincare and a positive centrifugal floor.

For prescribed arbitrary low u_P (ell<=20) on this collar,
 A_H u_H=2 Q_H S P u_P admits a unique zero-Dirichlet L2 response.
We also bound Q_{l>=21+N} u_H allowing feedback through intermediate
21<=l<21+N via a second coercive Schur estimate and original
PHYS47 Bernstein-Chebyshev direct angular coefficient bounds.

This is a BOUNDED RADIAL DIRICHLET COLLAR theorem, NOT an outgoing
Coulomb Green function, no physical ell>20 solution without traces,
nor physical cross section / k_HH(T) / rei_bianchi production admission.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from multiprocessing import get_context
from pathlib import Path
from time import perf_counter
import hashlib

from .phys33_coupled_source import exp_negative_bounds
from .phys47_high_ell import rho_prefactor, scientific_up

SCHEMA="WU088_HH_PHYS49_INFINITE_ANGULAR_DIRICHLET_COLLAR_SCHUR_V1"
FROZEN_SHA="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
B=F(20)
T=F(27)
R=F(7,10)
K=F(7,10)
L=20
# pi>3 yields rigorous Poincare pi²/49 > 9/49.
POINCARE_FLOOR=F(9,49)
SOURCE_L_FIRST=L+1


def barrier_floor(ell:int)->F:
    """Pointwise LOWER of Coulomb barrier on [20,27] for all ell>=21."""
    if type(ell) is not int or not SOURCE_L_FIRST<=ell<=2000:
        raise ValueError("integer high ell>=21 and bounded proof domain")
    # d/dr[ell(ell+1)/r²-2/r-k²]
    # = 2(r-ell(ell+1))/r³<0 on [20,27].
    return F(ell*(ell+1),T*T)-F(2,T)-K*K


def dirichlet_floor(ell:int)->F:
    """Exact rational lower of the radial Dirichlet eigenvalue."""
    return POINCARE_FLOOR+barrier_floor(ell)


def original_screened_coupling_max(terms:int=192)->F:
    """Rigorous operator upper ||2S|| on all m and r in [20,27]."""
    if type(terms) is not int or not 128<=terms<=384:
        raise ValueError("positive exponential Taylor truncation")
    hi=exp_negative_bounds(2*(B-R),terms)[1]
    delta=2*(1+1/(B-R))*hi
    assert delta>0
    return delta


def _direct_pointwise(ell_shift:int,rhos:tuple[int,...],terms:int)->tuple[F,int]:
    """Original +2S P<=20 -> Q>=21+N pointwise exact upper at B.

    PHYS47 rho_prefactor is the original 2*integrated coefficient bound;
    the sup in this collar for +2S is exactly twice that coefficient.
    """
    if ell_shift==0:
        return original_screened_coupling_max(terms),0
    options=[(2*rho_prefactor(rho,terms)[0]*F(rho)**(-ell_shift),rho)
             for rho in rhos]
    pointwise,rho=min(options,key=lambda a:(a[0],a[1]))
    return min(pointwise,original_screened_coupling_max(terms)),rho


def _row(job:tuple)->dict:
    n,rhos,terms,digits=job
    delta=original_screened_coupling_max(terms)
    low=dirichlet_floor(SOURCE_L_FIRST)
    if not 0<delta<low:
        raise ArithmeticError("screened perturbation not small vs infinite barrier")
    alpha=delta/(low-delta)
    # q = ||A_H0^-1 2QSQ|| <= delta/lambda_H <1.
    t=SOURCE_L_FIRST+n
    target_lam=dirichlet_floor(t)
    eps,best_rho=_direct_pointwise(n,rhos,terms)
    # This is not a bare direct-tail bound: M=21..(20+N) feeds T as well.
    # A_TT u_T=2Q_T S P u_P+2Q_T S Q_M u_M.
    # ||u_M||<=||u_H||<=alpha||u_P||.
    indirect=delta*alpha
    tail=(eps+indirect)/(target_lam-delta) if n else alpha
    return {
        "N":n,
        "input_maximum_l":L,
        "output_minimum_l":t,
        "selected_ellipse_rho":best_rho,
        "target_Dirichlet_lower_exact":str(target_lam),
        "direct_high_l_plus2S_pointwise_upper":scientific_up(eps,digits),
        "intermediate_multihop_source_upper":scientific_up(indirect,digits),
        "high_l_conditional_response_L2_gain_upper":scientific_up(tail,digits),
        "mid_channels":"ell21..20+N" if n>0 else "empty",
        "_tail":tail,
    }


def high_l_dirichlet_collar(
    frozen:str|Path,
    Ns:tuple[int,...]=(0,4,8,12,16,20,24,28,32,40),
    rhos:tuple[int,...]=tuple(range(4,29)),
    workers:int=1,terms:int=192,digits:int=22,
)->dict:
    sha=hashlib.sha256(Path(frozen).read_bytes()).hexdigest()
    if sha!=FROZEN_SHA:raise ValueError("original H-H source identity changed")
    if not Ns or any(type(n) is not int or not 0<=n<=80 for n in Ns) or len(set(Ns))!=len(Ns):
        raise ValueError("unique high source orders 0..80")
    if not rhos or any(type(r) is not int or not 3<=r<=28 for r in rhos) or len(set(rhos))!=len(rhos):
        raise ValueError("unique valid original analytic ellipses")
    if workers not in (1,2,3,4) or not 12<=digits<=28 or not 128<=terms<=384:
        raise ValueError("bounded rational precision and parallel budget")
    start=perf_counter()
    delta=original_screened_coupling_max(terms)
    lam=dirichlet_floor(SOURCE_L_FIRST)
    q=delta/lam
    if not 0<q<F(1,10**8):raise ArithmeticError("positive infinite high channel Schur contraction invalid")
    alpha=delta/(lam-delta)
    jobs=[(n,rhos,terms,digits) for n in Ns]
    if workers==1:
        rows=list(map(_row,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,mp_context=get_context("forkserver")) as pool:
            rows=list(pool.map(_row,jobs))
    return {
        "schema":SCHEMA,
        "original_source_sha256":sha,
        "same_original_hamiltonian":"h=-Delta/2-1/r-(1+1/s)exp(-2s), R=k=7/10",
        "radius_interval_a0":["20","27"],
        "radius_trace":"ZERO DIRICHLET imposed at BOTH endpoints for HIGH ell>=21 only; physical outgoing traces unknown",
        "radial_Hilbert_space":"L2(dr; l2 over all l>=21 and all m)",
        "full_high_block":"Q_high[-partial_r^2+l(l+1)/r^2-2/r-k^2-2S]Q_high",
        "high_barrier_min_at_r27_exact":str(barrier_floor(SOURCE_L_FIRST)),
        "Poincare_lower_exact":"9/49 (pi²/49 is stronger)",
        "unperturbed_high_Dirichlet_eigen_floor_exact":str(lam),
        "original_screening_plus2S_sup_upper":scientific_up(delta,digits),
        "infinite_high_ell_neumann_q_upper":scientific_up(q,digits),
        "screened_infinite_high_block_inverse_upper":scientific_up(1/(lam-delta),digits),
        "whole_high_response_gain_to_low_u_P_upper":scientific_up(alpha,digits),
        "response_problem":"u_H=(A_H)^-1[2 Q_high S P_low u_P], all m, any L2 low u_P on collar",
        "high_response_claim":"unique coercive self-adjoint zero-Dirichlet response for all ell>=21",
        "high_source_ell<=20":"source is arbitrary low radial trace, NOT extended from frozen r<=20 data",
        "source_physical_angular_normalization":"original normalized spherical Y_lm and s=sqrt(r²+R²-2rR cos(theta))",
        "tail_Schur_formula":"||Q_>20+N u_H|| <= [eps_N + delta*alpha_H]/[lambda_21+N-delta] ||u_P|| for N>0, where eps_N=||2Q_T S P_low||, delta=||2S||, alpha_H=delta/(lambda_21-delta)",
        "Ns":list(Ns),"rhos":list(rhos),
        "exact_outward_tail_rows":[{k:v for k,v in r.items() if not k.startswith("_")} for r in rows],
        "terms":terms,"digits":digits,"workers":workers,
        "elapsed_s":perf_counter()-start,
        "scientific_status":"PROVED_INFINITE_ANGULAR_ZERO_DIRICHLET_FINITE_RADIAL_COLLAR_SCHUR_RESPONSE_NOT_OUTGOING",
        "NOT_CERTIFIED":[
            "original physical Coulomb outgoing high-l Green and boundary traces",
            "full r>=20 outgoing infinite angular DtN or physical propagated exterior scattering",
            "original driven xi=F*y-phi continuation and source-locked regular origin",
            "incoming adjoint or microscopic sigma(E), Maxwellian k_HH(T), or rei_bianchi HH_R10",
        ],
    }
