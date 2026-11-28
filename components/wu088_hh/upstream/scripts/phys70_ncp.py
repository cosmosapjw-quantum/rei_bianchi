#!/usr/bin/env python3
"""Create-only PHYS70 native runs; default mode performs cheap preflight only.

The immutable PHYS69 physics/seed guards are reused.  --seed takes priority
over --make-seed.  --make-seed without --run never evaluates Coulomb functions.
A completed --resume checks saved bytes and the current engine/binary identity;
it launches no processes and writes no files.  A partial directory is retained
and requires a new output directory after its failure has been diagnosed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import signal
import socket
import subprocess
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import phys69_vigilode as inherited

ROOT = SCRIPT_DIR.parent
CRATE = ROOT / "native/phys70_optimized"
BINARY_NAME = "wu088-hh-phys70-optimized"
SOURCE_SHA = inherited.SOURCE_SHA
UPSTREAM = inherited.UPSTREAM
DEFAULT_SOURCE = inherited.DEFAULT_SOURCE
DEFAULT_SEED = inherited.DEFAULT_SEED
ENGINES = {"block_simd", "block_scalar", "legacy_gmres"}
SUCCESS_STATUS = "COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE"
THREAD_ENV = {
    "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1", "BLIS_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
    "RAYON_NUM_THREADS": "1", "CARGO_INCREMENTAL": "0",
    "CARGO_PROFILE_RELEASE_DEBUG": "0",
}


def sha(path: Path) -> str:
    return inherited.sha(path)


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(data: bytes) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"nonfinite JSON constant: {value}")
    result = json.loads(data, object_pairs_hook=_pairs, parse_constant=reject_constant)
    if type(result) is not dict:
        raise ValueError("JSON root must be an object")
    return result


def read(path: Path) -> dict:
    return decode(path.read_bytes())


def create_bytes(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def create_json(path: Path, value: dict) -> None:
    create_bytes(path, (json.dumps(value, indent=2, allow_nan=False) + "\n").encode())


def validate_request(request: dict) -> None:
    if set(request) != {"schema", "engine", "physics_request", "HH_R10"}:
        raise ValueError("PHYS70 request keys mismatch")
    if request["schema"] != "PHYS70_OPTIMIZED_REQUEST_V1" or request["HH_R10"] != "OFF":
        raise ValueError("PHYS70 request schema/HH_R10 mismatch")
    if type(request["engine"]) is not str or request["engine"] not in ENGINES:
        raise ValueError("unknown PHYS70 engine")
    if type(request["physics_request"]) is not dict:
        raise ValueError("physics_request must be an object")
    inherited.validate_request(request["physics_request"])
    physics = request["physics_request"]
    if physics["max_step"] > 0.5 or physics["initial_step"] > physics["max_step"]:
        raise ValueError("PHYS70 requires initial_step <= max_step <= 0.5")


def _number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def validate_result(result: dict, request: dict, request_sha: str, seed_sha: str) -> None:
    """Validate execution identity and finite endpoint layout, not ODE accuracy."""
    for key, expected in [
        ("schema", "PHYS70_OPTIMIZED_RESULT_V1"), ("engine", request["engine"]),
        ("request_sha256", request_sha), ("seed_sha256", seed_sha),
        ("source_sha256", SOURCE_SHA), ("upstream_commit", UPSTREAM), ("HH_R10", "OFF"),
        ("request", request), ("B", 27), ("T", 65), ("k", 0.7),
        ("eta_C", "-10/7"), ("m", 0), ("target", [21, 20]),
        ("clock", "tau=65-r;0..38"), ("q_scale", "2^80"), ("d2_scale", "2^160"),
    ]:
        actual = result.get(key)
        if actual != expected or (type(expected) in (int, float) and type(actual) not in (int, float)):
            raise ValueError(f"native result identity mismatch: {key}")
    if result.get("complete") is not True or result.get("status") != SUCCESS_STATUS:
        raise ValueError("native output is partial or unsuccessful")
    times, states = result.get("observed_times_tau"), result.get("observed_states_scaled")
    if (type(times) is not list or len(times) != 2 or
            any(not _number(x) for x in times) or times != [0.0, 38.0]):
        raise ValueError("native endpoint schedule must be exactly tau=[0,38]")
    dimension = 2 * (4 * (request["physics_request"]["lmax"] + 1) + 1)
    if (type(states) is not list or len(states) != 2 or
            any(type(row) is not list or len(row) != dimension or
                any(not _number(x) for x in row) for row in states)):
        raise ValueError("native state dimension/finiteness mismatch")
    d2 = result.get("endpoint", {}).get("d2", {})
    if type(d2) is not dict or any(not _number(d2.get(k)) for k in ("real", "imag")):
        raise ValueError("native D2 must have finite real and imaginary parts")
    if any(d2[k] != math.ldexp(states[-1][-2 + i], -160)
           for i, k in enumerate(("real", "imag"))):
        raise ValueError("D2 does not match the stored endpoint divided by 2^160")
    for key in ("accepted_steps", "rejected_steps", "attempts", "state_reuses"):
        value = result.get(key)
        if type(value) is not int or not 0 <= value < 2**64:
            raise ValueError(f"invalid native counter: {key}")
    if (result["accepted_steps"] < 1 or
            result["attempts"] != result["accepted_steps"] + result["rejected_steps"] or
            result["attempts"] > request["physics_request"]["max_attempts"]):
        raise ValueError("native attempt ledger mismatch")
    if type(result.get("counters")) is not dict:
        raise ValueError("native counters must be an object")
    elapsed = result.get("integration_elapsed_seconds")
    if not _number(elapsed) or elapsed < 0:
        raise ValueError("invalid native integration elapsed time")


def engine_identity() -> dict[str, str]:
    """Lock both crates, including the PHYS69 path dependency, and Python guards."""
    paths = []
    for crate in (CRATE, ROOT / "native/phys69_vigilode"):
        paths.extend(crate / name for name in ("Cargo.toml", "Cargo.lock"))
        source_files = sorted(path for path in crate.rglob("*.rs")
                              if "target" not in path.relative_to(crate).parts)
        if not source_files:
            raise FileNotFoundError(f"no Rust source files found: {crate / 'src'}")
        paths.extend(source_files)
    paths.extend([Path(__file__), SCRIPT_DIR / "phys69_vigilode.py",
                  SCRIPT_DIR / "phys68_rust_reference.py",
                  ROOT / "src/wu088_hh/phys67_coulomb_certificate.py"])
    return {str(path.relative_to(ROOT)): sha(path) for path in sorted(set(paths))}


def binary_digest(path: Path) -> str:
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError(f"binary is missing or not executable: {path}")
    return sha(path)


def current_identity(request_bytes: bytes, request: dict, seed: Path | None,
                     binary: Path | None) -> dict:
    engine = engine_identity()
    fingerprint = hashlib.sha256(json.dumps(engine, sort_keys=True,
                                            separators=(",", ":")).encode()).hexdigest()
    return {"request_sha256": hashlib.sha256(request_bytes).hexdigest(),
            "source_sha256": SOURCE_SHA, "seed_sha256": sha(seed) if seed else None,
            "engine": request["engine"], "upstream_commit": UPSTREAM,
            "engine_files_sha256": engine, "engine_fingerprint_sha256": fingerprint,
            "binary_sha256": binary_digest(binary) if binary else None}


def runtime_record() -> dict:
    return {"hostname": socket.gethostname(), "platform": platform.platform(),
            "machine": platform.machine(), "python": sys.version,
            "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None}


def payload_hashes(out: Path) -> dict[str, str]:
    files = {}
    for path in sorted(out.rglob("*")):
        if path.is_symlink():
            raise ValueError("run evidence may not contain symlinks")
        if path.is_file() and path != out / "CHECKSUMS.json":
            files[str(path.relative_to(out))] = sha(path)
    return files


def finalize(out: Path, receipt: dict) -> None:
    create_json(out / "EXECUTION.json", receipt)
    create_json(out / "CHECKSUMS.json", {"schema": "PHYS70_EXECUTION_CHECKSUMS_V1",
                                        "files": payload_hashes(out)})


def resume_completed(out: Path, request_bytes: bytes, request: dict,
                     seed: Path | None, binary: Path) -> dict:
    """Read-only: no build, seed generation, native invocation, or file write."""
    checksums = read(out / "CHECKSUMS.json")
    if (checksums.get("schema") != "PHYS70_EXECUTION_CHECKSUMS_V1" or
            checksums.get("files") != payload_hashes(out)):
        raise ValueError("saved run checksums or payload membership mismatch")
    receipt = read(out / "EXECUTION.json")
    if (receipt.get("schema") != "PHYS70_NCP_EXECUTION_V1" or
            receipt.get("status") != "COMPLETED_NATIVE_APPLICATION"):
        raise ValueError("only completed PHYS70 evidence can be resumed")
    local_seed = out / "SEED_INPUT.txt"
    inherited.validate_seed(local_seed, request["physics_request"]["lmax"])
    if seed is not None and sha(seed) != sha(local_seed):
        raise ValueError("provided seed differs from the completed seed")
    identity = current_identity(request_bytes, request, local_seed, binary)
    if receipt.get("identity") != identity:
        raise ValueError("completed source/request/seed/engine/binary identity changed")
    if ((out / "REQUEST.json").read_bytes() != request_bytes or
            sha(out / "FROZEN_U_SUBSET.npz") != SOURCE_SHA):
        raise ValueError("saved request or original frozen source mismatch")
    result = read(out / "RESULT.json")
    validate_result(result, request, identity["request_sha256"], identity["seed_sha256"])
    if receipt.get("result_sha256") != sha(out / "RESULT.json"):
        raise ValueError("execution receipt result hash mismatch")
    integration = read(out / "INTEGRATE_NATIVE.EXECUTION.json")
    if (integration.get("exit_code") != 0 or integration.get("timed_out") is not False or
            integration.get("interrupted") is not False or
            integration not in receipt.get("commands", []) or
            (out / "INTEGRATE_NATIVE.stdout.txt").read_bytes() != (out / "RESULT.json").read_bytes()):
        raise ValueError("completed result and invocation receipt do not agree")
    return {"status": "REUSED_COMPLETED", "new_integrations": 0, "files_written": 0,
            "result_sha256": receipt["result_sha256"], "out": str(out), "HH_R10": "OFF"}


def execute(command: list[str], out: Path, name: str, env: dict,
            timeout: int, memory_gib: float) -> dict:
    """Run one bounded Linux/POSIX process group, retaining failures verbatim."""
    if os.name != "posix":
        raise RuntimeError("bounded native execution requires a POSIX host")
    import resource

    def limits() -> None:
        cap = int(memory_gib * 1024**3)
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        os.nice(10)

    started = time.perf_counter()
    record = {"command": command, "cwd": str(ROOT), "exit_code": None,
              "timed_out": False, "interrupted": False, "wall_limit_seconds": timeout,
              "address_space_limit_bytes": int(memory_gib * 1024**3),
              "nice_increment": 10, "stdout": f"{name}.stdout.txt",
              "stderr": f"{name}.stderr.txt"}
    with (out / record["stdout"]).open("xb") as stdout, (out / record["stderr"]).open("xb") as stderr:
        try:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr,
                                       start_new_session=True, preexec_fn=limits)
            try:
                record["exit_code"] = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as interruption:
                record["timed_out"] = isinstance(interruption, subprocess.TimeoutExpired)
                record["interrupted"] = isinstance(interruption, KeyboardInterrupt)
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    record["exit_code"] = process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    record["exit_code"] = process.wait()
        except Exception as error:
            record["launch_error"] = f"{type(error).__name__}: {error}"
    record["elapsed_seconds"] = time.perf_counter() - started
    create_json(out / f"{name}.EXECUTION.json", record)
    return record


def _successful(record: dict) -> None:
    if record["exit_code"] != 0 or record["timed_out"] or record["interrupted"]:
        raise RuntimeError(f"{record['command'][0]} failed; original logs and execution receipt retained")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--request", type=Path, required=True)
    result.add_argument("--out", type=Path, required=True)
    result.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    result.add_argument("--seed", type=Path, help="reuse these exact seed bytes; takes priority over --make-seed")
    result.add_argument("--make-seed", action="store_true", help="explicit 512-bit inherited initializer, only with --run and no --seed")
    result.add_argument("--run", action="store_true")
    result.add_argument("--resume", action="store_true")
    result.add_argument("--binary", type=Path, help="use an already built binary; omit to build with Cargo on --run")
    result.add_argument("--cargo", default="cargo")
    result.add_argument("--rustc", default="rustc")
    result.add_argument("--cargo-home", type=Path)
    result.add_argument("--target-dir", type=Path, default=CRATE / "target")
    result.add_argument("--offline", action="store_true")
    result.add_argument("--timeout", type=int, default=900)
    result.add_argument("--build-timeout", type=int, default=900)
    result.add_argument("--memory-gib", type=float, default=4.0)
    return result


def run(args: argparse.Namespace) -> dict:
    request_bytes = args.request.read_bytes()
    request = decode(request_bytes)
    validate_request(request)
    if sha(args.source) != SOURCE_SHA:
        raise ValueError("original frozen source SHA256 mismatch")
    if (not 1 <= args.timeout <= 3600 or not 1 <= args.build_timeout <= 3600 or
            not math.isfinite(args.memory_gib) or not 1 <= args.memory_gib <= 64):
        raise ValueError("wall limits must be 1..3600 seconds and memory 1..64 GiB")
    args.out = args.out.resolve()
    binary = (args.binary or args.target_dir / "release" / BINARY_NAME).resolve()
    seed = args.seed
    if seed is None and not args.make_seed and request["physics_request"]["lmax"] == 28:
        seed = DEFAULT_SEED
    if seed is not None:
        inherited.validate_seed(seed, request["physics_request"]["lmax"])
        if seed.resolve() == DEFAULT_SEED.resolve() and sha(seed) != inherited.SEED_L28_SHA:
            raise ValueError("stored original L28 seed SHA256 mismatch")
    if args.out.exists():
        if not args.resume:
            raise FileExistsError("output exists; only exact completed --resume is supported")
        return resume_completed(args.out, request_bytes, request, seed, binary)
    if args.run and seed is None and not args.make_seed:
        raise ValueError("provide --seed or explicitly request --make-seed for this L")
    if args.run and args.binary:
        binary_digest(binary)
    if args.target_dir.resolve().is_relative_to(args.out):
        raise ValueError("Cargo target directory must be outside the immutable run directory")
    initial_identity = current_identity(request_bytes, request, seed,
                                        binary if binary.is_file() else None)
    args.out.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": "PHYS70_NCP_EXECUTION_V1", "status": "PREFLIGHT_ONLY",
               "started_utc": datetime.now(timezone.utc).isoformat(),
               "identity": initial_identity, "runtime": runtime_record(), "commands": [],
               "build_provenance": "EXTERNAL_BINARY_SHA_ONLY" if args.binary else "CARGO_BUILD_REQUESTED",
               "execution_limits": {"wall_seconds_per_native_or_seed_process": args.timeout,
                                    "wall_seconds_per_build_process": args.build_timeout,
                                    "memory_gib_per_process": args.memory_gib},
               "new_integrations": 0, "old_campaign_reruns": 0,
               "numerical_error_certification": "NOT_PERFORMED_BY_EXECUTION_WRAPPER",
               "NCP_submission": "DIRECT_HOST_EXECUTION_ONLY_NO_REMOTE_JOB_SUBMISSION",
               "HH_R10": "OFF"}
    try:
        create_bytes(args.out / "REQUEST.json", request_bytes)
        create_bytes(args.out / "FROZEN_U_SUBSET.npz", args.source.read_bytes())
        if sha(args.out / "FROZEN_U_SUBSET.npz") != SOURCE_SHA:
            raise ValueError("source changed while preparing this run")
        if seed is not None:
            create_bytes(args.out / "SEED_INPUT.txt", seed.read_bytes())
            if sha(args.out / "SEED_INPUT.txt") != initial_identity["seed_sha256"]:
                raise ValueError("seed changed while preparing this run")
            seed = args.out / "SEED_INPUT.txt"
        create_json(args.out / "INVOCATION.json", {
            "schema": "PHYS70_INVOCATION_V1", "request_sha256": initial_identity["request_sha256"],
            "engine_files_sha256": initial_identity["engine_files_sha256"],
            "run_requested": args.run, "make_seed_requested": args.make_seed,
            "existing_seed_selected": seed is not None, "binary_path": str(binary),
            "seed_generation_requested_for_run": bool(args.make_seed and seed is None and args.run),
            "thread_environment": THREAD_ENV, "HH_R10": "OFF"})
        if not args.run:
            receipt["preflight"] = {
                "physics_guard": "PASS", "source_guard": "PASS",
                "seed": "EXISTING_VALIDATED" if seed else "NOT_GENERATED_IN_PREFLIGHT",
                "binary": "AVAILABLE" if binary.is_file() else "BUILD_REQUIRED",
                "python_flint_available": importlib.util.find_spec("flint") is not None,
                "special_function_calls": 0, "processes_launched": 0}
            return {"status": "PREFLIGHT_ONLY", "new_integrations": 0, "out": str(args.out), "HH_R10": "OFF"}
        env = os.environ.copy()
        env.update(THREAD_ENV)
        env.update({"RUSTC": args.rustc, "CARGO_NET_GIT_FETCH_WITH_CLI": "true"})
        if args.cargo_home:
            env["CARGO_HOME"] = str(args.cargo_home.resolve())
        receipt["build_environment"] = {key: env.get(key) for key in (
            *THREAD_ENV, "RUSTC", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS",
            "CARGO_BUILD_TARGET", "CARGO_PROFILE_RELEASE_LTO",
            "CARGO_PROFILE_RELEASE_OPT_LEVEL", "CARGO_PROFILE_RELEASE_CODEGEN_UNITS")}

        def command(name: str, argv: list[str], timeout: int) -> dict:
            record = execute(argv, args.out, name, env, timeout, args.memory_gib)
            receipt["commands"].append(record)
            return record

        if seed is None:
            program = ("from pathlib import Path; import sys; sys.path.insert(0,sys.argv[1]); "
                       "from phys68_rust_reference import create_seed; "
                       "create_seed(Path(sys.argv[2]),Path(sys.argv[3]),lmax=int(sys.argv[4]))")
            _successful(command("MAKE_SEED", [sys.executable, "-c", program, str(SCRIPT_DIR),
                        str(args.out / "FROZEN_U_SUBSET.npz"), str(args.out),
                        str(request["physics_request"]["lmax"])], args.timeout))
            seed = args.out / "SEED_INPUT.txt"
            inherited.validate_seed(seed, request["physics_request"]["lmax"])
        if not args.binary:
            _successful(command("RUST_VERSION", [args.rustc, "--version"], 30))
            _successful(command("CARGO_VERSION", [args.cargo, "--version"], 30))
            build = [args.cargo, "build", "--locked", "--release", "--jobs", "1",
                     "--bin", BINARY_NAME,
                     "--manifest-path", str(CRATE / "Cargo.toml"),
                     "--target-dir", str(args.target_dir.resolve())]
            if args.offline:
                build.append("--offline")
            _successful(command("BUILD_NATIVE", build, args.build_timeout))
        identity = current_identity(request_bytes, request, seed, binary)
        if identity["engine_files_sha256"] != initial_identity["engine_files_sha256"]:
            raise ValueError("engine source changed during preparation/build")
        receipt["identity"] = identity
        argv = [str(binary), "run", str(args.out / "REQUEST.json"), str(seed),
                str(args.out / "FROZEN_U_SUBSET.npz")]
        integration = command("INTEGRATE_NATIVE", argv, args.timeout)
        receipt["new_integrations"] = int("launch_error" not in integration)
        raw = (args.out / "INTEGRATE_NATIVE.stdout.txt").read_bytes()
        try:
            result = decode(raw)
        except (ValueError, UnicodeError):
            _successful(integration)
            raise ValueError("native stdout is not a complete finite JSON object")
        create_bytes(args.out / "RESULT.json", raw)
        receipt["result_sha256"] = sha(args.out / "RESULT.json")
        receipt["native_reported_status"] = result.get("status")
        _successful(integration)
        validate_result(result, request, identity["request_sha256"], identity["seed_sha256"])
        if (current_identity(request_bytes, request, seed, binary) != identity or
                (args.out / "REQUEST.json").read_bytes() != request_bytes or
                sha(args.out / "FROZEN_U_SUBSET.npz") != SOURCE_SHA):
            raise ValueError("input, engine or binary changed during native execution")
        receipt["status"] = "COMPLETED_NATIVE_APPLICATION"
        return {"status": receipt["status"], "new_integrations": receipt["new_integrations"],
                "result_sha256": receipt["result_sha256"], "out": str(args.out), "HH_R10": "OFF"}
    except BaseException as error:
        receipt["status"] = "FAILED_OR_PARTIAL_WITH_PRESERVED_EVIDENCE"
        receipt["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        receipt["finished_utc"] = datetime.now(timezone.utc).isoformat()
        finalize(args.out, receipt)


def main(argv: list[str] | None = None) -> None:
    result = run(parser().parse_args(argv))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
