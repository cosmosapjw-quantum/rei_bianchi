"""PHYS57 exact-rational all-l Coulomb sign and finite-flux certificates.

Research-specific theorem uses the *attractive central Coulomb* reference at
kappa=7/10, r=27 (rho=189/10), eta_C=-10/7. The Nicholson/Erdelyi
positive Laplace representation of A_l**2=F_l**2+G_l**2 (Brune-Hale-Paris
arXiv:1708.07554, Eq.16--21) proves Re Z_l<0 for EVERY integer l>=128,
not just an empirically sampled finite range. Exact rational whole-tail proof.

The remaining finite channels 21<=l<=127 have a source-independent analytic
lower bound on positive Wronskian current, from an energy + logarithmic-norm
bound at T=512, propagating to B=27. The bound is very conservative.

These two certificates CLOSE the prerequisites of the *conditional* PHYS56
hybrid-Schur inverse bound, for original SCREENED COLLAR + CENTRAL Coulomb
OUTER domain. They do NOT establish the fully screened outer DtN or rates.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

SCHEMA="WU088_HH_PHYS57_EXACT_COULOMB_CUTOFF_FINITE_FLUX_V1"
FROZEN_SHA="f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
K=F(7,10)
ABS_ETA=F(10,7)
RHO=F(189,10)
B=27
T=512
L=128
ELL_FIRST=21
ELL_FINITE_LAST=L-1
ANGULAR_MAX=ELL_FINITE_LAST*(ELL_FINITE_LAST+1)
C_D=F(9,1000)
C_TRACE=F(4849,16800)


def source_sha_guard(path: str|Path)->str:
    digest=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest!=FROZEN_SHA:
        raise ValueError("frozen original H-H input differs from byte lock")
    return digest


def nicholson_rational_certificate()->dict:
    """Certify the attractive Coulomb Re Z_l(27)<0, uniformly l>=128.

    For a=10/7, u=(z²/(1+z²)), d_0=1 and
    d_(n+1)=d_n*((n-l)^2+a²)/(n+1)^2>0.
    Q(z)=exp(-2a arctan z)*(1+z²)^l sum_n d_n u^n.
    Nicholson A²=1+int_0^inf exp(-2rho*z) Q'(z) dz.
    Then (A²)'=-2 int_0^inf z exp(-2rho*z) Q'(z) dz.

    The derivative is nonnegative for z>=a/l. On 0..a/l,
    F(u)<= exp(2(l+a)z), Q<=exp(2a+3a²/l)<e³<27 and
    the possible negative integral magnitude <=27*a³/l².
    On 1..2, Q'>=2(l-a)*Q/5, Q>=exp(-a*pi)*2**l,
    exp(-4*rho-a*pi)>exp(-81)>3**(-81).
    Hence positive integral >=2(l-a)/5 *2**l/3**81.
    At l=128 this is already strictly larger than negative part;
    lhs increases, rhs decreases for all larger l.
    """
    assert ABS_ETA>0 and L>=2
    assert 4*RHO + ABS_ETA*F(22,7)<81  # rational pi<22/7
    small_exponent=2*ABS_ETA+3*ABS_ETA**2/L
    assert small_exponent<3
    z0=ABS_ETA/L
    assert F(0)<z0<1
    positive_lower=F(2,5)*(L-ABS_ETA)*2**L/F(3**81)
    negative_upper=27*ABS_ETA**3/L**2
    assert positive_lower>negative_upper
    return {
        "ell_cutoff":L,
        "radius_Bohr":B,
        "rho_exact":str(RHO),
        "attractive_eta_exact":"-"+str(ABS_ETA),
        "origin":"Nicholson positive amplitude Laplace kernel Eq.16-21 of Brune Hale Paris (2017)",
        "hypergeometric_coefficients": "d[n+1]=d[n]*((n-ell)^2+a^2)/(n+1)^2 >0",
        "monotone_interval":"Q'(z)>=0 for all z>=a/ell; negative part only 0<z<a/ell",
        "negative_integral_upper_at_cutoff_exact":str(negative_upper),
        "positive_integral_lower_at_cutoff_exact":str(positive_lower),
        "positive_minus_negative_exact":str(positive_lower-negative_upper),
        "relative_margin_floor_at_cutoff_exact":str(positive_lower/negative_upper),
        "pi_upper":"22/7",
        "exp_max_exponent_small_z_exact":str(small_exponent),
        "exp_large_z_floor":"exp(-4rho-a*pi)>3^-81",
        "all_integer_ell_gte_cutoff_sign": "PROVED_Re_Z_C_ell_strictly_negative",
        "status":"RIGOROUS_SOURCE_CONVENTION_SPECIFIC_ANALYTIC_LARGE_ELL_SIGN",
    }


def finite_channel_flux_certificate()->dict:
    """For 21<=l<=127 at B=27, exact lower Wronskian-current floor.

    q_l=k²+2/r-l(l+1)/r²; at T=512 q_l>=k²-Lambda/T²>1/4,
    int_T^infty |q'|<=2/T+Lambda/T²<1/8. Energy
    E=|H_r'|²+q|H|² has E(infty)=2k² and |E'|<=|q'|E/qmin,
    so E(T)<4k² (since e^(1/2)<2). For Y=(H,H_r'/k),
    ||Y(T)||<4. On [B,T], symmetric-part log norm is
      |k-q/k|/2<= (Lambda/r²+2/r)/(2k).
    ln(512/27)<3 (because e>8/3 and (8/3)^3=512/27).
    Thus D <=[Lambda*(1/B-1/T)+6]/(2k) < 412.
    Therefore |H(B)| < 4 exp(D), and Wronskian
      j_l(B)=k/|H_l(B)|² > k/(16*3^824).
    Divide by l+1<=128 to obtain uniform finite-exception jstar.
    """
    lam=ANGULAR_MAX
    q_floor=K*K-F(lam,T*T)
    variation=F(2,T)+F(lam,T*T)
    assert q_floor>F(1,4)
    assert variation<F(1,8)
    # For e^(V/q_min)<e^(1/2)<2, ||Y(T)||<4.
    assert 4*(4*K*K+1)<16
    # log(T/B)<3 because e>8/3 and (8/3)^3=T/B exactly.
    assert F(8,3)**3==F(T,B)
    exponent_D=(lam*(F(1,B)-F(1,T))+6)/(2*K)
    n=int(2*exponent_D)
    if F(n)<2*exponent_D:
        n+=1
    assert n==824
    # e<3, so exp(2 D) < 3**N with N = ceil(2D).
    jstar=K/F(16*L*(3**n))
    assert jstar>0
    return {
        "finite_ell_range_inclusive":[ELL_FIRST,L-1],
        "propagation_radius_Bohr":T,
        "qmin_lower_reference_exact":str(q_floor),
        "total_variation_bound_exact":str(variation),
        "lognorm_integral_up_exact":str(exponent_D),
        "twice_lognorm_ceiling_integer":n,
        "Y_energy_amplitude_at_T_upper":4,
        "finite_channel_flux_jstar_exact":str(jstar),
        "finite_channel_flux_jstar_numerator":jstar.numerator,
        "finite_channel_flux_jstar_denominator_decimal":str(jstar.denominator),
        "rigor":"exact_rational_Energy_and_logarithmic_norm_no_f64_Wronskian",
        "status":"RIGOROUS_ALL_FINITE_EXCEPTION_Wronskian_BOUND",
    }


def hybrid_inverse_certificate(original_source: str|Path)->dict:
    """Quantifies PHYS56's formerly conditional hybrid X*->X Schur estimate."""
    digest=source_sha_guard(original_source)
    tail=nicholson_rational_certificate()
    finite=finite_channel_flux_certificate()
    jstar=F(finite["finite_channel_flux_jstar_exact"])
    factor=(1+C_TRACE/C_D)**2
    inverse_up=factor*max(1/C_D,1/jstar)
    assert inverse_up>0 and inverse_up.denominator>0
    return {
        "schema":SCHEMA,
        "frozen_npz_sha256":digest,
        "physical_hamiltonian":"h=-Delta/2-1/r-(1+1/s)exp(-2s), s=|x-(7/10)zhat|",
        "original_eta_xi":"eta=Fy, xi=Fy-phi, distinct eta_C=-10/7",
        "angular_scope":"all ell>=21, all m, original screened collar + CENTRAL_COULOMB outer",
        "tail_sign_certificate":tail,
        "finite_exception_current_certificate":finite,
        "c_D_exact":str(C_D),
        "C_trace_exact":str(C_TRACE),
        "norm_X":"sum_(ell>=21,m)(ell+1)|g_lm|^2",
        "PHYS56_Schur_inverse_formula": "(1+C_trace/c_D)^2*max(1/c_D,1/jstar)",
        "hybrid_inverse_norm_upper_exact":str(inverse_up),
        "hybrid_inverse_upper_log10_approx_DIAGNOSTIC":len(str(inverse_up.numerator))-len(str(inverse_up.denominator)),
        "status":"RIGOROUS_QUANTIFIED_INFINITE_HIGH_HYBRID_INVERSE",
        "not_certified":[
            "full noncentral screened exterior all-angular Z_S and norm Z_S-Z_C",
            "any quantified observable low/full P-Q boundary matching",
            "original driven xi, regular origin, incoming adjoint",
            "physical sigma(E), Maxwellian identical-H k_HH(T)",
            "rei_bianchi HH_R10 (must remain OFF)",
        ],
    }


def write_json(path:str|Path, data:dict)->None:
    out=Path(path);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
