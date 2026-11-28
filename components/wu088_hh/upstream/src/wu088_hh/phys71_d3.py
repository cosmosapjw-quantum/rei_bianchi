"""Certified third Born panels using the two saved PHYS68/69 source rows.

No first/second Born integration is called here.  The saved q-center balls
are reused and their analytic derivatives are regenerated.  A new forward
primitive P'=q/f_j**2, P(B)=0 gives U=f_j P.  D3 is the integral of
U_21^T V U_20, with a bilinear (not Hermitian) angular contraction.
All coordinates and derivatives are in the original atomic convention.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import platform
import time

import flint
from flint import acb, acb_series, arb, ctx

from .phys67_coulomb_certificate import complex_ball_record, dyadic_ball, restore_ball, restore_complex_ball
from .phys67_first_born import legendre_coefficients
from .phys68_angular import R, angular_complex_disk_bound, angular_taylor_coefficients, monomial_laurent_pairs
from .phys68_profiles import cauchy_tail, local_coulomb_majorant, norm_radius_l1, polynomial_integral
from .phys68_taylor import coulomb_taylor, inflate_complex, rational_ball


@dataclass(frozen=True)
class D3Request:
    max_ell: int = 36
    ell: int = 21
    ellprime: int = 20
    m: int = 0
    boundary: str = "27"
    outer: str = "65"
    half_width: str = "1/4"
    zero_free_radius: str = "1/2"
    majorant_radius: str = "2"
    degree: int = 80
    precision_bits: int = 384
    coefficient_bits: int = 1024
    absolute_goal: str = "1e-78"
    HH_R10: str = "OFF"

    def validate(self):
        expected = asdict(D3Request())
        actual = asdict(self)
        # This first implementation deliberately binds the already certified
        # 73 source pairs and common 76-panel geometry.  Extending that geometry
        # needs new input evidence, not coercion of this request.
        for k in expected:
            if type(actual[k]) is not type(expected[k]) or actual[k] != expected[k]:
                raise ValueError(f"unsupported fixed PHYS71 request field: {k}")
        return self


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def series(coefficients, degree):
    return acb_series(list(coefficients), prec=degree+1)


@lru_cache(maxsize=129)
def _moment_constants(power, bits):
    """Exact Laurent construction, followed by explicitly enclosed exponentials."""
    with ctx.workprec(bits):
        plus, minus = (2*rational_ball(R)).exp(), (-2*rational_ball(R)).exp()
        return tuple(rational_ball(a)*plus + rational_ball(b)*minus
                     for a, b in monomial_laurent_pairs(power))


def monomial_moments(center, degree, max_power, coefficient_bits=1024):
    """Taylor series for I_n(r)=integral_-1^1 mu^n V(r,mu) dmu.

    The change d=r+t gives I_n=2 exp(-2r)/R times the inherited exact
    monomial Laurent polynomial.  This includes the physical V=2S once.
    The caller owns precision/cap and supplies a separate analytic remainder.
    """
    if type(max_power) is not int or not 0 <= max_power <= 128:
        raise ValueError("monomial degree must be an exact integer in 0..128")
    radial = series([acb(rational_ball(F(center))), acb(1)], degree)
    inv = radial.inv()
    factor = (-2*radial).exp() * (2/rational_ball(R))
    result = []
    for n in range(max_power+1):
        value = series([acb(0)], degree)
        for coefficient in reversed(_moment_constants(n, coefficient_bits)):
            value = value*inv + coefficient
        result.append(value*factor)
    return result


def angular_contraction(u_a, u_b, moments, degree):
    """Exact polynomial angular integration for m=0, with ball coefficients.

    The polar basis is sqrt((2j+1)/2) P_j.  Transform both vectors once,
    form their ordinary polynomial product, and contract with V moments.
    Only 2L+1 moment functions are needed instead of (L+1)^2 V entries.
    """
    if len(u_a) != len(u_b) or not u_a or len(moments) < 2*len(u_a)-1:
        raise ValueError("complete equal angular vectors and moment coverage required")
    length = len(u_a)
    aa = [series([acb(0)], degree) for _ in range(length)]
    bb = [series([acb(0)], degree) for _ in range(length)]
    for j in range(length):
        factor = rational_ball(F(2*j+1, 2)).sqrt()
        for n, c in enumerate(legendre_coefficients(j)):
            if c:
                weight = factor*rational_ball(c)
                aa[n] += u_a[j]*weight
                bb[n] += u_b[j]*weight
    value = series([acb(0)], degree)
    for n in range(2*length-1):
        product = series([acb(0)], degree)
        for j in range(max(0, n-length+1), min(n, length-1)+1):
            product += aa[j]*bb[n-j]
        value += product*moments[n]
    return value


def centered_angular_contraction(u_a, u_b, moments, degree, half_width, radius,
                                 v_majorant):
    """Enclose the retained Taylor coefficients without basis-amplified errors.

    The exact dyadic midpoint polynomials go through the monomial transform.
    Their coefficient uncertainties stay in the original orthonormal basis.
    The weighted nonnegative convolution bounds the *projected coefficients*,
    not just the untruncated product on the real axis. The caller separately
    adds the Cauchy tail of the actual full integrand and integrates this
    coefficient error over the panel. See ANGULAR_ERROR_STABILITY.md.
    """
    h, rho = F(half_width), F(radius)
    if not 0 < h < rho:
        raise ValueError("strictly nested positive radii are required")
    if not v_majorant.is_finite() or not v_majorant >= 0:
        raise ArithmeticError("finite nonnegative multiplier majorant required")

    def split(vector):
        centered, amplitude, error = [], arb(0), arb(0)
        for value in vector:
            coefficients = []
            for n in range(degree+1):
                coefficient = value[n]
                if not coefficient.is_finite():
                    raise ArithmeticError("nonfinite angular response coefficient")
                midpoint = acb(coefficient.real.mid(), coefficient.imag.mid())
                coefficients.append(midpoint)
                weight = rational_ball(h**n)
                amplitude += weight*(abs(midpoint.real)+abs(midpoint.imag))
                error += weight*rational_ball(norm_radius_l1(coefficient))
            centered.append(series(coefficients,degree))
        return centered, amplitude.upper(), error.upper()

    aa, a, ea = split(u_a)
    bb, b, eb = split(u_b)
    value = angular_contraction(aa,bb,moments,degree)
    weighted_v = (v_majorant/rational_ball(1-h/rho)).upper()
    coefficient_error = (weighted_v*(ea*b+a*eb+ea*eb)).upper()
    budget = {"schema":"PHYS71_CENTERED_ANGULAR_ERROR_V1",
              "midpoint_weighted_l1_a":dyadic_ball(a),
              "midpoint_weighted_l1_b":dyadic_ball(b),
              "coefficient_error_weighted_l1_a":dyadic_ball(ea),
              "coefficient_error_weighted_l1_b":dyadic_ball(eb),
              "multiplier_weighted_coefficient_bound":dyadic_ball(weighted_v),
              "projected_integrand_coefficient_error":dyadic_ball(coefficient_error),
              "basis_for_error_bound":"original_orthonormal_modes_with_L1_upper_bound",
              "midpoint_transform_roundoff":"retained_in_complex_ball_polynomial"}
    return value, coefficient_error, budget


def forward_primitive(s_coefficients, s_majorant, left_value, half_width, radius, degree):
    """Enclose P'=s from the left boundary on one zero-free disk.

    All coefficient errors are propagated by acb.  The separate Cauchy
    remainder is added to both the center and right endpoint.  A disk
    majorant controls P for later analytic products on the same disk.
    """
    h, rho = F(half_width), F(radius)
    if not 0 < h < rho or len(s_coefficients) != degree+1:
        raise ValueError("valid nested radii and all Taylor coefficients required")
    if not left_value.is_finite() or not s_majorant.is_finite() or not s_majorant >= 0:
        raise ArithmeticError("finite primitive input and nonnegative majorant required")
    remainder = cauchy_tail(s_majorant, rho, h, degree)
    center = inflate_complex(left_value + polynomial_integral(s_coefficients, -h, F(0)),
                             rational_ball(h)*remainder)
    right = inflate_complex(left_value + polynomial_integral(s_coefficients, -h, h),
                            rational_ball(2*h)*remainder)
    coefficients = (center,) + tuple(s_coefficients[n]/(n+1) for n in range(degree))
    majorant = (left_value.abs_upper() + rational_ball(rho+h)*s_majorant).upper()
    return coefficients, right, majorant, remainder


def build_d3_panel(inherited_panel, left_carry, request=None):
    """One new forward D3 panel; inherited index75 is the first at B=27."""
    req = (request or D3Request()).validate()
    n, bits = req.degree, req.precision_bits
    h, rho, big = map(F, (req.half_width, req.zero_free_radius, req.majorant_radius))
    modes = tuple(range(req.max_ell+1))
    expected = {(a,j) for a in (req.ell,req.ellprime) for j in modes}
    if set(left_carry) != expected:
        raise ValueError("all 74 directed source-response carries are required")
    if inherited_panel.right - inherited_panel.left != 2*h:
        raise ValueError("inherited panel geometry mismatch")
    started = time.monotonic()
    cap = ctx.cap
    with ctx.workprec(bits):
        ctx.cap = n+1
        try:
            c = inherited_panel.center
            disks = {j:coulomb_taylor(j,c,n,big,bits) for j in modes}
            lower = {j:disks[j].zero_free_lower(rho) for j in modes}
            failed = [j for j in modes if not lower[j] > 0]
            if failed:
                raise ArithmeticError(f"UNRESOLVED_ZERO_FREE_DISK: {failed}")
            ff = {j:series(disks[j].coefficients,n) for j in modes}
            fsmall = {j:local_coulomb_majorant(disks[j],rho) for j in modes}
            invsq = {j:(ff[j]*ff[j]).inv() for j in modes}
            qseries, qsmall = {}, {}
            for pair, row in inherited_panel.pairs.items():
                a,j = pair
                vv = series(angular_taylor_coefficients(a,j,c,n,bits,req.coefficient_bits),n)
                kk = ff[a]*ff[j]*vv
                qseries[pair] = series((restore_complex_ball(row["q_center"]),)
                                      +tuple(-kk[t]/(t+1) for t in range(n)),n)
                qsmall[pair] = restore_ball(row["q_small_disk_majorant"])
            uu, umajorant, right, records = {}, {}, {}, []
            for a,j in sorted(expected):
                pair = tuple(sorted((a,j)))
                ss = qseries[pair]*invsq[j]
                ms = (qsmall[pair]/lower[j]**2).upper()
                pc, pr, mp, remainder = forward_primitive(
                    tuple(ss[t] for t in range(n+1)), ms, left_carry[(a,j)], h,rho,n)
                uu[(a,j)] = ff[j]*series(pc,n)
                umajorant[(a,j)] = (fsmall[j]*mp).upper()
                right[(a,j)] = pr
                records.append({"external":a,"j":j,
                    "P_left":complex_ball_record(left_carry[(a,j)]),
                    "P_right":complex_ball_record(pr),
                    "P_center":complex_ball_record(pc[0]),
                    "S_majorant":dyadic_ball(ms),
                    "S_panel_remainder":dyadic_ball(remainder),
                    "U_disk_majorant":dyadic_ball(umajorant[(a,j)])})
            moments = monomial_moments(c,n,2*req.max_ell,req.coefficient_bits)
            vsmall = angular_complex_disk_bound(c,rho,bits)
            integral_series, coefficient_error, angular_error_budget = centered_angular_contraction(
                [uu[(req.ell,j)] for j in modes],
                [uu[(req.ellprime,j)] for j in modes],moments,n,h,rho,vsmall)
            mi = (vsmall*sum((umajorant[(req.ell,j)] for j in modes),arb(0))
                        *sum((umajorant[(req.ellprime,j)] for j in modes),arb(0))).upper()
            integral_remainder = cauchy_tail(mi,rho,h,n)
            increment = inflate_complex(polynomial_integral(
                tuple(integral_series[t] for t in range(n+1)),-h,h),
                rational_ball(2*h)*(integral_remainder+coefficient_error))
            if not increment.is_finite():
                raise ArithmeticError("nonfinite D3 panel enclosure")
            record = {"schema":"PHYS71_D3_PANEL_V1", "inherited_index":inherited_panel.index,
                "center":str(c),"left":str(inherited_panel.left),"right":str(inherited_panel.right),
                "forward_index":75-inherited_panel.index,"all_modes":list(modes),
                "D3_increment":complex_ball_record(increment),
                "D3_increment_error_l1":rational_record(norm_radius_l1(increment)),
                "integrand_disk_majorant":dyadic_ball(mi),
                "integrand_panel_remainder":dyadic_ball(integral_remainder),
                "angular_error_budget":angular_error_budget,
                "source_response_carries":records,
                "new_D1_or_D2_integrations":0,
                "regenerated_Coulomb_disks":len(modes),
                "regenerated_q_derivative_series":len(qseries),
                "angular_moment_series":len(moments),
                "elapsed_seconds":time.monotonic()-started,"HH_R10":"OFF"}
            return right, increment, record
        finally:
            ctx.cap = cap


def rational_record(value):
    value=F(value)
    return {"numerator":str(value.numerator),"denominator":str(value.denominator)}


def engine_identity():
    root=Path(__file__).parent
    files=("phys71_d3.py","phys71_inherit.py","phys71_angular_d3.py","phys69_angular_tail.py",
           "phys68_profiles.py","phys68_taylor.py","phys68_angular.py",
           "phys67_first_born.py","phys67_coulomb_certificate.py")
    return {"files_sha256":{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files},
            "python":platform.python_version(),"python_flint":flint.__version__,
            "flint":flint.__FLINT_VERSION__}
