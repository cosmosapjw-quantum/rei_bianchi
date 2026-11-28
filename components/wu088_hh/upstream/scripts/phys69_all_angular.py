#!/usr/bin/env python3
"""Assemble already saved PHYS68/69 results; performs no solver execution."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from wu088_hh.phys69_all_angular import assemble_saved, EXPECTED_BAND_SHA


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--band", type=Path, required=True)
    parser.add_argument("--band-certificate-sha256", default=EXPECTED_BAND_SHA)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; completed assembly is never overwritten")
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    t = time.monotonic()
    result = assemble_saved(args.repo, args.band, args.band_certificate_sha256)
    result["producer"] = {
        "started_utc": started, "elapsed_seconds": time.monotonic()-t,
        "python": sys.version, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256((ROOT/"src/wu088_hh/phys69_all_angular.py").read_bytes()).hexdigest(),
        "angular_bound_source_sha256": hashlib.sha256((ROOT/"src/wu088_hh/phys69_angular_tail.py").read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "result": result["result"]}, indent=2))
    return 0 if result["result"]["display_fixed_goal_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
