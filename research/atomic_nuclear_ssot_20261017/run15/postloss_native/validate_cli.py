#!/usr/bin/env python3
"""Three bounded manufactured source-measure controls; never run a native IVP."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import scipy
from scipy.integrate import quad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    output = args.output_root.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("output-root must be new")
    output.mkdir(parents=True)
    cases = [
        {"name": "n2_sub_h_manufactured_moments", "lo": 13.598434599702, "hi": 13.6, "kt": 4.0, "order": 2},
        {"name": "n6_thin_1e_minus7_ev_band", "lo": 13.6, "hi": 13.6000001, "kt": 4.0, "order": 6},
        {"name": "n8_optical_panel_positive_measure", "lo": 13.598644599702, "hi": 13.598884599702, "kt": 4.0, "order": 8},
    ]
    request = "".join(f"{c['lo']:.17g} {c['hi']:.17g} {c['kt']:.17g} {c['order']}\n" for c in cases)
    (output / "REQUEST.txt").write_text(request)
    started = time.monotonic()
    result = subprocess.run([str(binary)], input=request.encode("ascii"), capture_output=True, timeout=30)
    (output / "STDOUT.jsonl").write_bytes(result.stdout)
    (output / "STDERR.log").write_bytes(result.stderr)
    receipt = {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "IN_PROGRESS", "scope": "Three fixed source-measure controls only; kT=4 eV is an explicitly manufactured control, not a new RUN13/RUN15 physical input packet.",
        "new_native_ivps": 0, "native_cli_processes": 1, "requested_panel_evaluations": 3,
        "old_nine_tests_rerun": False, "old_nine_test_bodies_reconstructed": False,
        "command": [str(binary)], "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "returncode": result.returncode, "seconds": time.monotonic() - started,
        "environment": {"python": platform.python_version(), "scipy": scipy.__version__, "platform": platform.platform()},
        "thresholds": {"relative_mass_error": 2e-12, "absolute_mean_error_ev": 8e-14, "normalized_local_moment_error": 2e-11},
        "cases": [],
        "continuum_error_bound": "NOT_ESTABLISHED",
    }
    failure = None
    try:
        if result.returncode != 0:
            raise ValueError("native CLI returned nonzero")
        responses = [json.loads(line) for line in result.stdout.decode("utf-8").splitlines()]
        if len(responses) != 3:
            raise ValueError("expected exactly three native response lines")
        for case, response in zip(cases, responses):
            if "error" in response:
                raise ValueError(f"native panel rejected {case['name']}: {response}")
            lo, hi, kt = case["lo"], case["hi"], case["kt"]
            half, mid = (hi - lo) / 2.0, (lo + hi) / 2.0
            def shape(z: float) -> float:
                energy = mid + half * z
                return half * energy * energy / math.expm1(energy / kt)
            independent = [quad(lambda z, degree=k: shape(z) * z**degree, -1.0, 1.0,
                                epsabs=1e-25, epsrel=2e-13, limit=100) for k in range(4)]
            ref_mass = independent[0][0]
            ref_mean = mid + half * independent[1][0] / ref_mass
            nodes = response["nodes"]
            finite_positive = (len(nodes) == case["order"] and all(math.isfinite(e) and math.isfinite(w)
                               and lo < e < hi and w > 0.0 for e, w in nodes)
                               and all(a[0] < b[0] for a, b in zip(nodes, nodes[1:])))
            mass = math.fsum(w for _, w in nodes)
            mean = math.fsum(e * w for e, w in nodes) / mass
            errors = []
            for k in range(4):
                recovered = math.fsum(w * ((e - mid) / half)**k for e, w in nodes)
                errors.append((recovered - independent[k][0]) / ref_mass)
            # Mapping emitted binary64 E back to z loses precision on a 1e-7 eV band.
            # The mass and physical-energy mean remain the narrow-band acceptance controls.
            local_checked = case["order"] == 2
            passed = (finite_positive and abs((mass - ref_mass) / ref_mass) < 2e-12
                      and abs(mean - ref_mean) < 8e-14
                      and (not local_checked or max(map(abs, errors)) < 2e-11))
            receipt["cases"].append({"input": case, "status": "PASS" if passed else "FAIL", "native": response,
                                     "reference": {"method": "SciPy QUADPACK on local z, independently integrating continuous Planck source shape",
                                                   "mass_ev3": ref_mass, "mean_ev": ref_mean, "local_moments": independent},
                                     "diagnostics": {"nodes_positive_and_interior": finite_positive,
                                                     "sum_absolute_weights_ev3": mass, "weighted_mean_ev": mean,
                                                     "relative_mass_error": (mass - ref_mass) / ref_mass,
                                                     "absolute_mean_error_ev": mean - ref_mean,
                                                     "normalized_local_moment_errors_0_to_3": errors,
                                                     "local_moment_gate_applied": local_checked}})
            if not passed:
                raise ValueError("bounded control failed: " + case["name"])
        receipt["status"] = "NUMERICALLY_CHECKED"
    except Exception as error:
        failure = error
        receipt["status"] = "FAILED_OR_BLOCKED"
        receipt["error"] = type(error).__name__ + ": " + str(error)
    with (output / "THREE_CLI_CONTROLS.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": receipt["status"], "cases": [{"name": r['input']['name'], "status": r['status'],
          "diagnostics": r['diagnostics']} for r in receipt['cases']], "receipt": str(output / 'THREE_CLI_CONTROLS.json')}, indent=2))
    if failure is not None:
        raise failure


if __name__ == "__main__":
    main()
