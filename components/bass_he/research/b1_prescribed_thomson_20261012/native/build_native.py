"""Build only the source-pinned Thomson module and its C ABI boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
SOURCE_SHA256 = "e2472459aaf0f6b404010306fa6302801d2e21470079ba9f80c625bbc0f6ad6b"
SOURCE_COMMIT = "2325a42c0954e949bb57f53976d0c9a9d9a9a362"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rustc", default=None)
    parser.add_argument("--output", type=Path, default=ROOT / "libb1_thomson.so")
    args = parser.parse_args()
    actual = hashlib.sha256((ROOT / "pol_collide.rs").read_bytes()).hexdigest()
    if actual != SOURCE_SHA256:
        raise RuntimeError("Pinned pol_collide.rs byte identity mismatch")
    compiler = args.rustc or shutil.which("rustc")
    if not compiler:
        raise RuntimeError("Rust compiler unavailable; no native execution or fallback was performed")
    output = args.output.resolve()
    command = [compiler, "--edition=2021", "--crate-type=cdylib", "-C", "opt-level=3",
               "-C", "panic=unwind", "--crate-name=b1_thomson", str(ROOT / "lib.rs"),
               "-o", str(output)]
    start = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True)
    receipt = {"command": command, "returncode": proc.returncode,
               "compiler_version": subprocess.run([compiler, "--version"], capture_output=True,
                                                  text=True, check=True).stdout.strip(),
               "wall_s": time.perf_counter() - start,
               "stdout": proc.stdout, "stderr": proc.stderr,
               "kernel_sha256": actual, "kernel_commit": SOURCE_COMMIT,
               "kernel_repository": "cosmosapjw-quantum/bass",
               "kernel_path": "_rustcore/src/kinetic/pol_collide.rs",
               "physics_invocations": 0}
    if proc.returncode == 0:
        receipt["binary_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        receipt["binary_bytes"] = output.stat().st_size
    (ROOT / "NATIVE_BUILD_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    if proc.returncode:
        raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
