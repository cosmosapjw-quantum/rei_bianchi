#!/usr/bin/env python3
"""Bounded synthetic microbenchmark; does not establish physical/NCP speedup."""
import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_native import fixture, reference
from native_backend import native_info, prepare_element_kernel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=15)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 3 <= args.repeats <= 100:
        parser.error("repeats must be in [3,100]")
    inputs = fixture(14, 5, 193, 97)
    B, gaunt, vl, weights, kin, cent, ls = inputs
    prepared = prepare_element_kernel(B, gaunt, ls)
    baseline = reference(inputs)
    accelerated = prepared.blocks(vl, weights, kin, cent)
    scaled_difference = float(np.max(np.abs(accelerated-baseline))/max(1., np.max(np.abs(baseline))))
    if scaled_difference >= 2e-14:
        raise ArithmeticError("kernel benchmark agreement criterion failed")
    # Alternate measurements; report every sample so host contention is visible.
    samples = {"numpy_seconds": [], "native_seconds": []}
    for _ in range(args.repeats):
        start = time.perf_counter(); reference(inputs)
        samples["numpy_seconds"].append(time.perf_counter()-start)
        start = time.perf_counter(); prepared.blocks(vl, weights, kin, cent)
        samples["native_seconds"].append(time.perf_counter()-start)
    median_numpy = statistics.median(samples["numpy_seconds"])
    median_native = statistics.median(samples["native_seconds"])
    result = {
        "scope": "synthetic element only; shared local runtime, not NCP64 or eigensolver speedup",
        "shape": {"nq": 14, "na": 5, "nk": 193, "nl": 97},
        "gaunt_nonzero_fraction": float(np.count_nonzero(gaunt)/gaunt.size),
        "max_scaled_numpy_difference": scaled_difference,
        "repeats": args.repeats, "samples": samples,
        "median_numpy_seconds": median_numpy, "median_native_seconds": median_native,
        "median_ratio_numpy_over_native": median_numpy/median_native,
        "native": native_info(),
        "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
        "python": sys.version, "numpy": np.__version__,
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
