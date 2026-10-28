"""Single-attempt bounded launcher; run only after controller command release.

FROZEN_SHA256SUMS is authored before release and includes this launcher, the
Python executable, all new code/tests, and immutable source/contract inputs.
This is a small reproducibility receipt, not a new scientific authority.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
OUT = UNIT / "outputs"
CPU_LIMIT = 5
WALL_LIMIT = 25
MEMORY_BYTES = 512 * 1024 * 1024


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def usage(who):
    r = resource.getrusage(who)
    return {"user_s": r.ru_utime, "system_s": r.ru_stime,
            "cpu_s": r.ru_utime + r.ru_stime, "maxrss_KiB": r.ru_maxrss,
            "minor_faults": r.ru_minflt, "major_faults": r.ru_majflt,
            "voluntary_context_switches": r.ru_nvcsw, "involuntary_context_switches": r.ru_nivcsw}


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT, CPU_LIMIT))
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    started = time.monotonic()
    # A second invocation is forbidden even when the first attempt failed.
    marker = OUT / "RUN_STARTED.json"
    if marker.exists() or (OUT / "RUN_RECEIPT.json").exists():
        raise RuntimeError("single authorized attempt already started; stop for controller")
    manifest_path = OUT / "FROZEN_SHA256SUMS"
    expected = {}
    for line in manifest_path.read_text().splitlines():
        sha, name = line.split(None, 1)
        expected[name] = sha
    observed = {name: digest(REPO / name) for name in expected}
    mismatches = [name for name in expected if expected[name] != observed[name]]
    if mismatches:
        raise RuntimeError("BYTE_IDENTITY_MISMATCH before child launch: " + repr(mismatches))
    executable = str(Path(sys.executable).resolve())
    if executable not in expected:
        raise RuntimeError("running executable absent from frozen manifest")
    budget = json.loads((UNIT / "BUDGET_AUTHORIZATION.json").read_text())
    limits()
    child_command = [sys.executable, "-B", str(UNIT / "code/run_science.py")]
    child_env = dict(os.environ)
    child_env.update({"PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
                      "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    prelaunch = {"utc": datetime.now(timezone.utc).isoformat(), "frozen_manifest_sha256": digest(manifest_path),
                 "executable": executable, "executable_sha256": observed[executable],
                 "child_command": child_command, "limits": {"cpu_s": CPU_LIMIT, "wall_s": WALL_LIMIT,
                    "address_space_bytes": MEMORY_BYTES, "attempt": 1, "max_attempts": 1},
                 "input_and_program_sha256": observed}
    with marker.open("x") as f:
        json.dump(prelaunch, f, indent=2); f.write("\n")
    child_before = usage(resource.RUSAGE_CHILDREN)
    status, error, returncode = "NOT_STARTED", None, None
    with (OUT / "STDOUT.txt").open("wb") as stdout, (OUT / "STDERR.txt").open("wb") as stderr:
        try:
            child = subprocess.Popen(child_command, cwd=REPO, env=child_env,
                                     stdout=stdout, stderr=stderr, preexec_fn=limits)
            try:
                returncode = child.wait(timeout=max(.001, WALL_LIMIT - (time.monotonic() - started)))
                status = "EXIT_ZERO" if returncode == 0 else "CHILD_FAILED_STOP_FOR_CONTROLLER"
            except subprocess.TimeoutExpired:
                child.kill()
                returncode = child.wait()
                status = "WALL_TIMEOUT_STOP_FOR_CONTROLLER"
        except Exception as exc:
            status, error = "LAUNCH_FAILED_STOP_FOR_CONTROLLER", repr(exc)
    child_after = usage(resource.RUSAGE_CHILDREN)
    parent = usage(resource.RUSAGE_SELF)
    child_cpu = child_after["cpu_s"] - child_before["cpu_s"]
    # Full self rusage includes interpreter startup before main; child delta
    # includes all waited-for scientific process descendants.
    measured_total = parent["cpu_s"] + child_cpu
    upper = budget["main"]["latest_PR259_known_plus_reserves_cpu_s"] + budget["main"]["sibling_safety_reserve_cpu_s"] + measured_total
    produced = {p.name: digest(p) for p in (OUT / "RESULT.json", OUT / "intervals.tsv", OUT / "STDOUT.txt", OUT / "STDERR.txt") if p.exists()}
    receipt = {"schema": "REI_UVB_CONFIDENCE_EXECUTION_RECEIPT_V1", **prelaunch,
        "status": status, "error": error, "exit_code": returncode,
        "elapsed_wall_s": time.monotonic() - started,
        "environment": {"python_version": sys.version, "python_implementation": platform.python_implementation(),
                        "platform": platform.platform(), "cwd": str(REPO),
                        "selected_child_environment": {key: child_env[key] for key in
                            ("PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
                        "dependencies": "Python standard library only; no numpy/scipy/matplotlib import"},
        "usage": {"parent_self_at_snapshot": parent, "children_before": child_before,
                  "children_after": child_after, "child_cpu_s": child_cpu,
                  "measured_parent_plus_child_cpu_s": measured_total,
                  "receipt_serialization_tail": "UNKNOWN_NOT_ZERO"},
        "budget": {"unit_reservation_cpu_s": 10, "unit_debit_measured_cpu_s": measured_total,
            "remaining_unit_reservation_at_snapshot_cpu_s": 10 - measured_total,
            "prior_known_plus_reserves_cpu_s": budget["main"]["latest_PR259_known_plus_reserves_cpu_s"],
            "sibling_safety_reserve_cpu_s": budget["main"]["sibling_safety_reserve_cpu_s"],
            "known_plus_reserves_and_unit_at_snapshot_cpu_s": upper,
            "temporary_cumulative_ceiling_cpu_s": 700,
            "within_measured_unit_reservation": measured_total <= 10,
            "within_conservative_known_upper_ceiling": upper <= 700,
            "global_cumulative_verdict": "UNRESOLVED_RETAIN_PRIOR_CONCERN_AND_UNKNOWN_OVERHEAD",
            "restored_policy_caps_cpu_s": budget["restore_after_unit"],
            "restoration_semantics": "bounded temporary unit ended; original caps restored, over-baseline debit retained",
            "planning_science_debit_cpu_s": 0, "presentation_render_debit_cpu_s": 0,
            "unknown_overhead": budget["unknown_overhead"], "ledger_reset": False, "ledger_transfer": False},
        "new_ivps": 0, "old_campaign_replays": 0, "figures": "NOT_RUN_BUDGET_DEPENDENCY",
        "requested_executor_role": "lower-tier mechanical coding agent per frozen Astra contract",
        "observed_runtime_model_identity": "NOT_EXPOSED; no model inferred from routing",
        "outputs_sha256": produced,
        "scientific_admission": "PENDING_FRESH_ASTRA_REVIEW"}
    (OUT / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": status, "exit_code": returncode, "measured_cpu_s": measured_total,
                      "elapsed_wall_s": receipt["elapsed_wall_s"], "receipt": str(OUT / "RUN_RECEIPT.json")}))
    if measured_total > 10 or upper > 700:
        return 2
    return 0 if status == "EXIT_ZERO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
