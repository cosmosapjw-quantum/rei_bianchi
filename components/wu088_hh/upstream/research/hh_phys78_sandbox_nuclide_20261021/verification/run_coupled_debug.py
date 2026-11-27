"""Record the authorized single coupled control without changing its solver.

Every invocation uses a new exclusive trial directory. A failure receipt keeps
the last evaluated state; a success can be adopted by run_pilot without replay.
The wrapper is persistence/instrumentation only and is outside scientific code.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"

HERE = Path(__file__).resolve().parent
UNIT = HERE.parent / "phys78_impl"
sys.path.insert(0, str(UNIT / "source"))

import numpy as np
from run_pilot import scientific_manifest, identity
from coupled_model import solve_case


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+"\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    case = {"id": "coupled_debug_baseline", "sigma0_F_signed": 0.,
            "A_m": 0., "A_r": 0., "uv_scale": 1.}
    options = {"rtol": 2e-7, "resolution": None, "samples": 161}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    target = HERE / "coupled_trials" / stamp
    target.mkdir(parents=True, exist_ok=False)
    manifest = scientific_manifest()
    science_id, binding = identity(case, options, manifest)
    dump(target / "EXECUTION_SOURCE_MANIFEST.json", manifest)
    for relative, expected in manifest["files"].items():
        snapshot = target / "SOURCE_SNAPSHOT" / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(UNIT / relative, snapshot)
        if digest(snapshot) != expected:
            raise RuntimeError("SOURCE_CHANGED_WHILE_SNAPSHOTTING:" + relative)
    dump(target / "INPUT.json", {"case": case, "options": options,
                                "science_id": science_id, "binding": binding})
    print(json.dumps({"event": "START", "trial": str(target), "science_id": science_id}), flush=True)
    start = time.monotonic()
    try:
        arrays, metadata = solve_case(case, **options)
        np.savez_compressed(target / "CONTROL.npz", **arrays)
        dump(target / "METADATA.json", metadata)
        after = scientific_manifest()
        dump(target / "SOURCE_MANIFEST_AFTER.json", after)
        receipt = {"status": "COMPLETED_EXPLORATORY", "trial": str(target),
                   "science_id": science_id, "new_control_ode_calls": 1,
                   "wall_s_including_postflight": time.monotonic()-start,
                   "source_unchanged_during_execution": manifest == after,
                   "npz_sha256": digest(target / "CONTROL.npz"),
                   "metadata_sha256": digest(target / "METADATA.json"),
                   "checks": metadata["checks"], "HH_R10": "OFF",
                   "production_admission": False}
        dump(target / "RECEIPT.json", receipt)
        print(json.dumps(receipt), flush=True)
        return 0
    except Exception as error:
        frames = []
        tb = error.__traceback__
        while tb is not None:
            frames.append(tb.tb_frame)
            tb = tb.tb_next
        model = next((frame.f_locals["model"] for frame in frames
                      if "model" in frame.f_locals and hasattr(frame.f_locals["model"], "last_state")), None)
        state_details = {}
        if model is not None:
            if model.last_state is not None:
                np.savez_compressed(target / "LAST_RHS_STATE.npz",
                                    x=np.array(model.last_x), state=model.last_state,
                                    initial_state=model.initial_state)
            state_details = {"last_rhs_x": model.last_x,
                             "rhs_calls_including_jacobian": model.rhs_calls,
                             "negative_solver_stage_evaluations": model.negative_stage_count}
        after = scientific_manifest()
        dump(target / "SOURCE_MANIFEST_AFTER.json", after)
        receipt = {"status": "FAILED", "trial": str(target),
                   "science_id": science_id, "new_control_ode_calls": 1,
                   "wall_s": time.monotonic()-start, "error": repr(error),
                   "traceback": traceback.format_exc(),
                   "source_unchanged_during_execution": manifest == after,
                   **state_details, "HH_R10": "OFF", "production_admission": False}
        dump(target / "FAILED.json", receipt)
        print(json.dumps(receipt), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
