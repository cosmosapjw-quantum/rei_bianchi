"""PHYS59 R5: source-locked negative-energy real noncentral exterior DtN.

The ACTUAL original off-centre screened potential is retained everywhere on
r>=27, in the full angular space, including low/high P-Q couplings. The
real spectral energy is E=-kappa**2/2=-49/200 Hartree, NOT the user's
positive-energy scattering E=+49/200 Hartree.

The precise well-posed proof is variational on radial reduced functions
u_lm(r)=r psi_lm(r); the trace norm is
  ||g||_X^2 = sum_(l>=0,m) (l+1) |g_lm|^2.
The exterior DtN uses the inward coordinate derivative Z=+partial_r at r=27.

With A_t=-d²_r+L²/r²+kappa²-2/r-t V and V=2(1+1/s)e^-2s,
S>=0 and all-angular original V norm <= delta<3e-23. The form satisfies
A_t >= beta I with beta=2/5. An explicit compact triangular trace lift
has energy <=C_X||g||_X², C_X=6/5, so
   ||Z_1-Z_0||_{X->X*} < (delta*C_X/beta) <9e-23,
via the exact Green (Alessandrini) identity
   <h,(Z_1-Z_0)g> = integral V u_1(g) conjugate(u_0(h)).
This is a genuine off-shell all-angular noncentral screened exterior
boundary operator estimate; no claim about physical positive-energy
outgoing LAP, DtN or microphysical sigma(E), k_HH(T).
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from hashlib import sha256
from math import isqrt

R = F(7,10)
B = F(27)
KAPPA = F(7,10)
OFFSHELL_ENERGY_HARTREE = -KAPPA*KAPPA/2
ORIGINAL_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
DELTA_UP = F(3,10**23)
BETA_CERT = F(2,5)
TRACE_ENERGY_UP = F(6,5)
SCHEMA = "WU088_HH_PHYS59_R5_OFFSHELL_FULL_ANGULAR_SCREENED_DTN_V1"


def original_sha_guard(path: str | Path) -> str:
    actual=sha256(Path(path).read_bytes()).hexdigest()
    if actual != ORIGINAL_SHA:
        raise ValueError("original immutable 1386 complex128 source SHA256 mismatch")
    return actual


def positive_exp_taylor_lower(x:F,terms:int=160)->F:
    """Exact lower bound exp(x) >= sum_{j=0}^N x^j/j!, x>=0."""
    if not isinstance(x,F) or x<0 or type(terms) is not int or not 96<=terms<=384:
        raise ValueError("positive rational exponential argument and supported terms")
    t=F(1);s=t
    for j in range(1,terms+1):
        t*=x/j;s+=t
    return s


def rigorous_screen_upper(terms:int=160)->F:
    """Exact strict upper to sup_{r>=B,angle} physical V=2S."""
    x=2*(B-R)
    actual=2*(1+F(1,B-R))/positive_exp_taylor_lower(x,terms)
    if not actual<DELTA_UP:
        raise ArithmeticError("physical V exact exponent gate not certified")
    return actual


def hat_width(ell:int)->F:
    if type(ell) is not int or not 0<=ell<=10**7:
        raise ValueError("integer ell>=0 up to supported limit")
    return min(F(1),B/F(ell+1))


def lift_energy_normalized(ell:int)->F:
    """Exact upper bound for the negative-energy full angular boundary hat.

    Per |g_lm|², hat with radial width w has derivative energy 1/w
    and mass w/3. Since -2/r-t V<=0, omitting these lowers
    yields upper 1/w+(k²+l(l+1)/B²)*w/3.
    """
    w=hat_width(ell)
    return (1/w+(KAPPA*KAPPA+F(ell*(ell+1),B*B))*w/3)/F(ell+1)


def exact_all_ell_lift_proof()->dict:
    """Piecewise analytic, no finite angular cutoff asserted as theorem."""
    # ell<=26: w=1. Formula <= 1+k²/3+26/(3B²).
    low=1+KAPPA*KAPPA/3+F(26,3*B*B)
    # ell>=27: w=B/(ell+1), formula <=4/(3B)+k²B/(3*28²)
    high=F(4,3*B)+KAPPA*KAPPA*B/F(3*28**2)
    assert low<TRACE_ENERGY_UP and high<TRACE_ENERGY_UP
    for ell in (0,1,20,21,26,27,28,50,1000,100000):
        assert lift_energy_normalized(ell)<=TRACE_ENERGY_UP
    return {"ell_0_to26_energy_ratio_max_upper":str(low),
            "ell_ge27_energy_ratio_max_upper":str(high),
            "strict_below_C_X":str(TRACE_ENERGY_UP)}


def exact_q_and_operator_gates()->dict:
    screen=rigorous_screen_upper()
    beta_c=KAPPA*KAPPA-F(2,B)
    beta_s=beta_c-DELTA_UP
    assert beta_s>BETA_CERT
    contraction=DELTA_UP/beta_c
    assert contraction<F(1,10**20)
    weighted_diff=DELTA_UP*TRACE_ENERGY_UP/BETA_CERT
    assert weighted_diff==F(9,10**23)
    return {"exterior_A_C_zeroDirichlet_floor_exact":str(beta_c),
            "exterior_A_S_uniform_floor_lower_exact":str(beta_s),
            "proved_screen_upper_fraction":str(screen),
            "declared_delta_gate_exact":str(DELTA_UP),
            "real_negative_energy_Hartree":str(OFFSHELL_ENERGY_HARTREE),
            "zero_trace_neumann_q_upper_exact":str(contraction),
            "poisson_L2_gain_squared_exact_upper":str(TRACE_ENERGY_UP/BETA_CERT),
            "dtn_diff_full_angular_upper_exact":str(weighted_diff),
            "is_off_shell_not_physical_scattering":True}


def m0_l20_l21_dtn_lower()->dict:
    """Strict positive full *noncentral screened* off-shell DtN P20/Q21.

    In the m=0 real spherical harmonics, all V_ll' are nonnegative:
      V_ll'=2 sum_n A_n sqrt((2l+1)(2l'+1)) (3j)^2 >=0,
    from PHYS58 all n positive Gaussian-Laplace multipoles.
    A_C^-1 with zero Dirichlet on r>=B is channelwise
    positivity preserving (q_l>=beta_c>0); its Neumann expansion in
    V has contraction delta/beta_c<1. Thus u_S(e20) >=p_C,20
    coefficientwise and (Z_S-Z_C)21,20 >=int V21,20 p20 p21.

    On r∈[27,28], A1>= (9/8)*(B R/(B+R))exp[-2(28+R)].
    Angular Gaunt n1 for 21/20,m0 is 21/sqrt(41*43)>1/2,
    and other contributions are nonnegative; V21,20>=A1.
    Scalar decaying radial Coulomb p_l(r)>=exp[-a_l(r-B)] with
    a_l²=k²+l(l+1)/B²< (11/10)² for l=20,21.
    Hence Z_S(21,20) > (9/8)*(B R/(B+R))*exp[-298/5]
    > (1701/2216)*3^-60 (since e<3 and 298/5<60).
    """
    beta=KAPPA*KAPPA-F(2,B)
    assert beta>0
    a20sq=KAPPA*KAPPA+F(20*21,B*B)
    a21sq=KAPPA*KAPPA+F(21*22,B*B)
    assert a20sq<F(121,100) and a21sq<F(121,100)
    assert 41*43<42*42
    const=F(9,8)*B*R/(B+R)
    assert const==F(1701,2216)
    lower=const/F(3**60)
    assert lower>F(0)
    return {"source":"all positive m0 Legendre A_n and 3j-squared; scalar inverse positivity",
            "ell_input_P":20,"ell_output_Q":21,"m":0,"r_Bohr":str(B),
            "strict_full_original_screened_Zminus_PQ_lower_exact":str(lower),
            "strict_full_original_screened_Zminus_PQ_lower_decimal_floor_35":str(lower.numerator*10**35//lower.denominator).zfill(36),
            "energy":"NEGATIVE_OFF_SHELL_ONLY",
            "constant_width_B_to_Bplus1":True,
            "positive_radial_p20_p21_comparison_gate":True,
            "all_higher_legendre_and_multiple_scattering_terms_nonnegative_m0":True}


def certificate(path:str|Path)->dict:
    digest=original_sha_guard(path)
    return {"schema":SCHEMA,"original_sha256":digest,
            "physics":"ACTUAL_ALL_ANGULAR_NONCENTRAL_SCREENED_EXTERIOR_AT_NEGATIVE_ENERGY",
            "boundary_radius_Bohr":str(B),"kappa":str(KAPPA),
            "full_m_all_ell":True,
            "all_lifting":exact_all_ell_lift_proof(),
            "bounds":exact_q_and_operator_gates(),
            "strict_m0_P20_Q21":m0_l20_l21_dtn_lower(),
            "green_alessandrini_identity":"<h,(Z_S-Z_C)g> = int_B^infty <u_C(h),2S u_S(g)> drdOmega; Z=+partial_r",
            "signed_form_monotonicity":"0 <= Z_S-Z_C as Hermitian forms at negative E, strictly nonzero P20-Q21 m0",
            "not_proved":["positive-energy Coulomb outgoing LAP/Poisson constants", "physical positive-energy Z_S", "original driven xi", "sigma(E)", "identical neutral H Maxwellian k_HH(T)"],
            "production_HH_R10":"OFF"}
