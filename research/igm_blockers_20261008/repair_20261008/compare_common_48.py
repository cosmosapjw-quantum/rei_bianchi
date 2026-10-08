#!/usr/bin/env python3
"""Compare the completed tracked-stock 0.0008 horizon at k48/96/48."""
import json
import sys
from pathlib import Path

numeric = Path(__file__).resolve().parents[1] / "numeric"
sys.path.insert(0, str(numeric))
from igm_compare import compare_rows, read_csv  # noqa: E402

root = Path(__file__).resolve().parent
runs = root / "runs"
specs = {
    "coarse": ("coarse-energy-loss-final-b", 16, 48, "PHASE_15_16.json", "PHASE_16_48.json"),
    "fine": ("fine-energy-loss-final", 28, 96, "PHASE_24_28.json", "PHASE_28_96.json"),
    "tail": ("tail-energy-loss-final", 14, 48, "PHASE_12_14.json", "PHASE_14_48.json"),
}
rows = {
    label: read_csv(runs / run_name / f"endpoint_{end}.csv")
    for label, (run_name, _start, end, _prior_phase, _phase) in specs.items()
}
coarse_history = read_csv(runs / specs["coarse"][0] / "history_16_48.csv")
fine_history = read_csv(runs / specs["fine"][0] / "history_28_96.csv")[5::2]
tail_history = read_csv(runs / specs["tail"][0] / "history_14_48.csv")[2:]
if not (len(coarse_history) == len(fine_history) == len(tail_history) == 32):
    raise SystemExit("COMMON_HISTORY_ALIGNMENT")
results = {
    "temporal": compare_rows(coarse_history, fine_history),
    "tail": compare_rows(coarse_history, tail_history),
}

for label, (run_name, start, _end, prior_phase_name, phase_name) in specs.items():
    previous = read_csv(runs / run_name / f"endpoint_{start}.csv")[0]
    current = rows[label][0]
    phase = json.loads((runs / run_name / phase_name).read_text())
    prior_phase = json.loads((runs / run_name / prior_phase_name).read_text())
    # The receipt stores the source integral from the frozen initial epoch to
    # the phase endpoint.  A resumed suffix therefore owns the difference of
    # the two endpoint integrals, not the final cumulative value.
    source_n = phase["source_simpson128"] - prior_phase["source_simpson128"]
    source_e = source_n * phase["source_mean_energy_erg"]
    ratios = [
        abs(current["emitted_N"] - previous["emitted_N"] - source_n)
        / (1e-8 + 1e-3 * abs(source_n)),
        abs(current["emitted_E"] - previous["emitted_E"] - source_e)
        / (1e-20 + 1e-3 * abs(source_e)),
    ]
    results[label + "_source"] = {
        "ratios": ratios,
        "passed": max(ratios) <= 1.0,
        "original_allowance": True,
    }

results["passed"] = all(value["passed"] for value in results.values())
results["scope"] = "all 32 stored common rows through the tracked-stock 0.0008 horizon"
(root / "comparison_48.json").write_text(json.dumps(results, indent=2) + "\n")
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
