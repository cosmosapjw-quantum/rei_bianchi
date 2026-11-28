#!/usr/bin/env python3
"""R10 independent Decimal160 triangular-flow and Euler-Dobrushin reference.

This file never imports the production implementation or previous research
solvers. It reads immutable saved inputs/results. Its matrix exponential is the
unshifted scalar analytic solution, independent of the positive shifted Taylor
algorithm used in production. No ODE or native-source calculation is performed.
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
START_WALL = time.monotonic()
STARTED = datetime.now(timezone.utc).isoformat()
ZERO = Decimal(0)
ONE = Decimal(1)
REPORT = {
    "schema": "WU_R10_INDEPENDENT_REFERENCE_V1",
    "started_utc": STARTED,
    "checks": [],
    "hd_cases": [],
    "controls": [],
    "component_comparisons": 0,
    "failed_components": 0,
    "comparison_failures": [],
    "first_failure": None,
    "scope": {
        "arithmetic": "Decimal160 analytic unshifted triangular exponential",
        "generator_reference": "Exact Fraction stochastic Euler map and pair-column l1 distance",
        "production_imports": 0,
        "old_solver_imports": 0,
        "new_ODE_calls": 0,
        "old_science_replay": 0,
        "physical_consumer_admitted": False,
        "component_counts_are_not_distinct_physical_scenarios": True,
    },
    "versions": {"Python": platform.python_version(), "platform": platform.platform()},
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fq(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("exact reference input must be an integer or rational string")
    if not isinstance(value, (str, int, Fraction)):
        raise TypeError("unsupported exact scalar")
    return Fraction(value)


def dec(value):
    q = fq(value)
    return Decimal(q.numerator) / Decimal(q.denominator)


def matrix_dec(values):
    return [[dec(x) for x in row] for row in values]


def serial_vector(v):
    return [str(x) for x in v]


def serial_matrix(m):
    return [serial_vector(row) for row in m]


def cpu_seconds():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def budget_check():
    if cpu_seconds() > 60 or time.monotonic() - START_WALL > 90:
        raise RuntimeError("REFERENCE_RESOURCE_CEILING_EXCEEDED")


def check(name, okay, evidence=None):
    row = {"name": name, "status": "PASS" if okay else "FAIL"}
    if evidence is not None:
        row["evidence"] = evidence
    REPORT["checks"].append(row)
    if not okay and REPORT["first_failure"] is None:
        REPORT["first_failure"] = row.copy()
    return okay


def guard(*values):
    return Decimal("1e-80") * max(ONE, *(abs(x) for x in values))


def compare_components(name, reference, upper, lower=None):
    """Compare same-shaped scalar arrays; record numerical evidence once/group."""
    def flatten(value):
        if isinstance(value, (list, tuple)):
            out = []
            for v in value:
                out.extend(flatten(v))
            return out
        return [value]

    rv = flatten(reference)
    uv = flatten(upper)
    lv = flatten(lower) if lower is not None else None
    if not check(name + ":shape", len(rv) == len(uv) and (lv is None or len(lv) == len(rv)),
                 {"reference": len(rv), "upper": len(uv), "lower": None if lv is None else len(lv)}):
        return
    failures = []
    max_upper_excess = ZERO
    max_lower_excess = ZERO
    max_upper_slack = ZERO
    min_upper_slack = None
    max_width = ZERO
    for k, (r, u) in enumerate(zip(rv, uv)):
        ell = lv[k] if lv is not None else None
        eps = guard(r, u, *(() if ell is None else (ell,)))
        positive = u >= ZERO and (ell is None or ell >= ZERO)
        okay = positive and r <= u + eps and (ell is None or ell <= r + eps)
        REPORT["component_comparisons"] += 1
        slack = u - r
        max_upper_slack = max(max_upper_slack, slack)
        min_upper_slack = slack if min_upper_slack is None else min(min_upper_slack, slack)
        max_upper_excess = max(max_upper_excess, r - u)
        if ell is not None:
            max_lower_excess = max(max_lower_excess, ell - r)
            max_width = max(max_width, u - ell)
            okay = okay and ell <= u
        if not okay:
            REPORT["failed_components"] += 1
            row = {"index": k, "reference": str(r), "upper": str(u),
                   "lower": None if ell is None else str(ell), "guard": str(eps),
                   "nonnegative": positive}
            if len(failures) < 8:
                failures.append(row)
            if len(REPORT["comparison_failures"]) < 32:
                REPORT["comparison_failures"].append({"group": name, **row})
    check(name, not failures, {
        "components": len(rv), "failed_examples": failures,
        "max_reference_above_upper": str(max_upper_excess),
        "max_lower_above_reference": str(max_lower_excess),
        "min_upper_minus_reference": str(min_upper_slack or ZERO),
        "max_upper_minus_reference": str(max_upper_slack),
        "max_interval_width": str(max_width),
        "criterion": "lower <= Decimal160 reference <= upper, allowing 1e-80*max(1,abs(values)); all reported bounds nonnegative",
    })


def scalar_phi(q, t):
    """Integral exp(q*s) ds, exact zero-branch selected before Decimal conversion."""
    q = fq(q)
    if q == 0:
        return t
    z = dec(q)
    return ((z * t).exp() - ONE) / z


def analytic_flow(lam, c, d, g_r, g_e, delta, *, whole=False):
    """Unshifted analytic augmented triangular exponential; no matrix series."""
    lam, c, d, g_r, g_e = map(fq, (lam, c, d, g_r, g_e))
    t = dec(delta)
    a = Fraction(0) if whole else -lam
    b = max(d, Fraction(0)) if whole else d
    aa, bb = dec(a), dec(b)
    ea, eb = (aa * t).exp(), (bb * t).exp()
    pa, pb = scalar_phi(a, t), scalar_phi(b, t)
    # J = integral exp(b*(t-s))*exp(a*s) ds.
    j = t * ea if a == b else (ea - eb) / dec(a - b)
    # Q = integral exp(b*(t-s))*phi(a,s) ds.
    if a != 0:
        q = (j - pb) / aa
    elif b != 0:
        q = (eb - ONE - bb * t) / (bb * bb)
    else:
        q = t * t / Decimal(2)
    cc, rr, ee = dec(c), dec(g_r), dec(g_e)
    result = [[ea, ZERO, rr * pa],
              [cc * j, eb, cc * rr * q + ee * pb],
              [ZERO, ZERO, ONE]]
    return result


def advance(matrix, state):
    z = [state[0], state[1], ONE]
    return [sum((matrix[i][j] * z[j] for j in range(3)), ZERO) for i in range(2)]


def ideal_sweep(parameters, initial, cells, delta, cap=None):
    flow = analytic_flow(**parameters, delta=delta)
    whole_flow = analytic_flow(**parameters, delta=delta, whole=True)
    state = [dec(x) for x in initial]
    if cap is not None:
        state = [min(x, dec(y)) for x, y in zip(state, cap["endpoints"][0])]
    endpoints = [state]
    whole = []
    for k in range(cells):
        wc = advance(whole_flow, state)
        ep = advance(flow, state)
        if cap is not None:
            wc = [min(x, dec(y)) for x, y in zip(wc, cap["whole_cells"][k])]
            ep = [min(x, wc[j], dec(cap["endpoints"][k + 1][j])) for j, x in enumerate(ep)]
        whole.append(wc)
        endpoints.append(ep)
        state = ep
    return {"flow": flow, "whole_flow": whole_flow, "endpoints": endpoints, "whole_cells": whole}


def euler_coefficient(generator):
    """Independent exact zero-sum operator norm of an explicit Euler matrix."""
    a = [[fq(x) for x in row] for row in generator]
    n = len(a)
    if n == 0 or any(len(row) != n for row in a):
        raise ValueError("generator must be nonempty square")
    if any(sum(a[i][j] for i in range(n)) != 0 for j in range(n)):
        raise ValueError("generator columns do not sum exactly to zero")
    if any(a[i][j] < 0 for i in range(n) for j in range(n) if i != j):
        raise ValueError("off-diagonal generator entry is negative")
    if n == 1:
        return {"lambda": Fraction(0), "h": Fraction(1, 4), "delta": Fraction(1),
                "pair_l1": [], "singleton_convention": "lambda=0 on trivial zero-sum space"}
    departure = max(-a[j][j] for j in range(n))
    offdiag = max(a[i][j] for i in range(n) for j in range(n) if i != j)
    h = Fraction(1, 4) / (1 + departure + offdiag)
    p = [[(Fraction(1) if i == j else Fraction(0)) + h * a[i][j]
          for j in range(n)] for i in range(n)]
    if any(x < 0 for row in p for x in row):
        raise ArithmeticError("Euler matrix not nonnegative")
    pairs = [(i, j, sum(abs(p[k][i] - p[k][j]) for k in range(n)))
             for i in range(n) for j in range(i + 1, n)]
    delta = max(row[2] for row in pairs) / 2
    return {"lambda": (1 - delta) / h, "h": h, "delta": delta,
            "pair_l1": [[i, j, str(v)] for i, j, v in pairs]}


def independent_generator(case):
    k = [[fq(x) for x in row] for row in case["K"]]
    pi = [fq(x) for x in case["pi"]]
    destruction = [fq(x) for x in case["destruction"]]
    n = len(pi)
    if sum(pi) != 1 or any(x < 0 for x in pi + destruction):
        raise ValueError("invalid simplex/destruction input")
    h = [[pi[i] * destruction[j] - (destruction[i] if i == j else 0)
          for j in range(n)] for i in range(n)]
    wlo, whi = map(fq, case["density_box"]["w"])
    alo = [[k[i][j] + wlo * h[i][j] for j in range(n)] for i in range(n)]
    ahi = [[k[i][j] + whi * h[i][j] for j in range(n)] for i in range(n)]
    return {"K": k, "H": h, "A_lower": alo, "A_upper": ahi,
            "K_euler": euler_coefficient(k), "H_euler": euler_coefficient(h),
            "lower_euler": euler_coefficient(alo), "upper_euler": euler_coefficient(ahi),
            "w_lower": wlo, "w_upper": whi}


def verify_freeze(config, primary):
    freeze = read_json(LEAF / "raw/PREEXECUTION_FREEZE.json")
    rows = freeze.get("files", [])
    indexed = {row["path"]: row for row in rows}
    required = config["required_frozen_sources"]
    okay = check("frozen_source_status", freeze.get("status") == "PASS", {"status": freeze.get("status")})
    okay = check("frozen_source_membership", set(required).issubset(indexed),
                 {"required": required, "missing": sorted(set(required) - set(indexed))}) and okay
    for path, row in indexed.items():
        p = REPO / path
        found = p.is_file()
        size_ok = found and p.stat().st_size == row["bytes"]
        hash_ok = found and sha(p) == row["sha256"]
        okay = check("frozen_bytes:" + path, size_ok and hash_ok,
                     {"bytes_match": size_ok, "SHA256_match": hash_ok}) and okay
    for field, path in [("core_sha256", config["core_path"]),
                        ("input_sha256", config["primary_input_path"]),
                        ("runner_sha256", config["primary_runner_path"])]:
        same = path in indexed and primary.get(field) == indexed[path]["sha256"]
        okay = check("primary_frozen_binding:" + field, same,
                     {"actual": primary.get(field), "expected": indexed.get(path, {}).get("sha256")}) and okay
    if not okay:
        raise RuntimeError("FROZEN_SOURCE_IDENTITY_FAILURE")
    REPORT["freeze_sha256"] = sha(LEAF / "raw/PREEXECUTION_FREEZE.json")


def verify_inherited_sources(config):
    for row in config["source_files"]:
        p = REPO / row["path"]
        okay = p.is_file() and p.stat().st_size == row["bytes"] and sha(p) == row["sha256"]
        check("inherited_bytes:" + row["path"], okay,
              {"expected_SHA256": row["sha256"], "expected_bytes": row["bytes"]})
        if not okay:
            raise RuntimeError("INHERITED_INPUT_IDENTITY_FAILURE")


def sample_containment(name, certificate, saved):
    delta = fq(certificate["delta"])
    cells = certificate["cells"]
    times = saved["times"]
    values = saved["R_E"]
    okay_clock = len(times) == cells + 1 and len(values) == cells + 1
    clock_errors = []
    for k, t in enumerate(times):
        exact = k * delta
        ulp = Fraction.from_float(math.ulp(float(exact)))
        error = abs(Fraction.from_float(float(t)) - exact)
        clock_errors.append(error / ulp)
        okay_clock = okay_clock and error <= ulp
    check(name + ":saved_clock_identity", okay_clock,
          {"points": len(times), "cells": cells,
           "relation": "NUMERICAL_IDENTITY of saved binary64 sample clock to exact source-bound rational grid",
           "criterion": "absolute deviation <= one binary64 ULP of exact rational time rounded to binary64",
           "maximum_deviation_ULP": str(max(clock_errors, default=Fraction(0)))})
    if not okay_clock:
        return
    failures = []
    max_excess = ZERO
    for k, row in enumerate(values):
        for j, value in enumerate(row):
            actual = Decimal(str(value))
            upper = dec(certificate["endpoints_upper"][k][j])
            atol, rtol = Decimal("2e-12"), Decimal("2e-10")
            tolerance = atol + rtol * max(abs(actual), abs(upper))
            excess = actual - upper - tolerance
            max_excess = max(max_excess, excess)
            REPORT["component_comparisons"] += 1
            if actual < 0 or excess > 0:
                REPORT["failed_components"] += 1
                if len(failures) < 8:
                    failures.append({"index": k, "component": j, "sample": str(actual),
                                     "upper": str(upper), "tolerance": str(tolerance)})
    check(name + ":saved_sample_containment", not failures,
          {"points": len(times), "components": 2 * len(times), "failed_examples": failures,
           "max_positive_excess_after_tolerance": str(max_excess),
           "criterion": "sample <= upper + 2e-12 + 2e-10*max(abs(sample),abs(upper)); samples are validation evidence only"})


def verify_generator(case_id, source, production):
    own = independent_generator(source)
    names = [("lambda", "lower_euler"), ("lambda_K", "K_euler"),
             ("lambda_H", "H_euler"), ("lambda_at_w_upper", "upper_euler")]
    for field, own_field in names:
        check(case_id + ":Euler_Dobrushin:" + field,
              fq(production[field]) == own[own_field]["lambda"],
              {"expected": str(own[own_field]["lambda"]), "actual": production[field],
               "Euler_h": str(own[own_field]["h"]),
               "Euler_delta_from_half_max_column_l1": str(own[own_field]["delta"])})
    for field, own_field in [("H", "H"), ("A_w_lower", "A_lower"), ("A_w_upper", "A_upper")]:
        check(case_id + ":generator_array:" + field,
              [[fq(x) for x in row] for row in production[field]] == own[own_field])
    separate = own["K_euler"]["lambda"] + own["w_lower"] * own["H_euler"]["lambda"]
    check(case_id + ":separate_sum_value", fq(production["separate_sum_lower"]) == separate,
          {"expected": str(separate), "actual": production["separate_sum_lower"]})
    check(case_id + ":full_generator_vs_separate_sum", own["lower_euler"]["lambda"] >= separate)
    check(case_id + ":w_endpoint_monotonicity", own["upper_euler"]["lambda"] >= own["lower_euler"]["lambda"])
    check(case_id + ":w_box_identity", list(map(fq, production["w_box"])) == [own["w_lower"], own["w_upper"]])
    return own


def verify_matrix(name, artifact, reference):
    lower, upper = matrix_dec(artifact["lower"]), matrix_dec(artifact["upper"])
    check(name + ":matrix_shape", len(lower) == len(upper) == 3 and
          all(len(row) == 3 for row in lower + upper))
    compare_components(name + ":analytic_enclosure", reference, upper, lower)
    check(name + ":dyadic_bits", artifact["bits"] == 128)
    check(name + ":Taylor_degree", artifact["degree"] == 96)


def verify_certificate(name, artifact, parameters, initial, cells, delta, cap=None):
    check(name + ":grid_identity", artifact["cells"] == cells and fq(artifact["delta"]) == fq(delta))
    check(name + ":initial_identity", list(map(fq, artifact["initial"])) == list(map(fq, initial)))
    check(name + ":coefficient_identity", all(fq(artifact["coefficients"][k]) == fq(v)
                                             for k, v in parameters.items()))
    expected = ideal_sweep(parameters, initial, cells, delta, cap=cap)
    verify_matrix(name + ":point_flow", artifact["flow_interval"], expected["flow"])
    verify_matrix(name + ":whole_flow", artifact["whole_flow_interval"], expected["whole_flow"])
    point_upper = [[dec(x) for x in row] for row in artifact["endpoints_upper"]]
    whole_upper = [[dec(x) for x in row] for row in artifact["whole_cells_upper"]]
    check(name + ":output_row_shapes",
          len(point_upper) == cells + 1 and len(whole_upper) == cells and
          all(len(row) == 2 for row in point_upper + whole_upper))
    if cap is None:
        lower = artifact["endpoints_lower"]
        check(name + ":lower_enclosure_present", lower is not None)
        lower = None if lower is None else [[dec(x) for x in row] for row in lower]
    else:
        check(name + ":capped_lower_absent", artifact["endpoints_lower"] is None)
        lower = None
    compare_components(name + ":endpoint_reference", expected["endpoints"], point_upper, lower)
    compare_components(name + ":whole_cell_reference", expected["whole_cells"], whole_upper)
    if cap is None:
        closed = all(whole_upper[k][j] >= point_upper[k][j] for k in range(cells) for j in range(2))
        check(name + ":whole_includes_reported_left_endpoint", closed)
    if cap is not None:
        point_order = all(fq(artifact["endpoints_upper"][k][j]) <= fq(cap["endpoints"][k][j])
                          for k in range(cells + 1) for j in range(2))
        whole_order = all(fq(artifact["whole_cells_upper"][k][j]) <= fq(cap["whole_cells"][k][j])
                          for k in range(cells) for j in range(2))
        check(name + ":same_clock_cap_order", point_order)
        check(name + ":same_cell_cap_order", whole_order)
    final_direct = advance(analytic_flow(**parameters, delta=fq(delta) * cells), [dec(x) for x in initial])
    if cap is None:
        difference = [abs(a - b) for a, b in zip(expected["endpoints"][-1], final_direct)]
        check(name + ":analytic_semigroup_consistency",
              all(x <= guard(a, b) for x, a, b in zip(difference, expected["endpoints"][-1], final_direct)),
              {"absolute_differences": serial_vector(difference)})
    return {"id": name, "endpoint_reference": serial_vector(expected["endpoints"][-1]),
            "whole_cell_final_reference": serial_vector(expected["whole_cells"][-1]),
            "point_flow_reference": serial_matrix(expected["flow"]),
            "whole_flow_reference": serial_matrix(expected["whole_flow"]),
            "points": cells + 1, "cells": cells,
            "reference_construction": "analytic constant-generator semigroup; same-cell and same-clock minima only for capped mode"}


def execute():
    config = read_json(LEAF / "verification/REFERENCE_INPUT.json")
    primary = read_json(REPO / config["primary_result_path"])
    fixed = read_json(REPO / config["primary_input_path"])
    REPORT["input_sha256"] = sha(LEAF / "verification/REFERENCE_INPUT.json")
    REPORT["runner_sha256"] = sha(HERE)
    REPORT["primary_sha256"] = sha(REPO / config["primary_result_path"])
    REPORT["Decimal_precision"] = 160
    check("reference_precision_contract", config["precision_decimal_digits"] == 160)
    verify_freeze(config, primary)
    verify_inherited_sources(config)
    check("primary_result_status", primary.get("status") == "PASS" and primary.get("failure_count") == 0,
          {"status": primary.get("status"), "failure_count": primary.get("failure_count"),
           "preserved_first_failure": primary.get("first_failure")})
    source_input = read_json(REPO / config["source_root"] / "verification/PRIMARY_INPUT.json")
    source_primary = read_json(REPO / config["source_root"] / "raw/PRIMARY_RESULTS.json")
    source_reference = read_json(REPO / config["source_root"] / "raw/REFERENCE_RESULTS.json")
    source_caps = read_json(REPO / config["cap_root"] / "raw/PRIMARY_RESULTS.json")
    inputs = {row["id"]: row for row in source_input["hd_cases"]}
    saved_primary = {row["id"]: row for row in source_primary["hd_cases"]}
    saved_reference = {row["id"].removeprefix("HD:"): row for row in source_reference["hd_cases"]}
    caps = {row["id"]: row["capped"] for row in source_caps["hd_cases"]}
    new_rows = {row["id"]: row for row in primary["hd_cases"]}
    expected_ids = config["expected_HD_ids"]
    check("HD_case_identity", set(new_rows) == set(expected_ids) and len(primary["hd_cases"]) == len(expected_ids),
          {"expected": expected_ids, "actual": list(new_rows)})
    for case_id in expected_ids:
        budget_check()
        inp, old, new, cap = inputs[case_id], saved_primary[case_id], new_rows[case_id], caps[case_id]
        own = verify_generator(case_id, inp, new["generator"])
        p = {key: old["coefficients"][key] for key in ("c", "d", "g_r", "g_e")}
        p["lam"] = str(own["lower_euler"]["lambda"])
        check(case_id + ":top_coefficient_identity", all(fq(new["coefficients"][k]) == fq(v) for k, v in p.items()))
        initial = [old["initial_error"]["R"], old["initial_error"]["E"]]
        delta, cells = cap["delta"], cap["cells"]
        check(case_id + ":immutable_grid_contract",
              cells == config["expected_HD_cells"] and fq(delta) == fq(inp["H"]) / 64 and
              fq(delta) == fq(config["expected_HD_grids"][case_id]["delta"]),
              {"source_R9_delta": delta, "source_R7_H": inp["H"], "cells": cells})
        for mode in ("raw", "capped"):
            artifact = new[mode]
            binding = artifact["binding"]
            metadata_ok = all(binding.get(key) == cap["binding"].get(key)
                              for key in ("clock", "family_id", "state_ids", "norm"))
            metadata_ok = metadata_ok and binding.get("clock") == old["binding"]["clock"]
            check(case_id + ":" + mode + ":source_family_state_clock", metadata_ok,
                  {"clock": binding.get("clock"), "family": binding.get("family_id"),
                   "state_ids": binding.get("state_ids"), "cap_source": config["source_hashes_expected"]["R9_primary"]})
            evidence = verify_certificate(case_id + ":" + mode, artifact, p, initial, cells, delta,
                                          cap=None if mode == "raw" else cap)
            sample_containment(case_id + ":" + mode, artifact, saved_reference[case_id])
            REPORT["hd_cases"].append(evidence)
    fixed_controls = fixed["controls"]
    controls = {row["id"]: row for row in primary["controls"]}
    check("analytic_control_identity",
          len(fixed_controls) == config["expected_control_count"] == len(primary["controls"]) and
          set(controls) == {row["id"] for row in fixed_controls},
          {"expected_count": config["expected_control_count"], "source_ids": [x["id"] for x in fixed_controls],
           "actual_ids": list(controls)})
    for source in fixed_controls:
        budget_check()
        row = controls[source["id"]]
        # Parameters come from the frozen input, never from production arithmetic.
        parameters = {key: source[key] for key in ("lam", "c", "d", "g_r", "g_e")}
        metadata_keys = ("lam", "c", "d", "g_r", "g_e", "delta")
        parameter_identity = all(fq(row["parameters"][key]) == fq(source[key]) for key in metadata_keys)
        parameter_identity = parameter_identity and list(map(fq, row["parameters"]["initial"])) == list(map(fq, source["initial"]))
        parameter_identity = parameter_identity and row["parameters"]["cells"] == source["cells"]
        check(source["id"] + ":fixed_control_parameters", parameter_identity)
        result = verify_certificate("control:" + source["id"], row["raw"], parameters,
                                    source["initial"], source["cells"], source["delta"])
        REPORT["controls"].append(result)
    REPORT["case_counts"] = {"HD_cases": len(expected_ids), "HD_modes_per_case": 2,
                              "analytic_controls": len(fixed_controls),
                              "saved_clock_points_per_HD_mode": 193}
    budget_check()


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
    REPORT["status"] = "PASS" if REPORT["failure_count"] == 0 else "FAIL"
    REPORT["finished_utc"] = datetime.now(timezone.utc).isoformat()
    REPORT["internal_CPU_before_serialization_s"] = cpu_seconds()
    REPORT["internal_wall_before_serialization_s"] = time.monotonic() - START_WALL
    REPORT["complete_process_CPU_authority"] = "Externally measured raw/REFERENCE_PROCESS.json includes complete interpreter and output serialization."
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(REPORT, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"status": REPORT["status"], "checks": REPORT["check_count"],
                      "failed": REPORT["failure_count"], "component_comparisons": REPORT["component_comparisons"],
                      "failed_components": REPORT["failed_components"]}))
    return 0 if REPORT["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
