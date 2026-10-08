#!/usr/bin/env python3
"""Compare the tracked-stock repair at the common k17/34/17 epoch."""
import json
import sys
from pathlib import Path

numeric = Path(__file__).resolve().parents[1] / "numeric"
sys.path.insert(0, str(numeric))
from igm_compare import compare_rows, read_csv  # noqa: E402

root = Path(__file__).resolve().parent
runs = root / "runs"
coarse = read_csv(runs / "coarse-tracked-stock-k17n" / "endpoint_17.csv")
fine = read_csv(runs / "fine-tracked-stock-k34" / "endpoint_34.csv")
tail = read_csv(runs / "tail-tracked-stock-k17" / "endpoint_17.csv")
results = {
    "temporal": compare_rows(coarse, fine),
    "tail": compare_rows(coarse, tail),
}

old = Path(
    "/home/cosmosapjw/Documents/Codex/2026-10-07/task-4/"
    "duration-unprojected-20261008/progressive-support"
)
for label, folder, row, old_k, run_name, phase_name in [
    ("coarse", "h0008-coarse", coarse[0], 9, "coarse-tracked-stock-k17n", "PHASE_16_17.json"),
    ("fine", "h0008-fine-diagnostic", fine[0], 18, "fine-tracked-stock-k34", "PHASE_28_34.json"),
    ("tail", "h0008-tail-diagnostic", tail[0], 9, "tail-tracked-stock-k17", "PHASE_14_17.json"),
]:
    original = json.loads((old / folder / f"PHASE_{old_k}_{old_k}.json").read_text())
    history = list((old / folder).glob("history_0_*.csv"))[0]
    previous = read_csv(history)[-1]
    base_n = previous["emitted_N"] - original["incremental_emitted_N"]
    base_e = previous["emitted_E"] - original["incremental_emitted_E"]
    phase = json.loads((runs / run_name / phase_name).read_text())
    source_n = phase["source_simpson128"]
    source_e = source_n * phase["source_mean_energy_erg"]
    ratios = [
        abs(row["emitted_N"] - base_n - source_n) / (1e-8 + 1e-3 * abs(source_n)),
        abs(row["emitted_E"] - base_e - source_e) / (1e-20 + 1e-3 * abs(source_e)),
    ]
    results[label + "_source"] = {
        "ratios": ratios,
        "passed": max(ratios) <= 1.0,
        "original_allowance": True,
    }

results["passed"] = all(value["passed"] for value in results.values())
results["scope"] = "tracked-stock repaired common epoch k17/34/17 only"
(root / "comparison_17.json").write_text(json.dumps(results, indent=2) + "\n")
print(
    json.dumps(
        {
            "passed": results["passed"],
            "worst_temporal": max(
                value["max_allowance_ratio"]
                for value in results["temporal"]["fields"].values()
            ),
            "worst_tail": max(
                value["max_allowance_ratio"]
                for value in results["tail"]["fields"].values()
            ),
            "source": [
                results[key + "_source"]["ratios"]
                for key in ("coarse", "fine", "tail")
            ],
        }
    )
)
raise SystemExit(0 if results["passed"] else 1)
