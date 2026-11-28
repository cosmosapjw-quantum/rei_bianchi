"""Future direct mixed-node adapter; frozen before selected output access.

This module does not run a producer. It checks source identity and compares
the precomputed R31AK/R31Z predictions with a separately authorized node.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.linalg import norm


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def n2(value) -> float:
    return float(norm(np.asarray(value, dtype=np.complex128), 2))


def main() -> None:
    ap = argparse.ArgumentParser()
    for key in ("repo", "od", "jvp", "out"):
        ap.add_argument("--" + key, required=True, type=Path)
    a = ap.parse_args()
    repo = a.repo.resolve()
    base = repo / "research/r31ak_eight_node/ncp_followup_20260930"
    prereg = json.loads((base / "NEXT_VALIDATION_PREREGISTRATION.json").read_text())
    adapter_path = repo / "research/r31ak_eight_node/metadata_adapter.py"
    rule_path = base / "FROZEN_HOLDOUT_DECISION_RULE.json"
    predictions_path = base / "FROZEN_HOLDOUT_PREDICTIONS.npz"
    if sha(Path(__file__)) != prereg["comparator_sha256"]:
        raise ValueError("comparator drift")
    for path, key in ((adapter_path, "metadata_adapter_sha256"),
                      (rule_path, "decision_rule_sha256"),
                      (predictions_path, "frozen_predictions_sha256"),
                      (repo / "research/r31ad_five_node/unit_cell_model.py", "R31AK_engine_sha256"),
                      (repo / "research/r31z_source_bound/source_bound.py", "R31Z_model_sha256"),
                      (base / "EIGHT_NODE_INPUT_MANIFEST.json", "eight_node_manifest_sha256")):
        if sha(path) != prereg[key]:
            raise ValueError("pre-output source/model drift: " + key)
    rule = json.loads(rule_path.read_text())
    if rule["comparison_tolerance_per_ta"] != 1e-10 or rule["primary_metrics"] != ["E_K", "E_Dmax"]:
        raise ValueError("decision rule drift")
    adapter = load_module(adapter_path, "r31ak_frozen_metadata_adapter")
    if not adapter.identities_match(a.od.with_name("IDENTITY.json").read_bytes(),
                                    a.jvp.with_name("IDENTITY.json").read_bytes(),
                                    prereg["selected_z_decimal"]):
        raise ValueError("direct geometry identity drift")
    od_identity = json.loads(a.od.with_name("IDENTITY.json").read_text())
    jvp_identity = json.loads(a.jvp.with_name("IDENTITY.json").read_text())
    if od_identity.get("n") != 192 or jvp_identity.get("n") != 192:
        raise ValueError("direct radial order drift")
    with np.load(a.od, allow_pickle=False) as src:
        od = {key: src[key] for key in src.files}
    with np.load(a.jvp, allow_pickle=False) as src:
        jvp = {key: src[key] for key in src.files}
    if tuple(x.shape for x in (od["O"], od["D_col"], od["D_row"], jvp["dotO"], jvp["O"])) != ((47, 2), (47, 2), (2, 47), (47, 2), (47, 2)):
        raise ValueError("direct array shape drift")
    for arr, key in ((a.od, "OD"), (a.jvp, "JVP")):
        report = json.loads(arr.with_name("RESULTS.json").read_text())
        if report["sha256"] != sha(arr):
            raise ValueError(key + " direct byte identity drift")
        if key == "OD" and (report.get("Hamiltonian_included") is not False or report.get("independent_dotO_included") is not False):
            raise ValueError("OD output scope drift")
    zkey = prereg["prediction_key"]
    with np.load(predictions_path, allow_pickle=False) as source:
        predictions = {name: tuple(source[f"{zkey}_{name}_{field}"] for field in ("O", "dotO", "Dcol", "Drow", "K"))
                       for name in ("R31AK", "R31Z")}
    direct = (np.asarray(od["O"], dtype=np.complex128), np.asarray(jvp["dotO"], dtype=np.complex128),
              np.asarray(od["D_col"], dtype=np.complex128), np.asarray(od["D_row"], dtype=np.complex128))
    direct_K = (direct[2] - direct[3].conj().T) / 2
    source_O_gap = n2(jvp["O"] - od["O"])
    direct_metric_residual = n2(jvp["dotO"] - od["D_col"] - od["D_row"].conj().T)

    def errors(pred):
        O, dotO, Dcol, Drow, K = pred
        e = {"E_O": n2(O - direct[0]), "E_dotO_per_ta": n2(dotO - direct[1]),
             "E_Dcol_per_ta": n2(Dcol - direct[2]), "E_Drow_per_ta": n2(Drow - direct[3]),
             "E_K_per_ta": n2(K - direct_K),
             "candidate_metric_identity_residual_2norm": n2(dotO - Dcol - Drow.conj().T)}
        e["E_Dmax_per_ta"] = max(e["E_Dcol_per_ta"], e["E_Drow_per_ta"])
        return e

    local, global_error = errors(predictions["R31AK"]), errors(predictions["R31Z"])
    primary = ("E_K_per_ta", "E_Dmax_per_ta")
    tol = 1e-10
    local_support = all(local[k] <= global_error[k] + tol for k in primary) and any(global_error[k] - local[k] > tol for k in primary)
    global_support = all(global_error[k] <= local[k] + tol for k in primary) and any(local[k] - global_error[k] > tol for k in primary)
    if local_support and global_support:
        raise ValueError("inconsistent Pareto rule")
    verdict = "PARETO_SUPPORTED_AT_SELECTED_HOLDOUT" if local_support else "GLOBAL_SUPPORTED_AT_SELECTED_HOLDOUT" if global_support else "TRADEOFF_UNRESOLVED"
    result = {"schema": "WU088_R31AK_FUTURE_HOLDOUT_COMPARISON_V1", "selected_z_a0": prereg["selected_z_a0"],
              "OD_sha256": sha(a.od), "JVP_sha256": sha(a.jvp),
              "R31AK_errors": local, "R31Z_errors": global_error,
              "direct_source_O_gap_2norm": source_O_gap,
              "direct_metric_identity_residual_2norm": direct_metric_residual,
              "source_bridge_pass_existing_2e_minus_12_tolerance": max(source_O_gap, direct_metric_residual) <= 2e-12,
              "comparison_tolerance_per_ta": tol, "verdict": verdict,
              "reference_error_upper_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE",
              "design_score_used_for_verdict": False}
    if a.out.exists():
        raise FileExistsError(a.out)
    a.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
