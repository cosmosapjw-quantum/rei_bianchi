#!/usr/bin/env python3
"""One data-only independent D3 result review; no solver/model imports.

Reuses the recovery agent's complete prefix/tail identity audit, and checks
the physical definitions, grid coverage, saved numerical guards and source
identity needed for scoped preliminary admission. This is not a benchmark.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.root.resolve()
    reads = {}

    def sha(path):
        path = Path(path).resolve()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        reads[str(path)] = {"sha256": digest, "bytes": len(data)}
        return digest

    def read_json(path):
        sha(path)
        return json.loads(Path(path).read_text())

    def axes(c):
        return (c["Sigma_F_i"], c.get("P_m_i", 0.0),
                c.get("P_r_i", c["Pi_F_signed_i"]))

    manifest = read_json(root / "z2_extension/results/MANIFEST.json")
    b1manifest = read_json(root / "components/results/MANIFEST.json")
    oldmanifest = read_json(root / "results/MANIFEST.json")
    status = read_json(root / "z2_extension/results/STATUS.json")
    historical_check = read_json(root / "z2_extension/results/CHECK.json")
    b1check = read_json(root / "components/results/CHECK.json")
    source = read_json(root / "SOURCE_MANIFEST.json")
    lock = read_json(root / "vendor/REI_BACKGROUND_FAMILY_LOCK.json")
    recovery = read_json(root.parent / "D3_RAW_REUSE_READBACK.json")
    old_raw_audit = read_json(root / "_archive_evidence/independent_audit/B2_RECEIPT_FAILURE_RAW_AUDIT.json")
    contract_review = read_json(root / "_archive_evidence/PHYS_MATH_CONTRACT_REVIEW.json")
    operational = read_json(root / "z2_extension/OPERATIONAL_REPAIR.json")
    for path in ["UNIFIED_EXECUTION_CONTRACT.md", "components/COMPONENT_CONTRACT.md",
                 "components/component_adapter.py", "components/unified_pilot.py", "adapter.py",
                 "components/plot_extension.py", "components/recover_serialization_receipts.py",
                 "z2_extension/results/SERIALIZATION_RECEIPT_RECOVERY.json"]:
        sha(root / path)

    identity = {}
    for name, expected in source["files"].items():
        identity["vendor/" + name] = sha(root / "vendor" / name) == expected
    for name, expected in status["execution_code_identity"]["sha256"].items():
        identity[name] = sha(root / name) == expected
    identity["pre_repair_runner"] = sha(root / operational["original_source_snapshot"]) == operational["old_runner_sha256"]
    identity["post_repair_runner"] = sha(root / "components/unified_pilot.py") == operational["new_runner_sha256"]
    identity["contract"] = sha(root / "UNIFIED_EXECUTION_CONTRACT.md") == manifest["contract_sha256"] == contract_review["contract_sha256"]
    identity["component_contract"] = sha(root / "components/COMPONENT_CONTRACT.md") == manifest["component_contract_sha256"]

    cases = manifest["cases"]
    nominal = [c for c in cases if not c["config"]["guard"]]
    guards = [c for c in cases if c["config"]["guard"]]
    nominal_by_axes = {axes(c["config"]): c for c in nominal}
    sigmas = [0., .0003, .001, .003, .01, .03, .1]
    matter = [-.0003, -.0001, 0., .0001, .0003]
    radiation = [-.001, -.0003, 0., .0003, .001]
    joint_axes = set(itertools.product(sigmas, matter, radiation))
    original_axes = {axes(c["config"]) for c in oldmanifest["cases"] if not c["config"]["guard"]}
    b1_axes = {axes(c["config"]) for c in b1manifest["cases"] if not c["config"]["guard"]}
    coverage = {
        "all_ids_unique": len({c["id"] for c in cases}) == len(cases) == 237,
        "nominal_axes_unique": len(nominal_by_axes) == len(nominal) == 231,
        "component_grid_exact": b1_axes == joint_axes and len(joint_axes) == 175,
        "radiation_baseline_count91": len(original_axes) == 91,
        "joint_baseline_overlap35": len(joint_axes & original_axes) == 35,
        "union_equals237_minus6guards": set(nominal_by_axes) == joint_axes | original_axes,
        "six_guards": len(guards) == 6,
        "all_component_points_available": joint_axes <= set(nominal_by_axes),
    }
    maxima = {}
    minima = {k: math.inf for k in ["H", "rad_energy_norm", "dust_energy_norm", "massive_energy_norm",
                                  "massive_min_cell_population", "minimum_brightness_gamma", "minimum_brightness_nu"]}
    cache = {}
    rows = []
    failed = []
    missing_solver_metadata = 0
    h0 = lock["cosmology"]["H0_per_s"]
    a_ref = lock["clock"]["a_ref"]
    cosmo = lock["cosmology"]
    href = h0 * math.sqrt(cosmo["Omega_m"] / a_ref**3 + cosmo["Omega_r"] / a_ref**4 + cosmo["Omega_lambda"])
    kt = 8 * math.pi * 6.67430e-11 / 299792458.0**2
    sqrt6 = math.sqrt(6)

    def absmax(label, value):
        val = float(np.max(np.abs(value)))
        maxima[label] = max(maxima.get(label, 0.0), val)
        return val

    for case in cases:
        folder = root / "z2_extension/results/cases" / case["id"]
        rec = read_json(folder / "RESULT.json")
        digest = sha(folder / "raw.npz")
        # Immutable saved arrays only; no source/model import or field recomputation.
        with np.load(folder / "raw.npz", allow_pickle=False) as z:
            d = {k: z[k] for k in z.files}
        c = case["config"]
        pm = sqrt6 * kt * d["Pi_matter_J_m3"] / d["H"]**2
        pr = sqrt6 * kt * (d["Pi_gamma_J_m3"] + d["Pi_nu_J_m3"]) / d["H"]**2
        sig = sqrt6 * np.abs(d["s"]) / d["H"]
        errors = {
            "Pm_SI": absmax("Pm_SI_absolute", d["P_m"] - pm),
            "Pr_SI": absmax("Pr_SI_absolute", d["P_r"] - pr),
            "Sigma_F": absmax("Sigma_F_absolute", d["Sigma_F"] - sig),
            "half_adapter": absmax("half_adapter_absolute", d["Sigma_F"] - math.sqrt(2)*d["Sigma_half"]),
            "signed_sum": absmax("signed_sum_absolute", d["P_total"] - d["P_m"] - d["P_r"]),
            "Pi_m": absmax("Pi_m_absolute", d["Pi_m"] - np.abs(d["P_m"])),
            "Pi_r": absmax("Pi_r_absolute", d["Pi_r"] - np.abs(d["P_r"])),
            "Pi_total": absmax("Pi_total_absolute", d["Pi_total"] - np.abs(d["P_m"]+d["P_r"])),
            "component_cross": absmax("component_cross_absolute", d["Pi_total"]**2 - d["Pi_m"]**2 - d["Pi_r"]**2 - 2*d["P_m"]*d["P_r"]),
            "shear_state": absmax("shear_state_normalized_absolute", d["s"] / href - d["raw_y"][2]),
            "b_state": absmax("b_state_absolute", d["b"] - d["raw_y"][1]),
            "elapsed_state": absmax("elapsed_state_dimensionless_absolute", d["elapsed_proper_s"] * href - d["raw_y"][0]),
            "gamma_N0": absmax("gamma_N0_absolute", d["gamma_N0"] - 1),
            "nu_N0": absmax("nu_N0_absolute", d["nu_N0"] - 1),
        }
        # This is explicitly construction consistency, never an independent ODE constraint test.
        hsq = h0**2 * (d["dust_energy_norm"] + d["massive_energy_norm"] + d["rad_energy_norm"] + cosmo["Omega_lambda"]) + d["s"]**2
        hres = absmax("Hamiltonian_construction_relative", d["H"]**2/hsq - 1)
        expected_axes = axes(c)
        initial_errors = [abs(float(d[k][0])-v) for k,v in zip(("Sigma_F","P_m","P_r"),expected_axes)]
        absmax("initial_axis_absolute", initial_errors)
        for k in minima:
            minima[k] = min(minima[k], float(np.min(d[k])))
        checks = {
            "raw_identity": digest == rec["raw_sha256"],
            "receipt_identity": rec["id"] == case["id"] and rec["config"] == c,
            "completed": rec["status"] == "COMPLETED",
            "physical_definitions": max(errors[k] for k in errors if k not in {"gamma_N0", "nu_N0"}) < 2e-14,
            "number_tolerance": max(errors["gamma_N0"], errors["nu_N0"]) <= 5e-11,
            "initial_axes": max(initial_errors) <= 5e-12,
            "constraint_construction": hres < 2e-14,
            "all_config_ne_absent": c["ne_source"] is None,
            "fixed_nonbaryonic_component": c["mass_fraction"] == .1 and c["mass_over_Tref"] == 30.,
            "common_radiation_IC": c["calibration"]["k_gamma"] == c["calibration"]["k_nu"],
            "shear_orientation_nonnegative": c["calibration"]["shear_orientation"] in (0,1),
        }
        if rec.get("nfev") is None:
            missing_solver_metadata += 1
        row = {"id":case["id"],"axes":list(expected_axes),"guard":c["guard"],
               "raw_path":str(folder / "raw.npz"),"raw_sha256":digest,"checks":checks}
        rows.append(row)
        if not all(checks.values()):
            failed.append({"id":case["id"],"failed":[k for k,v in checks.items() if not v]})
        cache[case["id"]] = {k:d[k] for k in ["x","a","H","b","Sigma_F","s","P_m","P_r","P_total","elapsed_proper_s"]}

    guard_rows = []
    saved_guards = {g["id"]:g for g in historical_check["refinement_controls"]}
    for guard in guards:
        nom = nominal_by_axes[axes(guard["config"])]
        g,n = cache[guard["id"]],cache[nom["id"]]
        diff = {k:abs(float(g[k][-1]-n[k][-1])) for k in ["Sigma_F","P_m","P_r","b"]}
        diff["H_relative"] = abs(float(g["H"][-1]/n["H"][-1]-1))
        archived = saved_guards[guard["id"]]
        guard_rows.append({"id":guard["id"],"nominal_id":nom["id"],"axes":list(axes(guard["config"])),
                           "paired_by_physical_axes":True,"archived_pair_matches":nom["id"]==archived["nominal_id"],
                           "absolute_endpoint_differences":diff,
                           "saved_check_values_exact":diff==archived["absolute_endpoint_differences"],
                           "within_original_2e6_threshold":max(diff.values())<=2e-6})

    representatives = []
    for ax in [(0.,0.,0.),(0.,.0003,-.0003),(0.,-.0003,.0003),(.1,.0003,.001),(.1,-.0003,-.001)]:
        c = nominal_by_axes[ax]
        d = cache[c["id"]]
        row = {"id":c["id"],"axes":list(ax),"initial":{},"z4":{},"z2":{}}
        for name,idx in [("initial",0),("z4",120),("z2",152)]:
            row[name] = {k:float(d[k][idx]) for k in ("H","b","Sigma_F","P_m","P_r","P_total","elapsed_proper_s")}
            row[name]["signed_shear"] = sqrt6*float(d["s"][idx]/d["H"][idx])
        if ax == (0.,0.,0.):
            row["maximum_isotropy_magnitude"] = max(float(np.max(np.abs(d[k]))) for k in ("Sigma_F","P_m","P_r"))
        representatives.append(row)

    res = {
        "schema":"rei.d3.independent_saved_data_review.v1","reviewer":"/root/physics_literature",
        "method":"Independent SI/Frobenius and signed-component arithmetic on saved arrays, grid-set identity, physical-axis guard pairing, source-hash binding; reuse complete recovery prefix/tail audit. No model or solver import.",
        "new_ODE_calls":0,"new_IVPs":0,"benchmark_runs":0,
        "source_identity_checks":identity,"grid_coverage_checks":coverage,
        "case_count":len(cases),"nominal_count":len(nominal),"guard_count":len(guards),
        "all_cases_completed":all(r["checks"]["completed"] for r in rows),
        "source_commit":source["source_commit"],"source_kappa_t":kt,
        "missing_original_solver_metadata_cases":missing_solver_metadata,
        "norm_consistency_maxima":maxima,"minimum_saved_values":minima,
        "refinement_controls":guard_rows,"representative_saved_results":representatives,
        "historical_numerical_gates":{"b1":b1check["numerical_gate"],"b2":historical_check["numerical_gate"]},
        "reused_recovery_audit":{"path":str(root.parent/"D3_RAW_REUSE_READBACK.json"),"all237_join_prefix_tail_hash_checks_pass":not recovery["failed_checks"],"historical_false_checks":recovery["historical_result_false_checks"]},
        "reused_serialization_audit":{"decision":old_raw_audit["decision"],"observed_cases":old_raw_audit["observed_cases"],"failed_audit_cases":old_raw_audit["failed_audit_cases"]},
        "failed_cases":failed,"cases":rows,"read_paths_and_sha256":reads,
    }
    res["data_review_pass"] = (all(identity.values()) and all(coverage.values()) and not failed
          and all(r["within_original_2e6_threshold"] and r["archived_pair_matches"] and r["saved_check_values_exact"] for r in guard_rows)
          and not recovery["failed_checks"] and not old_raw_audit["failed_audit_cases"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:res[k] for k in ["data_review_pass","case_count","nominal_count","guard_count","missing_original_solver_metadata_cases","norm_consistency_maxima","minimum_saved_values","failed_cases"]},indent=2))
    return 0 if res["data_review_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
