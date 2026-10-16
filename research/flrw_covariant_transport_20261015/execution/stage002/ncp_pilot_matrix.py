#!/usr/bin/env python3
"""After controller GO, run one initial pilot and then two bounded pairs.

A failed or incomplete q128 first case stops the matrix without retries.
Completion of all cases supplies measurements for a separate full-run review.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import time

TASK = Path("/root/REI_FLRW_COVARIANT_20261015_002")
CONTROL = TASK / "stage/research/flrw_covariant_transport_20261015/execution/stage002/ncp_control.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-sha256", required=True)
    args = parser.parse_args()
    matrix = TASK / "pilot_matrix"
    matrix.mkdir()
    started = time.time()
    results = []
    groups = [[("q128", 0)], [("q256", 0), ("q512", 1)],
              [("q512_time", 0), ("q512_angle", 1)]]
    status = "RUNNING"
    for group in groups:
        active = []
        for label, cpu in group:
            case = "FLRW_SPLIT_PILOT_" + label.upper() + "_001"
            cfg = "pilot_split_z20_19p8_" + label + ".cfg"
            command = ["python3", str(CONTROL), "launch", "--kind", "pilot", "--case", case,
                       "--config", cfg, "--cpu", str(cpu), "--expected-source-sha256",
                       args.expected_source_sha256]
            log = (matrix / (label + ".log")).open("x")
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            active.append((label, case, command, proc, log))
        failed = False
        for label, case, command, proc, log in active:
            code = proc.wait()
            log.close()
            receipt = TASK / "launches" / (case + ".receipt.json")
            results.append({"label": label, "case": case, "command": command,
                            "returncode": code,
                            "receipt": json.loads(receipt.read_text()) if receipt.exists() else None})
            failed |= code != 0
        state = {"status": "FAILED_OR_INCOMPLETE_STOPPED" if failed else "GROUP_COMPLETED",
                 "started_utc": datetime.datetime.fromtimestamp(started, datetime.timezone.utc).isoformat(),
                 "elapsed_wall_s": time.time()-started, "cases": results,
                 "max_concurrent_scientific_cases": 2, "retry_count": 0}
        (matrix / "progress.json").write_text(json.dumps(state, indent=2)+"\n")
        if failed:
            status = "FAILED_OR_INCOMPLETE_STOPPED"
            break
    else:
        status = "ALL_FIVE_COMPLETED_PENDING_REFINEMENT_REVIEW"
    state["status"] = status
    (matrix / "final.json").write_text(json.dumps(state, indent=2)+"\n")
    print(json.dumps({"status": status, "cases_started": len(results),
                      "elapsed_wall_s": time.time()-started, "full_launches": 0}))
    if status != "ALL_FIVE_COMPLETED_PENDING_REFINEMENT_REVIEW":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
