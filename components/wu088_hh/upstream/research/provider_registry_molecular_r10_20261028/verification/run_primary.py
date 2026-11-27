"""Single frozen R10 primary pass; no predecessor module or ODE execution."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import sys
import time
import traceback

BASE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
CORE = BASE / "src/full_generator_triangular.py"
INPUT = BASE / "verification/PRIMARY_INPUT.json"
FREEZE = BASE / "raw/PREEXECUTION_FREEZE.json"
OUT = BASE / "raw/PRIMARY_RESULTS.json"
SOURCE_HASHES = {
    "R7_input": "3ff9c2535e5c0ce6ffa5e9671de15aad6649e0996cd9b9e275cc290facd8d330",
    "R7_primary": "6eaf3c0eed7968cf4023180e15373a180bb5b1bab2e56cd4a8547387ed337a15",
    "R9_primary": "494fad7b2195dfbf16857901127cdaa676d83cb1beafbf2c081122f99ba2d8d7",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within_repo(relative):
    p = (REPO / relative).resolve()
    if not p.is_relative_to(REPO.resolve()):
        raise ValueError("Input path escapes the repository")
    return p


def main():
    if OUT.exists():
        raise SystemExit("Refuse to overwrite the first primary result")
    cpu0, wall0 = time.process_time(), time.monotonic()
    result = {
        "schema": "WU_R10_PRIMARY_RESULTS_V1", "unit": "WU_FULL_GENERATOR_TRIANGULAR_R10",
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "input_sha256": digest(INPUT), "core_sha256": digest(CORE),
        "runner_sha256": digest(Path(__file__)), "checks": [], "hd_cases": [], "controls": [],
        "scope": {"old_science_replay": 0, "new_ODE_runs": 0, "predecessor_module_imports": 0,
                  "physical_consumer_admitted": False, "lower_arrays": "ideal comparison only; never physical-error lower bounds"},
        "budget": {"primary_runs": 1, "CPU_limit_s": 60, "wall_limit_s": 90, "bits": 128, "degree": 96},
    }
    module = None

    def check(name, ok, evidence=None):
        result["checks"].append({"name": name, "status": "PASS" if bool(ok) else "FAIL", "evidence": evidence})

    def require(name, ok, evidence=None):
        check(name, ok, evidence)
        if not ok:
            raise ValueError("Required source/contract assertion failed: " + name)

    def time_guard():
        if time.process_time() - cpu0 > 58 or time.monotonic() - wall0 > 88:
            raise RuntimeError("Primary run reached the bounded pre-finalization stop")

    try:
        freeze = json.loads(FREEZE.read_text())
        if freeze.get("status") != "PASS" or not isinstance(freeze.get("files"), list):
            raise ValueError("Successful source freeze is required before execution")
        frozen = {}
        for item in freeze["files"]:
            path = within_repo(item["path"])
            raw = path.read_bytes()
            if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("Frozen bytes differ: " + item["path"])
            frozen[item["path"]] = item["sha256"]
        required = [CORE.relative_to(REPO).as_posix(), INPUT.relative_to(REPO).as_posix(),
                    Path(__file__).resolve().relative_to(REPO).as_posix()]
        require("preexecution_freeze_membership", all(p in frozen for p in required), required)
        result["freeze_sha256"] = digest(FREEZE)
        spec = json.loads(INPUT.read_text())
        require("fixed_primary_contract", spec.get("schema") == "WU_R10_FIXED_PRIMARY_INPUT_V1" and
                spec.get("unit") == result["unit"] and spec.get("bits") == 128 and
                spec.get("degree") == 96 and spec.get("hd_cells") == 192 and
                spec.get("modes") == ["raw", "capped"])
        source = {}
        for name, sha in SOURCE_HASHES.items():
            rec = spec["sources"][name]
            path = within_repo(rec["path"])
            require("source_" + name + "_identity", rec["sha256"] == sha and digest(path) == sha and
                    frozen.get(rec["path"]) == sha, {"path": rec["path"], "sha256": sha})
            source[name] = json.loads(path.read_text())
        result["source_sha256"] = SOURCE_HASHES
        require("saved_primary_results_pass", source["R7_primary"]["status"] == "PASS" and
                source["R9_primary"]["status"] == "PASS")
        expected_ids = spec["hd_case_ids"]
        require("same_saved_case_order", all([x["id"] for x in source[n]["hd_cases"]] == expected_ids
                for n in ("R7_input", "R7_primary", "R9_primary")))
        loader = importlib.util.spec_from_file_location("wu_r10_frozen_core", CORE)
        module = importlib.util.module_from_spec(loader)
        sys.modules[loader.name] = module
        loader.loader.exec_module(module)
        Q = module.Q
        epsilon = Fraction(1, 1 << 128)

        def invariants(y):
            u, v, w, X = y
            return 2*u+w+X, v+X, v+w

        source_fields = ("id", "K", "pi", "alpha", "kf", "destruction", "coarse_kf_offset", "H", "rho",
                         "initial_fine", "initial_coarse", "density_box", "q_norm_upper",
                         "branch_distance_upper", "coarse_scalar_defect_upper", "source_map_identity", "source_scope")
        for i, fixture in enumerate(source["R7_input"]["hd_cases"]):
            time_guard()
            old = source["R7_primary"]["hd_cases"][i]
            saved = source["R9_primary"]["hd_cases"][i]["capped"]
            ident = fixture["id"]
            require(ident + ":saved_fixture_fields", all(fixture[k] == old[k] for k in source_fields))
            p = tuple(map(Q, fixture["pi"]))
            alpha = tuple(map(Q, fixture["alpha"]))
            ds = tuple(map(Q, fixture["destruction"]))
            K = tuple(tuple(map(Q, row)) for row in fixture["K"])
            fine = tuple(map(Q, fixture["initial_fine"]))
            coarse = tuple(map(Q, fixture["initial_coarse"]))
            aggregate = fine[:3] + (sum(fine[3:]),)
            eta = aggregate[3] - coarse[3]
            R0 = sum(abs(fine[j+3] - p[j]*aggregate[3]) for j in range(len(p)))
            require(ident + ":same_initial_invariant_class", invariants(aggregate) == invariants(coarse) and
                    tuple(a-b for a, b in zip(aggregate, coarse)) == (-eta, -eta, eta, eta) and
                    R0 == Q(old["initial_error"]["R"]) and abs(eta) == Q(old["initial_error"]["E"]) and
                    sum(fine[j+3] - p[j]*aggregate[3] for j in range(len(p))) == 0)
            require(ident + ":simplex_and_positive_state", sum(p) == 1 and sum(alpha) == 1 and
                    min(p+alpha+fine+coarse) >= 0)
            box = {k: tuple(map(Q, fixture["density_box"][k])) for k in ("u", "v", "w", "X")}
            # This fixed R7 invariant class has u=v=3/2-X and w=1/2+X.
            require(ident + ":whole_invariant_box_exact", invariants(aggregate) == (Fraction(7,2), Fraction(3,2), Fraction(2)) and
                    box == {"u": (0, Fraction(3,2)), "v": (0, Fraction(3,2)),
                            "w": (Fraction(1,2), 2), "X": (0, Fraction(3,2))})
            actual_q = sum(abs(sum(K[j][k]*p[k] for k in range(len(p)))) for j in range(len(p)))
            actual_theta = sum(abs(a-b) for a, b in zip(alpha, p))
            qstar, theta = Q(fixture["q_norm_upper"]), Q(fixture["branch_distance_upper"])
            require(ident + ":q_theta_upper", actual_q <= qstar and actual_theta <= theta <= 2)
            mu, mv, mw, mx = (box[k][0] for k in ("u", "v", "w", "X"))
            Mu, Mv, Mw, MX = (box[k][1] for k in ("u", "v", "w", "X"))
            rate, spread = Q(fixture["kf"]), max(ds)-min(ds)
            fresh = {"c": Mw*spread/2, "d": -(rate*(mu+mv)+min(ds)*(mw+mx)),
                     "g_r": qstar*MX + rate*Mu*Mv*theta + Mw*MX*spread/2,
                     "g_e": Q(fixture["coarse_scalar_defect_upper"])}
            coeff = old["coefficients"]
            require(ident + ":unchanged_R7_whole_domain_coefficients", all(fresh[k] == Q(coeff[k]) for k in fresh))
            require(ident + ":R9_actual_same_case_grid_inputs", saved["cells"] == 192 and
                    Q(saved["delta"]) == Q(fixture["H"])/64 and tuple(map(Q, saved["initial"])) == (R0, abs(eta)) and
                    tuple(map(Q, saved["g"])) == (fresh["g_r"], fresh["g_e"]) and
                    Q(saved["B"][1][0]) == fresh["c"] and Q(saved["B"][1][1]) == fresh["d"] and
                    saved["binding"]["clock"] == coeff["metadata"]["clock"] and
                    saved["binding"]["state_ids"] == coeff["metadata"]["state_ids"])
            args = {"K": fixture["K"], "pi": fixture["pi"], "destruction": fixture["destruction"],
                    "w_box": fixture["density_box"]["w"], **fresh, "delta": saved["delta"],
                    "initial": saved["initial"], "cells": 192, "binding": saved["binding"]}
            record = {"id": ident, "source_pointers": {"R7_input": f"/hd_cases/{i}",
                       "R7_primary": f"/hd_cases/{i}", "R9_primary": f"/hd_cases/{i}/capped"}}
            before = json.dumps(args, default=str, sort_keys=True)
            for mode in ("raw", "capped"):
                call = deepcopy(args)
                if mode == "capped":
                    for arg, kind in (("whole_caps", "whole_cells"), ("point_caps", "endpoints")):
                        call[arg] = {"source_kind": "saved_R9_"+kind, "source_sha256": SOURCE_HASHES["R9_primary"],
                                     "source_pointer": f"/hd_cases/{i}/capped/{kind}", "delta": saved["delta"],
                                     "cells": 192, "binding": deepcopy(saved["binding"]), "upper": saved[kind]}
                out = module.sweep(**call)
                record[mode] = out
                tag = ident + ":" + mode
                check(tag + ":geometry", len(out["endpoints_upper"]) == 193 and len(out["whole_cells_upper"]) == 192)
                check(tag + ":nonnegative", all(x >= 0 for key in ("endpoints_upper", "whole_cells_upper") for pair in out[key] for x in pair))
                check(tag + ":initial", tuple(out["endpoints_upper"][0]) == (R0, abs(eta)))
                check(tag + ":closed_cell_covers_reported_right_endpoint", all(out["endpoints_upper"][n+1][k] <= out["whole_cells_upper"][n][k] for n in range(192) for k in (0,1)))
                check(tag + ":full_generator_no_rho_transfer", not out["generator"]["nominal_K_block_rho_transferred"] and
                      out["generator"]["lambda"] >= out["generator"]["separate_sum_lower"] >= 0)
                if mode == "raw":
                    check(tag + ":ideal_comparison_interval_order", all(out["endpoints_lower"][n][k] <= out["endpoints_upper"][n][k] for n in range(193) for k in (0,1)))
                else:
                    check(tag + ":no_physical_error_lower", out["endpoints_lower"] is None)
                    check(tag + ":R9_point_no_worse", all(out["endpoints_upper"][n][k] <= Q(saved["endpoints"][n][k]) for n in range(193) for k in (0,1)))
                    check(tag + ":R9_whole_no_worse", all(out["whole_cells_upper"][n][k] <= Q(saved["whole_cells"][n][k]) for n in range(192) for k in (0,1)))
            check(ident + ":source_object_unchanged", before == json.dumps(args, default=str, sort_keys=True))
            record["generator"] = record["raw"]["generator"]
            record["coefficients"] = record["raw"]["coefficients"]
            record["comparison"] = {"R9_final": saved["endpoints"][-1], "raw_final": record["raw"]["endpoints_upper"][-1],
                                     "capped_final": record["capped"]["endpoints_upper"][-1]}
            for mode in ("raw", "capped"):
                for target, source_key in (("endpoints_upper", "endpoints"), ("whole_cells_upper", "whole_cells")):
                    pairs = [(a, Q(b)) for aa, bb in zip(record[mode][target], saved[source_key]) for a, b in zip(aa, bb)]
                    record["comparison"][mode+"_"+source_key+"_counts"] = {
                        "less": sum(a < b for a,b in pairs), "equal": sum(a == b for a,b in pairs), "greater": sum(a > b for a,b in pairs)}
            result["hd_cases"].append(record)

        control_bind = {"family_id": "R10_exact_analytic_controls", "state_ids": ["r0", "r1"],
                        "source_sha256": result["input_sha256"], "clock": "dimensionless exact control clock", "norm": "l1_on_kerP"}
        for control in spec["controls"]:
            time_guard()
            pars = {k: control[k] for k in ("lam", "c", "d", "g_r", "g_e", "delta", "initial", "cells")}
            lam = Q(pars["lam"])
            args = {k: v for k,v in pars.items() if k != "lam"}
            args.update(K=((-lam/2, lam/2), (lam/2, -lam/2)), pi=("1/2", "1/2"),
                        destruction=(0,0), w_box=(0,1), binding=control_bind)
            out = module.sweep(**args)
            record = {"id": control["id"], "parameters": pars, "raw": out}
            result["controls"].append(record)
            tag = "control:" + control["id"]
            check(tag + ":lambda", out["generator"]["lambda"] == lam)
            check(tag + ":geometry_initial", len(out["endpoints_upper"]) == pars["cells"]+1 and out["endpoints_upper"][0] == tuple(map(Q, pars["initial"])))
            check(tag + ":interval_order", all(0 <= lo <= hi for a,b in zip(out["endpoints_lower"], out["endpoints_upper"]) for lo,hi in zip(a,b)))
            flow = out["flow_interval"]
            check(tag + ":structural_zeros_and_affine_constant", flow["lower"][0][1] == flow["upper"][0][1] == 0 and
                  flow["lower"][2] == flow["upper"][2] == (0,0,1) and not flow["inverse_of_M_used"])
            if lam == 0 and Q(pars["d"]) == 0:
                R0, E0 = map(Q, pars["initial"])
                gr, ge, coupling, dt = (Q(pars[k]) for k in ("g_r", "g_e", "c", "delta"))
                truth = [(R0 + gr*n*dt, E0 + (coupling*R0+ge)*n*dt + coupling*gr*(n*dt)**2/2) for n in range(pars["cells"]+1)]
                check(tag + ":exact_polynomial_solution", all(out["endpoints_lower"][n][k] <= truth[n][k] <= out["endpoints_upper"][n][k]
                      for n in range(pars["cells"]+1) for k in (0,1)))

        base = {"K": ((-1,1),(1,-1)), "pi": ("1/2","1/2"), "destruction": (0,0), "w_box": (0,1),
                "c": 0, "d": 0, "g_r": 0, "g_e": 0, "delta": "1/8", "initial": (1,0), "cells": 1, "binding": control_bind}
        two = module.generator_certificate(base["K"], base["pi"], (2,4), ("1/2",2), binding=control_bind)
        check("generator_two_state_exact_overlap", two["lambda_K"] == 2 and two["lambda_H"] == 3 and two["lambda"] == Fraction(7,2) and two["lambda_at_w_upper"] == 8)
        boundary = module.generator_certificate(((0,0),(0,0)), (1,0), (2,4), (1,2), binding=control_bind)
        check("generator_boundary_simplex", boundary["lambda_H"] == 4 and boundary["lambda"] == 4)
        bind1 = dict(control_bind, state_ids=["only"])
        singleton = module.sweep(((0,),), (1,), (7,), (0,2), 0, -1, 0, 0, "1/8", (0,1), 1, binding=bind1)
        check("singleton_zero_residual_convention", singleton["generator"]["lambda"] == 0 and singleton["generator"]["n1_zero_residual_subspace"] and
              all(pair[0] == 0 for pair in singleton["endpoints_upper"]))
        n = 13
        bind13 = dict(control_bind, state_ids=[f"s{i}" for i in range(n)])
        maxdim = module.generator_certificate([[0]*n for _ in range(n)], [Fraction(1,n)]*n, [1]*n, (1,2), binding=bind13)
        check("generator_dimension13_and_column_conservation", maxdim["lambda"] == 1 and all(sum(row[j] for row in maxdim["H"]) == 0 for j in range(n)))
        forcing = module.sweep(**dict(base, initial=(0,0), g_r=1))
        check("fresh_source_enters_current_cell", forcing["endpoints_lower"][1][0] > 0 and forcing["endpoints_upper"][1][0] < Q(base["delta"]))
        check("directed_one_third", module.down(Fraction(1,3)) <= Fraction(1,3) <= module.up(Fraction(1,3)) and
              module.up(Fraction(1,3))-module.down(Fraction(1,3)) == epsilon)
        huge = Fraction((1 << 8191)+1, (1 << 8191)-1)
        check("exact_rational_8192bit_serialization", Q(module.export(huge)) == huge)

        def reject(name, values):
            try:
                module.sweep(**values)
            except module.DomainError as exc:
                check(name, True, str(exc))
            else:
                check(name, False, "Invalid input was accepted")

        for key, val, tag in (("delta",0,"zero_delta"),("delta",1.0,"binary_float"),("g_r",True,"boolean_scalar"),
                              ("c",-1,"negative_c"),("g_r",-1,"negative_gr"),("g_e",-1,"negative_ge"),
                              ("initial",(-1,0),"negative_initial"),("cells",193,"cell_limit"),("cells",True,"boolean_cells"),
                              ("bits",True,"boolean_bits"),("degree",95,"degree"),("delta",17,"scaled_norm_limit"),
                              ("g_r",1 << 8192,"scalar_bit_limit"),("w_box",(-1,2),"negative_w"),
                              ("w_box",(2,1),"reversed_w"),("w_box",(),"empty_w")):
            reject("guard_"+tag, dict(base, **{key:val}))
        reject("guard_nonconservative_K", dict(base, K=((0,1),(1,-1))))
        reject("guard_nonmetzler_K", dict(base, K=((1,-1),(-1,1))))
        reject("guard_bad_simplex", dict(base, pi=(1,1)))
        reject("guard_negative_pi", dict(base, pi=(-1,2)))
        reject("guard_destruction_dimension", dict(base, destruction=(1,)))
        reject("guard_negative_destruction", dict(base, destruction=(-1,0)))
        reject("guard_bad_norm", dict(base, binding=dict(control_bind,norm="l2")))
        reject("guard_missing_clock", dict(base, binding=dict(control_bind,clock="")))
        reject("guard_duplicate_state_ids", dict(base, binding=dict(control_bind,state_ids=["x","x"])))
        reject("guard_singleton_nonzero_residual", {**base,"K":((0,),),"pi":(1,),"destruction":(0,),"binding":bind1})
        saved = source["R9_primary"]["hd_cases"][0]["capped"]
        old = source["R7_primary"]["hd_cases"][0]
        capped_args = {"K": old["K"], "pi": old["pi"], "destruction": old["destruction"], "w_box": old["density_box"]["w"],
                       "c": old["coefficients"]["c"], "d": old["coefficients"]["d"], "g_r": old["coefficients"]["g_r"],
                       "g_e": old["coefficients"]["g_e"], "delta": saved["delta"], "initial": saved["initial"], "cells":192,"binding":deepcopy(saved["binding"])}
        for arg, kind in (("whole_caps","whole_cells"),("point_caps","endpoints")):
            capped_args[arg] = {"source_kind":"saved_R9_"+kind,"source_sha256":SOURCE_HASHES["R9_primary"],
                                "source_pointer":f"/hd_cases/0/capped/{kind}","delta":saved["delta"],"cells":192,
                                "binding":deepcopy(saved["binding"]),"upper":deepcopy(saved[kind])}
        bad=deepcopy(capped_args);bad["whole_caps"]["source_sha256"]="0"*64;reject("guard_cap_source_sha",bad)
        bad=deepcopy(capped_args);bad["whole_caps"]["source_kind"]="reference_trajectory";reject("guard_reference_sample_cap",bad)
        bad=deepcopy(capped_args);bad["whole_caps"]["delta"]="1/7";reject("guard_cap_grid",bad)
        bad=deepcopy(capped_args);bad["whole_caps"]["binding"]["clock"]="other";reject("guard_cap_clock",bad)
        bad=deepcopy(capped_args);bad["point_caps"]["binding"]["family_id"]="other";reject("guard_cap_family",bad)
        bad=deepcopy(capped_args);bad["point_caps"]["source_pointer"]="/hd_cases/1/capped/endpoints";reject("guard_cap_case_pointer_pair",bad)
        bad=deepcopy(capped_args);bad["point_caps"]["upper"][0][0]="0";reject("guard_cap_initial",bad)
        bad=deepcopy(capped_args);bad["point_caps"]=None;reject("guard_cap_pair_required",bad)
        time_guard()
    except Exception as exc:
        check("unexpected_execution_error", False, {"type":type(exc).__name__,"message":str(exc),"traceback":traceback.format_exc()})
    result["check_count"] = len(result["checks"])
    result["failure_count"] = sum(x["status"] == "FAIL" for x in result["checks"])
    result["status"] = "PASS" if result["failure_count"] == 0 else "FAIL"
    result["first_failure"] = next((x for x in result["checks"] if x["status"] == "FAIL"), None)
    result["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["internal_CPU_before_serialization_s"] = time.process_time() - cpu0
    result["internal_wall_before_serialization_s"] = time.monotonic() - wall0
    result["complete_process_CPU_authority"] = "outer supervisor process record includes imports and serialization"
    def encode(value):
        if isinstance(value, Fraction):
            return str(value)
        if isinstance(value, dict):
            return {str(k):encode(v) for k,v in value.items()}
        if isinstance(value, (list,tuple)):
            return [encode(v) for v in value]
        return value
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x",encoding="utf-8") as handle:
        json.dump(encode(result),handle,ensure_ascii=False,separators=(",",":"));handle.write("\n")
    print(json.dumps({"status":result["status"],"checks":result["check_count"],"failures":result["failure_count"],"output":OUT.relative_to(REPO).as_posix()}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
