"""Exact all-angular second-Born tail for the original attractive Coulomb screen.

For j >= 20, |H_j(t)/H_j(r)| <= (800/189)(j+1), B <= r <= t.
Combine this modewise bound with the inherited E_10 angular analyticity.
This module bounds the second coefficient of the DtN Taylor series in the
original screen strength.  It does not replace the nonlinear Born remainder.
All budget decisions and certificate assembly use exact rational arithmetic.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

from .phys65_exterior_bounds import SOURCE_SHA, exp_upper

B, K, SHIFT = F(27), F(7, 10), F(7, 10)
SCREEN_ELLIPSE_M = F(1, 4 * 10**19)  # S, not V=2S; PHYS67 E_10.
MODE_SLOPE = F(800, 189)
PHYS68_CERTIFICATE_SHA = "ddaae206009a276def281af5526851ceb717baf2e0de5f8472552a9db340de9a"
PHYS65_PROOF_SHA = "00a1f86a8f8d132d53f2e8ea274a26948fd80420ac1c2e943d7036910ef41959"
PHYS66_PROOF_SHA = "c0f67c47c36f445494af3df52a9e09e27a853962b8f500ebe1572603febb68ca"
# PR115 exact outward result is 7.54113862158...e-66; this decimal is an
# upward rational endpoint.  It covers every finite projection L <= 64 at T65.
RADIAL_BETA2_L64_T65_UPPER = F("7.541139e-66")


def _integer(value, name, low=0, high=None):
    if type(value) is not int or value < low or (high is not None and value > high):
        raise ValueError(f"{name}: exact integer in the stated domain required")
    return value


def _exact(value, name="value"):
    if isinstance(value, bool) or not isinstance(value, (F, int, str)):
        raise ValueError(f"{name}: Fraction, integer or exact string required")
    return F(value)


def rational_record(value):
    value = _exact(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _record_integer(value, name):
    """Parse exact JSON integer fields without float truncation or bool coercion."""
    if type(value) not in (int, str):
        raise ValueError(f"{name}: integer or integer string required")
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name}: integer or integer string required") from exc


def read_rational(value):
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise ValueError("exact numerator/denominator record required")
    n = _record_integer(value["numerator"], "numerator")
    d = _record_integer(value["denominator"], "denominator")
    if d == 0:
        raise ValueError("nonzero denominator required")
    return F(n, d)


def upward_decimal(value, digits=24):
    """A positive decimal ceiling; never use it for arithmetic decisions."""
    value = _exact(value)
    _integer(digits, "digits", 1, 200)
    if value < 0:
        raise ValueError("positive bound required")
    with localcontext() as ctx:
        ctx.prec = digits
        ctx.rounding = ROUND_CEILING
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def mode_ratio_bound(ell):
    _integer(ell, "ell", 20)
    return MODE_SLOPE * (ell + 1)


def mode_witness(ell):
    """Rational ingredients of the all-j analytic proof, not radial samples."""
    _integer(ell, "ell", 20)
    a, outer = F(ell - 1) / K, F(ell + 1) / K
    lam = ell * (ell + 1)
    nu_a = K*K + 2/a - lam/a**2
    nu_outer = K*K + 2/outer - lam/outer**2
    exponent = F(2) + F(14*ell + 182, 49*(ell - 1)**2)
    exp_ceiling = exp_upper(F(41, 20))
    assert a >= B and nu_a < 0 < nu_outer <= K*K
    assert K*K + F(1, lam) <= F(1, 2)
    assert exponent <= F(41, 20) and exp_ceiling < 8
    return {
        "ell": ell, "anchor": a, "allowed_start": outer,
        "nu_anchor": nu_a, "nu_allowed": nu_outer,
        "nu_max_upper": F(1, 2), "lognorm_exponent": exponent,
        "exponent_upper": F(41, 20), "exp_rational_upper": exp_ceiling,
        "ratio_absolute_bound": mode_ratio_bound(ell),
        "domain": "all real B <= r <= t < infinity",
    }


def quadratic_geometric_tail(cutoff, ratio=F(1, 100)):
    """Exact sum_{j=cutoff+1}^infinity (j+1)^2 ratio^j."""
    _integer(cutoff, "cutoff")
    x = _exact(ratio, "ratio")
    if not 0 < x < 1:
        raise ValueError("0 < ratio < 1 required")
    u = cutoff + 2
    return x**(cutoff+1) * (
        F(u*u)/(1-x) + 2*u*x/(1-x)**2 + x*(1+x)/(1-x)**3)


def angular_offdiagonal_multiplier(ell, high_ell, m=0):
    """|V_{ell,j}^m(r)| <= returned value * exp[-2(r-27)], j>ell.

    A degree j-ell-1 comparison polynomial has exactly zero matrix element.
    The V=2S factor is included once. Negative m has the same bound.
    """
    _integer(ell, "ell")
    _integer(high_ell, "high_ell", ell+1)
    if type(m) is not int or abs(m) > ell:
        raise ValueError("allowed fixed signed m required")
    degree = high_ell - ell - 1
    return 4 * SCREEN_ELLIPSE_M / 9 * F(1, 10**degree)


def external_ratio_product(ell, ellprime):
    """Reused finite-block bound on C_ell*C_ellprime, without enumeration."""
    _integer(ell, "ell", 0, 64)
    _integer(ellprime, "ellprime", 0, 64)
    return F(5929 if max(ell, ellprime) <= 28 else 32400)


def excluded_second_born_bound(cutoff, ell=21, ellprime=20, m=0):
    """Absolute omitted-j bound for the full radial second DtN coefficient."""
    gamma = external_ratio_product(ell, ellprime)
    _integer(cutoff, "cutoff", max(19, ell, ellprime))
    if type(m) is not int or abs(m) > min(ell, ellprime):
        raise ValueError("allowed common signed m required")
    return (gamma * MODE_SLOPE**2 * SCREEN_ELLIPSE_M**2 / 81
            * 10**(ell+ellprime+2) * quadratic_geometric_tail(cutoff))


def minimum_cutoff_for_angular_goal(goal, ell=21, ellprime=20, m=0, maximum=64):
    """First cutoff in the implemented finite-L range meeting an exact goal."""
    goal = _exact(goal, "goal")
    if goal <= 0:
        raise ValueError("positive angular goal required")
    external_ratio_product(ell, ellprime)
    _integer(maximum, "maximum", max(19, ell, ellprime), 64)
    for cutoff in range(max(19, ell, ellprime), maximum+1):
        if excluded_second_born_bound(cutoff, ell, ellprime, m) <= goal:
            return cutoff
    return None


def _hash_guard(path, expected):
    path = Path(path)
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != expected:
        raise ValueError(f"inherited identity mismatch: {path.name}")
    return data


def inherit(repo):
    """Read exact prior proofs/source/result; invoke no old integrator."""
    repo = Path(repo)
    pins = {
        "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz": SOURCE_SHA,
        "research/hh_phys65_20261018/r5/PROOF.md": PHYS65_PROOF_SHA,
        "research/hh_phys66_20261018/r5/PROOF.md": PHYS66_PROOF_SHA,
        "research/hh_phys68_20261019/profiles/run_l28_t65_completed/CERTIFICATE.json": PHYS68_CERTIFICATE_SHA,
    }
    for path, sha in pins.items():
        _hash_guard(repo/path, sha)
    saved = json.loads((repo/next(p for p in pins if p.endswith("CERTIFICATE.json"))).read_text())
    req = saved["request"]
    if (req["max_ell"], req["ell"], req["ellprime"], req["outer"], saved["m"]) != (28, 21, 20, "65", 0):
        raise ValueError("inherited finite-L physical request changed")
    gamma = saved["analytic_radial_cutoff"]["gamma"]
    if F(int(gamma["numerator_hex"], 16), int(gamma["denominator_hex"], 16)) != 5929:
        raise ValueError("inherited external ratio bound changed")
    return saved, pins


def _dyadic(value):
    if not isinstance(value, dict) or set(value) != {"mantissa", "exponent2"}:
        raise ValueError("dyadic record required")
    n = _record_integer(value["mantissa"], "mantissa")
    e = value["exponent2"]
    if type(e) is not int:
        raise ValueError("integer dyadic exponent required")
    return F(n) * F(2)**e


def saved_complex_midpoint(value):
    return tuple(_dyadic(value[k]["midpoint"]) for k in ("real", "imag"))


def coarse_all_angular_from_saved(repo):
    """Reuse the completed L28 full-radial enclosure and add the j>28 tail."""
    saved, pins = inherit(repo)
    mid = saved_complex_midpoint(saved["D2_B_cutoff"])
    old = read_rational(saved["D2_full_radial_absolute_error_about_cutoff_midpoint"])
    angular = excluded_second_born_bound(28)
    return {
        "schema": "PHYS69_ALL_ANGULAR_D2_COARSE_FROM_SAVED_V1",
        "scope": "all angular j, m0, external(21,20), all r>=27, order lambda^2 only",
        "midpoint": {k: rational_record(v) for k, v in zip(("real", "imag"), mid)},
        "inherited_full_radial_error": rational_record(old),
        "excluded_angular_error": rational_record(angular),
        "total_error": rational_record(old+angular),
        "total_error_upper_decimal": upward_decimal(old+angular),
        "real_part_strictly_positive": mid[0] > old+angular,
        "imag_part_strictly_positive": mid[1] > old+angular,
        "dependencies": pins, "new_radial_integrations": 0,
        "HH_R10": "OFF", "nonlinear_response_error": None,
    }


def bound_certificate(repo):
    _, pins = inherit(repo)
    cutoffs = (28, 29, 32, 34, 35, 36, 40, 64)
    return {
        "schema": "PHYS69_EXCLUDED_SECOND_BORN_BOUND_V1",
        "status": "DERIVED_EXACT_RATIONAL_APPLICATION",
        "physics": {"B": "27", "k": "7/10", "E_Hartree": "49/200",
                    "eta_C": "-10/7", "V": "2(1+1/d)exp(-2d)", "shift": "7/10"},
        "ell": 21, "ellprime": 20, "m_scope": "all allowed fixed signed m",
        "mode_slope": rational_record(MODE_SLOPE),
        "external_ratio_product": rational_record(external_ratio_product(21, 20)),
        "angular_S_ellipse_M": rational_record(SCREEN_ELLIPSE_M),
        "cutoffs": [{"L": L, "bound": rational_record(excluded_second_born_bound(L)),
                     "upper_decimal": upward_decimal(excluded_second_born_bound(L))}
                    for L in cutoffs],
        "minimum_L_for_angular_1e-62": minimum_cutoff_for_angular_goal("1e-62"),
        "minimum_L_for_angular_1e-63": minimum_cutoff_for_angular_goal("1e-63"),
        "mode_witnesses": [{k: rational_record(v) if isinstance(v, F) else v
                            for k, v in mode_witness(j).items()}
                           for j in (20, 29, 36, 65, 128, 1024)],
        "proof_of_all_j": "theory/PROOF.md; finite witnesses are implementation checks only",
        "dependencies": pins,
        "old_scientific_executions_repeated": 0,
        "full_nonlinear_response_bound": None, "original_xi_applied": False,
        "PHYS63_qualitative_existence": "ESTABLISHED_REUSED", "HH_R10": "OFF",
    }
