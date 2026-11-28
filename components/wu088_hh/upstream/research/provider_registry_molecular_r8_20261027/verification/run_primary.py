#!/usr/bin/env python3
"""Fixed R8 primary: four retained HD fixtures and five analytic controls.

No old runner, new generator, ODE solve, or adaptive parameter search.
Reconstructed from the frozen authoring design after transient-store loss;
the actual file digest, rather than the unpublished authoring digest, binds it.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time
import traceback

LEAF = Path(__file__).resolve().parents[1]
RESEARCH = LEAF.parent
OUT = LEAF / "raw/PRIMARY_RESULTS.json"
INPUT_SHA = "b47d561f1dc77c42a16544df0f59066b17d1bf8a50430a3ac5ba25845068e84c"
CORE_SHA = "3a415e8ccc76669a95bec30aa52fc1f1ad867cff1fd9fcca66734fb71872fba3"
PROOF_SHA = "643e9c918353c068e648e5c74290a608b9993be487d7f4773278880db1a7c51c"
PARENT = "c1badb7de44131715a4998d76515506da5573707"
PATHS = {
    "R6_primary": "provider_registry_molecular_r6_20261027/raw/PRIMARY_RESULTS.json",
    "R7_primary": "provider_registry_molecular_r7_20261027/raw/PRIMARY_RESULTS.json",
    "R7_reference": "provider_registry_molecular_r7_20261027/raw/REFERENCE_RESULTS.json",
    "R7_core": "provider_registry_molecular_r7_20261027/src/nonlinear_feedback.py",
}
CHECKS = []

def utc(): return datetime.now(timezone.utc).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def Q(value):
    if isinstance(value, (bool, float)): raise ValueError("Exact scalar required")
    return Fraction(value)
def export(value):
    if isinstance(value, Fraction): return str(value)
    if isinstance(value, dict): return {str(k): export(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [export(v) for v in value]
    return value
def flat(value):
    if isinstance(value, (tuple, list)):
        for item in value: yield from flat(item)
    else: yield value
def eq(left, right):
    if isinstance(left, (list, tuple)) or isinstance(right, (list, tuple)):
        return (isinstance(left, (list, tuple)) and isinstance(right, (list, tuple))
                and len(left) == len(right) and all(eq(a, b) for a, b in zip(left, right)))
    return Q(left) == Q(right)
def check(name, good, evidence=None):
    CHECKS.append({"name": name, "status": "PASS" if good else "FAIL", "evidence": evidence or {}})
    return bool(good)
def require(name, good, evidence=None):
    if not check(name, good, evidence): raise ValueError(name)
def preserved_exception(name, exc):
    check(name, False, {"exception": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
def pointer(document, path):
    for key in path.split("/")[1:]:
        key = key.replace("~1", "/").replace("~0", "~")
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document
def binding(clock, family, states, source):
    return {"clock": clock, "family_id": family, "state_ids": list(states), "source_sha256": source,
            "norm": "l1_on_kerP", "generator_scope": "nominal_K", "uniform_all_starts": True,
            "nonexpansive": True, "same_family_composition": True}

def validate(name, cert):
    n = cert["cells"]; h = cert["kernel"]["h"]; previous = cert["baseline_cells"]; ends = None
    require(name + "/fixed_two_passes", [p["pass"] for p in cert["passes"]] == [1, 2])
    check(name + "/lag_nonnegative_monotone", len(h) == n + 1 and h[0] == 1
          and all(0 <= h[k] <= h[k - 1] <= 1 for k in range(1, n + 1)))
    for p in cert["passes"]:
        tag = name + "/pass" + str(p["pass"])
        require(tag + "/shapes", all(len(p[k]) == size for k, size in
                (("whole_cells", n), ("raw_endpoints", n + 1), ("endpoints", n + 1), ("F_upper", n), ("L_upper", n))))
        check(tag + "/nonnegative", all(x >= 0 for k in
              ("whole_cells", "raw_endpoints", "endpoints", "F_upper", "L_upper") for x in flat(p[k])))
        check(tag + "/exact_whole_descent", all(a <= Q(b) for a, b in zip(flat(p["whole_cells"]), flat(previous))))
        count = sum(a < Q(b) for a, b in zip(flat(p["whole_cells"]), flat(previous)))
        check(tag + "/strict_count", count == p["strictly_tightened_cell_components"], {"count": count})
        if ends is not None:
            check(tag + "/endpoint_descent", all(a <= b for a, b in zip(flat(p["endpoints"]), flat(ends))))
        check(tag + "/all_exact_saved_caps", all(p["endpoints"][c["index"]][k] <= Q(c["upper"][k])
              for c in cert["cap_provenance"] for k in (0, 1)))
        previous, ends = p["whole_cells"], p["endpoints"]
    check(name + "/final_aliases", eq(cert["whole_cells"], previous) and eq(cert["endpoints"], ends))
    check(name + "/conditional_scope", cert["physical_consumer_admitted"] is False and cert["new_generator_or_ODE_calls"] == 0)

def retained_hd(index, case, r6, r7, frozen, report):
    name = case["id"]; H, rho = Q(case["H"]), Q(case["rho"]); delta = H / 64
    coeff = case["coefficients"]; meta = coeff["metadata"]; oldbind = case["binding"]
    initial = [case["initial_error"]["R"], case["initial_error"]["E"]]
    require(name + "/retained_invariant_compatibility", meta["initial_invariant_compatibility"] is True)
    require(name + "/retained_nominal_binding", oldbind["clock"] == meta["clock"] and oldbind["norm"] == "l1_on_kerP"
            and oldbind["generator_scope"] == "nominal_K" and oldbind["feedback_accounted"] is True
            and Q(oldbind["H"]) == H and Q(oldbind["rho"]) == rho)
    native = index == 3
    common = binding(meta["clock"], "R6_native100K_paraH2_interval_family" if native else
                     "R7_symmetric_two_state_nominal_family", meta["state_ids"],
                     frozen["source_sha256"]["R6_primary" if native else "R7_primary"])
    evidence = {"id": name, "binding": common, "old_binding": oldbind, "physical_consumer_admitted": False}
    if native:
        graph = r6["graph"]; blocks = sorted(graph["blocks"], key=lambda x: Q(x["H"]))
        require(name + "/four_shared_native_certificates", len(blocks) == 4 and all(
                Q(b["lambda"]) == Q(graph["lambda"]) and eq(b["P_lower"], graph["P_lower"]) for b in blocks))
        require(name + "/native_steps", [Q(b["H"]) / delta for b in blocks] == frozen["native_steps"])
        require(name + "/native_macro_pair", H == Q(blocks[-1]["H"]) and rho == Q(blocks[-1]["rho_upper"]))
        reuse = case["reuse"]
        require(name + "/native_saved_reuse", reuse["sha256"] == frozen["source_sha256"]["R6_primary"]
                and reuse["source_sha256"] == r6["thermal"]["source_sha256"] and reuse["graph_block_id"] == blocks[-1]["id"]
                and reuse["K_interval_midpoint"] is True and reuse["rho_and_H_reused_without_R6_execution"] is True
                and reuse["actual_native_chemical_densities_or_rates"] is False)
        K, lo, hi = case["K"], graph["K_lo"], graph["K_hi"]
        require(name + "/native_matrix_shape", len(K) == len(lo) == len(hi) == 9
                and all(len(row) == 9 for mat in (K, lo, hi) for row in mat))
        require(name + "/saved_K_box_midpoint_identity", all(Q(lo[i][j]) <= Q(K[i][j]) <= Q(hi[i][j])
                and 2 * Q(K[i][j]) == Q(lo[i][j]) + Q(hi[i][j]) for i in range(9) for j in range(9)))
        require(name + "/native_order_identity", r6["thermal"]["level_ids"] == list(range(1, 10))
                and meta["state_ids"] == ["HD_state_" + str(i) for i in range(9)])
        certificates = [{"id": b["id"], "H": b["H"], "rho": b["rho_upper"], "binding": common} for b in blocks]
        evidence.update(all_starts_proof={"sha256": PROOF_SHA, "sections": "2.1-2.3",
                        "scope": "Shared interval nominal family; uniform every-start bound and nonexpansive remainder"},
                        source_clock=graph["clock"], state_order_mapping=list(zip(r6["thermal"]["level_ids"], meta["state_ids"])),
                        source_clock_scope="Saved dimensionless mathematical identification; physical density remains unbound")
    else:
        require(name + "/saved_symmetric_pair", eq(case["K"], [[-1, 1], [1, -1]]) and H == Fraction(1, 4) and rho == Fraction(5, 8))
        oldcheck = "hd/" + name + "/analytic_two_state_nominal_rho"
        require(name + "/saved_analytic_admission", any(c["name"] == oldcheck and c["status"] == "PASS" for c in r7["checks"]))
        certificates = [{"id": case["certificate_id"], "H": H, "rho": rho, "binding": common}]
        evidence["all_starts_evidence"] = {"source_sha256": frozen["source_sha256"]["R7_primary"],
                                           "saved_check": oldcheck, "time_independent_nominal_K": True}
    require(name + "/three_saved_blocks", len(case["blocks"]) == 3)
    baseline, caps, previous = [], [], initial
    for bi, block in enumerate(case["blocks"]):
        bc = block["certificate"]; prefix = f"/hd_cases/{index}/blocks/{bi}"
        require(name + f"/block{bi}/binding", block["index"] == bi and Q(block["t0"]) == bi * H
                and eq(bc["B"], coeff["B"]) and eq(bc["g"], coeff["g"]) and Q(bc["H"]) == H
                and Q(bc["rho"]) == rho and bc["binding"] == oldbind
                and eq(block["w0"], previous) and eq(bc["w0"], previous))
        require(name + f"/block{bi}/five_saved_queries", [Q(q["t"]) for q in block["queries"]] == [H * k / 4 for k in range(5)])
        baseline.extend([deepcopy(bc["whole_block_upper"]) for _ in range(64)])
        for qi, query in enumerate(block["queries"]):
            caps.append({"time": Q(block["t0"]) + Q(query["t"]), "upper": deepcopy(query["bound"]),
                         "source_kind": "saved_R7_query", "source_sha256": frozen["source_sha256"]["R7_primary"],
                         "source_pointer": prefix + f"/queries/{qi}/bound"})
        caps.append({"time": (bi + 1) * H, "upper": deepcopy(bc["w_next_upper"]),
                     "source_kind": "saved_R7_endpoint", "source_sha256": frozen["source_sha256"]["R7_primary"],
                     "source_pointer": prefix + "/certificate/w_next_upper"})
        previous = bc["w_next_upper"]
    require(name + "/eighteen_exact_caps", len(caps) == 18 and all(eq(pointer(r7, c["source_pointer"]), c["upper"])
            and (c["time"] / delta).denominator == 1 for c in caps))
    require(name + "/exact_saved_whole_baseline", len(baseline) == 192 and all(eq(baseline[n],
            case["blocks"][n // 64]["certificate"]["whole_block_upper"]) for n in range(192)))
    report["binding_evidence"].append(evidence)
    return coeff["B"], coeff["g"], delta, initial, baseline, certificates, common, caps

def guards(core, common, frozen):
    delta = Fraction(1, 8); cert = {"id": "guard", "H": "1/4", "rho": "1/2", "binding": common}
    def ladder(**kwargs):
        args = {"delta": delta, "cells": 8, "certificates": [cert], "binding": common}; args.update(kwargs)
        return core.kernel_ladder(**args)
    def run(**kwargs):
        args = {"B": [[0, 0], [0, 0]], "g": [0, 0], "delta": delta, "initial": [1, 1],
                "baseline_cells": [[2, 2]] * 8, "certificates": [cert], "binding": common}; args.update(kwargs)
        return core.volterra_two_pass(**args)
    cap = {"time": 0, "upper": [1, 1], "source_kind": "saved_R7_query", "source_pointer": "/guard",
           "source_sha256": frozen["source_sha256"]["R7_primary"]}
    actions = [("binary_float", lambda: core.Q(0.5)), ("zero_delta", lambda: ladder(delta=0)),
               ("too_many_cells", lambda: ladder(cells=193)),
               ("noncommensurate_H", lambda: ladder(certificates=[{**cert, "H": "1/3"}])),
               ("rho_above_one", lambda: ladder(certificates=[{**cert, "rho": "9/8"}])),
               ("clock_mismatch", lambda: ladder(certificates=[{**cert, "binding": {**common, "clock": "other"}}])),
               ("all_starts_missing", lambda: ladder(binding={**common, "uniform_all_starts": False})),
               ("reactive_generator_scope", lambda: ladder(binding={**common, "generator_scope": "full_reactive"})),
               ("exp_argument_outside_domain", lambda: core.coarse_step_factors(17, 1)),
               ("negative_coupling", lambda: run(B=[[0, -1], [0, 0]])),
               ("negative_forcing", lambda: run(g=[-1, 0])),
               ("initial_excluded", lambda: run(baseline_cells=[[0, 0]] * 8)),
               ("reference_actual_cap", lambda: run(point_caps=[{**cap, "source_kind": "reference_actual"}])),
               ("off_grid_cap", lambda: run(point_caps=[{**cap, "time": "1/17"}]))]
    for name, action in actions:
        try: action()
        except core.DomainError as exc: check("guard/" + name, True, {"exception": str(exc)})
        except Exception as exc: preserved_exception("guard/" + name, exc)
        else: check("guard/" + name, False, {"reason": "invalid input was accepted"})

def run(report):
    require("no_adaptive_arguments", len(sys.argv) == 1)
    input_raw = (LEAF / "verification/PRIMARY_INPUT.json").read_bytes()
    core_path = LEAF / "src/volterra_feedback.py"; core_raw = core_path.read_bytes()
    require("frozen_input_sha256", sha(input_raw) == INPUT_SHA); require("frozen_core_sha256", sha(core_raw) == CORE_SHA)
    frozen = json.loads(input_raw); report.update(input_sha256=sha(input_raw), core_sha256=sha(core_raw))
    report["source_sha256"] = {"R8_input": sha(input_raw), "R8_core": sha(core_raw)}; saved = {}
    for key, path in PATHS.items():
        raw = (RESEARCH / path).read_bytes(); digest = sha(raw); report["source_sha256"][key] = digest
        require("frozen_source/" + key, digest == frozen["source_sha256"][key])
        if key != "R7_core": saved[key] = json.loads(raw)
    proof = (RESEARCH / "provider_registry_molecular_r6_20261027/theory/INTERVAL_BLOCK_PROOF_KO.md").read_bytes()
    report["source_sha256"]["R6_all_starts_proof"] = sha(proof); require("frozen_all_starts_proof", sha(proof) == PROOF_SHA)
    require("fixed_grid_and_scope", frozen["parent_commit"] == PARENT and [frozen[k] for k in
            ("cells_per_macro", "macro_blocks", "cells", "passes", "bits")] == [64, 3, 192, 2, 128]
            and frozen["native_steps"] == [2, 8, 32, 64] and frozen["new_ODE_runs"] == 0 and frozen["physical_consumer_admitted"] is False)
    r6, r7, ref = (saved[k] for k in ("R6_primary", "R7_primary", "R7_reference"))
    require("saved_R6_admission", r6["status"] == "PASS_SCOPED_EXACT_CERTIFICATES" and r6["failure_count"] == 0)
    require("saved_R7_admission", r7["status"] == "PASS" and r7["failure_count"] == 0 and r7["core_sha256"] == frozen["source_sha256"]["R7_core"])
    require("saved_reference_binding", ref["status"] == "PASS" and ref["failure_count"] == 0 and ref["primary_sha256"] == frozen["source_sha256"]["R7_primary"])
    require("fixed_HD_order", [c["id"] for c in r7["hd_cases"]] == frozen["hd_cases"])
    spec = importlib.util.spec_from_file_location("wu_r8_fixed_primary_core", core_path)
    if spec is None or spec.loader is None: raise ImportError("Cannot load frozen R8 core")
    core = importlib.util.module_from_spec(spec); sys.modules[spec.name] = core; spec.loader.exec_module(core)
    for i, case in enumerate(r7["hd_cases"]):
        try:
            B, g, delta, initial, baseline, certs, common, caps = retained_hd(i, case, r6, r7, frozen, report)
            result = core.volterra_two_pass(B, g, delta, initial, baseline, certs, binding=common, point_caps=caps, bits=128)
            report["hd_cases"].append({"id": case["id"], "certificate": result}); validate(case["id"], result)
            old = case["blocks"][-1]["certificate"]["w_next_upper"]
            report["binding_evidence"][-1]["final_comparison"] = {"saved_R7_endpoint": old, "R8_endpoint": result["endpoints"][-1],
                "strict_components": [result["endpoints"][-1][k] < Q(old[k]) for k in (0, 1)]}
        except Exception as exc: preserved_exception("HD/" + case["id"], exc)
    common = binding("dimensionless analytic control", "R8_declared_analytic_control_family",
                     ["control_state_0", "control_state_1"], INPUT_SHA)
    delta = Q(frozen["control_grid"]["delta"]); n = frozen["control_grid"]["cells"]
    require("fixed_control_grid", delta == Fraction(1, 8) and n == 8 and frozen["control_grid"]["passes"] == 2)
    for item in frozen["controls"]:
        name = item["id"]
        try:
            certs = [{"id": name, "H": delta * item["steps"], "rho": item["rho"], "binding": common}]
            result = core.volterra_two_pass(item["B"], item["g"], delta, item["initial"], [item["baseline_pair"]] * n, certs, binding=common)
            report["controls"].append({"id": name, "certificate": result}); validate("control/" + name, result)
            h = result["kernel"]["h"]; ends = result["endpoints"]
            check("control/" + name + "/closed_lag", all(h[k] == Q(item["rho"]) ** (k // item["steps"]) for k in range(n + 1)))
            if name == "noforcing": check("control/noforcing/closed_endpoint", eq(ends, [[2 * h[k], 3] for k in range(n + 1)]))
            elif name == "constantforcing":
                check("control/constantforcing/closed_endpoint", eq(ends, [[h[k] + 2 * delta * sum(h[:k]), 1 + 3 * k * delta] for k in range(n + 1)]))
                check("control/constantforcing/current_cell_h0", eq(result["whole_cells"][0], [1 + 2 * delta, 1 + 3 * delta]))
            elif name == "nilpotent": check("control/nilpotent/closed_endpoint", eq(ends, [[1 + 2 * k * delta, 2] for k in range(n + 1)]))
            else:
                e = result["coarse_factors"]["e_upper"]
                check("control/" + name + "/signed_exponential", e < 1 if name == "negative_d" else e > 1)
                check("control/" + name + "/baseline_contains_endpoints", all(v <= Q(item["baseline_pair"][k]) for row in ends for k, v in enumerate(row)))
        except Exception as exc: preserved_exception("control/" + name, exc)
    guards(core, common, frozen)
    late = deepcopy(r7["late_forcing"])
    require("retained_late_forcing_fixed_input", all(Q(late[k]) == Q(v) for k, v in frozen["late_forcing"].items()))
    check("retained_late_forcing_strict_violation", Q(late["strict_gap_lower"]) > 0
          and Q(late["correct_forcing_interval"][0]) > Q(late["wrong_forcing_upper"]))
    late["reused_R7_counterexample"] = {"source_sha256": frozen["source_sha256"]["R7_primary"], "source_pointer": "/late_forcing",
        "new_exp_evaluations": 0, "new_current_cell_check": "control/constantforcing/current_cell_h0"}; report["late_forcing"] = late
    check("every_fixed_case_persisted", len(report["hd_cases"]) == 4 and len(report["controls"]) == 5)

def main():
    wall_start = time.monotonic()
    if OUT.exists(): print('{"status":"FAIL","reason":"create-only output already exists"}'); return 2
    report = {"schema": "WU_R8_PRIMARY_RESULTS_V1", "started_utc": utc(), "parent_commit": PARENT,
              "runner_sha256": sha(Path(__file__).read_bytes()), "checks": CHECKS, "hd_cases": [], "controls": [], "binding_evidence": [],
              "budget": {"primary_runs": 1, "CPU_limit_s": 60, "passes": 2, "bits": 128},
              "scope": {"new_primary_runs_consumed": 1, "old_science_replay": 0, "new_ODE_runs": 0,
                        "new_generator_construction": 0, "physical_consumer_admitted": False}}
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
        limits = [60] + [v for v in (soft, hard) if v != resource.RLIM_INFINITY]
        bound = min(limits); resource.setrlimit(resource.RLIMIT_CPU, (bound, bound)); run(report)
    except Exception as exc: preserved_exception("primary_run_exception", exc)
    check("CPU_before_serialization", time.process_time() <= 60)
    failures = [c for c in CHECKS if c["status"] == "FAIL"]
    report.update(status="FAIL" if failures else "PASS", failure_count=len(failures), check_count=len(CHECKS),
                  first_failure=failures[0] if failures else None, finished_utc=utc(), actual_process_CPU_s=time.process_time(),
                  CPU_includes_Python_and_library_imports=True, actual_wall_s=time.monotonic() - wall_start,
                  complete_process_CPU_authority="External Actions wrapper includes output serialization and process shutdown")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x", encoding="utf-8") as handle: handle.write(json.dumps(export(report), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "check_count", "failure_count")}))
    return 1 if failures else 0

if __name__ == "__main__": raise SystemExit(main())
