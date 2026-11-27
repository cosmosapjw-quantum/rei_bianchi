#!/usr/bin/env python3
"""Plot complete nominal parameter grids from endpoint CSV and input metadata.

Reads no trajectory arrays and imports no model/ODE solver.  Original radiation
and matter lanes remain distinct.  The missing zero-stress matter column is a
blank strip, never an interpolated or recomputed trajectory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "hh_phys76_mplconfig"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np


FIELDS = ("Sigma_final_F", "Pi_total_final_F")
STEM = "04_full_parameter_sweep"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def nominal_grid(records, endpoints, lane):
    """Use requested initial parameters, not rounded moment-derived values."""
    selected = []
    for record in records:
        metadata = record["metadata"]
        current = metadata.get("lane", "RADIATION_SLICE")
        if current != lane:
            continue
        if lane == "RADIATION_SLICE":
            if record["source_lane"] != "radiation_slice":
                raise ValueError("RADIATION_SOURCE_LANE_MISMATCH")
            initial_s = float(metadata["Sigma0"]) * int(metadata["eps_sigma"])
            initial_p = float(metadata["Pi0"]) * int(metadata["eps_pi"])
        else:
            if record["source_lane"] != "new_matter_and_mixed":
                raise ValueError("MATTER_SOURCE_LANE_MISMATCH")
            initial_s = float(metadata["signed_Sigma0"])
            initial_p = float(metadata["signed_Pi_m0"])
            if float(metadata["signed_Pi_r0"]) != 0.0:
                raise ValueError("MATTER_INITIAL_RADIATION_STRESS_NOT_ZERO")
        row = endpoints[record["case_id"]]
        if row["source_lane"] != record["source_lane"] or row["metadata_lane"] != lane:
            raise ValueError("ENDPOINT_SOURCE_LANE_MISMATCH")
        if not np.isclose(float(row["z_final"]), 2.0, rtol=0.0, atol=3e-12):
            raise ValueError("Z2_ENDPOINT_REQUIRED")
        numbers = [float(row[field]) for field in FIELDS]
        if not np.isfinite([initial_s, initial_p, *numbers]).all() or min(numbers) < 0:
            raise ValueError("FINITE_NONNEGATIVE_ENDPOINT_NORMS_REQUIRED")
        selected.append((initial_s, initial_p, numbers, record["case_id"]))
    s_axis = np.array(sorted({row[0] for row in selected}))
    p_axis = np.array(sorted({row[1] for row in selected}))
    expected = (25, 25) if lane == "RADIATION_SLICE" else (25, 24)
    if (len(s_axis), len(p_axis)) != expected or len(selected) != expected[0] * expected[1]:
        raise ValueError("NOMINAL_GRID_DIMENSIONS_MISMATCH:" + lane)
    s_lookup = {float(value): k for k, value in enumerate(s_axis)}
    p_lookup = {float(value): k for k, value in enumerate(p_axis)}
    values = np.full((2, *expected), np.nan)
    cell_ids = np.full(expected, "", dtype="<U80")
    for initial_s, initial_p, numbers, cid in selected:
        i, j = s_lookup[initial_s], p_lookup[initial_p]
        if cell_ids[i, j]:
            raise ValueError("DUPLICATE_NOMINAL_GRID_CELL")
        values[:, i, j] = numbers
        cell_ids[i, j] = cid
    if not np.isfinite(values).all() or np.any(cell_ids == ""):
        raise ValueError("INCOMPLETE_NOMINAL_GRID")
    if lane == "MATTER_SLICE" and np.any(p_axis == 0):
        raise ValueError("UNEXPECTED_ZERO_MATTER_STRESS_CASE")
    return {"lane": lane, "s_axis": s_axis, "p_axis": p_axis,
            "values": values, "case_ids": cell_ids}


def edges(centers):
    centers = np.asarray(centers)
    delta = np.diff(centers)
    if centers.ndim != 1 or len(centers) < 2 or not np.all(delta > 0):
        raise ValueError("STRICTLY_INCREASING_GRID_AXIS_REQUIRED")
    return np.concatenate(([centers[0] - delta[0] / 2],
                           (centers[:-1] + centers[1:]) / 2,
                           [centers[-1] + delta[-1] / 2]))


def make_sweep_plot(analysis_dir, out):
    root, out = Path(analysis_dir), Path(out)
    endpoint_path, index_path = root / "ENDPOINTS.csv", root / "INPUT_INDEX.json"
    with endpoint_path.open() as stream:
        rows = list(csv.DictReader(stream))
    endpoints = {row["case_id"]: row for row in rows}
    index = json.loads(index_path.read_text())
    records = index["old_cases"]
    if len(endpoints) != 1231 or len(endpoints) != len(rows):
        raise ValueError("EXACT_1231_UNIQUE_ENDPOINTS_REQUIRED")
    if len(records) != 1231 or {r["case_id"] for r in records} != set(endpoints):
        raise ValueError("ENDPOINT_INPUT_INDEX_COVERAGE_MISMATCH")
    grids = [nominal_grid(records, endpoints, lane)
             for lane in ("RADIATION_SLICE", "MATTER_SLICE")]
    paths = [out / (STEM + ".png"), out / (STEM + ".pdf"), out / "FIGURE04_RECEIPT.json"]
    out.mkdir(parents=True, exist_ok=True)
    if any(path.exists() for path in paths):
        raise FileExistsError("FIGURE04_OUTPUTS_ARE_CREATE_ONLY")
    plt.rcParams.update({"font.size": 9.0, "axes.labelsize": 9.0, "axes.titlesize": 10.0,
                         "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
                         "savefig.facecolor": "white", "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.4), sharey=True, layout="constrained")
    fig.get_layout_engine().set(rect=(0.0, 0.155, 1.0, 0.80))
    fig.suptitle(r"Full parameter sweep at $\bar z=2$", fontsize=13)
    color_limits = []
    for row, field in enumerate(FIELDS):
        maximum = max(float(np.max(grid["values"][row])) for grid in grids)
        color_limits.append([0.0, maximum])
        norm = Normalize(vmin=0.0, vmax=maximum)
        for col, grid in enumerate(grids):
            ax = axes[row, col]
            p_axis, s_axis = grid["p_axis"], grid["s_axis"]
            yy = edges(s_axis)
            if col == 0:
                xx = edges(p_axis)
                ax.pcolormesh(xx, yy, grid["values"][row], shading="flat", norm=norm, cmap="viridis", rasterized=True)
            else:
                negative, positive = p_axis < 0, p_axis > 0
                left, right = edges(p_axis[negative]), edges(p_axis[positive])
                ax.axvspan(left[-1], right[0], facecolor="0.93", edgecolor="0.72", hatch="///", linewidth=0.0)
                for mask in (negative, positive):
                    ax.pcolormesh(edges(p_axis[mask]), yy, grid["values"][row][:, mask],
                                  shading="flat", norm=norm, cmap="viridis", rasterized=True)
            sector = "r" if col == 0 else "m"
            ax.set_xlabel(r"Initial signed $P_{" + sector + r",0}$ (half)")
            if col == 0:
                ax.set_ylabel(r"Initial signed $S_0$ (half)")
            pmax = float(np.max(np.abs(p_axis)))
            ax.set_xticks([-pmax, -pmax / 2, 0.0, pmax / 2, pmax])
            ax.set_yticks([-0.004, -0.002, 0.0, 0.002, 0.004])
            ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0), useMathText=True)
            label = "Radiation: 625 cases (25×25)" if col == 0 else "Matter: 600 cases (25×24)"
            ax.set_title("(" + "abcd"[2 * row + col] + ") " + label)
        colorbar = fig.colorbar(ScalarMappable(norm=norm, cmap="viridis"), ax=list(axes[row]),
                               fraction=0.045, pad=0.02, aspect=23)
        colorbar.set_label(r"$\Sigma_F$ at $\bar z=2$" if row == 0 else r"$\Pi_{{\rm total},F}$ at $\bar z=2$")
        colorbar.formatter.set_powerlimits((0, 0))
        colorbar.formatter.set_useMathText(True)
        colorbar.update_ticks()
    footer = ("Collisionless non-tilted LRS Bianchi I · same normal frame · preliminary\n"
              r"Colors: full Frobenius = $\sqrt{2}$ × half-contraction; total norm after signed tensor sum."
              "\nOther initial stress is zero; both species evolve. Mixed 6 cases are outside these grids."
              "\nHatched matter strip: initial zero-stress column absent; no interpolation.")
    fig.text(0.5, 0.004, footer, ha="center", va="bottom", fontsize=8.0)
    fig.savefig(paths[0], dpi=240, bbox_inches="tight")
    fig.savefig(paths[1], bbox_inches="tight")
    plt.close(fig)
    receipt = {"schema": "PHYS76_FULL_SWEEP_FIGURE_V1", "status": "PENDING_VISUAL_INSPECTION",
               "source_endpoints_sha256": sha256(endpoint_path), "source_input_index_sha256": sha256(index_path),
               "plot_source_sha256": sha256(__file__), "z_endpoint": 2.0,
               "color_fields": list(FIELDS), "shared_row_color_limits": color_limits,
               "axes": "nominal signed half-contraction initial parameters from original metadata",
               "color_normalization": "nonnegative full Frobenius; sqrt(2) times half norm; total after signed component sum",
               "missing_matter_zero_column": "hatched empty strip; never interpolated or resimulated",
               "mixed_cases": "6 opposing-sign cases excluded from rectangular grids",
               "intended_print_width_mm": 183, "new_ODE_solves": 0, "benchmark_runs": 0,
               "HH_R10": "OFF", "production_admission": "NOT_ISSUED",
               "grids": [{"lane": grid["lane"], "shape": list(grid["case_ids"].shape),
                          "cases": int(grid["case_ids"].size),
                          "s_axis_half": grid["s_axis"].tolist(), "p_axis_half": grid["p_axis"].tolist(),
                          "field_ranges": {field: {"min": float(np.min(grid["values"][k])),
                                                    "max": float(np.max(grid["values"][k]))}
                                           for k, field in enumerate(FIELDS)},
                          "case_ids_by_matrix_cell": grid["case_ids"].tolist()}
                         for grid in grids],
               "files": {path.name: sha256(path) for path in paths[:2]}}
    with paths[2].open("x") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = make_sweep_plot(args.analysis_dir, args.out)
    print(json.dumps({key: value for key, value in result.items() if key != "grids"}, indent=2))
