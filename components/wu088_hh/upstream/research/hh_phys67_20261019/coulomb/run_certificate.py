#!/usr/bin/env python3
"""Regenerate only the bounded PHYS67 Coulomb point certificate."""
from pathlib import Path
import argparse
import json
import time

from wu088_hh.phys67_coulomb_certificate import certify_points

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--precision-bits", type=int, default=512)
args = parser.parse_args()
start = time.perf_counter()
receipt = certify_points(args.source, precision_bits=args.precision_bits)
receipt["elapsed_seconds"] = time.perf_counter() - start
receipt["execution"] = "completed"
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"execution": receipt["execution"], "points": receipt["point_count"],
                  "precision_bits": receipt["precision_bits"],
                  "seconds": receipt["elapsed_seconds"], "output": str(args.output)}))
