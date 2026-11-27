"""Exact scalar audit of PHYS72's additional angular multiplier bounds.

The accompanying analytic addendum proves the continuum inequalities.
This fixed-input program evaluates their rational constants only. It does
not repeat any physical integration or the prior screen-envelope audit.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from bounds import (  # noqa: E402
    B, SHIFT, DELTA, C_RESOLVENT_UPPER, V_WEIGHTED_UPPER, Q_UPPER,
    rational_record,
)


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BOUNDS_SHA256 = "2036fc4b0d76a825d98e3ea3f2342c67c3029f4ed6fbe67686c1d70042762e7c"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report() -> dict:
    bounds_sha = digest(Path(__file__).with_name("bounds.py"))
    if bounds_sha != EXPECTED_BOUNDS_SHA256:
        raise ValueError("BLOCKED_BOUNDS_IDENTITY_MISMATCH")
    d0 = B - SHIFT
    angular_log_gradient = SHIFT * (2 + 1 / (d0 * (d0 + 1)))
    shear_entry = Fraction(3, 2)
    log_gradient_margin = shear_entry - angular_log_gradient
    shear_norm = Fraction(2)
    # For T=[[1,0],[3/2,1]], 4 I - T^T T has nonnegative diagonal
    # and zero determinant. Its null vector (2,1) proves norm(T)=2.
    shear_psd_11 = shear_norm**2 - (1 + shear_entry**2)
    shear_psd_22 = shear_norm**2 - 1
    shear_psd_det = shear_psd_11 * shear_psd_22 - shear_entry**2
    c_tail_slope = Fraction(800, 189)
    c_lower, c_upper = Fraction(2), Fraction(77)
    finite_lower_margin = c_upper**2 - c_lower**2 * (1 + 28 * 29)
    tail_lower_margin = c_tail_slope**2 - c_lower**2
    tail_upper_margin = c_upper**2 - 2 * c_tail_slope**2
    h1_factor = shear_norm
    hc_factor = c_upper * h1_factor / c_lower
    h1_multiplier = h1_factor * V_WEIGHTED_UPPER
    hc_multiplier = hc_factor * V_WEIGHTED_UPPER
    q_h1, q_hc = C_RESOLVENT_UPPER*h1_multiplier, C_RESOLVENT_UPPER*hc_multiplier
    checks = {
        "positive_d0": d0 > 0,
        "radial_envelope_weight_decreases": B > 1,
        "angular_log_gradient_strictly_below_3_over_2": log_gradient_margin > 0,
        "shear_psd_first_diagonal_nonnegative": shear_psd_11 >= 0,
        "shear_psd_second_diagonal_nonnegative": shear_psd_22 >= 0,
        "shear_psd_determinant_zero": shear_psd_det == 0,
        "finite_channel_comparison": finite_lower_margin > 0,
        "all_high_channel_lower_coefficient": tail_lower_margin > 0,
        "all_high_channel_upper_coefficient": tail_upper_margin > 0,
        "q_H1_equals_2q": q_h1 == 2*Q_UPPER,
        "q_HC_equals_77q": q_hc == 77*Q_UPPER,
        "lambda1_H1_sufficient_condition": q_h1 < 1,
        "lambda1_HC_sufficient_condition": q_hc < 1,
    }
    if not all(checks.values()):
        raise ArithmeticError("A fixed angular-bound rational witness failed")
    values = {
        "B": B, "shift_a": SHIFT, "d0": d0, "delta": DELTA,
        "angular_log_gradient_upper": angular_log_gradient,
        "angular_log_gradient_margin_to_3_over_2": log_gradient_margin,
        "shear_norm_upper": shear_norm,
        "shear_psd_11": shear_psd_11, "shear_psd_22": shear_psd_22,
        "shear_psd_determinant": shear_psd_det,
        "HC_to_H1_lower_constant": c_lower,
        "HC_to_H1_upper_constant": c_upper,
        "finite_channel_lower_comparison_margin": finite_lower_margin,
        "tail_lower_coefficient_margin": tail_lower_margin,
        "tail_upper_coefficient_margin": tail_upper_margin,
        "V_XminusH1_to_XplusH1_upper": h1_multiplier,
        "V_XminusHC_to_XplusHC_upper": hc_multiplier,
        "R0_weighted_upper": C_RESOLVENT_UPPER,
        "q_L2_sandwich_unchanged": Q_UPPER,
        "q_H1_R0V": q_h1, "q_HC_R0V": q_hc,
    }
    return {
        "schema": "PHYS72_ANGULAR_WEIGHTED_BOUNDS_V1",
        "status": "PASS_EXACT_SCALAR_WITNESSES_OF_PROVED_BOUNDS",
        "assumptions": [
            "Original atomic V=2(1+1/d)exp(-2d), d=|r*Omega-(7/10)zhat|, r>=27",
            "Proved original screen envelope V<=delta*exp(-2(r-B))",
            "Proved actual outgoing Coulomb Dirichlet estimate ||R0 f/r||<=Cstar||r f||",
            "Spherical boundary and central Coulomb R0 commute with angular spectral weights",
        ],
        "norms": {
            "H1": "sum_(j,m) (1+j(j+1))*abs(g_jm)^2",
            "HC": "sum_(j,m) C_j^2*abs(g_jm)^2; C_j=77 through j=28, then 800*(j+1)/189",
            "XminusY": "integral_B^infinity r^-2*||u(r)||_Y^2 dr",
            "XplusY": "integral_B^infinity r^2*||f(r)||_Y^2 dr",
            "angular_contraction_operator": "K=R0^+ V on Xminus(H1) or Xminus(HC)",
        },
        "proof_scope": "Scalar arithmetic verifies constants; accompanying analytic derivation supplies all-radial/all-angular inequalities",
        "proof": "theory/ANGULAR_MULTIPLIER_ADDENDUM.md",
        "values": {name: rational_record(value) for name, value in values.items()},
        "exact_comparisons": checks,
        "lambda1_admitted": {"XminusH1": True, "XminusHC": True},
        "remainder_authority": "Existing unweighted L2 sandwich q is unchanged and remains the sharper DtN remainder constant",
        "all_angular_degrees_retained": True,
        "physical_integrations": 0,
        "coulomb_evaluations": 0,
        "old_panel_or_profile_replays": 0,
        "old_campaign_verifier_runs": 0,
        "HH_R10": "OFF",
        "source_sha256": digest(Path(__file__)),
        "bounds_source_sha256": bounds_sha,
        "proof_source_sha256": digest(ROOT / "theory" / "ANGULAR_MULTIPLIER_ADDENDUM.md"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Create-only JSON output; otherwise stdout")
    args = parser.parse_args(argv)
    try:
        encoded = json.dumps(report(), indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
        else:
            print(encoded, end="")
        return 0
    except (OSError, ValueError, ArithmeticError) as exc:
        parser.exit(2, f"PHYS72 angular bound audit error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
