#!/usr/bin/env python3
"""Display only: read completed exact-rational evidence, never evaluate a kernel/root."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[1]
raw_path = root / "contributions/numerics/FINITE_WIDTH_FIRST.json"
raw = json.loads(raw_path.read_text())
checks = {x["id"]: x for x in raw["checks"]}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.5), gridspec_kw={"width_ratios": [1.45, 1]})
fig.patch.set_facecolor("#f7f9fc")
colors = {"upper": "#146c94", "lower": "#a44c2b"}
display_rows = []
for ax in axes:
    ax.set_facecolor("#ffffff")
    ax.grid(axis="x", color="#e2e8f0", lw=0.8)
    ax.set_axisbelow(True)

for y, key in enumerate(["upper_1_100", "upper_1_50", "lower_1_100", "lower_1_50"]):
    row = raw["branches"][key]
    ev = checks["P32-BRANCH-" + key]["evidence"]
    lo, hi = [float(Fraction(x)) * 1e4 for x in ev["scaled_quartic_remainder_interval"]]
    actual_lo, actual_hi = [float(Fraction(x)) * 1e4 for x in row["scaled_difference_interval"]]
    center = (actual_lo + actual_hi) / 2
    d4 = float(Fraction(row["bounds"]["D4"])) * 1e4
    color = colors[row["branch"]]
    axes[0].hlines(y, lo, hi, color=color, lw=7, alpha=0.20)
    axes[0].plot([lo, hi], [y, y], "|", color=color, markersize=14)
    axes[0].plot(d4, y, "o", color="white", markeredgecolor=color, markersize=8, markeredgewidth=1.5)
    axes[0].plot(center, y, "D", color=color, markersize=5)
    display_rows.append({"case": key, "bound_scaled_1e4": [lo, hi],
                         "exact_interval_scaled_1e4_display": [actual_lo, actual_hi],
                         "D4_scaled_1e4_display": d4})
axes[0].set_yticks(range(4), ["Upper   δ = 0.01", "Upper   δ = 0.02",
                            "Lower   δ = 0.01", "Lower   δ = 0.02"])
axes[0].invert_yaxis()
axes[0].set_ylim(3.5, -0.65)
axes[0].set_xlabel(r"$10^4\,(W_p-W_u)/\delta^4$   (dimensionless)")
axes[0].set_title("Branch differences", loc="left", fontweight="bold", pad=16)

for y, tag in enumerate(["1_100", "1_50"]):
    row = raw["gaps"][tag]
    d4 = float(Fraction(row["D4_gap"])) * 1e4
    rem = float(Fraction(row["R_gap"])) * 1e4
    actual = [float(Fraction(x)) * 1e4 for x in row["scaled_gap_interval"]]
    axes[1].hlines(y, d4 - rem, d4 + rem, color="#6857a5", lw=7, alpha=0.20)
    axes[1].plot([d4 - rem, d4 + rem], [y, y], "|", color="#6857a5", markersize=14)
    axes[1].plot(d4, y, "o", color="white", markeredgecolor="#6857a5", markersize=8, markeredgewidth=1.5)
    axes[1].plot(sum(actual) / 2, y, "D", color="#6857a5", markersize=5)
    display_rows.append({"case": "gap_" + tag, "bound_scaled_1e4": [d4 - rem, d4 + rem],
                         "exact_interval_scaled_1e4_display": actual,
                         "D4_scaled_1e4_display": d4})
axes[1].set_yticks([0, 1], ["δ = 0.01", "δ = 0.02"])
axes[1].set_ylim(1.5, -0.65)
axes[1].set_xlabel(r"$10^4\,(\Gamma_p-\Gamma_u)/\delta^4$   (dimensionless)")
axes[1].set_title("Lower − upper gap change", loc="left", fontweight="bold", pad=16)
fig.suptitle("PHYS32  |  Exact rational finite-width toy", x=0.035, ha="left",
             y=0.98, fontsize=18, fontweight="bold", color="#17243a")
fig.text(0.035, 0.90, r"$k(X)=1+X^2-X^3/10+X^4/100$;  fixed nonzero $A_s$, actual variance $W$",
         fontsize=11, color="#42526b")
fig.text(0.035, 0.105, "Shaded bar: proven remainder bound     ○  Quartic coefficient     ◆  Exact root enclosure",
         fontsize=10.5, color="#334155")
fig.text(0.035, 0.053, "Root intervals are smaller than the markers. This is a dimensionless toy, not a physical-kernel certificate.",
         fontsize=10, color="#53627b")
fig.subplots_adjust(left=0.17, right=0.975, bottom=0.24, top=0.79, wspace=0.37)
png = root / "report/PHYS32_FINITE_WIDTH_BOUNDS.png"
svg = root / "report/PHYS32_FINITE_WIDTH_BOUNDS.svg"
fig.savefig(png, dpi=150, facecolor=fig.get_facecolor())
fig.savefig(svg, facecolor=fig.get_facecolor())
plt.close(fig)
record = {
    "task": raw["task"], "scope": "DISPLAY_ONLY_FROM_RECORDED_EXACT_FRACTIONS",
    "new_scientific_evaluations": 0, "new_kernel_or_root_calls": 0,
    "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    "display_transform": "Fraction to binary64 solely for figure positions; interval midpoint marked; x scale 1e4",
    "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "display_rows": display_rows,
    "outputs": [{"path": str(p.relative_to(root)), "bytes": p.stat().st_size,
                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in [png, svg]],
}
(root / "report/FIGURE_PROVENANCE.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"display_only": True, "outputs": record["outputs"]}, indent=2))
