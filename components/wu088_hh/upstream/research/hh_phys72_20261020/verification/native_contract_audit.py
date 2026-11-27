#!/usr/bin/env python3
"""Focused regression checks for PHYS72 native CLI/result contract findings."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "ncp_delivery" / "run_native.py"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--valid-result", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    directory = args.out.resolve()
    binary = args.binary.resolve()
    spec = importlib.util.spec_from_file_location("phys72_native_contract_subject", RUNNER)
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    baseline = json.loads(args.valid_result.read_text())
    evidence = {
        "schema": "PHYS72_NATIVE_CONTRACT_AUDIT_V1",
        "scope": "six malformed CLI tokens, returned scope/input contract, one rounded denominator branch",
        "audit_source_sha256": sha256(__file__),
        "runner_sha256": sha256(RUNNER),
        "native_source_sha256": sha256(ROOT / "native" / "phys72_bounds.f90"),
        "binary_sha256": sha256(binary),
        "valid_result_sha256": sha256(args.valid_result),
        "checks": [], "physical_integrations": 0, "HH_R10": "OFF",
    }
    checks = evidence["checks"]
    subject.validate_native_payload(baseline, "1", 3)
    checks.append({"check": "accept_actual_corrected_default_payload", "status": "PASS"})
    for tokens in [("1 2", "3"), ("1/", "3"), ("/", "3"),
                   ("1", "3 4"), ("1", "3/"), ("1", "/")]:
        tic = time.monotonic()
        process = subprocess.run([str(binary), *tokens], capture_output=True, check=False, timeout=30)
        wall = time.monotonic()-tic
        assert process.returncode == 2 and process.stdout == b"", tokens
        checks.append({"check": "reject_whole_invalid_cli_token", "arguments": list(tokens),
                       "exit_code": process.returncode, "wall_seconds": wall,
                       "stdout": process.stdout.decode(), "stderr": process.stderr.decode(), "status": "PASS"})
    mutations = [
        ("schema", "OTHER_SCHEMA"), ("certified", True), ("HH_R10", "ON"),
        ("terms_retained", 4), ("physical_integrations", 1),
        ("lambda_abs_decimal_input", "2"), ("lambda_abs_rounded", "2"),
        ("q_formula_rounded", "NaN"), ("contraction_rounded", "1"),
        ("tail_formula_rounded", None),
    ]
    for field, replacement in mutations:
        payload = copy.deepcopy(baseline)
        payload[field] = replacement
        try:
            subject.validate_native_payload(payload, "1", 3)
        except ValueError as exc:
            checks.append({"check": "reject_inconsistent_payload", "mutated_field": field,
                           "replacement": replacement, "error": str(exc), "status": "PASS"})
        else:
            raise AssertionError(f"inconsistent {field} was accepted")

    # This native branch is a rounded diagnostic; its result grants no exact
    # convergence or divergence claim. It performs no physical integration.
    tic = time.monotonic()
    process = subprocess.run([str(binary), "1e30", "3"], capture_output=True, check=False, timeout=30)
    native_wall = time.monotonic()-tic
    assert process.returncode == 0
    payload = json.loads(process.stdout)
    subject.validate_native_payload(payload, "1e30", 3)
    assert payload["status"] == "NONPOSITIVE_ROUNDED_DENOMINATOR"
    assert payload["tail_formula_rounded"] is None
    checks.append({"check": "rounded_nonpositive_denominator_has_no_tail", "status": "PASS",
                   "arguments": ["1e30", "3"], "exit_code": 0, "wall_seconds": native_wall,
                   "stdout": process.stdout.decode(), "stderr": process.stderr.decode()})

    # Close the --binary finding through the actual runner entry point.
    bad_payload = copy.deepcopy(baseline)
    bad_payload["terms_retained"] = 4
    fixture_source = "#!"+sys.executable+"\nprint("+repr(json.dumps(bad_payload))+")\n"
    with tempfile.TemporaryDirectory(prefix="phys72_bad_native_") as temp:
        fixture = Path(temp) / "payload-emitter"
        fixture.write_text(fixture_source)
        fixture.chmod(0o755)
        process = subprocess.run(
            [sys.executable, str(RUNNER), "--binary", str(fixture), "--out",
             str(directory / "inconsistent_binary"), "--lambda-abs", "1", "--terms", "3"],
            capture_output=True, check=False, timeout=30)
    assert process.returncode == 2
    receipt = json.loads((directory / "inconsistent_binary" / "EXECUTION.json").read_text())
    assert receipt["status"] == "NATIVE_PAYLOAD_INVALID"
    assert receipt["native"]["exit_code"] == 0
    checks.append({"check": "actual_runner_rejects_inconsistent_existing_binary_payload", "status": "PASS",
                   "runner_exit_code": process.returncode, "receipt": "inconsistent_binary/EXECUTION.json",
                   "fixture_source": fixture_source,
                   "stdout": process.stdout.decode(), "stderr": process.stderr.decode()})
    evidence.update({"status": "PASS_SCOPED", "checks_passed": len(checks),
                     "rejected_native_cli_calls": 6, "successful_native_scalar_calls": 1,
                     "payload_fixture_processes": 1})
    with (directory / "AUDIT.json").open("x") as stream:
        json.dump(evidence, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": evidence["status"], "checks_passed": len(checks),
                      "out": str(directory)}))


if __name__ == "__main__":
    main()
