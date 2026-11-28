"""Frozen secondary z=0.75 comparison; requires completed parent primary result."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.linalg import norm


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def n2(a):
    return float(norm(np.asarray(a, dtype=np.complex128), 2))


def errors(prediction, truth):
    O, dotO, Dc, Dr, K = prediction
    direct_O, direct_dotO, direct_Dc, direct_Dr, direct_K = truth
    out = {"E_O": n2(O-direct_O), "E_dotO_per_ta": n2(dotO-direct_dotO),
           "E_Dcol_per_ta": n2(Dc-direct_Dc), "E_Drow_per_ta": n2(Dr-direct_Dr),
           "E_K_per_ta": n2(K-direct_K),
           "candidate_metric_identity_residual_2norm": n2(dotO-Dc-Dr.conj().T)}
    out["E_Dmax_per_ta"] = max(out["E_Dcol_per_ta"], out["E_Drow_per_ta"])
    return out


def main():
    ap = argparse.ArgumentParser()
    for key in ("repo", "od", "jvp", "primary_result", "out"):
        ap.add_argument("--" + key.replace("_", "-"), required=True, type=Path)
    a = ap.parse_args()
    repo = a.repo.resolve()
    base = repo / "research/r31al_z075_gate/ncp_followup_20260930"
    prereg = json.loads((base / "SECONDARY_REFINEMENT_PREREGISTRATION.json").read_text())
    if sha(Path(__file__)) != prereg["secondary_comparator_sha256"]:
        raise ValueError("secondary comparator drift")
    for key, relative in prereg["locked_files"].items():
        if sha(repo / relative["path"]) != relative["sha256"]:
            raise ValueError("pre-output lock drift: " + key)
    primary = json.loads(a.primary_result.read_text())
    if primary.get("verdict") not in ("PARETO_SUPPORTED_AT_SELECTED_HOLDOUT", "GLOBAL_SUPPORTED_AT_SELECTED_HOLDOUT", "TRADEOFF_UNRESOLVED"):
        raise ValueError("parent primary result required before secondary")
    if primary.get("OD_sha256") != sha(a.od) or primary.get("JVP_sha256") != sha(a.jvp):
        raise ValueError("primary and secondary direct source mismatch")
    adapter = module(repo / "research/r31ak_eight_node/metadata_adapter.py", "r31al_frozen_adapter")
    if not adapter.identities_match(a.od.with_name("IDENTITY.json").read_bytes(), a.jvp.with_name("IDENTITY.json").read_bytes(), "0.75"):
        raise ValueError("direct geometry identity drift")
    for path in (a.od, a.jvp):
        identity = json.loads(path.with_name("IDENTITY.json").read_text())
        if identity.get("n") != 192 or json.loads(path.with_name("RESULTS.json").read_text()).get("sha256") != sha(path):
            raise ValueError("direct order or byte identity drift")
    with np.load(a.od, allow_pickle=False) as f:
        od = {k: f[k] for k in f.files}
    with np.load(a.jvp, allow_pickle=False) as f:
        jvp = {k: f[k] for k in f.files}
    if tuple(x.shape for x in (od["O"], od["D_col"], od["D_row"], jvp["O"], jvp["dotO"])) != ((47,2),(47,2),(2,47),(47,2),(47,2)):
        raise ValueError("direct output scope drift")
    truth = tuple(np.asarray(x, dtype=np.complex128) for x in (od["O"], jvp["dotO"], od["D_col"], od["D_row"]))
    truth += ((truth[2]-truth[3].conj().T)/2,)
    with np.load(repo / prereg["locked_files"]["R31AK_prediction_npz"]["path"], allow_pickle=False) as f:
        refined = tuple(f["z0p75_R31AK_"+k] for k in ("O", "dotO", "Dcol", "Drow", "K"))
    with np.load(repo / prereg["locked_files"]["R31AD_coarse_npz"]["path"], allow_pickle=False) as f:
        coarse = tuple(f["z0p75_R31AD_"+k] for k in ("O", "dotO", "Dcol", "Drow", "K"))
    refined_errors, coarse_errors = errors(refined, truth), errors(coarse, truth)
    helper = module(repo / "research/r31al_z075_gate/refinement_gain.py", "r31al_frozen_refinement_gain")
    verdict = helper.pareto_verdict((refined_errors["E_K_per_ta"], refined_errors["E_Dmax_per_ta"]),
                                    (coarse_errors["E_K_per_ta"], coarse_errors["E_Dmax_per_ta"]), 1e-10)
    keys = ("E_O", "E_dotO_per_ta", "E_K_per_ta", "E_Dcol_per_ta", "E_Drow_per_ta", "E_Dmax_per_ta")
    gains = {key: (coarse_errors[key]-refined_errors[key])/coarse_errors[key] if coarse_errors[key] else None for key in keys}
    result = {"schema": "WU088_R31AL_Z075_SECONDARY_REFINEMENT_COMPARISON_V1", "z_a0": "0.75",
              "parent_primary_verdict_unchanged": primary["verdict"], "secondary_verdict": verdict,
              "OD_sha256": sha(a.od), "JVP_sha256": sha(a.jvp), "refined_R31AK_errors": refined_errors,
              "coarse_R31AD_errors": coarse_errors, "improvement_fractions_refined_vs_coarse": gains,
              "direct_metric_identity_residual_2norm": n2(truth[1]-truth[2]-truth[3].conj().T),
              "direct_OD_JVP_O_gap_2norm": n2(jvp["O"]-od["O"]),
              "comparison_tolerance_per_ta": 1e-10, "weighted_score_used": False,
              "source_accuracy_bound_status": "SOURCE_ACCURACY_BOUND_UNAVAILABLE"}
    if a.out.exists():
        raise FileExistsError(a.out)
    a.out.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
