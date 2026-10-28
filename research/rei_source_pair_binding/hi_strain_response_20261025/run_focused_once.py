"""One explicit-GO bounded child, measured wait4 receipt, no implicit retry."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", required=True)
    args = parser.parse_args()
    go_path = Path(args.go).resolve()
    go = json.loads(go_path.read_bytes())
    if go.get("unit") != "HI_NATIVE_STRAIN_RESPONSE_20261025" or go.get("science_execution") != "GO":
        raise SystemExit("explicit matching root GO required")
    manifest_bytes = (HERE / "PRE_EXECUTION_MANIFEST.json").read_bytes()
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    if go.get("manifest_sha256") != manifest_sha:
        raise SystemExit("root GO must bind actual frozen manifest")
    manifest = json.loads(manifest_bytes)
    for entry in manifest["files"]:
        data = (HERE / entry["path"]).read_bytes()
        if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise SystemExit("frozen payload identity changed: " + entry["path"])
    raw = HERE / "raw"
    raw.mkdir(exist_ok=True)
    with (raw / "ATTEMPT_STARTED.json").open("x") as stream:
        json.dump({"root_GO": str(go_path), "pid": os.getpid(), "start_wall_time": time.time()}, stream)
    environment = os.environ.copy()
    environment.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
                        "NUMEXPR_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"})
    def limits():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (6, 6))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 ** 2, 512 * 1024 ** 2))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    started = time.monotonic()
    timed_out = False
    with (raw / "stdout.jsonl").open("wb") as stdout, (raw / "stderr.txt").open("wb") as stderr:
        child = subprocess.Popen([sys.executable, "-B", str(HERE / "focused_check.py")], cwd=HERE,
                                 env=environment, stdout=stdout, stderr=stderr, preexec_fn=limits)
        while True:
            observed, status, usage = os.wait4(child.pid, os.WNOHANG)
            if observed:
                break
            if time.monotonic() - started >= 8:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                observed, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(0.005)
        child.returncode = os.waitstatus_to_exitcode(status)
    wall = time.monotonic() - started
    cpu = usage.ru_utime + usage.ru_stime
    receipt = {"schema": "REI_HI_STRAIN_RESOURCE_V1", "unit": "HI_NATIVE_STRAIN_RESPONSE_20261025",
               "root_GO": str(go_path), "manifest_sha256": manifest_sha, "children": 1,
               "command": [sys.executable, "-B", "focused_check.py"], "exit_code": child.returncode,
               "user_cpu_s": usage.ru_utime, "system_cpu_s": usage.ru_stime, "cpu_s": cpu,
               "wall_s": wall, "CPU_cap_s": 6, "wall_cap_s": 8, "maxrss_kB": usage.ru_maxrss,
               "wall_timeout": timed_out, "resource_pass": cpu <= 6 and wall <= 8 and not timed_out,
               "retry": 0, "old_tests_replayed": 0, "old_native_integrals_recomputed": 0,
               "network_calls_in_child": 0, "known_partial_before_s": "11.160661",
               "historical_failed_sequence_cpu_s": "10.110448", "historical_overrun_s": "0.110448",
               "historical_cap_reset": 0, "whole_L0": "UNKNOWN_NOT_ZERO",
               "original_cumulative_cap": "NOT_FROZEN", "remote_CAS_CPU": "UNKNOWN_NOT_ZERO_SEPARATE"}
    for name in ("stdout.jsonl", "stderr.txt"):
        data = (raw / name).read_bytes()
        receipt[name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    (raw / "resource_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if child.returncode == 0 and receipt["resource_pass"]:
        result = json.loads((raw / "stdout.jsonl").read_bytes())
        summary = {"schema": "REI_HI_STRAIN_RESULT_SUMMARY_V1", "observed_status": result["observed_status"],
                   "scientific_admission": "ROOT_PENDING", "primary_rows": result["primary_rows"],
                   "mass_eV": result["mass_eV"], "intervals": result["intervals"],
                   "Decimal100_comparison": result["Decimal100_comparison"], "native_tensors": result["native_tensors"],
                   "controls": result["controls"]["groups"], "resource": receipt,
                   "L4_ready": False, "whole_model_completion": None}
        (HERE / "RESULT_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if child.returncode == 0 and receipt["resource_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
