#!/usr/bin/env python3
"""Three source-bound figures from analyze_saved.py outputs; no ODE calls."""
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
import numpy as np


COLORS = {"matter": "#0072B2", "radiation": "#D55E00", "shear": "#222222",
          "initial": "#CC79A7", "sum": "#009E73", "boundary": "#777777"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _redshift_axis(ax, z, tail):
    ax.set_xlim(float(z[0]), float(z[-1]))
    ax.set_xlabel(r"Mean redshift $\bar z$")
    if tail:
        ax.axvline(4.0, color=COLORS["boundary"], linestyle=":", linewidth=0.9, zorder=0)
    ax.grid(alpha=0.18, linewidth=0.5)


def _save(fig, out, name):
    fig.savefig(out / (name + ".png"), dpi=240, bbox_inches="tight")
    fig.savefig(out / (name + ".pdf"), bbox_inches="tight")
    plt.close(fig)


def _footer(fig, coverage, extra=""):
    text = ("Collisionless finite-owner LRS Bianchi I · same normal frame · " + coverage
            + "\nFull Frobenius = " + r"$\sqrt{2}$" + " × half-contraction; " + extra)
    fig.text(0.5, 0.004, text, ha="center", va="bottom", fontsize=8.0)


def make_plots(analysis_dir, out):
    root, out = Path(analysis_dir), Path(out)
    summary = json.loads((root / "SUMMARY.json").read_text())
    packet_path = root / "TIME_PACKET.npz"
    if sha256(packet_path) != summary["packet_sha256"]:
        raise ValueError("PLOT_PACKET_HASH_MISMATCH")
    if sha256(root / "ENDPOINTS.csv") != summary["endpoints_sha256"]:
        raise ValueError("PLOT_ENDPOINT_HASH_MISMATCH")
    with np.load(packet_path, allow_pickle=False) as archive:
        data = {key: archive[key].copy() for key in archive.files}
    ids = list(data["case_ids"].astype(str))
    cid = "mixed_s+0_m+1" if "mixed_s+0_m+1" in ids else summary["selected_case_ids"][0]
    j = ids.index(cid)
    z = data["zbar"]
    _, S, Pm, Pr = data["values"][j]
    root2 = np.sqrt(2.0)
    tail = int(data["tail_samples"]) > 0
    coverage = r"$\bar z=20\rightarrow" + format(float(z[-1]), ".6g") + "$"
    out.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({"font.size": 9.5, "axes.labelsize": 10, "axes.titlesize": 10.5,
                         "legend.fontsize": 8.7, "xtick.labelsize": 9, "ytick.labelsize": 9,
                         "lines.linewidth": 1.8, "savefig.facecolor": "white", "pdf.fonttype": 42})

    # Figure 1: magnitudes, signed stress alternatives and cancellation are
    # different panels; no norm is labeled as a signed tensor component.
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.2), layout="constrained")
    fig.get_layout_engine().set(rect=(0.0, 0.085, 1.0, 0.87))
    fig.suptitle("Separate matter and radiation stresses", fontsize=13)
    ax = axes[0, 0]
    ax.plot(z, root2 * np.abs(S), color=COLORS["shear"], label=r"$\Sigma_F=\sqrt{2}|S|$")
    ax.plot(z, root2 * S, color=COLORS["sum"], linestyle="--", label=r"Signed $\sqrt{2} S$")
    ax.set_title("(a) Shear magnitude and sign")
    ax.set_ylabel("Dimensionless shear")
    ax.legend()
    ax = axes[0, 1]
    ax.plot(z, root2 * np.abs(Pm), color=COLORS["matter"], label=r"$\Pi_{m,F}$")
    ax.plot(z, root2 * np.abs(Pr), color=COLORS["radiation"], linestyle="--", label=r"$\Pi_{r,F}$")
    ax.plot(z, root2 * np.abs(Pm + Pr), color=COLORS["sum"], linestyle=":", label=r"$\Pi_{{\rm total},F}$")
    ax.set_title("(b) Stress magnitudes")
    ax.set_ylabel("Dimensionless stress norm")
    ax.legend(ncol=1)
    ax = axes[1, 0]
    ax.plot(z, root2 * Pm, color=COLORS["matter"], label="Matter")
    ax.plot(z, root2 * Pr, color=COLORS["radiation"], linestyle="--", label="Radiation")
    ax.plot(z, root2 * (Pm + Pr), color=COLORS["sum"], linestyle=":", label="Signed sum")
    ax.axhline(0.0, color="0.6", linewidth=0.6)
    ax.set_title("(c) Signed sector amplitudes")
    ax.set_ylabel(r"Signed $\sqrt{2} P_A$")
    ax.legend()
    denominator = np.abs(Pm) + np.abs(Pr)
    cancel = 1.0 - np.divide(np.abs(Pm + Pr), denominator, out=np.ones_like(S), where=denominator > 0)
    ax = axes[1, 1]
    ax.plot(z, cancel, color=COLORS["sum"])
    ax.set_ylim(-0.025, 1.025)
    ax.set_title("(d) Instantaneous cancellation")
    ax.set_ylabel(r"$1-|P_m+P_r|/(|P_m|+|P_r|)$")
    for ax in axes.flat:
        _redshift_axis(ax, z, tail)
    for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
    _footer(fig, coverage, "case " + cid + ("; dotted line: continuation at z=4" if tail else "; no z<4 input"))
    _save(fig, out, "01_separate_stress_time")

    # Figure 2: full source-memory attribution and an explicit sampled residual
    # budget. The z4 defect is propagated as a diagnostic, not absorbed into a
    # physical initial condition or a species contribution.
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 6.1), sharex=True, layout="constrained",
                             gridspec_kw={"height_ratios": [2.0, 1.0]})
    fig.get_layout_engine().set(rect=(0.0, 0.085, 1.0, 0.87))
    fig.suptitle("Signed memory along the same coupled trajectory", fontsize=13)
    ax = axes[0]
    for key, label, color, style in (
        ("initial_memory", "Initial memory", COLORS["initial"], "-."),
        ("matter_memory", "Matter memory", COLORS["matter"], "-"),
        ("radiation_memory", "Radiation memory", COLORS["radiation"], "--"),
        ("predicted_signed_shear", "Sum of memories", COLORS["sum"], ":"),
    ):
        ax.plot(z, root2 * data[key][j], color=color, linestyle=style, label=label)
    ax.plot(z, root2 * S, color=COLORS["shear"], linewidth=1.0, label="Saved signed shear")
    ax.set_ylabel(r"Signed $\sqrt{2}$-scaled shear amplitude")
    ax.set_title("(a) Conditional path contributions")
    ax.legend(ncol=2)
    ax.axhline(0.0, color="0.6", linewidth=0.6)
    ax = axes[1]
    ax.plot(z, root2 * data["closure_defect"][j], color=COLORS["shear"], label="Combined residual")
    if tail:
        tz = data["tail_zbar"]
        ax.plot(tz, root2 * data["tail_local_closure_defect"][j], color=COLORS["matter"],
                linestyle="--", label="Tail-local residual")
        ax.plot(tz, root2 * data["tail_transported_old_closure_defect"][j], color=COLORS["radiation"],
                linestyle=":", label="Transported z=4 residual")
    ax.set_ylabel("Sampled closure residual")
    ax.set_title("(b) Quadrature and saved-history diagnostic")
    ax.legend(ncol=2)
    for ax in axes:
        _redshift_axis(ax, z, tail)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
    _footer(fig, coverage, "case " + cid + "; sampled residuals, no continuum error certificate")
    _save(fig, out, "02_signed_memory_time")

    # Figure 3: two scientifically distinct initial-source slices remain
    # separate panels. These are selected paths from the actual stored sweep.
    with (root / "ENDPOINTS.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    selections = [
        [row for row in rows if row["source_lane"] == "radiation_slice"
         and abs(float(row["initial_S_h"])) <= 1e-15],
        [row for row in rows if row["metadata_lane"] == "MATTER_SLICE"
         and abs(float(row["initial_S_h"])) <= 1e-15],
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.0), layout="constrained")
    fig.get_layout_engine().set(rect=(0.0, 0.14, 1.0, 0.78))
    fig.suptitle("Endpoint response to signed initial stress", fontsize=13)
    used_slices = []
    for ax, chosen, source, title in zip(axes, selections, ("r", "m"),
                                       ("(a) Initial radiation-stress slice", "(b) Initial matter-stress slice")):
        key = "initial_Pi_" + source + "_F_signed"
        chosen.sort(key=lambda row: float(row[key]))
        used_slices.append([row["case_id"] for row in chosen])
        if len(chosen) < 2:
            ax.text(0.5, 0.5, "Required slice is absent", ha="center", va="center", transform=ax.transAxes)
        else:
            xx = [float(row[key]) for row in chosen]
            for field, label, color, style, marker in (
                ("matter_memory_final_F_signed", "Matter memory", COLORS["matter"], "-", "o"),
                ("radiation_memory_final_F_signed", "Radiation memory", COLORS["radiation"], "--", "s"),
                ("S_final_F_signed", "Saved signed shear", COLORS["shear"], ":", "."),
            ):
                ax.plot(xx, [float(row[field]) for row in chosen], label=label, color=color,
                        linestyle=style, marker=marker, markersize=3.0)
            ax.legend()
        ax.set_title(title)
        ax.set_xlabel(r"Initial signed $\Pi_{" + source + r",F}$")
        ax.set_ylabel("Endpoint signed shear contribution")
        ax.ticklabel_format(axis="both", style="sci", scilimits=(0, 0), useMathText=True)
        ax.grid(alpha=0.18, linewidth=0.5)
        ax.axhline(0.0, color="0.6", linewidth=0.6)
    _footer(fig, coverage, r"both slices: $\Sigma_0=0$; the other initial stress is approximately zero")
    _save(fig, out, "03_signed_endpoint_slices")
    receipt = {"schema": "PHYS76_TIME_FIGURE_RECEIPT_V1", "source_packet_sha256": sha256(packet_path),
               "source_summary_sha256": sha256(root / "SUMMARY.json"), "case": cid,
               "endpoint_slice_case_ids": used_slices, "z_start": float(z[0]), "z_end": float(z[-1]),
               "boundary_z4_shown": tail, "scope": summary["scope"],
               "normalization": summary["normalization"], "intended_print_width_mm": 183,
               "figure_read_status": "PENDING_VISUAL_INSPECTION",
               "new_ode_integrations": 0, "benchmark_runs": 0,
               "files": {path.name: sha256(path) for path in sorted(out.iterdir())}}
    with (out / "FIGURE_RECEIPT.json").open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(make_plots(args.analysis_dir, args.out), indent=2))
