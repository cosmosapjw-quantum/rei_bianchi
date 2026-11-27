"""Apply the frozen R31AF/R31Z E_K/E_Dmax rule once to direct z=3.5."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from scipy.linalg import norm

LOCKS = {
    "engine": ("research/r31ad_five_node/unit_cell_model.py", "ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0"),
    "adaptive_policy": ("research/r31af_adaptive/adaptive_policy.py", "720b221a9e01ab7fc1bbd482b600ea785fed0b8c6b80b5834c576a75c2b70756"),
    "global_model": ("research/r31z_source_bound/source_bound.py", "4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034"),
    "manifest": ("research/r31af_adaptive/ncp_followup_20260929/SIX_NODE_INPUT_MANIFEST.json", "e444e9f1cff7d4cc9425a2f44ff45a6e87199c6bf31ca2b095010364379e7573"),
    "selection": ("research/r31af_adaptive/ncp_followup_20260929/Z35_PREDICTION_SELECTION.json", "546026387ecae9952b0397fb0dd26ad0633465739d8bbb82878f0f4c532c545e"),
    "rule": ("research/r31af_adaptive/ncp_followup_20260929/FROZEN_Z35_DECISION_RULE.json", "52b995b2f5516cf586cf1cbcdb681ec521f1b911a7538e3999a11d0f3bd62560"),
    "prereg": ("research/r31af_adaptive/ncp_followup_20260929/NEXT_VALIDATION_PREREGISTRATION.json", "ec4613f5300ec38a488eae75f5c7267a2f1a166c34e45d54bb9fa8b449537447"),
    "post_policy": ("research/r31ah_post_z35/POST_Z35_DECISION_POLICY.json", "b7d9928e23d1f3cd8abf0fe7be34a5868d6760bfab388ac626bab6c1c524dbc8"),
    "post_policy_helper": ("research/r31ah_post_z35/post_validation_policy.py", "78af28d506edd3e7dedcb3257f10258ee1ed4477a8cabe7d78ecb1945142f6a5"),
    "snapshot": (None, "565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079"),
    "archive": (None, "c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9"),
    "z05_od": ("research/r31ae_z05_gate/authorized_z05_20260929/OD_RAW/ASSEMBLED_OD.npz", "1505463b2329e9398b92077d51a9704c4b5f2c5d71288cf811571763a672f80a"),
    "z05_jvp": ("research/r31ae_z05_gate/authorized_z05_20260929/JVP_RAW/ASSEMBLED.npz", "88b44ec142eef45ef7232f7fd050a0c5ca1773db416986a9a5857d60959b5fc3"),
    "z1_od": ("research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz", "020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818"),
    "z1_jvp": ("research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz", "b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819"),
}
Z3_OD = "47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af"
Z3_JVP = "9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def npz(blob: bytes) -> dict:
    with np.load(io.BytesIO(blob), allow_pickle=False) as source:
        return {key: source[key] for key in source.files}


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


def main() -> None:
    ap = argparse.ArgumentParser()
    for name in ("repo", "snapshot", "archive", "od", "jvp", "ledger", "out"):
        ap.add_argument("--" + name, required=True, type=Path)
    a = ap.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    repo = a.repo.resolve()
    paths = {key: repo / rel if rel else getattr(a, key) for key, (rel, _) in LOCKS.items()}
    actual = {key: sha(path) for key, path in paths.items()}
    if any(actual[key] != LOCKS[key][1] for key in LOCKS):
        raise ValueError("frozen source/input hash drift")
    prereg = json.loads(paths["prereg"].read_text())
    rule = json.loads(paths["rule"].read_text())
    selection = json.loads(paths["selection"].read_text())
    if prereg["selected_z_a0"] != selection["selected_z_a0"] or prereg["selected_z_a0"] != 3.5:
        raise ValueError("selected geometry drift")
    if prereg["comparison_tolerance"] != rule["comparison_tolerance"] or rule["comparison_tolerance"] != 1e-10:
        raise ValueError("comparison tolerance drift")
    ledger = json.loads(a.ledger.read_text())
    if ledger.get("one_shot_state") != "CONSUMED_OUTPUTS_COMPLETE" or ledger.get("science_commands_started") != 2:
        raise ValueError("one-shot ledger incomplete")
    od_report = json.loads(a.od.with_name("RESULTS.json").read_text())
    jvp_report = json.loads(a.jvp.with_name("RESULTS.json").read_text())
    od_identity = json.loads(a.od.with_name("IDENTITY.json").read_text())
    jvp_identity = json.loads(a.jvp.with_name("IDENTITY.json").read_text())
    if (float(od_identity["z"]), float(jvp_identity["z"]), od_identity["n"], jvp_identity["n"]) != (3.5, 3.5, 192, 192):
        raise ValueError("direct geometry/order drift")
    if sha(a.od) != od_report["sha256"] or sha(a.jvp) != jvp_report["sha256"]:
        raise ValueError("direct output identity drift")
    if od_report["Hamiltonian_included"] is not False or od_report["independent_dotO_included"] is not False:
        raise ValueError("OD scope drift")
    od, jvp = npz(a.od.read_bytes()), npz(a.jvp.read_bytes())
    if tuple(x.shape for x in (od["O"], od["D_col"], od["D_row"], jvp["dotO"], jvp["O"])) != ((47, 2), (47, 2), (2, 47), (47, 2), (47, 2)):
        raise ValueError("direct array shape drift")
    source_O_gap = jvp["O"] - od["O"]
    direct_metric_raw = jvp["dotO"] - od["D_col"] - od["D_row"].conj().T
    source_bridge_max_abs = max(float(np.max(np.abs(source_O_gap))), float(np.max(np.abs(direct_metric_raw))))

    fit = npz(paths["snapshot"].read_bytes())
    od05, jvp05 = npz(paths["z05_od"].read_bytes()), npz(paths["z05_jvp"].read_bytes())
    od1, jvp1 = npz(paths["z1_od"].read_bytes()), npz(paths["z1_jvp"].read_bytes())
    with zipfile.ZipFile(paths["archive"]) as z:
        od3_blob = z.read("completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz")
        jvp3_blob = z.read("completion/mixed_derivative/B192_z3/ASSEMBLED.npz")
    if hashlib.sha256(od3_blob).hexdigest() != Z3_OD or hashlib.sha256(jvp3_blob).hexdigest() != Z3_JVP:
        raise ValueError("z3 training data drift")
    od3, jvp3 = npz(od3_blob), npz(jvp3_blob)
    raw = [
        (fit["z0_od_O"], fit["z0_od_D_col"], fit["z0_od_D_row"], fit["z0_j_dotO"]),
        (od05["O"], od05["D_col"], od05["D_row"], jvp05["dotO"]),
        (od1["O"], od1["D_col"], od1["D_row"], jvp1["dotO"]),
        (fit["direct_O"][:47, 47:], fit["direct_D"][:47, 47:], fit["direct_D"][47:, :47], fit["direct_dotO"][:47, 47:]),
        (od3["O"], od3["D_col"], od3["D_row"], jvp3["dotO"]),
        (fit["z4_od_O"], fit["z4_od_D_col"], fit["z4_od_D_row"], fit["z4_j_dotO"]),
    ]
    values = [cast(row[0]) for row in raw]
    dcols = [cast(row[1]) for row in raw]
    drows = [cast(row[2]) for row in raw]
    dots = [cast(row[3]) for row in raw]
    ks = [(dc - dr.conj().T) / 2 for dc, dr in zip(dcols, drows)]
    velocity = float(fit["velocity"])
    times = [z / velocity for z in (0, .5, 1, 2, 3, 4)]
    t = 3.5 / velocity
    engine = module(paths["engine"], "r31af_engine_frozen_z35")
    global_model = module(paths["global_model"], "r31z_global_frozen_z35")
    post_policy = module(repo / "research/r31ah_post_z35/post_validation_policy.py", "r31ah_policy_frozen_z35")
    local = engine.piecewise_candidate(times, values, dots, ks, t)[:5]
    gO, gdot = global_model.quintic_hermite([values[i] for i in (0, 3, 5)], [dots[i] for i in (0, 3, 5)], times[-1], 3.5 / 4)
    gK = global_model.quadratic_three_nodes([ks[i] for i in (0, 3, 5)], 3.5 / 4)
    global_prediction = (gO, gdot, gdot / 2 + gK, (gdot / 2 - gK).conj().T, gK)
    direct = (cast(od["O"]), cast(jvp["dotO"]), cast(od["D_col"]), cast(od["D_row"]))
    direct_K = (direct[2] - direct[3].conj().T) / 2

    def errors(pred):
        O, dotO, Dcol, Drow, K = pred
        result = {"E_O": n2(O - direct[0]), "E_dotO_per_ta": n2(dotO - direct[1]), "E_Dcol_per_ta": n2(Dcol - direct[2]), "E_Drow_per_ta": n2(Drow - direct[3]), "E_K_per_ta": n2(K - direct_K), "candidate_metric_identity_residual_2norm": n2(dotO - Dcol - Drow.conj().T)}
        result["E_Dmax_per_ta"] = max(result["E_Dcol_per_ta"], result["E_Drow_per_ta"])
        return result

    local_error, global_error = errors(local), errors(global_prediction)
    primary = ("E_K_per_ta", "E_Dmax_per_ta")
    tol = 1e-10
    local_support = all(local_error[k] <= global_error[k] + tol for k in primary) and any(global_error[k] - local_error[k] > tol for k in primary)
    global_support = all(global_error[k] <= local_error[k] + tol for k in primary) and any(local_error[k] - global_error[k] > tol for k in primary)
    if local_support and global_support:
        raise ValueError("inconsistent Pareto rule")
    verdict = "PARETO_SUPPORTED_AT_Z35" if local_support else "GLOBAL_SUPPORTED_AT_Z35" if global_support else "TRADEOFF_UNRESOLVED"
    action = post_policy.post_z35_action(verdict)
    if verdict not in json.loads(paths["post_policy"].read_text())["verdicts"]:
        raise ValueError("post-result policy verdict drift")
    result = {
        "schema": "WU088_R31AF_Z35_ONE_SHOT_FROZEN_COMPARISON_V1", "z_a0": 3.5, "time_ta": t, "radial_order": 192,
        "direct_outputs": {"OD": {"path": str(a.od), "sha256": sha(a.od), "bytes": a.od.stat().st_size}, "JVP": {"path": str(a.jvp), "sha256": sha(a.jvp), "bytes": a.jvp.stat().st_size}},
        "frozen_hashes": actual, "comparison_dtype": "complex128; raw complex256 preserved", "training_nodes_z_a0": [0, .5, 1, 2, 3, 4],
        "direct_source_O_gap_raw_max_abs": float(np.max(np.abs(source_O_gap))),
        "direct_source_O_gap_2norm_complex128": n2(source_O_gap),
        "direct_metric_identity_raw_max_abs": float(np.max(np.abs(direct_metric_raw))),
        "direct_metric_identity_2norm_complex128": n2(direct[1] - direct[2] - direct[3].conj().T),
        "source_bridge_pass_existing_2e_minus_12_tolerance": source_bridge_max_abs <= 2e-12,
        "R31AF_adaptive_six_node": local_error, "R31Z_global": global_error,
        "primary_comparison_tolerance": tol, "frozen_decision_rule_verdict": verdict,
        "R31AH_post_z35_action": action, "design_score_used_for_final_verdict": False,
        "independent_z35_single_point_validation": source_bridge_max_abs <= 2e-12,
        "z35_residual_used_to_retune_model": False, "z25_direct_output_accessed": False,
        "interval_wide_accuracy_admitted": False, "transition_error_admitted": False, "trajectory_accuracy_admitted": False,
        "full_cell_admitted": False, "H_skip_admitted": False, "production_admitted": False,
    }
    if any(sha(path) != LOCKS[key][1] for key, path in paths.items()):
        raise ValueError("post-comparison frozen source/input drift")
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    a.out.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
