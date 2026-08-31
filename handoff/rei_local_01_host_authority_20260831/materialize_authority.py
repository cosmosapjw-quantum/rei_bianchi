#!/usr/bin/env python3
"""Verify and materialize sealed input bytes without executing them.

This utility is intentionally limited to byte intake.  It does not inspect an
archive's members, source an environment file, import repository code, or
start any runtime/scientific gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import stat
import sys
from typing import Any


SCHEMA = "rei-host-authority-materialization/v1"
CLASSIFICATION = "EXACT_EXTERNAL_INPUT_BYTES"
RECEIPT_SCHEMA = "rei-host-authority-materialization-receipt/v1"
CANONICAL_CONTRACT_SHA256 = (
    "3a0811cd19c10a5acaead1b328aaafe45a7f167f977ab13e19f4a17184d96122"
)
CHUNK_SIZE = 1024 * 1024


class MaterializationError(RuntimeError):
    """A fail-closed authority intake rejection."""


def _absolute(path: os.PathLike[str] | str) -> Path:
    # Deliberately do not call resolve(): following a symlink is an intake
    # failure, not a normalization step.
    return Path(os.path.abspath(os.fspath(path)))


def _assert_existing_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise MaterializationError(f"{label} does not exist: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise MaterializationError(f"{label} must be a non-symlink directory: {path}")
    _assert_no_symlink_components(path, label)


def _assert_no_symlink_components(path: Path, label: str) -> None:
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            return
        if stat.S_ISLNK(metadata.st_mode):
            raise MaterializationError(f"{label} contains a symlink component: {current}")


def _ensure_directory(path: Path, label: str) -> None:
    _assert_no_symlink_components(path, label)
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    _assert_existing_directory(current, label)
    for directory in reversed(missing):
        try:
            directory.mkdir(mode=0o755)
        except FileExistsError:
            pass
        metadata = directory.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise MaterializationError(
                f"{label} must remain a non-symlink directory: {directory}"
            )


def _safe_relative(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise MaterializationError(f"{field} must be a safe relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise MaterializationError(f"{field} must be a safe relative path: {value!r}")
    if str(pure) != value:
        raise MaterializationError(f"{field} must be a safe relative path: {value!r}")
    return Path(*pure.parts)


def _is_within_or_equal(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _paths_overlap(left: Path, right: Path) -> bool:
    return _is_within_or_equal(left, right) or _is_within_or_equal(right, left)


def _open_regular_readonly(path: Path, label: str) -> tuple[int, os.stat_result]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except (FileNotFoundError, OSError) as exc:
        raise MaterializationError(f"{label} must be a regular non-symlink file: {path}") from exc
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode):
        os.close(descriptor)
        raise MaterializationError(f"{label} must be a regular non-symlink file: {path}")
    return descriptor, metadata


def _sha256_and_size(path: Path, label: str) -> tuple[str, int]:
    descriptor, before = _open_regular_readonly(path, label)
    digest = hashlib.sha256()
    size = 0
    try:
        while True:
            block = os.read(descriptor, CHUNK_SIZE)
            if not block:
                break
            digest.update(block)
            size += len(block)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after:
        raise MaterializationError(f"{label} changed while being verified: {path}")
    return digest.hexdigest(), size


def _read_regular_bytes(path: Path, label: str) -> tuple[bytes, str]:
    descriptor, before = _open_regular_readonly(path, label)
    digest = hashlib.sha256()
    blocks: list[bytes] = []
    try:
        while True:
            block = os.read(descriptor, CHUNK_SIZE)
            if not block:
                break
            digest.update(block)
            blocks.append(block)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after:
        raise MaterializationError(f"{label} changed while being read: {path}")
    return b"".join(blocks), digest.hexdigest()


def _read_contract(path: Path) -> tuple[dict[str, Any], str]:
    try:
        payload, digest = _read_regular_bytes(path, "contract")
        parsed = json.loads(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaterializationError(f"contract is not valid UTF-8 JSON: {path}") from exc
    if not isinstance(parsed, dict) or set(parsed) != {
        "schema",
        "classification",
        "files",
    }:
        raise MaterializationError("contract must contain exactly schema, classification, and files")
    if parsed["schema"] != SCHEMA or parsed["classification"] != CLASSIFICATION:
        raise MaterializationError("contract schema or classification is not admitted")
    if not isinstance(parsed["files"], list) or not parsed["files"]:
        raise MaterializationError("contract files must be a non-empty list")
    return parsed, digest


def _validate_entries(raw_entries: list[Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    seen_destinations: set[str] = set()
    for index, raw in enumerate(raw_entries):
        if not isinstance(raw, dict) or set(raw) != {
            "source",
            "destination",
            "size",
            "sha256",
        }:
            raise MaterializationError(f"files[{index}] has an invalid shape")
        source = _safe_relative(raw["source"], f"files[{index}].source")
        destination = _safe_relative(raw["destination"], f"files[{index}].destination")
        size = raw["size"]
        sha256 = raw["sha256"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise MaterializationError(f"files[{index}].size must be a non-negative integer")
        if (
            not isinstance(sha256, str)
            or len(sha256) != 64
            or sha256 != sha256.lower()
            or any(character not in "0123456789abcdef" for character in sha256)
        ):
            raise MaterializationError(f"files[{index}].sha256 must be lowercase SHA-256")
        source_key = source.as_posix()
        destination_key = destination.as_posix()
        if source_key in seen_sources:
            raise MaterializationError(f"duplicate source path: {source_key}")
        if destination_key in seen_destinations:
            raise MaterializationError(f"duplicate destination path: {destination_key}")
        seen_sources.add(source_key)
        seen_destinations.add(destination_key)
        entries.append(
            {
                "source": source,
                "destination": destination,
                "size": size,
                "sha256": sha256,
            }
        )
    source_order = [entry["source"].as_posix() for entry in entries]
    destination_order = [entry["destination"].as_posix() for entry in entries]
    if source_order != sorted(source_order) or destination_order != sorted(destination_order):
        raise MaterializationError("contract entries must be sorted by source and destination")
    destinations = [entry["destination"] for entry in entries]
    for index, left in enumerate(destinations):
        for right in destinations[index + 1 :]:
            if _paths_overlap(left, right):
                raise MaterializationError(
                    "contract destinations have an ancestor collision: "
                    f"{left.as_posix()} and {right.as_posix()}"
                )
    return entries


def _verify_expected(path: Path, entry: dict[str, Any], label: str) -> None:
    observed_hash, observed_size = _sha256_and_size(path, label)
    if observed_size != entry["size"]:
        raise MaterializationError(
            f"{label} size mismatch for {path}: expected {entry['size']}, observed {observed_size}"
        )
    if observed_hash != entry["sha256"]:
        raise MaterializationError(
            f"{label} SHA-256 mismatch for {path}: expected {entry['sha256']}, "
            f"observed {observed_hash}"
        )


def _preflight_destination(path: Path, entry: dict[str, Any]) -> bool:
    _assert_no_symlink_components(path.parent, "destination parent")
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise MaterializationError(f"destination conflict (not a regular file): {path}")
    try:
        _verify_expected(path, entry, "destination")
    except MaterializationError as exc:
        raise MaterializationError(f"destination conflict: {path}: {exc}") from exc
    return True


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _close_quietly(descriptor: int | None) -> None:
    if descriptor is None:
        return
    try:
        os.close(descriptor)
    except OSError:
        pass


def _copy_create_only(source: Path, destination: Path, entry: dict[str, Any]) -> None:
    _ensure_directory(destination.parent, "destination parent")
    temporary = destination.parent / (
        f".{destination.name}.rei-materialize-{os.getpid()}-{secrets.token_hex(8)}.tmp"
    )
    source_descriptor: int | None = None
    temporary_descriptor: int | None = None
    try:
        source_descriptor, before = _open_regular_readonly(source, "source")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        temporary_descriptor = os.open(temporary, flags, 0o600)
        digest = hashlib.sha256()
        size = 0
        while True:
            block = os.read(source_descriptor, CHUNK_SIZE)
            if not block:
                break
            digest.update(block)
            size += len(block)
            view = memoryview(block)
            while view:
                written = os.write(temporary_descriptor, view)
                view = view[written:]
        after = os.fstat(source_descriptor)
        if (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise MaterializationError(f"source changed while being copied: {source}")
        if size != entry["size"]:
            raise MaterializationError(f"source size mismatch while copying: {source}")
        if digest.hexdigest() != entry["sha256"]:
            raise MaterializationError(f"source SHA-256 mismatch while copying: {source}")
        os.fchmod(temporary_descriptor, 0o444)
        os.fsync(temporary_descriptor)
        os.close(source_descriptor)
        source_descriptor = None
        os.close(temporary_descriptor)
        temporary_descriptor = None
        try:
            os.link(temporary, destination, follow_symlinks=False)
        except FileExistsError as exc:
            raise MaterializationError(
                f"destination appeared during create-only copy: {destination}"
            ) from exc
        _fsync_directory(destination.parent)
    finally:
        _close_quietly(source_descriptor)
        _close_quietly(temporary_descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _install_receipt_create_only(path: Path, payload: bytes) -> None:
    _ensure_directory(path.parent, "receipt parent")
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        metadata = None
    if metadata is not None:
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise MaterializationError(f"receipt conflict: {path}")
        observed_payload, _ = _read_regular_bytes(path, "receipt")
        if observed_payload != payload:
            raise MaterializationError(f"receipt conflict: {path}")
        return
    temporary = path.parent / f".{path.name}.rei-receipt-{os.getpid()}-{secrets.token_hex(8)}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(temporary, flags, 0o600)
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exc:
            raise MaterializationError(f"receipt appeared during create-only write: {path}") from exc
        _fsync_directory(path.parent)
    finally:
        _close_quietly(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _materialize(
    *,
    contract_path: os.PathLike[str] | str,
    source_root: os.PathLike[str] | str,
    destination_root: os.PathLike[str] | str,
    receipt_path: os.PathLike[str] | str,
    require_canonical_contract: bool,
) -> dict[str, Any]:
    """Materialize contract-listed bytes after applying the requested policy."""

    contract = _absolute(contract_path)
    source = _absolute(source_root)
    destination = _absolute(destination_root)
    receipt = _absolute(receipt_path)
    _assert_existing_directory(source, "source root")
    if _paths_overlap(source, destination):
        raise MaterializationError("source and destination roots must not overlap")
    _assert_no_symlink_components(contract, "contract")
    parsed, contract_digest = _read_contract(contract)
    if require_canonical_contract and contract_digest != CANONICAL_CONTRACT_SHA256:
        raise MaterializationError(
            "canonical contract SHA-256 mismatch: "
            f"expected {CANONICAL_CONTRACT_SHA256}, observed {contract_digest}"
        )
    entries = _validate_entries(parsed["files"])
    _ensure_directory(destination, "destination root")

    if _paths_overlap(receipt, source):
        raise MaterializationError("receipt path must not overlap the source authority root")

    receipt_document: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "status": "AUTHORITY_BYTES_MATERIALIZED",
        "identity_class": "BYTE_IDENTITY",
        "contract_path": str(contract),
        "contract_sha256": contract_digest,
        "source_root": str(source),
        "destination_root": str(destination),
        "files": [
            {
                "source": entry["source"].as_posix(),
                "destination": entry["destination"].as_posix(),
                "size": entry["size"],
                "sha256": entry["sha256"],
                "status": "VERIFIED",
            }
            for entry in entries
        ],
        "runtime_boundary": "NOT_RUN",
        "path_stability": "POINT_IN_TIME_NO_CONCURRENT_WRITER_CLAIM",
        "concurrent_writer_exclusion": "REQUIRED_NOT_KERNEL_ENFORCED",
        "scientific_gates": "NOT_RUN",
        "canonical_pilot": "NOT_RUN",
        "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
    }
    receipt_payload = (
        json.dumps(receipt_document, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")

    destination_paths = {destination / entry["destination"] for entry in entries}
    if any(_paths_overlap(receipt, path) for path in destination_paths):
        raise MaterializationError(
            "receipt path conflicts by identity or ancestry with a contract destination"
        )

    # Full source and existing-destination preflight occurs before the first
    # byte is copied.  A bad later entry therefore cannot leave earlier output.
    existing: dict[Path, bool] = {}
    for entry in entries:
        source_path = source / entry["source"]
        _assert_no_symlink_components(source_path.parent, "source parent")
        _verify_expected(source_path, entry, "source")
        destination_path = destination / entry["destination"]
        existing[destination_path] = _preflight_destination(destination_path, entry)

    try:
        receipt_metadata = receipt.lstat()
    except FileNotFoundError:
        receipt_metadata = None
    if receipt_metadata is not None:
        if stat.S_ISLNK(receipt_metadata.st_mode) or not stat.S_ISREG(receipt_metadata.st_mode):
            raise MaterializationError(f"receipt conflict: {receipt}")
        observed_receipt, _ = _read_regular_bytes(receipt, "receipt")
        if observed_receipt != receipt_payload:
            raise MaterializationError(f"receipt conflict: {receipt}")

    for entry in entries:
        source_path = source / entry["source"]
        destination_path = destination / entry["destination"]
        if not existing[destination_path]:
            _copy_create_only(source_path, destination_path, entry)

    # Verify installed files from their destination descriptors before the
    # receipt is admitted.  The receipt never substitutes for this readback.
    for entry in entries:
        _verify_expected(destination / entry["destination"], entry, "post-copy destination")
    _install_receipt_create_only(receipt, receipt_payload)
    return receipt_document


def materialize(
    *,
    contract_path: os.PathLike[str] | str,
    source_root: os.PathLike[str] | str,
    destination_root: os.PathLike[str] | str,
    receipt_path: os.PathLike[str] | str,
) -> dict[str, Any]:
    """Materialize only the canonical production contract."""

    return _materialize(
        contract_path=contract_path,
        source_root=source_root,
        destination_root=destination_root,
        receipt_path=receipt_path,
        require_canonical_contract=True,
    )


def materialize_test_contract(
    *,
    contract_path: os.PathLike[str] | str,
    source_root: os.PathLike[str] | str,
    destination_root: os.PathLike[str] | str,
    receipt_path: os.PathLike[str] | str,
) -> dict[str, Any]:
    """TEST_ONLY seam for mutation tests with generated small contracts."""

    return _materialize(
        contract_path=contract_path,
        source_root=source_root,
        destination_root=destination_root,
        receipt_path=receipt_path,
        require_canonical_contract=False,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify and create-only materialize exact authority bytes"
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--destination-root", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        receipt = materialize(
            contract_path=arguments.contract,
            source_root=arguments.source_root,
            destination_root=arguments.destination_root,
            receipt_path=arguments.receipt,
        )
    except (MaterializationError, OSError) as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
