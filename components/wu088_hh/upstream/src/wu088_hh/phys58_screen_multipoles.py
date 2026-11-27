"""PHYS58 R5: exact-rational exterior screened angular tail certificate.

Original immutable H(1s)+H(1s) h=-Delta/2-1/r-S(s),
S(s)=(1+1/s)exp(-2s), s=sqrt(r^2+R^2-2rR cos(theta)), R=7/10.

The bound holds for ALL r>=27, all ell/m, WITHOUT angular truncation.
It bounds the PHYSICAL MULTIPLICATION operator V=2S and low-to-high
angular transfers. It does NOT bound the OUTGOING DtN difference Z_S-Z_C.
"""
from __future__ import annotations

from fractions import Fraction as F
from hashlib import sha256
from math import factorial
from pathlib import Path

SCHEMA = "WU088_HH_PHYS58_R5_EXACT_SCREENED_ANGULAR_TAIL_V1"
FROZEN_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
R = F(7, 10)
B = F(27)
RHO_ELLIPSE = F(10)
ELL_LOW_MAX = 20
M_MAJOR = F(1, 4 * 10**19)  # exact strict bound for analytic |S(s)|
C_LEGENDRE = F(20,9) * M_MAJOR


def original_source_sha_guard(path: str | Path) -> str:
    actual = sha256(Path(path).read_bytes()).hexdigest()
    if actual != FROZEN_SHA:
        raise ValueError("original frozen source SHA256 differs")
    return actual


def taylor_exp_lower(x: F, n: int) -> F:
    """Finite exact positive Taylor partial sum <= exp(x) for x>=0."""
    if not isinstance(x, F) or x < 0 or type(n) is not int or n < 0 or n > 256:
        raise ValueError("nonnegative rational x and bounded nonnegative order")
    term=F(1)
    total=F(1)
    for k in range(1,n+1):
        term *= x/k
        total += term
    return total


def ellipse_min_square() -> F:
    """Minimum Re(s(z)^2) for r>=27 and z in Bernstein E_10.

    Re z <= (rho+1/rho)/2 = 101/20. The parabola
    r^2+R^2-2rR*(101/20) increases for r>=27.
    """
    major=(RHO_ELLIPSE+1/RHO_ELLIPSE)/2
    return B*B+R*R-2*B*R*major


def exact_r5_gates() -> dict:
    q=ellipse_min_square()
    assert q==F(2693,5)>F(23)**2
    assert B> R*(RHO_ELLIPSE+1/RHO_ELLIPSE)/2
    lower=taylor_exp_lower(F(46),46)
    assert lower>5*10**19  # exp(-46)<1/(5e19)=2e-20
    assert F(24,23)/F(5*10**19)<M_MAJOR
    return {
       "source_radius_R":str(R),"exterior_min_r":str(B),
       "Bernstein_rho":str(RHO_ELLIPSE),
       "min_Re_s_squared":str(q),
       "Re_s_strict_gt":23,
       "exp46_Taylor_order":46,
       "exp46_partial_sum_gt_5e19":lower>5*10**19,
       "sup_analytic_S_upper_exact":str(M_MAJOR),
       "Legendre_coefficient_prefactor_exact":str(C_LEGENDRE),
       "proved_infinite_angular":True,
       "status":"SCOPED_RIGOROUS_PHYSICAL_SCREENED_MULTIPLIER_ONLY",
    }


def legendre_coefficient_upper(n: int) -> F:
    """|(2n+1)/2*int_{-1}^1 S(mu) P_n(mu) dmu| for any r>=27.

    Use Cheb degree n-1 truncation in E_10, Legendre orthogonality,
    and ||P_n||_infty<=1. Valid n>=1 (n=0 bound M_MAJOR).
    """
    if type(n) is not int or n<0 or n>100_000:
        raise ValueError("bounded nonnegative integer angular index")
    if n==0:
        return M_MAJOR
    return F(2*n+1) * C_LEGENDRE / (10**n)


def legendre_tail_upper(degree: int) -> F:
    """Sup |S - sum_{n<=degree} A_n P_n|, for all r>=27.

    Since sum_{n>=p}(2n+1)x^n = x^p[(2p+1)/(1-x)+2x/(1-x)^2]
    with p=degree+1, x=1/10, and all p>=1.
    """
    if type(degree) is not int or degree<0 or degree>100_000:
        raise ValueError("bounded nonnegative integer polynomial degree")
    p=degree+1
    x=F(1,10)
    return C_LEGENDRE*x**p*(F(2*p+1)/(1-x)+2*x/(1-x)**2)


def low_to_high_2s_bound(degree:int, low_l_max:int=20) -> dict:
    """Norm of 2 Q_{ell>=lowmax+degree+1} S P_{ell<=lowmax}.

    The degree-degree Legendre polynomial S_degree cannot connect
    ell<=lowmax to ell>lowmax+degree, by Gaunt angular selection.
    Thus norm <=2||S-S_degree||_infty, exact all-m and all ell.
    """
    if type(low_l_max) is not int or low_l_max<0 or low_l_max>1000:
        raise ValueError("nonnegative low band")
    return {
      "original_low_ell_max":low_l_max,
      "physical_high_ell_min":low_l_max+degree+1,
      "legendre_degree":degree,
      "S_uniform_tail_upper_exact":str(legendre_tail_upper(degree)),
      "physical_2S_low_to_far_high_op_norm_upper_exact":str(2*legendre_tail_upper(degree)),
      "bound_is_independent_of_m":True,
      "r_domain_Bohr":"[27,infinity)",
      "NOT_DTN_BOUND":True,
    }


def make_certificate(path: str | Path, degrees=(0,2,4,6,8,10,12)) -> dict:
    src=original_source_sha_guard(path)
    out={"schema":SCHEMA,"frozen_SHA256":src,"gates":exact_r5_gates(),
         "theorem":"For every r>=27 all angular m and ell, ||2 Q_{ell>=21+N} S P_{ell<=20}|| <= 2 sum_{n>N}(2n+1) C_leg 10^-n",
         "selection_rule":"P_n(cos theta) couples only equal m and |ell-ell'|<=n with ell+ell'+n even",
         "positive_multipole_note":"Every exact Legendre A_n(r)>0 by positive Gaussian Laplace representation and i_n(2rRt)>0",
         "rows":[low_to_high_2s_bound(n) for n in degrees],
         "not_proved":["screened outgoing DtN Z_S or Z_S-Z_C", "weighted outgoing Coulomb LAP/Poisson", "physical full low-high P-Q Schur", "driven xi=Fy-phi, sigma(E), k_HH(T)"],
         "HH_R10":"OFF"}
    return out
