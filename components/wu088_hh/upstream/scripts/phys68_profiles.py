#!/usr/bin/env python3
"""Execute the complete validated profile/second-Born runner (no NCP solver design)."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from wu088_hh.phys68_profiles import ProfileRequest, run_profiles


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--request", type=Path, help="JSON object with exact ProfileRequest fields")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--max-new-panels", type=int, help="checkpoint after this many new panels; zero verifies stored panels")
    args = p.parse_args(argv)
    request = ProfileRequest(**json.loads(args.request.read_text())) if args.request else ProfileRequest()
    start = datetime.now(timezone.utc).isoformat()
    monotonic = time.monotonic()
    def progress(value):
        print(json.dumps({"event": "panel", **value}), flush=True)
    try:
        result = run_profiles(args.source, args.out, request, args.resume, args.max_new_panels, progress)
        status = result["status"]
        code = 0 if status in ("CERTIFIED_GOALS_MET", "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE") else 2
        record = {"schema": "PHYS68_PROFILE_INVOCATION_V1", "started_utc": start,
                  "finished_utc": datetime.now(timezone.utc).isoformat(),
                  "elapsed_seconds": time.monotonic()-monotonic, "request": asdict(request),
                  "status": status, "fingerprint": result["fingerprint"],
                  "computed": result["panels_computed_this_call"], "reused": result["panels_reused_this_call"],
                  "scientific_execution": result["scientific_execution"], "exit_code": code, "HH_R10": "OFF"}
    except Exception as exc:
        record = {"schema": "PHYS68_PROFILE_INVOCATION_V1", "started_utc": start,
                  "finished_utc": datetime.now(timezone.utc).isoformat(),
                  "elapsed_seconds": time.monotonic()-monotonic, "request": asdict(request),
                  "status": "FAILED_NO_COMPLETION_CLAIM", "error_type": type(exc).__name__,
                  "error": str(exc), "exit_code": 1, "HH_R10": "OFF"}
        code = 1
    args.out.mkdir(parents=True, exist_ok=True)
    # Append invocation evidence instead of replacing the original compute receipt on resume.
    with (args.out/"INVOCATIONS.jsonl").open("a") as stream:
        stream.write(json.dumps(record, sort_keys=True)+"\n")
    print(json.dumps(record, sort_keys=True), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
