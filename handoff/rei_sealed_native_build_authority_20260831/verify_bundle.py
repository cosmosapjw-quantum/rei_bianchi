#!/usr/bin/env python3
"""Verify an extracted sealed native authority bundle without executing it.

This is an intake verifier.  It hashes opaque regular files, checks literal
symbolic-link topology in a logical rootfs, and rejects undeclared members.
It never imports ``rei_bianchi`` and never executes a bundled member.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


HEX64 = frozenset("0123456789abcdef")
CANONICAL_CONTRACT_SHA256 = (
    "2f0356f77445ad34c6eea7ef647320d3afae63e07cfeb10e21ee09c28554c283"
)


class AuthorityVerificationError(RuntimeError):
    """A fail-closed authority-bundle verification error."""


def _fail(code: str, detail: str) -> "None":
    raise AuthorityVerificationError(f"{code}: {detail}")


def _load_json_and_digest(path: Path, *, role: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        _fail(f"{role}_READ_FAILED", str(exc))
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{role}_INVALID_JSON", str(exc))
    if not isinstance(value, dict):
        _fail(f"{role}_INVALID_JSON", "top level must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def _validate_digest(value: Any, *, role: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in HEX64 for char in value)
    ):
        _fail("INVALID_SHA256", role)
    return value


def _logical_path(value: Any, *, role: str) -> str:
    if not isinstance(value, str) or not value.startswith("/"):
        _fail("INVALID_ROOTFS_PATH", role)
    if "\\" in value or "\x00" in value or value == "/" or value.startswith("//"):
        _fail("INVALID_ROOTFS_PATH", role)
    pure = PurePosixPath(value)
    if any(part in ("", ".", "..") for part in pure.parts[1:]):
        _fail("INVALID_ROOTFS_PATH", role)
    if str(pure) != value:
        _fail("NON_CANONICAL_ROOTFS_PATH", role)
    return value


def _bundle_member_path(rootfs: Path, logical: str) -> Path:
    return rootfs.joinpath(*PurePosixPath(logical).parts[1:])


def _parse_mode(value: Any, *, role: str) -> int:
    if (
        not isinstance(value, str)
        or len(value) != 4
        or value[0] != "0"
        or any(char not in "01234567" for char in value[1:])
    ):
        _fail("INVALID_MODE", role)
    return int(value, 8)


def _entry_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        _fail("MANIFEST_ENTRIES_INVALID", "entries must be a list")
    result: dict[str, dict[str, Any]] = {}
    ordered: list[str] = []
    for index, value in enumerate(entries):
        if not isinstance(value, dict):
            _fail("MANIFEST_ENTRY_INVALID", str(index))
        logical = _logical_path(value.get("path"), role=f"entries[{index}].path")
        if logical in result:
            _fail("DUPLICATE_ROOTFS_PATH", logical)
        entry_type = value.get("type")
        if entry_type not in ("file", "symlink"):
            _fail("MANIFEST_ENTRY_TYPE_INVALID", logical)
        expected_keys = (
            {"path", "type", "sha256", "size", "mode", "role"}
            if entry_type == "file"
            else {"path", "type", "target", "role"}
        )
        if set(value) != expected_keys:
            _fail("MANIFEST_ENTRY_KEYS_INVALID", logical)
        if not isinstance(value.get("role"), str) or not value["role"]:
            _fail("MANIFEST_ENTRY_ROLE_INVALID", logical)
        if entry_type == "file":
            _validate_digest(value.get("sha256"), role=logical)
            if (
                not isinstance(value.get("size"), int)
                or isinstance(value["size"], bool)
                or value["size"] < 0
            ):
                _fail("MANIFEST_ENTRY_SIZE_INVALID", logical)
            _parse_mode(value.get("mode"), role=logical)
        else:
            target = value.get("target")
            if not isinstance(target, str) or not target or "\x00" in target:
                _fail("MANIFEST_SYMLINK_TARGET_INVALID", logical)
            _resolve_target(logical, target)
        result[logical] = value
        ordered.append(logical)
    if ordered != sorted(ordered):
        _fail("MANIFEST_ENTRIES_NOT_SORTED", "entries must use bytewise path order")
    return result


def _resolve_target(link_path: str, target: str) -> str:
    candidate = target if target.startswith("/") else posixpath.join(
        posixpath.dirname(link_path), target
    )
    normalized = posixpath.normpath(candidate)
    if not normalized.startswith("/") or normalized == "/":
        _fail("SYMLINK_TARGET_ESCAPES_ROOTFS", f"{link_path} -> {target}")
    return _logical_path(normalized, role=f"resolved target of {link_path}")


def _resolve_manifest_path(
    start: str, entries: dict[str, dict[str, Any]]
) -> str:
    current = start
    visited: set[str] = set()
    for _ in range(len(entries) + 1):
        if current in visited:
            _fail("SYMLINK_CYCLE", start)
        visited.add(current)
        entry = entries.get(current)
        if entry is None:
            _fail("SYMLINK_TERMINAL_UNDECLARED", f"{start} -> {current}")
        if entry["type"] == "file":
            return current
        current = _resolve_target(current, entry["target"])
    _fail("SYMLINK_CYCLE", start)


def _check_no_symlink_parents(rootfs: Path, member: Path, logical: str) -> None:
    relative = member.relative_to(rootfs)
    current = rootfs
    for part in relative.parts[:-1]:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            _fail("MEMBER_PARENT_MISSING", f"{logical}: {exc}")
        if stat.S_ISLNK(mode):
            _fail("SYMLINK_PARENT_FORBIDDEN", logical)
        if not stat.S_ISDIR(mode):
            _fail("MEMBER_PARENT_NOT_DIRECTORY", logical)


def _hash_regular_no_follow(path: Path, logical: str) -> tuple[str, os.stat_result]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        _fail("REGULAR_FILE_OPEN_FAILED", f"{logical}: {exc}")
    digest = hashlib.sha256()
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            _fail("MEMBER_NOT_REGULAR_FILE", logical)
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    finally:
        os.close(descriptor)
    return digest.hexdigest(), metadata


def _actual_members(rootfs: Path) -> set[str]:
    found: set[str] = set()
    for directory, dirnames, filenames in os.walk(rootfs, topdown=True, followlinks=False):
        directory_path = Path(directory)
        retained_dirs: list[str] = []
        for name in dirnames:
            path = directory_path / name
            mode = path.lstat().st_mode
            logical = "/" + path.relative_to(rootfs).as_posix()
            if stat.S_ISLNK(mode):
                found.add(logical)
            elif stat.S_ISDIR(mode):
                retained_dirs.append(name)
            else:
                _fail("SPECIAL_MEMBER_FORBIDDEN", logical)
        dirnames[:] = retained_dirs
        for name in filenames:
            path = directory_path / name
            mode = path.lstat().st_mode
            logical = "/" + path.relative_to(rootfs).as_posix()
            if stat.S_ISREG(mode) or stat.S_ISLNK(mode):
                found.add(logical)
            else:
                _fail("SPECIAL_MEMBER_FORBIDDEN", logical)
    return found


def _check_bundle_top_level(bundle_root: Path) -> None:
    expected = {"AUTHORITY_MANIFEST.json", "rootfs"}
    try:
        observed = {item.name for item in bundle_root.iterdir()}
    except OSError as exc:
        _fail("BUNDLE_ROOT_READ_FAILED", str(exc))
    if observed != expected:
        extra = sorted(observed - expected)
        missing = sorted(expected - observed)
        if extra:
            _fail("UNDECLARED_BUNDLE_TOP_LEVEL_MEMBER", ",".join(extra))
        _fail("BUNDLE_TOP_LEVEL_MEMBER_MISSING", ",".join(missing))
    manifest_mode = (bundle_root / "AUTHORITY_MANIFEST.json").lstat().st_mode
    if not stat.S_ISREG(manifest_mode):
        _fail("MANIFEST_NOT_REGULAR_FILE", "AUTHORITY_MANIFEST.json")


def _require_top_level_status(manifest: dict[str, Any], contract: dict[str, Any]) -> None:
    expected = contract.get("required_status")
    if not isinstance(expected, dict):
        _fail("CONTRACT_REQUIRED_STATUS_INVALID", "required_status")
    for key, value in expected.items():
        if manifest.get(key) != value:
            _fail("MANIFEST_STATUS_MISMATCH", key)
    allowed = set(expected) | {"schema", "entries", "source_packages", "notes"}
    extra = set(manifest) - allowed
    if extra:
        _fail("MANIFEST_TOP_LEVEL_KEYS_INVALID", ",".join(sorted(extra)))
    if manifest.get("schema") != contract.get("bundle", {}).get("manifest_schema"):
        _fail("MANIFEST_SCHEMA_MISMATCH", str(manifest.get("schema")))
    source_packages = manifest.get("source_packages")
    if not isinstance(source_packages, list) or not all(
        isinstance(item, dict) for item in source_packages
    ):
        _fail("MANIFEST_SOURCE_PACKAGES_INVALID", "source_packages")
    notes = manifest.get("notes")
    if not isinstance(notes, list) or not all(isinstance(item, str) for item in notes):
        _fail("MANIFEST_NOTES_INVALID", "notes")


def _require_contract_members(
    entries: dict[str, dict[str, Any]], contract: dict[str, Any]
) -> None:
    for required in contract.get("required_files", []):
        logical = _logical_path(required.get("path"), role="required file")
        entry = entries.get(logical)
        if entry is None or entry.get("type") != "file":
            _fail("REQUIRED_FILE_MISSING", logical)
        for key in ("sha256", "size", "mode", "role"):
            if entry.get(key) != required.get(key):
                _fail("REQUIRED_FILE_IDENTITY_MISMATCH", f"{logical}:{key}")
    for required in contract.get("required_symlinks", []):
        logical = _logical_path(required.get("path"), role="required symlink")
        entry = entries.get(logical)
        if entry is None or entry.get("type") != "symlink":
            _fail("REQUIRED_SYMLINK_MISSING", logical)
        if entry.get("target") != required.get("target"):
            _fail("REQUIRED_SYMLINK_TARGET_MISMATCH", logical)
        _resolve_manifest_path(logical, entries)


def _verify_bundle_against_contract(
    bundle_root: Path,
    contract_path: Path,
    expected_manifest_sha256: str,
    *,
    production_contract: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Verify against one contract and return its receipt plus verified entries."""

    expected_manifest_sha256 = _validate_digest(
        expected_manifest_sha256, role="expected manifest digest"
    )
    bundle_root = bundle_root.absolute()
    try:
        root_mode = bundle_root.lstat().st_mode
    except OSError as exc:
        _fail("BUNDLE_ROOT_MISSING", str(exc))
    if stat.S_ISLNK(root_mode) or not stat.S_ISDIR(root_mode):
        _fail("BUNDLE_ROOT_INVALID", str(bundle_root))
    try:
        if bundle_root.resolve(strict=True) != bundle_root:
            _fail("BUNDLE_ROOT_SYMLINK_COMPONENT", str(bundle_root))
    except OSError as exc:
        _fail("BUNDLE_ROOT_RESOLUTION_FAILED", str(exc))
    _check_bundle_top_level(bundle_root)
    contract, contract_sha256 = _load_json_and_digest(contract_path, role="CONTRACT")
    if production_contract and contract_sha256 != CANONICAL_CONTRACT_SHA256:
        _fail(
            "CANONICAL_CONTRACT_SHA256_MISMATCH",
            f"expected {CANONICAL_CONTRACT_SHA256}, observed {contract_sha256}",
        )
    if contract.get("schema") != "rei-sealed-native-build-authority-supplement-contract/v1":
        _fail("CONTRACT_SCHEMA_MISMATCH", str(contract.get("schema")))
    manifest_name = contract.get("bundle", {}).get("manifest_path")
    rootfs_name = contract.get("bundle", {}).get("rootfs_directory")
    if manifest_name != "AUTHORITY_MANIFEST.json" or rootfs_name != "rootfs":
        _fail("CONTRACT_LAYOUT_INVALID", "fixed layout required")
    manifest_path = bundle_root / manifest_name
    manifest, observed_manifest_sha256 = _load_json_and_digest(
        manifest_path, role="MANIFEST"
    )
    if observed_manifest_sha256 != expected_manifest_sha256:
        _fail(
            "MANIFEST_SHA256_MISMATCH",
            f"expected {expected_manifest_sha256}, observed {observed_manifest_sha256}",
        )
    _require_top_level_status(manifest, contract)
    entries = _entry_map(manifest)
    _require_contract_members(entries, contract)
    rootfs = bundle_root / rootfs_name
    try:
        rootfs_mode = rootfs.lstat().st_mode
    except OSError as exc:
        _fail("ROOTFS_MISSING", str(exc))
    if stat.S_ISLNK(rootfs_mode) or not stat.S_ISDIR(rootfs_mode):
        _fail("ROOTFS_INVALID", str(rootfs))
    actual = _actual_members(rootfs)
    declared = set(entries)
    if actual != declared:
        undeclared = sorted(actual - declared)
        missing = sorted(declared - actual)
        if undeclared:
            _fail("UNDECLARED_BUNDLE_MEMBER", ",".join(undeclared))
        _fail("DECLARED_BUNDLE_MEMBER_MISSING", ",".join(missing))
    for logical, entry in entries.items():
        member = _bundle_member_path(rootfs, logical)
        _check_no_symlink_parents(rootfs, member, logical)
        metadata = member.lstat()
        if entry["type"] == "symlink":
            if not stat.S_ISLNK(metadata.st_mode):
                _fail("MEMBER_TYPE_MISMATCH", logical)
            target = os.readlink(member)
            if target != entry["target"]:
                _fail("SYMLINK_TARGET_MISMATCH", logical)
            _resolve_manifest_path(logical, entries)
            continue
        digest, followed_metadata = _hash_regular_no_follow(member, logical)
        if digest != entry["sha256"]:
            _fail("FILE_SHA256_MISMATCH", logical)
        if followed_metadata.st_size != entry["size"]:
            _fail("FILE_SIZE_MISMATCH", logical)
        if stat.S_IMODE(followed_metadata.st_mode) != _parse_mode(
            entry["mode"], role=logical
        ):
            _fail("FILE_MODE_MISMATCH", logical)
    receipt = {
        "schema": "rei-sealed-native-build-authority-verification-receipt/v1",
        "classification": (
            "BYTE_IDENTITY_NON_SCIENTIFIC_AUTHORITY_SUPPLEMENT"
            if production_contract
            else "TEST_ONLY_CONTRACT_VERIFICATION_NOT_AUTHORITY"
        ),
        "contract_sha256": contract_sha256,
        "manifest_sha256": observed_manifest_sha256,
        "declared_member_count": len(entries),
        "regular_file_count": sum(entry["type"] == "file" for entry in entries.values()),
        "symlink_count": sum(entry["type"] == "symlink" for entry in entries.values()),
        "runtime_boundary": "NOT_RUN",
        "path_stability": "POINT_IN_TIME_NO_CONCURRENT_WRITER_CLAIM",
        "concurrent_writer_exclusion": "REQUIRED_NOT_KERNEL_ENFORCED",
        "build": "NOT_RUN",
        "native_tests": "NOT_RUN",
        "adapter": "STOP_INVALID",
        "canonical_pilot": "NOT_RUN",
        "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
        "scientific_pass": "NOT_CLAIMED",
        "scientific_publication": "NOT_RUN",
    }
    return receipt, list(entries.values())


def verify_bundle(
    bundle_root: Path,
    expected_manifest_sha256: str,
) -> dict[str, Any]:
    """Verify with the script-bound production contract and return a receipt."""

    receipt, _entries = _verify_bundle_against_contract(
        bundle_root,
        Path(__file__).with_name("CONTRACT.json"),
        expected_manifest_sha256,
        production_contract=True,
    )
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", required=True, type=Path)
    parser.add_argument("--expected-manifest-sha256", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = verify_bundle(args.bundle_root, args.expected_manifest_sha256)
    except AuthorityVerificationError as exc:
        print(str(exc), file=sys.stderr)
        return 65
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
