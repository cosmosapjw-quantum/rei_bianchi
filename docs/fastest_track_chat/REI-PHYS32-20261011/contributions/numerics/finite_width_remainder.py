#!/usr/bin/env python3
"""PHYS32 exact-rational finite-width diagnostics; no physical kernel imports."""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import platform
import sys


ROOT = Path(__file__).resolve().parents[2]
COUNTS = {
    "main_invocations": 1,
    "toy_root_enclosures": 0,
    "toy_bisection_steps": 0,
    "toy_moment_response_calls": 0,
    "toy_direct_response_calls": 0,
    "toy_profile_averages": 0,
    "peano_nonconstant_monomial_cases": 0,
    "physical_kernel_or_derivative_calls": 0,
    "physical_root_searches": 0,
    "old_scientific_imports_or_runs": 0,
    "numerical_quadrature_calls": 0,
    "finite_difference_calls": 0,
}
CHECKS = []
KCOEF = [Q(1), Q(0), Q(1), Q(-1, 10), Q(1, 100)]
MU = {
    "uniform": [Q(1), Q(0), Q(1, 3), Q(0), Q(1, 5)],
    "P4": [Q(1), Q(0), Q(1, 3), Q(0), Q(71, 315)],
}
R = Q(2)
W0 = Q(1)
ETA = Q(1, 4)
M1, M2, M3, M2_LOWER = Q(138, 25), Q(92, 25), Q(27, 25), Q(32, 25)
KAPPA = M2_LOWER / 2
SLOPE_UPPER = M2 / 2


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def check(identifier, gates, evidence):
    CHECKS.append({
        "id": identifier,
        "status": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "evidence": encode(evidence),
    })


def poly_derivative(p, order=1):
    ans = list(p)
    for _ in range(order):
        ans = [Q(i) * ans[i] for i in range(1, len(ans))]
    return ans


def poly_at(p, z):
    out = Q(0)
    for c in reversed(p):
        out = out * z + c
    return out


def poly_integral(p):
    return sum((2 * a / (i + 1) for i, a in enumerate(p) if i % 2 == 0), Q(0))


def monomial_average(n, y, delta, density):
    return sum(
        (
            Q(comb(n, j)) * y ** (n - j) * delta ** j
            * poly_integral([Q(0)] * j + list(density))
            for j in range(n + 1)
        ),
        Q(0),
    )


def geometry(s, delta, width_variance):
    r = R - delta
    v = width_variance - delta * delta / 3
    p = v / (r * r + v)
    e = -s * r
    x = s * v / r
    return r, v, p, 1 - p, e, x


def profile_average(y, delta, profile):
    COUNTS["toy_profile_averages"] += 1
    mu = MU[profile]
    return sum(
        (
            a * sum(
                (Q(comb(n, j)) * y ** (n - j) * delta ** j * mu[j]
                 for j in range(n + 1)), Q(0)
            )
            for n, a in enumerate(KCOEF)
        ),
        Q(0),
    )


def response_direct(s, delta, width_variance, profile):
    COUNTS["toy_direct_response_calls"] += 1
    _, _, p, q, e, x = geometry(s, delta, width_variance)
    return p * profile_average(e, delta, profile) + q * profile_average(x, delta, profile)


def response_moments(s, delta, width_variance, profile):
    COUNTS["toy_moment_response_calls"] += 1
    r = R - delta
    v = width_variance - delta * delta / 3
    third = s * v * (v / r - r)
    fourth = v * r * r - v * v + v ** 3 / (r * r)
    fourth += 2 * delta * delta * v + MU[profile][4] * delta ** 4
    return 1 + width_variance - third / 10 + fourth / 100


def analytic_bounds(s, delta):
    r, _, p, q, _, x = geometry(s, delta, W0)
    p0 = Q(1, 5)
    x0 = Q(s, 2)
    endpoint_oscillation = Q(1251 + 260 * s, 320)
    b = abs(p - p0) * endpoint_oscillation
    b += M1 * (p * delta + q * abs(x - x0))
    b += Q(1, 3) * M2 * delta * delta / 2
    rho = b / KAPPA
    h = max(delta, (rho + W0 * delta / R + delta * delta / 3) / r)
    slope_error = M3 * (h + delta) / 2
    c = Q(411 + 40 * s, 400)
    d4 = -Q(32, 315 * (411 + 40 * s))
    remainder = abs(d4) * slope_error / KAPPA
    return {
        "B": b, "rho": rho, "h": h, "S_C": slope_error,
        "C": c, "D4": d4, "remainder_R": remainder,
        "endpoint_k_oscillation": endpoint_oscillation,
        "k4_oscillation": Q(0), "omega4": Q(0),
        "kappa": KAPPA, "A": Q(813 + 60 * s, 400),
    }


def enclose_root(s, delta, profile, bounds, identifier):
    COUNTS["toy_root_enclosures"] += 1
    lo, hi = W0 - ETA, W0 + ETA
    level = bounds["A"]
    initial_lo = response_moments(s, delta, lo, profile) - level
    initial_hi = response_moments(s, delta, hi, profile) - level
    if not (initial_lo < 0 < initial_hi):
        raise ArithmeticError("Initial exact root bracket failed: " + identifier)
    for _ in range(80):
        mid = (lo + hi) / 2
        residual = response_moments(s, delta, mid, profile) - level
        COUNTS["toy_bisection_steps"] += 1
        if residual < 0:
            lo = mid
        else:
            hi = mid
    residual_lo = response_moments(s, delta, lo, profile) - level
    residual_hi = response_moments(s, delta, hi, profile) - level
    direct_lo = response_direct(s, delta, lo, profile) - level
    direct_hi = response_direct(s, delta, hi, profile) - level
    rho = bounds["rho"]
    check(identifier, {
        "initial_strict_bracket": initial_lo < 0 < initial_hi,
        "final_enclosure": residual_lo <= 0 <= residual_hi,
        "two_response_paths_identical_at_endpoints": residual_lo == direct_lo and residual_hi == direct_hi,
        "exact_80_step_width": hi - lo == Q(1, 2 ** 81),
        "enclosure_inside_derived_root_displacement": W0 - rho <= lo <= hi <= W0 + rho,
    }, {
        "profile": profile, "lo": lo, "hi": hi, "width": hi - lo,
        "initial_residuals": [initial_lo, initial_hi],
        "moment_residuals": [residual_lo, residual_hi],
        "direct_residuals": [direct_lo, direct_hi],
        "root_distance_bound": rho,
    })
    return {"lo": lo, "hi": hi, "profile": profile}


def peano_checks():
    qpoly = [Q(1), Q(0), Q(-4), Q(0), Q(6), Q(0), Q(-4), Q(0), Q(1)]
    difference = [Q(3, 16), Q(0), Q(-30, 16), Q(0), Q(35, 16)]
    obtained = [a / 768 for a in poly_derivative(qpoly, 4)]
    check("P32-RODRIGUES", {"exact_polynomial_coefficients": obtained == difference},
          {"obtained": obtained, "density_difference": difference})
    boundary = [[poly_at(poly_derivative(qpoly, order), z) for z in (Q(-1), Q(1))]
                for order in range(4)]
    check("P32-BOUNDARY", {"all_eight_boundary_terms_zero": all(v == 0 for row in boundary for v in row)},
          {"orders": [0, 1, 2, 3], "at_minus_plus_one": boundary})
    pi_density = [Q(315, 256) * a for a in qpoly]
    mass = poly_integral(pi_density)
    check("P32-NORMALIZATION", {"positive_weight_mass_one": mass == 1},
          {"mass": mass, "unscaled_mass": poly_integral(qpoly),
           "positivity_basis": "(1-z^2)^4 >= 0 on [-1,1]; exact factorization, not sampled"})
    for n in (5, 6):
        y, delta = Q(1, 3), Q(1, 7)
        lhs = monomial_average(n, y, delta, difference)
        rhs = delta ** 4 * Q(factorial(n), factorial(n - 4)) / 945
        rhs *= monomial_average(n - 4, y, delta, pi_density)
        COUNTS["peano_nonconstant_monomial_cases"] += 1
        check("P32-MONOMIAL-" + str(n), {"direct_integral_equals_positive_kernel": lhs == rhs},
              {"degree": n, "center": y, "delta": delta, "direct": lhs, "peano": rhs, "residual": lhs - rhs})


def main(output):
    contract_path = ROOT / "PHYSICS_CONTRACT.json"
    protocol_path = Path(__file__).with_name("PROTOCOL.json")
    contract = json.loads(contract_path.read_text())
    protocol = json.loads(protocol_path.read_text())
    checks_expected = protocol["check_ids"]
    peano_checks()
    branches = {}
    gaps = {}
    for delta in (Q(1, 100), Q(1, 50)):
        tag = str(delta).replace("/", "_")
        for branch, s in (("upper", 1), ("lower", -1)):
            key = branch + "_" + tag
            bounds = analytic_bounds(s, delta)
            at_base = {p: response_moments(s, delta, W0, p) for p in ("uniform", "P4")}
            direct_base = {p: response_direct(s, delta, W0, p) for p in ("uniform", "P4")}
            roots = {
                p: enclose_root(s, delta, p, bounds, "P32-ROOT-" + key + "-" + p)
                for p in ("uniform", "P4")
            }
            interval = [
                (roots["P4"]["lo"] - roots["uniform"]["hi"]) / delta ** 4,
                (roots["P4"]["hi"] - roots["uniform"]["lo"]) / delta ** 4,
            ]
            d4, rem = bounds["D4"], bounds["remainder_R"]
            lower_mvt = -Q(2, 7875) / KAPPA
            upper_mvt = -Q(2, 7875) / SLOPE_UPPER
            gates = {
                "fixed_tube_strictly_feasible": delta * delta / 3 < W0 - ETA and W0 + ETA < (2 - delta) ** 2,
                "noncircular_root_existence_B_lt_kappa_eta": bounds["B"] < KAPPA * ETA,
                "base_residuals_bounded": all(abs(v - bounds["A"]) <= bounds["B"] for v in at_base.values()),
                "independent_base_response_paths_equal": at_base == direct_base,
                "exact_finite_width_response_difference": at_base["P4"] - at_base["uniform"] == Q(2, 7875) * delta ** 4,
                "whole_root_difference_interval_in_quartic_remainder": d4 - rem <= interval[0] <= interval[1] <= d4 + rem,
                "whole_root_difference_interval_in_MVT_bounds": lower_mvt <= interval[0] <= interval[1] <= upper_mvt,
                "sufficient_sign_condition": rem < abs(d4),
                "negative_root_difference": interval[1] < 0,
                "finite_width_not_identically_quartic": interval[1] < d4 or d4 < interval[0],
            }
            check("P32-BRANCH-" + key, gates, {
                "delta": delta, "s": s, "bounds": bounds,
                "base_moment_responses": at_base, "base_direct_responses": direct_base,
                "scaled_root_difference_interval": interval,
                "scaled_quartic_remainder_interval": [d4 - rem, d4 + rem],
                "MVT_interval": [lower_mvt, upper_mvt],
                "scaled_error_interval": [interval[0] - d4, interval[1] - d4],
            })
            branches[key] = {"delta": delta, "branch": branch, "bounds": bounds,
                             "roots": roots, "scaled_difference_interval": interval}
        lower = branches["lower_" + tag]
        upper = branches["upper_" + tag]
        gap_interval = [
            lower["scaled_difference_interval"][0] - upper["scaled_difference_interval"][1],
            lower["scaled_difference_interval"][1] - upper["scaled_difference_interval"][0],
        ]
        gap_d4 = lower["bounds"]["D4"] - upper["bounds"]["D4"]
        gap_rem = lower["bounds"]["remainder_R"] + upper["bounds"]["remainder_R"]
        check("P32-GAP-" + tag, {
            "sum_remainder_encloses_whole_gap_interval": gap_d4 - gap_rem <= gap_interval[0] <= gap_interval[1] <= gap_d4 + gap_rem,
            "gap_sign_sufficient_condition": gap_rem < abs(gap_d4),
            "negative_toy_gap_change": gap_interval[1] < 0,
        }, {"delta": delta, "D4_gap": gap_d4, "R_gap": gap_rem, "scaled_gap_interval": gap_interval})
        gaps[tag] = {"delta": delta, "D4_gap": gap_d4, "R_gap": gap_rem,
                     "scaled_gap_interval": gap_interval}
    check("P32-EXECUTION-COUNTS", {
        "eight_enclosures": COUNTS["toy_root_enclosures"] == 8,
        "640_bisection_steps": COUNTS["toy_bisection_steps"] == 640,
        "680_moment_calls": COUNTS["toy_moment_response_calls"] == 680,
        "24_direct_calls": COUNTS["toy_direct_response_calls"] == 24,
        "48_profile_averages": COUNTS["toy_profile_averages"] == 48,
        "zero_physical_or_old_scientific_calls": all(COUNTS[k] == 0 for k in
            ("physical_kernel_or_derivative_calls", "physical_root_searches",
             "old_scientific_imports_or_runs", "numerical_quadrature_calls", "finite_difference_calls")),
    }, dict(COUNTS))
    actual_ids_including_this = [x["id"] for x in CHECKS] + ["P32-CONTRACT-AND-IDS"]
    check("P32-CONTRACT-AND-IDS", {
        "task": contract["task"] == "REI-PHYS32-20261011",
        "contract_bytes": hashlib.sha256(contract_path.read_bytes()).hexdigest() == protocol["contract_sha256"],
        "frozen_check_sequence": actual_ids_including_this == checks_expected,
        "rational_arithmetic_only": protocol["arithmetic"] == "fractions.Fraction",
    }, {"actual_check_ids": actual_ids_including_this, "expected_count": len(checks_expected)})
    failed = [x["id"] for x in CHECKS if x["status"] != "PASS"]
    raw = {
        "task": contract["task"],
        "schema": "PHYS32_EXACT_FINITE_WIDTH_V1",
        "evidence_scope": "Exact rational diagnostics of a dimensionless polynomial toy; no physical enclosure",
        "arithmetic": "fractions.Fraction; zero tolerance for identities; exact outward interval subtraction",
        "python_version": platform.python_version(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "protocol_sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        "counts": COUNTS,
        "branches": branches,
        "gaps": gaps,
        "checks": CHECKS,
        "summary": {
            "evaluated_check_groups": len(CHECKS), "passing_check_groups": len(CHECKS) - len(failed),
            "failed_check_ids": failed, "not_evaluated_check_ids": [],
            "mathematical_check_groups": 19, "contract_and_accounting_groups": 2,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(encode(raw), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(raw["summary"], sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(main(args.output))
