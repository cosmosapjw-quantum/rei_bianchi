"""Exact analytic budget for the original HH exterior driven source.

This computes continuum bounds, not a certificate for sampled grid outputs.
The unchanged PHYS72 scalar authority is loaded only after its SHA256 matches.
See ../theory/ORIGINAL_SOURCE_AND_ERROR_BUDGET.md for the proof and conventions.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from math import isqrt
from pathlib import Path
import sys

PHYS72_SHA256 = "2036fc4b0d76a825d98e3ea3f2342c67c3029f4ed6fbe67686c1d70042762e7c"
PHYS72_PATH = (Path(__file__).resolve().parents[2] / "hh_phys72_20261020"
               / "implementation" / "bounds.py")


def _authority():
    raw = PHYS72_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PHYS72_SHA256:
        raise ValueError("PHYS72 scalar authority SHA256 mismatch")
    name = "_phys73_pinned_phys72_bounds"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, PHYS72_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load pinned PHYS72 scalar authority")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _q(value, name):
    if isinstance(value, bool) or not isinstance(value, (str, int, Q)):
        raise TypeError(f"{name} requires an exact rational string, int or Fraction")
    try:
        return Q(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be finite and rational") from exc


def _integer(value, name, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum}, {maximum}]")
    return value


def positive_taylor(x: Q, terms: int = 128) -> Q:
    """Exact positive partial sum S_terms(x) <= exp(x), for x >= 0."""
    x = _q(x, "Taylor argument")
    if x < 0:
        raise ValueError("Taylor argument must be nonnegative")
    _integer(terms, "Taylor terms", 1, 512)
    total = term = Q(1)
    for n in range(1, terms + 1):
        term *= x / n
        total += term
    return total


def exp_negative_upper(x: Q) -> Q:
    """Rigorous rational upper on exp(-x), without floating exponential.

    Split x=m*y with 0<=y<=32.  [1/S_128(y)]**m >= exp(-x).
    This is an enclosure regardless of how small the omitted Taylor tail is.
    """
    x = _q(x, "exponential argument")
    if x < 0:
        raise ValueError("exponential argument must be nonnegative")
    if x == 0:
        return Q(1)
    m = max(1, (x.numerator + 32 * x.denominator - 1) // (32 * x.denominator))
    return positive_taylor(x / m) ** (-m)


def sqrt_upper(x: Q) -> Q:
    """An outward rational square root proved by an integer-square check.

    Decimal selects a useful scale only.  The returned endpoint is certified
    solely by exact integer comparison, including for very small tail bounds.
    """
    x = _q(x, "square root argument")
    if x < 0:
        raise ValueError("square root argument must be nonnegative")
    if not x:
        return Q(0)
    with localcontext() as ctx:
        ctx.prec = 24
        exponent = (Decimal(x.numerator) / Decimal(x.denominator)).adjusted()
    digits = max(96, 96 - exponent // 2)
    scale = 10**digits
    target = x.numerator * scale * scale
    root = isqrt(target // x.denominator)
    if root * root * x.denominator < target:
        root += 1
    result = Q(root, scale)
    if result * result < x:
        raise ArithmeticError("outward square-root invariant failed")
    return result


def moment4(t: Q) -> Q:
    """I4(t)=integral_0^infinity (t+s)^4 exp(-6s) ds, exactly."""
    t = _q(t, "moment radius")
    if t < 0:
        raise ValueError("moment radius must be nonnegative")
    return t**4 / 6 + t**3 / 9 + t**2 / 18 + t / 54 + Q(1, 324)


def source_budget(ell: int = 64, outer: Q | int | str = 44, terms: int = 1) -> dict:
    """Proved continuum budget for lambda=1, zero Dirichlet particular xi.

    The omitted-source estimate applies to exact P_ell 1_[B,outer] (V r phi).
    The Born estimate is for N exact continuum K applications; projected
    multiplication errors at subsequent iterations require separate bounds.
    Actual finite angular/radial quadratures and native roundoff are not inputs
    to this function and are not certified by its result.
    """
    p72 = _authority()
    _integer(ell, "ell", 0, 4096)
    _integer(terms, "terms", 1, 256)
    outer = _q(outer, "outer")
    B, delta = p72.B, p72.DELTA
    if not B <= outer <= 256:
        raise ValueError("outer must lie in the implemented exact range [27, 256]")
    c, q, m = p72.C_RESOLVENT_UPPER, p72.Q_UPPER, p72.V_WEIGHTED_UPPER
    if not (q == c * m and 0 <= q < 1):
        raise ArithmeticError("inherited PHYS72 contraction identity failed")
    rho, delta8 = Q(8), Q(3, 10**20)
    ellipse_at_B = B**2 + Q(7, 10)**2 - 2 * B * Q(7, 10) * Q(65, 16)
    ellipse_margin = ellipse_at_B - 23**2
    screen8_witness = delta8 - Q(48, 23) / positive_taylor(Q(46))
    if not (ellipse_margin > 0 and screen8_witness > 0):
        raise ArithmeticError("Bernstein ellipse screen envelope witness failed")

    # f=V*chi, chi=r*exp(-r)/sqrt(pi); norm_X+ includes an additional r.
    source_sq = 4 * delta**2 * exp_negative_upper(2 * B) * moment4(B)
    source = sqrt_upper(source_sq)
    seed_sq = delta * exp_negative_upper(2 * B) * (B**2 + B / 2 + Q(1, 8))
    seed = sqrt_upper(seed_sq)
    radial_sq = 4 * delta**2 * exp_negative_upper(6 * outer - 4 * B) * moment4(outer)
    radial = sqrt_upper(radial_sq)
    angular_sq = (16 * delta8**2 / (rho - 1)**2 * rho**(-2 * ell)
                  * exp_negative_upper(2 * B) * moment4(B))
    angular = sqrt_upper(angular_sq)
    inverse_gain = c / (1 - q)
    # Two valid first-application majorants.  Taking their minimum is valid.
    first_green = min(c * source, c * sqrt_upper(m) * seed)
    born_tail = first_green * q**terms / (1 - q)
    omitted_source_output = inverse_gain * (radial + angular)
    analytic_total = born_tail + omitted_source_output
    record = p72.rational_record
    return {
        "schema": "WU088_HH_PHYS73_ORIGINAL_EXTERIOR_SOURCE_BUDGET_V1",
        "status": "PROVED_CONTINUUM_ANALYTIC_COMPONENTS_NOT_GRID_CERTIFICATE",
        "finite_grid_certified": False,
        "physical_equation": "A1 u=V chi; u=r xi; chi=r exp(-r)/sqrt(pi)",
        "boundary": "u(27)=0, actual outgoing Coulomb radiation at infinity",
        "source_variables": {"eta": "F y", "xi": "F y-phi at lambda=1",
                             "F": "exp(exp(-d))", "phi": "exp(-r)/sqrt(pi)",
                             "eta_C": "-10/7"},
        "source_space": "X_plus: ||r f||_L2(dr dOmega)",
        "solution_space": "X_minus: ||u/r||_L2(dr dOmega)",
        "ell": ell, "outer": str(outer), "terms": terms,
        "angular_projection": "exact orthogonal spherical projection, m=0 source",
        "terms_meaning": "N exact continuum source Born terms K^n R0 f, n=0..N-1",
        "input_identity": {"phys72_bounds_sha256": PHYS72_SHA256,
                           "frozen_npz_sha256": p72.FROZEN_NPZ_SHA256,
                           "frozen_npz_used_as_exterior_source": False},
        "inherited": {"C_R_upper": record(c), "M_upper": record(m), "q_upper": record(q)},
        "exact_witnesses": {
            "ellipse_rho": record(rho), "ellipse_real_d_squared_at_B": record(ellipse_at_B),
            "ellipse_margin_above_23_squared": record(ellipse_margin),
            "ellipse_screen_envelope_delta8": record(delta8),
            "delta8_minus_48_over_23_S128_46": record(screen8_witness)},
        "bounds": {
            "source_Xplus_squared_upper": record(source_sq),
            "source_Xplus_upper": record(source),
            "b0_L2_squared_upper": record(seed_sq),
            "b0_L2_upper": record(seed),
            "first_green_Xminus_upper": record(first_green),
            "solution_Xminus_upper": record(first_green / (1 - q)),
            "screened_resolvent_Xplus_to_Xminus_upper": record(inverse_gain),
            "radial_omitted_source_Xplus_squared_upper": record(radial_sq),
            "radial_omitted_source_Xplus_upper": record(radial),
            "angular_omitted_source_Xplus_squared_upper": record(angular_sq),
            "angular_omitted_source_Xplus_upper": record(angular),
            "source_omission_solution_Xminus_upper": record(omitted_source_output),
            "born_tail_after_N_Xminus_upper": record(born_tail),
            "analytic_components_Xminus_upper": record(analytic_total)},
        "remaining_numerical_obligations": [
            "Coulomb d_i,t_i input enclosures or reconstructed residual",
            "finite angular quadrature coefficient error in Xplus",
            "radial quadrature/interpolation error and reconstruction norm",
            "native arithmetic error including underflow/subnormal effects",
            "extra projected-operator defect for N>1 finite-angular iterations"],
        "original_matched_problem_obligation": (
            "The frozen r<=20 NPZ does not determine physical boundary trace at B=27; "
            "nonzero trace, interior/origin matching and observables remain separate."),
        "HH_R10": "OFF",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ell", type=int, default=64)
    parser.add_argument("--outer", default="44")
    parser.add_argument("--terms", type=int, default=1)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = source_budget(args.ell, args.outer, args.terms)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    print(json.dumps({"out": str(args.out), "status": result["status"],
                      "analytic_components_Xminus_upper":
                      result["bounds"]["analytic_components_Xminus_upper"]["upper_decimal"]}))


if __name__ == "__main__":
    main()
