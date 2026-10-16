"""Summarize native fixed-481-grid reference lanes from preserved result files."""
import csv
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
report = {"schema": "rei.bass.longstep.refined.v1", "root": str(root), "runs": {}, "series": {}}
for lane in ("refined_reference", "refined_cap_repair", "exact_endpoint_reference", "ultrafine_probe", "full_exp_reference"):
    base = root / lane
    if not (base / "exits.csv").exists():
        continue
    entries = []
    for row in csv.DictReader((base / "exits.csv").open()):
        key = f"{row['mode']}_{row['case']}_{row['steps']}"
        result = base / key / "output" / "result.json"
        obj = json.loads(result.read_text()) if result.exists() else None
        out = base / key / "output"
        owner_file = out / "owner_rates.json"
        owner = json.loads(owner_file.read_text()) if owner_file.exists() else None
        source_file = out / "source_time_check.txt"
        source_lines = dict(line.strip().split("=", 1) for line in source_file.open()
                            if "=" in line) if source_file.exists() else {}
        checks = {
            "exit_zero": row["exit_code"] == "0",
            "result_present": obj is not None,
            "owner_present": owner is not None,
            "source_time_present": bool(source_lines),
        }
        if obj is not None:
            checks.update({
                "grid_481": obj["grid_points"] == 481,
                "photon_ledger": abs(obj["photon_normalized"]) <= 1e-8,
                "energy_ledger": abs(obj["energy_normalized"]) <= 1e-8,
                "hamiltonian": obj["max_hamiltonian_normalized"] <= 3e-12,
                "raychaudhuri": obj["max_raychaudhuri_normalized"] <= 3e-12,
                "restart_exact": obj["restart_max_abs"] == 0,
                "clock_exact": obj["clock_residual_s"] == 0,
                "gas_physical": obj["temperature_k"] > 0 and all(0 <= obj[k] <= 1
                    for k in ("x_hii", "x_heii", "x_heiii")) and
                    obj["x_heii"] + obj["x_heiii"] <= 1,
            })
        if owner is not None:
            checks["owner_ledger"] = abs(owner["owner_normalized"]) <= 1e-12
        if source_lines:
            checks["midpoint_source_residual"] = abs(float(source_lines["max_source_residual_per_h"])) <= 1e-10
        if lane in ("exact_endpoint_reference", "ultrafine_probe") or \
            (lane == "full_exp_reference" and int(row["steps"]) >= 128):
            checks["exact_epoch"] = source_lines.get("exact_endpoint") == "true" and \
                source_lines.get("total_dln") == "4.00000000000000019e-4"
            if obj is not None and "target_a" in source_lines:
                checks["target_a_binary64"] = abs(obj["a"]-float(source_lines["target_a"])) <= 1e-17
        entries.append({**row, "key": key, "result": obj, "owner": owner,
                        "source_time": source_lines, "checks": checks,
                        "accepted": all(checks.values())})
    report["runs"][lane] = entries

for lane, entries in report["runs"].items():
    for case in ("COLD_FLRW", "SIGNED_MINUS"):
        for mode in ("original", "legacy_trace", "split_be", "uniform_birth", "full_exponential_frozen"):
            series = sorted((e for e in entries if e["case"] == case and e["mode"] == mode
                             and e["accepted"]), key=lambda e: int(e["steps"]))
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
report["acceptance"] = {lane: {"runs": len(entries),
    "accepted": sum(e["accepted"] for e in entries),
    "failed_keys": [e["key"] for e in entries if not e["accepted"]]}
    for lane, entries in report["runs"].items()}
out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(out, len(report["series"]), "series", sum(len(x) for x in report["runs"].values()), "runs")
