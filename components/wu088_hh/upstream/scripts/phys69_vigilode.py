#!/usr/bin/env python3
"""Build/run the pinned PHYS69 native adapter, with create-only run receipts.

Default mode records preflight only. --run explicitly compiles and executes.
--seed reuses existing seeds. --make-seed explicitly constructs new 512-bit
PHYS67 Coulomb seeds; no old PHYS68 integral or RK4 campaign is launched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CRATE = ROOT / "native/phys69_vigilode"
UPSTREAM = "a21d573980f66fe02891bd216153443b5352f921"
SOURCE_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
CERT_SHA = "ddaae206009a276def281af5526851ceb717baf2e0de5f8472552a9db340de9a"
SEED_L28_SHA = "3aae5f37d858deca71f4f4217d56484d8430f06ad95e30280a44aafc2b6f7862"
DEFAULT_SOURCE = ROOT / "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
DEFAULT_SEED = ROOT / "research/hh_phys69_20261019/vigilode/inputs/L28_SEED_INPUT.txt"
DEFAULT_CERT = ROOT / "research/hh_phys68_20261019/profiles/run_l28_t65_completed/CERTIFICATE.json"
REQUEST_KEYS = {"schema", "lmax", "angular_nodes", "rtol", "atol", "initial_step",
                "max_step", "max_attempts", "upstream_commit", "frozen_source_sha256", "HH_R10"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def validate_request(request: dict) -> None:
    if set(request) != REQUEST_KEYS:
        raise ValueError("request schema keys mismatch")
    for key, value in [("schema", "PHYS69_VIGILODE_REQUEST_V1"), ("upstream_commit", UPSTREAM),
                       ("frozen_source_sha256", SOURCE_SHA), ("HH_R10", "OFF")]:
        if request[key] != value:
            raise ValueError(f"request identity mismatch: {key}")
    lmax, nodes, attempts = (request[k] for k in ["lmax", "angular_nodes", "max_attempts"])
    if type(lmax) is not int or not 21 <= lmax <= 64:
        raise ValueError("L must be an integer in 21..64")
    if type(nodes) is not int or not lmax + 29 <= nodes <= 1024:
        raise ValueError("angular order outside fixed client limits")
    if type(attempts) is not int or not 1 <= attempts <= 100000:
        raise ValueError("invalid attempt cap")
    for key in ["rtol", "atol", "initial_step", "max_step"]:
        value = request[key]
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError(f"invalid {key}")
    if request["rtol"] == request["atol"] == 0:
        raise ValueError("both tolerances are zero")
    if request["initial_step"] <= 0 or request["max_step"] < 1e-14:
        raise ValueError("invalid positive step")


def validate_seed(path: Path, lmax: int) -> None:
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        values = line.split()
        if len(values) != 5 or int(values[0]) != len(rows):
            raise ValueError("seed ordering/shape mismatch")
        parts = list(map(float, values[1:]))
        if not all(map(math.isfinite, parts)) or complex(*parts[:2]) == 0:
            raise ValueError("nonfinite seed or zero denominator")
        rows.append(parts)
    if len(rows) != lmax + 1:
        raise ValueError("seed count does not match L")


def dyadic(record: dict) -> Fraction:
    m, e = int(record["mantissa"]), int(record["exponent2"])
    return Fraction(m << e) if e >= 0 else Fraction(m, 1 << -e)


def sqrt_bounds(value: Fraction, bits: int = 512) -> tuple[Fraction, Fraction]:
    """Exact integer enclosure, independent of Arb and native floating arithmetic."""
    if value < 0:
        raise ValueError("negative radicand")
    scaled_num = value.numerator << (2 * bits)
    floor = math.isqrt(scaled_num // value.denominator)
    low = Fraction(floor, 1 << bits)
    high = low if floor * floor * value.denominator == scaled_num else Fraction(floor + 1, 1 << bits)
    return low, high


def rational_record(value: Fraction) -> dict:
    with localcontext() as ctx:
        ctx.prec = 30
        display = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"numerator": str(value.numerator), "denominator": str(value.denominator),
            "display_approximate": display}


def compare_certificate(result: dict, certificate_path: Path, relative_goal: Fraction = Fraction(1, 1000000)) -> dict:
    """Bound the error of this stored finite-L28 D2 value, without re-integration."""
    if sha(certificate_path) != CERT_SHA:
        raise ValueError("PHYS68 certificate identity mismatch")
    certificate = read(certificate_path)
    if result["request"]["lmax"] != 28 or result["target"] != [21, 20] or result["m"] != 0:
        raise ValueError("L28 certificate cannot validate another angular block")
    data = certificate["D2_B_cutoff"]
    tail_data = certificate["D2_radial_cutoff_error"]
    tail = Fraction(int(tail_data["numerator"]), int(tail_data["denominator"]))
    squared_low, squared_high = Fraction(0), Fraction(0)
    norm_low2, norm_high2 = Fraction(0), Fraction(0)
    point = {}
    for part in ["real", "imag"]:
        value = result["endpoint"]["d2"][part]
        if type(value) is not float or not math.isfinite(value):
            raise ValueError("stored native output must be finite binary64")
        p = Fraction.from_float(value)
        mid, rad = dyadic(data[part]["midpoint"]), dyadic(data[part]["radius"])
        if rad < 0:
            raise ValueError("negative reference radius")
        separation = abs(p - mid)
        squared_low += max(Fraction(0), separation - rad) ** 2
        squared_high += (separation + rad) ** 2
        norm_low2 += max(Fraction(0), abs(mid) - rad) ** 2
        norm_high2 += (abs(mid) + rad) ** 2
        point[part] = rational_record(p)
    low = max(Fraction(0), sqrt_bounds(squared_low)[0] - tail)
    high = sqrt_bounds(squared_high)[1] + tail
    norm_low = max(Fraction(0), sqrt_bounds(norm_low2)[0] - tail)
    norm_high = sqrt_bounds(norm_high2)[1] + tail
    if norm_low <= 0:
        raise ArithmeticError("unresolved reference modulus")
    relative_low, relative_high = low / norm_high, high / norm_low
    return {"status": "CERTIFIED_ERROR_OF_THIS_STORED_NATIVE_VALUE_ONLY",
            "certificate_sha256": CERT_SHA, "relative_goal": str(relative_goal),
            "goal_met": relative_high < relative_goal,
            "absolute_error_lower": rational_record(low), "absolute_error_upper": rational_record(high),
            "relative_error_lower": rational_record(relative_low), "relative_error_upper": rational_record(relative_high),
            "stored_binary64_value": point, "radial_tail": rational_record(tail),
            "algorithm_uniform_error_bound": False, "unit": "a0^-1", "integrations_launched": 0}


def validate_result(result: dict, request: dict, source_sha: str, seed_sha: str) -> None:
    if result.get("schema") != "PHYS69_VIGILODE_RESULT_V1" or result.get("request") != request:
        raise ValueError("native result request/schema mismatch")
    for key, expected in [("upstream_commit", UPSTREAM), ("source_sha256", source_sha),
                          ("seed_sha256", seed_sha), ("HH_R10", "OFF"), ("B", 27), ("T", 65),
                          ("target", [21, 20]), ("m", 0), ("q_scale", "2^80"), ("d2_scale", "2^160")]:
        if result.get(key) != expected:
            raise ValueError(f"native result identity mismatch: {key}")
    if result.get("status") != "COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE" or result.get("complete") is not True:
        raise ValueError("native integration did not complete")
    times, states = result["observed_times_tau"], result["observed_states_scaled"]
    if times != [0.0, 38.0] or len(states) != 2:
        raise ValueError("incomplete native endpoint schedule")
    dim = 2 * (4 * (request["lmax"] + 1) + 1)
    if any(len(row) != dim or any(type(x) not in (int, float) or not math.isfinite(x) for x in row) for row in states):
        raise ValueError("native state dimension/finiteness mismatch")
    counters = result["counters"]
    if counters["jacobian_builds"] != 0 or counters["direct_factorizations"] != 0 or counters["jvp_vectors"] <= 0:
        raise ValueError("claimed matrix-free path not supported by counters")
    if result["attempts"] != result["accepted_steps"] + result["rejected_steps"]:
        raise ValueError("attempt ledger mismatch")


def execute(command: list[str], out: Path, name: str, env: dict, timeout: int) -> dict:
    started = time.perf_counter()
    with (out / f"{name}.stdout.txt").open("w") as stdout, (out / f"{name}.stderr.txt").open("w") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        timed_out = False
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                code = process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                code = process.wait()
    record = {"command": command, "exit_code": code, "timed_out": timed_out,
              "elapsed_seconds": time.perf_counter() - started,
              "stdout": f"{name}.stdout.txt", "stderr": f"{name}.stderr.txt"}
    write(out / f"{name}.EXECUTION.json", record)
    if code != 0 or timed_out:
        raise RuntimeError(f"{name} failed; exact logs and status retained")
    return record


def engine_identity() -> dict:
    paths = [CRATE / "Cargo.toml", CRATE / "Cargo.lock", CRATE / "src/lib.rs", CRATE / "src/main.rs", Path(__file__)]
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--make-seed", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--test", action="store_true", help="new adapter Rust unit tests only")
    parser.add_argument("--resume", action="store_true", help="reuse an exactly matching completed result only")
    parser.add_argument("--cargo", default="cargo")
    parser.add_argument("--rustc", default="rustc")
    parser.add_argument("--cargo-home", type=Path)
    parser.add_argument("--target-dir", type=Path, default=CRATE / "target")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERT)
    args = parser.parse_args()
    request = read(args.request)
    validate_request(request)
    if sha(args.source) != SOURCE_SHA:
        raise ValueError("original frozen source SHA256 mismatch")
    if args.seed and args.make_seed:
        raise ValueError("choose existing --seed or explicit --make-seed")
    if not 1 <= args.timeout <= 3600:
        raise ValueError("timeout must lie in 1..3600 seconds")
    seed = args.seed or (DEFAULT_SEED if request["lmax"] == 28 else None)
    if seed and not args.make_seed:
        validate_seed(seed, request["lmax"])
        if seed == DEFAULT_SEED and sha(seed) != SEED_L28_SHA:
            raise ValueError("saved PHYS68 seed identity mismatch")
    if not seed and not args.make_seed:
        raise ValueError("provide existing --seed or --make-seed for this L")
    engine = engine_identity()
    base_identity = {"request": request, "request_sha256": sha(args.request), "source_sha256": SOURCE_SHA,
                     "engine_sha256": engine, "seed_sha256": sha(seed) if seed and not args.make_seed else None}
    if args.out.exists():
        if not args.resume:
            raise FileExistsError("run output exists; use --resume only for exact completed evidence")
        if args.make_seed:
            validate_seed(args.out / "SEED_INPUT.txt", request["lmax"])
            base_identity["seed_sha256"] = sha(args.out / "SEED_INPUT.txt")
        receipt = read(args.out / "EXECUTION_RECORD.json")
        if receipt.get("identity") != base_identity or receipt.get("status") != "COMPLETED_NATIVE_APPLICATION":
            raise ValueError("only unchanged completed identity can be resumed")
        result_path = args.out / "RESULT.json"
        if sha(result_path) != receipt["result_sha256"]:
            raise ValueError("saved result digest mismatch")
        validate_result(read(result_path), request, SOURCE_SHA, base_identity["seed_sha256"])
        print(json.dumps({"status": "REUSED_COMPLETED", "new_integrations": 0, "out": str(args.out)}))
        return
    args.out.mkdir(parents=True, exist_ok=False)
    write(args.out / "REQUEST.json", request)
    if args.make_seed:
        sys.path.insert(0, str(ROOT / "scripts"))
        from phys68_rust_reference import create_seed
        seed, _ = create_seed(args.source, args.out, lmax=request["lmax"])
        base_identity["seed_sha256"] = sha(seed)
    else:
        shutil.copyfile(seed, args.out / "SEED_INPUT.txt")
        seed = args.out / "SEED_INPUT.txt"
    receipt = {"schema": "PHYS69_VIGILODE_EXECUTION_V1", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "identity": base_identity, "status": "PREFLIGHT_ONLY", "commands": [], "old_campaign_reruns": 0,
               "ncp_submission": "NOT_SUBMITTED_BY_THIS_DRIVER", "HH_R10": "OFF"}
    write(args.out / "EXECUTION_RECORD.json", receipt)
    if not args.run:
        print(json.dumps(receipt, indent=2))
        return
    env = os.environ.copy()
    env.update({"RUSTC": args.rustc, "CARGO_NET_GIT_FETCH_WITH_CLI": "true", "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "RAYON_NUM_THREADS": "1",
                "CARGO_INCREMENTAL": "0", "CARGO_PROFILE_RELEASE_DEBUG": "0"})
    if args.cargo_home:
        env["CARGO_HOME"] = str(args.cargo_home.resolve())
    receipt["build_environment"] = {key: env[key] for key in ["RUSTC", "CARGO_INCREMENTAL", "CARGO_PROFILE_RELEASE_DEBUG", "RAYON_NUM_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"]}
    common = ["--manifest-path", str(CRATE / "Cargo.toml"), "--locked", "--release", "--jobs", "1",
              "--target-dir", str(args.target_dir.resolve())]
    if args.offline:
        common.append("--offline")
    try:
        for name, command in [("RUST_VERSION", [args.rustc, "--version"]), ("CARGO_VERSION", [args.cargo, "--version"])]:
            receipt["commands"].append(execute(command, args.out, name, env, 30))
        if args.test:
            receipt["commands"].append(execute([args.cargo, "test", *common, "--lib"], args.out, "RUST_TESTS", env, args.timeout))
        receipt["commands"].append(execute([args.cargo, "build", *common], args.out, "BUILD_NATIVE", env, args.timeout))
        binary = args.target_dir.resolve() / "release/wu088-hh-phys69-vigilode"
        receipt["binary_sha256"] = sha(binary)
        receipt["commands"].append(execute([str(binary), str((args.out / "REQUEST.json").resolve()), str(seed.resolve()), str(args.source.resolve())], args.out, "INTEGRATE_NATIVE", env, args.timeout))
        result = read(args.out / "INTEGRATE_NATIVE.stdout.txt")
        if result.get("request_sha256") != sha(args.out / "REQUEST.json"):
            raise ValueError("native request byte digest mismatch")
        validate_result(result, request, SOURCE_SHA, sha(seed))
        write(args.out / "RESULT.json", result)
        receipt["result_sha256"] = sha(args.out / "RESULT.json")
        if request["lmax"] == 28:
            comparison = compare_certificate(result, args.certificate)
            write(args.out / "CERTIFICATE_COMPARISON.json", comparison)
            receipt["comparison_goal_met"] = comparison["goal_met"]
            if not comparison["goal_met"]:
                raise ArithmeticError("native completed, but the pre-fixed 1e-6 relative D2 goal failed")
        receipt["status"] = "COMPLETED_NATIVE_APPLICATION"
    except Exception as error:
        receipt["status"] = "FAILED_WITH_PRESERVED_RECEIPTS"
        receipt["error"] = str(error)
        raise
    finally:
        write(args.out / "EXECUTION_RECORD.json", receipt)
    print(json.dumps({"status": receipt["status"], "result_sha256": receipt["result_sha256"], "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
