#!/usr/bin/env python3
"""Render PHYS30 cached coefficients; no physics program imports or evaluations."""

from pathlib import Path
import hashlib
import json
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


DIRECTORY = Path(__file__).resolve().parent
PROJECT = DIRECTORY.parent
RAW_RELATIVE = "contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json"
RAW_EXPECTED_SHA256 = "5184af6139423792abc0a95e53bd5ccabca459820761aa1a3f350bda4ac7082e"
RAW_EXPECTED_BYTES = 231082
PNG = DIRECTORY / "PHYS30_PROFILE_SECOND_ORDER.png"
PROVENANCE = DIRECTORY / "FIGURE_PROVENANCE.json"

PROFILES = ("uniform", "triangular")
BRANCHES = ("upper_root", "lower_root")
COLORS = {"uniform": "#286AA7", "triangular": "#D57B18"}
LABELS = (
    "Geometry (7 terms)",
    "Band averaging",
    "Variance correction",
    "Implicit mixed term",
    "Implicit curvature",
    "Total d",
)
FIELDS = (
    ("d_profile_independent_geometry_sum",),
    ("d_decomposition_dimensionless", "profile_band_averaging"),
    ("d_decomposition_dimensionless", "center_variance_V_second"),
    ("d_decomposition_dimensionless", "implicit_root_delta_W_cross"),
    ("d_decomposition_dimensionless", "implicit_root_W_curvature"),
    ("d_dimensionless",),
)


def identity(path):
    content = path.read_bytes()
    return {"path": path.relative_to(PROJECT).as_posix(), "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest()}


def retained_value(affine, keys):
    value = affine
    for key in keys:
        value = value[key]
    if not isinstance(value, str):
        raise TypeError("Every displayed coefficient must be a retained raw string")
    return value


def render():
    if PNG.exists() or PROVENANCE.exists():
        raise FileExistsError("Preserve existing figure/source/provenance before another layout render")
    raw_path = PROJECT / RAW_RELATIVE
    raw_bytes = raw_path.read_bytes()
    if len(raw_bytes) != RAW_EXPECTED_BYTES or hashlib.sha256(raw_bytes).hexdigest() != RAW_EXPECTED_SHA256:
        raise ValueError("PHYS30 first raw identity mismatch")
    raw = json.loads(raw_bytes)
    if raw["status"] != "SCOPED_CACHED_ALGEBRA_PASS" or raw["summary"]["all_pass"] is not True:
        raise ValueError("Figure input is not the actual successful first raw")

    displayed = {}
    for branch in BRANCHES:
        displayed[branch] = {}
        for profile in PROFILES:
            affine = raw["profile_results"][profile]["branches"][branch]["affine"]
            displayed[branch][profile] = {
                "c_eV": affine["c_eV"],
                "values": [retained_value(affine, fields) for fields in FIELDS],
                "source_pointers": ["profile_results."+profile+".branches."+branch+".affine."+".".join(fields)
                                    for fields in FIELDS],
            }
        if displayed[branch]["uniform"]["c_eV"] != displayed[branch]["triangular"]["c_eV"]:
            raise ValueError("The common c subtitle requires identical retained strings")

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12,
        "axes.titlesize": 15, "axes.labelsize": 12, "xtick.labelsize": 11,
        "ytick.labelsize": 12, "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "mathtext.fontset": "dejavusans",
    })
    fig, axes = plt.subplots(1, 2, figsize=(15, 8.4), dpi=160, sharex=True, sharey=True)
    fig.subplots_adjust(left=0.18, right=0.985, bottom=0.18, top=0.75, wspace=0.13)
    for axis, branch in zip(axes, BRANCHES):
        axis.set_axisbelow(True)
        axis.axhspan(4.56, 5.44, color="#F0F3F7", zorder=0)
        axis.grid(axis="x", color="#DEE3EA", linewidth=0.8)
        axis.axvline(0, color="#45515E", linewidth=1.1, zorder=2)
        for profile, offset in (("uniform", -0.16), ("triangular", 0.16)):
            values = [float(value) for value in displayed[branch][profile]["values"]]
            bars = axis.barh([row+offset for row in range(6)], values, height=0.27,
                             color=COLORS[profile], zorder=3)
            bars[-1].set_edgecolor("#263440")
            bars[-1].set_linewidth(0.8)
            total = values[-1]
            axis.text(total+(0.055 if total >= 0 else -0.055), 5+offset,
                      format(total, "+.9f"), va="center",
                      ha="left" if total >= 0 else "right", color=COLORS[profile],
                      fontsize=11, fontweight="bold")
        axis.set_xlim(-1.12, 2.30)
        axis.set_xticks([-1, -0.5, 0, 0.5, 1, 1.5, 2])
        axis.set_ylim(5.62, -0.62)
        axis.set_yticks(range(6), LABELS)
        axis.tick_params(axis="y", length=0, pad=10)
        axis.tick_params(axis="x", length=4, color="#9CA8B6")
        for side in ("top", "right", "left"):
            axis.spines[side].set_visible(False)
        axis.spines["bottom"].set_color("#9CA8B6")
        axis.set_xlabel("Contribution to d  (dimensionless)", labelpad=14)
        heading = r"Upper-response threshold  $W_\star$" if branch == "upper_root" else r"Lower-response threshold  $W_0$"
        axis.set_title(heading, y=1.13, fontweight="bold")
        common_c = float(displayed[branch]["uniform"]["c_eV"])
        axis.text(0.5, 1.06, "Common c = "+format(common_c, "+.10f")+" eV",
                  transform=axis.transAxes, ha="center", va="bottom", color="#4B5663", fontsize=11)

    fig.suptitle("Profile dependence of the second-order threshold coefficient", y=0.972,
                 fontsize=19, fontweight="bold", color="#182532")
    fig.text(0.5, 0.923,
             r"Local $\delta\to0^+$ expansion:  $W=w+c\delta+d\delta^2+o(\delta^2)$;  $d=W''(0^+)/2$",
             ha="center", va="center", fontsize=12.5, color="#45515E")
    legend = [Patch(facecolor=COLORS["uniform"], label=r"Uniform profile  ($\mu_2=1/3$)"),
              Patch(facecolor=COLORS["triangular"], label=r"Triangular profile  ($\mu_2=1/6$)")]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.56, 0.882),
               ncol=2, frameon=False, fontsize=12, handlelength=1.8, columnspacing=3.0)
    fig.text(0.18, 0.078, "Fixed actual variance W; identical center interval [a + δ, b − δ] for both profiles.",
             fontsize=10.5, color="#45515E")
    fig.text(0.18, 0.045, "Retained numerical points and nonzero A levels. Finite-width root accuracy is not assessed.",
             fontsize=10.5, color="#45515E")
    fig.savefig(PNG, dpi=160, metadata={"Software": "Matplotlib cached-value display",
                                      "Description": "PHYS30 zero-width second-order coefficients; no finite-width inference"})
    plt.close(fig)

    provenance = {
        "task": "REI-PHYS30-20261011", "kind": "Cached-value scientific figure",
        "contributor": "/root/phys30_numerics", "role": "Numerical generator reused for display only; not final reviewer",
        "input": identity(raw_path), "source": identity(Path(__file__)), "output": identity(PNG),
        "matplotlib_version": matplotlib.__version__, "python_version": platform.python_version(),
        "pixels": [2400, 1344], "background": "opaque white", "displayed_raw_strings": displayed,
        "display_operation": "Read registered raw fields; direct float conversion and formatting for positions/text only",
        "formula_evaluation": "None. Geometry sum and total d are read from existing raw fields, not recomputed.",
        "axes": {"panels": 2, "common_xlim": [-1.12, 2.30], "zero_line": True,
                 "categories": list(LABELS), "uniform_mu2": "1/3", "triangular_mu2": "1/6"},
        "actual_scope_counters": {"figure_render_invocations_this_command": 1,
                                  "scientific_main": 0, "candidate_import": 0,
                                  "new_physical_kernel_or_derivative": 0, "new_physical_root": 0,
                                  "profile_moment_or_toy_evaluation": 0,
                                  "new_coefficient_formula_or_sum": 0},
        "claim_limits": ["Local zero-width same-level coefficients at retained numerical points",
                         "No finite-width root accuracy, error bound or valid-width window",
                         "Rounding and colors are display only; raw strings retain the numerical evidence"],
        "visual_review": "PENDING actual view_image; see separate FIGURE_VISUAL_REVIEW.json once observed",
    }
    with PROVENANCE.open("x", encoding="utf-8") as output:
        json.dump(provenance, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({"figure": identity(PNG), "provenance": identity(PROVENANCE),
                      "scientific_main": 0, "new_physical_evaluations": 0}, indent=2))


if __name__ == "__main__":
    render()
