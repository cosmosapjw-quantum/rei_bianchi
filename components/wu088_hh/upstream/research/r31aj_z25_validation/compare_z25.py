"""Frozen z=2.5 prediction and one-shot comparison adapter.

The prelock command reads training nodes only. The compare command reads direct
OD/JVP after the prelock is published and checks its byte identity.
"""
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
    "scope": ("research/r31aj_z25_validation/AUTHORIZATION_SCOPE_CANONICAL.json", "78d960c041536f2baa2160639e5a60878f43f73aadee2e3174ffd5a27d8a68e7"),
    "prereg": ("research/r31ai_adaptive/ncp_followup_20260930/NEXT_VALIDATION_PREREGISTRATION.json", "10d05889a336541c81f2153bb232f254c406ebe45d22da6e5470230b40b1a691"),
    "rule": ("research/r31ai_adaptive/ncp_followup_20260930/FROZEN_Z25_DECISION_RULE.json", "c5712e2539a7db7dda02c563c327c51edc27fb30741df180f19d1cee0cb21d86"),
    "engine": ("research/r31ad_five_node/unit_cell_model.py", "ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0"),
    "policy": ("research/r31ai_adaptive/MODEL_POLICY.json", "f200fd1837938020c4a99673b1a32f6e652cc4bdcb215318f5588530eb6ac388"),
    "helper": ("research/r31ai_adaptive/successor_policy.py", "9709bd806d95915c353f5ef95fc36212ac779feedc8c1128818d5c2437b332d3"),
    "manifest": ("research/r31ai_adaptive/ncp_followup_20260930/SEVEN_NODE_INPUT_MANIFEST.json", "57a1379cc7b658fb8f9eebe2f47cb48f806c3f0ca0292e8e52f53d82d703835b"),
    "global": ("research/r31z_source_bound/source_bound.py", "4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034"),
    "prediction_record": ("research/r31ai_adaptive/ncp_followup_20260930/Z25_PREDICTION_ONLY.json", "64f47cc6a5e6906071636a10d022d4575f9f458c10c31f59881e1808d7b5fba4"),
    "snapshot": (None, "565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079"),
    "archive": (None, "c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9"),
    "z05_od": ("research/r31ae_z05_gate/authorized_z05_20260929/OD_RAW/ASSEMBLED_OD.npz", "1505463b2329e9398b92077d51a9704c4b5f2c5d71288cf811571763a672f80a"),
    "z05_jvp": ("research/r31ae_z05_gate/authorized_z05_20260929/JVP_RAW/ASSEMBLED.npz", "88b44ec142eef45ef7232f7fd050a0c5ca1773db416986a9a5857d60959b5fc3"),
    "z1_od": ("research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz", "020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818"),
    "z1_jvp": ("research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz", "b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819"),
    "z35_od": ("research/r31ah_post_z35/authorized_z35_20260930/OD_RAW/ASSEMBLED_OD.npz", "de730fcb4b6b65e86d5910cc456d35eaf33dab3610d0326939434d0f391d610a"),
    "z35_jvp": ("research/r31ah_post_z35/authorized_z35_20260930/JVP_RAW/ASSEMBLED.npz", "17d3d306f1e104591f91281f0acb8dae3ed6bc743f1d366da5b6bccb96e82a8c"),
}
Z3_OD = "47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af"
Z3_JVP = "9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arrays(blob: bytes) -> dict:
    with np.load(io.BytesIO(blob), allow_pickle=False) as source:
        return {key: source[key] for key in source.files}


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def cast(value):
    return np.asarray(value, dtype=np.complex128)


def n2(value) -> float:
    return float(norm(cast(value), 2))


def check_locks(repo: Path, snapshot: Path, archive: Path) -> dict:
    paths = {key: repo / rel if rel else {"snapshot": snapshot, "archive": archive}[key]
             for key, (rel, _) in LOCKS.items()}
    actual = {key: sha(path) for key, path in paths.items()}
    if any(actual[key] != LOCKS[key][1] for key in LOCKS):
        raise ValueError("source/input lock drift")
    rule = json.loads(paths["rule"].read_text())
    prereg = json.loads(paths["prereg"].read_text())
    if rule["comparison_tolerance"] != prereg["comparison_tolerance"] or rule["comparison_tolerance"] != 1e-10:
        raise ValueError("decision tolerance drift")
    if rule["primary_metrics"] != ["E_K", "E_Dmax"] or prereg["selected_z_a0"] != 2.5:
        raise ValueError("decision/geometry drift")
    return paths


def prelock(args, paths: dict) -> None:
    if args.predictions.exists():
        raise FileExistsError(args.predictions)
    fit = arrays(paths["snapshot"].read_bytes())
    od05, jvp05 = arrays(paths["z05_od"].read_bytes()), arrays(paths["z05_jvp"].read_bytes())
    od1, jvp1 = arrays(paths["z1_od"].read_bytes()), arrays(paths["z1_jvp"].read_bytes())
    od35, jvp35 = arrays(paths["z35_od"].read_bytes()), arrays(paths["z35_jvp"].read_bytes())
    with zipfile.ZipFile(paths["archive"]) as z:
        od3_blob = z.read("completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz")
        jvp3_blob = z.read("completion/mixed_derivative/B192_z3/ASSEMBLED.npz")
    if hashlib.sha256(od3_blob).hexdigest() != Z3_OD or hashlib.sha256(jvp3_blob).hexdigest() != Z3_JVP:
        raise ValueError("z3 training member drift")
    od3, jvp3 = arrays(od3_blob), arrays(jvp3_blob)
    raw = [
        (fit["z0_od_O"], fit["z0_od_D_col"], fit["z0_od_D_row"], fit["z0_j_dotO"]),
        (od05["O"], od05["D_col"], od05["D_row"], jvp05["dotO"]),
        (od1["O"], od1["D_col"], od1["D_row"], jvp1["dotO"]),
        (fit["direct_O"][:47, 47:], fit["direct_D"][:47, 47:], fit["direct_D"][47:, :47], fit["direct_dotO"][:47, 47:]),
        (od3["O"], od3["D_col"], od3["D_row"], jvp3["dotO"]),
        (od35["O"], od35["D_col"], od35["D_row"], jvp35["dotO"]),
        (fit["z4_od_O"], fit["z4_od_D_col"], fit["z4_od_D_row"], fit["z4_j_dotO"]),
    ]
    values = [cast(row[0]) for row in raw]
    dcols = [cast(row[1]) for row in raw]
    drows = [cast(row[2]) for row in raw]
    dots = [cast(row[3]) for row in raw]
    ks = [(dc - dr.conj().T) / 2 for dc, dr in zip(dcols, drows)]
    velocity = float(fit["velocity"])
    times = [z / velocity for z in (0, .5, 1, 2, 3, 3.5, 4)]
    t = 2.5 / velocity
    engine = module(paths["engine"], "r31ad_engine_frozen_z25")
    global_model = module(paths["global"], "r31z_global_frozen_z25")
    local = engine.piecewise_candidate(times, values, dots, ks, t)[:5]
    gO, gdot = global_model.quintic_hermite([values[i] for i in (0, 3, 6)], [dots[i] for i in (0, 3, 6)], times[-1], 2.5 / 4)
    gK = global_model.quadratic_three_nodes([ks[i] for i in (0, 3, 6)], 2.5 / 4)
    global_pred = (gO, gdot, gdot / 2 + gK, (gdot / 2 - gK).conj().T, gK)
    sep_K = n2(local[4] - global_pred[4])
    sep_Dmax = max(n2(local[2] - global_pred[2]), n2(local[3] - global_pred[3]))
    if abs(sep_K - .1912237840334797) > 1e-13 or abs(sep_Dmax - .20561180584475613) > 1e-13:
        raise ValueError("pre-output prediction separation drift")
    np.savez(args.predictions, **{f"{who}_{key}": array for who, pred in (("R31AI", local), ("R31Z", global_pred))
                                   for key, array in zip(("O", "dotO", "Dcol", "Drow", "K"), pred)})
    print(json.dumps({"prediction_sha256": sha(args.predictions), "prediction_bytes": args.predictions.stat().st_size,
                      "time_ta_computed": t, "DeltaK": sep_K, "DeltaDmax": sep_Dmax}, indent=2))


def compare(args, paths: dict) -> None:
    lock = json.loads(args.lock.read_text())
    if sha(args.predictions) != lock["prediction_arrays_sha256"] or sha(Path(__file__)) != lock["comparator_sha256"]:
        raise ValueError("pre-output comparator/prediction drift")
    od_report = json.loads(args.od.with_name("RESULTS.json").read_text())
    jvp_report = json.loads(args.jvp.with_name("RESULTS.json").read_text())
    od_id = json.loads(args.od.with_name("IDENTITY.json").read_text())
    jvp_id = json.loads(args.jvp.with_name("IDENTITY.json").read_text())
    if (od_id["z"], jvp_id["z"], od_id["n"], jvp_id["n"]) != (2.5, 2.5, 192, 192):
        raise ValueError("direct geometry/order drift")
    if sha(args.od) != od_report["sha256"] or sha(args.jvp) != jvp_report["sha256"]:
        raise ValueError("direct output identity drift")
    if od_report["Hamiltonian_included"] is not False or od_report["independent_dotO_included"] is not False:
        raise ValueError("OD output scope drift")
    od, jvp = arrays(args.od.read_bytes()), arrays(args.jvp.read_bytes())
    if tuple(x.shape for x in (od["O"], od["D_col"], od["D_row"], jvp["dotO"], jvp["O"])) != ((47, 2), (47, 2), (2, 47), (47, 2), (47, 2)):
        raise ValueError("direct array shape drift")
    direct = (cast(od["O"]), cast(jvp["dotO"]), cast(od["D_col"]), cast(od["D_row"]))
    direct_K = (direct[2] - direct[3].conj().T) / 2
    with np.load(args.predictions, allow_pickle=False) as p:
        predictions = {name: tuple(p[f"{name}_{key}"] for key in ("O", "dotO", "Dcol", "Drow", "K")) for name in ("R31AI", "R31Z")}

    def errors(pred):
        O, dotO, Dcol, Drow, K = pred
        result = {"E_O": n2(O - direct[0]), "E_dotO_per_ta": n2(dotO - direct[1]),
                  "E_Dcol_per_ta": n2(Dcol - direct[2]), "E_Drow_per_ta": n2(Drow - direct[3]),
                  "E_K_per_ta": n2(K - direct_K),
                  "candidate_metric_identity_residual_2norm": n2(dotO - Dcol - Drow.conj().T)}
        result["E_Dmax_per_ta"] = max(result["E_Dcol_per_ta"], result["E_Drow_per_ta"])
        return result

    local, global_error = errors(predictions["R31AI"]), errors(predictions["R31Z"])
    primary = ("E_K_per_ta", "E_Dmax_per_ta")
    tol = 1e-10
    local_support = all(local[k] <= global_error[k] + tol for k in primary) and any(global_error[k] - local[k] > tol for k in primary)
    global_support = all(global_error[k] <= local[k] + tol for k in primary) and any(local[k] - global_error[k] > tol for k in primary)
    if local_support and global_support:
        raise ValueError("inconsistent Pareto rule")
    verdict = "PARETO_SUPPORTED_AT_Z25" if local_support else "GLOBAL_SUPPORTED_AT_Z25" if global_support else "TRADEOFF_UNRESOLVED"
    gap = jvp["O"] - od["O"]
    residual = jvp["dotO"] - od["D_col"] - od["D_row"].conj().T
    result = {"schema": "WU088_R31AI_Z25_ONE_SHOT_FROZEN_COMPARISON_V1", "z_a0": 2.5,
              "time_ta_computed": lock["time_ta_computed"], "radial_order": 192,
              "direct_outputs": {"OD": {"path": str(args.od), "sha256": sha(args.od), "bytes": args.od.stat().st_size},
                                 "JVP": {"path": str(args.jvp), "sha256": sha(args.jvp), "bytes": args.jvp.stat().st_size}},
              "comparison_dtype": "complex128; original extended-precision raw preserved",
              "direct_source_O_gap_raw_max_abs": float(np.max(np.abs(gap))),
              "direct_source_O_gap_2norm_complex128": n2(gap),
              "direct_metric_identity_raw_max_abs": float(np.max(np.abs(residual))),
              "direct_metric_identity_2norm_complex128": n2(residual),
              "source_bridge_pass_existing_2e_minus_12_tolerance": max(float(np.max(np.abs(gap))), float(np.max(np.abs(residual)))) <= 2e-12,
              "R31AI_adaptive_seven_node": local, "R31Z_global": global_error,
              "primary_comparison_tolerance": tol, "frozen_decision_rule_verdict": verdict,
              "observed_margins_global_minus_R31AI": {"delta_K_per_ta": global_error["E_K_per_ta"] - local["E_K_per_ta"],
                                                     "delta_Dmax_per_ta": global_error["E_Dmax_per_ta"] - local["E_Dmax_per_ta"]},
              "reference_error_upper_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE",
              "conditional_true_margin_intervals": None,
              "design_score_used_for_final_verdict": False,
              "independent_single_point_central_cell_relative_validation": True,
              "end_cell_refinement_gain_directly_validated": False,
              "interval_wide_accuracy_admitted": False, "transition_error_admitted": False,
              "full_cell_admitted": False, "fixed_Q_physical_invariance_admitted": False,
              "H_skip_admitted": False, "production_admitted": False}
    if any(sha(path) != LOCKS[key][1] for key, path in paths.items()):
        raise ValueError("post-output locked source/input drift")
    if args.out.exists():
        raise FileExistsError(args.out)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("prelock", "compare"))
    for name in ("repo", "snapshot", "archive", "predictions", "lock", "od", "jvp", "out"):
        ap.add_argument("--" + name, type=Path)
    args = ap.parse_args()
    repo = args.repo.resolve()
    paths = check_locks(repo, args.snapshot, args.archive)
    if args.mode == "prelock":
        prelock(args, paths)
    else:
        compare(args, paths)


if __name__ == "__main__":
    main()
