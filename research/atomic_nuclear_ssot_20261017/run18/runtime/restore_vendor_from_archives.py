#!/usr/bin/env python3
"""Restore the five locked pure-Rust dependencies without network or Cargo.

Inputs are the published runtime directory, its Cargo.lock, official metadata,
and preserved .crate bytes. The output workspace must not already exist.
Original files and the historical producer configuration remain untouched.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import platform
import sys
import tarfile
import tomllib

EXPECTED = {
    "num-rational": "0.4.2", "num-bigint": "0.4.6",
    "num-integer": "0.1.46", "num-traits": "0.2.19", "autocfg": "1.5.0",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def identity(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path.resolve()), "bytes": len(raw), "sha256": sha(raw)}


def save(path: Path, data: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def read_members(payload: bytes, stem: str) -> list[tuple[str, bytes]]:
    files = []
    seen = set()
    expanded = 0
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member in archive.getmembers():
            name = member.name.rstrip("/") if member.isdir() else member.name
            path = PurePosixPath(name)
            if ("\\" in name or path.is_absolute() or ".." in path.parts
                    or not path.parts or path.parts[0] != stem
                    or str(path) != name or name in seen):
                raise ValueError(f"unsafe or duplicate member: {member.name!r}")
            seen.add(name)
            if member.isdir():
                continue
            if not member.isfile() or len(path.parts) < 2 or member.size > 2_000_000:
                raise ValueError("only bounded regular-file members are supported")
            expanded += member.size
            if expanded > 8_000_000:
                raise ValueError("expanded crate exceeds bounded restore size")
            relative = str(PurePosixPath(*path.parts[1:]))
            if relative == ".cargo-checksum.json":
                raise ValueError("unexpected producer vendor checksum inside crate")
            with archive.extractfile(member) as stream:
                raw = stream.read(member.size + 1)
            if len(raw) != member.size:
                raise ValueError("member byte count mismatch")
            files.append((relative, raw))
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--workspace-dir", type=Path, required=True)
    args = parser.parse_args()
    source = args.runtime_root.resolve()
    workspace = args.workspace_dir.resolve()
    if workspace.exists():
        raise FileExistsError("a new workspace directory is required")
    lock_path = source / "exact_dense_adapter/Cargo.lock"
    receipt_path = source / "CRATE_DOWNLOAD_RECEIPT.json"
    locked = tomllib.loads(lock_path.read_text(encoding="utf-8"))["package"]
    dependencies = [row for row in locked if "source" in row]
    if {row["name"]: row["version"] for row in dependencies} != EXPECTED:
        raise ValueError("Cargo.lock does not contain the expected five dependencies")
    downloaded = json.loads(receipt_path.read_text(encoding="utf-8"))["packages"]
    recorded = {(row["crate"], row["version"]): row for row in downloaded}
    plan = []
    for package in sorted(dependencies, key=lambda row: row["name"]):
        name, version = package["name"], package["version"]
        stem = f"{name}-{version}"
        record = recorded[name, version]
        archive_path = source / "crate_downloads" / f"{stem}.crate"
        metadata_path = source / "official_metadata" / f"{stem}.json"
        payload = archive_path.read_bytes()
        metadata_raw = metadata_path.read_bytes()
        metadata = json.loads(metadata_raw)["version"]
        checksum = sha(payload)
        if (checksum != package["checksum"] or checksum != record["archive_sha256"]
                or checksum != metadata["checksum"]
                or len(payload) != record["archive_bytes"]
                or len(payload) != metadata["crate_size"]
                or sha(metadata_raw) != record["metadata_sha256"]):
            raise ValueError(f"locked/archive/official-metadata identity mismatch: {stem}")
        files = read_members(payload, stem)
        if (len(files) != record["files"]
                or sum(len(raw) for _, raw in files) != record["expanded_bytes"]):
            raise ValueError(f"archive inventory differs from producer receipt: {stem}")
        plan.append((stem, files, checksum, identity(archive_path)))
    workspace.mkdir(parents=True, exist_ok=False)
    vendor = workspace / "vendor"
    vendor.mkdir()
    restored = []
    for stem, files, checksum, archive_identity in plan:
        destination = vendor / stem
        destination.mkdir()
        checksums = {}
        for relative, raw in files:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(raw)
            if sha(target.read_bytes()) != sha(raw):
                raise IOError("restored file failed readback identity")
            checksums[relative] = sha(raw)
        with (destination / ".cargo-checksum.json").open("x", encoding="utf-8") as stream:
            json.dump({"files": checksums, "package": checksum}, stream, sort_keys=True)
            stream.write("\n")
        restored.append({"package": stem, "archive": archive_identity,
            "files": len(files), "expanded_bytes": sum(len(raw) for _, raw in files),
            "all_regular_file_bytes_verified": True,
            "cargo_checksum_file": identity(destination / ".cargo-checksum.json")})
    config = workspace / "vendor_config.toml"
    with config.open("x", encoding="utf-8") as stream:
        stream.write('[source.crates-io]\nreplace-with = "preserved-crates"\n\n')
        stream.write('[source.preserved-crates]\ndirectory = ' + json.dumps(str(vendor)) + '\n')
    result = {"schema": "rei.run18.offline-vendor-restore.v1",
        "status": "IMPLEMENTATION_VERIFIED_DEPENDENCY_BYTE_RESTORATION",
        "source_runtime": str(source), "workspace": str(workspace),
        "lock": identity(lock_path), "download_receipt": identity(receipt_path),
        "helper": identity(Path(__file__)), "packages": restored,
        "packages_restored": len(restored), "inari_restored": False,
        "network_requests": 0, "cargo_builds": 0, "tests": 0,
        "native_gas_RHS_calls": 0, "new_IVP_solves": 0,
        "config": identity(config), "command_argv": sys.argv,
        "python": sys.version, "platform": platform.platform()}
    save(workspace / "OFFLINE_VENDOR_RESTORE.json", result)
    print(json.dumps({"status": result["status"], "packages_restored": len(restored),
                      "config": str(config), "network_requests": 0, "cargo_builds": 0}))


if __name__ == "__main__":
    main()
