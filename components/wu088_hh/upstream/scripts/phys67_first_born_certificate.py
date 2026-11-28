#!/usr/bin/env python3
"""Bounded reproduction of the PHYS67 original m=0 first Born certificate.

Run with PYTHONPATH=src. An existing output is never silently overwritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

from wu088_hh.phys67_first_born import integrate_first_born


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ell", type=int, default=21)
    parser.add_argument("--ellprime", type=int, default=20)
    parser.add_argument("--outer", default="65")
    parser.add_argument("--precision-bits", type=int, default=256)
    parser.add_argument("--coefficient-bits", type=int, default=1024)
    parser.add_argument("--absolute-goal", default="1e-40")
    parser.add_argument("--relative-goal", default="1e-22")
    parser.add_argument("--eval-limit", type=int, default=5000)
    parser.add_argument("--panel-width", default="4")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; inspect/reuse the completed receipt or choose a new output")
    request = {name: getattr(args, name) for name in (
        "ell", "ellprime", "outer", "precision_bits", "coefficient_bits",
        "absolute_goal", "relative_goal", "eval_limit", "panel_width")}
    start = datetime.now(timezone.utc).isoformat()
    result = integrate_first_born(args.source, **request)
    root = Path(__file__).resolve().parents[1]
    files = ["src/wu088_hh/phys67_first_born.py", "src/wu088_hh/phys67_coulomb_certificate.py",
             "src/wu088_hh/phys66_radial_budget.py", "src/wu088_hh/phys65_exterior_bounds.py",
             "scripts/phys67_first_born_certificate.py"]
    result["execution"] = {"started_utc": start,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(), "request": request,
        "code_sha256": {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in files}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation preserves another producer's result if it appeared in the meantime.
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    print(json.dumps({"output": str(args.output), "actual_numerical_goal_met": result["actual_numerical_goal_met"],
        "function_evaluations": result["function_evaluations"], "wall_seconds": result["wall_seconds"],
        "HH_R10": "OFF"}))
    return 0 if result["actual_numerical_goal_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
