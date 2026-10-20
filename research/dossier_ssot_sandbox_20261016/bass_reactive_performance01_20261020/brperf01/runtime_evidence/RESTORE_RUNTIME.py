#!/usr/bin/env python3
"""Restore the isolated, checksum-pinned BRPERF01 runtime into a fresh directory.

Usage: python3 RESTORE_RUNTIME.py RUST_ARCHIVE REGISTRY_ARCHIVE NEW_RUNTIME_DIR
Python 3.12+ is required for tarfile's data extraction filter.
No network access, user home installation, or ldconfig operation is requested.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile

RUST_SHA = "294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40"
REGISTRY_SHA = "a609f400af02d432e16956ef44d4ba5187a5a9b5360a9f6218f1d540818b3292"
RUST_ROOT = "rust-1.94.1-x86_64-unknown-linux-gnu"
COMPONENTS = (
    "rustc",
    "cargo",
    "rust-std-x86_64-unknown-linux-gnu",
    "rustfmt-preview",
    "clippy-preview",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"Checksum mismatch for {path}: {actual}")


def validate_member(member: tarfile.TarInfo, root: str) -> None:
    path = Path(member.name)
    if path.is_absolute() or ".." in path.parts or path.parts[0] != root:
        raise ValueError(f"Unsafe archive member: {member.name}")
    if (member.issym() or member.islnk()) and Path(member.linkname).is_absolute():
        raise ValueError(f"Absolute archive link: {member.name}")


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    rust_archive, registry_archive, destination = map(
        lambda value: Path(value).resolve(), sys.argv[1:]
    )
    require_hash(rust_archive, RUST_SHA)
    require_hash(registry_archive, REGISTRY_SHA)
    if destination.exists():
        raise ValueError("The runtime destination must be a new directory.")
    destination.mkdir(parents=True)
    installer = destination / "installer"
    installer.mkdir()
    with tarfile.open(rust_archive, "r|xz") as archive:
        for member in archive:
            validate_member(member, RUST_ROOT)
            parts = Path(member.name).parts
            selected = len(parts) <= 2 or parts[1] in COMPONENTS
            if len(parts) == 2 and member.isdir() and parts[1] not in COMPONENTS:
                selected = False
            if selected:
                archive.extract(member, installer, filter="data")
    prefix = destination / "rust-1.94.1"
    command = [
        "bash",
        str(installer / RUST_ROOT / "install.sh"),
        f"--prefix={prefix}",
        f"--components={','.join(COMPONENTS)}",
        "--disable-ldconfig",
    ]
    installed = subprocess.run(command, capture_output=True, text=True, check=False)
    (destination / "INSTALL.log").write_text(installed.stdout + installed.stderr)
    installed.check_returncode()
    vendor = destination / "vendor"
    vendor.mkdir()
    with tarfile.open(registry_archive, "r:gz") as archive:
        for member in archive:
            validate_member(member, "registry")
            archive.extract(member, vendor, filter="data")
    registry = vendor / "registry"
    package_count, payload_count = 0, 0
    for checksum_path in sorted(registry.glob("*/.cargo-checksum.json")):
        package_count += 1
        checks = json.loads(checksum_path.read_text())
        for name, expected in checks["files"].items():
            require_hash(checksum_path.parent / name, expected)
            payload_count += 1
    if (package_count, payload_count) != (99, 4944):
        raise ValueError(f"Registry inventory mismatch: {package_count}, {payload_count}")
    cargo_home = destination / "cargo_home"
    cargo_home.mkdir()
    (cargo_home / "config.toml").write_text(
        '[source.crates-io]\nreplace-with = "brperf-vendored"\n\n'
        '[source.brperf-vendored]\n'
        f"directory = {json.dumps(str(registry))}\n\n[net]\noffline = true\n"
    )
    env_path = destination / "env.sh"
    env_path.write_text(
        "# Source this file for the isolated BRPERF01 Rust 1.94.1 runtime.\n"
        f"export BRPERF01_RUST_PREFIX={shlex.quote(str(prefix))}\n"
        'export PATH="$BRPERF01_RUST_PREFIX/bin:$PATH"\n'
        'export LD_LIBRARY_PATH="$BRPERF01_RUST_PREFIX/lib:${LD_LIBRARY_PATH:-}"\n'
        f"export CARGO_HOME={shlex.quote(str(cargo_home))}\n"
    )
    print(json.dumps({"env": str(env_path), "registry": str(registry)}, indent=2))


if __name__ == "__main__":
    main()
