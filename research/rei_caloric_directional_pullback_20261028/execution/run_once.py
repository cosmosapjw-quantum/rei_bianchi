"""Future single invocation: NOT_RUN. Invoke only after new explicit allowance.

From unit root: python -B -S execution/run_once.py --execute-authorized
One child, CPU soft/hard1s, wall10s, address-space256MiB. No retries.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCY_BLOB = "bc3ebd682c363afc7d5c36d164406086145b6964"


def metadata(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()}


def worker():
    sys.path.insert(0, str(ROOT))
    import unittest
    from fractions import Fraction
    from tests.test_directional_pullback import DirectionalControls
    def encode(value):
        if isinstance(value, Fraction):
            return {"num": str(value.numerator), "den": str(value.denominator)}
        raise TypeError(type(value).__name__)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(DirectionalControls))
    print(json.dumps({"scope": "manufactured exact moving-knot controls A-G",
          "successful": result.wasSuccessful(), "methods_run": result.testsRun,
          "failures": len(result.failures), "errors": len(result.errors),
          "controls": DirectionalControls.evidence, "saved_source_H": "NOT_RUN_NOT_SELECTED",
          "old_suite_replays": 0, "source_producer_replays": 0, "IVP_CAS_runs": 0,
          "actual_recipient_temperature": None, "physical_radii": None,
          "L4_ready": False, "stage_admission": "NOT_ISSUED_BY_RUNNER"}, default=encode, indent=2))
    return 0 if result.wasSuccessful() else 1


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))


def main():
    if sys.argv[1:] == ["--worker"]:
        return worker()
    if sys.argv[1:] != ["--execute-authorized"]:
        raise SystemExit("Pending explicit allowance; command requires --execute-authorized")
    dependency = ROOT / "deps/caloric_branch.py"
    if metadata(dependency)["git_blob"] != DEPENDENCY_BLOB:
        raise SystemExit("Frozen dependency blob mismatch")
    attempt = ROOT / "execution/attempt_01"
    attempt.mkdir(exist_ok=False)  # Never replace old outputs or silently retry.
    sources = {str(p.relative_to(ROOT)): metadata(p) for p in [
        dependency, ROOT/"THEORY_AND_CONTRACT.md", ROOT/"implementation/directional_pullback.py",
        ROOT/"tests/test_directional_pullback.py", Path(__file__).resolve()]}
    command = [sys.executable, "-B", "-S", str(Path(__file__).resolve()), "--worker"]
    start_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.perf_counter()
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               preexec_fn=limits, start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        timed_out = True
        import signal
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    wall = time.perf_counter()-started
    end_cpu = resource.getrusage(resource.RUSAGE_CHILDREN)
    (attempt/"STDOUT.json").write_bytes(stdout)
    (attempt/"STDERR.txt").write_bytes(stderr)
    user = end_cpu.ru_utime-start_cpu.ru_utime
    system = end_cpu.ru_stime-start_cpu.ru_stime
    receipt = {"command": command, "sources": sources, "exit_code": process.returncode,
               "wall_timeout": timed_out, "wall_s": wall, "user_CPU_s": user,
               "system_CPU_s": system, "CPU_s": user+system,
               "accounting_scope": "OS RUSAGE_CHILDREN delta for the sole complete child; wrapper/model/connector/tail excluded",
               "timing_precision": "OS resource counters and perf_counter; printed digits are not a physical accuracy certificate",
               "limits": {"CPU_s": 1, "wall_s": 10, "address_space_bytes": 268435456},
               "outputs": {n: metadata(attempt/n) for n in ("STDOUT.json", "STDERR.txt")},
               "old_reservations_reopened": False, "historical_debit_reset": False,
               "historical_planning_charged_known_plus_reserve_s": "16.586967885",
               "historical_presentation_charged_known_plus_reserve_s": "50.928518494",
               "separate_native_F1_Bash_display": "wall0.037 user0.037 system0.000",
               "main": "595.225063/600 NO_MORE_IVPs", "other_cost": "UNKNOWN_NOT_ZERO",
               "stage_admission": "NOT_ISSUED_BY_RUNNER"}
    (attempt/"PROCESS.json").write_text(json.dumps(receipt, indent=2)+"\n")
    return process.returncode if process.returncode and process.returncode > 0 else (1 if process.returncode else 0)


if __name__ == "__main__":
    raise SystemExit(main())
