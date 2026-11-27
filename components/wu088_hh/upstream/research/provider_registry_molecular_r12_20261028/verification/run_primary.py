"""One frozen R12 primary pass; no predecessor import/run or ODE execution."""
from __future__ import annotations

import ast
from copy import deepcopy
import datetime
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import traceback

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
CORE = BASE / "src/nonaligned_convolution.py"
ARITHMETIC = BASE / "src/positive_arithmetic.py"
INPUT = BASE / "verification/PRIMARY_INPUT.json"
CONTRACT = BASE / "CONTRACT.json"
FREEZE = BASE / "raw/PREEXECUTION_FREEZE.json"
OUT = BASE / "raw/PRIMARY_RESULTS.json"
SOURCE_HASHES = {
    "R11_primary": "80ed0f8df5c785e47ce737acb8b029485db54b543d57498bf182427093f29b1b",
    "R11_arithmetic_source": "c3720dcc9b4e79e7d44eaa16c420a1a9b0d29d141be2fd994cc77c779cc9fa0f",
}
CONTROL_ARGUMENTS = ("q", "tau", "c", "d", "g_r", "g_e", "source_knots", "observation_knots", "initial")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(relative):
    path = (REPO / relative).resolve()
    if not path.is_relative_to(REPO.resolve()):
        raise ValueError("Source path escapes the repository")
    return path


def serialize(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(v) for v in value]
    return value


def counts(new, old):
    pairs = [(a, Fraction(b)) for aa, bb in zip(new, old) for a, b in zip(aa, bb)]
    return {"less": sum(a < b for a, b in pairs), "equal": sum(a == b for a, b in pairs),
            "greater": sum(a > b for a, b in pairs)}


def main():
    if len(sys.argv) != 1:
        raise SystemExit("R12 primary takes no command-line arguments")
    if OUT.exists():
        raise SystemExit("Refuse to overwrite the first R12 primary result")
    cpu0, wall0 = time.process_time(), time.monotonic()
    result = {
        "schema": "WU_R12_PRIMARY_RESULTS_V1", "unit": "WU_NONALIGNED_CONVOLUTION_R12",
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_sha256": digest(INPUT), "core_sha256": digest(CORE),
        "arithmetic_sha256": digest(ARITHMETIC), "runner_sha256": digest(Path(__file__)),
        "contract_sha256": digest(CONTRACT), "checks": [], "hd_cases": [], "controls": [],
        "scope": {"old_science_replay": 0, "predecessor_module_imports": 0, "new_ODE_runs": 0,
                  "native_exponential_runs": 0, "new_generator_calculations": 0,
                  "new_saved_sample_campaign": 0, "physical_consumer_admitted": False,
                  "lower_arrays": "chosen rational-q ideal comparison only",
                  "raw_universal_superiority_claim": False},
        "budget": {"runs": 1, "CPU_limit_s": 60, "wall_limit_s": 90, "bits": 128, "degree": 96},
    }

    def check(name, ok, evidence=None):
        result["checks"].append({"name": name, "status": "PASS" if bool(ok) else "FAIL", "evidence": evidence})

    def require(name, ok, evidence=None):
        check(name, ok, evidence)
        if not ok:
            raise ValueError("Required contract assertion failed: " + name)

    def guard_budget():
        if time.process_time() - cpu0 > 58 or time.monotonic() - wall0 > 88:
            raise RuntimeError("R12 primary bounded pre-finalization stop")

    try:
        freeze = json.loads(FREEZE.read_text())
        if freeze.get("status") != "PASS" or not isinstance(freeze.get("files"), list):
            raise ValueError("Successful preexecution freeze required")
        frozen = {}
        for row in freeze["files"]:
            path = inside(row["path"])
            raw_bytes = path.read_bytes()
            if len(raw_bytes) != row["bytes"] or hashlib.sha256(raw_bytes).hexdigest() != row["sha256"]:
                raise ValueError("Frozen source bytes differ: " + row["path"])
            frozen[row["path"]] = row["sha256"]
        required = [p.relative_to(REPO).as_posix() for p in (CORE, ARITHMETIC, INPUT, CONTRACT, Path(__file__).resolve())]
        require("freeze_membership", all(path in frozen for path in required), required)
        result["freeze_sha256"] = digest(FREEZE)
        spec = json.loads(INPUT.read_text())
        contract = json.loads(CONTRACT.read_text())
        require("fixed_primary_input", spec.get("schema") == "WU_R12_FIXED_PRIMARY_INPUT_V1" and
                spec.get("unit") == result["unit"] and spec.get("bits") == 128 and spec.get("degree") == 96 and
                spec.get("saved_cells") == 192 and spec.get("saved_grid_variants") == ["aligned", "nonaligned"])
        finite = contract["finite_domain"]
        require("finite_domain_contract", contract["unit"] == result["unit"] and
                finite["source_cells"] == finite["observation_cells"] == finite["old_cap_cells"] == [1, 192] and
                finite["maximum_refined_cells"] == 2048 and finite["maximum_full_blocks"] == 8 and
                finite["maximum_overlap_terms"] == 200000 and finite["exact_input_scalar_bits_max"] == 1024 and
                finite["dyadic_bits"] == 128 and finite["Taylor_degree"] == 96 and
                finite["absolute_d_times_horizon_max"] == 16)
        source_bytes = {}
        for name, expected in SOURCE_HASHES.items():
            item = spec["sources"][name]
            path = inside(item["path"])
            require("source_" + name + "_identity", item["sha256"] == expected and digest(path) == expected and
                    frozen.get(item["path"]) == expected, item)
            source_bytes[name] = path.read_bytes()
        source = json.loads(source_bytes["R11_primary"])
        require("R11_actual_primary_PASS", source["status"] == "PASS" and source["unit"] == "WU_FULL_GENERATOR_BLOCK_R11")
        require("R11_case_order", [x["id"] for x in source["hd_cases"]] == spec["hd_case_ids"])
        result["source_sha256"] = SOURCE_HASHES

        trees = {"core": ast.parse(CORE.read_text()), "arithmetic": ast.parse(ARITHMETIC.read_text()),
                 "R11_arithmetic_source": ast.parse(source_bytes["R11_arithmetic_source"].decode())}
        copied_names = ("Q", "_positive", "_ceil", "_floor_scaled", "_ceil_scaled", "down", "up", "_tail",
                        "_positive_series", "_exp_fraction", "exp_interval", "bernstein_weights")
        functions = {key: {x.name: x for x in tree.body if isinstance(x, ast.FunctionDef)} for key, tree in trees.items()}
        copy_equal = {name: ast.dump(functions["arithmetic"][name], include_attributes=False) ==
                      ast.dump(functions["R11_arithmetic_source"][name], include_attributes=False) for name in copied_names}
        require("copied_R11_pure_arithmetic_AST", all(copy_equal.values()), copy_equal)
        imports = []
        for key in ("core", "arithmetic"):
            for node in ast.walk(trees[key]):
                if isinstance(node, ast.Import):
                    imports.extend(x.name for x in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
        require("production_import_surface", set(imports) <= {"__future__", "bisect", "collections.abc", "copy",
                "fractions", "hashlib", "json", "re", "math", "positive_arithmetic"}, sorted(set(imports)))
        sys.path.insert(0, str(CORE.parent))
        loader = importlib.util.spec_from_file_location("wu_r12_frozen_core", CORE)
        module = importlib.util.module_from_spec(loader)
        sys.modules[loader.name] = module
        loader.loader.exec_module(module)
        Q = module.Q
        require("runtime_finite_constants", module.MAX_INPUT_BITS == 1024 and module.MAX_CELLS == 192 and
                module.MAX_REFINED_CELLS == 2048 and module.MAX_BLOCKS == 8 and module.MAX_OVERLAP_TERMS == 200000)

        def verify_geometry(tag, out):
            times, requested = out["refined_times"], out["requested_times"]
            ns, nr = len(times) - 1, len(requested) - 1
            check(tag + ":strict_exact_geometry", all(isinstance(t, Fraction) for t in times + requested) and
                  all(a < b for a, b in zip(times, times[1:])) and times[0] == requested[0] and times[-1] == requested[-1])
            selected = out["refinement"]["requested_point_indices"]
            ranges = out["refinement"]["requested_subcell_ranges"]
            check(tag + ":requested_exact_selection", len(selected) == nr + 1 and
                  all(times[i] == t for i, t in zip(selected, requested)) and
                  ranges == list(zip(selected, selected[1:])))
            src = out["source"]["knots"]
            si = out["refinement"]["source_cell_indices"]
            check(tag + ":source_subcell_inclusion", len(si) == ns and all(src[j] <= times[i] < times[i + 1] <= src[j + 1]
                                                                          for i, j in enumerate(si)))
            tau, t0, end = out["parameters"]["tau"], out["parameters"]["t0"], out["parameters"]["T"]
            expected_jumps = {a + k * tau for a in src for k in range(out["work"]["full_blocks"] + 1)
                              if t0 <= a + k * tau <= end}
            check(tag + ":translated_source_jumps_retained", expected_jumps <= set(times))
            check(tag + ":resource_domain", ns <= 2048 and out["work"]["overlap_terms"] <= 200000 and
                  out["work"]["full_blocks"] <= 8 and abs(out["parameters"]["d"]) * (end - t0) <= 16)
            check(tag + ":fresh_age_and_no_restart", out["h0"] == 1 and out["exact"]["kernel_at_refined"][0] == 1 and
                  out["exact"]["F_at_refined"][0] == 0 and out["R_memory_reset"] is False)
            for mode in ("raw", "capped"):
                data = out[mode]
                if data is None:
                    continue
                suffix = tag + ":" + mode
                check(suffix + ":shape", len(data["endpoints_upper"]) == nr + 1 and
                      len(data["whole_cells_upper"]) == nr and len(data["refined_endpoints_upper"]) == ns + 1 and
                      len(data["refined_whole_cells_upper"]) == ns)
                check(suffix + ":nonnegative", all(x >= 0 for key in ("endpoints_upper", "whole_cells_upper",
                      "refined_endpoints_upper", "refined_whole_cells_upper") for row in data[key] for x in row))
                check(suffix + ":initial", tuple(data["endpoints_upper"][0]) == tuple(out["parameters"]["initial"]))
                check(suffix + ":closed_refined_cells_cover_points", all(data["refined_endpoints_upper"][i + e][k] <=
                      data["refined_whole_cells_upper"][i][k] for i in range(ns) for e in (0, 1) for k in (0, 1)))
                check(suffix + ":closed_requested_cells_cover_points", all(data["endpoints_upper"][i + e][k] <=
                      data["whole_cells_upper"][i][k] for i in range(nr) for e in (0, 1) for k in (0, 1)))
                check(suffix + ":aggregation_is_gap_free_max", all(data["whole_cells_upper"][i][k] ==
                      max(x[k] for x in data["refined_whole_cells_upper"][a:b]) for i, (a, b) in enumerate(ranges) for k in (0, 1)))
            raw = out["raw"]
            check(tag + ":raw_interval_order", all(lo <= hi for a, b in zip(raw["refined_endpoints_lower"],
                  raw["refined_endpoints_upper"]) for lo, hi in zip(a, b)))
            check(tag + ":exact_R_enclosed", all(lo[0] <= value <= hi[0] for lo, value, hi in
                  zip(raw["refined_endpoints_lower"], out["exact"]["R_at_refined"], raw["refined_endpoints_upper"])))
            check(tag + ":affine_left_limit_enclosed", all(a["left_interval"][0] <= x["L"] <= a["left_interval"][1] and
                  a["right_left_limit_interval"][0] <= x["V"] <= a["right_left_limit_interval"][1] and
                  raw["refined_whole_cells_upper"][i][0] >= a["right_left_limit_interval"][1]
                  for i, (a, x) in enumerate(zip(raw["R_affine_cells"], out["exact"]["R_affine_cells"]))))
            if out["caps"] is not None:
                caps, capped = out["caps"], out["capped"]
                knots, oldwhole = caps["old_knots"], caps["old_whole_cells_upper"]
                mapping = caps["subcell_to_old_cell"]
                check(tag + ":cap_source_SHA", caps["source_sha256"] == SOURCE_HASHES["R11_primary"])
                check(tag + ":cap_closed_inclusion", all(knots[j] <= times[i] < times[i + 1] <= knots[j + 1]
                      for i, j in enumerate(mapping)))
                check(tag + ":cap_point_only_exact", all((j is not None and knots[j] == t) or
                      (j is None and t not in set(knots)) for t, j in zip(times, caps["refined_point_to_old_point"])))
                check(tag + ":cap_refined_no_worse", all(capped["refined_whole_cells_upper"][i][k] <= oldwhole[j][k]
                      for i, j in enumerate(mapping) for k in (0, 1)))
                check(tag + ":cap_below_raw", all(a <= b for key in ("endpoints_upper", "whole_cells_upper",
                      "refined_endpoints_upper", "refined_whole_cells_upper") for aa, bb in zip(capped[key], raw[key]) for a, b in zip(aa, bb)))
                check(tag + ":cap_lower_absent", capped["endpoints_lower"] is None and capped["refined_endpoints_lower"] is None)

        for i, case_id in enumerate(spec["hd_case_ids"]):
            guard_budget()
            oldcase = source["hd_cases"][i]
            record = {"id": case_id, "source_scope": oldcase["source_scope"], "variants": {}, "comparison": {}}
            old_knots = [n * Q(oldcase["raw"]["delta"]) for n in range(193)]
            for variant in spec["saved_grid_variants"]:
                guard_budget()
                out = module.saved_case_sweep(source_bytes["R11_primary"], case_id, variant)
                record["variants"][variant] = out
                tag = case_id + ":" + variant
                verify_geometry(tag, out)
                check(tag + ":source_compression_exact", out["saved_case"]["constant_source_compression_exact"] and
                      out["work"]["source_cells"] == 1 and all(Q(x) == out["source"][key][0]
                      for key in ("g_r", "g_e") for x in oldcase["raw"]["coefficients"][key]))
                check(tag + ":q_tau_reused_without_generator", out["parameters"]["q"] == Q(oldcase["raw"]["q"]) and
                      out["parameters"]["tau"] == Q(oldcase["raw"]["tau"]) and
                      out["saved_case"]["nominal_K_recomputed"] is False and out["saved_case"]["native_exponential_recomputed"] is False)
                if variant == "aligned":
                    check(tag + ":aligned_exact_grid", list(out["requested_times"]) == old_knots and list(out["refined_times"]) == old_knots)
                    check(tag + ":aligned_exact_R_in_R11_raw_interval", all(Q(a[0]) <= x <= Q(b[0]) for a, x, b in
                          zip(oldcase["raw"]["endpoints_lower"], out["exact"]["R_at_refined"], oldcase["raw"]["endpoints_upper"])))
                    check(tag + ":aligned_E_intervals_overlap", all(newlo[1] <= Q(oldhi[1]) and Q(oldlo[1]) <= newhi[1]
                          for newlo, newhi, oldlo, oldhi in zip(out["raw"]["endpoints_lower"], out["raw"]["endpoints_upper"],
                          oldcase["raw"]["endpoints_lower"], oldcase["raw"]["endpoints_upper"])))
                    for key in ("endpoints_upper", "whole_cells_upper"):
                        check(tag + ":capped_" + key + "_no_worse_R11", all(a <= Q(b) for aa, bb in
                              zip(out["capped"][key], oldcase["capped"][key]) for a, b in zip(aa, bb)))
                        record["comparison"]["aligned_raw_" + key + "_vs_R11_capped"] = counts(out["raw"][key], oldcase["capped"][key])
                        record["comparison"]["aligned_capped_" + key + "_vs_R11_capped"] = counts(out["capped"][key], oldcase["capped"][key])
                else:
                    check(tag + ":nonaligned_knots_are_actual_new_times", set(out["requested_times"][1:-1]).isdisjoint(set(old_knots)))
                    pm = out["caps"]["requested_point_to_old_point"]
                    check(tag + ":no_interpolated_point_cap", pm[0] == 0 and pm[-1] == 192 and all(x is None for x in pm[1:-1]))
            aligned, nonaligned = record["variants"]["aligned"], record["variants"]["nonaligned"]
            index = {t: j for j, t in enumerate(nonaligned["refined_times"])}
            check(case_id + ":grid_independent_exact_RF_at_old_knots", all(aligned["exact"][key][j] ==
                  nonaligned["exact"][key][index[t]] for j, t in enumerate(aligned["refined_times"])
                  for key in ("kernel_at_refined", "F_at_refined", "R_at_refined")))
            check(case_id + ":same_ideal_E_overlap_at_old_knots", all(
                  aligned["raw"]["refined_endpoints_lower"][j][1] <= nonaligned["raw"]["refined_endpoints_upper"][index[t]][1] and
                  nonaligned["raw"]["refined_endpoints_lower"][index[t]][1] <= aligned["raw"]["refined_endpoints_upper"][j][1]
                  for j, t in enumerate(aligned["refined_times"])))
            record["comparison"]["nonaligned_vs_R11_points"] = "NOT_COMPARED_AT_DIFFERENT_CLOCKS; old point caps only at exact equal times"
            record["comparison"]["R11_final"] = oldcase["capped"]["endpoints_upper"][-1]
            record["comparison"]["aligned_capped_final"] = aligned["capped"]["endpoints_upper"][-1]
            record["comparison"]["nonaligned_capped_final"] = nonaligned["capped"]["endpoints_upper"][-1]
            result["hd_cases"].append(record)

        def control_call(control, control_index):
            pars = {k: deepcopy(control[k]) for k in CONTROL_ARGUMENTS}
            binding = {"family_id": "R12_exact_arithmetic_control_family", "norm": "l1_on_kerP",
                       "source_sha256": result["input_sha256"], "clock": "exact dimensionless R12 arithmetic control clock",
                       "state_ids": [f"s{i}" for i in range(control["state_count"])]}
            certificate = {"certificate_id": "R12_control_" + control["id"], "scientific_status": "ARITHMETIC_CONTROL_PREMISE",
                           "source_sha256": result["input_sha256"], "source_pointer": "/controls/" + str(control_index),
                           "family_scope": "Arithmetic block-kernel control; no physical generator realizability claim",
                           "q": pars["q"], "tau": pars["tau"],
                           "validity_interval": [pars["source_knots"][0], pars["source_knots"][-1]],
                           "uniform_all_starts": True, "same_family_composition": True,
                           "remainder_l1_nonexpansive": True, "zero_mass_forcing": True, "whole_domain_forcing": True,
                           "binding": deepcopy(binding)}
            return dict(pars, binding=binding, certificate=certificate)

        control_outputs, control_inputs = {}, {}
        for control_index, control in enumerate(spec["controls"]):
            guard_budget()
            call = control_call(control, control_index)
            before = json.dumps(serialize(call), sort_keys=True)
            out = module.nonaligned_sweep(**call)
            control_outputs[control["id"]] = out
            control_inputs[control["id"]] = call
            result["controls"].append({"id": control["id"], "parameters": deepcopy(control), "result": out})
            verify_geometry("control:" + control["id"], out)
            check("control:" + control["id"] + ":arguments_unchanged", json.dumps(serialize(call), sort_keys=True) == before)

        poly = control_outputs["q1_polynomial_nonaligned"]
        expected_poly = [(1 + 2 * t, 2 + Fraction(7, 2) * t + t * t / 2) for t in poly["requested_times"]]
        check("control:q1_exact_polynomial", all(lo[k] <= exact[k] <= hi[k] for lo, exact, hi in
              zip(poly["raw"]["endpoints_lower"], expected_poly, poly["raw"]["endpoints_upper"]) for k in (0, 1)),
              {"final_exact": [3, 6]})
        check("control:d0_positive_moment_limits", all(w["exp"] == (1, 1) and
              w["W0"][0] <= Fraction(length) / 2 <= w["W0"][1] and
              w["W1"][0] <= Fraction(length) / 2 <= w["W1"][1] and
              w["phi"][0] <= Fraction(length) <= w["phi"][1]
              for length, w in poly["Bernstein_weights_by_length"].items()))
        late = control_outputs["q0_late_source_nonaligned"]
        check("control:q0_fresh_forcing_survives", late["exact"]["R_at_refined"][-1] == Fraction(1, 4) and
              late["raw"]["endpoints_lower"][-1][1] <= Fraction(1, 32) <= late["raw"]["endpoints_upper"][-1][1],
              {"final_exact_R": "1/4", "final_exact_E": "1/32", "fresh_interval": ["3/4", "1"]})
        translated = control_outputs["translated_source_breakpoints"]
        check("control:translated_knots_not_only_homogeneous_jumps", {Fraction(8, 15), Fraction(13, 15)} <= set(translated["refined_times"]))
        jump = control_outputs["block_jump_left_limit"]
        ji = jump["refined_times"].index(Fraction(2, 5))
        check("control:left_limit_is_required", jump["exact"]["R_affine_cells"][ji - 1]["V"] == 1 and
              jump["exact"]["R_at_refined"][ji] == Fraction(1, 2) and
              jump["raw"]["refined_whole_cells_upper"][ji - 1][0] == 1,
              {"right_knot": "2/5", "left_limit": "1", "right_point": "1/2"})
        check("control:positive_negative_and_nearzero_d", control_outputs["positive_d_nonaligned"]["parameters"]["d"] > 0 and
              translated["parameters"]["d"] < 0 and
              control_outputs["near_zero_d_positive"]["parameters"]["d"] == Fraction(1, 10**30) and
              control_outputs["near_zero_d_negative"]["parameters"]["d"] == -Fraction(1, 10**30))
        check("control:eight_full_blocks_boundary", control_outputs["near_one_q"]["work"]["full_blocks"] == 8)
        singleton = control_outputs["singleton_zero_residual"]
        check("control:singleton_zero_residual", all(x == 0 for x in singleton["exact"]["R_at_refined"]))
        for relation in spec["paired_relations"]:
            a, b = control_outputs[relation["base"]], control_outputs[relation["other"]]
            if relation["kind"] == "absolute_clock_translation":
                shift = Q(relation["offset"])
                check("paired:shifted_exact_clock", tuple(t + shift for t in a["refined_times"]) == b["refined_times"] and
                      all(a["exact"][key] == b["exact"][key] for key in ("kernel_at_refined", "F_at_refined", "R_at_refined")) and
                      a["raw"]["refined_endpoints_upper"] == b["raw"]["refined_endpoints_upper"] and
                      a["raw"]["refined_endpoints_lower"] == b["raw"]["refined_endpoints_lower"])
            elif relation["kind"] == "observation_refinement_same_ideal_function":
                index = {t: i for i, t in enumerate(b["refined_times"])}
                check("paired:refinement_exact_RF", set(a["requested_times"]) <= set(b["requested_times"]) and all(
                      a["exact"][key][i] == b["exact"][key][index[t]] for i, t in enumerate(a["refined_times"])
                      for key in ("kernel_at_refined", "F_at_refined", "R_at_refined")))
                check("paired:refinement_E_intervals_overlap", all(a["raw"]["refined_endpoints_lower"][i][1] <=
                      b["raw"]["refined_endpoints_upper"][index[t]][1] and b["raw"]["refined_endpoints_lower"][index[t]][1] <=
                      a["raw"]["refined_endpoints_upper"][i][1] for i, t in enumerate(a["refined_times"])))
            elif relation["kind"] == "signed_near_zero_scalar":
                check("paired:nearzero_R_same_and_scalar_order", a["exact"] == b["exact"] and all(
                      b["raw"]["endpoints_lower"][i][1] <= a["raw"]["endpoints_upper"][i][1]
                      for i in range(len(a["requested_times"]))))
            else:
                raise ValueError("Unknown frozen paired relation")

        def reject(name, args, message_part=None):
            guard_budget()
            try:
                module.nonaligned_sweep(**args)
            except module.DomainError as exc:
                check("guard:" + name, message_part is None or message_part in str(exc), str(exc))
            else:
                check("guard:" + name, False, "Invalid input accepted")

        base = control_inputs["q1_polynomial_nonaligned"]
        invalid = [
            ("q", -1, "negative_q", "q in"), ("q", 2, "q_above_one", "q in"),
            ("q", 0.5, "float_q", "float/bool"), ("q", True, "bool_q", "float/bool"),
            ("tau", 0, "zero_tau", "tau>0"), ("tau", -1, "negative_tau", "tau>0"),
            ("tau", "1/10", "block_limit", "eight"), ("c", -1, "negative_c", "c>=0"),
            ("d", 17, "global_scaled_exp_limit", "horizon"), ("d", 0.0, "float_d", "float/bool"),
            ("g_r", -1, "negative_gr", "nonnegative"), ("g_e", -1, "negative_ge", "nonnegative"),
            ("g_r", True, "bool_forcing", "float/bool"), ("g_r", [1, 2], "forcing_dimension", "dimension"),
            ("g_e", [-1], "negative_forcing_array", "nonnegative"),
            ("g_r", 1 << 1024, "input_scalar_bits", "1024-bit"),
            ("initial", [-1, 0], "negative_initial", "nonnegative"),
            ("initial", [0], "initial_dimension", "dimension"),
            ("source_knots", [0, 0], "zero_source_cell", "strictly increasing"),
            ("source_knots", [1, 0], "reversed_source_grid", "strictly increasing"),
            ("source_knots", [0, 0.5, 1], "float_source_knot", "float/bool"),
            ("source_knots", [False, 1], "bool_source_knot", "float/bool"),
            ("source_knots", [Fraction(i, 193) for i in range(194)], "source_cell_limit", "1..192"),
            ("observation_knots", [0, "1/2", "1/2", 1], "duplicate_observation_knot", "strictly increasing"),
            ("observation_knots", [0, True], "bool_observation_knot", "float/bool"),
            ("observation_knots", [0, 0.5, 1], "float_observation_knot", "float/bool"),
            ("observation_knots", [0, 2], "observation_horizon_mismatch", "same exact interval"),
            ("observation_knots", [Fraction(i, 193) for i in range(194)], "observation_cell_limit", "1..192"),
            ("bits", 127, "bits_fixed", "bits"), ("degree", 95, "Taylor_degree_fixed", "degree"),
            ("cap_source_bytes", {}, "cap_pair_required", "supplied together"),
            ("cap_case_id", "two_state_no_reaction", "cap_source_required", "supplied together"),
        ]
        for key, value, name, message in invalid:
            call = deepcopy(base)
            call[key] = value
            reject(name, call, message)
        for flag in ("uniform_all_starts", "same_family_composition", "remainder_l1_nonexpansive",
                     "zero_mass_forcing", "whole_domain_forcing"):
            call = deepcopy(base)
            call["certificate"][flag] = False
            reject(flag, call, "premise")
        for key, value, name, message in (
                ("q", "1/2", "certificate_q", "q/tau"),
                ("tau", "1/2", "certificate_tau", "q/tau"),
                ("validity_interval", ["1/10", 1], "all_start_left_coverage", "cover"),
                ("validity_interval", [0, "9/10"], "all_start_right_coverage", "cover"),
                ("source_sha256", "bad", "certificate_source_sha", "locator"),
                ("source_pointer", "not_pointer", "certificate_pointer", "locator"),
                ("scientific_status", "CERTIFIED_K_ONLY", "nominal_K_not_full_A", "full-A")):
            call = deepcopy(base)
            call["certificate"][key] = value
            reject(name, call, message)
        for key, value, name, message in (
                ("clock", "other clock", "certificate_clock_mismatch", "binding mismatch"),
                ("state_ids", ["s1", "s0"], "certificate_state_order_mismatch", "binding mismatch"),
                ("family_id", "other family", "certificate_family_mismatch", "binding mismatch"),
                ("norm", "different", "norm", "normalization"),
                ("source_sha256", "bad", "binding_source_sha", "SHA256"),
                ("state_ids", ["s0", "s0"], "duplicate_states", "state IDs"),
                ("state_ids", [f"s{i}" for i in range(14)], "state_limit", "state IDs")):
            call = deepcopy(base)
            call["binding"][key] = value
            reject(name, call, message)
        call = deepcopy(base)
        call["binding"]["state_ids"] = ["s0"]
        call["certificate"]["binding"] = deepcopy(call["binding"])
        reject("singleton_nonzero_R0", call, "Singleton")
        call["initial"] = [0, 2]
        reject("singleton_nonzero_gr", call, "Singleton")
        call = deepcopy(base)
        call["tau"] = Fraction(1, 8)
        call["certificate"]["tau"] = call["tau"]
        call["source_knots"] = [Fraction(0)] + [Fraction(i, 100000) for i in range(1, 192)] + [Fraction(1)]
        call["observation_knots"] = [0, 1]
        reject("overlap_term_resource_limit", call, "200000")

        saved = result["hd_cases"][0]["variants"]["aligned"]
        cap_base = {k: deepcopy(saved["parameters"][k]) for k in ("q", "tau", "c", "d", "initial", "binding", "certificate")}
        cap_base.update(g_r=saved["source"]["g_r"], g_e=saved["source"]["g_e"],
                        source_knots=saved["source"]["knots"], observation_knots=saved["requested_times"],
                        cap_source_bytes=source_bytes["R11_primary"], cap_case_id=spec["hd_case_ids"][0])
        call = deepcopy(cap_base)
        call["cap_source_bytes"] = call["cap_source_bytes"][:-1] + b"X"
        reject("cap_original_bytes_required", call, "SHA256 mismatch")
        call = deepcopy(cap_base)
        call["cap_source_bytes"] = {"source_sha256": SOURCE_HASHES["R11_primary"], "upper": [[1, 1]]}
        reject("metadata_only_caps_rejected", call, "Original R11 result bytes")
        call = deepcopy(cap_base)
        call["cap_case_id"] = "unknown"
        reject("unknown_cap_case", call, "case ID")
        call = deepcopy(cap_base)
        call["cap_case_id"] = spec["hd_case_ids"][1]
        reject("different_known_cap_case", call, "binding mismatch")
        for key, value, name in (("clock", "other clock", "cap_clock_binding"),
                                 ("family_id", "other family", "cap_family_binding"),
                                 ("state_ids", list(reversed(cap_base["binding"]["state_ids"])), "cap_state_order")):
            call = deepcopy(cap_base)
            call["binding"][key] = value
            call["certificate"]["binding"] = deepcopy(call["binding"])
            reject(name, call, "binding mismatch")
        call = deepcopy(cap_base)
        call["q"] = (call["q"] + 1) / 2
        call["certificate"]["q"] = call["q"]
        reject("cap_q_identity", call, "binding mismatch")
        call = deepcopy(cap_base)
        call["g_r"] = [Q(call["g_r"][0]) + 1]
        reject("cap_whole_forcing_identity", call, "Forcing function differs")
        call = deepcopy(cap_base)
        shortened = call["source_knots"][-1] - call["tau"] / 10
        call["source_knots"] = [call["source_knots"][0], shortened]
        call["observation_knots"] = [call["observation_knots"][0], shortened]
        reject("cap_clock_coverage_gap", call, "coverage")
        check("no_predecessor_module_imports", not any(name.startswith("wu_r11") or "full_generator_blocks" in name for name in sys.modules))
        result["first_failure"] = None
    except Exception as exc:
        result["first_failure"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        check("uncaught_exception", False, str(exc))
    result["check_count"] = len(result["checks"])
    result["failure_count"] = sum(x["status"] != "PASS" for x in result["checks"])
    result["status"] = "PASS" if result["failure_count"] == 0 else "FAIL"
    result["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["internal_CPU_before_serialization_s"] = time.process_time() - cpu0
    result["internal_wall_before_serialization_s"] = time.monotonic() - wall0
    result["complete_process_CPU_authority"] = "external execute_once OS rusage including imports and serialization"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(serialize(result), ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": result["check_count"], "failures": result["failure_count"],
                      "CPU_before_serialization_s": result["internal_CPU_before_serialization_s"]}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
