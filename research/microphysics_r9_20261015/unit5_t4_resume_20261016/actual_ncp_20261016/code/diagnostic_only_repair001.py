#!/usr/bin/env python3
"""Recover the Unit5 residual diagnostic from a saved checkpoint, without H actions."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import t4_resume as original
import t4_resume_diagnostic_repair001 as repaired


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--failed-run", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (24 * 1024**3, 24 * 1024**3))
    started = time.monotonic()
    failure = json.loads((args.failed_run / "receipt.json").read_text())
    assert failure["status"] == "failure" and "trapz" in failure["traceback"]
    assert failure["new_Hamiltonian_actions"] <= 70
    deadline = dt.datetime.fromisoformat(failure["new_allocation"]["absolute_deadline_utc"].replace("Z", "+00:00"))
    assert dt.datetime.now(dt.timezone.utc) < deadline
    args.out.mkdir(parents=True, exist_ok=True)
    assert not (args.out / "recovery_receipt.json").exists()
    source_hashes = {name: original.b.sha(ROOT / "code" / name) for name in
                     ("t4_resume.py", "t4_resume_diagnostic_repair001.py", "diagnostic_only_repair001.py")}
    _, _, _, ground, u, info = original.b.load_saved(args.receipt, args.data)
    state = original.load_checkpoint(args.checkpoint, ground, u, info["W"])
    assert state["length"] == 128 and state["metadata"]["new_Hamiltonian_actions"] == failure["new_Hamiltonian_actions"]
    checkpoint_hash = original.b.sha(args.checkpoint)
    diagnostic = repaired.residual_diagnostic(state["V"], state["KV"], u, info["W"])
    original.b.dump(args.out / "residual_summary.json", diagnostic.pop("summary"))
    original.b.save_npz(args.out / "residual.npz", **diagnostic)
    completed = dt.datetime.now(dt.timezone.utc)
    summary = {
        "status": "success" if completed < deadline else "partial",
        "scope": "diagnostic_recovered_after_original_failure",
        "source_hashes": source_hashes,
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_length": state["length"],
        "checkpoint_cached_validation": state["validation"],
        "H_actions_in_recovery": 0,
        "original_new_Hamiltonian_actions": failure["new_Hamiltonian_actions"],
        "original_receipt_sha256": original.b.sha(args.failed_run / "receipt.json"),
        "original_deadline_utc": failure["new_allocation"]["absolute_deadline_utc"],
        "completed_utc": completed.isoformat().replace("+00:00", "Z"),
        "within_original_deadline": completed < deadline,
        "wall_s": time.monotonic() - started,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "runtime": original.b.runtime(),
    }
    original.b.dump(args.out / "recovery_receipt.json", summary)
    original.b.dump(args.out / "receipt.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if completed < deadline else 1


if __name__ == "__main__":
    raise SystemExit(main())
