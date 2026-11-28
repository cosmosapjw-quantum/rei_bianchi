#!/usr/bin/env python3
"""Run the reproducible PHYS34 certified *broken bulk* radial envelope."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from wu088_hh.phys33_residual import bound_broken_bulk


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=ROOT / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--subcells", type=int, default=16)
    p.add_argument("--partition", choices=["geometric", "uniform"], default="geometric")
    p.add_argument("--output", type=Path, required=True, help="new JSON file; never overwritten")
    args = p.parse_args()
    started = time.monotonic()
    result = bound_broken_bulk(args.input, subcells=args.subcells, partition=args.partition)
    result["elapsed_s"] = time.monotonic() - started
    result["python_command"] = [str(Path(__file__).relative_to(ROOT)),
                                "--input", str(args.input), "--subcells", str(args.subcells),
                                "--partition", args.partition, "--output", str(args.output)]
    result["implementation_sha256"] = hashlib.sha256((ROOT / "src/wu088_hh/phys33_residual.py").read_bytes()).hexdigest()
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "seconds": result["elapsed_s"],
                      "bound": result["norm_upper"], "source_sha256": result["source_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
