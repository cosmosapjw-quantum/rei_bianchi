#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
receipts = root / "receipts"
records = []
for name in ("octave_receipt.json", "jas_receipt.json", "julia_receipt.json"):
    matches = list(root.parent.parent.parent.rglob(name))
    if not matches:
        raise FileNotFoundError(name)
    data = json.loads(matches[0].read_text())
    if data["status"] != "PASS":
        raise RuntimeError((name, data))
    records.append((data["tool"], len(data.get("checks", {}))))

plot_dir = root / "plots"
plot_dir.mkdir(exist_ok=True)
labels = [item[0] for item in records]
values = [item[1] for item in records]
fig, ax = plt.subplots(figsize=(8.0, 4.8))
ax.bar(labels, values)
ax.set_ylabel("independently executed checks")
ax.set_title("REI-XCAS-01 independent verification coverage")
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(plot_dir / "external_cas_check_coverage.png", dpi=180)
plt.close(fig)

summary = {
    "status": "PASS",
    "tools": {label: count for label, count in records},
    "plot": "plots/external_cas_check_coverage.png",
    "claim_boundary": "CHECK_COVERAGE_PLOT_NOT_PHYSICS_COMPLETENESS",
}
(receipts / "aggregate_receipt.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
print(json.dumps(summary, sort_keys=True))
