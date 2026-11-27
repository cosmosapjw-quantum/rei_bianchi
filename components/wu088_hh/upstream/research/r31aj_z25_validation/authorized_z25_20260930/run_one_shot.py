"""Run the two approved producer stages once with durable checkpoint evidence."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME = Path("/root/WU088_R31AJ_Z25_RUNTIME_20260930")
PY = "/root/wu088_hh_ncp_work_v2/venv/bin/python"
LEDGER = HERE / "ONE_SHOT_LEDGER.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main() -> None:
    lock = json.loads((HERE / "PRE_OUTPUT_LOCK.json").read_text())
    ledger = json.loads(LEDGER.read_text())
    if ledger["one_shot_state"] != "AUTHORIZED_PRE_OUTPUT" or ledger["science_commands_started"] != 0:
        raise RuntimeError("one-shot already started or consumed")
    if sha(REPO / "research/r31aj_z25_validation/compare_z25.py") != lock["comparator_sha256"]:
        raise RuntimeError("comparator changed")
    if sha(REPO / lock["prediction_arrays_path"]) != lock["prediction_arrays_sha256"]:
        raise RuntimeError("predictions changed")
    for rel, expected in lock["producer_source_sha256"].items():
        if sha(RUNTIME / rel) != expected:
            raise RuntimeError("producer source changed: " + rel)
    od_dir = RUNTIME / "completion/mixed_h/od/B192_z2.5"
    jvp_dir = RUNTIME / "completion/mixed_derivative/B192_z2.5"
    if od_dir.exists() or jvp_dir.exists():
        raise RuntimeError("existing direct output")
    stages = [
        ("OD", [PY, "completion/mixed_h/od_run.py", "--n", "192", "--z", "2.5", "--workers", "1"], od_dir),
        ("JVP", [PY, "completion/mixed_derivative/run.py", "--z", "2.5", "--n", "192"], jvp_dir),
    ]
    env = {**os.environ, "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    for name, argv, folder in stages:
        ledger["science_commands_started"] += 1
        ledger["one_shot_state"] = "STAGE_RUNNING"
        ledger["current_stage"] = name
        ledger["current_stage_started_utc"] = now()
        write(LEDGER, ledger)
        write(HERE / (name + ".argv.json"), argv)
        with (HERE / (name + ".stdout")).open("w") as stdout, (HERE / (name + ".stderr")).open("w") as stderr:
            proc = subprocess.Popen(argv, cwd=RUNTIME, env=env, stdout=stdout, stderr=stderr)
            while proc.poll() is None:
                if not ledger["authorization_consumed"] and folder.exists():
                    pair = next(folder.glob("pair_*.npz"), None)
                    if pair is not None:
                        identity = {"first_output_identity_utc": now(), "stage": name,
                                    "path": str(pair), "sha256": sha(pair), "bytes": pair.stat().st_size}
                        write(HERE / "FIRST_OUTPUT_IDENTITY.json", identity)
                        ledger["authorization_consumed"] = True
                        ledger["first_output_identity_utc"] = identity["first_output_identity_utc"]
                        ledger["one_shot_state"] = "CONSUMED_STAGE_RUNNING"
                        write(LEDGER, ledger)
                time.sleep(1)
            rc = proc.wait()
        (HERE / (name + ".exit")).write_text(str(rc) + "\n")
        if not ledger["authorization_consumed"] and folder.exists():
            pair = next(folder.glob("pair_*.npz"), None)
            if pair is not None:
                identity = {"first_output_identity_utc": now(), "stage": name,
                            "path": str(pair), "sha256": sha(pair), "bytes": pair.stat().st_size}
                write(HERE / "FIRST_OUTPUT_IDENTITY.json", identity)
                ledger["authorization_consumed"] = True
                ledger["first_output_identity_utc"] = identity["first_output_identity_utc"]
        ledger["last_stage_exit"] = rc
        ledger["last_stage_completed_utc"] = now()
        if rc:
            ledger["one_shot_state"] = "PARTIAL_FAILURE_NO_AUTOMATIC_RERUN"
            ledger["failed_stage"] = name
            write(LEDGER, ledger)
            raise SystemExit(rc)
        write(LEDGER, ledger)
    ledger["one_shot_state"] = "CONSUMED_OUTPUTS_COMPLETE"
    ledger["science_node_count"] = 1
    write(LEDGER, ledger)


if __name__ == "__main__":
    main()
