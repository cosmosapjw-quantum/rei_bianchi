"""R31AL read-only source replay and pre-output lock construction."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from scipy.linalg import norm


EXPECTED = {
    "NEXT_VALIDATION_PREREGISTRATION.json": "44b2273afeddb4a6befa73ce485ae84d8f8777a92ac75c4de2fd90d0fea74b81",
    "FROZEN_HOLDOUT_DECISION_RULE.json": "08ad89d35c31e133bce39da1f5c8b59eb782b647fb1e4e26da522e010ed6d995",
    "FROZEN_HOLDOUT_PREDICTIONS.npz": "6d29acbe1aee9bb34cf3627c04136d67e27b5a44b44ee7b3104cdcd3fe1ff88c",
    "HOLDOUT_SELECTION.json": "f01460fe12920280f09281d0763c896986574061806eb0568839b50fcccd096e",
    "EIGHT_NODE_INPUT_MANIFEST.json": "d978792bef0c3bf2b670d4e73d70dcea391645f38555f1070323037610162ece",
}
SOURCES = {
    "snapshot": ("/root/WU088_R31W_INPUT_20260929/overlay/research/r31w_metric_cell/inputs/EXISTING_METRIC_INPUTS.npz", "565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079"),
    "z05_od": ("research/r31ae_z05_gate/authorized_z05_20260929/OD_RAW/ASSEMBLED_OD.npz", "1505463b2329e9398b92077d51a9704c4b5f2c5d71288cf811571763a672f80a"),
    "z05_jvp": ("research/r31ae_z05_gate/authorized_z05_20260929/JVP_RAW/ASSEMBLED.npz", "88b44ec142eef45ef7232f7fd050a0c5ca1773db416986a9a5857d60959b5fc3"),
    "z1_od": ("research/r31ac_z1_authorization/authorized_z1_20260929/OD_RAW/ASSEMBLED_OD.npz", "020dc2c2c580f7e7f8a2d5d322b771b4957fbcc1166ab4e2c363f5a9c3d06818"),
    "z1_jvp": ("research/r31ac_z1_authorization/authorized_z1_20260929/JVP_RAW/ASSEMBLED.npz", "b6a9926052999c70cc6092c0d47001eff0716d2aefb6ff380edfa18558696819"),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def load_npz(path):
    with np.load(path, allow_pickle=False) as f:
        return {k: f[k] for k in f.files}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def n2(a):
    return float(norm(np.asarray(a, dtype=np.complex128), 2))


def array_sha(arrays):
    digest = hashlib.sha256()
    for a in arrays:
        digest.update(np.asarray(a, dtype="<c16", order="C").tobytes(order="C"))
    return digest.hexdigest()


def main():
    repo = Path(__file__).resolve().parents[2]
    out = repo / "research/r31al_z075_gate/ncp_followup_20260930"
    out.mkdir(exist_ok=True)
    parent = repo / "research/r31ak_eight_node/ncp_followup_20260930"
    verified = {}
    for filename, expected in EXPECTED.items():
        path = parent / filename
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"parent lock drift: {filename}: {actual}")
        verified[filename] = {"path": str(path.relative_to(repo)), "sha256": actual}
    other = {
        "R31AK_engine": (repo / "research/r31ad_five_node/unit_cell_model.py", "ab220248066580fc77af70c412251dbe3ed643a6fadc266cf5c25a7a3a6651a0"),
        "R31Z_model": (repo / "research/r31z_source_bound/source_bound.py", "4ba03ba2adbdc9533f6472558b33a7edf86959bfc397e5fc8e3e90f8765ba034"),
        "metadata_adapter": (repo / "research/r31ak_eight_node/metadata_adapter.py", "41a8a67d0b3de90aa22ea4c1f011cbeb0cb48c417dd47b5d958ac26f52f63619"),
        "parent_comparator": (repo / "research/r31ak_eight_node/compare_future_holdout.py", "5443b1ef98b1b70044b8a2e5e8bb065a1d927824066c6a142be3935bfc695394"),
    }
    for name, (path, expected) in other.items():
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"parent source drift: {name}: {actual}")
        verified[name] = {"path": str(path.relative_to(repo)), "sha256": actual}
    prereg = json.loads((parent / "NEXT_VALIDATION_PREREGISTRATION.json").read_text())
    if (prereg["selected_z_decimal"] != "0.75" or prereg["selected_time_ta"] != 1.6769079292753586
            or prereg["radial_order"] != 192 or prereg["primary_metrics"] != ["E_K", "E_Dmax"]
            or prereg["comparison_tolerance_per_ta"] != 1e-10 or prereg["execution_authorized"]
            or prereg["direct_output_accessed"]):
        raise ValueError("parent primary semantics drift")
    with np.load(parent / "FROZEN_HOLDOUT_PREDICTIONS.npz", allow_pickle=False) as f:
        refined = tuple(f[f"z0p75_R31AK_{k}"] for k in ("O", "dotO", "Dcol", "Drow", "K"))
        global_model = tuple(f[f"z0p75_R31Z_{k}"] for k in ("O", "dotO", "Dcol", "Drow", "K"))
    for name, arrays, expected in (("R31AK", refined, prereg["selected_R31AK_prediction_arrays_sha256"]),
                                    ("R31Z", global_model, prereg["selected_R31Z_prediction_arrays_sha256"])):
        if array_sha(arrays) != expected:
            raise ValueError(name + " selected prediction drift")
        verified[name + "_selected_prediction"] = {"sha256": expected}
    verified["R31AK_model_aggregate_sha256"] = prereg["R31AK_model_aggregate_sha256"]
    if prereg["R31AK_model_aggregate_sha256"] != "50a5f0eeda63d6e04795e301f6b07a41fd11a4b145e267cfc608261356d49b30":
        raise ValueError("R31AK aggregate drift")
    write(out / "PRIMARY_LOCK_VERIFICATION.json", {"schema": "WU088_R31AL_PARENT_PRIMARY_LOCK_V1", "parent_unchanged": True, "verified": verified,
                                                   "selected_z_a0": "0.75", "selected_time_ta": "1.6769079292753586", "radial_order": 192,
                                                   "primary_models": ["R31AK_ADAPTIVE_EIGHT_NODE_CUBIC_O_LINEAR_K", "R31Z_GLOBAL_QUINTIC_O_QUADRATIC_K"],
                                                   "primary_metrics": ["E_K", "E_Dmax"], "tolerance_per_ta": "1e-10", "direct_output_accessed": False})
    source_paths = {}
    for key, (raw_path, expected) in SOURCES.items():
        path = Path(raw_path) if raw_path.startswith("/") else repo / raw_path
        actual = sha(path)
        if actual != expected:
            raise ValueError("existing source drift: " + key)
        source_paths[key] = path
    fit = load_npz(source_paths["snapshot"])
    od05, j05 = load_npz(source_paths["z05_od"]), load_npz(source_paths["z05_jvp"])
    od1, j1 = load_npz(source_paths["z1_od"]), load_npz(source_paths["z1_jvp"])
    nodes = [(fit["z0_od_O"], fit["z0_od_D_col"], fit["z0_od_D_row"], fit["z0_j_dotO"]),
             (od1["O"], od1["D_col"], od1["D_row"], j1["dotO"])]
    for O, Dc, Dr, dot in nodes:
        if (O.shape, Dc.shape, Dr.shape, dot.shape) != ((47, 2), (47, 2), (2, 47), (47, 2)):
            raise ValueError("coarse source shape drift")
    velocity = float(fit["velocity"])
    H = 1.0 / velocity
    target_t = 0.75 / velocity
    if abs(H - 2.2358772390338113) > 1e-14 or abs(target_t - 1.6769079292753586) > 1e-14:
        raise ValueError("producer time drift")
    engine = load_module(other["R31AK_engine"][0], "r31ad_engine_r31al")
    values = [np.asarray(x[0], dtype=np.complex128) for x in nodes]
    dots = [np.asarray(x[3], dtype=np.complex128) for x in nodes]
    ks = [(np.asarray(x[1], dtype=np.complex128) - np.asarray(x[2], dtype=np.complex128).conj().T) / 2 for x in nodes]
    coarse = engine.piecewise_candidate([0.0, H], values, dots, ks, target_t)[:5]
    coarse_mid = engine.piecewise_candidate([0.0, H], values, dots, ks, H / 2)[:5]
    direct_mid = (np.asarray(od05["O"], dtype=np.complex128), np.asarray(j05["dotO"], dtype=np.complex128),
                  np.asarray(od05["D_col"], dtype=np.complex128), np.asarray(od05["D_row"], dtype=np.complex128))
    dK_mid = (direct_mid[2] - direct_mid[3].conj().T) / 2
    helper = load_module(repo / "research/r31al_z075_gate/refinement_gain.py", "r31al_gain")
    correction = helper.propagated_midpoint_correction(direct_mid[0] - coarse_mid[0], direct_mid[1] - coarse_mid[1], dK_mid - coarse_mid[4], H)
    # Helper's row contribution is Drow dagger; transpose for comparison.
    expected_differences = (correction[0], correction[1], correction[2], correction[3].conj().T, correction[4])
    gaps = {k: n2(r - c - e) for k, r, c, e in zip(("O", "dotO", "Dcol", "Drow", "K"), refined, coarse, expected_differences)}
    predicted_k = n2(correction[4])
    eo, ed, ek = n2(direct_mid[0] - coarse_mid[0]), n2(direct_mid[1] - coarse_mid[1]), n2(dK_mid - coarse_mid[4])
    bounds = helper.norm_bounds_from_z05_errors(eo, ed, ek, H)
    if max(gaps.values()) > 2e-12 or abs(predicted_k - 0.07515459630271762) > 1e-12:
        raise ValueError("REFINE_PROPAGATION_CONTRACT_MISMATCH")
    if not (0.03508653720881643 - 1e-12 <= n2(correction[0]) <= 0.05244308388179227 + 1e-12
            and 0.1019178360724072 - 1e-12 <= n2(correction[1]) <= 0.1329688193195485 + 1e-12):
        raise ValueError("REFINE_PROPAGATION_CONTRACT_MISMATCH: historical bounds")
    arrays = {"z0p75_R31AD_" + k: np.asarray(a, dtype=np.complex128) for k, a in zip(("O", "dotO", "Dcol", "Drow", "K"), coarse)}
    np.savez(out / "Z075_COARSE_PREDICTION.npz", **arrays)
    coarse_array_hash = array_sha(coarse)
    write(out / "Z075_COARSE_PREDICTION.json", {"schema": "WU088_R31AL_Z075_COARSE_PREDICTION_V1", "model": "R31AD_FIVE_NODE_UNIT_CELL_CUBIC_O_LINEAR_K",
        "cell_z_a0": ["0", "1"], "target_z_a0": "0.75", "target_time_ta": "1.6769079292753586", "engine_sha256": verified["R31AK_engine"]["sha256"],
        "R31AD_policy_git_blob": "aba52d2c8ffdf97079999cc5f54bd20154bdf4a2", "sources": {k: {"path": str(v), "sha256": SOURCES[k][1], "bytes": v.stat().st_size} for k, v in source_paths.items() if k in ("snapshot", "z1_od", "z1_jvp")},
        "array_artifact": "Z075_COARSE_PREDICTION.npz", "array_artifact_sha256": sha(out / "Z075_COARSE_PREDICTION.npz"), "selected_arrays_sha256": coarse_array_hash,
        "array_hash_order": ["O", "dotO", "Dcol", "Drow", "K"], "comparison_dtype": "complex128", "direct_z075_output_accessed": False})
    write(out / "REFINEMENT_PROPAGATION_CHECK.json", {"schema": "WU088_R31AL_REFINEMENT_PROPAGATION_CHECK_V1", "status": "PASS",
        "formula_source": "research/r31al_z075_gate/refinement_gain.py:17-27", "z05_direct_minus_coarse_norms": {"O": eo, "dotO_per_ta": ed, "K_per_ta": ek},
        "H_ta": H, "predicted_correction_K_2norm_per_ta": predicted_k,
        "actual_model_difference_norms": {"O": n2(refined[0] - coarse[0]), "dotO_per_ta": n2(refined[1] - coarse[1]), "K_per_ta": n2(refined[4] - coarse[4])},
        "identity_2norm_gaps": gaps, "historical_norm_only_bounds": bounds,
        "historical_required_bounds": {"O": [0.03508653720881643, 0.05244308388179227], "dotO_per_ta": [0.1019178360724072, 0.1329688193195485]},
        "direct_z075_output_accessed": False})
    print(json.dumps({"parent_lock": "PASS", "coarse_npz_sha256": sha(out / "Z075_COARSE_PREDICTION.npz"), "coarse_arrays_sha256": coarse_array_hash,
                      "refinement_identity_max_gap": max(gaps.values()), "delta_K_norm": predicted_k, "direct_z075_output_accessed": False}, indent=2))


if __name__ == "__main__":
    main()
