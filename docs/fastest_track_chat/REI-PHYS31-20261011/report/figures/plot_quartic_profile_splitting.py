#!/usr/bin/env python3
"""Plot PHYS31 cached coefficients and exact-defined profiles, display only.

This program imports no research implementation and performs no integration,
physical kernel/derivative evaluation, root search, finite difference, or toy
calculation. The only sampled functions are the two displayed density formulas.
Moment labels are copied from the exact derivation and accepted raw record.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


FIGURE_DIR = Path(__file__).resolve().parent
TASK_ROOT = FIGURE_DIR.parents[1]
RAW_PATH = TASK_ROOT / "contributions/numerics/QUARTIC_PROFILE_FIRST.json"
EXPECTED_RAW_SHA256 = "843335dd8754bfaf57d201d9db888e80a7713d95a8147de08ffdb97db609e66a"
BASENAME = "PHYS31_QUARTIC_PROFILE_SPLITTING"


def main() -> None:
    raw_bytes = RAW_PATH.read_bytes()
    raw_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    if raw_sha256 != EXPECTED_RAW_SHA256:
        raise RuntimeError("The cached numerical record changed; reselect the figure source explicitly.")
    raw = json.loads(raw_bytes)
    coefficients = raw["physical_quartic_profile_difference"]
    branch_keys = ("upper_root", "lower_root")
    decimal_strings = [coefficients[key]["paths"]["log"]["D4_eV-2"] for key in branch_keys]
    # Float conversion and x1000 are display conversions only, not new estimates.
    bar_values = [float(value) * 1000.0 for value in decimal_strings]
    gap_string = raw["descriptive_gap_quartic_difference"]["paths"]["log"]
    gap_display = float(gap_string) * 1000.0

    # Exactly 501 display abscissae. These samples do not establish the moments.
    z = np.linspace(-1.0, 1.0, 501)
    h_u = np.full_like(z, 0.5)
    h_p = (35.0 * z**4 - 30.0 * z**2 + 11.0) / 16.0

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "mathtext.fontset": "dejavusans",
        "font.size": 12,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "axes.linewidth": 0.85,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "svg.fonttype": "none",
        "svg.hashsalt": "REI-PHYS31-20261011-cached-figure",
    })
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14.2, 5.8))
    fig.subplots_adjust(left=0.065, right=0.97, bottom=0.27, top=0.75, wspace=0.37)
    fig.suptitle("Equal second moments, distinct quartic threshold coefficients", y=0.976,
                 fontsize=18, fontweight="semibold", color="#1E293B")
    fig.text(0.5, 0.877,
             r"$W_{j,p}(\delta)-W_{j,u}(\delta)=D_{4,j}\,\delta^4+o(\delta^4)$"
             r"$\qquad(\delta\downarrow0)$",
             ha="center", va="center", fontsize=15, color="#334155")

    navy, teal, plum = "#355C8D", "#087F80", "#8D527A"
    ax_a.set_title("A  Fixed symmetric density profiles", loc="left", pad=13,
                   fontweight="semibold", color="#1E293B")
    ax_a.plot(z, h_u, color=navy, linewidth=2.2, linestyle=(0, (5, 3)),
              label=r"$h_u(z)=1/2$")
    ax_a.plot(z, h_p, color=teal, linewidth=2.5,
              label=r"$h_p(z)=(35z^4-30z^2+11)/16$")
    ax_a.set_xlim(-1.03, 1.03)
    ax_a.set_ylim(0, 1.1)
    ax_a.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax_a.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_a.set_xlabel(r"Profile coordinate $z$")
    ax_a.set_ylabel(r"Density $h(z)$")
    ax_a.text(0.5, 0.90,
              r"$\mu_{2,u}=\mu_{2,p}=1/3,\quad\Delta\mu_4=8/315$",
              transform=ax_a.transAxes, ha="center", va="center", fontsize=12,
              bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.0})
    ax_a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.245), frameon=False,
                fontsize=11.8, handlelength=2.6, borderaxespad=0, labelspacing=0.45)

    ax_b.set_title("B  Quartic coefficients at retained levels", loc="left", pad=13,
                   fontweight="semibold", color="#1E293B")
    ax_b.bar([0, 1], bar_values, width=0.44, color=plum, alpha=0.93, zorder=3)
    ax_b.axhline(0, color="#475569", linewidth=1.0, zorder=4)
    ax_b.set_xlim(-0.6, 1.6)
    ax_b.set_ylim(-1.36, 0.065)
    ax_b.set_xticks([0, 1], [r"Upper branch $(\star)$", r"Lower branch $(0)$"])
    ax_b.set_yticks([-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0])
    ax_b.set_ylabel(r"$D_{4,j}$  ($10^{-3}$ eV$^{-2}$)")
    ax_b.tick_params(axis="x", pad=9)
    for x_pos, value in enumerate(bar_values):
        ax_b.annotate(f"{value:.6f}", xy=(x_pos, value), xytext=(0, -10),
                      textcoords="offset points", ha="center", va="top",
                      fontsize=12.5, color="#653A58", fontweight="semibold")
    ax_b.text(0.5, -0.245, "Gap coefficient (lower minus upper)",
              transform=ax_b.transAxes, ha="center", va="top", fontsize=11.6,
              color="#334155")
    ax_b.text(0.5, -0.350,
              r"$D_{4,0}-D_{4,\star}=+" + f"{gap_display:.6f}"
              + r"\times10^{-3}\ \mathrm{eV}^{-2}$",
              transform=ax_b.transAxes, ha="center", va="top", fontsize=12,
              color="#653A58")

    for ax in (ax_a, ax_b):
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["bottom", "left"]].set_color("#64748B")
        ax.tick_params(colors="#334155", length=3.5)
        ax.grid(axis="y", color="#E2E8F0", linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)

    fig.text(0.5, 0.032,
             r"PHYS31  |  Fixed inputs; the same retained $A_j$ level within each branch. "
             "Coefficients only; no finite-width certification.",
             ha="center", va="center", fontsize=10.7, color="#475569")
    description = (
        "PHYS31 cached-result figure. Left: two exact-defined symmetric probability "
        "densities on [-1,1], 501 display samples, equal mu2=1/3 and delta_mu4=8/315. "
        "Right: upper and lower quartic profile-difference coefficients from the "
        "existing raw log-energy calculation. Fixed inputs and equal retained A_j "
        "within each branch; no finite-width certification, no new science execution."
    )
    png = FIGURE_DIR / f"{BASENAME}.png"
    svg = FIGURE_DIR / f"{BASENAME}.svg"
    fig.savefig(png, dpi=180, metadata={"Title": BASENAME, "Description": description})
    fig.savefig(svg, metadata={"Title": BASENAME, "Description": description,
                               "Date": None})
    plt.close(fig)
    print(json.dumps({
        "status": "RENDERED_PENDING_VISUAL_INSPECTION",
        "raw_sha256": raw_sha256,
        "display_samples": 501,
        "display_coefficient_path": "physical_quartic_profile_difference.*.paths.log.D4_eV-2",
        "coefficient_strings": dict(zip(branch_keys, decimal_strings)),
        "gap_string": gap_string,
        "new_scientific_execution_count": 0,
        "files": [{"path": str(path), "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                   for path in (png, svg)],
        "matplotlib_version": matplotlib.__version__,
        "numpy_version": np.__version__,
    }, indent=2))


if __name__ == "__main__":
    main()
