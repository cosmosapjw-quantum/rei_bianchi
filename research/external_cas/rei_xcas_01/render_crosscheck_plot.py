#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
receipts = root / "receipts"
external = root.parents[2] / "external-receipts"

records = {}
for name in ("octave_receipt.json", "jas_receipt.json", "julia_receipt.json"):
    candidates = list(external.rglob(name)) + list(root.parents[2].rglob(name))
    if not candidates:
        raise FileNotFoundError(name)
    data = json.loads(candidates[0].read_text())
    if data["status"] != "PASS":
        raise RuntimeError((name, data))
    records[name] = data

coverage_labels = [records[name]["tool"] for name in records]
coverage_values = [len(records[name].get("checks", {})) for name in records]
plot_dir = root / "plots"
plot_dir.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(8.0, 4.8))
ax.bar(coverage_labels, coverage_values)
ax.set_ylabel("independently executed checks")
ax.set_title("REI-XCAS-01 independent verification coverage")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(plot_dir / "external_cas_check_coverage.png", dpi=180)
plt.close(fig)

octave = records["octave_receipt.json"]
julia = records["julia_receipt.json"]
margin_rows = [
    ("GNU Octave", float(octave["max_abs_residual"]), float(octave["tolerance"])),
    ("Julia BigFloat", float(julia["max_bigfloat_residual"]), float(julia["bigfloat_tolerance"])),
]
with (plot_dir / "numerical_residual_margins.csv").open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["tool", "max_abs_residual", "tolerance", "ratio", "log10_ratio"])
    for label, residual, tolerance in margin_rows:
        ratio = residual / tolerance
        writer.writerow([label, residual, tolerance, ratio, math.log10(max(ratio, 1e-300))])

fig, ax = plt.subplots(figsize=(7.2, 4.8))
labels = [row[0] for row in margin_rows]
log_ratios = [math.log10(max(row[1] / row[2], 1e-300)) for row in margin_rows]
ax.bar(labels, log_ratios)
ax.axhline(0.0, linestyle="--", linewidth=1.2, label="declared tolerance")
ax.set_ylabel(r"$\log_{10}(\mathrm{max\ residual}/\mathrm{tolerance})$")
ax.set_title("REI-XCAS-01 numerical residual margins")
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(plot_dir / "numerical_residual_margins.png", dpi=180)
plt.close(fig)

summary = {
    "status": "PASS",
    "tools": {records[name]["tool"]: len(records[name].get("checks", {})) for name in records},
    "plots": [
        "plots/external_cas_check_coverage.png",
        "plots/numerical_residual_margins.png",
        "plots/numerical_residual_margins.csv"
    ],
    "numerical_margin_ratios": {
        label: residual / tolerance for label, residual, tolerance in margin_rows
    },
    "claim_boundary": "FORMULA_CROSSCHECK_PLOTS_NOT_PHYSICS_OR_SOLVER_COMPLETENESS",
}
receipts.mkdir(exist_ok=True)
(receipts / "aggregate_receipt.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
print(json.dumps(summary, sort_keys=True))
