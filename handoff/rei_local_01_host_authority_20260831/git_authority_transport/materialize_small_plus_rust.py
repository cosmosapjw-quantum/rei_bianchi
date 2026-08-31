#!/usr/bin/env python3
"""Fail-closed staged intake for four Git blobs plus one Rust archive.

This tool does not execute, extract, or source any authority member.  It
preflights all five exact bytes through stable file descriptors before creating
the staged source root consumed by ``materialize_authority.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ERROR_PREFIX = "STOP_INVALID_GIT_SMALL_PLUS_RUST"
SMALL_MANIFEST_SCHEMA = "rei-host-authority-git-small-inputs/v1"
SMALL_MANIFEST_CLASSIFICATION = "BYTE_IDENTITY_DIRECT_GIT_BLOBS"
CONTRACT_SCHEMA = "rei-host-authority-materialization/v1"
CONTRACT_CLASSIFICATION = "EXACT_EXTERNAL_INPUT_BYTES"
RUST_ARCHIVE_NAME = "08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz"
CHUNK_SIZE = 1024 * 1024


class ContractError(RuntimeError):
    """A byte-identity, path, or publication invariant was violated."""


@dataclass(frozen=True)
class ExpectedFile:
    name: str
    size: int
    sha256: str
    origin: str


@dataclass
class VerifiedFile:
    expected: ExpectedFile
    source_path: Path
    descriptor: int


def _sha256_from_descriptor(descriptor: int) -> str:
    digest = hashlib.sha256()
    os.lseek(descriptor, 0, os.SEEK_SET)
    while True:
        chunk = os.read(descriptor, CHUNK_SIZE)
        if not chunk:
            break
        digest.update(chunk)
    os.lseek(descriptor, 0, os.SEEK_SET)
    return digest.hexdigest()


def _sha256_path(path: Path) -> str:
    descriptor = _open_regular_non_symlink(path, "metadata")
    try:
        return _sha256_from_descriptor(descriptor)
    finally:
        os.close(descriptor)


def _normal_absolute(path: Path, label: str) -> Path:
    absolute = Path(os.path.abspath(os.fspath(path)))
    if Path(os.path.realpath(absolute)) != absolute:
        raise ContractError(f"{label} must not traverse a symlink: {absolute}")
    return absolute


def _real_directory(path: Path, label: str) -> Path:
    absolute = _normal_absolute(path, label)
    try:
        mode = os.lstat(absolute).st_mode
    except FileNotFoundError as error:
        raise ContractError(f"{label} is missing: {absolute}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise ContractError(f"{label} must be a real non-symlink directory: {absolute}")
    return absolute


def _open_regular_non_symlink(path: Path, label: str) -> int:
    try:
        before = os.lstat(path)
    except FileNotFoundError as error:
        raise ContractError(f"{label} is missing: {path}") from error
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise ContractError(f"{label} must be a regular non-symlink file: {path}")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ContractError(f"could not open {label} without following links: {path}: {error}") from error
    try:
        observed = os.fstat(descriptor)
        if not stat.S_ISREG(observed.st_mode):
            raise ContractError(f"{label} must remain a regular non-symlink file: {path}")
        if (before.st_dev, before.st_ino) != (observed.st_dev, observed.st_ino):
            raise ContractError(f"{label} changed while opening: {path}")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _read_json_regular(path: Path, label: str) -> tuple[dict[str, Any], str]:
    descriptor = _open_regular_non_symlink(path, label)
    try:
        pieces: list[bytes] = []
        while True:
            chunk = os.read(descriptor, CHUNK_SIZE)
            if not chunk:
                break
            pieces.append(chunk)
        raw = b"".join(pieces)
    finally:
        os.close(descriptor)
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is not valid UTF-8 JSON: {path}") from error
    if not isinstance(parsed, dict):
        raise ContractError(f"{label} must be a JSON object: {path}")
    return parsed, hashlib.sha256(raw).hexdigest()


def _field_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{label} must be a non-empty string")
    return value


def _field_size(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError(f"{label} must be a non-negative integer")
    return value


def _field_sha256(value: Any, label: str) -> str:
    candidate = _field_string(value, label)
    if len(candidate) != 64 or any(character not in "0123456789abcdef" for character in candidate):
        raise ContractError(f"{label} must be a lowercase SHA-256 digest")
    return candidate


def _safe_basename(name: str, label: str) -> str:
    if Path(name).name != name or name in {".", ".."}:
        raise ContractError(f"{label} must be a basename")
    return name


def _expected_from_contract(contract: dict[str, Any]) -> dict[str, ExpectedFile]:
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise ContractError("contract schema is not admitted")
    if contract.get("classification") != CONTRACT_CLASSIFICATION:
        raise ContractError("contract classification is not admitted")
    entries = contract.get("files")
    if not isinstance(entries, list) or len(entries) != 5:
        raise ContractError("contract must declare exactly five files")

    expected: dict[str, ExpectedFile] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ContractError(f"contract files[{index}] must be an object")
        source = _safe_basename(_field_string(entry.get("source"), f"contract files[{index}].source"), "contract source")
        destination = _safe_basename(
            _field_string(entry.get("destination"), f"contract files[{index}].destination"),
            "contract destination",
        )
        if source != destination:
            raise ContractError(f"contract source and destination must match for {source}")
        if source in expected:
            raise ContractError(f"contract has duplicate file {source}")
        expected[source] = ExpectedFile(
            name=source,
            size=_field_size(entry.get("size"), f"contract files[{index}].size"),
            sha256=_field_sha256(entry.get("sha256"), f"contract files[{index}].sha256"),
            origin="external-rust-archive" if source == RUST_ARCHIVE_NAME else "git-resident-small-input",
        )

    if RUST_ARCHIVE_NAME not in expected:
        raise ContractError(f"contract is missing {RUST_ARCHIVE_NAME}")
    if len(expected) != 5:
        raise ContractError("contract has an invalid file set")
    return expected


def _validate_small_manifest(manifest: dict[str, Any], expected: dict[str, ExpectedFile]) -> tuple[str, ...]:
    if manifest.get("schema") != SMALL_MANIFEST_SCHEMA:
        raise ContractError("small-input manifest schema is not admitted")
    if manifest.get("classification") != SMALL_MANIFEST_CLASSIFICATION:
        raise ContractError("small-input manifest classification is not admitted")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) != 4:
        raise ContractError("small-input manifest must declare exactly four files")

    observed: list[str] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ContractError(f"small-input manifest files[{index}] must be an object")
        name = _safe_basename(_field_string(entry.get("filename"), f"small-input manifest files[{index}].filename"), "small-input filename")
        if name == RUST_ARCHIVE_NAME or name not in expected:
            raise ContractError(f"small-input manifest declares an unadmitted file: {name}")
        if name in observed:
            raise ContractError(f"small-input manifest has duplicate file {name}")
        candidate = expected[name]
        if _field_size(entry.get("size"), f"small-input manifest files[{index}].size") != candidate.size:
            raise ContractError(f"small-input manifest size disagrees with contract for {name}")
        if _field_sha256(entry.get("sha256"), f"small-input manifest files[{index}].sha256") != candidate.sha256:
            raise ContractError(f"small-input manifest digest disagrees with contract for {name}")
        observed.append(name)

    expected_small = {name for name in expected if name != RUST_ARCHIVE_NAME}
    if set(observed) != expected_small:
        raise ContractError("small-input manifest does not exactly cover the four contract small inputs")
    return tuple(observed)


def _verify_member(root: Path, expected: ExpectedFile) -> VerifiedFile:
    path = root / expected.name
    descriptor = _open_regular_non_symlink(path, expected.origin)
    try:
        observed = os.fstat(descriptor)
        if observed.st_size != expected.size:
            raise ContractError(
                f"{expected.origin} size mismatch for {expected.name}: expected {expected.size}, observed {observed.st_size}"
            )
        observed_digest = _sha256_from_descriptor(descriptor)
        if observed_digest != expected.sha256:
            raise ContractError(
                f"{expected.origin} SHA-256 mismatch for {expected.name}: expected {expected.sha256}, observed {observed_digest}"
            )
    except BaseException:
        os.close(descriptor)
        raise
    return VerifiedFile(expected=expected, source_path=path, descriptor=descriptor)


def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise OSError("short write while publishing authority bytes")
        offset += written


def _copy_verified(source: VerifiedFile, destination: Path) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(destination, flags, 0o444)
    try:
        digest = hashlib.sha256()
        copied = 0
        os.lseek(source.descriptor, 0, os.SEEK_SET)
        while True:
            chunk = os.read(source.descriptor, CHUNK_SIZE)
            if not chunk:
                break
            _write_all(descriptor, chunk)
            digest.update(chunk)
            copied += len(chunk)
        os.fsync(descriptor)
        if copied != source.expected.size or digest.hexdigest() != source.expected.sha256:
            raise ContractError(f"copy verification failed for {source.expected.name}")
    finally:
        os.close(descriptor)
    os.chmod(destination, 0o444)


def _publish_new_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o444)
    try:
        _write_all(descriptor, encoded)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.chmod(path, 0o444)


def _remove_created_directory(path: Path) -> None:
    if not os.path.lexists(path):
        return
    for child in path.iterdir():
        child.unlink()
    path.rmdir()


def _paths_overlap(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def _preflight_destinations(destination_root: Path, receipt: Path, git_small_root: Path, rust_source_root: Path) -> tuple[Path, Path]:
    destination = Path(os.path.abspath(os.fspath(destination_root)))
    receipt_path = Path(os.path.abspath(os.fspath(receipt)))
    destination_parent = _real_directory(destination.parent, "destination parent")
    receipt_parent = _real_directory(receipt_path.parent, "receipt parent")
    if os.path.lexists(destination):
        raise ContractError(f"destination root already exists: {destination}")
    if os.path.lexists(receipt_path):
        raise ContractError(f"receipt already exists: {receipt_path}")
    if any(_paths_overlap(destination, source_root) for source_root in (git_small_root, rust_source_root)):
        raise ContractError("destination root must not overlap either source root")
    if receipt_path.parent == destination:
        raise ContractError("receipt must be outside the newly created destination root")
    return destination_parent / destination.name, receipt_parent / receipt_path.name


def materialize(
    git_small_root: Path,
    rust_source_root: Path,
    contract_path: Path,
    small_manifest_path: Path,
    destination_root: Path,
    receipt_path: Path,
) -> None:
    git_root = _real_directory(git_small_root, "Git small-input root")
    rust_root = _real_directory(rust_source_root, "Rust archive source root")
    if git_root == rust_root:
        raise ContractError("Git small-input root and Rust archive source root must be distinct")
    contract, contract_sha256 = _read_json_regular(_normal_absolute(contract_path, "contract"), "contract")
    small_manifest, small_manifest_sha256 = _read_json_regular(
        _normal_absolute(small_manifest_path, "small-input manifest"), "small-input manifest"
    )
    expected = _expected_from_contract(contract)
    small_names = _validate_small_manifest(small_manifest, expected)
    destination, receipt = _preflight_destinations(destination_root, receipt_path, git_root, rust_root)

    verified: list[VerifiedFile] = []
    destination_created = False
    receipt_created = False
    try:
        for name in small_names:
            verified.append(_verify_member(git_root, expected[name]))
        verified.append(_verify_member(rust_root, expected[RUST_ARCHIVE_NAME]))

        os.mkdir(destination, 0o755)
        destination_created = True
        for source in verified:
            _copy_verified(source, destination / source.expected.name)

        receipt_payload = {
            "schema": "rei-host-authority-mixed-source-receipt/v1",
            "classification": "BYTE_IDENTITY_MIXED_SOURCE_ASSEMBLY",
            "contract_sha256": contract_sha256,
            "small_inputs_manifest_sha256": small_manifest_sha256,
            "staged_source_root": str(destination),
            "origins": {source.expected.name: source.expected.origin for source in verified},
            "files": [
                {
                    "name": source.expected.name,
                    "size": source.expected.size,
                    "sha256": source.expected.sha256,
                }
                for source in verified
            ],
        }
        _publish_new_json(receipt, receipt_payload)
        receipt_created = True
    except BaseException:
        if receipt_created and os.path.lexists(receipt):
            receipt.unlink()
        if destination_created:
            _remove_created_directory(destination)
        raise
    finally:
        for source in verified:
            os.close(source.descriptor)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-small-root", type=Path, required=True)
    parser.add_argument("--rust-source-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--small-manifest", type=Path, required=True)
    parser.add_argument("--destination-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        materialize(
            arguments.git_small_root,
            arguments.rust_source_root,
            arguments.contract,
            arguments.small_manifest,
            arguments.destination_root,
            arguments.receipt,
        )
    except (ContractError, OSError) as error:
        print(f"{ERROR_PREFIX}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
