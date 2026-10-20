#!/usr/bin/env python3
"""Independent SciPy PCHIP and Decimal-Hermite verification of Rust coefficients.

Original physical source values are inputs, not independently re-fitted here.
The independent oracle checks the numerical receiver, fallback and positivity.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


def relative(a: float, b: float) -> float:
    return abs(b / a - 1.0) if a else (0.0 if b == 0.0 else math.inf)


def decimal_hermite(values: np.ndarray, i: int, j: int, theta: float) -> float:
    def exact(v: float) -> Decimal:
        return Decimal.from_float(float(v))

    def harmonic(a: Decimal, b: Decimal) -> Decimal:
        if a == 0 or b == 0 or (a > 0) != (b > 0):
            return Decimal(0)
        return 2 * a * b / (a + b)

    with localcontext() as context:
        context.prec = 60
        q = exact(theta)
        ym, y0, y1, yp = [exact(values[k, j]) for k in range(i - 1, i + 3)]
        m0 = harmonic(y0 - ym, y1 - y0)
        m1 = harmonic(y1 - y0, yp - y1)
        h00 = 2 * q**3 - 3 * q**2 + 1
        h10 = q**3 - 2 * q**2 + q
        h01 = -2 * q**3 + 3 * q**2
        h11 = q**3 - q**2
        return float(h00 * y0 + h10 * m0 + h01 * y1 + h11 * m1)


def main() -> None:
    grids: dict[int, np.ndarray] = {}
    interpolators: dict[int, PchipInterpolator] = {}
    for nodes in (1025, 2049, 4097, 8193):
        grid = np.genfromtxt(EVIDENCE / f"NODES_{nodes}.csv", delimiter=",", names=True)
        values = np.column_stack([grid[f"c{i}"] for i in range(15)])
        grids[nodes] = values
        # SciPy computes actual cell widths from the printed x_i coordinates.
        # Rust uses the mathematically uniform-grid harmonic mean explicitly.
        interpolators[nodes] = PchipInterpolator(grid["log_t"], values, axis=0)

    metrics = defaultdict(lambda: {"samples": 0, "fallback_samples": 0,
        "scipy_max_relative": 0.0, "decimal_max_relative": 0.0,
        "positive_samples": 0, "zero_samples": 0, "fallback_bit_mismatches": 0})
    with (EVIDENCE / "INDEPENDENT_SAMPLES.csv").open() as stream:
        for row in csv.DictReader(stream):
            nodes, j, i = int(row["nodes"]), int(row["channel"]), int(row["cell"])
            t, theta = float(row["temperature_k"]), float(row["theta"])
            direct, compact = float(row["direct"]), float(row["compact"])
            metric = metrics[nodes]
            metric["samples"] += 1
            assert math.isfinite(compact) and compact >= 0.0
            metric["positive_samples"] += int(compact > 0.0)
            metric["zero_samples"] += int(compact == 0.0)
            if row["fallback"] == "true":
                metric["fallback_samples"] += 1
                metric["fallback_bit_mismatches"] += int(compact.hex() != direct.hex())
                continue
            scipy_value = float(interpolators[nodes](math.log(t))[j])
            decimal_value = decimal_hermite(grids[nodes], i, j, theta)
            metric["scipy_max_relative"] = max(metric["scipy_max_relative"], relative(compact, scipy_value))
            metric["decimal_max_relative"] = max(metric["decimal_max_relative"], relative(compact, decimal_value))
    for value in metrics.values():
        assert value["fallback_bit_mismatches"] == 0
        assert value["scipy_max_relative"] < 1e-11, value
        assert value["decimal_max_relative"] < 3e-14, value

    with (EVIDENCE / "RESOLUTION_SCAN.csv").open() as stream:
        scan = list(csv.DictReader(stream))
    recommended = next(row for row in scan if row["nodes"] == "8193")
    assert float(recommended["max_relative_error"]) < 1e-4
    summary = {
        "status": "PASS",
        "oracle_scope": "Numerical interpolation and direct fallback; physical coefficients supplied by immutable source owner.",
        "precision": "Decimal60 using exact binary64 inputs and independent Hermite basis; SciPy PCHIP uses independent implementation and actual printed lnT widths.",
        "scipy_relative_tolerance": 1e-11,
        "decimal_relative_tolerance": 3e-14,
        "resolutions": dict(metrics),
        "selected_nodes": 8193,
        "sampled_error_target": 1e-4,
        "sampled_error_selected": float(recommended["max_relative_error"]),
        "universal_error_bound_claimed": False,
        "coarse_resolution_target_misses": [1025, 2049, 4097],
    }
    (EVIDENCE / "INDEPENDENT_PCHIP_VERIFICATION.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
