#!/usr/bin/env python3
"""Render BR04 measured diagnostics. Plot residuals are never exact native errors."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="rei_br04_mpl_"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
COLORS = {1: "#9A3B31", 2: "#176C9D", 4: "#C47B16", 8: "#34816E", 16: "#6C4C95"}


def load_certificates(path):
    rows = list(csv.DictReader(path.open()))
    keys = [(r["family"], float(r["tau"]), int(r["nsteps"]), int(r["resolution"]), r["measure"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate certificate case")
    result = dict(zip(keys, rows))
    for row in rows:
        for field in ("cdf_sup", "w1"):
            value = float(row[field])
            if not np.isfinite(value) or not 0 <= value <= 1.000000000001:
                raise ValueError("invalid probability shape distance")
    return result


def finish(fig, out, name, paths, figures):
    fig.savefig(out / (name + ".png"), dpi=180, facecolor="white")
    fig.savefig(out / (name + ".pdf"), metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    figures.append({"name": name, "inputs": [str(p.relative_to(ROOT)) for p in paths],
                    "png_sha256": hashlib.sha256((out / (name + ".png")).read_bytes()).hexdigest()})


def shape_figure(root, out, figures):
    cp = root / "evidence/age_study/AGE_CERTIFICATES.csv"
    npth = root / "evidence/age_study/AGE_ACTUAL_NODES.csv"
    certs = load_certificates(cp)
    nodes = {r: [] for r in (1, 4, 16)}
    for row in csv.DictReader(npth.open()):
        if row["family"] == "AP" and float(row["tau"]) == 93 and int(row["nsteps"]) == 1 and int(row["resolution"]) in nodes:
            nodes[int(row["resolution"])].append((float(row["age"]), float(row["emitted_weight"])))
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.8), constrained_layout=True)
    y = np.linspace(0, 6, 3000)
    target = -np.expm1(-y) / -np.expm1(-93.)
    axes[0, 0].plot(y, target, color="#202D39", lw=1.8, label="continuous exact CDF")
    for r, atoms in nodes.items():
        atoms = np.array(sorted(atoms))
        ages, emitted = atoms.T
        w = emitted * np.exp(-93 * ages)
        c = np.r_[0, np.cumsum(w / w.sum())]
        visible_atoms = (93 * ages)[93 * ages <= 6]
        plot_y = np.unique(np.r_[y, visible_atoms, np.nextafter(visible_atoms, -np.inf)])
        values = c[np.searchsorted(93 * ages, plot_y, side="right")]
        plot_target = -np.expm1(-plot_y) / -np.expm1(-93.)
        axes[0, 0].step(plot_y, values, where="post", color=COLORS[r], alpha=.9, label=f"AP r={r}")
        axes[0, 1].plot(plot_y, values - plot_target, color=COLORS[r], lw=.9, label=f"r={r}")
    axes[0, 0].set(title="A. Actual retained birth ages", xlabel=r"optical age $y=\kappa A$", ylabel="normalized survivor CDF", xlim=(0, 6), ylim=(-.02, 1.03))
    axes[0, 0].legend(loc="lower right", fontsize=9)
    axes[0, 1].axhline(0, color="black", lw=.6)
    axes[0, 1].set(title="B. Signed CDF residual", xlabel=r"optical age $y=\kappa A$", ylabel=r"$F_{\rm discrete}-F_{\rm exact}$", xlim=(0, 6))
    rs = np.array([1, 2, 4, 8, 16])
    for nt, marker, style in ((1, "o", "-"), (32, "s", "--")):
        rows = [certs[("AP", 93., nt, int(r), "survivor")] for r in rs]
        axes[1, 0].loglog(rs, [93*float(q["w1"]) for q in rows], marker=marker, ls=style, color="#176C9D", label=fr"$\kappa W_1$, $N_t={nt}$")
        axes[1, 0].loglog(rs, [float(q["cdf_sup"]) for q in rows], marker=marker, ls=style, color="#9A3B31", label=fr"CDF supremum, $N_t={nt}$")
    rows = [certs[("AP", 93., 1, int(r), "survivor")] for r in rs]
    axes[1, 1].loglog(rs, [abs(float(q["mean_defect"]))/float(q["exact_mean"]) for q in rows], "o-", color="#34816E", label="relative mean-age defect")
    axes[1, 1].loglog(rs, [abs(float(q["second_defect"]))/float(q["exact_second"]) for q in rows], "s-", color="#6C4C95", label="relative second-moment defect")
    axes[1, 1].loglog(rs, [93*float(q["w1"]) for q in rows], "^-", color="#176C9D", label=r"shape distance $\kappa W_1$")
    for ax in axes[1, :]:
        ax.set_xscale("log", base=2)
        ax.set_xticks(rs, labels=[str(r) for r in rs])
        ax.set_xlabel("birth refinement r")
        ax.legend(fontsize=8.7)
    axes[1, 0].set(title="C. Distribution error persists with time subdivision", ylabel="dimensionless distribution distance")
    axes[1, 1].set(title="D. Moment accuracy does not fix distribution accuracy", ylabel="dimensionless error or distance")
    for ax in axes.flat:
        ax.grid(alpha=.22)
    fig.suptitle("BR04 frozen control: total optical depth 93, constant source\nExact mass fit; finite age-distribution error measured separately", fontsize=13)
    finish(fig, out, "BR04_AGE_DISTRIBUTION", [cp, npth], figures)


def native_figure(root, out, figures):
    path = root / "evidence/native_audit/crossed/TIME_AGE_ANALYSIS.json"
    data = json.loads(path.read_text())
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 8.4), constrained_layout=True)
    fields = [("photons_com3", r"$|\Delta_t N_\gamma|$ [reference-comoving $\mathrm{m}^{-3}$]", "A. Surviving photon number"),
              ("mean_age_s", r"$|\Delta_t\langle A\rangle|$ [s]", "B. Mean birth age"),
              ("q2", r"$|\Delta_t q_2|$ [dimensionless]", "C. Energy-weighted quadrupole")]
    plot_points = []
    for ax, (field, ylabel, title) in zip(axes.flat, fields):
        for r in (2, 4):
            series = data["fixed_r_time_slices"][str(r)]
            ns = series["N_t"]
            changes = series["fields"][field]["changes"]
            vals = [float(d["absolute"]) for d in changes]
            if any(v >= 0 for v in vals):
                raise ValueError("caption all negative no longer true")
            ax.loglog(ns[1:], np.abs(vals), "o-" if r == 2 else "s-", color=COLORS[r], label=f"r={r}")
            for lo, hi, v in zip(ns, ns[1:], vals):
                plot_points.append({"field": field, "r": r, "N_coarse": lo, "N_fine": hi, "signed_time_difference": v})
        ax.set_xscale("log", base=2)
        ax.set_xticks([32, 64, 128], labels=["16→32", "32→64", "64→128"])
        ax.set(title=title, xlabel="temporal grid pair", ylabel=ylabel)
        ax.legend()
        ax.grid(alpha=.22)
    ax = axes[1, 1]
    rects = [data["rectangles"][key] for key in ("N16_32_r2_4", "N32_64_r2_4")]
    for offset, field, color, label in ((-.16, "mean_age_s", "#34816E", "mean age"), (.16, "q2", "#6C4C95", r"$q_2$")):
        vals = [float(rect["final"][field]["D_tr_over_time_difference_at_2r"]) for rect in rects]
        bars = ax.bar(np.arange(2) + offset, vals, width=.29, color=color, label=label)
        ax.bar_label(bars, labels=[f"{v:.3f}" for v in vals], padding=3, fontsize=10)
    ax.axhline(0, color="black", lw=.7)
    ax.axhline(-1, color="#666666", lw=.8, ls=":")
    ax.set_xticks([0, 1], labels=["16→32, r=2→4", "32→64, r=2→4"])
    ax.set(title="D. Measured time–birth interaction", ylabel=r"$D_{tr}/\Delta_t O\,(r=4)$", ylim=(-7.5, .65))
    ax.legend(loc="lower left")
    ax.grid(axis="y", alpha=.22)
    fig.suptitle("BR04 evolving H/He/D: two new histories complete two crossed grids\nFinite-grid differences; no exact evolving reference or universal order claim", fontsize=13)
    fig.supxlabel("Panels A–C show magnitudes; every displayed signed time difference is negative.", fontsize=9)
    finish(fig, out, "BR04_NATIVE_TIME_AGE", [path], figures)
    with (out / "NATIVE_PLOT_POINTS.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(plot_points[0]))
        writer.writeheader(); writer.writerows(plot_points)


def source_figure(root, out, figures):
    path = root / "evidence/age_study/AGE_SOURCE_MIXTURE_BOUNDS.csv"
    rows = [r for r in csv.DictReader(path.open()) if r["measure"] == "survivor"]
    lookup = {(r["family"], int(r["resolution"])): r for r in rows}
    sequence = [("GL", 2), ("GL", 4)] + [("AP", r) for r in (1, 2, 4, 8)]
    ordered = [lookup[k] for k in sequence]
    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.7), constrained_layout=True)
    labels = [f"{family}{r}" if family == "GL" else f"AP r={r}" for family, r in sequence]
    ratios = [float(r["discrete_mass_com3"])/float(r["exact_mass_com3"]) for r in ordered]
    bars = axes[0].bar(labels, ratios, color=["#999999", "#666666", *[COLORS[r] for r in (1, 2, 4, 8)]])
    axes[0].axhline(1, color="black", lw=.9, ls=":")
    axes[0].bar_label(bars, labels=[f"{v:.5f}" for v in ratios], fontsize=8.5, padding=3)
    axes[0].set(title="A. Surviving photon mass", ylabel=r"$\widehat N_\gamma/N_{\gamma,\mathrm{exact}}$", ylim=(0, 1.14))
    axes[0].tick_params(axis="x", labelrotation=35)
    rs = [1, 2, 4, 8]
    ap = [lookup[("AP", r)] for r in rs]
    axes[1].loglog(rs, [float(r["mixture_cdf_upper_bound"]) for r in ap], "o-", color="#9A3B31")
    axes[1].set(title="B. AP CDF error upper bound", ylabel="labelwise bound plus mixture-weight TV")
    axes[2].loglog(rs, [float(r["duration_s"])*float(r["mixture_w1_upper_bound"]) for r in ap], "o-", color="#176C9D", label=r"upper bound for $W_1$")
    axes[2].loglog(rs, [float(r["duration_s"])*abs(float(r["mixture_mean_defect"])) for r in ap], "s--", color="#34816E", label="actual mean-age error")
    axes[2].set(title="C. AP age distribution and mean", ylabel="seconds")
    axes[2].legend(fontsize=9)
    for ax in axes[1:]:
        ax.set_xscale("log", base=2)
        ax.set_xticks(rs, labels=[str(r) for r in rs])
        ax.set_xlabel("birth refinement r")
    for ax in axes:
        ax.grid(axis="y", alpha=.22)
    fig.suptitle("BR04 original 384 photon labels: frozen opacity, constant source, T=8×10¹² s, Nₜ=32\nPanels B–C retain labels in the bound; the exact unlabelled mixture distance was not computed", fontsize=12.5)
    finish(fig, out, "BR04_SOURCE_AGE_BOUNDS", [path], figures)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=ROOT / "evidence/figures")
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
    figures = []
    shape_figure(ROOT, a.output, figures)
    native_figure(ROOT, a.output, figures)
    source_figure(ROOT, a.output, figures)
    (a.output / "PLOT_PROVENANCE.json").write_text(json.dumps({"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "figures": figures,
        "interpretation": "Frozen reference errors and native finite-grid differences are different quantities. CDF display is cropped at optical age 6; reported certificate integrates full support."}, indent=2) + "\n")
    print(json.dumps({"status": "RENDERED_PENDING_VISUAL_AUDIT", "figures": len(figures)}))


if __name__ == "__main__":
    main()
