#!/usr/bin/env python3
"""R9 independent Decimal100/Gaussian reference.

No production imports, no old kernel/factor evaluation, no ODE.
The external process wrapper measures full CPU including imports/serialization.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time
import traceback
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 100
ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT.parent
REPO = ROOT.parents[1]
OUT = ROOT / "raw/REFERENCE_RESULTS.json"
R8PATH = RESEARCH / "provider_registry_molecular_r8_20261027/raw/PRIMARY_RESULTS.json"
SAVEDPATH = RESEARCH / "provider_registry_molecular_r7_20261027/raw/REFERENCE_RESULTS.json"
R8SHA = "520110d1cae1677491aecd7216621c25f1098470c939ee027d5df3bde183686b"
SAVEDSHA = "e403c7803c080fd4f26be71a93b782b02d874f80ef11c85a706bea71e2a743cd"
ZERO, ONE = Decimal(0), Decimal(1)
EPS = ONE / Decimal(2**128)
DECIMAL_GUARD = Decimal("1e-80")
CHECKS = []


class StopRecorded(Exception):
    pass


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def Q(x):
    if isinstance(x, (bool, float)):
        raise ValueError("Exact scalar required")
    return Fraction(x)


def dec(x):
    if isinstance(x, Decimal):
        if not x.is_finite():
            raise ValueError("Nonfinite Decimal")
        return x
    x = Q(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def pair(x):
    if not isinstance(x, (list, tuple)) or len(x) != 2:
        raise ValueError("Pair required")
    return [dec(v) for v in x]


def flat(x):
    if isinstance(x, (list, tuple)):
        for v in x:
            yield from flat(v)
    else:
        yield x


def exact_equal(a, b):
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return (
            isinstance(a, (list, tuple))
            and isinstance(b, (list, tuple))
            and len(a) == len(b)
            and all(exact_equal(x, y) for x, y in zip(a, b))
        )
    return Q(a) == Q(b)


def parse(raw):
    def reject(x):
        raise ValueError("Nonfinite JSON: " + x)
    return json.loads(raw, parse_float=Decimal, parse_constant=reject)


def record(name, ok, evidence=None, components=1, failed=None):
    CHECKS.append({
        "name": name,
        "status": "PASS" if ok else "FAIL",
        "component_comparisons": components,
        "failed_components": (0 if ok else components) if failed is None else failed,
        "evidence": evidence or {},
    })


def require(ok, name, evidence=None):
    record(name, bool(ok), evidence)
    if not ok:
        raise StopRecorded(name)


def compare(name, actual, reference, budget):
    aa, rr, bb = list(flat(actual)), list(flat(reference)), list(flat(budget))
    if not (len(aa) == len(rr) == len(bb)):
        record(name, False, {"lengths": [len(aa), len(rr), len(bb)]})
        return
    failures = []
    count = 0
    min_diff, max_diff, max_budget = None, None, ZERO
    for i, (a, r, b) in enumerate(zip(aa, rr, bb)):
        a, r, b = dec(a), dec(r), dec(b)
        guard = DECIMAL_GUARD * max(ONE, abs(a), abs(r), abs(b))
        difference = a - r
        min_diff = difference if min_diff is None else min(min_diff, difference)
        max_diff = difference if max_diff is None else max(max_diff, difference)
        max_budget = max(max_budget, b)
        if b < 0 or not -guard <= difference <= b + guard:
            count += 1
            if len(failures) < 12:
                failures.append({
                    "index": i, "produced": a, "reference": r,
                    "difference": difference, "rounding_budget": b,
                    "Decimal100_guard": guard,
                })
    record(name, count == 0, {
        "min_difference": min_diff,
        "max_difference": max_diff,
        "max_rounding_budget": max_budget,
        "first_failures": failures,
        "policy": "one-sided dyadic128 propagation plus independent Decimal100 guard",
    }, len(aa), count)


def containment(name, actual, upper):
    aa, uu = list(flat(actual)), list(flat(upper))
    if len(aa) != len(uu):
        record(name, False, {"lengths": [len(aa), len(uu)]})
        return
    failures, count, worst = [], 0, None
    for i, (a, u) in enumerate(zip(aa, uu)):
        a, u = dec(a), dec(u)
        tol = Decimal("2e-12") + Decimal("2e-10") * max(abs(a), abs(u))
        excess = a - u - tol
        worst = excess if worst is None else max(worst, excess)
        if excess > 0:
            count += 1
            if len(failures) < 12:
                failures.append({
                    "index": i, "actual": a, "upper": u, "tolerance": tol,
                })
    record(name, count == 0, {
        "max_excess_after_tolerance": worst,
        "first_failures": failures,
        "scope": "Reused binary64 sample corroboration, not a new continuous ODE enclosure",
    }, len(aa), count)


def immutable(path, expected, label, report):
    raw = path.read_bytes()
    got = sha(raw)
    require(got == expected, label + ": exact original bytes",
            {"expected": expected, "actual": got, "bytes": len(raw)})
    report["sources"][label] = {
        "path": str(path.relative_to(REPO)),
        "sha256": got, "bytes": len(raw),
    }
    return parse(raw)


def check_freeze(report):
    path = ROOT / "raw/PREEXECUTION_FREEZE.json"
    raw = path.read_bytes()
    freeze = parse(raw)
    require(freeze.get("status") == "PASS",
            "Actual preexecution freeze has PASS status")
    entries = freeze.get("files")
    require(isinstance(entries, list) and bool(entries),
            "Nonempty actual preexecution freeze")
    seen = set()
    resolved_frozen_paths = set()
    for item in entries:
        p = item["path"]
        require(isinstance(p, str) and not Path(p).is_absolute()
                and ".." not in Path(p).parts and p not in seen,
                "Safe unique frozen path: " + str(p))
        seen.add(p)
        source = REPO / p if p.startswith("research/") else ROOT / p
        source_bytes = source.read_bytes()
        got = sha(source_bytes)
        require(got == item["sha256"] and len(source_bytes) == item["bytes"],
                "Frozen bytes: " + p,
                {"expected": item["sha256"], "actual": got,
                 "expected_bytes": item["bytes"], "actual_bytes": len(source_bytes)})
        resolved_frozen_paths.add(source.resolve())
    required = {
        (ROOT / "src/causal_resolvent.py").resolve(),
        (ROOT / "verification/PRIMARY_INPUT.json").resolve(),
        (ROOT / "verification/run_primary.py").resolve(),
        Path(__file__).resolve(),
    }
    require(required.issubset(resolved_frozen_paths),
            "Core, input, primary and independent reference are all frozen")
    report["preexecution_freeze_sha256"] = sha(raw)


def reference_sweep(cert, capped):
    a, b = pair(cert["B"][0])
    c, d = pair(cert["B"][1])
    gr, ge = pair(cert["g"])
    R0, E0 = pair(cert["initial"])
    dt = dec(cert["delta"])
    h = [dec(x) for x in cert["kernel"]["h"]]
    e = dec(cert["coarse_factors"]["e_upper"])
    phi = dec(cert["coarse_factors"]["phi_upper"])
    N = cert["cells"]
    aq, bq = map(Q, cert["B"][0])
    cq = Q(cert["B"][1][0])
    dtq, phiq = Q(cert["delta"]), Q(cert["coarse_factors"]["phi_upper"])
    exact_D = 1 - dtq * aq - dtq * bq * phiq * cq
    if exact_D <= 0:
        raise ValueError("The frozen case has D<=0")
    denom = dec(exact_D)
    # Independent Gaussian elimination: eliminate R, solve E first.
    pivot1 = ONE - dt * a
    off12, off21 = -dt * b, -phi * c
    multiplier = off21 / pivot1
    pivot2 = ONE - multiplier * off12
    if pivot1 <= 0 or pivot2 <= 0:
        raise ValueError("Nonpositive Gaussian pivot")
    powers, power_error = [ONE], [ZERO]
    for _ in range(N):
        powers.append(powers[-1] * e)
        power_error.append(e * power_error[-1] + EPS)
    caps_w = [pair(x) for x in cert["whole_cells"]] if capped else None
    caps_p = [pair(x) for x in cert["endpoints"]] if capped else None
    whole, raw_whole, error_w, error_rw = [], [], [], []
    F, L, error_F, error_L = [], [], [], []
    A_values, B_values, error_A, error_B = [], [], [], []
    raw_ends, ends = [[R0, E0]], [[R0, E0]]
    error_raw_ends, error_ends = [[ZERO, ZERO]], [[ZERO, ZERO]]
    if capped:
        ends[0] = [min(ends[0][k], caps_p[0][k]) for k in range(2)]
    for n in range(N):
        A = h[n] * R0 + dt * sum(
            (h[n-j-1] * F[j] for j in range(n)), ZERO
        ) + dt * gr
        dA = dt * sum(
            (h[n-j-1] * error_F[j] for j in range(n)), ZERO
        ) + EPS
        initial_power = n if d <= 0 else n + 1
        shift = 1 if d <= 0 else 0
        B = powers[initial_power] * E0 + phi * sum(
            (powers[n-j-shift] * L[j] for j in range(n)), ZERO
        ) + phi * ge
        dB = power_error[initial_power] * E0 + phi * sum(
            ((powers[n-j-shift] + power_error[n-j-shift]) * error_L[j]
             + power_error[n-j-shift] * L[j] for j in range(n)), ZERO
        ) + EPS
        raw_E = (B - multiplier * A) / pivot2
        raw_R = (A - off12 * raw_E) / pivot1
        dR = (dA + dt * b * dB) / denom + EPS
        dE = dB + phi * c * dR + EPS
        raw_whole.append([raw_R, raw_E])
        error_rw.append([dR, dE])
        A_values.append(A)
        B_values.append(B)
        error_A.append(dA)
        error_B.append(dB)
        row = [raw_R, raw_E]
        if capped:
            row = [min(row[k], caps_w[n][k]) for k in range(2)]
        whole.append(row)
        error_w.append([dR, dE])
        F.append(a * row[0] + b * row[1] + gr)
        L.append(c * row[0] + ge)
        error_F.append(a * dR + b * dE + EPS)
        error_L.append(c * dR + EPS)
        r_end = h[n+1] * R0 + dt * sum(
            (h[n-j] * F[j] for j in range(n+1)), ZERO
        )
        e_end = powers[n+1] * E0 + phi * sum(
            (powers[n-j] * L[j] for j in range(n+1)), ZERO
        )
        dr_end = dt * sum(
            (h[n-j] * error_F[j] for j in range(n+1)), ZERO
        ) + EPS
        de_end = power_error[n+1] * E0 + phi * sum(
            ((powers[n-j] + power_error[n-j]) * error_L[j]
             + power_error[n-j] * L[j] for j in range(n+1)), ZERO
        ) + EPS
        raw_ends.append([r_end, e_end])
        error_raw_ends.append([dr_end, de_end])
        endpoint = [min(r_end, row[0]), min(e_end, row[1])]
        if capped:
            endpoint = [min(endpoint[k], caps_p[n+1][k]) for k in range(2)]
        ends.append(endpoint)
        error_ends.append([max(dr_end, dR), max(de_end, dE)])
    values = {
        "powers": powers, "A_base": A_values, "B_base": B_values,
        "raw_whole_cells": raw_whole, "whole_cells": whole,
        "F_upper": F, "L_upper": L,
        "raw_endpoints": raw_ends, "endpoints": ends,
    }
    errors = {
        "powers": power_error, "A_base": error_A, "B_base": error_B,
        "raw_whole_cells": error_rw, "whole_cells": error_w,
        "F_upper": error_F, "L_upper": error_L,
        "raw_endpoints": error_raw_ends, "endpoints": error_ends,
    }
    return values, errors, exact_D, {
        "pivot1": pivot1, "pivot2": pivot2,
        "determinant_residual": pivot1 * pivot2 - denom,
    }


def check_mode(name, prod, cert, capped):
    mode = "capped" if capped else "raw"
    label = name + "/" + mode
    N = cert["cells"]
    require(prod["mode"] == mode and prod["cells"] == N,
            label + ": exact mode and dimensions")
    for field in ("B", "g", "delta", "initial"):
        require(exact_equal(prod[field], cert[field]),
                label + ": exact source " + field)
    require(prod["binding"] == cert["kernel"]["binding"],
            label + ": exact source family binding")
    for key in ("e_upper", "phi_upper"):
        require(Q(prod[key]) == Q(cert["coarse_factors"][key]),
                label + ": saved factor " + key)
    values, errors, exact_D, pivots = reference_sweep(cert, capped)
    require(Q(prod["D"]) == exact_D and exact_D > 0,
            label + ": exact determinant", {"D": str(exact_D)})
    require(abs(pivots["determinant_residual"]) <= DECIMAL_GUARD,
            label + ": independent Gaussian determinant", pivots)
    for field in values:
        compare(label + ": " + field, prod[field], values[field], errors[field])
    if capped:
        for field in ("whole_cells", "endpoints"):
            pp, cc = list(flat(prod[field])), list(flat(cert[field]))
            bad = [i for i, (x, y) in enumerate(zip(pp, cc)) if Q(x) > Q(y)]
            record(label + ": exact no-worse " + field,
                   len(pp) == len(cc) and not bad,
                   {"failed_indices": bad[:12]},
                   max(len(pp), len(cc)), len(bad) + abs(len(pp)-len(cc)))
    return {
        "mode": mode, "D": str(exact_D), "Gaussian_pivots": pivots,
        "independent_final_endpoint": values["endpoints"][-1],
        "max_propagated_rounding_budget": max(flat(list(errors.values()))),
        "comparison_fields": list(values),
    }


def exact_controls(name, prod, cert):
    if name not in ("noforcing", "constantforcing", "nilpotent"):
        return
    dt = Q(cert["delta"])
    h = [Q(x) for x in cert["kernel"]["h"]]
    R0, E0 = map(Q, cert["initial"])
    gr, ge = map(Q, cert["g"])
    force = gr + Q(cert["B"][0][1]) * E0
    N = cert["cells"]
    whole, endpoints = [], [[R0, E0]]
    for n in range(N):
        rw = h[n] * R0 + dt * force * (
            1 + sum((h[k] for k in range(n)), Fraction(0))
        )
        ew = E0 + dt * ge * (n+1)
        re = h[n+1] * R0 + dt * force * sum(
            (h[k] for k in range(n+1)), Fraction(0)
        )
        whole.append([rw, ew])
        endpoints.append([min(re, rw), ew])
    require(exact_equal(prod["whole_cells"], whole),
            name + ": independent exact closed whole-cell formula")
    require(exact_equal(prod["endpoints"], endpoints),
            name + ": independent exact closed endpoint formula")


def saved_samples(name, case, cert, prod):
    require(case["id"] == "HD:" + name
            and case["physical_consumer_admitted"] is False,
            name + ": retained trajectory identity")
    require(len(case["times"]) == len(case["R_E"]) == 193,
            name + ": retained 193 clocks")
    dt = dec(cert["delta"])
    bad = []
    max_error = ZERO
    for i, t in enumerate(case["times"]):
        error = abs(dec(t) - Decimal(i) * dt)
        tol = Decimal("5e-14") + Decimal("5e-15") * abs(Decimal(i) * dt)
        max_error = max(max_error, error)
        if error > tol:
            bad.append(i)
    record(name + ": retained clock agreement", not bad,
           {"maximum_error": max_error, "failed_indices": bad[:12]},
           193, len(bad))
    for mode in ("raw", "capped"):
        result = prod[mode]
        containment(name + "/" + mode + ": saved endpoint samples",
                    case["R_E"], result["endpoints"])
        actual, upper = [], []
        for n in range(192):
            actual.extend([case["R_E"][n], case["R_E"][n+1]])
            upper.extend([result["whole_cells"][n]] * 2)
        containment(name + "/" + mode + ": saved closed-cell boundaries",
                    actual, upper)


def run(report):
    require(len(sys.argv) == 1, "No adaptive reference arguments")
    check_freeze(report)
    old = immutable(R8PATH, R8SHA, "R8_primary", report)
    saved = immutable(SAVEDPATH, SAVEDSHA, "R7_saved_reference", report)
    require(old["failure_count"] == 0 and old["status"].startswith("PASS"),
            "R8 primary actual acceptance")
    require(saved["failure_count"] == 0 and saved["status"] == "PASS",
            "R7 saved reference actual acceptance")
    raw = (ROOT / "raw/PRIMARY_RESULTS.json").read_bytes()
    primary = parse(raw)
    report["primary_sha256"] = sha(raw)
    report["primary_bytes"] = len(raw)
    require(primary["failure_count"] == 0 and primary["status"] == "PASS",
            "R9 primary actual PASS")
    require(primary["core_sha256"] ==
            sha((ROOT / "src/causal_resolvent.py").read_bytes()),
            "R9 primary/core source identity")
    require(primary["input_sha256"] ==
            sha((ROOT / "verification/PRIMARY_INPUT.json").read_bytes()),
            "R9 primary/input source identity")
    for group, count, cells in (("hd_cases", 4, 192), ("controls", 5, 8)):
        source_rows = old[group]
        produced_rows = primary[group]
        require(len(source_rows) == len(produced_rows) == count,
                group + ": exact fixed count")
        require([x["id"] for x in source_rows] ==
                [x["id"] for x in produced_rows],
                group + ": exact fixed order")
        for source, produced in zip(source_rows, produced_rows):
            name, cert = source["id"], source["certificate"]
            require(cert["cells"] == cells, name + ": fixed source grid")
            modes = [
                check_mode(name, produced[mode], cert, mode == "capped")
                for mode in ("raw", "capped")
            ]
            if group == "controls":
                exact_controls(name, produced["raw"], cert)
            else:
                trajectory = next(x for x in saved["hd_cases"]
                                  if x["id"] == "HD:" + name)
                saved_samples(name, trajectory, cert, produced)
            report[group].append({
                "id": name, "modes": modes,
                "physical_consumer_admitted": False,
            })
    require(len(report["hd_cases"]) == 4 and len(report["controls"]) == 5,
            "Every frozen case completed")


def main():
    start = time.monotonic()
    if OUT.exists():
        print('{"status":"FAIL","reason":"create-only reference output exists"}')
        return 2
    report = {
        "schema": "WU_R9_INDEPENDENT_REFERENCE_RESULTS_V1",
        "run_id": "WU_R9_REFERENCE_01",
        "started_utc": utc(),
        "script_sha256": sha(Path(__file__).read_bytes()),
        "sources": {}, "hd_cases": [], "controls": [], "checks": CHECKS,
        "execution": {
            "reference_runs": 1, "CPU_limit_s": 60,
            "external_wrapper_full_CPU_authoritative": True,
            "production_imports": 0, "old_factor_or_kernel_calls": 0,
            "new_ODE_runs": 0, "old_science_replay": 0,
            "arithmetic": "Decimal100 direct convolutions and E-first Gaussian elimination",
            "GITHUB_SHA": os.environ.get("GITHUB_SHA"),
            "GITHUB_RUN_ID": os.environ.get("GITHUB_RUN_ID"),
            "observed_RLIMIT_CPU": list(resource.getrlimit(resource.RLIMIT_CPU)),
        },
        "comparison_contract": {
            "dyadic_unit": str(Fraction(1, 2**128)),
            "rounding_budget": "Recursively propagated per actual rounding site and exact determinant",
            "Decimal100_scaled_guard": str(DECIMAL_GUARD),
            "phi_policy": "Identical saved outward rational input; no fresh exponential or fixed phi-closeness test",
            "trajectory_atol": "2e-12", "trajectory_rtol": "2e-10",
            "trajectory_scope": "Saved binary64 samples, no new continuous-time certificate",
        },
        "scope": {
            "physical_consumer_admitted": False, "physical_IVP": 0,
            "global_remaining": None,
        },
    }
    try:
        run(report)
    except StopRecorded as exc:
        report["stopped_after_recorded_failure"] = str(exc)
    except Exception as exc:
        record("Preserved reference exception", False, {
            "message": str(exc), "traceback": traceback.format_exc(),
        })
    usage = resource.getrusage(resource.RUSAGE_SELF)
    cpu = usage.ru_utime + usage.ru_stime
    record("CPU before serialization", cpu <= 60, {
        "seconds": cpu, "full_process_CPU_authority": "external wrapper",
    })
    report.update(
        check_count=len(CHECKS),
        failure_count=sum(x["status"] == "FAIL" for x in CHECKS),
        component_comparison_count=sum(x["component_comparisons"] for x in CHECKS),
        failed_component_count=sum(x["failed_components"] for x in CHECKS),
        process_CPU_before_serialization_s=cpu,
        wall_before_serialization_s=time.monotonic() - start,
        finished_utc_before_serialization=utc(),
        counts_are_not_distinct_physical_scenarios=True,
    )
    report["status"] = "PASS" if report["failure_count"] == 0 else "FAIL"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x", encoding="utf-8") as f:
        f.write(json.dumps(report, indent=2, default=str,
                           ensure_ascii=True, allow_nan=False) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "check_count", "failure_count",
                       "component_comparison_count", "failed_component_count")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
