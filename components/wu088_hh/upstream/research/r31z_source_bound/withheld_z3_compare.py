"""Read-only, hash-locked comparison of the fixed R31Z fit with archived z=3."""
import argparse
import hashlib
import io
import json
import zipfile

import numpy as np
from scipy.linalg import norm

from source_bound import EXPECTED, quadratic_three_nodes, quintic_hermite

ARCHIVE_SHA = "c10c932a6cdad817982e00920a893733b367827b116d058791bf5aacad517cd9"
OD = ("completion/mixed_h/od/B192_z3/ASSEMBLED_OD.npz",
      "47f41c15aba4fc3eb4e9a6b6f08202067cf525503a87431035ee692990b553af")
JVP = ("completion/mixed_derivative/B192_z3/ASSEMBLED.npz",
       "9223dfea7956a58a70595ab25dda457be64b966ce247830e5c12a73d87515661")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def spectral(x):
    return float(norm(x, 2))


def run(snapshot, archive):
    raw = snapshot.read_bytes()
    if sha(raw) != EXPECTED:
        raise ValueError("snapshot SHA mismatch")
    if sha(archive.read_bytes()) != ARCHIVE_SHA:
        raise ValueError("archive SHA mismatch")
    with np.load(io.BytesIO(raw), allow_pickle=False) as f:
        d = {key: f[key] for key in f.files}
    with zipfile.ZipFile(archive) as z:
        arrays = []
        for member, expected in (OD, JVP):
            content = z.read(member)
            if sha(content) != expected:
                raise ValueError(f"member SHA mismatch: {member}")
            with np.load(io.BytesIO(content), allow_pickle=False) as f:
                arrays.append({key: f[key] for key in f.files})
    od, jvp = arrays
    if int(od["n"]) != 192 or float(od["z"]) != 3 or float(jvp["z"]) != 3:
        raise ValueError("withheld node identity mismatch")
    if any(od[key].shape != (47, 2) for key in ("O", "D_col")) or od["D_row"].shape != (2, 47):
        raise ValueError("withheld OD shape mismatch")
    if jvp["O"].shape != (47, 2) or jvp["dotO"].shape != (47, 2):
        raise ValueError("withheld JVP shape mismatch")
    cast = lambda x: np.asarray(x, dtype=np.complex128)
    O = [cast(d["z0_od_O"]), cast(d["direct_O"][:47, 47:]), cast(d["z4_od_O"])]
    dot = [cast(d["z0_j_dotO"]), cast(d["direct_dotO"][:47, 47:]), cast(d["z4_j_dotO"])]
    dc = [cast(d["z0_od_D_col"]), cast(d["direct_D"][:47, 47:]), cast(d["z4_od_D_col"])]
    dr = [cast(d["z0_od_D_row"]), cast(d["direct_D"][47:, :47]), cast(d["z4_od_D_row"])]
    K = [(c-r.conj().T)/2 for c, r in zip(dc, dr)]
    T = 4/float(d["velocity"])
    pred_o, pred_dot = quintic_hermite(O, dot, T, 0.75)
    pred_k = quadratic_three_nodes(K, 0.75)
    pred_dc = pred_dot/2+pred_k
    pred_dr = (pred_dot/2-pred_k).conj().T
    actual_o, actual_dot = cast(od["O"]), cast(jvp["dotO"])
    actual_dc, actual_dr = cast(od["D_col"]), cast(od["D_row"])
    return {
        "schema": "WU088_R31Z_WITHHELD_Z3_COMPARISON_V1",
        "fit_nodes_z": [0, 2, 4], "withheld_z": 3, "withheld_time_ta": 3/float(d["velocity"]),
        "fit_input_sha256": EXPECTED, "archive_sha256": ARCHIVE_SHA,
        "od_member": OD[0], "od_member_sha256": OD[1],
        "jvp_member": JVP[0], "jvp_member_sha256": JVP[1],
        "comparison_dtype": "complex128, matching R31Z replay",
        "source_O_OD_minus_JVP_2norm": spectral(actual_o-cast(jvp["O"])),
        "source_metric_identity_2norm": spectral(actual_dot-actual_dc-actual_dr.conj().T),
        "candidate_O_error_2norm": spectral(pred_o-actual_o),
        "candidate_dotO_error_2norm_per_ta": spectral(pred_dot-actual_dot),
        "candidate_D_col_error_2norm_per_ta": spectral(pred_dc-actual_dc),
        "candidate_D_row_error_2norm_per_ta": spectral(pred_dr-actual_dr),
        "candidate_metric_identity_2norm": spectral(pred_dot-pred_dc-pred_dr.conj().T),
        "withheld_node_used_in_fit": False,
        "comparison_only": True,
        "interval_predictive_validation_admitted": False,
        "new_scientific_nodes": 0,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=__import__("pathlib").Path, required=True)
    p.add_argument("--archive", type=__import__("pathlib").Path, required=True)
    p.add_argument("--out", type=__import__("pathlib").Path, required=True)
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    result = run(a.snapshot, a.archive)
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    a.out.write_text(payload)
    print(payload, end="")
