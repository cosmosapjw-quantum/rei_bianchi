"""Independent saved-tail scientific consistency review; never calls an ODE.

Algebraic constraints and tensor contractions are checked on all saved samples.
The radiation energy-work integral is a sampled Simpson diagnostic, without a
continuum error or positivity claim. Execution accounting is not a benchmark.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np

PINNED_RUNNER = "959952f9d347bcc515410ef90b3b8dc4b36388ad4bfd2acc2bac356fafd6d97b"
PINNED_INDEX = "62f5d96fd323b1ed60c61f4b51e35ab80eb3498d2800c6c04addc1e5e2483115"
SCOPE = "NEW_Z4_TO_Z2_TAIL_FROM_IMMUTABLE_REI198_ENDPOINT"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def state_sha(state):
    return hashlib.sha256(np.asarray(state, dtype="<f8").tobytes(order="C")).hexdigest()


def relative_error(a, b):
    a, b = np.asarray(a), np.asarray(b)
    scale = np.maximum(np.abs(a), np.abs(b))
    return float(np.max(np.divide(np.abs(a-b), scale,
                                 out=np.zeros_like(scale), where=scale > 0)))


def audit(tail_root, owner_root, terminal_index, output):
    tail_root, owner_root = Path(tail_root), Path(owner_root)
    output = Path(output)
    run_path = tail_root / "run_identity.json"
    run = json.loads(run_path.read_text())
    run_hash = canonical_sha(run)
    assert run["runner_sha256"] == PINNED_RUNNER
    assert run["scope"] == SCOPE and run["HH_R10"] == "OFF"
    assert run["production_admission"] == "NOT_ISSUED"
    assert sha(terminal_index) == PINNED_INDEX == run["terminal_index_sha256"]
    rows = json.loads(Path(terminal_index).read_text())["rows"]
    terminal = {row["case_id"]: row for row in rows}
    assert len(terminal) == 1231
    for name, digest in run["owner_files"].items():
        assert sha(owner_root / name) == digest
    lock_path = owner_root / "vendor/REI_BACKGROUND_FAMILY_LOCK.json"
    lock = json.loads(lock_path.read_text())
    c = lock["cosmology"]
    h0, om, ore, ol = (c[k] for k in ("H0_per_s", "Omega_m", "Omega_r", "Omega_lambda"))
    aref = lock["clock"]["a_ref"]
    href = h0 * math.sqrt(om/aref**3 + ore/aref**4 + ol)
    # Same SI convention as the pinned SourceLock: pressure is J/m^3,
    # H and s are per proper second, hence K=8*pi*G/c^2 in these equations.
    K = 8*math.pi*6.67430e-11 / 299792458.0**2
    rhocrit = 3*h0*h0/K
    fm = 0.1
    finished_paths = list((tail_root / "invocations").glob("*/FINISHED.json"))
    assert len(finished_paths) == 1
    finish = json.loads(finished_paths[0].read_text())
    start = json.loads(finished_paths[0].with_name("STARTED.json").read_text())
    assert finish["status"] == "COMPLETE_SELECTED_PRELIMINARY_TAILS"
    assert not finish["pending_selected_cases"] and not finish["failed_or_interrupted_preserved"]
    assert not list((tail_root / "cases").glob("*/FAILED.json"))
    paths = sorted((tail_root / "cases").glob("*/COMPLETED.json"))
    assert len(paths) == 1231 and {p.parent.name for p in paths} == set(terminal)
    extrema = {"H_min_per_s": math.inf, "E0_min": math.inf,
               "sampled_angular_brightness_min": math.inf,
               "matter_cell_population_min_from_receipts": math.inf,
               "elapsed_step_min_s": math.inf, "elapsed_end_min_s": math.inf,
               "elapsed_end_max_s": -math.inf, "b_abs_max": 0.0,
               "target_redshift_max_abs_error": 0.0}
    errors = Counter()
    energy_rows, source_rows, selected = [], [], []
    lanes = Counter()
    damping = Counter()
    selected_ids = {"mixed_s+0_m+1", "mixed_s+0_m-1", "m_s00_+0_p12_+1",
                    "m_s00_+0_p12_-1", "s00_+0_p12_+1", "s00_+0_p12_-1",
                    "s00_+0_p00_+0"}
    new_solves = 0
    for path in paths:
        receipt = json.loads(path.read_text())
        ident = receipt["identity"]
        cid = ident["case_id"]
        old = terminal[cid]
        assert receipt["status"] == "COMPLETED" and receipt["new_ODE_solves"] == 1
        assert receipt["HH_R10"] == "OFF" and receipt["production_admission"] == "NOT_ISSUED"
        assert receipt["old_trajectories_rerun"] == 0 and receipt["new_tail_only"] is True
        assert ident["run_identity_sha256"] == run_hash
        assert receipt["identity_sha256"] == canonical_sha(ident)
        assert ident["npz_sha256"] == old["npz_sha256"]
        assert ident["receipt_sha256"] == old["receipt_sha256"]
        assert state_sha(ident["amplitude_from_receipt"]) == state_sha(old["initial_matter_A"])
        assert receipt["global_aref_unchanged"] == aref
        assert receipt["global_href_unchanged"] == href
        for key in ("restart_boundary_before_solver", "restart_boundary_after_solver"):
            bnd = receipt[key]
            assert bnd["status"] == "BIT_IDENTICAL_TO_SAVED_DIAGNOSTICS"
            assert bnd["recomputation_max_abs_difference"] == 0
            assert bnd["source"] == ident["restart_diagnostics_source"]
        history = path.with_name("history.npz")
        assert sha(history) == receipt["history_sha256"]
        with np.load(history, allow_pickle=False) as archive:
            d = {key: archive[key].copy() for key in archive.files
                 if archive[key].dtype.kind in "biufc"}
            assert str(archive["identity_sha256"].item()) == receipt["identity_sha256"]
        x, H, state = d["x"], d["H_per_s"], d["state"]
        assert state.shape == (8, 33) and len(x) == 33
        assert all(np.isfinite(value).all() for value in d.values())
        assert state_sha(state[:, 0]) == state_sha(old["terminal"]["state"]) == ident["restart_state_sha256"]
        assert x[0] == old["terminal"]["x"] and x[-1] == run["target_x"]
        assert np.all(np.diff(x) > 0) and np.all(np.diff(d["elapsed_seconds"]) > 0)
        assert np.all(H > 0) and np.all(d["E0"] > 0)
        assert np.min(d["sampled_min_angular_brightness"]) >= 0
        assert receipt["min_matter_cell_population"] >= 0
        assert receipt["minimum_sampled_angular_brightness"] == float(np.min(d["sampled_min_angular_brightness"]))
        a = aref*np.exp(x)
        w = d["s_over_H"]
        s = w*H
        density = rhocrit*((1-fm)*om/a**3 + fm*om/aref**3*d["massive_rho_norm"]
                          + ore/a**4*d["E0"] + ol)
        H2_constraint = K*density/3 + s*s
        errors["Einstein_constraint_max_relative"] = max(errors["Einstein_constraint_max_relative"], relative_error(H*H, H2_constraint))
        errors["proper_time_state_max_relative"] = max(errors["proper_time_state_max_relative"], relative_error(d["elapsed_seconds"], state[0]/href))
        sigma = np.stack((-s, -s, 2*s))
        sigma_norm = np.sqrt(np.sum(sigma*sigma, axis=0))/H
        errors["Sigma_F_tensor_norm_max_relative"] = max(errors["Sigma_F_tensor_norm_max_relative"], relative_error(d["Sigma_frobenius"], sigma_norm))
        for sec in ("m", "r", "total"):
            tensor = np.stack([d[f"pi_{sec}_{k}_J_m3"] for k in ("11", "22", "33")])
            assert np.array_equal(tensor.sum(axis=0), np.zeros(33))
            full = K*np.sqrt(np.sum(tensor*tensor, axis=0))/(H*H)
            errors["Pi_F_tensor_norm_max_relative"] = max(errors["Pi_F_tensor_norm_max_relative"], relative_error(d[f"Pi_{sec}_frobenius"], full))
            errors["sqrt2_normalization_max_relative"] = max(errors["sqrt2_normalization_max_relative"], relative_error(d[f"Pi_{sec}_frobenius"], math.sqrt(2)*d[f"Pi_{sec}_half"]))
            if sec != "total":
                contraction = -np.sum((sigma/H)*tensor, axis=0)
                errors["work_tensor_contraction_max_relative"] = max(errors["work_tensor_contraction_max_relative"], relative_error(d[f"work_{sec}_J_m3_per_x"], contraction))
                damping[sec+"_magnitude_decreases_z4_to2"] += bool(abs(d[f"signed_Pi_{sec}"][-1]) <= abs(d[f"signed_Pi_{sec}"][0]))
        for k in ("11", "22", "33"):
            assert np.array_equal(d[f"pi_total_{k}_J_m3"], d[f"pi_m_{k}_J_m3"]+d[f"pi_r_{k}_J_m3"])
        assert np.array_equal(d["signed_Pi_total"], d["signed_Pi_m"]+d["signed_Pi_r"])
        assert np.array_equal(d["Pi_total_half"], abs(d["signed_Pi_total"]))
        h = (x[-1]-x[0])/32
        assert np.allclose(np.diff(x), h, rtol=2e-12, atol=0)
        weights = np.ones(33); weights[1:-1:2] = 4; weights[2:-1:2] = 2
        # rho_r'+4rho_r=-sigma:pi_r/H is equivalent to E0'=-2*w*E2.
        integrand = -2*w*d["E2"]
        work_integral = h/3*float(np.dot(weights, integrand))
        variation = h/3*float(np.dot(weights, abs(integrand)))
        observed = float(d["E0"][-1]-d["E0"][0])
        energy_rows.append({"case_id": cid, "delta_E0": observed,
                            "sampled_work_integral": work_integral,
                            "sampled_absolute_work_integral": variation,
                            "sampled_residual": observed-work_integral})
        extrema["H_min_per_s"] = min(extrema["H_min_per_s"], float(H.min()))
        extrema["E0_min"] = min(extrema["E0_min"], float(d["E0"].min()))
        extrema["sampled_angular_brightness_min"] = min(extrema["sampled_angular_brightness_min"], float(d["sampled_min_angular_brightness"].min()))
        extrema["matter_cell_population_min_from_receipts"] = min(extrema["matter_cell_population_min_from_receipts"], receipt["min_matter_cell_population"])
        extrema["elapsed_step_min_s"] = min(extrema["elapsed_step_min_s"], float(np.diff(d["elapsed_seconds"]).min()))
        extrema["elapsed_end_min_s"] = min(extrema["elapsed_end_min_s"], float(d["elapsed_seconds"][-1]))
        extrema["elapsed_end_max_s"] = max(extrema["elapsed_end_max_s"], float(d["elapsed_seconds"][-1]))
        extrema["b_abs_max"] = max(extrema["b_abs_max"], float(abs(d["b"]).max()))
        extrema["target_redshift_max_abs_error"] = max(extrema["target_redshift_max_abs_error"], abs(float(d["zbar"][-1])-2.0))
        source_rows.append({"case_id": cid, "receipt_sha256": sha(path), "history_sha256": receipt["history_sha256"]})
        if cid in selected_ids:
            with np.load(owner_root/ident["restart_diagnostics_source"]["npz_path"], allow_pickle=False) as original:
                initial = {k: float(original[k][0]) for k in ("s_over_H", "signed_Pi_m", "signed_Pi_r")}
            entries = []
            for z, w0, pm, pr in ((20., initial["s_over_H"], initial["signed_Pi_m"], initial["signed_Pi_r"]),
                                  (4., float(w[0]), float(d["signed_Pi_m"][0]), float(d["signed_Pi_r"][0])),
                                  (2., float(w[-1]), float(d["signed_Pi_m"][-1]), float(d["signed_Pi_r"][-1]))):
                denominator = abs(pm)+abs(pr)
                entries.append({"z": z, "signed_S_F": math.sqrt(6)*w0,
                                "Sigma_F": math.sqrt(6)*abs(w0), "signed_Pi_m_F": math.sqrt(2)*pm,
                                "signed_Pi_r_F": math.sqrt(2)*pr, "Pi_total_F": math.sqrt(2)*abs(pm+pr),
                                "instantaneous_cancellation": None if denominator == 0 else 1-abs(pm+pr)/denominator})
            selected.append({"case_id": cid, "lane": ident["lane"], "values": entries})
        lanes[ident["lane"]] += 1
        new_solves += receipt["new_ODE_solves"]
    assert new_solves == finish["cumulative_costs"]["new_ODE_solves"] == 1231
    assert dict(lanes) == {"RADIATION_SLICE": 625, "MATTER_SLICE": 600, "MIXED_CANCELLATION": 6}
    assert max(errors.values()) < 2e-13
    worst = max(energy_rows, key=lambda r: abs(r["sampled_residual"]))
    active = [r for r in energy_rows if r["sampled_absolute_work_integral"] >= 1e-10]
    relative_work = max(abs(r["sampled_residual"])/(abs(r["delta_E0"])+r["sampled_absolute_work_integral"]) for r in active)
    report = {"schema": "PHYS76_SCIENTIFIC_RESULT_REVIEW_V1", "status": "PASS_SCOPED_SAVED_RESULT_CONSISTENCY",
              "reviewer": "theory_literature_independent_of_runner_and_analyzer_authors",
              "audit_source_sha256": sha(__file__), "run_identity_file_sha256": sha(run_path),
              "run_identity_sha256": run_hash, "finished_invocation_sha256": sha(finished_paths[0]),
              "terminal_index_sha256": PINNED_INDEX, "background_lock_sha256": sha(lock_path),
              "completed_cases": 1231, "failed_cases": 0, "pending_cases": 0,
              "saved_tail_samples_checked": 1231*33, "new_display_samples_added": 1231*32,
              "lanes": dict(lanes), "all_case_identity_and_restart_guards": "PASS",
              "execution_accounting": {"site": start["site"], "max_workers": start["max_workers"],
                  **finish["cumulative_costs"], "old_trajectories_rerun": 0,
                  "benchmark_runs": 0, "new_NCP_runs": int(start["site"] == "ncp"),
                  "interpretation": "Execution accounting only; no measured speedup or benchmark comparison"},
              "positivity_and_clock": extrema,
              "algebraic_and_tensor_checks": {"max_relative_errors": dict(errors),
                  "review_threshold": 2e-13,
                  "equations": ["H^2=K*(rho_dust+rho_massive+rho_radiation+rho_Lambda)/3+s^2",
                                "Sigma_F=sqrt(sigma_ab*sigma_ab)/H",
                                "Pi_A,F=K*sqrt(pi_A,ab*pi_A,ab)/H^2",
                                "work_A=-sum_ab(sigma_ab/H*pi_A,ab)",
                                "pi_total=pi_m+pi_r before norm; full=sqrt(2)*half"],
                  "interpretation": "Algebraic diagnostic consistency, not an independent global ODE-error certificate"},
              "radiation_work_diagnostic": {"identity": "E0'=-2*(s/H)*E2; rho_r'+4rho_r=-sigma:pi_r/H",
                  "quadrature": "33 saved uniform samples; composite Simpson on new tail only",
                  "max_abs_sampled_residual": abs(worst["sampled_residual"]), "worst_case": worst,
                  "active_integral_cutoff": 1e-10, "active_cases": len(active),
                  "max_residual_over_observed_plus_absolute_integral_on_active_cases": relative_work,
                  "interpretation": "Includes saved-trajectory and sampled-quadrature errors; no continuum bound"},
              "observed_endpoint_damping_counts": dict(damping), "selected_examples": selected,
              "source_manifest": source_rows,
              "limitations": ["finiteL8 collisionless owner only; not full cold-EoR",
                              "positive sampled angular brightness does not prove all-angle or all-time positivity",
                              "matter cell positivity here is read from hash-bound run receipts",
                              "no matter differential-energy certificate: saved mean pressure is unavailable",
                              "same-trajectory sector attribution is not a species-off causal experiment",
                              "sampled work or shear residual is not a continuum certificate"],
              "new_ode_integrations_by_review": 0, "benchmark_runs_by_review": 0,
              "HH_R10": "OFF", "production_admission": "NOT_ISSUED"}
    with output.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({k: report[k] for k in ("status", "completed_cases", "failed_cases",
                                           "execution_accounting", "positivity_and_clock",
                                           "algebraic_and_tensor_checks", "radiation_work_diagnostic")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tail-root", type=Path, required=True)
    parser.add_argument("--owner-root", type=Path, required=True)
    parser.add_argument("--terminal-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.tail_root, args.owner_root, args.terminal_index, args.output)
