"""One bounded unittest run with an actual resource/evidence receipt."""

import contextlib
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import resource
import sys
import time
import unittest

import test_rate_defect


def main():
    directory = Path(__file__).resolve().parent
    start = time.perf_counter()
    before = resource.getrusage(resource.RUSAGE_SELF)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_rate_defect)
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    after = resource.getrusage(resource.RUSAGE_SELF)
    elapsed = time.perf_counter() - start
    output = stream.getvalue()
    (directory / "test_output.txt").write_text(output)
    receipt = {
        "classification": "manufactured mathematical verification; no physical Li/RUN19/full trajectory",
        "utc_completed": datetime.now(timezone.utc).isoformat(),
        "command": "timeout 20s python3 run_verification.py",
        "working_directory": str(directory),
        "python": sys.version,
        "platform": platform.platform(),
        "dependencies": "Python standard library only",
        "execution_allocation": "one local process; timeout 20 s; no NCP, network, physical provider, or ODE solver",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "successful": result.wasSuccessful(),
        "exit_status": 0 if result.wasSuccessful() else 1,
        "elapsed_seconds": elapsed,
        "user_cpu_seconds": after.ru_utime-before.ru_utime,
        "system_cpu_seconds": after.ru_stime-before.ru_stime,
        "max_rss_kib_linux": after.ru_maxrss,
        "metrics": test_rate_defect.METRICS,
        "sha256": {name: hashlib.sha256((directory/name).read_bytes()).hexdigest()
                   for name in ("rate_defect.py", "test_rate_defect.py", "run_verification.py")},
        "limitations": ["Float arithmetic is not outward-rounded interval arithmetic.",
                       "Panel bound is conditional on valid caller-supplied continuous suprema and clock conversion.",
                       "Frozen-bath block only; nonlinear feedback and physical provider integration remain outside this kernel.",
                       "Independent review required before adoption or publication."],
    }
    (directory / "results_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(output, end="")
    print(json.dumps(receipt, indent=2))
    return receipt["exit_status"]


if __name__ == "__main__":
    raise SystemExit(main())
