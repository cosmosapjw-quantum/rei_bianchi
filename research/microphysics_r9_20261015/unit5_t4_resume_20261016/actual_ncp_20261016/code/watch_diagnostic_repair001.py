#!/usr/bin/env python3
"""Run one supervised zero-action diagnostic recovery after the original receipt."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import t4_resume as t

OUT = Path("/root/REI_R9_UNIT5_RESUME_20261016T024854Z_99ca7c")
PKG = Path("/root/REI_R9_UNIT4_STAGE_Ma8caml9/REI_R9_UNIT4_T4_SPECTRAL_20261016")


def main() -> int:
    while not Path(str(OUT) + ".exit_code").exists():
        time.sleep(10)
    failed = json.loads((OUT / "receipt.json").read_text())
    if failed.get("status") != "failure" or "trapz" not in failed.get("traceback", ""):
        print("No targeted diagnostic recovery needed", flush=True)
        return 0
    assert failed["new_Hamiltonian_actions"] <= 70
    checkpoint = OUT / "checkpoint.npz"
    assert checkpoint.is_file()
    deadline = dt.datetime.fromisoformat(failed["new_allocation"]["absolute_deadline_utc"].replace("Z", "+00:00"))
    remaining = (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds()
    assert remaining > 0
    diagnostic_out = OUT / "diagnostic_repair001"
    diagnostic_out.mkdir(exist_ok=False)
    env = dict(os.environ, OMP_NUM_THREADS="12", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    command = [sys.executable, str(ROOT / "code/diagnostic_only_repair001.py"),
               "--receipt", str(PKG / "inputs/receipt.json"),
               "--data", str(PKG / "inputs/data.npz"),
               "--checkpoint", str(checkpoint),
               "--failed-run", str(OUT),
               "--out", str(diagnostic_out)]
    result = t.b.supervise(command, diagnostic_out, remaining, 24., env=env, headroom_gib=20.)
    print(json.dumps(result, indent=2), flush=True)
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
