"""Run bounded checks and preserve the raw implementation receipt."""

import json
import platform
import sys
import time
import traceback
from pathlib import Path

def main():
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    import scipy
    import test_rr_adapter
    receipt = {
        "contract": "../RR_ADAPTER_CONTRACT.md",
        "command": "python3 run_tests.py",
        "cwd": str(Path(__file__).resolve().parent),
        "environment": {"python": platform.python_version(), "scipy": scipy.__version__,
                        "platform": platform.platform()},
        "execution_identity": {"requested": "lower-tier coding agent",
                               "observed": "unverified by runtime metadata"},
        "zero_ivps": True,
        "observed_failures_resolved": [
            {"class": "implementation_test_path", "observation":
             "First run resolved source under research/research; corrected repository-root parent index.",
             "final_status": "resolved"},
            {"class": "numerical_test_assertion", "observation":
             "Two runs rejected 1e-6 versus floating (0.01)**3 under exact and 2e-16 relative equality; corrected representation-level unit check to 1e-15 relative.",
             "final_status": "resolved"},
        ],
        "checks": {},
        "status": "FAILED",
    }
    try:
        receipt["checks"] = test_rr_adapter.run()
        receipt["status"] = "PASS_SCOPED_IMPLEMENTATION"
        receipt["exit_code"] = 0
    except BaseException:
        receipt["failure_traceback"] = traceback.format_exc()
        receipt["exit_code"] = 1
    finally:
        receipt["wall_seconds"] = time.perf_counter()-start_wall
        receipt["process_cpu_seconds"] = time.process_time()-start_cpu
        receipt["budget"] = {"aggregate_cpu_less_than_s": 30,
                             "aggregate_wall_less_than_s": 60}
        if receipt["process_cpu_seconds"] >= 30 or receipt["wall_seconds"] >= 60:
            receipt["status"] = "BUDGET_FAILURE"
            receipt["exit_code"] = 1
        receipt["C1_C10"] = {
            "C1": "Frozen contract and original six rows with SHA identity checked in source test.",
            "C2": "rr_rows.json -> rr_rate -> SI coefficients and optional ledger; no old-module imports.",
            "C3": "Closed analytic log-slope; positivity and boundary checks; no discretized ODE.",
            "C4": "Source check, slope, 257-point grid, manufactured quadrature, ledger; measured budget here.",
            "C5": "Scalar rr_adapter.py and explicit channel/charge/isotope mapping.",
            "C6": "Checks and exceptions recorded in checks or failure_traceback.",
            "C7": "Manufactured Maxwellian integrals and energy cancellation checks.",
            "C8": "Finite differences, quadrature, grid extrema, runtime and environment recorded.",
            "C9": "Fresh independent scientific review pending parent controller.",
            "C10": "Raw receipt, source rows, code and tests retained; scientific admission pending review.",
        }
        Path(__file__).with_name("IMPLEMENTATION_RECORD.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if receipt["exit_code"]:
        print(receipt.get("failure_traceback", "resource budget exceeded"), file=sys.stderr)
    else:
        print(json.dumps(receipt["checks"], indent=2, sort_keys=True))
    return receipt["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
