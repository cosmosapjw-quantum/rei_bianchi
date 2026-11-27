"""PHYS54 conditional weighted DtN coercivity reduction and diagnostics.

This module deliberately separates a proved Hilbert-space reduction from the
unproved exterior screened perturbation estimate.  It does not solve the
physical driven problem or claim an infinite-angular outgoing theorem.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

RADIUS = 27.0
KAPPA = 0.7
ELL_FIRST = 21
ELL_LAST = 256


def screened_multiplier_upper(radius: float = RADIUS, center: float = KAPPA) -> float:
    """Uniform upper bound for 2(1+1/s)exp(-2s) when |x| >= radius."""
    if not (radius > center > 0.0):
        raise ValueError("require radius > center > 0")
    s = radius - center
    return 2.0 * (1.0 + 1.0 / s) * math.exp(-2.0 * s)


def coercivity_margin(c_coulomb: float, epsilon_outgoing: float) -> float:
    """Exact reduction margin c-epsilon in the W^{1/2} trace form."""
    if c_coulomb < 0.0 or epsilon_outgoing < 0.0:
        raise ValueError("form constants must be nonnegative")
    return c_coulomb - epsilon_outgoing


def conditional_statement(c_coulomb: float, epsilon_outgoing: float) -> dict:
    margin = coercivity_margin(c_coulomb, epsilon_outgoing)
    return {
        "trace_space": "X=H^(1/2)(S^2) restricted to ell>=21; W Y_lm=(ell+1)Y_lm",
        "central_hypothesis": "-Re<g,Z_C g> >= c_C ||W^(1/2)g||^2",
        "screened_hypothesis": "|Re<g,(Z_S-Z_C)g>| <= epsilon ||W^(1/2)g||^2",
        "deduction": "-Re<g,Z_S g> >= (c_C-epsilon)||W^(1/2)g||^2",
        "c_coulomb": c_coulomb,
        "epsilon_outgoing": epsilon_outgoing,
        "margin": margin,
        "state": "CONDITIONAL_COERCIVE" if margin > 0.0 else "NO_COERCIVITY_FROM_THESE_CONSTANTS",
    }


def central_cf_real(ell: int, radius: float = RADIUS, depth: int = 1152) -> float:
    """The Rust finite-CF real part, reproduced dependency-free for diagnostics."""
    if ell < 0 or depth < 1:
        raise ValueError("ell and depth must be positive")
    eta = -10.0 / 7.0
    rho = 0.7 * radius

    def rust_div(a: complex, b: complex) -> complex:
        # Same scaled real-arithmetic division as native/phys53_coulomb_cf.rs.
        scale = max(abs(b.real), abs(b.imag))
        ar, ai, br, bi = a.real / scale, a.imag / scale, b.real / scale, b.imag / scale
        den = br * br + bi * bi
        return complex((ar * br + ai * bi) / den, (ai * br - ar * bi) / den)

    a = complex(ell + 1.0, eta)
    b = complex(-float(ell), eta)
    tail = 0j
    for n in range(depth, 0, -1):
        x = float(n - 1)
        tail = rust_div((a + x) * (b + x), complex(2.0 * (rho - eta), 2.0 * n) + tail)
    return (complex(0.0, 1.0 - eta / rho) + 1j * tail / rho).real * 0.7


def central_cf_diagnostic(first: int = ELL_FIRST, last: int = ELL_LAST) -> dict:
    # Values are a diagnostic, not an all-ell proof or a finite-CF certificate.
    # Avoid importing the mpmath oracle implementation: this NCP Python runtime
    # intentionally has no mpmath package installed.
    ratios = []
    for ell in range(first, last + 1):
        ratios.append((-central_cf_real(ell) / (ell + 1.0), ell))
    minimum, at = min(ratios)
    maximum, max_at = max(ratios)
    return {
        "kind": "NONCERTIFYING_CENTRAL_CF_DIAGNOSTIC",
        "radius_Bohr": RADIUS,
        "ell_range": [first, last],
        "depth": 1152,
        "min_minus_re_z_over_ell_plus_1": minimum,
        "min_at_ell": at,
        "max_minus_re_z_over_ell_plus_1": maximum,
        "max_at_ell": max_at,
        "not_a_proof": [
            "all_ell_coulomb_real_part_bound",
            "screened_outgoing_perturbation_bound",
            "physical_driven_solution",
        ],
    }


def run(output: Path) -> dict:
    diagnostic = central_cf_diagnostic()
    screen = screened_multiplier_upper()
    # A multiplication bound is not a DtN perturbation bound.  Retain it as a
    # separate exterior input-scale diagnostic, never substitute it for epsilon.
    statement = conditional_statement(diagnostic["min_minus_re_z_over_ell_plus_1"], 0.0)
    out = {
        "schema": "WU088_HH_PHYS54_WEIGHTED_DTN_REDUCTION_V1",
        "physics_scope": "NONCENTRAL_SCREENED_OUTGOING_DTN_CONDITIONAL_REDUCTION",
        "fixed_radius_Bohr": RADIUS,
        "screened_multiplier_upper_at_and_beyond_radius": screen,
        "central_diagnostic": diagnostic,
        "conditional_reduction_with_epsilon_zero_only_as_algebraic_baseline": statement,
        "open_prerequisites": [
            {
                "name": "central all-ell real-part and weighted DtN theorem",
                "required_form": "Z_C:X->X* exists and -Re<g,Z_Cg> >= c_C||W^(1/2)g||^2 for every high trace",
                "status": "OPEN_NOT_INFERRED_FROM_FINITE_CF_SAMPLES",
            },
            {
                "name": "high-block definition for noncentral exterior",
                "required_form": "define Z_S as the Q-to-Q Schur/compressed outgoing DtN after treating P-Q coupling",
                "status": "OPEN_Q_IS_NOT_INVARIANT_UNDER_NONCENTRAL_MULTIPLICATION",
            },
            {
                "name": "uniform weighted exterior screened DtN perturbation",
                "required_form": "||W^(-1/2)(Z_S-Z_C)W^(-1/2)||_Re <= epsilon < c_C",
                "status": "OPEN_NOT_INFERRED_FROM_MULTIPLIER_BOUND_OR_FINITE_CF_SAMPLES",
            },
        ],
        "HH_R10": "OFF",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(run(args.output), sort_keys=True))
