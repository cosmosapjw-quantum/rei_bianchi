#!/usr/bin/env python3
"""Produce the exact PHYS69 tail budget using saved PHYS68 evidence only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from wu088_hh import phys69_angular_tail as core


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists; preserve and reuse completed results")
    started = time.monotonic()
    result = {
        "schema": "PHYS69_ANGULAR_BOUND_APPLICATION_V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "certificate": core.bound_certificate(args.repo),
        "coarse_all_angular_D2": core.coarse_all_angular_from_saved(args.repo),
        "command": sys.argv, "python_version": platform.python_version(),
        "code_sha256": hashlib.sha256(Path(core.__file__).read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scientific_radial_integrations": 0, "NCP_submissions": 0,
        "HH_R10": "OFF", "elapsed_seconds": time.monotonic()-started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as out:
        json.dump(result, out, indent=2)
        out.write("\n")
    print(json.dumps({"status": "COMPLETE_EXACT_BOUND_APPLICATION", "output": str(args.output),
                      "minimum_L_for_angular_1e-63": result["certificate"]["minimum_L_for_angular_1e-63"],
                      "old_integrations_repeated": 0, "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
