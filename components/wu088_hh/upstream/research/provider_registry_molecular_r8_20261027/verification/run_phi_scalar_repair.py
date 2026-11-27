#!/usr/bin/env python3
"""One fixed exact-rational re-adjudication of the saved native9 phi bound.

No production import, exponential evaluation, ODE, prior runner, or retry.
The original failed reference remains unchanged. Full CPU is wrapper-owned.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import time
import traceback
from datetime import datetime, timezone
from fractions import Fraction
from math import factorial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw/PHI_SCALAR_REPAIR_RESULTS.json"
CONTRACT = ROOT / "verification/PHI_SCALAR_REPAIR_CONTRACT.json"
PRIMARY = ROOT / "raw/PRIMARY_RESULTS.json"
REFERENCE = ROOT / "raw/REFERENCE_RESULTS.json"
PRIMARY_SHA = "520110d1cae1677491aecd7216621c25f1098470c939ee027d5df3bde183686b"
REFERENCE_SHA = "da699b9a8b53389e3d222f34a5a421cd88ce17787bde69cc2e9bed5fb15409df"
CORE_SHA = "3a415e8ccc76669a95bec30aa52fc1f1ad867cff1fd9fcca66734fb71872fba3"
INPUT_SHA = "b47d561f1dc77c42a16544df0f59066b17d1bf8a50430a3ac5ba25845068e84c"
PRIMARY_RUNNER_SHA = "19aa784543bf75343e70ba76f9696cca0ecce7396e03d2c5c4206827dcf8250a"
REFERENCE_RUNNER_SHA = "e0d4d88e367413b1e72a88c2d25b223f69ea0c37a916b7b40c610df78e0c4c2f"
R6_SHA = "1a3b55f7c14a64a10a651de2df7b7f7d2df24d0b9e809b729f32d73377c90e84"
R7_SHA = "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15"
R7_CORE_SHA = "002a66a30961b21e566a940462468c9ea8e1bc868d98549d3ea79d164c239957"
CASE = "saved_native_nine_state_K_conditional_feedback"
FAILED_CHECK = CASE + ": phi factor"
DELTA = "180925139433306555349329664076074856020734351040063381311652475012364265062400/381278994305842111336547231457422955269255660722928784591943370443365273692999"
FIXED_B = [
    ["89999999999999999960983035416324981333019/25000000000000000000000000000000000000010000000",
     "7136972085547229927108412996433070443666400000000000000000000001/2500000000000000000000000000000000000001000000000000000000000000000000"],
    ["1/1250000", "-1/20000000"],
]
FIXED_LO = "170141179423685480793786875825819006271/170141183460469231731687303715884105728"
FIXED_HI = "340282358847370961587573751651638012593/340282366920938463463374607431768211456"
FIXED_PHI = "315373730542023470928911335895078125/664613997892457936451903530140172288"
CHECKS = []


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def Q(value):
    if isinstance(value, (bool, float)):
        raise ValueError("Only exact rational inputs are admitted")
    return Fraction(value)


def check(name, condition, evidence=None):
    CHECKS.append({"name": name, "status": "PASS" if condition else "FAIL",
                   "evidence": evidence or {}})
    if not condition:
        raise ValueError(name)


def run(report):
    contract_raw = CONTRACT.read_bytes()
    contract = json.loads(contract_raw)
    report["contract_sha256"] = sha(contract_raw)
    check("01 contract schema", isinstance(contract, dict) and
          contract.get("schema") == "WU_R8_PHI_SCALAR_REPAIR_CONTRACT_V1")

    primary_raw, reference_raw = PRIMARY.read_bytes(), REFERENCE.read_bytes()
    report["sources"] = {
        "primary": {"path": "raw/PRIMARY_RESULTS.json", "sha256": sha(primary_raw), "bytes": len(primary_raw)},
        "reference": {"path": "raw/REFERENCE_RESULTS.json", "sha256": sha(reference_raw), "bytes": len(reference_raw)},
    }
    check("02 primary raw bytes", sha(primary_raw) == PRIMARY_SHA and len(primary_raw) == 2194159)
    check("03 reference raw bytes", sha(reference_raw) == REFERENCE_SHA and len(reference_raw) == 1739360)
    primary, reference = json.loads(primary_raw), json.loads(reference_raw)
    check("04 primary fixed status and provenance",
          primary["status"] == "PASS" and primary["check_count"] == 237 and primary["failure_count"] == 0
          and primary["runner_sha256"] == PRIMARY_RUNNER_SHA
          and primary["core_sha256"] == CORE_SHA and primary["input_sha256"] == INPUT_SHA
          and primary["source_sha256"]["R6_primary"] == R6_SHA
          and primary["source_sha256"]["R7_primary"] == R7_SHA
          and primary["source_sha256"]["R7_core"] == R7_CORE_SHA)
    original_checks = reference["checks"]
    failed = [item for item in original_checks if item["status"] == "FAIL"]
    check("05 reference fixed failure summary and provenance",
          reference["status"] == "FAIL" and reference["check_count"] == len(original_checks) == 727
          and reference["failure_count"] == len(failed) == 1
          and reference["component_comparison_count"] == sum(item["component_comparisons"] for item in original_checks) == 22659
          and reference["failed_component_count"] == sum(item["failed_components"] for item in original_checks) == 1
          and reference["script_sha256"] == REFERENCE_RUNNER_SHA
          and reference["R8_primary_sha256"] == PRIMARY_SHA and reference["R8_primary_bytes"] == len(primary_raw))
    failure = failed[0]
    check("06 exactly one preserved failed component",
          failure["name"] == FAILED_CHECK and failure["component_comparisons"] == failure["failed_components"] == 1
          and len(failure["evidence"]["first_failures"]) == 1)
    report["original_failure"] = failure
    check("07 original strict tolerance unchanged",
          reference["tolerances"]["arithmetic_upper_scaled"] == "1e-30"
          and reference["tolerances"]["arithmetic_lower_scaled"] == "1e-60"
          and failure["evidence"]["policy"] == "arithmetic")
    operand = failure["evidence"]["first_failures"][0]
    recorded_gap = Q(operand["difference"])
    old_threshold = Fraction(1, 10**30)
    check("08 recorded difference exceeds original threshold",
          operand["index"] == 0 and recorded_gap > old_threshold
          and all(Q(failure["evidence"][key]) == recorded_gap
                  for key in ("min_difference", "max_difference", "max_absolute_difference")))

    cases = [item for item in primary["hd_cases"] if item["id"] == CASE]
    check("09 single fixed native case", len(cases) == 1 and len(primary["hd_cases"]) == 4)
    cert = cases[0]["certificate"]
    binding = cert["kernel"]["binding"]
    check("10 native source binding and declared grid",
          cert["B"] == FIXED_B and cert["delta"] == DELTA and cert["cells"] == 192
          and cert["baseline_expected_sha256"] == R7_SHA
          and binding["family_id"] == "R6_native100K_paraH2_interval_family"
          and binding["source_sha256"] == R6_SHA
          and binding["state_ids"] == ["HD_state_" + str(i) for i in range(9)]
          and binding["generator_scope"] == "nominal_K"
          and binding["norm"] == "l1_on_kerP"
          and all(binding[key] is True for key in ("uniform_all_starts", "nonexpansive", "same_family_composition")))
    factors = cert["coarse_factors"]
    check("11 factor metadata and fixed saved values",
          factors["d"] == "-1/20000000" and factors["delta"] == DELTA
          and factors["branch"] == "negative_d" and factors["bits"] == 128 and factors["degree"] == 48
          and factors["dependency_sha256"] == R7_CORE_SHA
          and factors["negative_exp_interval"] == [FIXED_LO, FIXED_HI]
          and factors["e_upper"] == FIXED_HI and factors["phi_upper"] == FIXED_PHI)
    d, delta, p = Q(factors["d"]), Q(factors["delta"]), Q(factors["phi_upper"])
    lo, hi = (Q(value) for value in factors["negative_exp_interval"])
    x = -d * delta
    scale = 2**128
    quantum = Fraction(1, scale)
    check("12 positive decay argument in alternating domain", d < 0 and delta > 0 and 0 < x < 1)
    check("13 ordered source exponential interval", 0 < lo <= hi <= 1 and Q(factors["e_upper"]) == hi)
    check("14 source interval width", hi - lo == Fraction(51, scale))
    unrounded = (1 - lo) / (-d)
    scaled = unrounded * scale
    numerator_up = -((-scaled.numerator) // scaled.denominator)
    check("15 outward phi reconstruction exact", p == Fraction(numerator_up, scale) and 0 <= p - unrounded < quantum)
    slack = (hi - lo) / (-d) + quantum
    check("16 dyadic quantum and analytic amplification budget", slack == Fraction(1020000001, scale))

    # For 0 < x < 1, t_k = delta*x^k/(k+1)! decreases strictly.
    # The alternating-series theorem gives S_9 <= phi <= S_8.
    terms = [delta * x**k / factorial(k + 1) for k in range(10)]
    check("17 positive decreasing alternating terms", all(t > 0 for t in terms)
          and all(terms[k + 1] < terms[k] for k in range(9)))
    upper = sum(((-1)**k * terms[k] for k in range(9)), Fraction(0))
    lower = sum(((-1)**k * terms[k] for k in range(10)), Fraction(0))
    width = upper - lower
    check("18 lower and upper partial sum order and gap", 0 < lower < upper
          and width == delta * x**9 / factorial(10))
    check("19 saved phi dominates exact upper partial sum", p >= upper,
          {"saved_minus_exact_upper": p - upper})
    check("20 saved phi slack is within source-induced analytic budget", p - lower <= slack + width,
          {"saved_minus_exact_lower": p - lower, "analytic_budget": slack, "bracket_width": width})
    check("21 exact positive slack explains original closeness failure", p < 1 and p - upper > old_threshold,
          {"rigorous_lower_on_true_slack": p - upper, "original_upper_tolerance": old_threshold})
    ref_cases = [item for item in reference["hd_cases"] if item["id"] == CASE]
    check("22 original serialized operands bind the same saved scalar",
          len(ref_cases) == 1 and Q(ref_cases[0]["independent_Decimal80"]["phi"]) == Q(operand["reference"])
          and abs(p - Q(operand["production"])) <= Fraction(1, 10**79),
          {"printing_only_bound": "1e-79; not the scientific acceptance criterion"})
    report["exact_scalar"] = {
        "case": CASE, "d": d, "delta": delta, "x": x,
        "saved_phi_upper": p, "saved_exp_interval": [lo, hi], "interval_width": hi-lo,
        "dyadic_quantum": quantum, "unrounded_phi_upper": unrounded,
        "upper_partial_degree": 8, "lower_partial_degree": 9,
        "positive_terms_k0_through_k9": terms,
        "exact_phi_lower": lower, "exact_phi_upper": upper, "bracket_width": width,
        "saved_minus_exact_upper": p-upper, "saved_minus_exact_lower": p-lower,
        "source_induced_slack_budget": slack,
        "original_closeness_threshold": old_threshold, "original_recorded_gap": recorded_gap,
        "theorem": "For 0<x<1, phi=delta*sum_{k>=0}(-x)^k/(k+1)! lies between odd S9 and even S8.",
    }
    check("23 original raw identities unchanged after scalar evaluation",
          sha(PRIMARY.read_bytes()) == PRIMARY_SHA and sha(REFERENCE.read_bytes()) == REFERENCE_SHA)


def main():
    if OUT.exists():
        print('{"status":"FAIL","reason":"create-only output already exists"}')
        return 2
    wall0 = time.monotonic()
    report = {
        "schema": "WU_R8_PHI_SCALAR_REPAIR_RESULT_V1",
        "run_id": "WU_R8_PHI_SCALAR_REPAIR_01", "started_utc": utc(),
        "script_sha256": sha(Path(__file__).read_bytes()), "checks": CHECKS,
        "execution": {"new_targeted_scalar_evaluations": 1, "CPU_limit_s": 10,
                      "wrapper_full_CPU_authoritative": True,
                      "arithmetic": "Exact Fraction alternating integral-series bracket; fixed degrees8/9",
                      "production_imports": 0, "exponential_evaluations": 0, "new_ODE_runs": 0,
                      "prior_primary_reruns": 0, "prior_reference_reruns": 0, "old_science_replay": 0,
                      "GITHUB_SHA": os.environ.get("GITHUB_SHA"),
                      "GITHUB_RUN_ID": os.environ.get("GITHUB_RUN_ID"),
                      "observed_RLIMIT_CPU": list(resource.getrlimit(resource.RLIMIT_CPU))},
        "scope": {"changed_core": False, "changed_primary": False, "changed_original_reference": False,
                  "blanket_tolerance_change": False, "physical_consumer_admitted": False,
                  "global_remaining": None, "full_historical_CPU": None,
                  "original_reference_status": "FAIL_PRESERVED",
                  "acceptance": "Only the original native phi bound is re-adjudicated by exact enclosure."},
    }
    try:
        run(report)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        cpu = usage.ru_utime + usage.ru_stime
        check("24 process CPU before serialization", cpu <= 10, {"seconds": cpu, "full_CPU": "external wrapper"})
    except Exception as exc:
        CHECKS.append({"name": "preserved exception", "status": "FAIL",
                       "evidence": {"message": str(exc), "traceback": traceback.format_exc()}})
    usage = resource.getrusage(resource.RUSAGE_SELF)
    report.update(check_count=len(CHECKS), failure_count=sum(item["status"] == "FAIL" for item in CHECKS),
                  process_CPU_before_serialization_s=usage.ru_utime + usage.ru_stime,
                  wall_before_serialization_s=time.monotonic() - wall0,
                  finished_utc_before_serialization=utc(),
                  counts_are_not_distinct_physical_scenarios=True)
    report["status"] = "PASS" if report["failure_count"] == 0 and len(CHECKS) == 24 else "FAIL"
    report["adjudication"] = ("SAVED_PHI_IS_RIGOROUS_UPPER; ORIGINAL_CLOSENESS_FAILURE_RECLASSIFIED"
                              if report["status"] == "PASS" else "NOT_RESOLVED")
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, ensure_ascii=True, default=str, allow_nan=False) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "check_count", "failure_count", "adjudication")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
