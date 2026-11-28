#!/usr/bin/env python3
"""Preflight or explicitly execute the disjoint j=29..36 validated Born band.

Default: mathematical preflight only.  --run executes one bounded child.
Successful panels are hash-verified and reused with --resume.  The PHYS68
completed j=0..28 campaign is not a supported execution target.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))

from wu088_hh.phys69_band_profiles import (
    BandRequest, _canonical, _write_json, request_binding, preflight, run_band_profiles,
)
from phys68_ncp import campaign_lock, run_child, invocation_lines, new_child_invocation


def read_request(path=None):
    payload = json.loads(Path(path).read_text()) if path else asdict(BandRequest())
    if not isinstance(payload, dict) or set(payload) != set(asdict(BandRequest())):
        raise ValueError("complete BandRequest JSON fields required")
    return BandRequest(**payload).validate()


def inspect_output(output, binding, resume):
    output = Path(output)
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise ValueError("output must be an ordinary directory")
    fingerprint = hashlib.sha256(_canonical(binding)).hexdigest()
    if output.exists() and any(output.iterdir()):
        if not resume:
            raise FileExistsError("existing output: --resume is required")
        path = output/"REQUEST.json"
        if not path.exists():
            raise ValueError("nonempty output has no bound request")
        saved = json.loads(path.read_text())
        if (saved.get("schema") != "PHYS69_BAND_REQUEST_V1" or
                saved.get("fingerprint") != fingerprint or saved.get("binding") != binding):
            raise ValueError("output request/source/engine/runtime mismatch")
    return fingerprint


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT/"research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-new-panels", type=int)
    parser.add_argument("--wall-seconds", type=int, default=240)
    parser.add_argument("--memory-gib", type=int, default=4)
    parser.add_argument("--ncp-limits", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    request = read_request(args.request)
    started = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    begin = time.monotonic()
    binding = request_binding(args.source, request)
    fingerprint = hashlib.sha256(_canonical(binding)).hexdigest()
    if args.worker:
        try:
            result = run_band_profiles(args.source, args.out, request, args.resume,
                                       args.max_new_panels,
                                       lambda event: print(json.dumps({"event": "panel", **event}), flush=True))
            status = result["status"]
            code = 0 if status in ("CERTIFIED_BAND_NUMERICAL_GOAL_MET", "PARTIAL_CHECKPOINT_NO_FINAL_CERTIFICATE") else 2
            record = {"schema": "PHYS69_BAND_INVOCATION_V1", "started_utc": started,
                      "finished_utc": datetime.now(timezone.utc).isoformat(),
                      "elapsed_seconds": time.monotonic()-begin, "request": asdict(request),
                      "status": status, "fingerprint": fingerprint,
                      "computed": result["panels_computed_this_call"], "reused": result["panels_reused_this_call"],
                      "scientific_execution": result["scientific_execution"], "exit_code": code, "HH_R10": "OFF"}
        except Exception as exc:
            code = 1
            record = {"schema": "PHYS69_BAND_INVOCATION_V1", "started_utc": started,
                      "finished_utc": datetime.now(timezone.utc).isoformat(),
                      "elapsed_seconds": time.monotonic()-begin, "request": asdict(request),
                      "fingerprint": fingerprint, "status": "FAILED_NO_COMPLETION_CLAIM",
                      "error_type": type(exc).__name__, "error": str(exc), "exit_code": code, "HH_R10": "OFF"}
        if (args.out/"REQUEST.json").exists():
            with (args.out/"INVOCATIONS.jsonl").open("a") as stream:
                stream.write(json.dumps(record, sort_keys=True)+"\n")
        print(json.dumps(record, sort_keys=True), flush=True)
        return code

    if not args.run:
        record = preflight(args.source, request)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        path = args.out.parent/(args.out.name+".preflight."+stamp+".json")
        _write_json(path, record)
        print(json.dumps({"status": record["status"], "receipt": str(path),
                          "fingerprint": fingerprint, "radial_panels": 0, "HH_R10": "OFF"}), flush=True)
        return 0

    with campaign_lock(args.out.parent, fingerprint):
        inspect_output(args.out, binding, args.resume)
        parent = args.out.parent/(args.out.name+"_invocations")
        parent.mkdir(parents=True, exist_ok=True)
        request_path = parent/(stamp+".request.json")
        _write_json(request_path, asdict(request))
        command = [sys.executable, str(Path(__file__).resolve()), "--worker", "--source",
                   str(args.source.resolve()), "--out", str(args.out.resolve()),
                   "--request", str(request_path.resolve())]
        if args.resume:
            command.append("--resume")
        if args.max_new_panels is not None:
            command += ["--max-new-panels", str(args.max_new_panels)]
        previous = len(invocation_lines(args.out/"INVOCATIONS.jsonl"))
        logs = parent/stamp
        result = run_child(command, logs, args.wall_seconds, args.memory_gib, args.ncp_limits)
        invocation = new_child_invocation(args.out/"INVOCATIONS.jsonl", previous, fingerprint)
        record = {"schema": "PHYS69_BAND_WRAPPER_V1", "started_utc": started,
                  "finished_utc": datetime.now(timezone.utc).isoformat(), "binding": binding,
                  "fingerprint": fingerprint, "command": command, "child": result,
                  "appended_child_invocation": invocation, "NCP_submitted": False,
                  "HH_R10": "OFF"}
        _write_json(logs/"WRAPPER_RECEIPT.json", record)
        print(json.dumps(record, sort_keys=True), flush=True)
        success = (result["returncode"] == 0 and not result["timed_out"]
                   and invocation is not None and invocation.get("exit_code") == 0)
        return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
