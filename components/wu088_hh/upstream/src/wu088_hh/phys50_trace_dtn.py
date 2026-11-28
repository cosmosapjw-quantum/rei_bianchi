"""PHYS50: nonzero high-angular boundary traces and screened Dirichlet DtN.

Source-locked original H(1s)+H(1s) h=-Delta/2-1/r-(1+1/s)e^-2s,
s=|x-R z|, k=R=7/10, radial collar B=20,T=27 Bohr.
P low is ell<=20, Q high is all ell>=21 and all m.

On the high angular trace space X:
 ||g||_X² = sum_(ell>=21,m) (ell+1)(|g_B,ellm|²+|g_T,ellm|²)
the physically ORIGINAL screened high operator
 A_H=Q[-d²/dr²+ell(ell+1)/r²-2/r-k²-2S]Q
with two arbitrary prescribed HIGH Dirichlet traces admits a unique
weak solution. The positive HIGH-only Dirichlet-to-Neumann form obeys
  0<=<g,Lambda g> <= C_trace||g||_X²
  C_trace=2/(T-B)+(T-B)/(6B²)=4849/16800.
This follows by the l-dependent compact triangular trace extension
with width h_l=(T-B)/(2(l+1)), energy minimization, and actual screened
S>=0. Potential is bounded below uniformly by PHYS49 beta=barrier-delta.

For original low driving f=+2 Q S P u_P, decompose into harmonic
nonzero trace solution + previously certified PHYS49 zero-trace
particular solution. This yields a rigorous all-ell conditional
L2 bound and a controlled low-channel feedback source.

CRITICAL: exact DtN is for the POSITIVE finite radial COLLAR with two
Dirichlet boundaries. This is not outgoing Coulomb DtN, does not supply
the unknown physical traces at r=20,27 and not a physical H-H rate.
"""
from __future__ import annotations

from fractions import Fraction as F
from pathlib import Path
import hashlib
from math import isqrt

from .phys49_dirichlet_collar import (
    FROZEN_SHA,B,T,R,L,POINCARE_FLOOR,barrier_floor,dirichlet_floor,
    original_screened_coupling_max
)
from .phys47_high_ell import scientific_up

SCHEMA="WU088_HH_PHYS50_NONZERO_HIGH_TRACE_DIRICHLET_DTN_V1"
D=T-B
C_TRACE=F(2,D)+F(D,6*B*B)
FIRST_HIGH=L+1


def sqrt_upper_fraction(q:F,decimals:int=24)->F:
    """Exact rational ceiling for sqrt(q) at 1e-decimals."""
    if not isinstance(q,F) or q<0 or type(decimals) is not int or not 12<=decimals<=36:
        raise ValueError("nonnegative rational and decimal precision")
    scale=10**decimals
    n=(q.numerator*scale*scale)//q.denominator
    x=isqrt(n)
    if F(x,scale)**2<q:x+=1
    out=F(x,scale)
    assert out*out>=q
    return out


def hat_width(ell:int)->F:
    if type(ell) is not int or ell<21 or ell>1000000:
        raise ValueError("positive physical high angular ell>=21")
    return D/F(2*(ell+1))


def hat_energy_bound_per_pair(ell:int)->F:
    """Upper a(v_l,v_l)/( |g_l(B)|²+|g_l(T)|² ).

    Both hats have disjoint supports for high ell; derivative energy
    1/h, potential <= l(l+1)/B² on whole collar and mass h/3.
    Actual screened potential -2S decreases energy, so its omission
    is a conservative bound on a(v,v).
    """
    h=hat_width(ell)
    return 1/h+F(ell*(ell+1),B*B)*h/3


def verified_high_trace_lifting(frozen:str|Path,terms:int=192,digits:int=24,
                                 examples:tuple[int,...]=(21,28,41,61,120,300))->dict:
    src=Path(frozen)
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if digest!=FROZEN_SHA:
        raise ValueError("original immutable source byte identity mismatch")
    if type(terms) is not int or not 128<=terms<=384:
        raise ValueError("positive exponential terms")
    if not 16<=digits<=27:
        raise ValueError("bounded exact outward precision")
    if not examples or len(set(examples))!=len(examples):
        raise ValueError("at least one distinct representative high ell")
    delta=original_screened_coupling_max(terms)
    bmin=barrier_floor(FIRST_HIGH)
    beta=bmin-delta
    lam=dirichlet_floor(FIRST_HIGH)
    alpha=delta/(lam-delta)
    if beta<=0 or alpha>=1:raise ArithmeticError("nonpositive original high trace form")
    c=C_TRACE
    if c!=F(4849,16800):raise ArithmeticError("original trace constant changed")
    # E(u_g)<=E(v_g)<=C_trace||g||_X².
    # E(u_g)>=beta||u_g||² (positive barrier on the full affine space).
    # E(f_D inverse)<= ... and ||f_D solution|| <=alpha ||u_P||.
    gain=sqrt_upper_fraction(c/beta,digits)
    if not gain*gain>=c/beta:raise ArithmeticError("upward sqrt not rigorous")
    pair=[]
    for ell in examples:
        h=hat_width(ell)
        e=hat_energy_bound_per_pair(ell)
        if e>c*(ell+1):
            raise ArithmeticError("all-high-ell uniform trace estimate violated")
        pair.append({
            "ell":ell,
            "hat_width_exact_Bohr":str(h),
            "lift_unperturbed_energy_upper_per_boundary_amplitude_pair":str(e),
            "energy_over_ell_plus_one_upper":scientific_up(e/(ell+1),digits),
            "ramp_supports_disjoint":2*h<=D,
        })
    return {
        "schema":SCHEMA,
        "source_sha256":digest,
        "radial_Coulomb_reference":"central -1/r, kappa=7/10, original screened offcentre -S",
        "radius_interval_a0":["20","27"],
        "angular_space":"all m, all ell>=21; low input P_ell<=20",
        "trace_space":"X with ||g||_X²=sum_(ell>=21,m) (ell+1)(|g_B|²+|g_T|²)",
        "nonzero_trace_allowed":True,
        "explicit_lift":"disjoint piecewise-linear hats at B,T of width h_l=(T-B)/(2(l+1))",
        "full_form":"a(u,v)=sum int (u'_ell conjugate(v'_ell)+(ell(ell+1)/r²-2/r-k²)u_ell conj(v_ell)) dr -2 int S(s) u conj(v) drdOmega",
        "exact_trace_energy_coefficient":str(c),
        "infinite_high_trace_DtN_form":"<g,Lambda_D g>=a(u_g,u_g), 0<=...<=C_trace||g||_X²; lambda positive selfadjoint X->X*",
        "outward_flux_sign":"Lambda_D g=(-u'_high(B),u'_high(T)) as a boundary dual pairing",
        "exact_min_barrier":str(bmin),
        "positive_nonzero_trace_form_lower_exact":str(beta),
        "screened_twoS_sup_upper":scientific_up(delta,digits),
        "all_high_zero_trace_Poincare_floor_exact":str(lam),
        "original_PHYS49_zero_trace_force_gain_upper":scientific_up(alpha,digits),
        "trace_to_high_homogeneous_L2_gain_upper":scientific_up(gain,digits),
        "trace_to_high_L2_gain_sqrt_rational_up":str(gain),
        "physical_low_to_high_response_with_trace":"||u_H||_L2 <= gamma||g||_X + alpha||u_P||_L2, source f=+2QS P u_P",
        "screened_high_to_low_feedback_from_unknown_traces_upper":
            scientific_up(delta*gain,digits),
        "screened_high_to_low_feedback_from_low_field_upper":
            scientific_up(delta*alpha,digits),
        "sample_high_ell_hats":pair,
        "scientific_scope":"RIGOROUS_INFINITE_HIGH_ANGULAR_NONZERO_DIRICHLET_TRACE_DTN_BOUNDED_FINITE_COLLAR",
        "physical_outgoing_high_trace":"UNKNOWN_NOT_SUPPLIED",
        "NOT_CERTIFIED":[
           "physical outgoing Coulomb DtN on r>=27 and actual high trace values at B,T",
           "original driven xi=F*y-phi high-angular exterior source and regular origin",
           "full global continuum inverse, incoming adjoint or microscopic sigma(E)",
           "thermal k_HH(T) or rei_bianchi HH_R10 source admission",
        ],
    }
