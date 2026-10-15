#!/usr/bin/env python3
"""AX08 conditional actual-history plots; time-ordered and NOT an accuracy claim."""
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DIAG = HERE / "paired_diagnostic_001"
RECEIPT = json.loads((DIAG / "REDUCTION_RECEIPT.json").read_text())
MANIFEST = json.loads((HERE / "paired_manifest.json").read_text())
assert RECEIPT["status"] == "DIAGNOSTIC_REDUCTION_COMPLETE_RESPONSE_UNRESOLVED"
assert RECEIPT["scientific_admission"] == "NOT_ISSUED"
assert RECEIPT["grid_samples"] == 1001

paired = defaultdict(list)
with (DIAG / "sampled_comparisons.csv").open(newline="") as f:
    for row in csv.DictReader(f):
        if row["observable"] in ("x_HII", "Tgas_K", "U2_eV_per_H"):
            paired[row["observable"]].append(row)
fig, axes = plt.subplots(3, 2, figsize=(11, 10), constrained_layout=True)
units = {"x_HII": "HII / H", "Tgas_K": "Tgas [K]", "U2_eV_per_H": "U2 [eV/H]"}
for i, observable in enumerate(("x_HII", "Tgas_K", "U2_eV_per_H")):
    rows = paired[observable]
    assert len(rows) == 1001
    assert [int(r["sample"]) for r in rows] == list(range(1001))
    z = [float(r["candidate_zbar"]) for r in rows]
    y0 = [float(r["reference_value"]) for r in rows]
    yq = [float(r["candidate_value"]) for r in rows]
    delta = [float(r["difference"]) for r in rows]
    a, b = axes[i]
    a.plot(z, y0, label="ZERO (q=0)")
    a.plot(z, yq, label="SHEAR_HALF_PLUS (q=+0.005)", linestyle="--")
    b.plot(z, delta, label="q - ZERO")
    b.axhline(0, linewidth=.7, color="gray")
    floor = rows[0]["absolute_resolution_floor"]
    if floor != "":
        b.axhline(float(floor), linewidth=.7, linestyle=":", color="gray", label="Declared floor")
        b.axhline(-float(floor), linewidth=.7, linestyle=":", color="gray")
    a.set_ylabel(units[observable])
    b.set_ylabel("Difference: " + units[observable])
    a.set_xlabel("Mean redshift zbar (common ln a)")
    b.set_xlabel("Mean redshift zbar (common ln a)")
    a.invert_xaxis()
    b.invert_xaxis()
    a.legend(fontsize=8)
    b.legend(fontsize=8)
fig.suptitle("AX08 conditional +0.005 / ZERO, 1001 sampled points; NUMERICAL ERROR UNKNOWN", fontsize=12)
fig.savefig(HERE / "paired_sampled_diagnostics.png", dpi=175)
plt.close(fig)

path = ROOT / MANIFEST["candidate"]["history"]["path"]
hold = []
with path.open(newline="") as f:
    for i, row in enumerate(csv.DictReader(f)):
        if i % 80 == 0 or row["a"] == "0.2":
            hold.append(row)
assert len(hold) >= 3900
assert float(hold[0]["time_s"]) == 0
assert float(hold[-1]["a"]) == 0.2
assert all(float(v["time_s"]) < float(w["time_s"]) for v, w in zip(hold, hold[1:]))
tmyr = [float(r["time_s"]) / (365.25 * 86400 * 1e6) for r in hold]
tk = [float(r["temperature_K"]) for r in hold]
spec = (("x_HI", "x_HII"), ("x_HeI", "x_HeII", "x_HeIII"))
fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
for j, species in enumerate(spec):
    for name in species:
        y = [float(r[name]) for r in hold]
        axes[j, 0].plot(tmyr, y, label=name)
        # Keep chronological connection; never sort by nonmonotone gas temperature.
        axes[j, 1].plot(tk, y, label=name)
    axes[j, 0].set_xlabel("Elapsed proper time since zbar=20 [Myr]")
    axes[j, 1].set_xlabel("Gas temperature [K]; points joined in TIME order")
    axes[j, 0].set_ylabel("Element number fraction")
    axes[j, 1].set_ylabel("Element number fraction")
    axes[j, 0].legend()
    axes[j, 1].legend()
fig.suptitle("AX08 SHEAR_HALF_PLUS full H-He history (q_ref=+0.005); CONDITIONAL", fontsize=12)
fig.savefig(HERE / "half_plus_abundance_time_temperature.png", dpi=175)
plt.close(fig)
print(json.dumps({"status": "PLOTS_FROM_ACTUAL_AX08_COMPLETED_HISTORY", "chronological_samples": len(hold), "same_grid_comparison_samples": 1001, "scientific_admission": "NOT_ISSUED", "plots": ["paired_sampled_diagnostics.png", "half_plus_abundance_time_temperature.png"]}))
