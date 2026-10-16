"""Summarize independent mesh-axis endpoint changes without claiming convergence."""
import csv
import json
import sys
from pathlib import Path

rows = list(csv.DictReader(open(sys.argv[1], newline="")))
axes = {
    "source_age": ("age_panels", [8, 16, 32]),
    "angular": ("nmu", [8, 16, 32]),
    "source_spectral": ("source_spectral", [8, 16, 32]),
    "proper_time": ("time_steps", [32, 64, 128]),
    "transport_cells": ("cells", [16, 32, 64]),
}
observables = ["N", "U", "xHII", "xHeII", "xHeIII", "w", "photoHI", "photoHeI", "photoHeII", "rrHI", "rrHeI", "rrHeII", "ciHI", "ciHeI", "ciHeII"]
keys = ["nmu", "cells", "source_spectral", "time_steps", "age_panels"]
out = {}
for q in [-0.1, 0.0, 0.1]:
    subset = [r for r in rows if float(r["q"]) == q]
    base = next(r for r in subset if all(int(float(r[k])) == v for k, v in zip(keys, [8, 16, 8, 32, 8])))
    out[str(q)] = {}
    for name, (key, levels) in axes.items():
        series = []
        for lev in levels:
            found = [r for r in subset if int(float(r[key])) == lev and all(int(float(r[k])) == int(float(base[k])) for k in keys if k != key)]
            assert found, (q, name, lev)
            assert all(all(r[k] == found[0][k] for k in r) for r in found), (q, name, lev)
            series.append(found[0])
        out[str(q)][name] = {
            "levels": levels,
            "endpoint": {k: [float(r[k]) for r in series] for k in observables},
            "consecutive_absolute_changes": {k: [abs(float(series[i + 1][k]) - float(series[i][k])) for i in range(2)] for k in observables},
            "interpretation": "raw endpoint differences only; no independent continuum truth",
        }
Path(sys.argv[2]).write_text(json.dumps(out, indent=2) + "\n")
