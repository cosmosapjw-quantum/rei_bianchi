"""PHYS61 source-locked infinite-angular, UPPER-half-plane screened exterior DtN.

NOT an on-shell / limiting-absorption theorem. Physical real E=49/200 Eh,
but fixed Im E=1/100 Eh. All radial and angular channels retained
as operator-theoretic objects; no discretization in the inequalities.

Use u=r psi on [27, infinity), Coulomb real A0^D selfadjoint,
A0(z)=-d²+ell(ell+1)/r²-2/r-k²-i*tau, tau=2*Im(E)>0;
A_S(z)=A_C(z)-V, V=2(1+1/s)exp(-2s).
"""
from __future__ import annotations
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

SOURCE_SHA = 'f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d'
B=F(27)
R=F(7,10)
K2=F(49,100)
TAU_DEFAULT=F(1,50)  # Imag(E)=tau/2=1/100 Hartree
V_DELTA_UP=F(3,10**23)
SQRT_B2_UP=F(15,4)  # > sqrt(27/2)


def source_gate(source:str|Path)->str:
    actual=sha256(Path(source).read_bytes()).hexdigest()
    if actual!=SOURCE_SHA:
        raise ValueError('ORIGINAL_FROZEN_NPZ_SHA256_MISMATCH')
    return actual


def exponential_positive_partial(x:F, terms:int)->F:
    if not isinstance(x,F) or x<0 or type(terms) is not int or not 0<=terms<=1000:
        raise ValueError('invalid exact rational exponential series')
    total=curr=F(1)
    for j in range(1,terms+1):
        curr=curr*x/j
        total+=curr
    return total


def screened_delta_rational(terms:int=160)->F:
    """Exact >sup_{r>=27,mu} V(r,mu); also radial exp[-2(r-B)] envelope."""
    x=2*(B-R)  # =263/5
    lo=exponential_positive_partial(x,terms)
    return 2*(1+1/(B-R))/lo


def exact_obligations()->dict:
    delta=screened_delta_rational()
    assert B==27 and K2==F(49,100)
    assert F(1,B*B) < F(1,B)
    assert F(B,2) < SQRT_B2_UP**2
    assert delta < V_DELTA_UP
    # Every integer ell>=0, all m: v_l(r)=g_l exp[-(ell+1)(r-B)/B].
    # ||v||_L2 <= sqrt(B/2)||g||_X,
    # ||A_C v||_L2 <= {sqrt(B/2)(B^-2+2/B+k²+tau)+B^-3/2}||g||_X.
    return {
      'exact_screen_upper_by_partial_Taylor':str(delta),
      'actual_screen_sup_strict_lt':str(V_DELTA_UP),
      'trace_weight':'W_ell=ell+1; X=H^1/2(S²) for reduced radial u=r psi',
      'all_angular_no_truncation':True,
      'radial_domain_Bohr':'[27,infinity)',
      'original_h':'-Delta/2-1/r-(1+1/s)*exp(-2*s), s=|x-(7/10) zhat|',
    }


def uniform_bounds(tau:F=TAU_DEFAULT)->dict:
    """Exact rational upper-half-plane operator-norm enclosure.

    True for any rational tau>delta, no claim of tau-down-to-zero uniformity.
    Fallback constants use sqrt(B/2)<15/4 and B^-3/2<1/B.
    """
    if not isinstance(tau,F) or tau<=0:
        raise ValueError('IM_ENERGY_MUST_BE_POSITIVE')
    delta=screened_delta_rational()
    assert delta<V_DELTA_UP
    if tau<=V_DELTA_UP:
        raise ValueError('SMALLNESS_GATE_NOT_CERTIFIED')
    c=F(1,B*B)+F(2,B)+K2+tau
    # ||G_C(tau)|| <=1/tau on all radial/angular zero-Dirichlet L2.
    cp=SQRT_B2_UP+(SQRT_B2_UP*c+1/B)/tau
    q=V_DELTA_UP/tau
    dt=V_DELTA_UP*cp*cp/(1-q)
    assert 0<q<1 and dt>0
    return {
      'schema':'WU088_HH_PHYS61_UPPER_HALF_PLANE_ALL_ANGULAR_DTN_V1',
      'tau_twice_imag_energy':str(tau),
      'complex_spectral_energy_E_hartree':f'49/200 + i*({tau}/2)',
      'poisson_norm_upper':str(cp),
      'screened_neumann_q_upper':str(q),
      'dtn_difference_norm_upper':str(dt),
      'all_angular_zero_dirichlet_coulomb_resolvent_norm_upper':str(1/tau),
      'physical_screen_multiplier_sup_bound':str(V_DELTA_UP),
      'poisson_screened_norm_upper':str(cp/(1-q)),
      'source_scope':'ACTUAL_NONCENTRAL_SCREENED_INFINITE_ANGULAR_AT_IM_E_POSITIVE_ONLY',
      'source_SHA256_expected':SOURCE_SHA,
      'not_claimed':[ 'positive real energy outgoing LAP tau->0',
          'uniform finite-L outgoing norm at tau=0',
          'driven xi, incoming adjoint, sigma(E), k_HH(T)',
          'rei_bianchi HH_R10' ],
      'HH_R10':'OFF',
    }


def certified_contract(source:str|Path)->dict:
    sha=source_gate(source)
    bounds=uniform_bounds(TAU_DEFAULT)
    exact=exact_obligations()
    if F(bounds['poisson_norm_upper']) != F(224285,1944):
        raise ArithmeticError('unexpected source-locked Poisson certificate')
    if not F(bounds['dtn_difference_norm_upper'])<F(4,10**19):
        raise ArithmeticError('upper-half-plane DtN difference >4e-19')
    return {'source_SHA256_actual':sha, 'source_identity':'BYTE_IDENTITY_PASS',
            'science':bounds, 'source_gates':exact,
            'numeric_scope':'EXACT_RATIONAL_BOUND_NOT_ON_SHELL_SCIENCE_PASS'}
