"""PHYS46: rigorous finite-21-channel Coulomb outgoing Volterra contraction.

Physical raw reduced-radial m=0 Schrödinger equation, not the frozen
transformed y strong residual:
 U''+[diag(k²+2/r-l(l+1)/r²)+2 V21(r)]U=0, l=0..20,
 k=7/10, V21=P21 (1+1/s)exp(-2s) P21, s=|r-R zhat|, R=7/10.

For outgoing H_l^(+)=G_l+iF_l, W_r(H+,H-)=-2ik,
 K_l(r,t)=[H_l^+(r)H_l^-(t)-H_l^-(r)H_l^+(t)]/(2ik)
 has K(r,r)=0, derivative_r K|r=t=1, and D_l K=0.

Because |H-|=|H+| and Wronskian is exactly 1 in rho,
 |K_l(r,t)|<=|H_l^+(r)| |H_l^+(t)|/k.

An ENTIRELY RATIONAL elementary energy estimate bounds every original
l=0..20 outgoing Coulomb channel by the scalar
 w(r)=M exp(c (T-r)) when B<=r<=T, and w(r)=M when r>=T,
 with B=20, c=59/70, M/T selected from rational candidates.
In Banach weighted sup_l2 norm ||U||_w=sup_{r>=B}||U(r)||2/w(r),
 the coupled Volterra kernel norm q <=(2/k)int_B^infty w(t)^2 S(t-R)dt.
Exact-rational exponential envelopes certify q<1 and boundary Jost
matrix invertibility if alpha=q/(1-q)<1.

Scope: 21-mode homogeneous radial screened exterior ONLY. Inhomogeneous
source and PHYS44 y->xi lift, infinite l>20 Coulomb barrier and full
continuous Schur inverse are still distinct, unproved interfaces.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import factorial, isqrt
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from time import perf_counter
import hashlib
import json

from .phys33_coupled_source import exp_negative_bounds,outward_decimal

FROZEN_SHA256="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
K=F(7,10)
R=F(7,10)
B=F(20)
L_MAX=20
L_CAP=L_MAX*(L_MAX+1)
C=F(59,70)
SCHEMA="WU088_HH_PHYS46_FINITE21_COULOMB_OUTGOING_VOLTERRA_V1"


def exp_positive_rational_upper(z:F,n:int=72)->F:
    """Rigorous upper for exp(z), z>=0, with positive geometric tail.

    sum_0^n z^k/k! + (z^(n+1)/(n+1)!)/(1-z/(n+2))
    is an exact rational upper for exp(z), provided n+2>z.
    """
    if not isinstance(z,F) or z<0 or not 4<=n<=256 or z>=n+2:
        raise ValueError("nonnegative Fraction and sufficient Taylor order")
    term=F(1)
    partial=term
    for k in range(1,n+1):
        term*=z/k
        partial+=term
    first=term*z/(n+1)
    return partial+first/(1-z/F(n+2))


def q0_of_r(ell:int,r:F)->F:
    if type(ell) is not int or not 0<=ell<=L_MAX or not isinstance(r,F) or r<=0:
        raise ValueError("physical ell and exact rational r>0")
    return K*K+2/r-F(ell*(ell+1),r*r)


def _energy_candidate(job:tuple)->dict:
    T,order,digits=job
    if type(T) is not int or not 29<=T<=40:
        raise ValueError("integer energy patch T in [29,40]")
    Tq=F(T)
    qmin=q0_of_r(L_MAX,Tq)
    # q_l has only a single MAXIMUM on r>=T, so
    # min(q_l(T),q_l(infty))>=q_lmax(T)>0.
    if not F(0)<qmin<K*K:
        raise ArithmeticError("outgoing positive energy regime not established")
    # ∫_T^infty |q_l'(r)|dr <=2/T + l(l+1)/T².
    variation=2/Tq+F(L_CAP,T*T)
    z=variation/qmin
    emax=exp_positive_rational_upper(z,order)
    M2_limit=2*K*K*emax*(1/qmin+1/(K*K))
    # M integer, strictly larger than required state bound:
    qfloor=M2_limit.numerator//M2_limit.denominator
    M=isqrt(qfloor)+1
    if M*M<=M2_limit:
        M+=1
    assert M*M>M2_limit
    delta=Tq-B
    if delta<=0:
        raise ValueError("energy matching should lie exterior to B")
    p1=2*(B-R)-2*C*delta
    p2=2*(Tq-R)
    if p1<=0 or p2<=0:
        raise ArithmeticError("exponential tail integrability not bounded")
    # Fixed exact 192-term reciprocal Taylor with positive enclosing error.
    e1=exp_negative_bounds(p1,192)[1]
    e2=exp_negative_bounds(p2,192)[1]
    screened_coeff=1+1/(B-R)
    q=F(M*M,1)/K*screened_coeff*(e1/(1+C)+e2)
    # Dimensionless finite-channel Banach operator contraction constant.
    alpha=q/(1-q) if q<1 else None
    pinv=1/(1-alpha) if alpha is not None and alpha<1 else None
    assert q>0
    return {
        "T_a0":T,
        "energy_qmin_exact":str(qmin),
        "qprime_total_variation_upper_exact":str(variation),
        "energy_exponent_exact":str(z),
        "exp_energy_upper_rational":outward_decimal(emax,16,True),
        "energy_state_squared_limit_upper":outward_decimal(M2_limit,16,True),
        "M_integer":M,
        "oscillator_A_operator_bound_exact":str(C),
        "physical_radial_exponential1_exact":str(p1),
        "physical_radial_exponential2_exact":str(p2),
        "q_exact":str(q),
        "q_upper":outward_decimal(q,digits,True),
        "alpha_exact":str(alpha) if alpha is not None else None,
        "Jost_boundary_relative_correction_upper":
            outward_decimal(alpha,digits,True) if alpha is not None else None,
        "boundary_inverse_factor_upper":
            outward_decimal(pinv,digits,True) if pinv is not None else None,
        "strict_contraction":q<1,
        "outgoing_boundary_Jost_invertible":alpha is not None and alpha<1,
        "_q":q,
    }


def _public_candidate(d:dict)->dict:
    return {k:v for k,v in d.items() if not k.startswith("_") and k!="q_exact" and k!="alpha_exact"}


def finite21_volterra_certificate(frozen:str|Path,candidate_T:tuple[int,...]=tuple(range(29,41)),
                                   workers:int=1,terms:int=72,digits:int=24)->dict:
    src=Path(frozen)
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if digest!=FROZEN_SHA256:
        raise ValueError("wrong immutable frozen H(1s)+H(1s) source")
    if not candidate_T or any(type(t) is not int or t<29 or t>40 for t in candidate_T):
        raise ValueError("bounded positive exterior patch search")
    if len(set(candidate_T))!=len(candidate_T):
        raise ValueError("duplicate energy-patch candidates")
    if workers not in (1,2,3,4) or not 48<=terms<=192 or not 12<=digits<=24:
        raise ValueError("bounded rational precision or host worker count")
    tic=perf_counter()
    jobs=[(t,terms,digits) for t in candidate_T]
    if workers==1:
        rows=list(map(_energy_candidate,jobs))
    else:
        with ProcessPoolExecutor(max_workers=workers,
                                 mp_context=get_context("forkserver")) as pool:
            rows=list(pool.map(_energy_candidate,jobs))
    best=min(rows,key=lambda d:(d["_q"],d["T_a0"]))
    q=best["_q"]
    if not q<F(1,2):
        raise ArithmeticError("strict outgoing Jost boundary invertibility not certified")
    alpha=q/(1-q)
    delta_coefficient=2*alpha/(1-alpha)
    # D=diag(H_l+(B)); U(B)=D(I+E), U'(B)=D'(I+E')
    # with ||E||,||E'|| <= alpha, hence
    # ||D^-1 (Z-Z_C) D|| <= max_l |H_l'(B)/H_l(B)| * 2alpha/(1-alpha).
    if delta_coefficient<=0:
        raise ArithmeticError("invalid perturbative DtN factor")
    return {
        "schema":SCHEMA,
        "source_sha256":digest,
        "model":"raw physical homogeneous Schr radial equation, finite l=0..20, m=0 (not transformed y, not forced xi)",
        "exterior_domain_a0":["20","+infinity"],
        "base_kappa":"7/10",
        "Coulomb_eta":"-10/7",
        "spectator_R":"7/10",
        "angular_channel_count":21,
        "potential":"(1+1/s)exp(-2s), s=|r zhat-R zhat|; full angular compression 21x21",
        "coupled_radial_equation":"U''+[diag(k²+2/r-l(l+1)/r²)+2 V21(r)] U=0",
        "outgoing_kernel":"K_l(r,t)=(H_l^+(r)H_l^-(t)-H_l^-(r)H_l^+(t))/(2 i k)",
        "kernel_properties":"K(t,t)=0, d_rK(t,t)=1, (d_r²+q_l(r))K=0 for r<t",
        "kernel_amplitude_bound":"|K_l(r,t)|<=|H_l^+(r)| |H_l^+(t)|/k for r<=t",
        "weighted_Banach_norm":"sup_{r>=20} ||U(r)||_{ell2(l=0..20)}/w(r)",
        "certified_weight":"w(r)=M exp[(59/70)(T-r)] for 20<=r<=T; w(r)=M for r>=T",
        "T_energy_patch_a0":best["T_a0"],
        "M_state_bound_integer":best["M_integer"],
        "uniform_min_radial_q_for_r_ge_T":best["energy_qmin_exact"],
        "uniform_oscillator_matrix_bound_exact":str(C),
        "selected_q_strict_upper":outward_decimal(q,digits,True),
        "selected_alpha_Jost_relative_error_upper":outward_decimal(alpha,digits,True),
        "Neumann_tail_after_first_Born_weighted_upper":outward_decimal(q*q/(1-q),digits,True),
        "Neumann_tail_after_second_Born_weighted_upper":outward_decimal(q*q*q/(1-q),digits,True),
        "outgoing_Jost_B_invertible":True,
        "selected_B_matrix_inverse_factor_upper":outward_decimal(1/(1-alpha),digits,True),
        "similarity_normalized_DtN_multiplier_upper":
            outward_decimal(delta_coefficient,digits,True),
        "similarity_normalized_DtN_bound":
            "||D^-1[Z_screened^21(B)-Z_C^21(B)]D||_2 <= multiplier * max_l |k H_l^+'(eta,kB)/H_l^+(eta,kB)|",
        "D_definition":"D=diag(H_l^+(eta,kB)), Z=U'(B)U(B)^-1, Z_C=diag(k H_l^+' / H_l^+)",
        "exact_mathematical_claim":"Existence, uniqueness, and invertibility of finite-21-channel homogeneous outgoing Jost matrix on r>=20 with specified m0 projection and original projected screened V",
        "all_candidates_sorted_original_order":[_public_candidate(d) for d in rows],
        "evaluated_patch_count":len(rows),
        "workers":workers,"elapsed_s":perf_counter()-tic,
        "scientific_status":"RIGOROUS_FINITE21_HOMOGENEOUS_OUTGOING_VOLTERRA_CONTRACTION_ONLY",
        "NOT_CERTIFIED":[
            "infinite angular hierarchy l>20 (large-l barrier has no uniform w(r))",
            "full physical noncentral outgoing DtN beyond 21 mode projection",
            "inhomogeneous scattered xi=F*y-phi source on r>=20",
            "driven origin and physical outgoing source-to-amplitude inverse",
            "incoming adjoint, sigma(E), Maxwellian k_HH(T) or rei_bianchi source admission",
        ],
    }
