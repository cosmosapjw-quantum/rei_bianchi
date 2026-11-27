"""Frozen R13 primary campaign. Run only after root's S05 publication freeze.

This runner calls only the new affine-forcing module, keeps every failed
check, and writes one result file before returning a nonzero status on failure.
Its CPU field is internal runner CPU; root records whole OS-process resources.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
from fractions import Fraction

HERE = Path(__file__).resolve().parent
LEAF = HERE.parent
sys.path.insert(0, str(LEAF / "src"))
from affine_convolution import DomainError, derived, run_case, serializable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=LEAF)
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.root.resolve() != LEAF:
        parser.error("--root must match this frozen runner's leaf")
    args.cases = args.cases or args.root / "verification" / "CASES.json"
    args.output = args.output or args.root / "verification" / "PRIMARY_RESULTS.json"
    if args.output.exists():
        parser.error("Output already exists; frozen primary results cannot be overwritten")
    started = time.process_time()
    fixtures = json.loads(args.cases.read_text())
    checks, records, by_id = [], [], {}

    def check(ident, passed, detail=None):
        item = {"id": ident, "status": "PASS" if bool(passed) else "FAIL"}
        if detail is not None:
            item["detail"] = serializable(detail)
        checks.append(item)

    fixture_source_path = HERE / "FIXTURE_SOURCE.json"
    fixture_source_bytes = fixture_source_path.read_bytes()
    fixture_source_sha = hashlib.sha256(fixture_source_bytes).hexdigest()
    fixture_source = json.loads(fixture_source_bytes)
    source_cases = {row["id"]: row for row in fixture_source["cases"]}
    source_fields = ("id", "states", "q", "tau", "c", "d", "initial", "source_knots", "observation_knots", "g_r", "g_e")
    check("fixture_source_actual_bytes_bound",
          all(case[container]["source_sha256"] == fixture_source_sha for case in fixtures["cases"]
              for container in ("binding", "certificate")))
    check("fixture_whole_forcing_identities_bound",
          all(case[container]["whole_forcing_source_sha256"]
              == fixture_source["whole_forcing_identities"][case["id"]]
              for case in fixtures["cases"] for container in ("binding", "certificate")))
    check("fixture_source_case_payload_identity",
          len(source_cases) == len(fixtures["cases"])
          and all(source_cases.get(case["id"]) == {key: case[key] for key in source_fields}
                  for case in fixtures["cases"]))
    check("fixtures_explicit_arithmetic_premises",
          fixture_source.get("scientific_status") == "ARITHMETIC_CONTROL_PREMISE"
          and all(case[container]["scientific_status"] == "ARITHMETIC_CONTROL_PREMISE"
                  for case in fixtures["cases"] for container in ("binding", "certificate")))

    for case in fixtures["cases"]:
        ident = case["id"]
        try:
            result = run_case(case)
        except Exception as exc:
            check(ident + ":execution", False, {"error_type": type(exc).__name__, "message": str(exc)})
            records.append({"id": ident, "input": case, "result": None,
                            "execution_error": {"type": type(exc).__name__, "message": str(exc)}})
            continue
        records.append({"id": ident, "input": case, "result": result})
        by_id[ident] = result
        check(ident + ":execution", True)
        raw, exact = result["raw"], result["exact"]
        lo, hi = raw["refined_endpoints_lower"], raw["refined_endpoints_upper"]
        whole = raw["refined_whole_cells_upper"]
        check(ident + ":endpoint_nonnegative_enclosure",
              all(0 <= a[j] <= b[j] for a, b in zip(lo, hi) for j in (0, 1)))
        check(ident + ":whole_closed_cell_endpoints",
              all(cell[j] >= max(hi[i][j], hi[i + 1][j])
                  for i, cell in enumerate(whole) for j in (0, 1)))
        check(ident + ":positive_Bernstein_coefficients",
              all(value >= 0 for cell in exact["R_quadratic_cells"] for value in cell["bernstein"]))
        check(ident + ":quadratic_endpoint_binding",
              all(cell["bernstein"][0] == exact["R_at_refined"][i]
                  and cell["bernstein"][2] >= exact["R_at_refined"][i + 1]
                  for i, cell in enumerate(exact["R_quadratic_cells"])))
        check(ident + ":positive_weight_enclosures",
              all(0 <= row[key][0] <= row[key][1]
                  for row in result["weights"] for key in ("exp", "W0", "W1", "W2", "phi")))
        work = result["work"]
        check(ident + ":precharged_work_limit",
              work["guard_applied_before_overlap"] is True
              and work["overlap_terms_actual"] <= work["overlap_terms_upper"] <= 200000
              and work["F_evaluations_actual"] <= work["F_evaluations_upper"])
        check(ident + ":history_and_cap_scope",
              result["R_history"] == "GLOBAL_FROM_ORIGINAL_T0" and result["cap_application"] == "NONE")
        requested = result["requested_times"]
        refined = result["refined_times"]
        check(ident + ":observation_event_coverage",
              set(requested).issubset(set(refined))
              and len(raw["whole_cells_upper"]) + 1 == len(requested))
        if Fraction(case["d"]) == 0:
            check(ident + ":zero_d_beta_integrals",
                  all(row["exp"] == (Fraction(1), Fraction(1))
                      and all(row[key][0] <= (row["right"] - row["left"]) / 3 <= row[key][1]
                              for key in ("W0", "W1", "W2")) for row in result["weights"]))
        control = case.get("controls", {})
        if "endpoint" in control:
            endpoint = control["endpoint"]
            if "R" in endpoint:
                target = Fraction(endpoint["R"])
                check(ident + ":analytic_endpoint_R", raw["endpoints_lower"][-1][0] == target,
                      {"expected": target, "actual": raw["endpoints_lower"][-1][0]})
            if "E" in endpoint:
                target = Fraction(endpoint["E"])
                check(ident + ":analytic_endpoint_E",
                      raw["endpoints_lower"][-1][1] <= target <= raw["endpoints_upper"][-1][1],
                      {"expected": target, "lower": raw["endpoints_lower"][-1][1],
                       "upper": raw["endpoints_upper"][-1][1]})
        if control.get("all_zero"):
            check(ident + ":zero_invariant",
                  all(x == 0 for rows in (lo, hi, whole) for row in rows for x in row))
        if "vertex_times" in control:
            check(ident + ":analytic_vertices",
                  result["vertex_times"] == [Fraction(t) for t in control["vertex_times"]])
        lookup = {t: i for i, t in enumerate(refined)}
        for time_text, targets in control.get("at_refined", {}).items():
            idx = lookup.get(Fraction(time_text))
            check(ident + ":analytic_refined_time:" + time_text, idx is not None)
            if idx is None:
                continue
            if "R" in targets:
                check(ident + ":analytic_refined_R:" + time_text,
                      exact["R_at_refined"][idx] == Fraction(targets["R"]))
            if "E" in targets:
                check(ident + ":analytic_refined_E:" + time_text,
                      lo[idx][1] <= Fraction(targets["E"]) <= hi[idx][1])
        for time_text, target in control.get("F_at_refined", {}).items():
            idx = lookup.get(Fraction(time_text))
            check(ident + ":analytic_global_F:" + time_text,
                  idx is not None and exact["F_at_refined"][idx] == Fraction(target))
        if "whole_R" in control:
            check(ident + ":analytic_whole_R",
                  [row[0] for row in raw["whole_cells_upper"]] == [Fraction(x) for x in control["whole_R"]])
        if "last_whole_E_majorant" in control:
            target = Fraction(control["last_whole_E_majorant"])
            delta = raw["whole_cells_upper"][-1][1] - target
            check(ident + ":analytic_whole_E_majorant",
                  0 <= delta <= Fraction(control["majorant_rounding_guard"]),
                  {"majorant": target, "upper_minus_majorant": delta})
        if "right_left_limit" in control:
            check(ident + ":unattained_left_limit_supremum",
                  exact["R_quadratic_cells"][-1]["bernstein"][-1] == Fraction(control["right_left_limit"])
                  and exact["R_quadratic_cells"][-1]["bernstein"][-1] > exact["R_at_refined"][-1])

    for case in fixtures["cases"]:
        relations = list(case.get("relations", []))
        if "relation" in case:
            relations.append(case["relation"])
        for relation in relations:
            left, right = by_id.get(case["id"]), by_id.get(relation["other"])
            name = case["id"] + ":relation:" + relation["kind"]
            if left is None or right is None:
                check(name, False, "A relation case did not execute")
                continue
            il = {t: i for i, t in enumerate(left["requested_times"])}
            ir = {t: i for i, t in enumerate(right["requested_times"])}
            common = sorted(set(il) & set(ir))
            if relation["kind"] == "same_function":
                equal_r = all(left["raw"]["endpoints_lower"][il[t]][0]
                              == right["raw"]["endpoints_lower"][ir[t]][0] for t in common)
                overlap_e = all(max(left["raw"]["endpoints_lower"][il[t]][1],
                                    right["raw"]["endpoints_lower"][ir[t]][1])
                                <= min(left["raw"]["endpoints_upper"][il[t]][1],
                                       right["raw"]["endpoints_upper"][ir[t]][1]) for t in common)
                check(name + ":exact_R", bool(common) and equal_r)
                check(name + ":ideal_E_intervals_overlap", bool(common) and overlap_e)
            elif relation["kind"] == "supremum_constant":
                ordered_r = all(left["raw"]["endpoints_lower"][il[t]][0]
                                <= right["raw"]["endpoints_lower"][ir[t]][0] for t in common)
                compatible_e = all(left["raw"]["endpoints_lower"][il[t]][1]
                                   <= right["raw"]["endpoints_upper"][ir[t]][1] for t in common)
                check(name + ":exact_R_order", bool(common) and ordered_r)
                check(name + ":E_enclosure_order_compatible", bool(common) and compatible_e,
                      "This check rejects a reversed disjoint enclosure; ideal monotonicity also has a proof and independent reference.")
            else:
                check(name, False, "Unknown relation kind")

    guard_results = []
    for fixture in fixtures.get("guards", []):
        ident = fixture["id"]
        error = None
        try:
            if fixture.get("operation") == "derived_scalar_power_of_two":
                derived(1 << fixture["exponent"])
            else:
                run_case(fixture["input"])
        except DomainError as exc:
            error = str(exc)
        except Exception as exc:
            error = "UNEXPECTED " + type(exc).__name__ + ": " + str(exc)
        passed = error is not None and fixture["expected_error_contains"] in error and not error.startswith("UNEXPECTED")
        check("guard:" + ident, passed, {"actual_error": error,
                                       "expected_error_contains": fixture["expected_error_contains"]})
        guard_results.append({"id": ident, "status": "PASS" if passed else "FAIL", "error": error})
    check("derived_scalar_boundary_accepted", derived(1 << 16383).numerator.bit_length() == 16384)
    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    identities = {}
    for path in (Path(__file__), args.cases, fixture_source_path, LEAF / "src" / "affine_convolution.py", LEAF / "src" / "positive_arithmetic.py"):
        identities[str(path.relative_to(LEAF)) if path.is_relative_to(LEAF) else str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    output = {"schema": "WU_R13_PRIMARY_RESULTS_V1", "status": "PASS_SCOPED" if not failed else "FAIL",
              "cases": records, "checks": checks, "guards": guard_results,
              "summary": {"valid_cases": len(fixtures["cases"]), "valid_case_executions_completed": len(by_id),
                          "guard_cases": len(guard_results), "checks": len(checks), "passed": passed, "failed": failed},
              "execution": {"primary_process_runs": 1, "old_science_or_ODE_replay": 0,
                            "internal_runner_CPU_s": time.process_time() - started,
                            "CPU_scope": "runner body; root wrapper measures complete OS process including imports and serialization"},
              "input_and_code_sha256": identities,
              "scope": "Synthetic conditional affine-forcing comparisons; physical input status remains INPUT_PENDING; no caps applied."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(serializable(output), ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": output["status"], **output["summary"], "output": str(args.output)}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
