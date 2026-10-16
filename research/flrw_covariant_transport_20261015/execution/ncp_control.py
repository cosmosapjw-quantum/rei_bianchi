#!/usr/bin/env python3
"""NCP build or one fresh bounded native launch, explicitly selected by root.

Prepare/stage/build, pilot admission, and full launch are separate operations.
Calling launch is reserved for the controller's corresponding execution GO.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

TASK = Path("/root/REI_FLRW_COVARIANT_20261015_001")
STAGE = TASK / "stage"
TC = Path("/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001/toolchain")
SCOPE = Path("research/flrw_covariant_transport_20261015")
BINARY = TASK / "target/release/examples/axbi_reionization"
AS_BYTES = 8 * 1024**3
OUTPUT_BYTES = 4 * 1024**3


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def environment():
    env = os.environ.copy()
    env.update(RUSTC=str(TC / "bin/rustc"), RUSTDOC=str(TC / "bin/rustdoc"),
               LD_LIBRARY_PATH=str(TC / "lib"), CARGO_TARGET_DIR=str(TASK / "target"),
               CARGO_BUILD_JOBS="4", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", RAYON_NUM_THREADS="1")
    return env


def verify_source():
    for line in (STAGE / "SOURCE_SHA256SUMS.txt").read_text().splitlines():
        expected, relative = line.split("  ", 1)
        if sha(STAGE / relative) != expected:
            raise RuntimeError("staged source byte identity mismatch: " + relative)


def source_identity():
    driver = STAGE / "rust/rei_microphysics/src/axbi_driver.rs"
    body = driver.read_text().split("pub fn compiled_identity() -> String {", 1)[1]
    body = body.split("fn ledger_values", 1)[0]
    inputs = re.findall(r'include_str!\(\s*"([^"]+)"\s*\)', body)
    return "\nAXBI_SOURCE_BOUNDARY\n".join((driver.parent / p).read_text() for p in inputs).encode()


def write_new(path, value):
    with path.open("x") as out:
        json.dump(value, out, indent=2)
        out.write("\n")


def build():
    verify_source()
    command = ["taskset", "-c", "0-3", "prlimit", f"--as={AS_BYTES}", "--",
               str(TC / "bin/cargo"), "build", "--release", "--locked", "--offline",
               "--manifest-path", str(STAGE / "rust/rei_microphysics/Cargo.toml"),
               "--example", "axbi_reionization"]
    started = time.time()
    with (TASK / "build.log").open("x") as log:
        result = subprocess.run(command, env=environment(), stdout=log,
                                stderr=subprocess.STDOUT, timeout=600)
    receipt = {"command": command, "returncode": result.returncode,
               "wall_s": time.time() - started, "finished_utc": utc(),
               "source_identity_sha256": hashlib.sha256(source_identity()).hexdigest(),
               "binary_sha256": sha(BINARY) if BINARY.exists() else None}
    write_new(TASK / "build_receipt.json", receipt)
    if result.returncode:
        raise SystemExit(result.returncode)
    print(json.dumps(receipt))


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def directory_bytes(root):
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file()) if root.exists() else 0


def launch(args):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.case):
        raise RuntimeError("case ID must be a single path component")
    verify_source()
    identity = source_identity()
    identity_sha = hashlib.sha256(identity).hexdigest()
    if identity_sha != args.expected_source_sha256:
        raise RuntimeError("source identity differs from the reviewed pilot binding")
    built = json.loads((TASK / "build_receipt.json").read_text())
    if built["returncode"] or built["binary_sha256"] != sha(BINARY):
        raise RuntimeError("native binary differs from successful build receipt")
    if built["source_identity_sha256"] != identity_sha:
        raise RuntimeError("native build and current staged source differ")
    cfg = STAGE / SCOPE / "configs" / args.config
    if cfg.parent != STAGE / SCOPE / "configs" or not cfg.is_file():
        raise RuntimeError("select a staged config filename")
    controls = TASK / "launches"
    controls.mkdir(exist_ok=True)
    output = TASK / "runs" / args.case
    if output.exists():
        raise RuntimeError("fresh native output required; no checkpoint resume")
    with (TASK / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        slots_path = TASK / "active_cases.json"
        slots = json.loads(slots_path.read_text()) if slots_path.exists() else []
        slots = [s for s in slots if alive(s["launcher_pid"])]
        if len(slots) >= 2 or any(s["cpu"] == args.cpu for s in slots):
            raise RuntimeError("two-case/single-thread allocation is already occupied")
        now = time.time()
        if args.kind == "full":
            epoch_path = TASK / "campaign_epoch.json"
            if not epoch_path.exists():
                write_new(epoch_path, {"first_full_launch_epoch": now, "first_full_launch_utc": utc(),
                                      "deadline_epoch": now + 43200, "cumulative_wall_cap_s": 43200,
                                      "closeout_reserve_s": 300})
            epoch = json.loads(epoch_path.read_text())
            limit = int(epoch["deadline_epoch"] - now - 300)
            if limit <= 10:
                raise RuntimeError("cumulative full-campaign compute budget exhausted")
        else:
            limit = 600
        text = cfg.read_text()
        if args.kind == "full":
            text, count = re.subn(r"(?m)^max_wall_s=.*$", f"max_wall_s={limit - 10}", text)
            if count != 1:
                raise RuntimeError("full config must contain exactly one cooperative wall cap")
        runtime_cfg = controls / (args.case + ".cfg")
        with runtime_cfg.open("x") as out:
            out.write(text)
        command = ["taskset", "-c", str(args.cpu), "prlimit", f"--as={AS_BYTES}",
                   f"--fsize={OUTPUT_BYTES}", "--", str(BINARY), "--config", str(runtime_cfg),
                   "--output", str(output), "--case", args.case]
        binding = {"case": args.case, "kind": args.kind, "started_utc": utc(), "command": command,
                   "source_identity_sha256": identity_sha, "binary_sha256": sha(BINARY),
                   "base_config_sha256": sha(cfg), "runtime_config_sha256": sha(runtime_cfg),
                   "cooperative_max_wall_s": limit - 10 if args.kind == "full" else 600,
                   "external_wall_cap_s": limit, "address_space_bytes": AS_BYTES,
                   "aggregate_output_cap_bytes": OUTPUT_BYTES, "native_threads": 1,
                   "cpu": args.cpu, "launcher_pid": os.getpid()}
        write_new(controls / (args.case + ".binding.json"), binding)
        slots.append({"case": args.case, "cpu": args.cpu, "launcher_pid": os.getpid()})
        slots_path.write_text(json.dumps(slots, indent=2) + "\n")
    started = time.monotonic()
    peak_rss = 0
    stop_reason = None
    log_path = controls / (args.case + ".log")
    with log_path.open("x") as log:
        proc = subprocess.Popen(command, env=environment(), stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        while proc.poll() is None:
            elapsed = time.monotonic() - started
            count = directory_bytes(output) + log_path.stat().st_size
            status = Path(f"/proc/{proc.pid}/status")
            if status.exists():
                match = re.search(r"(?m)^VmRSS:\s+(\d+) kB$", status.read_text())
                if match:
                    peak_rss = max(peak_rss, int(match.group(1)) * 1024)
            if elapsed >= limit:
                stop_reason = "EXTERNAL_WALL_CAP"
            elif count >= OUTPUT_BYTES:
                stop_reason = "AGGREGATE_OUTPUT_CAP"
            if stop_reason:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                break
            time.sleep(1)
        returncode = proc.wait()
    identity_file = output / "source_identity.txt"
    receipt = {"case": args.case, "returncode": returncode, "stop_reason": stop_reason,
               "finished_utc": utc(), "wall_s": time.monotonic() - started,
               "observed_peak_rss_bytes": peak_rss, "output_bytes": directory_bytes(output),
               "source_identity_readback_equal": identity_file.exists() and identity_file.read_bytes() == identity,
               "config_readback_equal": (output / "config.cfg").exists()
                    and (output / "config.cfg").read_bytes() == runtime_cfg.read_bytes()}
    write_new(controls / (args.case + ".receipt.json"), receipt)
    with (TASK / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        slots = json.loads(slots_path.read_text())
        slots_path.write_text(json.dumps([s for s in slots if s["launcher_pid"] != os.getpid()], indent=2) + "\n")
    print(json.dumps(receipt))
    if returncode or stop_reason or not receipt["source_identity_readback_equal"] or not receipt["config_readback_equal"]:
        raise SystemExit(returncode or 1)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("build")
    run = sub.add_parser("launch")
    run.add_argument("--kind", choices=["pilot", "full"], required=True)
    run.add_argument("--case", required=True)
    run.add_argument("--config", required=True, help="filename inside staged configs")
    run.add_argument("--cpu", type=int, choices=[0, 1], required=True)
    run.add_argument("--expected-source-sha256", required=True)
    args = parser.parse_args()
    if args.action == "build":
        build()
    else:
        launch(args)


if __name__ == "__main__":
    main()
