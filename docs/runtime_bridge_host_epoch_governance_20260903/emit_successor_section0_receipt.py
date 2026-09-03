#!/usr/bin/env python3
"""Create a new successor-host Section-0 receipt after exact field verification.

This script never reconstructs the historical raw receipt and never invokes the
REI production bridge.  It emits a new O_EXCL receipt only when every observed
host/toolchain field exactly matches the semantic lock in the governance policy.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_POLICY = HERE / "HOST_EPOCH_REATTESTATION_POLICY.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def require_regular(path: Path, label: str, executable: bool = False) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise SystemExit(f"{label}_NOT_ABSOLUTE")
    if candidate.is_symlink() or not candidate.is_file():
        raise SystemExit(f"{label}_UNAVAILABLE")
    mode = candidate.stat().st_mode
    if not stat.S_ISREG(mode) or (executable and not os.access(candidate, os.X_OK)):
        raise SystemExit(f"{label}_UNAVAILABLE")
    return candidate.resolve(strict=True)


def run_text(argv: list[str]) -> str:
    completed = subprocess.run(
        argv,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        raise SystemExit(f"HOST_ATTESTATION_COMMAND_FAILED:{argv[0]}:{completed.returncode}")
    return completed.stdout.strip()


def stdlib_closure(root: Path) -> str:
    rows: list[bytes] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name.encode("utf-8")):
        mode = child.lstat().st_mode
        if stat.S_ISREG(mode):
            rows.append(f"{sha256_file(child)}  ./{child.name}\n".encode("utf-8"))
    return hashlib.sha256(b"".join(rows)).hexdigest()


def o_excl_json(path: Path, value: dict[str, Any]) -> None:
    encoded = canonical_bytes(value) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--mpfr", type=Path, required=True)
    parser.add_argument("--gmp", type=Path, required=True)
    parser.add_argument("--cc", type=Path, required=True)
    parser.add_argument("--ld", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    policy = json.loads(args.policy.read_text(encoding="utf-8"))
    successor = policy["successor_environment_epoch"]
    lock = successor["semantic_toolchain_lock"]
    lock_sha = hashlib.sha256(canonical_bytes(lock)).hexdigest()
    if lock_sha != successor["semantic_toolchain_lock_sha256"]:
        raise SystemExit("SEMANTIC_TOOLCHAIN_LOCK_HASH_MISMATCH")

    rustc = require_regular(args.rustc, "RUSTC", executable=True)
    python = require_regular(args.python, "PYTHON", executable=True)
    mpfr = require_regular(args.mpfr, "MPFR")
    gmp = require_regular(args.gmp, "GMP")
    cc = require_regular(args.cc, "CC", executable=True)
    ld = require_regular(args.ld, "LD", executable=True)

    rustc_version = run_text([str(rustc), "--version"])
    sysroot = Path(run_text([str(rustc), "--print", "sysroot"])).resolve(strict=True)
    target = lock["target"]
    driver = require_regular(sysroot / "lib/librustc_driver-83018425804cb0fc.so", "RUSTC_DRIVER")
    llvm = require_regular(sysroot / "lib/libLLVM.so.21.1-rust-1.94.1-stable", "LLVM")
    stdlib = (sysroot / f"lib/rustlib/{target}/lib").resolve(strict=True)

    observed = {
        "cc_sha256": sha256_file(cc),
        "gmp_sha256": sha256_file(gmp),
        "ld_sha256": sha256_file(ld),
        "llvm_sha256": sha256_file(llvm),
        "mpfr_sha256": sha256_file(mpfr),
        "precision_bits": 256,
        "python_sha256": sha256_file(python),
        "rounding_policy": "MPFR_RNDD_RNDU",
        "rustc_driver_sha256": sha256_file(driver),
        "rustc_sha256": sha256_file(rustc),
        "rustc_version": rustc_version,
        "stdlib_closure_sha256": stdlib_closure(stdlib),
        "target": target,
    }
    if observed != lock:
        mismatch = sorted(key for key in lock if observed.get(key) != lock[key])
        raise SystemExit("SUCCESSOR_SECTION0_SEMANTIC_MISMATCH:" + ",".join(mismatch))

    host_context = {
        "machine": platform.machine(),
        "node": platform.node(),
        "platform": platform.platform(),
        "python_runtime": platform.python_version(),
        "system": platform.system(),
    }
    host_epoch_fingerprint = hashlib.sha256(canonical_bytes(host_context)).hexdigest()
    receipt = {
        "schema": "rei-successor-section0-receipt/v1",
        "status": successor["required_status"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host_epoch_fingerprint": host_epoch_fingerprint,
        "host_identity_relation": successor["host_identity_relation"],
        "raw_receipt_relation": successor["raw_receipt_relation"],
        "semantic_toolchain_lock_sha256": lock_sha,
        "observed_toolchain": observed,
        "host_context": host_context,
        "historical_receipt": {
            "sha256": policy["historical_environment_epoch"]["section0_receipt_sha256"],
            "availability": "UNAVAILABLE_EXACT_BYTES",
            "reconstructed": false,
        },
        "claim_boundary": "HOST_REATTESTATION_ONLY_NATIVE_RUNTIME_NOT_RUN",
    }
    output = Path(args.output)
    if not output.is_absolute():
        raise SystemExit("SUCCESSOR_SECTION0_OUTPUT_NOT_ABSOLUTE")
    output.parent.resolve(strict=True)
    o_excl_json(output, receipt)
    print(json.dumps({"status": receipt["status"], "path": str(output), "sha256": sha256_file(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
