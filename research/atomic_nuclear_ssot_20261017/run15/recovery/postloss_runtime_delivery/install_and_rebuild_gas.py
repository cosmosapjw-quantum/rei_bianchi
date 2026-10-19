#!/usr/bin/env python3
"""Install inspected official Rust into /tmp and rebuild the unchanged gas server.

This bounded receipt generator never runs an IVP or cargo test.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import time
from pathlib import Path

EXPECTED_HEAD = "3dcb5f7aed8d33ff64f7952e9465f4239a216c89"
EXPECTED_GAS_SHA = "3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b"
EXPECTED_GAS_BYTES = 571904
EXPECTED_SOURCE_MAP = "7d04e35d4f77e7ee07e7e969f7a79e03623dbdbde33306dea54014202c172036"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while data := stream.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


def inventory(root: Path) -> list[dict]:
    out = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            out.append({"path": str(path.relative_to(root)), "symlink": os.readlink(path)})
        elif path.is_file():
            out.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha(path)})
    return out


def save(path: Path, data: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain-root", required=True, type=Path)
    parser.add_argument("--checkout-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    toolchain = args.toolchain_root.resolve(strict=True)
    checkout = args.checkout_root.resolve(strict=True)
    output = args.output_root.absolute()
    prefix = toolchain / "prefix"
    if prefix.exists() or output.exists() or output.is_symlink():
        raise ValueError("prefix and output must both be new")
    if not str(toolchain).startswith("/tmp/") or not str(output).startswith("/tmp/"):
        raise ValueError("all generated runtime artifacts must remain under /tmp")
    output.mkdir(parents=True)
    (output / "logs").mkdir()
    source = checkout / "research/atomic_nuclear_ssot_20261017/run13/recovered/code/rei_bass_coupled"
    source_map = source.parent.parent / "evidence/run13/UNCHANGED_INPUT_CODE.json"
    before = inventory(source)
    save(output / "SOURCE_BEFORE.json", before)
    receipt = {
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "IN_PROGRESS",
        "execution_environment": {"platform": platform.platform(), "python": platform.python_version()},
        "toolchain_prefix": str(prefix),
        "original_crate": str(source),
        "commands": [],
        "new_ivps": 0,
        "new_test_executions": 0,
        "binary_execution_probes": 0,
    }
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"

    def run(name: str, command: list[str], cwd: Path, timeout: float = 180) -> str:
        started = time.monotonic()
        print(json.dumps({"stage": name, "status": "STARTED", "command": command}), flush=True)
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=timeout)
        stdout = output / "logs" / (name + ".stdout.log")
        stderr = output / "logs" / (name + ".stderr.log")
        with stdout.open("xb") as stream:
            stream.write(result.stdout)
        with stderr.open("xb") as stream:
            stream.write(result.stderr)
        row = {"stage": name, "command": command, "cwd": str(cwd), "returncode": result.returncode,
               "seconds": time.monotonic() - started, "stdout": str(stdout), "stderr": str(stderr),
               "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)}
        receipt["commands"].append(row)
        print(json.dumps({"stage": name, "status": "COMPLETE" if result.returncode == 0 else "FAILED", "seconds": row["seconds"]}), flush=True)
        if result.returncode:
            raise RuntimeError(f"command failed: {name}, returncode={result.returncode}")
        return result.stdout.decode("utf-8")

    try:
        head = run("git_head", ["git", "rev-parse", "HEAD"], checkout).strip()
        if head != EXPECTED_HEAD:
            raise ValueError("unexpected recovered checkout HEAD")
        receipt["source_git_head"] = head
        if sha(source_map) != EXPECTED_SOURCE_MAP:
            raise ValueError("sealed source/input identity map changed")
        receipt["source_map_sha256"] = sha(source_map)
        official_receipt_path = toolchain / "OFFICIAL_COMPONENTS_RECEIPT.json"
        official = json.loads(official_receipt_path.read_text())
        receipt["official_components_receipt_sha256"] = sha(official_receipt_path)
        for row in official["components"]:
            component = row["component"]
            artifact = Path(row["extracted_root"])
            components = (artifact / "components").read_text().strip()
            if components not in {"rustc", "cargo", "rust-std-x86_64-unknown-linux-gnu"}:
                raise ValueError("unexpected installer component")
            command = ["sh", str(artifact / "install.sh"), "--prefix=" + str(prefix),
                       "--components=" + components, "--disable-ldconfig"]
            run("install_" + component, command, artifact)
        for key in list(env):
            if key.startswith("CARGO_") or key.startswith("RUSTFLAGS") or key in {
                "RUSTC", "RUSTC_WRAPPER", "RUSTC_WORKSPACE_WRAPPER", "RUSTDOC", "RUSTDOCFLAGS", "PYTHONPATH", "PYTHONHOME"
            }:
                env.pop(key)
        cargo_home = output / "cargo_home"
        target = output / "target"
        cargo_home.mkdir()
        target.mkdir()
        env.update({"PATH": str(prefix / "bin") + os.pathsep + os.environ.get("PATH", ""),
                    "LD_LIBRARY_PATH": str(prefix / "lib"), "RUSTC": str(prefix / "bin/rustc"),
                    "CARGO_HOME": str(cargo_home), "CARGO_TARGET_DIR": str(target), "CARGO_NET_OFFLINE": "true"})
        receipt["build_environment"] = {key: env[key] for key in ["PATH", "LD_LIBRARY_PATH", "RUSTC", "CARGO_HOME", "CARGO_TARGET_DIR", "CARGO_NET_OFFLINE"]}
        rustc = run("rustc_version", [str(prefix / "bin/rustc"), "--version", "--verbose"], output)
        cargo = run("cargo_version", [str(prefix / "bin/cargo"), "--version", "--verbose"], output)
        if "commit-hash: e408947bfd200af42db322daf0fadfe7e26d3bd1" not in rustc:
            raise ValueError("rustc identity differs from the historical compiler")
        if "commit-hash: 29ea6fb6a5db279426f4cc4e17aa385f05a0cfbc" not in cargo:
            raise ValueError("cargo identity differs from the historical compiler")
        if "host: x86_64-unknown-linux-gnu" not in rustc:
            raise ValueError("unexpected Rust target host")
        save(output / "INSTALLED_TOOLCHAIN_MANIFEST.json", inventory(prefix))
        run("gas_build", [str(prefix / "bin/cargo"), "build", "--release", "--offline", "--locked", "--example", "gas_rhs_server", "--jobs", "2"], source)
        binary = target / "release/examples/gas_rhs_server"
        actual = {"path": str(binary), "bytes": binary.stat().st_size, "sha256": sha(binary),
                  "expected_bytes": EXPECTED_GAS_BYTES, "expected_sha256": EXPECTED_GAS_SHA}
        actual["historical_byte_identity_match"] = actual["bytes"] == EXPECTED_GAS_BYTES and actual["sha256"] == EXPECTED_GAS_SHA
        receipt["rebuilt_gas_binary"] = actual
        after = inventory(source)
        save(output / "SOURCE_AFTER.json", after)
        receipt["original_source_inventory_unchanged"] = before == after
        if before != after:
            raise ValueError("original source inventory changed")
        if not actual["historical_byte_identity_match"]:
            raise ValueError("rebuilt binary SHA does not match the historical binary")
        receipt["status"] = "IMPLEMENTATION_VERIFIED"
    except Exception as exc:
        receipt["status"] = "FAILED_OR_BLOCKED"
        receipt["error"] = type(exc).__name__ + ": " + str(exc)
        save(output / "ORIGINAL_GAS_REBUILD_RECEIPT.json", receipt)
        print(json.dumps({"status": receipt["status"], "error": receipt["error"], "receipt": str(output / "ORIGINAL_GAS_REBUILD_RECEIPT.json")}), flush=True)
        raise
    save(output / "ORIGINAL_GAS_REBUILD_RECEIPT.json", receipt)
    print(json.dumps({"status": receipt["status"], "binary": receipt["rebuilt_gas_binary"], "receipt": str(output / "ORIGINAL_GAS_REBUILD_RECEIPT.json")}), flush=True)


if __name__ == "__main__":
    main()
