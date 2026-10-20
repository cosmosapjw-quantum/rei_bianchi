#!/usr/bin/env python3
"""Summarize all recorded ABBA blocks without dropping slow observations."""
import csv
import json
import statistics
from pathlib import Path

root = Path(__file__).resolve().parent / "evidence"
rows = list(csv.DictReader((root / "BENCHMARK_ABBA.csv").open()))
result = {}
for candidate in dict.fromkeys(row["candidate"] for row in rows):
    subset = [row for row in rows if row["candidate"] == candidate]
    direct = [float(row["seconds"]) for row in subset if row["backend"] == "direct"]
    measured = [float(row["seconds"]) for row in subset if row["backend"] == candidate]
    paired = []
    for block in range(6):
        group = [row for row in subset if int(row["block"]) == block]
        assert [row["backend"] for row in group] == ["direct", candidate, candidate, "direct"]
        a = [float(row["seconds"]) for row in group if row["backend"] == "direct"]
        b = [float(row["seconds"]) for row in group if row["backend"] == candidate]
        paired.append(statistics.mean(a) / statistics.mean(b))
    result[candidate] = {
        "direct_median_seconds": statistics.median(direct),
        "candidate_median_seconds": statistics.median(measured),
        "ratio_of_medians": statistics.median(direct) / statistics.median(measured),
        "paired_speedup_median": statistics.median(paired),
        "paired_speedup_min": min(paired),
        "paired_speedup_max": max(paired),
        "timed_queries_per_run": 100000,
        "abba_blocks": 6,
        "warmup_queries_per_backend": 10000,
    }
(root / "BENCHMARK_SUMMARY.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
