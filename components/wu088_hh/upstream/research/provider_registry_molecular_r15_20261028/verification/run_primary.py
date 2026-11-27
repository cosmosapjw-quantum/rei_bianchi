"""One frozen R15 mathematical/control/guard campaign. No hidden rerun."""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def file_identity(path, relative):
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def frozen_identities(root):
    manifest_path = root / "verification/FROZEN_FILES.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    rows = manifest["files"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Frozen files manifest is empty or malformed")
    actual, seen = [], set()
    for row in rows:
        relative = row["path"]
        if not isinstance(relative, str) or relative in seen:
            raise ValueError("Duplicate or invalid frozen source path")
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Frozen source path escapes leaf or is not a file")
        seen.add(relative)
        identity = file_identity(path, relative)
        if identity["bytes"] != row["bytes"] or identity["sha256"] != row["sha256"]:
            raise ValueError("Frozen source identity mismatch: " + relative)
        actual.append(identity)
    return actual, hashlib.sha256(manifest_bytes).hexdigest()


def main():
    sys.set_int_max_str_digits(6000)
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError("Primary output must be new; automatic overwrite/retry forbidden")
    checks, valid_cases, guards, frozen = [], [], [], []
    payload = {"schema": "WU_R15_PRIMARY_RESULTS_V1", "status": "FAIL", "summary": {},
               "valid_cases": valid_cases, "extrema_controls": [], "guard_cases": guards,
               "checks": checks, "frozen_files": frozen,
               "arithmetic": {"production": "exact Fraction; positive Taylor96; dyadic128",
                              "runtime_int_max_str_digits": 6000,
                              "acceptance": "exact controls and directed intervals; no float tolerance",
                              "lower_meaning": "ideal supplied-forcing comparison only; not physical error lower",
                              "source_classification": "ARITHMETIC_CONTROL_PREMISE",
                              "no_physical_admission": True,
                              "no_ODE_or_predecessor_execution": True}}
    core = None

    def check(check_id, condition, kind="MATHEMATICAL_CONTROL", **details):
        checks.append({"id": check_id, "status": "PASS" if condition else "FAIL", "kind": kind, **details})
        return bool(condition)

    def reject(guard_id, thunk):
        try:
            thunk()
        except core.DomainError as exc:
            row = {"id": guard_id, "status": "PASS", "exception_type": type(exc).__name__, "message": str(exc)}
        except Exception as exc:
            row = {"id": guard_id, "status": "FAIL", "exception_type": type(exc).__name__, "message": str(exc)}
        else:
            row = {"id": guard_id, "status": "FAIL", "exception_type": None, "message": "Invalid input was accepted"}
        guards.append(row)
        check("GUARD:" + guard_id, row["status"] == "PASS", kind="REJECTION_GUARD")

    try:
        before, manifest_hash = frozen_identities(root)
        frozen.extend(before)
        check("FROZEN_BEFORE", True, kind="SOURCE_IDENTITY", files=len(before), manifest_sha256=manifest_hash)
        spec = importlib.util.spec_from_file_location("wu_r15_production", root / "src/cubic_convolution.py")
        if spec is None or spec.loader is None:
            raise ImportError("Cannot load the explicit frozen production path")
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        core.configure_r15_runtime()
        fixed = json.loads((root / "verification/CASES.json").read_text(encoding="utf-8"))
        if fixed.get("schema") != "WU_R15_FIXED_CASES_V1" or len(fixed["cases"]) != 21:
            raise ValueError("The frozen 21-case campaign schema/count changed")
        cases = fixed["cases"]
        by_id = {row["id"]: row for row in cases}
        if len(by_id) != 21 or fixed.get("extrema_cases") != []:
            raise ValueError("Unexpected case identities or standalone extrema campaign")
        source_id = file_identity(root / "verification/ARITHMETIC_SOURCE.json", "verification/ARITHMETIC_SOURCE.json")
        check("ARITHMETIC_SOURCE_BINDING", all(
            row["input"]["binding"]["source_sha256"] == source_id["sha256"]
            and row["input"]["binding"]["source_locator"] == source_id["path"] + "#" + row["id"]
            and row["input"]["binding"]["scientific_status"] == "ARITHMETIC_CONTROL_PREMISE"
            for row in cases), kind="SOURCE_IDENTITY", source=source_id)
        results = {}
        derivative_controls = {
            "ROOT_THREE_RATIONAL": ["3/32", "-11/16", "3/2", "-1"],
            "ROOT_THREE_MIXED_ALGEBRAIC": ["1/32", "-3/8", "5/4", "-1"],
            "ROOT_SIMPLE_DOUBLE": ["-2/27", "5/9", "-4/3", "1"],
            "ROOT_TRIPLE": ["-1", "9", "-27", "27"],
            "ROOT_ENDPOINT_INTERIOR": ["0", "1/2", "-3/2", "1"],
            "ROOTLESS_MIXED_COEFFICIENTS": ["13/50", "-1", "1", "0"],
            "ROOT_CONSTANT": ["0", "0", "0", "0"]}
        for row in cases:
            case_id, expected = row["id"], row["expected"]
            first_check = len(checks)
            try:
                result = core.run_case(row["input"])
            except Exception as exc:
                check(case_id + ":EXECUTION", False, kind="CASE_EXECUTION", exception_type=type(exc).__name__, message=str(exc))
                continue
            results[case_id] = result
            cells = result["exact"]["R_quartic_cells"]
            raw, work = result["raw"], result["work"]
            check(case_id + ":EXECUTION", True, kind="CASE_EXECUTION")
            if "R_final" in expected:
                target = Fraction(expected["R_final"])
                check(case_id + ":R_FINAL_EXACT", result["exact"]["R_at_refined"][-1] == target,
                      target=target, actual=result["exact"]["R_at_refined"][-1])
            if "E_final" in expected:
                target = Fraction(expected["E_final"])
                lo, hi = raw["endpoints_lower"][-1][1], raw["endpoints_upper"][-1][1]
                check(case_id + ":E_FINAL_RATIONAL_CONTROL", lo <= target <= hi, target=target, interval=[lo, hi])
            if "R_final_left_limit" in expected:
                target = Fraction(expected["R_final_left_limit"])
                check(case_id + ":RIGHT_LEFT_LIMIT", cells[-1]["right_left_limit"] == target,
                      target=target, actual=cells[-1]["right_left_limit"])
            if "R_last_cell_sup" in expected:
                target = Fraction(expected["R_last_cell_sup"])
                sup = result["exact"]["observation_R_suprema"][-1]
                check(case_id + ":R_SUPREMUM_EXACT_CONTROL", sup["exact_lower"] == target == sup["exact_upper"],
                      target=target, bounds=[sup["exact_lower"], sup["exact_upper"]])
            if "base_times" in expected:
                check(case_id + ":NONALIGNED_CLOCK", result["base_times"] == [Fraction(x) for x in expected["base_times"]])
            if "full_blocks" in expected:
                check(case_id + ":BLOCK_BOUNDARY", work["full_blocks"] == expected["full_blocks"])
            if "overlap_precharge" in expected:
                check(case_id + ":OVERLAP_BOUNDARY", work["overlap_terms_upper"] == expected["overlap_precharge"])
            check(case_id + ":FINITE_WORK", work["overlap_terms_actual"] == work["overlap_terms_upper"]
                  and work["subdivision_splits_actual"] <= work["subdivision_splits_upper"]
                  and work["subdivision_nodes_actual"] <= work["subdivision_nodes_upper"]
                  and work["coefficient_cell_builds"] == len(cells)
                  and work["guard_applied_before_overlap"] is True
                  and work["guard_applied_before_subdivision"] is True, kind="FINITE_WORK", counters=work)
            partition_ok, gap_ok, positive_ok = True, True, True
            for cell in cells:
                subdivision, sup = cell["subdivision"], cell["supremum"]
                leaves = subdivision["leaves"]
                partition_ok = partition_ok and leaves[0]["left"] == 0 and leaves[-1]["right"] == 1
                partition_ok = partition_ok and all(a["right"] == b["left"] for a, b in zip(leaves, leaves[1:]))
                partition_ok = partition_ok and all(leaf["left"] < leaf["right"] and leaf["lower"] <= leaf["upper"] for leaf in leaves)
                partition_ok = partition_ok and subdivision["nodes_visited"] == 2 * subdivision["splits_actual"] + 1
                partition_ok = partition_ok and len(leaves) == subdivision["splits_actual"] + 1 == subdivision["terminal_leaves"]
                partition_ok = partition_ok and all(leaf["depth"] == 96 and leaf["right"] - leaf["left"] == Fraction(1, 1 << 96)
                    for leaf in leaves if leaf["kind"] == "DEPTH_LIMIT")
                gap_ok = gap_ok and sup["exact_gap"] == sup["exact_upper"] - sup["exact_lower"]
                gap_ok = gap_ok and 0 <= sup["exact_gap"] <= sup["proved_gap_bound"] == sup["M_B"] / (1 << 96)
                gap_ok = gap_ok and sup["M_B"] <= 4 * sup["Cmax"]
                gap_ok = gap_ok and sup["dyadic_lower"] <= sup["exact_lower"] <= sup["exact_upper"] <= sup["dyadic_upper"]
                gap_ok = gap_ok and sup["dyadic_upper"] - sup["dyadic_lower"] <= sup["proved_gap_bound"] + Fraction(2, 1 << 128)
                positive_ok = positive_ok and min(cell["bernstein"] + cell["F_bernstein"] + cell["ge_bernstein"] + cell["forcing_bernstein"]) >= 0
            check(case_id + ":COMPLETE_PARTITION", partition_ok, kind="EXACT_CERTIFICATE")
            check(case_id + ":GAP_AND_OUTWARD", gap_ok, kind="EXACT_CERTIFICATE")
            check(case_id + ":POSITIVE_BERNSTEIN", positive_ok, kind="EXACT_CERTIFICATE")
            check(case_id + ":GLOBAL_MEMORY_CONTINUITY", result["R_history"] == "GLOBAL_FROM_ORIGINAL_T0"
                  and all(a["F_bernstein"][-1] == b["F_bernstein"][0] for a, b in zip(cells, cells[1:])), kind="EXACT_CERTIFICATE")
            pairs = (("endpoints_lower", "endpoints_upper"), ("whole_cells_lower", "whole_cells_upper"),
                     ("refined_endpoints_lower", "refined_endpoints_upper"), ("refined_whole_cells_lower", "refined_whole_cells_upper"))
            check(case_id + ":ORDERED_COMPARISON_INTERVALS", all(len(raw[lo]) == len(raw[hi]) and
                  all(0 <= a <= b for row_lo, row_hi in zip(raw[lo], raw[hi]) for a, b in zip(row_lo, row_hi)) for lo, hi in pairs), kind="EXACT_CERTIFICATE")
            moment_ok = True
            for weights in result["weights"]:
                duration = weights["right"] - weights["left"]
                moment_ok = moment_ok and all(0 <= weights[key][0] <= weights[key][1] for key in ("exp", "phi", "W0", "W1", "W2", "W3", "W4"))
                moment_ok = moment_ok and tuple(weights["phi"]) == tuple(sum(weights["W" + str(i)][j] for i in range(5)) for j in range(2))
                if not weights["z"]:
                    moment_ok = moment_ok and weights["exp"] == (Fraction(1), Fraction(1))
                    moment_ok = moment_ok and all(weights["W" + str(i)] == (duration / 5, duration / 5) for i in range(5))
            check(case_id + ":MOMENT_POSITIVITY_AND_PARTITION", moment_ok, kind="EXACT_CERTIFICATE")
            if case_id in derivative_controls:
                coeff = cells[1]["coefficients_normalized"]
                actual = [(i + 1) * coeff[i + 1] for i in range(4)]
                target = [Fraction(x) for x in derivative_controls[case_id]]
                check(case_id + ":MOVING_WINDOW_DERIVATIVE", actual == target, target=target, actual=actual,
                      derivative_root_pattern=expected["derivative_root_pattern"])
            if case_id == "ROOT_THREE_RATIONAL":
                check(case_id + ":DYADIC_ROOT_TERMINATION", cells[1]["subdivision"]["depth_limit_leaves"] == 0
                      and cells[1]["supremum"]["exact_gap"] == 0)
            elif case_id == "ROOT_THREE_MIXED_ALGEBRAIC":
                check(case_id + ":IRRATIONAL_MAXIMUM_GAP", cells[1]["supremum"]["exact_gap"] > 0
                      and cells[1]["subdivision"]["max_depth"] == 96)
            elif case_id == "ROOTLESS_MIXED_COEFFICIENTS":
                check(case_id + ":ROOTLESS_PRUNING", cells[1]["subdivision"]["splits_actual"] == 1
                      and cells[1]["subdivision"]["depth_limit_leaves"] == 0)
            elif case_id == "ROOT_CONSTANT":
                check(case_id + ":CONSTANT_PRUNING", cells[1]["subdivision"]["splits_actual"] == 0
                      and cells[1]["supremum"]["M_B"] == 0)
            if case_id.startswith("SIGNED_DOMAIN_"):
                d = result["parameters"]["d"]
                exp_lo, exp_hi = result["weights"][0]["exp"]
                factor, offset = 1 + 1 / d, -1 / d
                analytic = [factor * exp_lo + offset, factor * exp_hi + offset]
                output_pair = [raw["endpoints_lower"][-1][1], raw["endpoints_upper"][-1][1]]
                check(case_id + ":CONSTANT_FORCING_EXP_INTERVAL_OVERLAP", max(analytic[0], output_pair[0]) <= min(analytic[1], output_pair[1]),
                      kind="ANALYTIC_INTERVAL_CROSSCHECK", analytic=analytic, calculated=output_pair)
            status = "PASS" if all(item["status"] == "PASS" for item in checks[first_check:]) else "FAIL"
            valid_cases.append({"id": case_id, "status": status, "result": result})
        check("CAMPAIGN_FIXED_COUNTS", len(results) == 21
              and sum(result["work"]["base_cells"] for result in results.values()) == 75
              and sum(result["work"]["overlap_terms_upper"] for result in results.values()) == 4811,
              kind="FINITE_WORK", models=len(results), base_cells=sum(result["work"]["base_cells"] for result in results.values()))

        # Same frozen process, fixed-depth diagnostics only; no additional model.
        sweep = fixed["depth_sweep"]
        if sweep["depths"] != [0, 4, 8, 16, 32, 64, 96] or len(sweep["controls"]) != 2:
            raise ValueError("Frozen depth-sweep design changed")
        split_charge = len(sweep["controls"]) * sum(3 * depth for depth in sweep["depths"])
        node_charge = len(sweep["controls"]) * sum(6 * depth + 1 for depth in sweep["depths"])
        if (split_charge, node_charge) != (1320, 2654):
            raise ValueError("Depth diagnostics exceed declared combined precharge")
        sweep_splits = sweep_nodes = 0
        for control in sweep["controls"]:
            bernstein = [Fraction(x) for x in control["bernstein"]]
            model_cell = results[control["model"]]["exact"]["R_quartic_cells"][control["base_cell_index"]]
            condition = bernstein == model_cell["bernstein"]
            rows = []
            for depth in sweep["depths"]:
                ext = core._quartic_supremum(bernstein, depth_limit=depth)
                sup, subd = ext["supremum"], ext["subdivision"]
                item = {"depth": depth, **{key: sup[key] for key in ("exact_lower", "exact_upper", "exact_gap", "M_B", "proved_gap_bound")},
                        "splits_actual": subd["splits_actual"], "nodes_visited": subd["nodes_visited"]}
                condition = condition and 0 <= item["exact_gap"] <= item["proved_gap_bound"] == item["M_B"] / (1 << depth)
                condition = condition and item["splits_actual"] <= 3 * depth and item["nodes_visited"] <= 6 * depth + 1
                if "expected_supremum" in control:
                    target = Fraction(control["expected_supremum"])
                    condition = condition and item["exact_lower"] <= target <= item["exact_upper"]
                rows.append(item)
                sweep_splits += item["splits_actual"]
                sweep_nodes += item["nodes_visited"]
            condition = condition and all(a["exact_gap"] >= b["exact_gap"] for a, b in zip(rows, rows[1:]))
            check(control["id"], condition, kind="DEPTH_SWEEP", bernstein=bernstein, rows=rows)
        check("DEPTH_SWEEP_WORK", sweep_splits <= split_charge and sweep_nodes <= node_charge,
              kind="FINITE_WORK", splits_actual=sweep_splits, nodes_visited=sweep_nodes,
              splits_precharged=split_charge, nodes_precharged=node_charge)

        # Mathematical acceptance controls, not extra full-model runs.
        check("RATIONAL_ASCII_SIGNED_ACCEPTANCE", core.exact("+2/-4") == Fraction(-1, 2)
              and core.exact("0" * 2048) == 0 and core.exact((1 << 256) - 1) == (1 << 256) - 1,
              kind="PARSER_BOUNDARY")
        maximum_derived = Fraction(-((1 << 16384) - 1), (1 << 16384) - 3)
        derived_text = core.serializable(core.derived(maximum_derived))
        check("DERIVED_SERIALIZATION_BOUNDARY", len(derived_text) <= 10000
              and sys.get_int_max_str_digits() == 6000, kind="PARSER_BOUNDARY",
              output_characters=len(derived_text), numerator_bits=abs(maximum_derived.numerator).bit_length(),
              denominator_bits=maximum_derived.denominator.bit_length())
        check("MAXIMUM_PRECHARGE_ONLY", core.precharge_work(512, 16, 8) == (73728, 147456, 295424),
              kind="FINITE_WORK", qualification="Count calculation only; maximum grid is not executed")
        lexical = {"BOOLEAN": True, "FLOAT": 0.5, "WHITESPACE": " 1", "DECIMAL": "0.5", "EXPONENT": "1e0",
                   "UNICODE_DIGITS": "١", "ZERO_DENOMINATOR": "1/0", "EMPTY": "", "TOKEN_TOO_LONG": "0" * 2049,
                   "INPUT_BITS": 1 << 256, "RAW_COMPONENT_BITS_BEFORE_REDUCTION": str(1 << 256) + "/" + str(1 << 256)}
        for guard_id, value in lexical.items():
            reject("RATIONAL_" + guard_id, lambda value=value: core.exact(value))
        reject("DERIVED_BITS", lambda: core.derived(1 << 16384))
        for guard_id, counts in (("BASE_OVER512", (513, 16, 8)), ("SOURCE_OVER16", (512, 17, 8)),
                                 ("BLOCKS_OVER8", (512, 16, 9)), ("BOOL_COUNT", (True, 1, 0))):
            reject("WORK_" + guard_id, lambda counts=counts: core.precharge_work(*counts))

        base_case = by_id["CUBIC"]["input"]

        def reject_case(guard_id, mutations):
            altered = deepcopy(base_case)
            for path, value in mutations:
                target = altered
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
            reject(guard_id, lambda: core.validate(altered))

        input_mutations = [
            ("B3_ROW_LENGTH", [(('g_r',), [["0", "0", "1"]])]),
            ("B3_ROW_COUNT", [(('g_e',), [])]),
            ("B3_NEGATIVE", [(('g_r', 0, 0), "-1")]),
            ("NONNEGATIVE_POLYNOMIAL_OUTSIDE_CONE", [(('g_r',), [["1/4", "-1/12", "-1/12", "1/4"]])]),
            ("SINGLETON_GR", [(('states',), 1)]),
            ("SINGLETON_R0", [(('states',), 1), (('g_r',), [["0"] * 4]), (('initial', 0), "1")]),
            ("SOURCE_UNORDERED", [(('source_knots',), ["1", "0"])]),
            ("OBSERVATION_DUPLICATE", [(('observation_knots',), ["0", "0", "1"])]),
            ("HORIZON_MISMATCH", [(('observation_knots',), ["0", "2"])]),
            ("SOURCE_CELLS_OVER16", [(('source_knots',), [str(Fraction(j, 17)) for j in range(18)])]),
            ("OBSERVATION_CELLS_OVER32", [(('observation_knots',), [str(Fraction(j, 33)) for j in range(34)])]),
            ("FULL_BLOCKS_OVER8", [(('tau',), "1/9")]),
            ("Q_NEGATIVE", [(('q',), "-1/2")]),
            ("Q_OVER1", [(('q',), "3/2")]),
            ("TAU_NONPOSITIVE", [(('tau',), "0")]),
            ("C_NEGATIVE", [(('c',), "-1")]),
            ("INITIAL_NEGATIVE", [(('initial', 1), "-1")]),
            ("D_HORIZON_OVER16", [(('d',), "17")]),
            ("STATES_ZERO", [(('states',), 0)]),
            ("STATES_OVER13", [(('states',), 14)]),
            ("STATES_BOOL", [(('states',), True)]),
            ("CAP_ADAPTER", [(('caps',), {})]),
            ("UNKNOWN_INPUT_FIELD", [(('unexpected',), 1)]),
            ("WHOLE_FORCING_CHANGED", [(('g_r', 0, 0), "1")]),
            ("GENERATOR_NOMINAL_K", [(('certificate', 'generator'), "K")]),
            ("W_BOX_NEGATIVE", [(('certificate', 'w_box'), ["-1", "1"])]),
            ("W_BOX_REVERSED", [(('certificate', 'w_box'), ["2", "1"])]),
            ("STATUS_UNKNOWN", [(('binding', 'scientific_status'), "PHYSICAL_ACCEPTED"), (('certificate', 'scientific_status'), "PHYSICAL_ACCEPTED")]),
            ("STATE_ORDER_DUPLICATE", [(('binding', 'state_order'), ["same", "same"]), (('certificate', 'state_order'), ["same", "same"])]),
            ("IDENTITY_TEXT_TOO_LONG", [(('binding', 'source_id'), "x" * 257)]),
            ("SOURCE_SHA_INVALID", [(('binding', 'source_sha256'), "not-a-sha")]),
            ("CERTIFICATE_EXTRA_FIELD", [(('certificate', 'unexpected'), True)])]
        for guard_id, mutations in input_mutations:
            reject_case(guard_id, mutations)
        for key in core.IDENTITY_KEYS:
            original = base_case["certificate"][key]
            value = list(reversed(original)) if isinstance(original, list) else original + "_MISMATCH"
            reject_case("IDENTITY_MISMATCH_" + key, [(("certificate", key), value)])
        for flag in core.PREMISE_FLAGS:
            reject_case("PREMISE_FALSE_" + flag, [(("certificate", flag), False)])
        for key, value in (("q", "0"), ("tau", "2"), ("t0", "-1"), ("T", "2")):
            reject_case("CERTIFICATE_SCALAR_" + key, [(("certificate", key), value)])
        after, after_manifest_hash = frozen_identities(root)
        check("FROZEN_AFTER", before == after and manifest_hash == after_manifest_hash,
              kind="SOURCE_IDENTITY", files=len(after), manifest_sha256=after_manifest_hash)
    except Exception as exc:
        check("CAMPAIGN_EXCEPTION", False, kind="EXECUTION_FAILURE",
              exception_type=type(exc).__name__, message=str(exc))
    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload["status"] = "PASS_SCOPED" if not failed and len(valid_cases) == 21 else "FAIL"
    payload["summary"] = {"valid_cases": len(valid_cases), "extrema_controls": 0,
                          "rejection_guards": len(guards), "depth_sweep_rows": sum(len(row.get("rows", [])) for row in checks if row.get("kind") == "DEPTH_SWEEP"),
                          "checks": len(checks), "passed": passed, "failed": failed}
    if core is not None:
        payload = core.serializable(payload)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "output": str(output)}, sort_keys=True))
    return 0 if payload["status"] == "PASS_SCOPED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
