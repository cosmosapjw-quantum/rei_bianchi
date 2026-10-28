"""Project one already-saved conditional nuclear n/T history without solving it."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "inputs"
OUTPUTS = ROOT / "outputs"
CASE = "quotient_L16_S-0.6_Am0_Ar0"
PINNED = {
    "NUCLEAR_NETWORK_HISTORIES.npz": (8157876, "087aa44cbd035e95fa593ac4099c108a5c5f6a60d0de8f59ce8a81d8d664b405"),
    "NUCLEAR_NETWORK_LOG_RATE_TABLE.npz": (39180, "9b557ccf7f16b2fc20a1af618a486e2795252f2017df28c99f74aec1a00eb88b"),
    "TRACER_HISTORIES.npz": (1137358, "f0147f864970faa805252c8d329159b466ef853f733028b938eed1ce1ab163a8"),
}
SPECIES = ("n", "H1", "D", "T", "He3", "He4", "Li6", "Li7")
FAMILIES = (
    "he3_n_gamma", "p_t_gamma", "d_d_gamma", "p_d_gamma", "p_n_gamma",
    "t_beta", "n_beta", "t_alpha_gamma", "d_d_p", "d_d_n", "d_t_n",
    "d_he3_p", "n_he3_p", "d_alpha_gamma", "p_li6_alpha", "n_li6_alpha",
    "p_li7_alpha", "d_n_gamma",
)
LN10 = math.log(10.0)


def verify_inputs(inputs: Path) -> None:
    for name, (size, digest) in PINNED.items():
        path = inputs / name
        if path.stat().st_size != size:
            raise ValueError(f"source size mismatch: {name}")
        with path.open("rb") as stream:
            observed = hashlib.file_digest(stream, "sha256").hexdigest()
        if observed != digest:
            raise ValueError(f"source SHA256 mismatch: {name}")


def encoded_log(value: float) -> float | str:
    value = float(value)
    if math.isnan(value) or value == math.inf:
        raise ValueError("saved log contains NaN or +Infinity")
    return "-Infinity" if value == -math.inf else value


def log10_view(value: float | str) -> float | None:
    return None if value == "-Infinity" else float(value) / LN10


def _sample_check(sample_path: Path, selected: dict, case_index: int) -> list[dict]:
    sample = json.loads(sample_path.read_text(encoding="utf-8"))
    if sample["case_name"] != CASE or sample["case_index"] != case_index:
        raise ValueError("C2 saved sample case mismatch")
    checks = []
    for row in sample["epochs"]:
        i = row["epoch_index"]
        if i not in (0, 128, 256):
            raise ValueError("unexpected C2 sample epoch")
        comparisons = {"elapsed_s": (row["elapsed_s"], selected["elapsed_s"][i])}
        for j, name in enumerate(("T", "n")):
            comparisons[f"ln_Y_{name}"] = (row["log_T_n"]["values"][j], selected[f"ln_Y_{name}"][i])
        for field, (expected, observed) in comparisons.items():
            if expected == "-Infinity":
                if observed != expected:
                    raise ValueError(f"C2 {field} mismatch at epoch {i}")
                difference, reason = 0.0, "exact tagged negative infinity"
            else:
                difference = abs(float(expected) - float(observed))
                if difference > 1e-12:
                    raise ValueError(f"C2 {field} mismatch at epoch {i}: {difference}")
                reason = "exact serialized float" if difference == 0 else "decimal serialization roundoff <=1e-12"
            checks.append({"epoch": i, "field": field, "absolute_difference": difference, "reason": reason})
    if sorted(set(x["epoch"] for x in checks)) != [0, 128, 256]:
        raise ValueError("C2 sample coverage mismatch")
    return checks


def _assert_monotone_cumulative(values: np.ndarray, label: str) -> None:
    if np.isnan(values).any() or np.isposinf(values).any():
        raise ValueError(f"invalid cumulative log values: {label}")
    if np.any(values[1:] < values[:-1] - 1e-12):
        raise ValueError(f"decreasing saved cumulative log events: {label}")


def extract(inputs: Path = INPUTS) -> dict:
    verify_inputs(inputs)
    with np.load(inputs / "NUCLEAR_NETWORK_HISTORIES.npz", allow_pickle=False) as saved:
        expected_shapes = {
            "case_names": (82,), "family_ids": (18,), "species": (8,), "x": (257,),
            "T_K": (257,), "elapsed_s": (82, 257), "nB_m3": (82, 257),
            "log_T_n": (82, 257, 2), "log_fast_source": (82, 257, 2),
            "log_forward_reverse_flux": (82, 257, 18, 2),
            "log_forward_reverse_cumulative": (82, 257, 18, 2),
        }
        if set(saved.files) != set(expected_shapes):
            raise ValueError("nuclear history key registry mismatch")
        for key, shape in expected_shapes.items():
            if saved[key].shape != shape:
                raise ValueError(f"nuclear history shape mismatch: {key}")
        names = saved["case_names"].tolist()
        families = saved["family_ids"].tolist()
        if names.count(CASE) != 1 or names.index(CASE) != 0:
            raise ValueError("selected case missing, duplicate, or unexpected index")
        if tuple(saved["species"].tolist()) != SPECIES or tuple(families) != FAMILIES:
            raise ValueError("source species/family registry mismatch")
        t = saved["elapsed_s"][0]
        if not np.isfinite(t).all() or t[0] != 0 or not np.all(np.diff(t) > 0):
            raise ValueError("saved proper elapsed seconds are not finite and strictly increasing")
        stock = saved["log_T_n"][0]
        cumulative = saved["log_forward_reverse_cumulative"][0]
        flux = saved["log_forward_reverse_flux"][0]
        source = saved["log_fast_source"][0]
        for label, arr in (("stock", stock), ("cumulative", cumulative), ("flux", flux), ("source", source)):
            if np.isnan(arr).any() or np.isposinf(arr).any():
                raise ValueError(f"saved {label} has NaN or +Infinity")
        f = {name: families.index(name) for name in ("n_beta", "t_beta", "d_d_n", "d_d_p")}
        for name in ("n_beta", "t_beta"):
            _assert_monotone_cumulative(cumulative[:, f[name], 0], name)
        # All these selections are direct source columns; the forward direction is index 0.
        columns = {
            "elapsed_s": t, "x": saved["x"],
            "ln_Y_T": stock[:, 0], "ln_Y_n": stock[:, 1],
            "ln_C_n_beta_forward": cumulative[:, f["n_beta"], 0],
            "ln_C_t_beta_forward": cumulative[:, f["t_beta"], 0],
            "ln_F_DDn_forward": flux[:, f["d_d_n"], 0],
            "ln_F_DDp_forward": flux[:, f["d_d_p"], 0],
            "ln_F_n_beta_forward": flux[:, f["n_beta"], 0],
            "ln_F_t_beta_forward": flux[:, f["t_beta"], 0],
            "ln_S_T": source[:, 0], "ln_S_n": source[:, 1],
        }
        if not np.array_equal(columns["ln_Y_T"], saved["log_T_n"][0, :, 0]) or not np.array_equal(columns["ln_Y_n"], saved["log_T_n"][0, :, 1]):
            raise ValueError("stock extraction changed source values")
        for name in ("n_beta", "t_beta"):
            if not np.array_equal(columns[f"ln_C_{name}_forward"], saved["log_forward_reverse_cumulative"][0, :, f[name], 0]):
                raise ValueError(f"cumulative extraction changed source values: {name}")
        result = {key: [encoded_log(v) for v in values] for key, values in columns.items()}
    result["case_name"] = CASE
    result["case_index"] = 0
    result["epoch_count"] = 257
    result["source_file_sha256"] = PINNED["NUCLEAR_NETWORK_HISTORIES.npz"][1]
    result["scope"] = "saved conditional 18-family all-bare instantaneously-thermalized passive-reservoir sensitivity; separate from ANGTHERM01 17 ionic states"
    result["time_axis"] = "source saved elapsed proper seconds; not cosmic age"
    result["normalization"] = "Y_i=n_i/n_B; source natural logs; event counts per baryon"
    result["log_conversion"] = "log10=value/ln(10); no exponentiation or floor"
    result["negative_infinity"] = "tagged -Infinity denotes source exact zero for these active forward series; plotted as missing, not a fabricated floor"
    for key in ("ln_Y_T", "ln_Y_n", "ln_C_n_beta_forward", "ln_C_t_beta_forward"):
        transformed = [log10_view(v) for v in result[key]]
        for raw, view in zip(result[key], transformed):
            if view is not None and abs(view - raw / LN10) > 4 * np.finfo(float).eps * max(1, abs(view)):
                raise ValueError("log10 view conversion mismatch")
        result["log10_" + key[3:]] = transformed
    result["sample_checks"] = _sample_check(inputs / "c2/NUCLEAR_SAVED_SAMPLE.json", result, 0)
    result["diagnostic_epochs"] = [
        {"epoch": i, **{key: result[key][i] for key in (
            "elapsed_s", "ln_F_DDn_forward", "ln_F_DDp_forward", "ln_S_T", "ln_S_n",
            "ln_F_n_beta_forward", "ln_F_t_beta_forward")}}
        for i in (0, 128, 256)
    ]
    if not all(any(value is not None for value in result[key][1:]) for key in (
        "log10_Y_T", "log10_Y_n", "log10_C_n_beta_forward", "log10_C_t_beta_forward")):
        raise ValueError("a required saved curve lacks finite positive values")
    return result


def write_outputs(result: dict, outputs: Path = OUTPUTS) -> None:
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / "nt_saved_projection.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    fields = ("epoch", "elapsed_s", "x", "ln_Y_T", "ln_Y_n", "ln_C_n_beta_forward", "ln_C_t_beta_forward",
              "ln_F_DDn_forward", "ln_F_DDp_forward", "ln_F_n_beta_forward", "ln_F_t_beta_forward", "ln_S_T", "ln_S_n",
              "log10_Y_T", "log10_Y_n", "log10_C_n_beta_forward", "log10_C_t_beta_forward")
    with (outputs / "nt_saved_projection.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for i in range(result["epoch_count"]):
            writer.writerow({key: i if key == "epoch" else ("" if result[key][i] is None else result[key][i]) for key in fields})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=INPUTS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUTS)
    args = parser.parse_args()
    result = extract(args.input_dir)
    write_outputs(result, args.output_dir)
    print(json.dumps({"case": CASE, "epochs": result["epoch_count"], "sample_checks": len(result["sample_checks"]), "output_dir": str(args.output_dir)}))


if __name__ == "__main__":
    main()
