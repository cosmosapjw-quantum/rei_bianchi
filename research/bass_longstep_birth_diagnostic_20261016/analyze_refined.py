"""Summarize native fixed-481-grid reference lanes from preserved result files."""
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
report = {"schema": "rei.bass.longstep.refined.v1", "root": str(root), "runs": {}, "series": {}}
for lane in ("refined_reference", "refined_cap_repair", "exact_endpoint_reference"):
    base = root / lane
    if not (base / "exits.csv").exists():
        continue
    entries = []
    for row in csv.DictReader((base / "exits.csv").open()):
        key = f"{row['mode']}_{row['case']}_{row['steps']}"
        result = base / key / "output" / "result.json"
        obj = json.loads(result.read_text()) if result.exists() else None
        entries.append({**row, "key": key, "result": obj})
    report["runs"][lane] = entries

for lane, entries in report["runs"].items():
    for case in ("COLD_FLRW", "SIGNED_MINUS"):
        for mode in ("original", "legacy_trace", "split_be", "uniform_birth"):
            series = sorted((e for e in entries if e["case"] == case and e["mode"] == mode
                             and e["result"] is not None), key=lambda e: int(e["steps"]))
            if not series:
                continue
            values = {field: {e["steps"]: e["result"][field] for e in series}
                      for field in ("a", "time_s", "temperature_k", "x_hii", "x_heii", "x_heiii",
                                    "source_n_per_h", "source_u_ev_per_h", "photon_normalized",
                                    "energy_normalized", "restart_max_abs")}
            ratios = {}
            for field in ("temperature_k", "source_n_per_h", "x_hii"):
                y = [e["result"][field] for e in series]
                n = [int(e["steps"]) for e in series]
                ratios[field] = {f"{n[i-2]}/{n[i-1]}/{n[i]}":
                                 (y[i-2]-y[i-1])/(y[i-1]-y[i]) if y[i-1] != y[i] else None
                                 for i in range(2, len(series))}
            report["series"][f"{lane}:{mode}:{case}"] = {
                "steps": [int(e["steps"]) for e in series], "values": values, "ratios": ratios,
                "max_abs_photon_normalized": max(abs(e["result"]["photon_normalized"]) for e in series),
                "max_abs_energy_normalized": max(abs(e["result"]["energy_normalized"]) for e in series),
                "max_restart_abs": max(e["result"]["restart_max_abs"] for e in series),
            }

out = root / "REFINED_ANALYSIS.json"
out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(out, len(report["series"]), "series", sum(len(x) for x in report["runs"].values()), "runs")
