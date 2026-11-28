"""Existing-data eight-node replay and prediction-only holdout lock."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
from scipy.linalg import norm

EXPECTED = {
    "snapshot": "565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079",
    "archive": "c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9",
    "engine": "ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0",
    "global_model": "4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034",
    "z05_od": "1505463b2329e9398b92077d51a9704c4b5f2c5d71288cf811571763a672f80a",
    "z05_jvp": "88b44ec142eef45ef7232f7fd050a0c5ca1773db416986a9a5857d60959b5fc3",
    "z1_od": "020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818",
    "z1_jvp": "b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819",
    "z25_od": "6f6702ad6fc0c36c03332cf0cf688786426f324ca9bbf3e30cd32084a915be23",
    "z25_jvp": "3d365cc16192ac9f9b29bbebeb01a42fc8acd668879c1c18d533cfeb884d8465",
    "z35_od": "de730fcb4b6b65e86d5910cc456d35eaf33dab3610d0326939434d0f391d610a",
    "z35_jvp": "17d3d306f1e104591f91281f0acb8dae3ed6bc743f1d366da5b6bccb96e82a8c",
    "z25_comparison": "851565f86da5e050525abb425e80c6eada8ea9ac698cf8df168e1ba9e0290ed3",
}
Z3_OD = "47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af"
Z3_JVP = "9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661"


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def read_npz(blob: bytes) -> dict:
    with np.load(io.BytesIO(blob), allow_pickle=False) as f:
        return {key: f[key] for key in f.files}


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def cast(value):
    return np.asarray(value, dtype=np.complex128)


def n2(value) -> float:
    return float(norm(cast(value), 2))


def write(path: Path, value: dict) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    for key in ("repo", "snapshot", "archive", "inventory", "outdir"):
        ap.add_argument("--" + key, required=True, type=Path)
    a = ap.parse_args()
    repo, out = a.repo.resolve(), a.outdir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "snapshot": a.snapshot, "archive": a.archive,
        "engine": repo / "research/r31ad_five_node/unit_cell_model.py",
        "global_model": repo / "research/r31z_source_bound/source_bound.py",
        "z05_od": repo / "research/r31ae_z05_gate/authorized_z05_20260929/OD_RAW/ASSEMBLED_OD.npz",
        "z05_jvp": repo / "research/r31ae_z05_gate/authorized_z05_20260929/JVP_RAW/ASSEMBLED.npz",
        "z1_od": repo / "research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz",
        "z1_jvp": repo / "research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz",
        "z25_od": repo / "research/r31aj_z25_validation/authorized_z25_20260930/OD_RAW/ASSEMBLED_OD.npz",
        "z25_jvp": repo / "research/r31aj_z25_validation/authorized_z25_20260930/JVP_RAW/ASSEMBLED.npz",
        "z35_od": repo / "research/r31ah_post_z35/authorized_z35_20260930/OD_RAW/ASSEMBLED_OD.npz",
        "z35_jvp": repo / "research/r31ah_post_z35/authorized_z35_20260930/JVP_RAW/ASSEMBLED.npz",
        "z25_comparison": repo / "research/r31aj_z25_validation/authorized_z25_20260930/Z25_COMPARISON_RECOVERY.json",
    }
    blobs = {key: path.read_bytes() for key, path in paths.items()}
    for key, blob in blobs.items():
        if sha(blob) != EXPECTED[key]:
            raise ValueError("source/input hash drift: " + key)
    comp = json.loads(blobs["z25_comparison"])
    if comp["frozen_decision_rule_verdict"] != "PARETO_SUPPORTED_AT_Z25" or comp["independent_single_point_central_cell_relative_validation"]:
        raise ValueError("z2.5 protocol status drift")
    fit = read_npz(blobs["snapshot"])
    od05, jvp05 = read_npz(blobs["z05_od"]), read_npz(blobs["z05_jvp"])
    od1, jvp1 = read_npz(blobs["z1_od"]), read_npz(blobs["z1_jvp"])
    od25, jvp25 = read_npz(blobs["z25_od"]), read_npz(blobs["z25_jvp"])
    od35, jvp35 = read_npz(blobs["z35_od"]), read_npz(blobs["z35_jvp"])
    with zipfile.ZipFile(a.archive) as archive:
        od3_member = "completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz"
        jvp3_member = "completion/mixed_derivative/B192_z3/ASSEMBLED.npz"
        od3_blob, jvp3_blob = archive.read(od3_member), archive.read(jvp3_member)
    if sha(od3_blob) != Z3_OD or sha(jvp3_blob) != Z3_JVP:
        raise ValueError("z3 training member drift")
    od3, jvp3 = read_npz(od3_blob), read_npz(jvp3_blob)
    zvals = [0., .5, 1., 2., 2.5, 3., 3.5, 4.]
    role = ["TRAINING"] * 8
    role[4] = "PROTOCOL_DEVIATED_NUMERICAL_COMPARISON_CONSUMED_AS_R31AK_TRAINING"
    role[6] = "PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AI_TRAINING"
    raw = [
        (fit["z0_od_O"], fit["z0_od_D_col"], fit["z0_od_D_row"], fit["z0_j_dotO"]),
        (od05["O"], od05["D_col"], od05["D_row"], jvp05["dotO"]),
        (od1["O"], od1["D_col"], od1["D_row"], jvp1["dotO"]),
        (fit["direct_O"][:47, 47:], fit["direct_D"][:47, 47:], fit["direct_D"][47:, :47], fit["direct_dotO"][:47, 47:]),
        (od25["O"], od25["D_col"], od25["D_row"], jvp25["dotO"]),
        (od3["O"], od3["D_col"], od3["D_row"], jvp3["dotO"]),
        (od35["O"], od35["D_col"], od35["D_row"], jvp35["dotO"]),
        (fit["z4_od_O"], fit["z4_od_D_col"], fit["z4_od_D_row"], fit["z4_j_dotO"]),
    ]
    sources = [
        {"path": str(paths["snapshot"]), "objects": ["z0_od_O", "z0_od_D_col", "z0_od_D_row", "z0_j_dotO"], "sha256": EXPECTED["snapshot"], "bytes": len(blobs["snapshot"])},
        {"OD_path": str(paths["z05_od"]), "OD_sha256": EXPECTED["z05_od"], "OD_bytes": len(blobs["z05_od"]), "JVP_path": str(paths["z05_jvp"]), "JVP_sha256": EXPECTED["z05_jvp"], "JVP_bytes": len(blobs["z05_jvp"])},
        {"OD_path": str(paths["z1_od"]), "OD_sha256": EXPECTED["z1_od"], "OD_bytes": len(blobs["z1_od"]), "JVP_path": str(paths["z1_jvp"]), "JVP_sha256": EXPECTED["z1_jvp"], "JVP_bytes": len(blobs["z1_jvp"])},
        {"path": str(paths["snapshot"]), "objects": ["direct_O[:47,47:]", "direct_D[:47,47:]", "direct_D[47:,:47]", "direct_dotO[:47,47:]"], "sha256": EXPECTED["snapshot"], "bytes": len(blobs["snapshot"]), "upstream_member": "WU088_HH_R31S_NCP_20260928/evidence/z2/R31S_FULL49_z2.npz"},
        {"OD_path": str(paths["z25_od"]), "OD_sha256": EXPECTED["z25_od"], "OD_bytes": len(blobs["z25_od"]), "JVP_path": str(paths["z25_jvp"]), "JVP_sha256": EXPECTED["z25_jvp"], "JVP_bytes": len(blobs["z25_jvp"]), "one_shot_parent": "research/r31aj_z25_validation/authorized_z25_20260930/RETURN.json"},
        {"archive": str(paths["archive"]), "OD_member": od3_member, "OD_sha256": Z3_OD, "OD_bytes": len(od3_blob), "JVP_member": jvp3_member, "JVP_sha256": Z3_JVP, "JVP_bytes": len(jvp3_blob)},
        {"OD_path": str(paths["z35_od"]), "OD_sha256": EXPECTED["z35_od"], "OD_bytes": len(blobs["z35_od"]), "JVP_path": str(paths["z35_jvp"]), "JVP_sha256": EXPECTED["z35_jvp"], "JVP_bytes": len(blobs["z35_jvp"])},
        {"path": str(paths["snapshot"]), "objects": ["z4_od_O", "z4_od_D_col", "z4_od_D_row", "z4_j_dotO"], "sha256": EXPECTED["snapshot"], "bytes": len(blobs["snapshot"])},
    ]
    velocity = float(fit["velocity"])
    times = [z / velocity for z in zvals]
    rows = []
    for z, t, label, source, (O, Dc, Dr, dotO) in zip(zvals, times, role, sources, raw):
        if tuple(x.shape for x in (O, Dc, Dr, dotO)) != ((47, 2), (47, 2), (2, 47), (47, 2)):
            raise ValueError("node shape drift")
        rows.append({"z_a0": z, "time_ta": t, "role": label, "source": source,
                     "fields": {"O": "47x2", "D_col": "47x2", "D_row": "2x47", "independent_dotO": "47x2"},
                     "raw_dtypes": dict(zip(("O", "D_col", "D_row", "dotO"), (str(x.dtype) for x in (O, Dc, Dr, dotO)))),
                     "raw_metric_identity_max_abs": float(np.max(np.abs(dotO - Dc - Dr.conj().T))),
                     "basis_order_phase_contract": "CP4 frozen B192 neutral rows centre0 24 then centre1 excited23; ionic columns 2; phase_E, tau=z/velocity; analytic JVP dotO in 1/t_a; producer lines in R31Y PRODUCER_INTAKE.json"})
    manifest = {"schema": "WU088_R31AK_EIGHT_NODE_INPUT_MANIFEST_V1", "nodes": rows,
                "R31AK_independent_validation_points": [], "source_array_mutation": False,
                "comparison_dtype": "complex128; original complex256/complex128 raw arrays preserved",
                "upstream_provenance": ["research/r31ai_adaptive/ncp_followup_20260930/SEVEN_NODE_INPUT_MANIFEST.json", "research/r31aj_z25_validation/authorized_z25_20260930/RETURN.json"]}
    engine = module(paths["engine"], "r31ad_engine_unchanged_r31ak")
    global_model = module(paths["global_model"], "r31z_global_unchanged_r31ak")
    helper_path = repo / "research/r31ak_eight_node/successor_policy.py"
    helper = module(helper_path, "r31ak_policy_unchanged")
    values = [cast(row[0]) for row in raw]
    dcols = [cast(row[1]) for row in raw]
    drows = [cast(row[2]) for row in raw]
    dots = [cast(row[3]) for row in raw]
    ks = [(dc - dr.conj().T) / 2 for dc, dr in zip(dcols, drows)]
    maxima = {key: 0. for key in ("O", "dotO", "K", "D_col", "D_row")}
    for j, t in enumerate(times):
        O, dotO, Dc, Dr, K, _ = engine.piecewise_candidate(times, values, dots, ks, t)
        for key, error in (("O", O - values[j]), ("dotO", dotO - dots[j]), ("K", K - ks[j]), ("D_col", Dc - dcols[j]), ("D_row", Dr - drows[j])):
            maxima[key] = max(maxima[key], n2(error))
    continuity = {key: 0. for key in maxima}
    for j in range(1, 7):
        left_O, left_dot = engine.cubic_hermite(values[j-1], values[j], dots[j-1], dots[j], times[j]-times[j-1], 1.)
        right_O, right_dot = engine.cubic_hermite(values[j], values[j+1], dots[j], dots[j+1], times[j+1]-times[j], 0.)
        for key, error in (("O", left_O - right_O), ("dotO", left_dot - right_dot),
                           ("K", ks[j] - ks[j]),
                           ("D_col", left_dot / 2 + ks[j] - right_dot / 2 - ks[j]),
                           ("D_row", (left_dot / 2 - ks[j]).conj().T - (right_dot / 2 - ks[j]).conj().T)):
            continuity[key] = max(continuity[key], n2(error))
    metric = 0.
    for t in np.linspace(times[0], times[-1], 401):
        _, dotO, Dc, Dr, _, _ = engine.piecewise_candidate(times, values, dots, ks, float(t))
        metric = max(metric, n2(dotO - Dc - Dr.conj().T))
    if max(maxima.values()) > 1e-12 or max(continuity.values()) > 1e-12 or metric > 1e-12:
        raise ValueError("eight-node algebraic replay failed")
    replay = {"schema": "WU088_R31AK_EIGHT_NODE_MODEL_REPLAY_V1", "model_name": "R31AK_ADAPTIVE_EIGHT_NODE_CUBIC_O_LINEAR_K",
              "engine_sha256": EXPECTED["engine"], "cells_z_a0": [[zvals[i], zvals[i+1]] for i in range(7)],
              "node_reproduction_max_2norm": maxima, "internal_node_continuity_max_2norm": continuity,
              "dense_grid_points": 401, "dense_grid_metric_identity_max_2norm": metric,
              "source_array_mutation": False, "science_node_count": 0, "predictive_validation_performed": False}
    old_indices = [0, 1, 2, 3, 5, 6, 7]
    old = engine.piecewise_candidate([times[i] for i in old_indices], [values[i] for i in old_indices],
                                     [dots[i] for i in old_indices], [ks[i] for i in old_indices], times[4])
    EO, EK = n2(old[0] - values[4]), n2(old[4] - ks[4])
    for got, target in ((EO, .019184864006565112), (EK, .08583702792342718)):
        if abs(got - target) > 1e-13:
            raise ValueError("z2.5 prior numerical comparison drift")
    bounds = helper.midpoint_lower_bounds(EO, EK, 1 / velocity, 1.)
    indicator = {"schema": "WU088_R31AK_Z25_LOCAL_INDICATOR_V1", "E_O": EO, "E_K_per_ta": EK,
                 "cell_width_ta": 1 / velocity, "cell_width_a0": 1., "necessary_lower_bounds": bounds,
                 "certified_source_error_enclosure": False, "z25_original_numerical_verdict": "PARETO_SUPPORTED_AT_Z25",
                 "z25_independent_validation_admitted": False,
                 "z25_role": role[4]}
    inventory = json.loads(a.inventory.read_text())
    selected_candidates = inventory["fresh_candidate_z_a0"]
    if selected_candidates != helper.fresh_candidate_points():
        raise ValueError("holdout inventory/policy candidate drift")
    prediction_arrays = {}
    candidate_rows = []
    for z in selected_candidates:
        t = z / velocity
        local = engine.piecewise_candidate(times, values, dots, ks, t)[:5]
        gO, gdot = global_model.quintic_hermite([values[i] for i in (0, 3, 7)], [dots[i] for i in (0, 3, 7)], times[-1], z / 4)
        gK = global_model.quadratic_three_nodes([ks[i] for i in (0, 3, 7)], z / 4)
        global_pred = (gO, gdot, gdot / 2 + gK, (gdot / 2 - gK).conj().T, gK)
        key = "z" + str(z).replace(".", "p")
        for name, pred in (("R31AK", local), ("R31Z", global_pred)):
            for field, array in zip(("O", "dotO", "Dcol", "Drow", "K"), pred):
                prediction_arrays[f"{key}_{name}_{field}"] = np.asarray(array, dtype=np.complex128)
        dk = n2(local[4] - global_pred[4])
        dcol = n2(local[2] - global_pred[2])
        drow = n2(local[3] - global_pred[3])
        dmax = max(dcol, drow)
        candidate_rows.append({"z": z, "time_ta": t, "prediction_key": key,
                               "DeltaK": dk, "DeltaDcol": dcol, "DeltaDrow": drow,
                               "DeltaDmax": dmax, "S": math.hypot(dk, dmax)})
    chosen = helper.select_candidate(candidate_rows)["selected"]
    selected_row = next(row for row in candidate_rows if row["z"] == chosen["z"])
    if any(sha(path.read_bytes()) != EXPECTED[key] for key, path in paths.items()):
        raise ValueError("source/input mutated during replay")
    write(out / "EIGHT_NODE_INPUT_MANIFEST.json", manifest)
    write(out / "R31AK_MODEL_REPLAY.json", replay)
    write(out / "Z25_LOCAL_INDICATOR.json", indicator)
    if (out / "FROZEN_HOLDOUT_PREDICTIONS.npz").exists():
        raise FileExistsError(out / "FROZEN_HOLDOUT_PREDICTIONS.npz")
    np.savez(out / "FROZEN_HOLDOUT_PREDICTIONS.npz", **prediction_arrays)
    manifest_sha = sha((out / "EIGHT_NODE_INPUT_MANIFEST.json").read_bytes())
    prediction_sha = sha((out / "FROZEN_HOLDOUT_PREDICTIONS.npz").read_bytes())
    adapter_sha = sha((repo / "research/r31ak_eight_node/metadata_adapter.py").read_bytes())
    comparator_sha = sha((repo / "research/r31ak_eight_node/compare_future_holdout.py").read_bytes())
    engine_sha = EXPECTED["engine"]
    policy_sha = sha((repo / "research/r31ak_eight_node/MODEL_POLICY.json").read_bytes())
    helper_sha = sha(helper_path.read_bytes())
    model_components = {"engine_sha256": engine_sha, "policy_sha256": policy_sha, "helper_sha256": helper_sha,
                        "eight_node_manifest_sha256": manifest_sha}
    model_sha = sha(json.dumps(model_components, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
    rule = {"schema": "WU088_R31AK_FUTURE_HOLDOUT_DECISION_RULE_V1", "models": ["R31AK_ADAPTIVE_EIGHT_NODE_CUBIC_O_LINEAR_K", "R31Z_GLOBAL_QUINTIC_O_QUADRATIC_K"],
            "primary_metrics": ["E_K", "E_Dmax"], "comparison_tolerance_per_ta": 1e-10,
            "pareto_rule": {"PARETO_SUPPORTED_AT_SELECTED_HOLDOUT": "R31AK E_K <= R31Z E_K+tol and R31AK E_Dmax <= R31Z E_Dmax+tol and at least one improvement >tol",
                            "GLOBAL_SUPPORTED_AT_SELECTED_HOLDOUT": "reverse primary dominance with same tol",
                            "TRADEOFF_UNRESOLVED": "otherwise"},
            "mandatory_secondary": ["E_O", "E_dotO", "E_Dcol", "E_Drow", "direct_metric_identity_residual", "both_candidate_metric_identity_residuals"],
            "weighted_score_for_final_verdict": False, "execution_authorized": False}
    write(out / "FROZEN_HOLDOUT_DECISION_RULE.json", rule)
    rule_sha = sha((out / "FROZEN_HOLDOUT_DECISION_RULE.json").read_bytes())
    selection_rule = {"schema": "WU088_R31AK_HOLDOUT_SELECTION_RULE_V1", "candidate_set_z_a0": [0.25, .75, 1.5, 2.25, 2.75, 3.25, 3.75],
                      "exclude_prior_direct_exposure": True, "score": "sqrt(DeltaK_model^2+DeltaDmax_model^2)",
                      "select": "maximum S", "exact_tie": "lower z", "final_verdict_score": False}
    write(out / "HOLDOUT_SELECTION_RULE.json", selection_rule)
    selection_rule_sha = sha((out / "HOLDOUT_SELECTION_RULE.json").read_bytes())
    inventory_sha = sha(a.inventory.read_bytes())
    selection = {"schema": "WU088_R31AK_HOLDOUT_SELECTION_V1", "excluded": [{"z_a0": 1.5, "reason": "prior CP4 OD-only direct exposure"}],
                 "candidate_rows": candidate_rows, "selected_z_a0": selected_row["z"], "selected_time_ta": selected_row["time_ta"],
                 "selected_prediction_key": selected_row["prediction_key"], "R31AK_model_aggregate_sha256": model_sha,
                 "R31Z_model_sha256": EXPECTED["global_model"], "eight_node_manifest_sha256": manifest_sha,
                 "frozen_predictions_sha256": prediction_sha, "metadata_adapter_sha256": adapter_sha,
                 "comparator_sha256": comparator_sha, "selection_rule_sha256": selection_rule_sha,
                 "fresh_holdout_inventory_sha256": inventory_sha,
                 "S_design_only": True, "direct_truth_used_for_selection": False}
    write(out / "HOLDOUT_SELECTION.json", selection)
    selection_sha = sha((out / "HOLDOUT_SELECTION.json").read_bytes())
    prereg = {"schema": "WU088_R31AK_NEXT_HOLDOUT_PREREGISTRATION_V1", "selected_z_a0": selected_row["z"],
              "selected_z_decimal": str(selected_row["z"]), "selected_time_ta": selected_row["time_ta"],
              "radial_order": 192, "required_outputs_only": ["mixed_O_47x2", "mixed_D_col_47x2", "mixed_D_row_2x47", "independent_mixed_dotO_47x2"],
              "prediction_key": selected_row["prediction_key"], "training_nodes_z_a0": zvals,
              "R31AK_independent_validation_points": [], "R31AK_model_aggregate_sha256": model_sha,
              "R31AK_model_components": model_components, "R31AK_engine_sha256": engine_sha,
              "R31Z_model_sha256": EXPECTED["global_model"], "eight_node_manifest_sha256": manifest_sha,
              "metadata_adapter_sha256": adapter_sha, "comparator_sha256": comparator_sha,
              "frozen_predictions_sha256": prediction_sha, "selection_sha256": selection_sha,
              "fresh_holdout_inventory_sha256": inventory_sha,
              "selection_rule_sha256": selection_rule_sha, "decision_rule_sha256": rule_sha,
              "primary_metrics": ["E_K", "E_Dmax"], "comparison_tolerance_per_ta": 1e-10,
              "mandatory_secondary": rule["mandatory_secondary"], "execution_authorized": False,
              "direct_output_accessed": False, "science_node_count_this_handoff": 0,
              "source_accuracy_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE",
              "forbidden": ["H", "neutral47", "ionic2", "full49", "trajectory", "other_z", "M3_reference", "post_output_model_retuning"]}
    write(out / "NEXT_VALIDATION_PREREGISTRATION.json", prereg)
    print(json.dumps({"manifest_sha256": manifest_sha, "model_sha256": model_sha, "replay": replay,
                      "indicator": indicator, "selection": selection, "preregistration_sha256": sha((out / "NEXT_VALIDATION_PREREGISTRATION.json").read_bytes())}, indent=2))


if __name__ == "__main__":
    main()
