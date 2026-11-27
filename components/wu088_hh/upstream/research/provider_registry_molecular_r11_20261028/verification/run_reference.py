#!/usr/bin/env python3
"""One independent R11 reference, fixed before execution.

No production or predecessor solver is imported. Exact Fraction powers and a
direct finite convolution construct the selected-rational-q residual envelope.
The E solution uses Decimal160 closed-form scalar exp/phi1/phi2 moments, not the
production positive Taylor96 algorithm. The inherited native exponential and
the saved ODE trajectories are read as immutable evidence, never recomputed.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve()
LEAF = HERE.parents[1]
REPO = HERE.parents[3]
WALL_START = time.monotonic()
ZERO, ONE = Decimal(0), Decimal(1)
EXPECTED_SOURCE_SHA = {
    "R6_primary": "1a3b55f7c14a64a10a651de2df7b7f7d2df24d0b9e809b729f32d73377c90e84",
    "R7_input": "3ff9c2535e5c0ce6ffa5e9671de15aad6649e0996cd9b9e275cc290facd8d330",
    "R7_primary": "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15",
    "R7_reference": "e403c7803c080fd4f26be71a93b782b02d874f80ef11c85a706bea71e2a743cd",
    "R10_primary": "1713df54bc3653003614f3deba93212735a345e8d7220f053ab9af2d84677fb1",
}
REPORT = {
    "schema": "WU_R11_INDEPENDENT_REFERENCE_V1",
    "unit": "WU_FULL_GENERATOR_BLOCK_R11",
    "started_utc": datetime.now(timezone.utc).isoformat(),
    "checks": [], "hd_cases": [], "controls": [], "generator_controls": [],
    "component_comparisons": 0, "exact_component_comparisons": 0,
    "decimal_component_comparisons": 0, "sample_component_comparisons": 0,
    "failed_components": 0, "comparison_failures": [], "first_failure": None,
    "scope": {
        "production_imports": 0, "predecessor_solver_imports": 0,
        "new_ODE_calls": 0, "native_matrix_exponential_recomputations": 0,
        "old_science_replay": 0, "physical_consumer_admitted": False,
        "kernel": "exact Fraction q**floor(n/block_steps), using actual selected rational q",
        "E_reference": "Decimal160 scalar closed-form phi1/phi2, signed d, zero branch exact",
        "guard": "1e-80*max(1,abs(reference),abs(lower),abs(upper)); fixed before execution",
        "lower_meaning": "ideal selected-rational-q comparison only, never actual physical error",
        "sample_meaning": "saved validation samples with original tolerance; never caps",
        "component_counts_are_not_distinct_physical_scenarios": True,
    },
    "versions": {"Python": platform.python_version(), "platform": platform.platform()},
}


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inside(relative):
    path = (REPO / relative).resolve()
    if not path.is_relative_to(REPO.resolve()):
        raise ValueError("Source path escapes the repository")
    return path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def q(value):
    if isinstance(value, (bool, float)) or not isinstance(value, (str, int, Fraction)):
        raise TypeError("Reference exact input must be int, rational text, or Fraction")
    return Fraction(value)


def decimal(value):
    if isinstance(value, Decimal):
        return value
    value = q(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def as_matrix(values):
    return [[q(x) for x in row] for row in values]


def flatten(values):
    if isinstance(values, (list, tuple)):
        for value in values:
            yield from flatten(value)
    else:
        yield values


def encode(value):
    if isinstance(value, (Fraction, Decimal)):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def cpu_seconds():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def budget():
    if cpu_seconds() > 58 or time.monotonic() - WALL_START > 88:
        raise RuntimeError("R11_REFERENCE_BOUNDED_PREFINALIZATION_STOP")


def check(name, okay, evidence=None):
    row = {"name": name, "status": "PASS" if bool(okay) else "FAIL"}
    if evidence is not None:
        row["evidence"] = encode(evidence)
    REPORT["checks"].append(row)
    if not okay and REPORT["first_failure"] is None:
        REPORT["first_failure"] = row.copy()
    return bool(okay)


def require(name, okay, evidence=None):
    if not check(name, okay, evidence):
        raise ValueError("Required reference identity failed: " + name)


def compare(name, truth, upper, lower=None, *, exact=False):
    """Finite component enclosure check; exact checks use no numerical guard."""
    tt, uu = list(flatten(truth)), list(flatten(upper))
    ll = None if lower is None else list(flatten(lower))
    require(name + ":shape", len(tt) == len(uu) and (ll is None or len(ll) == len(tt)),
            {"truth": len(tt), "upper": len(uu), "lower": None if ll is None else len(ll)})
    failures = []
    max_above, max_below, max_width = ZERO, ZERO, ZERO
    min_slack = None
    for index, (tv, uv) in enumerate(zip(tt, uu)):
        lv = None if ll is None else ll[index]
        if exact:
            a, b = q(tv), q(uv)
            low = None if lv is None else q(lv)
            eps = Fraction(0)
            REPORT["exact_component_comparisons"] += 1
        else:
            a, b = decimal(tv), decimal(uv)
            low = None if lv is None else decimal(lv)
            eps = Decimal("1e-80") * max(ONE, abs(a), abs(b), ZERO if low is None else abs(low))
            REPORT["decimal_component_comparisons"] += 1
        REPORT["component_comparisons"] += 1
        okay = b >= 0 and a <= b + eps
        if low is not None:
            okay = okay and low >= 0 and low <= b and low <= a + eps
            max_below = max(max_below, decimal(low - a))
            max_width = max(max_width, decimal(b - low))
        max_above = max(max_above, decimal(a - b))
        slack = decimal(b - a)
        min_slack = slack if min_slack is None else min(min_slack, slack)
        if not okay:
            REPORT["failed_components"] += 1
            detail = {"index": index, "reference": str(a), "upper": str(b),
                      "lower": None if low is None else str(low), "guard": str(eps)}
            if len(failures) < 8:
                failures.append(detail)
            if len(REPORT["comparison_failures"]) < 40:
                REPORT["comparison_failures"].append({"group": name, **detail})
    check(name, not failures, {
        "components": len(tt), "arithmetic": "exact Fraction" if exact else "Decimal160",
        "failed_examples": failures, "max_reference_above_upper": max_above,
        "max_lower_above_reference": max_below, "min_upper_minus_reference": min_slack,
        "max_interval_width": max_width,
    })


def fixed_sources(config, primary):
    freeze_path = LEAF / "raw/PREEXECUTION_FREEZE.json"
    freeze = read_json(freeze_path)
    require("freeze_status", freeze.get("status") == "PASS")
    indexed = {row["path"]: row for row in freeze["files"]}
    required = config["required_frozen_sources"] + [row["path"] for row in config["sources"].values()]
    require("freeze_required_membership", set(required).issubset(indexed),
            {"missing": sorted(set(required) - set(indexed))})
    require("freeze_no_duplicate_paths", len(indexed) == len(freeze["files"]))
    for relative, entry in indexed.items():
        path = inside(relative)
        require("freeze_bytes:" + relative,
                path.is_file() and path.stat().st_size == entry["bytes"] and file_sha(path) == entry["sha256"])
    for field, key in (("core_sha256", "core_path"), ("input_sha256", "primary_input_path"),
                       ("runner_sha256", "primary_runner_path")):
        require("primary_frozen_binding:" + field, primary.get(field) == indexed[config[key]]["sha256"])
    require("primary_freeze_binding", primary.get("freeze_sha256") == file_sha(freeze_path))
    REPORT["freeze_sha256"] = file_sha(freeze_path)
    result = {}
    for name, entry in config["sources"].items():
        path = inside(entry["path"])
        require("source_identity:" + name, entry["sha256"] == EXPECTED_SOURCE_SHA[name]
                and path.stat().st_size == entry["bytes"] and file_sha(path) == entry["sha256"]
                and indexed[entry["path"]]["sha256"] == entry["sha256"])
        result[name] = read_json(path)
    REPORT["source_sha256"] = EXPECTED_SOURCE_SHA
    return result


def generator_reference(name, fixture, certificate):
    K = as_matrix(fixture["K"])
    pi, destruction = [q(x) for x in fixture["pi"]], [q(x) for x in fixture["destruction"]]
    n = len(pi)
    require(name + ":generator_dimensions", n >= 1 and len(K) == n and len(destruction) == n
            and all(len(row) == n for row in K))
    check(name + ":conservative_Metzler_K", all(sum(K[i][j] for i in range(n)) == 0 for j in range(n))
          and all(K[i][j] >= 0 for i in range(n) for j in range(n) if i != j))
    check(name + ":simplex_nonnegative_d", sum(pi) == 1 and min(pi + destruction) >= 0)
    H = [[pi[i] * destruction[j] - (destruction[j] if i == j else 0)
          for j in range(n)] for i in range(n)]
    exits = [-H[j][j] for j in range(n)]
    bH = max(exits)
    norm = max(sum(abs(H[i][j]) for i in range(n)) for j in range(n))
    wbox = [q(x) for x in fixture["w_box"]]
    tau, rho = q(fixture["tau"]), q(fixture["rho_K"])
    epsilon = bH * wbox[1] * tau
    ex = (-decimal(epsilon)).exp()
    additive = min(Fraction(1), rho + tau * wbox[1] * norm)
    minor = ONE - ex * (ONE - decimal(rho))
    check(name + ":exact_H", as_matrix(certificate["H"]) == H)
    check(name + ":exact_norm_identity", q(certificate["b_H"]) == bH and
          q(certificate["H_l1_norm"]) == norm == 2 * bH)
    check(name + ":exact_parameters", q(certificate["tau"]) == tau
          and q(certificate["rho_K"]) == rho and list(map(q, certificate["w_box"])) == wbox
          and q(certificate["epsilon"]) == epsilon and q(certificate["q_additive"]) == additive)
    compare(name + ":exp_minus_epsilon", [ex], [certificate["exp_minus_epsilon_interval"][1]],
            [certificate["exp_minus_epsilon_interval"][0]])
    compare(name + ":minorization", [minor], [certificate["q_minorization_interval"][1]],
            [certificate["q_minorization_interval"][0]])
    chosen = q(certificate["q"])
    ideal_min = min(ONE, decimal(additive), minor)
    compare(name + ":chosen_q_encloses_ideal_min", [ideal_min], [chosen])
    scale = 2 ** 128
    numerator = additive.numerator * scale
    ceiling = Fraction((numerator + additive.denominator - 1) // additive.denominator, scale)
    check(name + ":chosen_outward_minimum", chosen == min(Fraction(1), ceiling,
          q(certificate["q_minorization_interval"][1])))
    check(name + ":contraction_range", 0 <= chosen <= 1 and
          certificate["strict_implemented_contraction"] == (chosen < 1))
    check(name + ":full_family_flags", certificate["uniform_all_starts"] is True and
          certificate["nominal_K_rho_directly_transferred"] is False and
          certificate["physical_consumer_admitted"] is False)
    return {"q": chosen, "b_H": bH, "epsilon": epsilon,
            "ideal_additive": additive, "ideal_minorization": minor}


def nominal_source_binding(name, fixture, certificate, inherited):
    K = as_matrix(fixture["K"])
    tau, rho = q(fixture["H"]), q(fixture["rho"])
    nominal = certificate["nominal_certificate"]
    canonical_matrix = json.dumps([[str(x) for x in row] for row in K], separators=(",", ":"))
    check(name + ":nominal_K_hash", nominal["K_sha256"] == hashlib.sha256(canonical_matrix.encode()).hexdigest())
    check(name + ":nominal_all_starts_metadata", nominal["uniform_all_starts"] is True
          and nominal["fixed_homogeneous_K"] is True
          and nominal["scientific_status"] == "CERTIFIED_K_BLOCK"
          and nominal["source_sha256"] == EXPECTED_SOURCE_SHA["R7_primary"]
          and nominal["certificate_id"] == fixture["certificate_id"]
          and q(nominal["tau"]) == tau and q(nominal["rho_K"]) == rho)
    if len(K) == 2:
        check(name + ":analytic_two_state_K", K == [[Fraction(-1), Fraction(1)], [Fraction(1), Fraction(-1)]]
              and tau == Fraction(1, 4) and rho == Fraction(5, 8))
        check(name + ":analytic_nominal_rho", (-2 * decimal(tau)).exp() <= decimal(rho))
    else:
        graph = inherited["R6_primary"]["graph"]
        candidates = [row for row in graph["blocks"] if row["id"] == "native_mu_256"]
        require(name + ":unique_saved_native_block", len(candidates) == 1)
        block = candidates[0]
        check(name + ":saved_native_tau_rho", q(block["H"]) == tau and q(block["rho_upper"]) == rho
              and q(block["beta_lower"]) + rho == 1 and block["N"] == 512)
        lo, hi = as_matrix(graph["K_lo"]), as_matrix(graph["K_hi"])
        check(name + ":saved_native_K_box_membership", len(K) == 9 and
              all(lo[i][j] <= K[i][j] <= hi[i][j] for i in range(9) for j in range(9)))
        check(name + ":native_missingness_retained", inherited["R6_primary"]["thermal"]["vibrational_state"] == "UNSPECIFIED"
              and inherited["R6_primary"]["thermal"]["missing_transitions"] == "MISSING_NOT_ZERO"
              and fixture["source_scope"] == "SYNTHETIC_REACTION_CONTROL_ON_REUSED_NATIVE_GENERATOR_BOX")


def moments(d, delta):
    """Independent closed forms; exact d=0 branch avoids singular expressions."""
    dd, dt = q(d), q(delta)
    x = decimal(dd * dt)
    expx = x.exp()
    if dd == 0:
        half = decimal(dt) / 2
        return {"exp": ONE, "W0": half, "W1": half, "phi": decimal(dt)}
    # phi_1=(exp(x)-1)/x, phi_2=(exp(x)-1-x)/x^2.
    # W0=delta*(phi_1-phi_2); W1=delta*phi_2.
    phi1 = (expx - ONE) / x
    phi2 = (expx - ONE - x) / (x * x)
    return {"exp": expx, "W0": decimal(dt) * (phi1 - phi2),
            "W1": decimal(dt) * phi2, "phi": decimal(dt) * phi1}


def forcing_array(value, cells):
    result = list(map(q, value)) if isinstance(value, list) else [q(value)] * cells
    if len(result) != cells or min(result) < 0:
        raise ValueError("Invalid independent forcing input")
    return result


def ideal_raw(parameters):
    cells, block = parameters["cells"], parameters["block_steps"]
    chosen, dt = q(parameters["q"]), q(parameters["delta"])
    R0, E0 = map(q, parameters["initial"])
    cc, dd = q(parameters["c"]), q(parameters["d"])
    gr, ge = (forcing_array(parameters[k], cells) for k in ("g_r", "g_e"))
    # Direct exact powers differ from the production rounded recurrence.
    h = [chosen ** (n // block) for n in range(cells + 1)]
    F = [Fraction(0)] + [dt * sum((h[n - 1 - j] * gr[j] for j in range(n)), Fraction(0))
                            for n in range(1, cells + 1)]
    R = [R0 * h[n] + F[n] for n in range(cells + 1)]
    V = [R0 * h[n] + F[n + 1] for n in range(cells)]
    rw = [max(R[n], V[n]) for n in range(cells)]
    weights = moments(dd, dt)
    ex, p0, p1, phi = (weights[k] for k in ("exp", "W0", "W1", "phi"))
    E = [decimal(E0)]
    ew = []
    for n in range(cells):
        # The exact envelope is affine from R[n] to V[n] inside the cell.
        endpoint = ex * E[-1] + decimal(cc) * (p0 * decimal(R[n]) + p1 * decimal(V[n])) + phi * decimal(ge[n])
        constant_endpoint = ex * E[-1] + phi * (decimal(cc * rw[n]) + decimal(ge[n]))
        ew.append(max(E[-1], endpoint, constant_endpoint))
        E.append(endpoint)
    return {"h": h, "F": F, "R": R, "V": V, "E": E,
            "Rwhole": rw, "Ewhole": ew, "weights": weights,
            "points": [[decimal(R[n]), E[n]] for n in range(cells + 1)],
            "whole": [[decimal(rw[n]), ew[n]] for n in range(cells)]}


def ideal_capped(parameters, raw, cap):
    """Ideal monotone comparison map for the documented capped arithmetic."""
    cells = parameters["cells"]
    cc = decimal(parameters["c"])
    ge = list(map(decimal, forcing_array(parameters["g_e"], cells)))
    point = [[decimal(x) for x in row] for row in cap["endpoints_upper"]]
    whole = [[decimal(x) for x in row] for row in cap["whole_cells_upper"]]
    ex, phi = raw["weights"]["exp"], raw["weights"]["phi"]
    P = [[decimal(x) for x in parameters["initial"]]]
    W = []
    for n in range(cells):
        # Whole-cell valid intersections are used as separate scalar inputs.
        Rcell = min(decimal(raw["Rwhole"][n]), whole[n][0])
        Eleft = min(P[n][1], raw["E"][n], point[n][1], whole[n][1])
        end = ex * Eleft + phi * (cc * Rcell + ge[n])
        Ecell = min(raw["Ewhole"][n], max(Eleft, end), whole[n][1])
        P.append([min(decimal(raw["R"][n + 1]), Rcell, point[n + 1][0]),
                  min(raw["E"][n + 1], end, Ecell, point[n + 1][1])])
        W.append([Rcell, Ecell])
    # This final output intersection is independent of the global R convolution.
    final = []
    for n, value in enumerate(P):
        neighbors = []
        if n:
            neighbors.append(W[n - 1])
        if n < cells:
            neighbors.append(W[n])
        final.append([min([value[j]] + [v[j] for v in neighbors]) for j in (0, 1)])
    return {"points": final, "whole": W}


def check_sweep(name, artifact, parameters, cap=None):
    cells = parameters["cells"]
    require(name + ":output_shape", len(artifact["endpoints_upper"]) == cells + 1
            and len(artifact["whole_cells_upper"]) == cells
            and all(len(row) == 2 for row in artifact["endpoints_upper"] + artifact["whole_cells_upper"]))
    check(name + ":grid_and_q", artifact["cells"] == cells and artifact["block_steps"] == parameters["block_steps"]
          and q(artifact["q"]) == q(parameters["q"]) and q(artifact["delta"]) == q(parameters["delta"])
          and q(artifact["tau"]) == q(parameters["delta"]) * parameters["block_steps"])
    check(name + ":initial", list(map(q, artifact["initial"])) == list(map(q, parameters["initial"])))
    check(name + ":coefficients", q(artifact["coefficients"]["c"]) == q(parameters["c"])
          and q(artifact["coefficients"]["d"]) == q(parameters["d"])
          and all(list(map(q, artifact["coefficients"][k])) == forcing_array(parameters[k], cells) for k in ("g_r", "g_e")))
    check(name + ":scope", artifact["h0"] == 1 and artifact["R_memory_reset"] is False
          and artifact["physical_consumer_admitted"] is False and artifact["new_ODE_calls"] == 0
          and artifact["rounding"]["bits"] == 128 and artifact["rounding"]["degree"] == 96)
    raw = ideal_raw(parameters)
    compare(name + ":kernel_exact", raw["h"], artifact["kernel_upper"], artifact["kernel_lower"], exact=True)
    compare(name + ":forcing_exact", raw["F"], artifact["forcing_upper"], artifact["forcing_lower"], exact=True)
    affine = artifact["R_affine_cells"]
    require(name + ":affine_shape", len(affine) == cells)
    compare(name + ":affine_left_exact", raw["R"][:-1], [x["left_interval"][1] for x in affine],
            [x["left_interval"][0] for x in affine], exact=True)
    compare(name + ":affine_right_left_limit_exact", raw["V"], [x["right_left_limit_interval"][1] for x in affine],
            [x["right_left_limit_interval"][0] for x in affine], exact=True)
    for key in ("exp", "W0", "W1", "phi"):
        compare(name + ":closed_form_" + key, [raw["weights"][key]],
                [artifact["Bernstein_weights"][key][1]], [artifact["Bernstein_weights"][key][0]])
    if cap is None:
        require(name + ":raw_lower_present", artifact["endpoints_lower"] is not None)
        compare(name + ":R_endpoints_exact", raw["R"], [row[0] for row in artifact["endpoints_upper"]],
                [row[0] for row in artifact["endpoints_lower"]], exact=True)
        compare(name + ":E_endpoints_Decimal160", raw["E"], [row[1] for row in artifact["endpoints_upper"]],
                [row[1] for row in artifact["endpoints_lower"]])
        compare(name + ":R_whole_exact", raw["Rwhole"], [row[0] for row in artifact["whole_cells_upper"]], exact=True)
        compare(name + ":E_whole_signed_scalar", raw["Ewhole"], [row[1] for row in artifact["whole_cells_upper"]])
        target = {"points": raw["points"], "whole": raw["whole"]}
        check(name + ":raw_cap_absent", artifact["cap_source_sha256"] is None)
    else:
        check(name + ":capped_lower_absent", artifact["endpoints_lower"] is None)
        check(name + ":cap_source_identity", artifact["cap_source_sha256"] == EXPECTED_SOURCE_SHA["R10_primary"])
        target = ideal_capped(parameters, raw, cap)
        compare(name + ":capped_endpoint_reference", target["points"], artifact["endpoints_upper"])
        compare(name + ":capped_whole_reference", target["whole"], artifact["whole_cells_upper"])
        for key in ("endpoints_upper", "whole_cells_upper"):
            compare(name + ":no_worse_R10:" + key, artifact[key], cap[key], exact=True)
    check(name + ":closed_cells_cover_both_reported_endpoints",
          all(q(artifact["endpoints_upper"][n + edge][j]) <= q(artifact["whole_cells_upper"][n][j])
              for n in range(cells) for edge in (0, 1) for j in (0, 1)))
    check(name + ":fresh_forcing_h0", raw["h"][0] == 1 and raw["F"][1] ==
          q(parameters["delta"]) * forcing_array(parameters["g_r"], cells)[0])
    return {"id": name, "q": str(q(parameters["q"])), "cells": cells,
            "endpoint_reference": encode(target["points"][-1]),
            "whole_final_reference": encode(target["whole"][-1]),
            "moment_reference": encode(raw["weights"]),
            "reference_construction": "exact chosen-q kernel/convolution, independent Decimal160 closed forms",
            "raw_internal": raw}


def saved_samples(name, artifact, saved):
    dt, cells = q(artifact["delta"]), artifact["cells"]
    require(name + ":sample_shape", len(saved["times"]) == len(saved["R_E"]) == cells + 1)
    ulp_errors = []
    for n, clock in enumerate(saved["times"]):
        exact = n * dt
        ulp = Fraction.from_float(math.ulp(float(exact)))
        ulp_errors.append(abs(Fraction.from_float(float(clock)) - exact) / ulp)
    require(name + ":saved_clock_identity", max(ulp_errors) <= 1,
            {"maximum_deviation_ULP": max(ulp_errors),
             "relation": "saved binary64 clock within one ULP of the exact source-bound rational grid"})
    failures = []
    max_raw = {"excess": ZERO}
    max_after = ZERO
    strict_failures = 0
    for n, values in enumerate(saved["R_E"]):
        for j, value in enumerate(values):
            sample, upper = Decimal(str(value)), decimal(artifact["endpoints_upper"][n][j])
            tolerance = Decimal("2e-12") + Decimal("2e-10") * max(abs(sample), abs(upper))
            excess = sample - upper
            after = excess - tolerance
            REPORT["component_comparisons"] += 1
            REPORT["sample_component_comparisons"] += 1
            strict_failures += int(excess > 0)
            if excess > max_raw["excess"]:
                max_raw = {"excess": excess, "index": n, "component": j,
                           "sample": sample, "upper": upper, "tolerance": tolerance}
            max_after = max(max_after, after)
            if sample < 0 or after > 0:
                REPORT["failed_components"] += 1
                if len(failures) < 8:
                    failures.append({"index": n, "component": j, "sample": sample,
                                     "upper": upper, "tolerance": tolerance})
    check(name + ":saved_sample_tolerance", not failures, {
        "components": 2 * (cells + 1), "failed_examples": failures,
        "maximum_actual_positive_excess": max_raw, "maximum_positive_excess_after_tolerance": max_after,
        "strict_sample_containment": strict_failures == 0,
        "strictly_above_upper_component_count": strict_failures,
        "criterion": "sample <= upper + 2e-12 + 2e-10*max(abs(sample),abs(upper)); fixed inherited criterion",
    })


def execute():
    config_path = LEAF / "verification/REFERENCE_INPUT.json"
    config = read_json(config_path)
    primary = read_json(inside(config["primary_result_path"]))
    fixed = read_json(inside(config["primary_input_path"]))
    REPORT["input_sha256"], REPORT["runner_sha256"] = file_sha(config_path), file_sha(HERE)
    REPORT["primary_sha256"] = file_sha(inside(config["primary_result_path"]))
    REPORT["Decimal_precision"] = 160
    require("fixed_reference_contract", config["precision_decimal_digits"] == 160
            and config["relative_guard"] == "1e-80" and config["sample_atol"] == "2e-12"
            and config["sample_rtol"] == "2e-10" and config["sample_clock_max_ULP"] == 1)
    inherited = fixed_sources(config, primary)
    require("primary_success_receipt", primary["status"] == "PASS" and primary["failure_count"] == 0,
            {"status": primary["status"], "failure_count": primary["failure_count"]})
    require("inherited_success_receipts", all(inherited[key]["status"] == expected_status
            for key, expected_status in config["expected_source_status"].items()),
            {key: inherited[key]["status"] for key in config["expected_source_status"]})
    expected = config["expected_HD_ids"]
    by_id = {row["id"]: row for row in primary["hd_cases"]}
    fixtures = {row["id"]: row for row in inherited["R7_input"]["hd_cases"]}
    old = {row["id"]: row for row in inherited["R7_primary"]["hd_cases"]}
    caps = {row["id"]: row["capped"] for row in inherited["R10_primary"]["hd_cases"]}
    samples = {row["id"].removeprefix("HD:"): row for row in inherited["R7_reference"]["hd_cases"]}
    require("HD_exact_case_identity", list(by_id) == expected and len(by_id) == len(primary["hd_cases"])
            and set(expected) == set(fixtures) == set(old) == set(caps) == set(samples))
    for index, case_id in enumerate(expected):
        budget()
        fixture, row, saved, cap = fixtures[case_id], by_id[case_id], old[case_id], caps[case_id]
        source = {"K": fixture["K"], "pi": fixture["pi"], "destruction": fixture["destruction"],
                  "w_box": fixture["density_box"]["w"], "tau": fixture["H"], "rho_K": fixture["rho"]}
        parameters = {key: saved["coefficients"][key] for key in ("c", "d", "g_r", "g_e")}
        parameters.update(delta=cap["delta"], cells=config["expected_HD_cells"],
                          block_steps=config["expected_block_steps"],
                          initial=[saved["initial_error"]["R"], saved["initial_error"]["E"]])
        check(case_id + ":grid_bound_to_tau", q(parameters["delta"]) * parameters["block_steps"] == q(fixture["H"])
              and cap["cells"] == 192 and list(map(q, cap["initial"])) == list(map(q, parameters["initial"])))
        for mode in ("raw", "capped"):
            name, artifact = case_id + ":" + mode, row[mode]
            gen = generator_reference(name, source, artifact["generator"])
            nominal_source_binding(name, fixture, artifact["generator"], inherited)
            parameters["q"] = gen["q"]
            check(name + ":source_binding", artifact["binding"] == cap["binding"]
                  and artifact["generator"]["binding"] == cap["binding"]
                  and artifact["generator"]["nominal_certificate"]["binding"] == cap["binding"]
                  and artifact["generator"]["nominal_certificate"]["source_pointer"] == f"/hd_cases/{index}/binding")
            checked = check_sweep(name, artifact, parameters, None if mode == "raw" else cap)
            checked.pop("raw_internal")
            REPORT["hd_cases"].append(checked)
            saved_samples(name, artifact, samples[case_id])
    control_source = {row["id"]: row for row in fixed["controls"]}
    controls = {row["id"]: row for row in primary["controls"]}
    require("control_identity", set(controls) == set(control_source)
            and len(controls) == len(primary["controls"])
            and set(config["required_controls"]).issubset(controls))
    for ident, source in control_source.items():
        budget()
        parameters = {key: value for key, value in source.items() if key != "id"}
        require("control:" + ident + ":frozen_parameters", controls[ident]["parameters"] == parameters)
        checked = check_sweep("control:" + ident, controls[ident]["raw"], parameters)
        raw = checked.pop("raw_internal")
        if ident in ("zero", "polynomial_q1"):
            dt, cc = q(parameters["delta"]), q(parameters["c"])
            gr, ge = q(parameters["g_r"]), q(parameters["g_e"])
            R0, E0 = map(q, parameters["initial"])
            truth = [[R0 + gr * n * dt, E0 + (cc * R0 + ge) * n * dt + cc * gr * (n * dt) ** 2 / 2]
                     for n in range(parameters["cells"] + 1)]
            compare("control:" + ident + ":exact_polynomial", truth,
                    controls[ident]["raw"]["endpoints_upper"], controls[ident]["raw"]["endpoints_lower"], exact=True)
        if ident == "late_forcing_q0":
            check("control:late_forcing_explicit", raw["R"][-1] == Fraction(1, 8)
                  and abs(raw["E"][-1] - Decimal(1) / 128) <= Decimal("1e-80"))
        if ident == "block_jump_left_limit":
            check("control:left_limit_explicit", raw["V"][1] == 1 and raw["R"][2] == Fraction(1, 2)
                  and raw["Rwhole"][1] == 1)
        REPORT["controls"].append(checked)
    for record in primary["generator_controls"]:
        source = record.get("parameters")
        if source is None and record["id"] == "reducible_q1":
            source = {"K": [[0, 0], [0, 0]], "pi": ["1/2", "1/2"], "destruction": [2, 4],
                      "w_box": [0, 2], "tau": "1/4", "rho_K": 1}
        require("generator_control:" + record["id"] + ":known_source", source is not None)
        checked = generator_reference("generator_control:" + record["id"], source, record["certificate"])
        REPORT["generator_controls"].append({"id": record["id"], **encode(checked)})
    REPORT["case_counts"] = {"HD_cases": len(expected), "HD_modes_per_case": 2,
                            "HD_endpoints_each": 193, "HD_closed_cells_each": 192,
                            "controls": len(control_source), "generator_controls": len(primary["generator_controls"])}
    budget()


def main():
    output = LEAF / "raw/REFERENCE_RESULTS.json"
    if output.exists():
        print(json.dumps({"status": "REFUSED_EXISTING_OUTPUT", "path": str(output)}), file=sys.stderr)
        return 2
    try:
        with localcontext() as context:
            context.prec = 160
            execute()
    except Exception as exc:
        check("reference_execution_exception", False,
              {"class": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
    REPORT["check_count"] = len(REPORT["checks"])
    REPORT["failure_count"] = sum(row["status"] == "FAIL" for row in REPORT["checks"])
    REPORT["status"] = "PASS" if REPORT["failure_count"] == 0 and REPORT["failed_components"] == 0 else "FAIL"
    REPORT["finished_utc"] = datetime.now(timezone.utc).isoformat()
    REPORT["internal_CPU_before_serialization_s"] = cpu_seconds()
    REPORT["internal_wall_before_serialization_s"] = time.monotonic() - WALL_START
    REPORT["complete_process_CPU_authority"] = "Externally measured complete OS process, including imports and serialization."
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(encode(REPORT), stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"status": REPORT["status"], "checks": REPORT["check_count"],
                      "failed": REPORT["failure_count"], "component_comparisons": REPORT["component_comparisons"],
                      "failed_components": REPORT["failed_components"]}))
    return 0 if REPORT["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
