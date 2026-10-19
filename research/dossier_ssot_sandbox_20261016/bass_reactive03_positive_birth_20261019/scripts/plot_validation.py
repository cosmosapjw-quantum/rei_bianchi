#!/usr/bin/env python3
"""Scientific figures from verified CSV/JSON; no fitted trends or error claims."""
from pathlib import Path
import csv
import json
import math
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "rei_ap_matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np

root = Path(__file__).resolve().parents[1]
out = root / "figures"
out.mkdir(exist_ok=True)
science = json.loads((root / "evidence/SCIENCE_RESULTS.json").read_text())
legacy = json.loads((root / "evidence/parent_comparison/SCIENCE_RESULTS.json").read_text())
with (root / "evidence/independent_theory/RESTORED_SOURCE_FROZEN_GRID.csv").open() as handle:
    frozen = list(csv.DictReader(handle))
with (root / "evidence/frozen/AP_RULE_NODES.csv").open() as handle:
    nodes = list(csv.DictReader(handle))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 11,
                     "legend.frameon": False, "savefig.dpi": 180})
fig, axes = plt.subplots(2, 2, figsize=(12, 8.3))
colors = {"gl2": "#BE4D45", "gl4": "#CB892A", "ap": "#13766D", "blue": "#336DA8"}
nt = [16, 32, 64, 128]

ax = axes[0, 0]
for r, label, color in [(2, "Legacy GL2", colors["gl2"]), (4, "Legacy GL4", colors["gl4"])]:
    rows = [x for x in frozen if x["method"] == "legacy_gl" and int(x["refinement"]) == r]
    rows.sort(key=lambda x: int(x["nsteps"]))
    ax.plot([int(x["nsteps"]) for x in rows],
            [100 * float(x["survivor_relative_error"]) for x in rows], "o-", color=color, label=label)
ax.plot(nt, [0] * 4, "s-", color=colors["ap"], label="Positive fitted birth, r=2")
ax.set(xscale="log", xticks=nt, xticklabels=[str(n) for n in nt], ylim=(-102, 7),
       xlabel="Macrosteps, $N_t$", ylabel="Survivor bias against exact frozen solution (%)",
       title="A  Frozen source / opacity: count accuracy")
ax.legend(loc="lower right", fontsize=9)
ax.xaxis.set_minor_locator(NullLocator())
ax.grid(alpha=.15)

ax = axes[0, 1]
y = np.linspace(0, 6, 600)
ax.plot(y, -np.expm1(-y) / (-math.expm1(-93.0)), color="#333333", lw=2, label="Exact conditional CDF")
for r, color in [(1, colors["gl2"]), (8, colors["ap"])]:
    rule = sorted([(93 * float(x["age_fraction"]), float(x["emission_weight"])) for x in nodes
                   if float(x["tau"]) == 93.0 and int(x["refinement"]) == r])
    ys = np.array([x for x, _ in rule])
    masses = np.array([w * math.exp(-x) for x, w in rule])
    masses /= sum(masses)
    ax.step(np.r_[0, ys, 93], np.r_[0, np.cumsum(masses), 1], where="post",
            color=color, label=f"Finite cohorts, r={r}")
ax.set(xlim=(0, 6), ylim=(0, 1.03), xlabel="Scaled survivor age, $y=\\kappa A$",
       ylabel="Conditional cumulative probability", title="B  $\\tau=93$: age distribution remains discrete")
ax.legend(loc="lower right", fontsize=9)
ax.grid(alpha=.15)

ax = axes[1, 0]
new_counts = [science["finals"][f"ap_n{n}_r2"]["photons_com3"] for n in nt]
old_counts = [legacy["finals"][f"time{n}"]["photons_com3"] for n in nt]
ax.plot(nt, np.array(old_counts) / 1e-8, "o-", color=colors["gl2"], label="Legacy GL2 (parent data)")
ax.plot(nt, np.array(new_counts) / 1e-8, "s-", color=colors["ap"], label="Positive fitted birth, r=2")
ax.set(xscale="log", xticks=nt, xticklabels=[str(n) for n in nt], ylim=(0, 1.09),
       xlabel="Macrosteps, $N_t$", ylabel="$N_{\\gamma,\\mathrm{surv}}$ [$10^{-8}\\,\\mathrm{m}_{com}^{-3}$]",
       title="C  Evolving native H/He/D: survivor count")
ax.text(.04, .56, "No exact evolving reference is assumed", transform=ax.transAxes, fontsize=9)
ax.legend(loc="lower right", fontsize=9)
ax.xaxis.set_minor_locator(NullLocator())
ax.grid(alpha=.15)

ax = axes[1, 1]
time_mean = science["independent_axes"]["time_r2"]["mean_age_s"]["successive_relative_changes"]
birth_mean = science["independent_axes"]["birth_n32"]["mean_age_s"]["successive_relative_changes"]
ax.loglog([2, 4, 8], np.abs(time_mean), "o-", color=colors["blue"], label="Time: $N_t$ 16 to 128; r=2")
ax.loglog([2, 4, 8], np.abs(birth_mean), "s-", color=colors["ap"], label="Birth: r 1 to 8; $N_t$=32")
ax.set(xticks=[2, 4, 8], xticklabels=["2", "4", "8"],
       xlabel="Refinement factor from the coarsest grid",
       ylabel="Successive mean-age change, $|\\Delta\\mu/\\mu_{prev}|$",
       title="D  Mean-age accuracy requires a separate check")
ax.legend(loc="upper right", fontsize=9)
ax.xaxis.set_minor_locator(NullLocator())
ax.grid(which="both", alpha=.15)
fig.suptitle("BASS-REACTIVE-03 | Positive optically thick photon births", fontsize=16, weight="bold", y=.985)
fig.text(.075, .022, "$T=8\\times10^{12}$ s. Panels A/B: frozen benchmarks. Panels C/D: one-way BASS background.\n"
         "Count exactness and small conservation residuals do not certify complete age, time, spectral or angular convergence.",
         fontsize=9, va="bottom")
fig.tight_layout(rect=(.025, .08, .99, .96), h_pad=2.8, w_pad=2.2)
fig.savefig(out / "BIRTH_INTEGRATION_VALIDATION.png")
fig.savefig(out / "BIRTH_INTEGRATION_VALIDATION.pdf")
plt.close(fig)
(out / "FIGURE_DATA.json").write_text(json.dumps({"time_grid": nt, "new_counts": new_counts,
    "legacy_counts": old_counts, "native_time_mean_successive_relative_changes": time_mean,
    "native_birth_mean_successive_relative_changes": birth_mean,
    "scope": "Four panels use distinct benchmark assumptions, labelled explicitly. No curve is a convergence fit."}, indent=2) + "\n")
print("Saved PNG, PDF, and exact figure data")
