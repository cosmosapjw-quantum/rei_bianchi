"""Exact-Gauss angular truncation for the original finite-L screen matrix.

For every r>=27 and all signed m, Q>=L+1 exact Gauss-Legendre nodes
give ||V_L - V_L,Q||_2 <= epsilon_LQ exp[-2(r-27)], with V=2S.
The coefficient is exact Fraction arithmetic.  The target is the ideal
Gauss rule, so floating nodes/weights/basis/screen and matrix arithmetic
remain separate errors.  See research/hh_phys67_20261019/angular/PROOF.md.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction as F
from pathlib import Path

from .phys58_screen_multipoles import (
    B, R, RHO_ELLIPSE, M_MAJOR, FROZEN_SHA,
    exact_r5_gates, legendre_tail_upper, original_source_sha_guard,
)
from .phys66_order_tail import json_safe

SCHEMA = "PHYS67_EXACT_GAUSS_ANGULAR_CERTIFICATE_V1"
SCREEN_SCALE = F(3, 10**23)
PUBLISHED_PREMISE_COMMIT = "445d82db9c42b4f2f81e4ac1b107dec3b69b3c24"


def _integer(value: int, name: str, lower: int, upper: int) -> int:
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{name} must be an integer in [{lower},{upper}]")
    return value


def polynomial_budget(max_ell: int, nodes: int) -> int:
    """Largest degree N for which 2L+N <= 2Q-1, with exact Gram=I.

    This proof applies to all Q>=L+1.  AngularScreen currently accepts
    Q in 64..512; small Q are useful independently verifiable examples.
    """
    _integer(max_ell, "max_ell", 0, 64)
    _integer(nodes, "nodes", 1, 512)
    if nodes <= max_ell:
        raise ValueError("exact-Gram certificate requires Q >= L+1")
    return 2*nodes-1-2*max_ell


def basis_product_degree(ell: int, ell_prime: int, m: int) -> int:
    """Degree of b_ell^m b_ell_prime^m, including odd and negative m.

    Each individual associated Legendre function can contain a square
    root; their equal-|m| product is a polynomial of degree ell+ell_prime.
    """
    _integer(ell, "ell", 0, 64)
    _integer(ell_prime, "ell_prime", 0, 64)
    _integer(m, "m", -64, 64)
    if abs(m) > min(ell, ell_prime):
        raise ValueError("|m| must not exceed either angular degree")
    return ell+ell_prime


def weighted_ellipse_gates() -> dict:
    """Exact witnesses for |S(r,z)| <= M exp[-2(r-27)] on E_10.

    Re(d^2) >= r^2-707r/100+49/100.  Subtracting (r-4)^2
    gives (93r-1551)/100 >= 48/5 > 0 on the entire exterior.
    The principal root then obeys Re(d)>r-4=23+(r-27).
    """
    if (B, R, RHO_ELLIPSE, M_MAJOR) != (
        F(27), F(7, 10), F(10), F(1, 4*10**19)
    ):
        raise ValueError("inherited physical/ellipse constants changed")
    reused = exact_r5_gates()
    slope = F(93, 100)
    intercept = -F(1551, 100)
    margin = slope*B+intercept
    if not margin > 0:
        raise ArithmeticError("positive exterior ellipse margin required")
    return {
        "rho": RHO_ELLIPSE,
        "S_weighted_ellipse_majorant": M_MAJOR,
        "quadratic_gap_slope": slope,
        "quadratic_gap_intercept": intercept,
        "quadratic_gap_at_B": margin,
        "root_real_part_lower_expression": "r-4 = 23+(r-27)",
        "radial_weight_expression": "exp[-2(r-27)]",
        "inherited_positive_Taylor_gate": reused,
    }


def screen_polynomial_tail(degree: int, family: str = "chebyshev") -> F:
    """Weighted L-infinity error coefficient for S, not yet V=2S.

    Chebyshev: 2 M rho^(-N)/(rho-1), from the Cauchy/Laurent
    coefficient bound.  Legendre: reuse PHYS58's coefficient-tail sum.
    The weighted extension uses the same homogeneous majorant proof.
    """
    _integer(degree, "degree", 0, 1023)
    if family == "chebyshev":
        return 2*M_MAJOR / (RHO_ELLIPSE-1) / RHO_ELLIPSE**degree
    if family == "legendre":
        return legendre_tail_upper(degree)
    raise ValueError("polynomial family must be chebyshev or legendre")


def exact_gauss_error_bound(max_ell: int = 64, nodes: int = 128,
                           degree: int | None = None,
                           family: str = "chebyshev") -> F:
    """Weighted operator bound for exact V_L versus exact Q-node matrix.

    Positivity and polynomial exactness make the sampled basis an
    isometry.  Two residual multiplication norms contribute; V=2S
    supplies the other factor two.  There is no channel-count factor.
    """
    budget = polynomial_budget(max_ell, nodes)
    if degree is None:
        degree = budget
    _integer(degree, "degree", 0, budget)
    weighted_ellipse_gates()
    return 4*screen_polynomial_tail(degree, family)


def decimal_upper(value: F, significant_digits: int = 24) -> str:
    """An outward decimal display, retaining arbitrarily tiny rationals."""
    if not isinstance(value, F) or value < 0:
        raise ValueError("nonnegative Fraction required")
    _integer(significant_digits, "significant_digits", 2, 100)
    with localcontext() as ctx:
        ctx.prec = significant_digits
        ctx.rounding = ROUND_CEILING
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def make_angular_certificate(source: str | Path, max_ell: int = 64,
                             nodes: int = 128,
                             degree: int | None = None) -> dict:
    """Source-bound certificate for ideal angular quadrature only."""
    source_sha = original_source_sha_guard(source)
    budget = polynomial_budget(max_ell, nodes)
    if degree is None:
        degree = budget
    cheb = exact_gauss_error_bound(max_ell, nodes, degree, "chebyshev")
    leg = exact_gauss_error_bound(max_ell, nodes, degree, "legendre")
    return {
        "schema": SCHEMA,
        "source_sha256": source_sha,
        "published_premise_commit": PUBLISHED_PREMISE_COMMIT,
        "max_ell": max_ell,
        "nodes": nodes,
        "polynomial_degree": degree,
        "maximum_polynomial_degree": budget,
        "basis_product_degree_maximum": 2*max_ell,
        "Gauss_exactness_degree": 2*nodes-1,
        "all_signed_m": True,
        "full_projection_dimension": (max_ell+1)**2,
        "channel_dimension_factor": 1,
        "radial_domain": "r/a0 in [27,infinity)",
        "radial_weight": "exp[-2(r/a0-27)]",
        "units": "radial-equation multiplication coefficient in a0^-2",
        "quantity": "V=2(1+1/d)exp(-2d), d=|r n-(7/10)zhat| in atomic coordinates",
        "weighted_ellipse": weighted_ellipse_gates(),
        "chebyshev_operator_error_coefficient": cheb,
        "legendre_operator_error_coefficient": leg,
        "chebyshev_operator_error_decimal_upper": decimal_upper(cheb),
        "legendre_operator_error_decimal_upper": decimal_upper(leg),
        "scaled_AngularScreen_error_coefficient": cheb/SCREEN_SCALE,
        "scaled_AngularScreen_error_decimal_upper": decimal_upper(cheb/SCREEN_SCALE),
        "exact_gauss_quadrature_truncation_certified": True,
        "ideal_nodes_weights_and_point_evaluation": True,
        "floating_nodes_weights_basis_screen_roundoff_bound": None,
        "matrix_arithmetic_roundoff_bound": None,
        "radial_integration_error_bound": None,
        "coulomb_evaluation_error_bound": None,
        "excluded_angular_response_bound": None,
        "total_numerical_error_bound": None,
        "total_numerical_error_certified": False,
        "HH_R10": "OFF",
    }


__all__ = [
    "basis_product_degree", "polynomial_budget", "weighted_ellipse_gates",
    "screen_polynomial_tail", "exact_gauss_error_bound", "decimal_upper",
    "make_angular_certificate", "json_safe", "FROZEN_SHA",
]
