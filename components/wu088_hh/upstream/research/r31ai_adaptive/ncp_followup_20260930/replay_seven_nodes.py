"""Read-only seven-node R31AI replay and z=2.5 prediction-only lock."""
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
    "policy": "f200fd1837938020c4a99673b1a32f6e652cc4bdcb215318f5588530eb6ac388",
    "helper": "9709bd806d95915c353f5ef95fc36212ac779feedc8c1128818d5c2437b332d3",
    "parent_prereg": "3f42116a959c5a869be3d9be019d84c3231c2ad4a595e6fc99094b773ced1527",
    "six_manifest": "e444e9f1cff7d4cc9425a2f44ff45a6e87199c6bf31ca2b095010364379e7573",
    "z35_comparison": "10dae8d41ecad3db2283515610fcf586ca57aeb2d1af5e5a6382158abd733e4f",
    "z05_od": "1505463b2329e9398b92077d51a9704c4b5f2c5d71288cf811571763a672f80a",
    "z05_jvp": "88b44ec142eef45ef7232f7fd050a0c5ca1773db416986a9a5857d60959b5fc3",
    "z1_od": "020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818",
    "z1_jvp": "b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819",
    "z35_od": "de730fcb4b6b65e86d5910cc456d35eaf33dab3610d0326939434d0f391d610a",
    "z35_jvp": "17d3d306f1e104591f91281f0acb8dae3ed6bc743f1d366da5b6bccb96e82a8c",
}
Z3_OD = "47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af"
Z3_JVP = "9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661"


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def npz(blob: bytes) -> dict:
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


def write(path: Path, obj: dict) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    for field in ("repo", "snapshot", "archive", "outdir"):
        ap.add_argument("--" + field, required=True, type=Path)
    a = ap.parse_args()
    repo, out = a.repo.resolve(), a.outdir.resolve()
    paths = {
        "snapshot": a.snapshot, "archive": a.archive,
        "engine": repo / "research/r31ad_five_node/unit_cell_model.py",
        "global_model": repo / "research/r31z_source_bound/source_bound.py",
        "policy": repo / "research/r31ai_adaptive/MODEL_POLICY.json",
        "helper": repo / "research/r31ai_adaptive/successor_policy.py",
        "parent_prereg": repo / "research/r31ai_adaptive/NEXT_VALIDATION_PREREGISTRATION.json",
        "six_manifest": repo / "research/r31af_adaptive/ncp_followup_20260929/SIX_NODE_INPUT_MANIFEST.json",
        "z35_comparison": repo / "research/r31ah_post_z35/authorized_z35_20260930/Z35_COMPARISON.json",
        "z05_od": repo / "research/r31ae_z05_gate/authorized_z05_20260929/OD_RAW/ASSEMBLED_OD.npz",
        "z05_jvp": repo / "research/r31ae_z05_gate/authorized_z05_20260929/JVP_RAW/ASSEMBLED.npz",
        "z1_od": repo / "research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz",
        "z1_jvp": repo / "research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz",
        "z35_od": repo / "research/r31ah_post_z35/authorized_z35_20260930/OD_RAW/ASSEMBLED_OD.npz",
        "z35_jvp": repo / "research/r31ah_post_z35/authorized_z35_20260930/JVP_RAW/ASSEMBLED.npz",
    }
    blobs = {key: path.read_bytes() for key, path in paths.items()}
    for key, blob in blobs.items():
        if sha(blob) != EXPECTED[key]:
            raise ValueError(f"source/input hash drift: {key}")
    parent_comparison = json.loads(blobs["z35_comparison"])
    if parent_comparison["frozen_decision_rule_verdict"] != "PARETO_SUPPORTED_AT_Z35":
        raise ValueError("R31AH policy does not permit successor training")
    parent_prereg = json.loads(blobs["parent_prereg"])
    model_policy = json.loads(blobs["policy"])
    if parent_prereg["direct_z25_output_accessed"] or parent_prereg["execution_authorized"]:
        raise ValueError("z2.5 prereg is not fresh/unauthorized")
    if model_policy["local_refinement_cells"] != [[0, 1], [3, 4]]:
        raise ValueError("local refinement policy drift")
    with zipfile.ZipFile(a.archive) as z:
        z3_od_member = "completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz"
        z3_jvp_member = "completion/mixed_derivative/B192_z3/ASSEMBLED.npz"
        z3_od_blob, z3_jvp_blob = z.read(z3_od_member), z.read(z3_jvp_member)
        z25_members = [name for name in z.namelist() if name.startswith(("completion/mixed_h/od/B192_z2.5/", "completion/mixed_derivative/B192_z2.5/"))]
    if sha(z3_od_blob) != Z3_OD or sha(z3_jvp_blob) != Z3_JVP:
        raise ValueError("z3 source member drift")
    if z25_members:
        raise ValueError("existing z2.5 archive member: fresh holdout requires review")
    runtime = Path("/root/WU088_R31AG_Z35_RUNTIME_20260930")
    z25_local_dirs = [runtime / "completion/mixed_h/od/B192_z2.5", runtime / "completion/mixed_derivative/B192_z2.5"]
    if any(path.exists() for path in z25_local_dirs):
        raise ValueError("existing z2.5 runtime output: fresh holdout requires review")

    fit = npz(blobs["snapshot"])
    od05, jvp05 = npz(blobs["z05_od"]), npz(blobs["z05_jvp"])
    od1, jvp1 = npz(blobs["z1_od"]), npz(blobs["z1_jvp"])
    od3, jvp3 = npz(z3_od_blob), npz(z3_jvp_blob)
    od35, jvp35 = npz(blobs["z35_od"]), npz(blobs["z35_jvp"])
    zvals = [0., .5, 1., 2., 3., 3.5, 4.]
    roles = ["TRAINING"] * 5 + ["PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AI_TRAINING", "TRAINING"]
    raw = [
        (fit["z0_od_O"], fit["z0_od_D_col"], fit["z0_od_D_row"], fit["z0_j_dotO"]),
        (od05["O"], od05["D_col"], od05["D_row"], jvp05["dotO"]),
        (od1["O"], od1["D_col"], od1["D_row"], jvp1["dotO"]),
        (fit["direct_O"][:47, 47:], fit["direct_D"][:47, 47:], fit["direct_D"][47:, :47], fit["direct_dotO"][:47, 47:]),
        (od3["O"], od3["D_col"], od3["D_row"], jvp3["dotO"]),
        (od35["O"], od35["D_col"], od35["D_row"], jvp35["dotO"]),
        (fit["z4_od_O"], fit["z4_od_D_col"], fit["z4_od_D_row"], fit["z4_j_dotO"]),
    ]
    sources = [
        {"path": str(a.snapshot), "objects": ["z0_od_O", "z0_od_D_col", "z0_od_D_row", "z0_j_dotO"], "sha256": EXPECTED["snapshot"], "bytes": len(blobs["snapshot"])},
        {"OD_path": str(paths["z05_od"]), "OD_sha256": EXPECTED["z05_od"], "OD_bytes": len(blobs["z05_od"]), "JVP_path": str(paths["z05_jvp"]), "JVP_sha256": EXPECTED["z05_jvp"], "JVP_bytes": len(blobs["z05_jvp"])},
        {"OD_path": str(paths["z1_od"]), "OD_sha256": EXPECTED["z1_od"], "OD_bytes": len(blobs["z1_od"]), "JVP_path": str(paths["z1_jvp"]), "JVP_sha256": EXPECTED["z1_jvp"], "JVP_bytes": len(blobs["z1_jvp"])},
        {"path": str(a.snapshot), "objects": ["direct_O[:47,47:]", "direct_D[:47,47:]", "direct_D[47:,:47]", "direct_dotO[:47,47:]"], "sha256": EXPECTED["snapshot"], "bytes": len(blobs["snapshot"]), "upstream_member": "WU088_HH_R31S_NCP_20260928/evidence/z2/R31S_FULL49_z2.npz"},
        {"archive": str(a.archive), "OD_member": z3_od_member, "OD_sha256": Z3_OD, "OD_bytes": len(z3_od_blob), "JVP_member": z3_jvp_member, "JVP_sha256": Z3_JVP, "JVP_bytes": len(z3_jvp_blob)},
        {"OD_path": str(paths["z35_od"]), "OD_sha256": EXPECTED["z35_od"], "OD_bytes": len(blobs["z35_od"]), "JVP_path": str(paths["z35_jvp"]), "JVP_sha256": EXPECTED["z35_jvp"], "JVP_bytes": len(blobs["z35_jvp"]), "one_shot_parent": "research/r31ah_post_z35/authorized_z35_20260930/RETURN.json"},
        {"path": str(a.snapshot), "objects": ["z4_od_O", "z4_od_D_col", "z4_od_D_row", "z4_j_dotO"], "sha256": EXPECTED["snapshot"], "bytes": len(blobs["snapshot"])},
    ]
    velocity = float(fit["velocity"])
    times = [z / velocity for z in zvals]
    manifest_rows = []
    for z, t, role, (O, Dc, Dr, dotO), source in zip(zvals, times, roles, raw, sources):
        if tuple(x.shape for x in (O, Dc, Dr, dotO)) != ((47, 2), (47, 2), (2, 47), (47, 2)):
            raise ValueError(f"node shape drift at z={z}")
        row = {"z_a0": z, "time_ta": t, "role": role, "source": source,
               "fields": {"O": "47x2", "D_col": "47x2", "D_row": "2x47", "independent_dotO": "47x2"},
               "raw_dtypes": dict(zip(("O", "D_col", "D_row", "dotO"), (str(x.dtype) for x in (O, Dc, Dr, dotO)))),
               "raw_metric_identity_max_abs": float(np.max(np.abs(dotO - Dc - Dr.conj().T))),
               "basis_order_phase_contract": "CP4 frozen B192 47 channel order: centre0 24 then centre1 excited23; ionic columns 2; phase_E and tau=z/velocity; independent dotO is analytic JVP in 1/t_a; producer lines pinned in R31Y PRODUCER_INTAKE.json"}
        if z in (.5, 1., 3., 3.5):
            jvp_O = {.5: jvp05["O"], 1.: jvp1["O"], 3.: jvp3["O"], 3.5: jvp35["O"]}[z]
            row["OD_vs_JVP_O_raw_max_abs"] = float(np.max(np.abs(O - jvp_O)))
        manifest_rows.append(row)
    manifest = {"schema": "WU088_R31AI_SEVEN_NODE_INPUT_MANIFEST_V1", "nodes": manifest_rows,
                "R31AI_independent_validation_points": [], "comparison_dtype": "complex128; original complex256/complex128 raw arrays preserved", "source_array_mutation": False,
                "upstream_provenance": ["research/r31y_lowrank/ncp_followup_20260929/PRODUCER_INTAKE.json", "research/r31ah_post_z35/authorized_z35_20260930/RETURN.json"]}
    write(out / "SEVEN_NODE_INPUT_MANIFEST.json", manifest)

    engine = module(paths["engine"], "r31ad_engine_unchanged_r31ai")
    global_model = module(paths["global_model"], "r31z_global_unchanged_r31ai")
    helper = module(paths["helper"], "r31ai_successor_policy_unchanged")
    values = [cast(x[0]) for x in raw]
    dcols = [cast(x[1]) for x in raw]
    drows = [cast(x[2]) for x in raw]
    dots = [cast(x[3]) for x in raw]
    ks = [(dc - dr.conj().T) / 2 for dc, dr in zip(dcols, drows)]
    maxima = {key: 0. for key in ("O", "dotO", "K", "D_col", "D_row")}
    for j, t in enumerate(times):
        O, dotO, Dc, Dr, K, _ = engine.piecewise_candidate(times, values, dots, ks, t)
        for key, error in (("O", O-values[j]), ("dotO", dotO-dots[j]), ("K", K-ks[j]), ("D_col", Dc-dcols[j]), ("D_row", Dr-drows[j])):
            maxima[key] = max(maxima[key], n2(error))
    continuity = {key: 0. for key in maxima}
    for j in range(1, 6):
        lo, ld = engine.cubic_hermite(values[j-1], values[j], dots[j-1], dots[j], times[j]-times[j-1], 1.)
        ro, rd = engine.cubic_hermite(values[j], values[j+1], dots[j], dots[j+1], times[j+1]-times[j], 0.)
        for key, error in (("O", lo-ro), ("dotO", ld-rd), ("K", ks[j]-ks[j]), ("D_col", ld/2+ks[j]-rd/2-ks[j]), ("D_row", (ld/2-ks[j]).conj().T-(rd/2-ks[j]).conj().T)):
            continuity[key] = max(continuity[key], n2(error))
    metric = 0.
    for t in np.linspace(times[0], times[-1], 401):
        _, dotO, Dc, Dr, _, _ = engine.piecewise_candidate(times, values, dots, ks, float(t))
        metric = max(metric, n2(dotO - Dc - Dr.conj().T))
    if max(maxima.values()) > 1e-12 or max(continuity.values()) > 1e-12 or metric > 1e-12:
        raise ValueError("seven-node algebraic replay failed")
    model_replay = {"schema": "WU088_R31AI_SEVEN_NODE_MODEL_REPLAY_V1", "model_name": model_policy["model_name"],
                    "engine_sha256": EXPECTED["engine"], "cells_z_a0": [[0,.5],[.5,1],[1,2],[2,3],[3,3.5],[3.5,4]],
                    "node_reproduction_max_2norm": maxima, "internal_node_continuity_max_2norm": continuity,
                    "dense_grid_points": 401, "dense_grid_metric_identity_max_2norm": metric,
                    "source_array_mutation": False, "science_node_count": 0, "predictive_validation_performed": False}
    write(out / "R31AI_MODEL_REPLAY.json", model_replay)

    six_indices = (0, 1, 2, 3, 4, 6)
    six_times = [times[i] for i in six_indices]
    six_values = [values[i] for i in six_indices]
    six_dots = [dots[i] for i in six_indices]
    six_ks = [ks[i] for i in six_indices]
    t35 = times[5]
    old_O, old_dot, old_Dc, old_Dr, old_K, _ = engine.piecewise_candidate(six_times, six_values, six_dots, six_ks, t35)
    EO = n2(old_O-values[5]); Edot = n2(old_dot-dots[5]); EK = n2(old_K-ks[5])
    EDmax = max(n2(old_Dc-dcols[5]), n2(old_Dr-drows[5]))
    parent = parent_comparison["R31AF_adaptive_six_node"]
    for actual, expected in ((EO, parent["E_O"]), (Edot, parent["E_dotO_per_ta"]), (EK, parent["E_K_per_ta"]), (EDmax, parent["E_Dmax_per_ta"])):
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-13):
            raise ValueError("z3.5 parent midpoint error mismatch")
    bounds = helper.midpoint_lower_bounds(EO, EK, 1/velocity, 1.)
    indicator = {"schema": "WU088_R31AI_Z35_APOSTERIORI_INDICATOR_V1", "E_O": EO, "E_dotO_per_ta": Edot, "E_K_per_ta": EK, "E_Dmax_per_ta": EDmax,
                 "cell_width_ta": 1/velocity, "cell_width_a0": 1., "necessary_lower_bounds": bounds,
                 "R31AF_original_verdict": "PARETO_SUPPORTED_AT_Z35", "R31AF_original_verdict_scope": "single-point relative support only",
                 "direct_point_role": "PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AI_TRAINING", "certified_source_error_enclosure": False, "empirical_error_reduction_claimed": False}
    write(out / "Z35_APOSTERIORI_INDICATOR.json", indicator)

    t25 = 2.5 / velocity
    new = engine.piecewise_candidate(times, values, dots, ks, t25)[:5]
    predecessor = engine.piecewise_candidate(six_times, six_values, six_dots, six_ks, t25)[:5]
    unchanged = {key: n2(new[i]-predecessor[i]) for i, key in enumerate(("O", "dotO", "Dcol", "Drow", "K"))}
    if max(unchanged.values()) > 1e-14:
        raise ValueError("unaffected [2,3] prediction changed")
    gO, gdot = global_model.quintic_hermite([values[i] for i in (0, 3, 6)], [dots[i] for i in (0, 3, 6)], times[-1], 2.5/4)
    gK = global_model.quadratic_three_nodes([ks[i] for i in (0, 3, 6)], 2.5/4)
    global_prediction = (gO, gdot, gdot/2+gK, (gdot/2-gK).conj().T, gK)
    separation = engine.separation(global_prediction, new)
    parent_information = helper.next_holdout_information()
    for actual, expected in ((separation["K"], parent_information["DeltaK_per_ta"]),
                             (separation["Dmax"], parent_information["DeltaDmax_per_ta"]),
                             (separation["T_like_primary"], parent_information["S_design_only_per_ta"])):
        if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-13):
            raise ValueError("z2.5 pre-output information drift")
    prediction = {"schema": "WU088_R31AI_Z25_PREDICTION_ONLY_V1", "selected_z_a0": 2.5, "selected_time_ta": 5.589693097584528,
                  "computed_time_ta": t25,
                  "z25_direct_output_accessed": False, "z25_archive_members": z25_members, "z25_local_runtime_paths_existing": [],
                  "unchanged_unaffected_cell_prediction_max_2norm": unchanged,
                  "DeltaK_model": separation["K"], "DeltaDcol_model": separation["Dcol"], "DeltaDrow_model": separation["Drow"],
                  "DeltaDmax_model": separation["Dmax"], "S_design_only": separation["T_like_primary"],
                  "truth_independent_half_gaps": {"E_K": separation["K"]/2, "E_Dmax": separation["Dmax"]/2},
                  "S_used_as_final_model_selection_score": False, "science_node_count": 0}
    write(out / "Z25_PREDICTION_ONLY.json", prediction)

    rule = {"schema": "WU088_R31AI_Z25_FUTURE_DECISION_RULE_V1", "z_a0": 2.5, "radial_order": 192,
            "models": ["R31AI_ADAPTIVE_SEVEN_NODE_CUBIC_O_LINEAR_K", "R31Z_GLOBAL_QUINTIC_O_QUADRATIC_K"],
            "primary_metrics": ["E_K", "E_Dmax"], "comparison_tolerance": 1e-10,
            "pareto_rule": {"PARETO_SUPPORTED_AT_Z25": "R31AI E_K <= R31Z E_K+tol and R31AI E_Dmax <= R31Z E_Dmax+tol and at least one improvement >tol",
                            "GLOBAL_SUPPORTED_AT_Z25": "reverse primary dominance with same tol", "TRADEOFF_UNRESOLVED": "otherwise"},
            "mandatory_secondary": ["E_O", "E_dotO", "E_Dcol", "E_Drow", "direct_metric_identity_residual", "both_candidate_metric_identity_residuals"],
            "weighted_score_for_final_decision": False, "execution_authorized": False}
    write(out / "FROZEN_Z25_DECISION_RULE.json", rule)
    manifest_sha = sha((out / "SEVEN_NODE_INPUT_MANIFEST.json").read_bytes())
    model_inputs = {"engine_sha256": EXPECTED["engine"], "policy_sha256": EXPECTED["policy"], "helper_sha256": EXPECTED["helper"], "seven_node_manifest_sha256": manifest_sha}
    model_sha = sha(json.dumps(model_inputs, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
    prereg = {"schema": "WU088_R31AI_Z25_FROZEN_PREREGISTRATION_V1", "selected_z_a0": 2.5, "selected_time_ta": 5.589693097584528, "radial_order": 192,
              "required_outputs_only": ["mixed_O_47x2", "mixed_D_col_47x2", "mixed_D_row_2x47", "independent_mixed_dotO_47x2"],
              "training_node_z_a0": zvals, "R31AI_independent_validation_points": [],
              "R31AI_model_aggregate_sha256": model_sha, "R31AI_model_aggregate_components": model_inputs,
              "R31Z_model_sha256": EXPECTED["global_model"], "seven_node_manifest_sha256": manifest_sha,
              "decision_rule_sha256": sha((out / "FROZEN_Z25_DECISION_RULE.json").read_bytes()),
              "z25_prediction_only_sha256": sha((out / "Z25_PREDICTION_ONLY.json").read_bytes()),
              "future_primary_metrics": ["E_K", "E_Dmax"], "comparison_tolerance": 1e-10,
              "future_verdicts": ["PARETO_SUPPORTED_AT_Z25", "GLOBAL_SUPPORTED_AT_Z25", "TRADEOFF_UNRESOLVED"],
              "weighted_score_for_final_decision": False, "direct_z25_output_accessed": False,
              "execution_authorized": False, "science_node_count_this_handoff": 0,
              "forbidden": ["H", "neutral47", "ionic2", "full49", "trajectory", "other_z", "M3_reference", "post_prereg_model_retuning"]}
    write(out / "NEXT_VALIDATION_PREREGISTRATION.json", prereg)
    for key, path in paths.items():
        if sha(path.read_bytes()) != EXPECTED[key]:
            raise ValueError(f"source array/file mutated: {key}")
    print(json.dumps({"manifest_sha256": manifest_sha, "replay": model_replay, "indicator": indicator,
                      "prediction": prediction, "preregistration_sha256": sha((out / "NEXT_VALIDATION_PREREGISTRATION.json").read_bytes())}, indent=2))


if __name__ == "__main__":
    main()
