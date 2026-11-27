#!/usr/bin/env python3
"""Exact algebraic controls only; no scientific solver/coefficient imports.

The two-segment zero-opacity limit uses polynomial photon stocks and
E(u)=E0*exp(-u).  Energy identities are checked in Q[T], T=exp(-1).
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math
import platform
import resource
import sys
import time
from datetime import datetime, timezone


def poly(values):
    out = [F(x) for x in values]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out)


def add(a, b):
    n = max(len(a), len(b))
    return poly([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0) for i in range(n)])


def scale(a, x):
    return poly([v * F(x) for v in a])


def sub(a, b):
    return add(a, scale(b, -1))


def derivative(a):
    return poly([i * a[i] for i in range(1, len(a))] or [0])


def primitive(a):
    return poly([0] + [x / (i + 1) for i, x in enumerate(a)])


def evaluate(a, x):
    ans = F(0)
    for coeff in reversed(a):
        ans = ans * x + coeff
    return ans


def integral(a):
    return sum((x / (i + 1) for i, x in enumerate(a)), F(0))


def exponential_integral(a):
    # Integration by parts: int_0^1 u^n exp(-u)du
    # = n! (1 - T sum_{k=0}^n 1/k!), T=exp(-1).
    constant, t_coeff = F(0), F(0)
    for n, coeff in enumerate(a):
        fact = math.factorial(n)
        constant += coeff * fact
        t_coeff -= coeff * fact * sum((F(1, math.factorial(k))
                                      for k in range(n + 1)), F(0))
    return poly([constant, t_coeff])


def rational_string(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, (tuple, list)):
        return [rational_string(v) for v in x]
    if isinstance(x, dict):
        return {k: rational_string(v) for k, v in x.items()}
    return x


def interval_intersection(a, b):
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (lo, hi) if lo <= hi else None


def main():
    output = Path(sys.argv[1])
    if output.exists():
        raise FileExistsError(output)
    started = time.perf_counter()
    source = Path(__file__).resolve()
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    checks = []

    def check(name, lhs, rhs, relation="eq"):
        result = lhs == rhs if relation == "eq" else lhs != rhs
        checks.append({"name": name, "lhs": rational_string(lhs),
                       "rhs": rational_string(rhs), "relation": relation,
                       "pass": result})
        if not result:
            raise AssertionError(name)

    # Exact model: lambda=0, segment width h=1, photon-continuous seam.
    # f1(0)=P1(0)=2, q_f1=1, q1=1+u.
    frozen1, source1 = poly([2, 1]), poly([1, 1])
    true1 = add(poly([2]), primitive(source1))
    local1 = sub(true1, frozen1)
    endpoint1 = evaluate(true1, F(1))
    check("segment1_ODE_exact", derivative(true1), source1)
    check("segment1_incoming_zero", evaluate(local1, F(0)), F(0))
    check("segment1_local_residual", local1, poly([0, 0, F(1, 2)]))
    check("segment1_endpoint", endpoint1, F(7, 2))

    # Captured first endpoint and next frozen initial stock are 3.
    # f2=3+2u, q2=2-u.  Correct incoming is 7/2-3=1/2.
    captured1, frozen2_initial = F(3), F(3)
    frozen2, source2 = poly([3, 2]), poly([2, -1])
    incoming2 = endpoint1 - frozen2_initial
    true2 = add(poly([endpoint1]), primitive(source2))
    local2_zero_incoming = primitive(sub(source2, derivative(frozen2)))
    defect2 = add(poly([incoming2]), local2_zero_incoming)
    check("second_incoming_absolute_definition", incoming2, F(1, 2))
    representation1 = evaluate(frozen1, F(1)) - captured1
    frozen_defect1 = evaluate(local1, F(1))
    photon_gap = captured1 - frozen2_initial
    check("second_incoming_representation_bridge",
          frozen_defect1 + representation1 + photon_gap, incoming2)
    check("segment2_ODE_exact", derivative(true2), source2)
    check("segment2_firstvariation_response", add(frozen2, defect2), true2)
    check("segment2_endpoint", evaluate(true2, F(1)), F(5))
    reset_endpoint = evaluate(add(frozen2, local2_zero_incoming), F(1))
    check("reset_incoming_counterexample", reset_endpoint,
          evaluate(true2, F(1)), "ne")
    check("reset_exact_defect", evaluate(true2, F(1)) - reset_endpoint, F(1, 2))

    # A nonzero frozen/native representation change is also carried exactly.
    alternate_captured1 = F(14, 5)
    alternate_frozen2_initial = F(29, 10)
    alt_representation = evaluate(frozen1, F(1)) - alternate_captured1
    alt_gap = alternate_captured1 - alternate_frozen2_initial
    alt_incoming = endpoint1 - alternate_frozen2_initial
    check("nonzero_representation_and_gap_both_carried",
          frozen_defect1 + alt_representation + alt_gap, alt_incoming)
    check("representation_omission_detected", frozen_defect1 + alt_gap,
          alt_incoming, "ne")
    check("gap_omission_detected", frozen_defect1 + alt_representation,
          alt_incoming, "ne")

    # Generic linear accumulated photon moment; not an absorption claim at L=0.
    cumulative_moment = integral(true1) + integral(true2)
    frozen_moment = integral(frozen1) + integral(frozen2)
    moment_correction = integral(local1) + integral(defect2)
    check("generic_moment_exact_sum", cumulative_moment, F(7))
    check("generic_moment_correction_bridge", cumulative_moment - frozen_moment,
          moment_correction)
    check("generic_moment_total_correction", moment_correction, F(1, 2))
    prior_radius, local_radius, arbitrary_photon_gain = F(1, 7), F(1, 11), F(1, 2)
    correct_cumulative_radius = prior_radius + local_radius
    incorrectly_damped_radius = arbitrary_photon_gain * prior_radius + local_radius
    check("cumulative_moment_damping_counterexample", incorrectly_damped_radius,
          correct_cumulative_radius, "ne")
    check("cumulative_moment_damping_missing_error",
          correct_cumulative_radius - incorrectly_damped_radius, F(1, 14))

    # Exact rational bound on exp(-1): finite positive series + geometric tail.
    n = 6
    e_lo = sum((F(1, math.factorial(k)) for k in range(n + 1)), F(0))
    e_hi = e_lo + F(1, math.factorial(n + 1)) / (1 - F(1, n + 2))
    t_interval = (1 / e_hi, 1 / e_lo)
    check("exp_minus_one_lower_positive", t_interval[0] > F(1, 3), True)
    check("exp_minus_one_upper_less_half", t_interval[1] < F(1, 2), True)

    seam_results = []
    for label, energy2 in (("positive", F(5)), ("negative", F(1, 2))):
        # E1=3 exp(-u), E2=energy2 exp(-u), Z=int E P du.
        energy1 = F(3)
        source_energy = add(scale(exponential_integral(source1), energy1),
                            scale(exponential_integral(source2), energy2))
        redshift = add(scale(exponential_integral(true1), energy1),
                       scale(exponential_integral(true2), energy2))
        endpoint_stock = poly([0, energy2 * evaluate(true2, F(1))])
        initial_stock = poly([energy1 * evaluate(true1, F(0))])
        delta_energy = poly([energy2, -energy1])
        seam = scale(delta_energy, endpoint1)
        unanchored = add(sub(endpoint_stock, initial_stock), sub(redshift, source_energy))
        check(label + "_signed_global_energy_ledger", sub(unanchored, seam), poly([0]))
        check(label + "_omitting_anchor_detected", unanchored, poly([0]), "ne")
        check(label + "_wrong_anchor_sign_detected", add(unanchored, seam), poly([0]), "ne")
        captured_anchor = scale(delta_energy, captured1)
        correction_anchor = scale(delta_energy, endpoint1 - captured1)
        check(label + "_native_anchor_split", add(captured_anchor, correction_anchor), seam)
        seam_box = tuple(sorted(evaluate(seam, t) for t in t_interval))
        check(label + "_seam_sign", seam_box[0] > 0 if label == "positive" else seam_box[1] < 0, True)
        seam_results.append({"case": label, "DeltaE_polynomial": delta_energy,
                             "anchor_polynomial": seam, "anchor_interval": seam_box})

    # Incoming uncertainty survives exact local quadrature in the L=0 limit.
    eta = F(1, 10)
    carried_box = (incoming2 - eta, incoming2 + eta)
    endpoint_box = (carried_box[0] - F(1, 2), carried_box[1] - F(1, 2))
    check("fixed_incoming_radius_remains", (endpoint_box[1] - endpoint_box[0]) / 2, eta)

    # Intersection is valid only after same-target individual validity.
    target = F(5)
    old, new = (F(4), F(11, 2)), (F(9, 2), F(6))
    intersection = interval_intersection(old, new)
    check("same_target_intersection_contains_target", intersection[0] <= target <= intersection[1], True)
    check("same_target_crossing_intersection", intersection, (F(9, 2), F(11, 2)))
    bad_old, bad_new = (F(4), F(6)), (F(5), F(7))
    bad_intersection = interval_intersection(bad_old, bad_new)
    check("different_target_overlap_excludes_first", bad_intersection[0] <= F(9, 2) <= bad_intersection[1], False)
    check("different_target_overlap_excludes_second", bad_intersection[0] <= F(13, 2) <= bad_intersection[1], False)
    check("empty_intersection_failure", interval_intersection((F(0), F(1)), (F(2), F(3))), None)

    # Fixed positive-weight Minkowski route: maximal removable width ceiling.
    contributions = (F(1), F(2), F(6))
    full_width, removable = sum(contributions), sum(contributions[:2])
    fixed_floor = full_width - removable
    check("weighted_width_floor", fixed_floor, F(6))
    check("weighted_max_gain", removable / full_width, F(1, 3))
    check("weighted_max_ratio", full_width / fixed_floor, F(3, 2))

    finished_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    check("source_unchanged", finished_hash, source_hash)
    payload = {"schema": "bass-he-e13c6-transfer-exact-toys-v1",
               "status": "PASS_SCOPED_EXACT_TRANSFER_IDENTITIES",
               "model_identity": "GPT-6 Astra Pro",
               "role": "theory contributor; not independent decision reviewer",
               "scope": "Q[T] identities with T=exp(-1), zero-opacity two-segment manufactured model and exact interval bookkeeping",
               "claim_limits": "No actual candidate coefficient, path, physical, production, continuum or receiver verification",
               "source_sha256": source_hash, "source_bytes": source.stat().st_size,
               "executed_utc": datetime.now(timezone.utc).isoformat(),
               "argv": sys.argv, "python": sys.version, "platform": platform.platform(),
               "checks": checks, "checks_passed": len(checks), "checks_failed": 0,
               "scientific_solver_invocations": 0, "coefficient_evaluations": 0,
               "seam_controls": rational_string(seam_results),
               "exp_minus_one_bound": rational_string(t_interval),
               "elapsed_seconds": time.perf_counter() - started,
               "peak_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": payload["status"], "checks_passed": len(checks),
                      "checks_failed": 0, "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
