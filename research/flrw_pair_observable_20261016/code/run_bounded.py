#!/usr/bin/env python3
"""Execute the two frozen sandbox commands with individual 30-second limits."""
from datetime import datetime, timezone
import json
from pathlib import Path
import resource
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    contract = json.loads((ROOT / "spec/THOMSON_PAIR_CONTRACT.json").read_text())
    limits = contract["execution_limits"]
    commands = [limits["primary_command"], limits["tests_command"]]
    records = []
    for command in commands:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        start, wall0 = stamp(), time.perf_counter()
        try:
            completed = subprocess.run(command.split(), cwd=ROOT, text=True, capture_output=True,
                                       timeout=limits["max_wall_seconds_per_command"])
            exit_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
            timed_out = False
        except subprocess.TimeoutExpired as error:
            exit_code, stdout, stderr = None, error.stdout or "", error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode()
            if isinstance(stderr, bytes):
                stderr = stderr.decode()
            timed_out = True
        elapsed, end = time.perf_counter()-wall0, stamp()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        record = {"command": command, "host": "current assistant sandbox", "start_utc": start,
                  "end_utc": end, "wall_seconds": elapsed,
                  "child_user_cpu_seconds": after.ru_utime-before.ru_utime,
                  "child_system_cpu_seconds": after.ru_stime-before.ru_stime,
                  "child_total_cpu_seconds": after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
                  "exit_code": exit_code, "timed_out": timed_out,
                  "wall_limit_seconds": limits["max_wall_seconds_per_command"],
                  "stdout": stdout, "stderr": stderr}
        records.append(record)
        print(json.dumps(record))
        # A command failure returns evidence for review; do not run an optional retry.
        if timed_out or exit_code != 0:
            break
    fixture_path = ROOT / "results/TEST_RESULTS.json"
    fixtures = json.loads(fixture_path.read_text()) if fixture_path.exists() else {}
    receipt = {"schema_version": 1, "unit_id": contract["unit_id"], "commands": records,
               "status": "PASS" if len(records) == 2 and all(r["exit_code"] == 0 and not r["timed_out"] for r in records) else "FAIL",
               "executor": "lower-tier coding agent; requested gpt-6.1-sol",
               "runtime_model_observed": "NOT_INDEPENDENTLY_OBSERVED",
               "executed_fixtures": [r["id"] for r in fixtures.get("fixtures", [])],
               "solver_runs": 0, "raw_history_reads": 0, "renderer_runs": 0, "remote_runs": 0,
               "historical_FULL005_cumulative_wall_s": limits["historical_FULL005_cumulative_wall_s"],
               "historical_FULL005_budget_s": 300,
               "historical_absolute_deadline_unix": limits["historical_absolute_deadline_unix"],
               "historical_budget_reset": False, "new_NCP_allocation_seconds": 0,
               "historical_values_role": "Archival provenance, unchanged; not an active sandbox deadline",
               "local_measured_wall_seconds": sum(r["wall_seconds"] for r in records),
               "bounded_commands_only": True,
               "preflight_probe": {"purpose": "diagnosed original 4096-panel contract width failure; authorized amendment now uses8192",
                                    "count": 1, "exit_code": 0,
                                    "wall_cpu_accounting": "Preflight probe had no internal wall/CPU measurement; not included in measured two-command total",
                                    "original_p1_relative_width": .0005224535107466936,
                                    "original_p2_relative_width": .0010421504568676387}}
    (ROOT / "results/EXECUTION_RECEIPT.json").write_text(json.dumps(receipt, indent=2)+"\n")
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
