#!/usr/bin/env python3
"""Fail-closed extractor for the sealed native build-authority archive.

The extractor uses only the Python standard library.  It verifies an
externally supplied SHA-256 before parsing the tar stream, validates every
member before creating the destination, and writes through directory file
descriptors with create-only operations.  Packaged members are never
executed, imported, or followed as symbolic links.

Absolute symbolic-link target text is preserved because it is part of the
logical rootfs authority.  Such targets are resolved only by the preflight
model, where ``/`` means the packaged ``rootfs``.  They must terminate at a
declared archive member.  On the extracted host filesystem an absolute link
can name the host root, so consumers must continue to use ``lstat`` and the
bundle verifier; extracting this bundle does not authorize member traversal
or execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tarfile
from pathlib import Path
from typing import BinaryIO, Iterable, NamedTuple


ARCHIVE_ROOT = "REI_SEALED_NATIVE_BUILD_AUTHORITY_20260831"
MANIFEST_MEMBER = f"{ARCHIVE_ROOT}/AUTHORITY_MANIFEST.json"
ROOTFS_MEMBER = f"{ARCHIVE_ROOT}/rootfs"
HEX64 = frozenset("0123456789abcdef")


class BundleExtractionError(RuntimeError):
    """A fail-closed archive verification or extraction error."""


class _Member(NamedTuple):
    name: str
    kind: str
    info: tarfile.TarInfo


class _ArchiveFingerprint(NamedTuple):
    device: int
    inode: int
    mode: int
    link_count: int
    owner: int
    group: int
    size: int
    modified_ns: int
    changed_ns: int


def _fail(code: str, detail: str) -> "None":
    raise BundleExtractionError(f"{code}: {detail}")


def _validate_sha256(value: object) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in HEX64 for character in value)
    ):
        _fail("EXPECTED_ARCHIVE_SHA256_INVALID", repr(value))
    return value


def _fingerprint(metadata: os.stat_result) -> _ArchiveFingerprint:
    return _ArchiveFingerprint(
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_uid,
        metadata.st_gid,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _digest_stream(stream: BinaryIO) -> str:
    stream.seek(0)
    digest = hashlib.sha256()
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
    stream.seek(0)
    return digest.hexdigest()


def _hash_open_archive(path: Path) -> tuple[BinaryIO, str, _ArchiveFingerprint]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        _fail("ARCHIVE_OPEN_FAILED", str(exc))
    try:
        initial_metadata = os.fstat(descriptor)
        if not stat.S_ISREG(initial_metadata.st_mode):
            _fail("ARCHIVE_NOT_REGULAR_FILE", os.fspath(path))
        stream = os.fdopen(descriptor, "rb", closefd=True)
    except BaseException:
        os.close(descriptor)
        raise

    try:
        digest = _digest_stream(stream)
        final_metadata = os.fstat(stream.fileno())
    except BaseException:
        stream.close()
        raise
    initial_fingerprint = _fingerprint(initial_metadata)
    if _fingerprint(final_metadata) != initial_fingerprint:
        stream.close()
        _fail("ARCHIVE_CHANGED_DURING_INITIAL_HASH", os.fspath(path))
    return stream, digest, initial_fingerprint


def _canonical_member_name(info: tarfile.TarInfo) -> str:
    raw = info.name
    if not isinstance(raw, str) or not raw or "\x00" in raw or "\\" in raw:
        _fail("ARCHIVE_MEMBER_PATH_INVALID", repr(raw))
    if raw.startswith("/"):
        _fail("ARCHIVE_MEMBER_ABSOLUTE_PATH", raw)
    if raw.endswith("/"):
        if not info.isdir():
            _fail("ARCHIVE_MEMBER_NONCANONICAL_PATH", raw)
        raw = raw[:-1]
    parts = raw.split("/")
    if any(part in ("", ".", "..") for part in parts):
        _fail("ARCHIVE_MEMBER_TRAVERSAL_PATH", raw)
    if parts[0] != ARCHIVE_ROOT:
        _fail("ARCHIVE_EXTRA_TOP_LEVEL_ROOT", parts[0])
    return "/".join(parts)


def _member_kind(info: tarfile.TarInfo, name: str) -> str:
    if info.isdir():
        kind = "directory"
    elif info.type in (tarfile.REGTYPE, tarfile.AREGTYPE):
        kind = "file"
    elif info.issym():
        kind = "symlink"
    else:
        _fail("ARCHIVE_MEMBER_TYPE_FORBIDDEN", f"{name}: {info.type!r}")
    if not isinstance(info.mode, int) or info.mode < 0 or info.mode & ~0o777:
        _fail("ARCHIVE_MEMBER_MODE_INVALID", f"{name}: {info.mode!r}")
    return kind


def _validate_bundle_location(name: str) -> None:
    if name in (ARCHIVE_ROOT, MANIFEST_MEMBER, ROOTFS_MEMBER):
        return
    if name.startswith(ROOTFS_MEMBER + "/"):
        return
    _fail("ARCHIVE_UNDECLARED_BUNDLE_TOP_LEVEL_MEMBER", name)


def _logical_rootfs_path(member_name: str) -> str:
    if member_name == ROOTFS_MEMBER:
        return "/"
    prefix = ROOTFS_MEMBER + "/"
    if not member_name.startswith(prefix):
        _fail("ARCHIVE_SYMLINK_OUTSIDE_ROOTFS", member_name)
    return "/" + member_name[len(prefix) :]


def _resolve_logical_target(link_path: str, target: object) -> str:
    if (
        not isinstance(target, str)
        or not target
        or "\x00" in target
        or "\\" in target
        or target.startswith("//")
    ):
        _fail("ARCHIVE_SYMLINK_TARGET_INVALID", f"{link_path} -> {target!r}")

    if target.startswith("/"):
        stack: list[str] = []
    else:
        stack = [part for part in link_path.rsplit("/", 1)[0].split("/") if part]

    for component in target.split("/"):
        if component in ("", "."):
            continue
        if component == "..":
            if not stack:
                _fail("ARCHIVE_SYMLINK_TARGET_ESCAPES_ROOTFS", f"{link_path} -> {target}")
            stack.pop()
            continue
        stack.append(component)
    return "/" + "/".join(stack) if stack else "/"


def _validate_symlink_graph(members: dict[str, _Member]) -> None:
    logical_members = {
        _logical_rootfs_path(name): member
        for name, member in members.items()
        if name == ROOTFS_MEMBER or name.startswith(ROOTFS_MEMBER + "/")
    }
    for member in members.values():
        if member.kind != "symlink":
            continue
        logical_link = _logical_rootfs_path(member.name)
        current = _resolve_logical_target(logical_link, member.info.linkname)
        visited = {logical_link}
        while True:
            if current in visited:
                _fail("ARCHIVE_SYMLINK_CYCLE", logical_link)
            visited.add(current)
            terminal = logical_members.get(current)
            if terminal is None:
                _fail("ARCHIVE_SYMLINK_TERMINAL_UNDECLARED", f"{logical_link} -> {current}")
            if terminal.kind != "symlink":
                break
            current = _resolve_logical_target(current, terminal.info.linkname)


def _preflight(archive: tarfile.TarFile) -> list[_Member]:
    members: dict[str, _Member] = {}
    try:
        raw_members = archive.getmembers()
    except (OSError, EOFError, tarfile.TarError) as exc:
        _fail("ARCHIVE_MEMBER_SCAN_FAILED", str(exc))
    for info in raw_members:
        name = _canonical_member_name(info)
        if name in members:
            _fail("ARCHIVE_DUPLICATE_MEMBER", name)
        _validate_bundle_location(name)
        members[name] = _Member(name, _member_kind(info, name), info)

    required = {
        ARCHIVE_ROOT: "directory",
        MANIFEST_MEMBER: "file",
        ROOTFS_MEMBER: "directory",
    }
    for name, kind in required.items():
        observed = members.get(name)
        if observed is None:
            _fail("ARCHIVE_REQUIRED_MEMBER_MISSING", name)
        if observed.kind != kind:
            _fail("ARCHIVE_REQUIRED_MEMBER_TYPE_INVALID", f"{name}: {observed.kind}")

    for name, member in members.items():
        if name == ARCHIVE_ROOT:
            continue
        parent_name = name.rsplit("/", 1)[0]
        parent = members.get(parent_name)
        if parent is None:
            _fail("ARCHIVE_MEMBER_PARENT_UNDECLARED", f"{name}: {parent_name}")
        if parent.kind != "directory":
            code = (
                "ARCHIVE_MEMBER_SYMLINK_ANCESTOR"
                if parent.kind == "symlink"
                else "ARCHIVE_MEMBER_PARENT_NOT_DIRECTORY"
            )
            _fail(code, f"{name}: {parent_name}")

    _validate_symlink_graph(members)
    return list(members.values())


def _open_relative_directory(base_descriptor: int, parts: list[str]) -> int:
    descriptor = os.dup(base_descriptor)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        for part in parts:
            next_descriptor = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _open_destination(destination: Path) -> tuple[int, Path]:
    absolute = Path(os.path.abspath(os.fspath(destination)))
    if absolute == Path("/") or not absolute.name:
        _fail("DESTINATION_INVALID", os.fspath(destination))
    parent_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        parent_descriptor = os.open(absolute.parent, parent_flags)
    except OSError as exc:
        _fail("DESTINATION_PARENT_OPEN_FAILED", str(exc))
    try:
        try:
            metadata = os.stat(absolute.name, dir_fd=parent_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            try:
                os.mkdir(absolute.name, 0o700, dir_fd=parent_descriptor)
            except OSError as exc:
                _fail("DESTINATION_CREATE_FAILED", str(exc))
        else:
            if stat.S_ISLNK(metadata.st_mode):
                _fail("DESTINATION_SYMLINK_FORBIDDEN", os.fspath(absolute))
            if not stat.S_ISDIR(metadata.st_mode):
                _fail("DESTINATION_NOT_DIRECTORY", os.fspath(absolute))

        destination_flags = (
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            destination_descriptor = os.open(
                absolute.name, destination_flags, dir_fd=parent_descriptor
            )
        except OSError as exc:
            _fail("DESTINATION_OPEN_FAILED", str(exc))
        try:
            if os.listdir(destination_descriptor):
                _fail("DESTINATION_NOT_EMPTY", os.fspath(absolute))
        except BaseException:
            os.close(destination_descriptor)
            raise
        return destination_descriptor, absolute
    finally:
        os.close(parent_descriptor)


def _relative_parts(member_name: str) -> list[str]:
    return member_name.split("/")


def _create_directory(destination_descriptor: int, member: _Member) -> None:
    parts = _relative_parts(member.name)
    parent = _open_relative_directory(destination_descriptor, parts[:-1])
    try:
        os.mkdir(parts[-1], 0o700, dir_fd=parent)
    finally:
        os.close(parent)


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            _fail("ARCHIVE_MEMBER_WRITE_FAILED", "short write")
        view = view[written:]


def _create_file(
    archive: tarfile.TarFile,
    destination_descriptor: int,
    member: _Member,
) -> None:
    source = archive.extractfile(member.info)
    if source is None:
        _fail("ARCHIVE_REGULAR_MEMBER_READ_FAILED", member.name)
    parts = _relative_parts(member.name)
    parent = _open_relative_directory(destination_descriptor, parts[:-1])
    descriptor = -1
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(parts[-1], flags, 0o600, dir_fd=parent)
        remaining = member.info.size
        while remaining:
            chunk = source.read(min(1024 * 1024, remaining))
            if not chunk:
                _fail("ARCHIVE_REGULAR_MEMBER_TRUNCATED", member.name)
            _write_all(descriptor, chunk)
            remaining -= len(chunk)
        if source.read(1):
            _fail("ARCHIVE_REGULAR_MEMBER_OVERRUN", member.name)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size != member.info.size:
            _fail("EXTRACTED_REGULAR_MEMBER_INVALID", member.name)
        os.fchmod(descriptor, member.info.mode)
    finally:
        source.close()
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent)


def _create_symlink(destination_descriptor: int, member: _Member) -> None:
    parts = _relative_parts(member.name)
    parent = _open_relative_directory(destination_descriptor, parts[:-1])
    try:
        os.symlink(member.info.linkname, parts[-1], dir_fd=parent)
    finally:
        os.close(parent)


def _apply_directory_mode(destination_descriptor: int, member: _Member) -> None:
    descriptor = _open_relative_directory(
        destination_descriptor, _relative_parts(member.name)
    )
    try:
        os.fchmod(descriptor, member.info.mode)
    finally:
        os.close(descriptor)


def _extract_preflighted(
    archive: tarfile.TarFile,
    destination_descriptor: int,
    members: list[_Member],
) -> None:
    directories = sorted(
        (member for member in members if member.kind == "directory"),
        key=lambda member: (member.name.count("/"), member.name),
    )
    files = sorted(
        (member for member in members if member.kind == "file"),
        key=lambda member: member.name,
    )
    symlinks = sorted(
        (member for member in members if member.kind == "symlink"),
        key=lambda member: member.name,
    )
    try:
        for member in directories:
            _create_directory(destination_descriptor, member)
        for member in files:
            _create_file(archive, destination_descriptor, member)
        # Symbolic links are created only after every directory and regular file.
        for member in symlinks:
            _create_symlink(destination_descriptor, member)
        for member in sorted(
            directories,
            key=lambda value: (value.name.count("/"), value.name),
            reverse=True,
        ):
            _apply_directory_mode(destination_descriptor, member)
    except BundleExtractionError:
        raise
    except OSError as exc:
        _fail("ARCHIVE_MEMBER_CREATE_FAILED", str(exc))


def extract_bundle(
    archive_path: Path,
    destination: Path,
    expected_archive_sha256: str,
) -> dict[str, object]:
    """Verify and safely extract one sealed authority bundle.

    ``destination`` is a container directory.  The archive's single
    ``ARCHIVE_ROOT`` directory is created beneath it.  A failed preflight does
    not create or modify the destination.  An I/O failure after extraction
    begins intentionally leaves a partial, non-overwritable directory for
    forensic inspection; a retry must use a new absent or empty destination.
    """

    expected = _validate_sha256(expected_archive_sha256)
    stream, observed, initial_fingerprint = _hash_open_archive(Path(archive_path))
    try:
        if observed != expected:
            _fail("ARCHIVE_SHA256_MISMATCH", f"expected {expected}, observed {observed}")
        try:
            archive = tarfile.open(fileobj=stream, mode="r:xz")
        except (OSError, EOFError, tarfile.TarError) as exc:
            _fail("ARCHIVE_INVALID_TAR_XZ", str(exc))
        with archive:
            members = _preflight(archive)
            destination_descriptor, absolute_destination = _open_destination(
                Path(destination)
            )
            try:
                _extract_preflighted(archive, destination_descriptor, members)
            finally:
                os.close(destination_descriptor)
        before_rehash = _fingerprint(os.fstat(stream.fileno()))
        post_extraction_digest = _digest_stream(stream)
        after_rehash = _fingerprint(os.fstat(stream.fileno()))
        if (
            post_extraction_digest != observed
            or before_rehash != initial_fingerprint
            or after_rehash != initial_fingerprint
        ):
            _fail(
                "ARCHIVE_CHANGED_DURING_EXTRACTION",
                f"initial {observed}, post-extraction {post_extraction_digest}",
            )
    finally:
        stream.close()

    return {
        "schema": "rei-sealed-native-build-authority-extraction-receipt/v1",
        "archive_sha256": observed,
        "archive_root": ARCHIVE_ROOT,
        "destination": os.fspath(absolute_destination),
        "member_count": len(members),
        "packaged_member_execution": "NOT_RUN",
        "runtime_boundary": "NOT_RUN",
        "adapter": "STOP_INVALID",
        "canonical_pilot": "NOT_RUN",
        "first_interval": "NO_PASS_FIRST_CANONICAL_INTERVAL",
        "scientific_pass": "NOT_CLAIMED",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--expected-archive-sha256", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = extract_bundle(
            args.archive,
            args.destination,
            args.expected_archive_sha256,
        )
    except (BundleExtractionError, OSError, EOFError, tarfile.TarError) as exc:
        print(str(exc), file=sys.stderr)
        return 65
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
