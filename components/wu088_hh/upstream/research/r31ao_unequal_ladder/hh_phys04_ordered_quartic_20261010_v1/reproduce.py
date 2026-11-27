#!/usr/bin/env python3
"""Verify sealed bytes by default; explicitly replay only new PHYS04 checks."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent

def verify():
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    entries = manifest["files"]
    for row in entries:
        path = ROOT / row["path"]
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError("Manifest path escapes packet")
        raw = path.read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("Payload identity mismatch: " + row["path"])
    return len(entries)

def replay(out):
    out = out.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise ValueError("Replay workspace must be separate from packet")
    out.mkdir(parents=True, exist_ok=False)
    copied = [
        "quartic/ordered_be_quartic.py",
        "src/remap_opacity.py",
        "src/implicit_mixed.py",
        "tests/check_implicit_mixed.py",
        "inputs/SELECTED_SOURCE.json",
    ]
    for rel in copied:
        target = out / "workspace" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    base = out / "workspace"
    commands = [
        ("quartic", [sys.executable, "-B", str(base / copied[0]),
                     "--output", str(out / "quartic_result")]),
        ("remap", [sys.executable, "-B", str(base / copied[1]),
                   "--source", str(base / copied[4]),
                   "--output", str(out / "REMAP_OPACITY.json")]),
        ("implicit", [sys.executable, "-B", str(base / copied[3]),
                      "--output", str(out / "IMPLICIT_MIXED.json")]),
    ]
    ledger = []
    for name, command in commands:
        start = datetime.now(timezone.utc).isoformat()
        p = subprocess.run(command, cwd=base, capture_output=True)
        (out / (name + ".stdout")).write_bytes(p.stdout)
        (out / (name + ".stderr")).write_bytes(p.stderr)
        ledger.append({"name": name, "command": command, "start_utc": start,
                       "exit_code": p.returncode})
        (out / "REPLAY_RUN_LEDGER.json").write_text(json.dumps({
            "runs": ledger, "native_dispatches": 0, "old_science_runs": 0,
            "scope": "new PHYS04 algebra only"}, indent=2) + "\n")
        if p.returncode:
            raise RuntimeError("New PHYS04 check failed: " + name)
    return ledger

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--verify-only", action="store_true")
    group.add_argument("--run-new-checks", action="store_true")
    ap.add_argument("--out-dir", type=Path)
    ns = ap.parse_args()
    if ns.run_new_checks != (ns.out_dir is not None):
        ap.error("--run-new-checks and --out-dir must be used together")
    count = verify()
    runs = replay(ns.out_dir) if ns.run_new_checks else []
    print(json.dumps({"payloads_verified": count, "new_checks_executed": len(runs),
                      "native_dispatches": 0, "old_science_runs": 0}, indent=2))

if __name__ == "__main__":
    main()
