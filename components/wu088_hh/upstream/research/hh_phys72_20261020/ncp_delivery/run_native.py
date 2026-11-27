#!/usr/bin/env python3
"""Compile and run PHYS72's optional Fortran scalar cross-check, create-only.

Exact rational results from implementation/bounds.py remain authoritative.
The optional native run evaluates scalar formulas only: zero HH integrations,
zero Coulomb evaluations, no replay of prior certificates or panels.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native" / "phys72_bounds.f90"
EXACT_SOURCE = ROOT / "implementation" / "bounds.py"
SPEC = importlib.util.spec_from_file_location("phys72_native_exact_authority", EXACT_SOURCE)
exact = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = exact
SPEC.loader.exec_module(exact)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def create_json(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def capture(command, directory, label, timeout, environment):
    start = time.time()
    tic = time.monotonic()
    status, code = "completed", None
    try:
        proc = subprocess.run(command, capture_output=True, timeout=timeout,
                              check=False, env=environment)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        if code != 0:
            status = "failed"
    except subprocess.TimeoutExpired as exc:
        status, stdout, stderr = "timeout", exc.stdout or b"", exc.stderr or b""
    except OSError as exc:
        status, stdout, stderr = "execution_failed", b"", str(exc).encode()
    for suffix, data in [("stdout", stdout), ("stderr", stderr)]:
        with (directory/f"{label}.{suffix}.txt").open("xb") as stream:
            stream.write(data)
    result = {"command": command, "status": status, "exit_code": code,
              "started_unix_seconds": start, "wall_seconds": time.monotonic()-tic,
              "timeout_seconds": timeout,
              "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
              "stderr_sha256": hashlib.sha256(stderr).hexdigest()}
    create_json(directory/f"{label}.EXECUTION.json", result)
    return result, stdout


def validate_native_payload(native, lambda_decimal, terms):
    """Check the native result contract before treating it as this run's output.

    These checks authenticate the reported scope and input echoes, not a
    convergence certificate. The exact Fraction authority is unchanged even
    if the rounded denominator selects a different branch near the boundary.
    """
    if not isinstance(native, dict):
        raise ValueError("native result must be one JSON object")
    required = {
        "schema": "PHYS72_FORTRAN_ROUNDED_CROSSCHECK_V1",
        "certificate_authority": "Python exact Fraction evaluator",
        "HH_R10": "OFF",
        "lambda_abs_decimal_input": lambda_decimal,
    }
    for key, expected in required.items():
        if native.get(key) != expected:
            raise ValueError(f"native {key} does not match the requested contract")
    if native.get("certified") is not False:
        raise ValueError("native result must declare certified:false")
    for key, expected in [("terms_retained", terms), ("physical_integrations", 0),
                          ("real_significand_bits", 113), ("real_decimal_range", 4931)]:
        if type(native.get(key)) is not int or native[key] != expected:
            raise ValueError(f"native {key} does not match the requested contract")

    def number(key):
        value = native.get(key)
        grammar = r"[+]?(?:[0-9]+(?:[.][0-9]*)?|[.][0-9]+)(?:[Ee][+-]?[0-9]+)?"
        if not isinstance(value, str) or re.fullmatch(grammar, value) is None:
            raise ValueError(f"native {key} must be one nonnegative decimal token")
        parsed = Decimal(value)
        if not parsed.is_finite() or parsed < 0:
            raise ValueError(f"native {key} must be finite and nonnegative")
        return Fraction(parsed)

    q_value = number("q_formula_rounded")
    lambda_value = number("lambda_abs_rounded")
    rho_value = number("contraction_rounded")
    if q_value <= 0:
        raise ValueError("native rounded q must be positive")
    sent_value = Fraction(Decimal(lambda_decimal))
    # Binary128 roundoff and the 38-digit printed echo are far below this
    # relative allowance. This is only an input-consistency check.
    if abs(lambda_value-sent_value) > abs(sent_value)/2**110:
        raise ValueError("native rounded lambda does not match the sent decimal")
    status = native.get("status")
    if status == "NONPOSITIVE_ROUNDED_DENOMINATOR":
        if rho_value < 1 or "tail_formula_rounded" not in native or native["tail_formula_rounded"] is not None:
            raise ValueError("native nonpositive-denominator branch is inconsistent")
        tail_value = None
    elif status in ("FINITE_ROUNDED_CROSSCHECK", "ROUNDED_TAIL_UNDERFLOW"):
        tail_value = number("tail_formula_rounded")
        if rho_value >= 1:
            raise ValueError("native finite-tail branch requires rounded rho < 1")
        if status == "ROUNDED_TAIL_UNDERFLOW":
            if lambda_value <= 0 or tail_value != 0:
                raise ValueError("native underflow branch is inconsistent")
        elif (lambda_value == 0) != (tail_value == 0):
            raise ValueError("native finite-tail zero branch is inconsistent")
    else:
        raise ValueError("native status is outside the rounded diagnostic contract")
    return q_value, tail_value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New output directory; existing paths are preserved")
    parser.add_argument("--fc", default="gfortran", help="Compiler executable name or exact path")
    parser.add_argument("--fc-arg", action="append", default=[], help="Extra compiler argument; use --fc-arg=-B/path")
    parser.add_argument("--lambda-abs", default="1", help="Exact nonnegative rational; native input is its decimal approximation")
    parser.add_argument("--terms", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--binary", type=Path, help="Use an existing binary, recording its distinct SHA, without compiling")
    args = parser.parse_args(argv)
    lam = exact.exact_nonnegative(args.lambda_abs, "lambda_abs")
    exact.positive_integer(args.terms, "terms")
    if args.terms > 10000 or args.timeout <= 0 or args.timeout > 900:
        parser.error("terms must be <=10000 and timeout must be 1..900 seconds")
    authority = exact.report(args.terms, lam)
    # For a rational extremely near the boundary, the rounded native branch
    # may differ. That branch is only a diagnostic and never changes authority.
    with localcontext() as ctx:
        ctx.prec = 80
        lam_decimal = str(Decimal(lam.numerator)/Decimal(lam.denominator))
    compiler = shutil.which(args.fc) if not Path(args.fc).is_absolute() else args.fc
    if args.binary is None and not compiler:
        parser.error("COMPILER_MISSING: specify a working --fc or --binary")
    args.out.mkdir(parents=True, exist_ok=False)
    directory = args.out.resolve()
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1"})
    create_json(directory/"EXACT_AUTHORITY.json", authority)
    receipt = {"schema": "PHYS72_NATIVE_CROSSCHECK_EXECUTION_V1", "status": "in_progress",
               "source_sha256": digest(SOURCE), "exact_source_sha256": digest(EXACT_SOURCE),
               "runner_sha256": digest(__file__), "platform": platform.platform(),
               "python": sys.version, "native_certified": False,
               "exact_lambda": str(lam), "native_lambda_decimal": lam_decimal,
               "terms": args.terms, "physical_integrations": 0, "HH_R10": "OFF"}
    if args.binary is None:
        version, _ = capture([str(compiler), "--version"], directory, "COMPILER_VERSION", args.timeout, env)
        receipt["compiler_version_execution"] = version
        binary = directory/"phys72-bounds"
        command = [str(compiler), "-O2", "-std=f2008", "-Wall", "-Wextra", "-fcheck=all",
                   "-fno-fast-math", *args.fc_arg, str(SOURCE), "-o", str(binary)]
        compiled, _ = capture(command, directory, "COMPILE", args.timeout, env)
        receipt["compile"] = compiled
        if compiled["exit_code"] != 0:
            receipt["status"] = "COMPILE_FAILED"
            create_json(directory/"EXECUTION.json", receipt)
            return 2
    else:
        binary = args.binary.resolve()
        receipt["compile"] = {"status": "not_run", "reason": "explicit existing binary"}
    receipt["binary_sha256"] = digest(binary)
    execution, stdout = capture([str(binary), lam_decimal, str(args.terms)], directory,
                                 "NATIVE", args.timeout, env)
    receipt["native"] = execution
    if execution["exit_code"] != 0:
        receipt["status"] = "NATIVE_EXECUTION_FAILED"
        create_json(directory/"EXECUTION.json", receipt)
        return 2
    try:
        native = json.loads(stdout)
        create_json(directory/"NATIVE_RESULT.json", native)
        q_native, tail_native = validate_native_payload(native, lam_decimal, args.terms)
    except (ValueError, UnicodeError) as exc:
        receipt["status"] = "NATIVE_PAYLOAD_INVALID"
        receipt["native_payload_error"] = str(exc)
        create_json(directory/"EXECUTION.json", receipt)
        return 2
    receipt["native_payload_validation"] = "PASSED_SCOPE_INPUT_AND_BRANCH_CONTRACT"
    q_error = abs(q_native-exact.Q_UPPER)/exact.Q_UPPER
    comparison = {"q_relative_difference": exact.rational_record(q_error),
                  "scope": "rounded scalar comparison only; exact authority unchanged"}
    tail_exact = exact.born_remainder_bound(args.terms, lam).remainder_upper
    if tail_native is not None and tail_exact is not None:
        actual = tail_native
        difference = abs(actual-tail_exact)
        comparison["tail_absolute_difference"] = exact.rational_record(difference)
        if tail_exact > 0:
            comparison["tail_relative_difference"] = exact.rational_record(difference/tail_exact)
        else:
            comparison["both_zero"] = (actual == 0)
    else:
        comparison["tail_comparison"] = "NOT_COMPARABLE_AT_ROUNDED_OR_EXACT_BOUNDARY"
    receipt["comparison"] = comparison
    receipt["status"] = "COMPLETED_ROUNDED_CROSSCHECK"
    create_json(directory/"EXECUTION.json", receipt)
    print(json.dumps({"status": receipt["status"], "out": str(directory),
                      "native_certified": False, "binary_sha256": receipt["binary_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
