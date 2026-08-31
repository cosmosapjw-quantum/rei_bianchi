#!/usr/bin/env python3
"""Create-only repair for archive-owned stdlib components missing from a sysroot.

The script is intentionally narrow.  It reads an exact Rust distribution
archive without extracting or executing archive members and may add only the
two contract-declared regular files, create-only, to an already verified
stdlib directory.  It never invokes rustc, cargo, repository code, or a
native build.  A successful materialization remains diagnostic-only until a
fresh full Section 0 replay passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import sys
import tarfile
from pathlib import Path
from typing import Any


CHUNK_SIZE = 1024 * 1024
SCHEMA = "rei-rust-stdlib-closure-repair-receipt/v1"


class RepairError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _fail(code: str, detail: str) -> None:
    raise RepairError(code, detail)


def _fingerprint(st: os.stat_result) -> tuple[int, int, int, int, int]:
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def _require_real_directory(path: Path, *, role: str) -> None:
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        _fail("DIRECTORY_MISSING", f"{role}: {path}")
    if stat.S_ISLNK(st.st_mode):
        _fail("SYMLINKED_DIRECTORY", f"{role}: {path}")
    if not stat.S_ISDIR(st.st_mode):
        _fail("DIRECTORY_NOT_REAL", f"{role}: {path}")


def _hash_regular_no_follow(path: Path, *, role: str) -> tuple[str, int]:
    try:
        before = os.lstat(path)
    except FileNotFoundError:
        _fail("FILE_MISSING", f"{role}: {path}")
    if stat.S_ISLNK(before.st_mode):
        _fail("SYMLINKED_FILE", f"{role}: {path}")
    if not stat.S_ISREG(before.st_mode):
        _fail("FILE_NOT_REGULAR", f"{role}: {path}")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        _fail("FILE_OPEN_FAILED", f"{role}: {path}: {exc}")
    try:
        opened = os.fstat(fd)
        if _fingerprint(before)[:3] != _fingerprint(opened)[:3]:
            _fail("FILE_REPLACED_BEFORE_HASH", f"{role}: {path}")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
        after_open = os.fstat(fd)
    finally:
        os.close(fd)
    after = os.lstat(path)
    if _fingerprint(before) != _fingerprint(after) or _fingerprint(opened) != _fingerprint(after_open):
        _fail("FILE_MUTATED_DURING_HASH", f"{role}: {path}")
    return digest.hexdigest(), before.st_size


def _read_json_regular(path: Path, *, role: str) -> tuple[dict[str, Any], str]:
    digest, _ = _hash_regular_no_follow(path, role=role)
    try:
        before = os.lstat(path)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        _fail("CONTRACT_OPEN_FAILED", f"{role}: {path}: {exc}")
    try:
        opened = os.fstat(fd)
        if _fingerprint(before)[:3] != _fingerprint(opened)[:3]:
            _fail("CONTRACT_REPLACED_BEFORE_READ", str(path))
        raw_parts: list[bytes] = []
        while True:
            chunk = os.read(fd, CHUNK_SIZE)
            if not chunk:
                break
            raw_parts.append(chunk)
        after_open = os.fstat(fd)
    finally:
        os.close(fd)
    after = os.lstat(path)
    if _fingerprint(before) != _fingerprint(after) or _fingerprint(opened) != _fingerprint(after_open):
        _fail("CONTRACT_MUTATED_DURING_READ", str(path))
    raw = b"".join(raw_parts)
    if hashlib.sha256(raw).hexdigest() != digest:
        _fail("CONTRACT_MUTATED_DURING_READ", str(path))
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("CONTRACT_PARSE_FAILED", str(exc))
    if not isinstance(value, dict):
        _fail("CONTRACT_NOT_OBJECT", str(path))
    return value, digest


def _require_digest(value: Any, *, role: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        _fail("DIGEST_INVALID", role)
    return value


def _require_name(value: Any, *, role: str) -> str:
    if not isinstance(value, str) or not value or "/" in value or "\x00" in value:
        _fail("TARGET_NAME_INVALID", role)
    try:
        raw = value.encode("ascii", "strict")
    except UnicodeEncodeError:
        _fail("TARGET_NAME_UNSAFE", role)
    allowed = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if any(byte not in allowed for byte in raw):
        _fail("TARGET_NAME_UNSAFE", role)
    return value


def _load_contract(path: Path) -> tuple[dict[str, Any], str]:
    contract, digest = _read_json_regular(path, role="repair contract")
    expected_keys = {"schema", "rust_archive", "supplements", "expected_closure_sha256"}
    if set(contract) != expected_keys:
        _fail("CONTRACT_KEYS_INVALID", ",".join(sorted(set(contract) ^ expected_keys)))
    if contract["schema"] != "rei-rust-stdlib-closure-repair-contract/v1":
        _fail("CONTRACT_SCHEMA_INVALID", str(contract["schema"]))
    archive = contract["rust_archive"]
    if not isinstance(archive, dict) or set(archive) != {"sha256", "base_prefix"}:
        _fail("CONTRACT_ARCHIVE_INVALID", "rust_archive")
    _require_digest(archive["sha256"], role="archive SHA-256")
    if not isinstance(archive["base_prefix"], str) or not archive["base_prefix"].endswith("/"):
        _fail("CONTRACT_BASE_PREFIX_INVALID", "rust_archive.base_prefix")
    supplements = contract["supplements"]
    if not isinstance(supplements, list) or not supplements:
        _fail("CONTRACT_SUPPLEMENTS_INVALID", "supplements")
    seen_paths: set[str] = set()
    seen_targets: set[str] = set()
    for index, item in enumerate(supplements):
        if not isinstance(item, dict) or set(item) != {"archive_path", "target_name", "sha256", "size_bytes"}:
            _fail("CONTRACT_SUPPLEMENT_INVALID", str(index))
        if not isinstance(item["archive_path"], str) or not item["archive_path"]:
            _fail("CONTRACT_ARCHIVE_PATH_INVALID", str(index))
        name = _require_name(item["target_name"], role=f"supplement {index}")
        _require_digest(item["sha256"], role=f"supplement {index}")
        if not isinstance(item["size_bytes"], int) or item["size_bytes"] < 0:
            _fail("CONTRACT_SUPPLEMENT_SIZE_INVALID", str(index))
        if item["archive_path"] in seen_paths or name in seen_targets:
            _fail("CONTRACT_SUPPLEMENT_DUPLICATE", str(index))
        seen_paths.add(item["archive_path"])
        seen_targets.add(name)
    _require_digest(contract["expected_closure_sha256"], role="expected closure SHA-256")
    return contract, digest


def _archive_rows(
    archive: Path, *, archive_sha256: str, base_prefix: str, supplements: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    observed, _ = _hash_regular_no_follow(archive, role="Rust archive")
    if observed != archive_sha256:
        _fail("ARCHIVE_SHA256_MISMATCH", f"expected {archive_sha256}, observed {observed}")
    try:
        before = os.lstat(archive)
        fd = os.open(archive, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        _fail("ARCHIVE_OPEN_FAILED", str(exc))
    base_rows: list[dict[str, Any]] = []
    supplement_by_path = {item["archive_path"]: item for item in supplements}
    found: dict[str, dict[str, Any]] = {}
    try:
        opened = os.fstat(fd)
        if _fingerprint(before)[:3] != _fingerprint(opened)[:3]:
            _fail("ARCHIVE_REPLACED_BEFORE_READ", str(archive))
        with os.fdopen(os.dup(fd), "rb", closefd=True) as stream:
            with tarfile.open(fileobj=stream, mode="r:xz") as bundle:
                for member in bundle:
                    is_base = member.isfile() and member.name.startswith(base_prefix)
                    is_supplement = member.name in supplement_by_path
                    if not is_base and not is_supplement:
                        continue
                    if not member.isfile():
                        _fail("ARCHIVE_MEMBER_NOT_REGULAR", member.name)
                    if is_base:
                        target_name = member.name[len(base_prefix) :]
                        if "/" in target_name:
                            continue
                        _require_name(target_name, role="base archive member")
                    else:
                        target_name = supplement_by_path[member.name]["target_name"]
                    content = bundle.extractfile(member)
                    if content is None:
                        _fail("ARCHIVE_MEMBER_UNREADABLE", member.name)
                    digest = hashlib.sha256()
                    size = 0
                    with content:
                        while True:
                            chunk = content.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            digest.update(chunk)
                            size += len(chunk)
                    row = {"name": target_name, "sha256": digest.hexdigest(), "size_bytes": size, "archive_path": member.name}
                    if is_base:
                        base_rows.append(row)
                    else:
                        expected = supplement_by_path[member.name]
                        if row["sha256"] != expected["sha256"] or row["size_bytes"] != expected["size_bytes"]:
                            _fail("ARCHIVE_SUPPLEMENT_IDENTITY_MISMATCH", member.name)
                        found[target_name] = row
        after_open = os.fstat(fd)
    except (tarfile.TarError, OSError) as exc:
        _fail("ARCHIVE_READ_FAILED", str(exc))
    finally:
        os.close(fd)
    after = os.lstat(archive)
    if _fingerprint(before) != _fingerprint(after) or _fingerprint(opened) != _fingerprint(after_open):
        _fail("ARCHIVE_MUTATED_DURING_READ", str(archive))
    base_rows.sort(key=lambda row: row["name"].encode("ascii"))
    if not base_rows:
        _fail("ARCHIVE_BASE_EMPTY", base_prefix)
    if len({row["name"] for row in base_rows}) != len(base_rows):
        _fail("ARCHIVE_BASE_DUPLICATE", base_prefix)
    if set(found) != {item["target_name"] for item in supplements}:
        _fail("ARCHIVE_SUPPLEMENT_MISSING", ",".join(sorted({item["target_name"] for item in supplements} - set(found))))
    return base_rows, found


def _directory_rows(stdlib_dir: Path) -> dict[str, dict[str, Any]]:
    _require_real_directory(stdlib_dir, role="stdlib directory")
    rows: dict[str, dict[str, Any]] = {}
    with os.scandir(stdlib_dir) as entries:
        for entry in entries:
            path = stdlib_dir / entry.name
            st = os.lstat(path)
            if stat.S_ISDIR(st.st_mode):
                continue
            if stat.S_ISLNK(st.st_mode):
                _fail("STDLIB_SYMLINK_FORBIDDEN", entry.name)
            if not stat.S_ISREG(st.st_mode):
                _fail("STDLIB_SPECIAL_FILE_FORBIDDEN", entry.name)
            _require_name(entry.name, role="stdlib directory member")
            digest, size = _hash_regular_no_follow(path, role="stdlib member")
            rows[entry.name] = {"name": entry.name, "sha256": digest, "size_bytes": size}
    return rows


def _legacy_closure(rows: list[dict[str, Any]]) -> str:
    transcript = b"".join(
        f"{row['sha256']}  ./{row['name']}\n".encode("ascii")
        for row in sorted(rows, key=lambda row: row["name"].encode("ascii"))
    )
    return hashlib.sha256(transcript).hexdigest()


def _preflight(
    *, base_rows: list[dict[str, Any]], supplement_rows: dict[str, dict[str, Any]], directory_rows: dict[str, dict[str, Any]]
) -> tuple[list[str], list[str]]:
    base_by_name = {row["name"]: row for row in base_rows}
    allowed_names = set(base_by_name) | set(supplement_rows)
    unexpected = sorted(set(directory_rows) - allowed_names)
    if unexpected:
        _fail("UNDECLARED_STDLIB_MEMBER", ",".join(unexpected))
    for name, expected in base_by_name.items():
        actual = directory_rows.get(name)
        if actual is None:
            _fail("BASE_MEMBER_MISSING", name)
        if {key: actual[key] for key in ("name", "sha256", "size_bytes")} != {
            key: expected[key] for key in ("name", "sha256", "size_bytes")
        }:
            _fail("BASE_MEMBER_MISMATCH", name)
    missing = []
    present = []
    for name, expected in supplement_rows.items():
        actual = directory_rows.get(name)
        if actual is None:
            missing.append(name)
        elif {key: actual[key] for key in ("name", "sha256", "size_bytes")} == {
            key: expected[key] for key in ("name", "sha256", "size_bytes")
        }:
            present.append(name)
        else:
            _fail("SUPPLEMENT_TARGET_CONFLICT", name)
    return sorted(missing), sorted(present)


def _copy_one_from_archive(
    *, archive: Path, archive_sha256: str, archive_path: str, expected: dict[str, Any], destination: Path
) -> None:
    _require_real_directory(destination, role="stdlib destination")
    target_name = expected["target_name"]
    try:
        target_stat = os.lstat(destination / target_name)
    except FileNotFoundError:
        target_stat = None
    if target_stat is not None:
        _fail("SUPPLEMENT_TARGET_CONFLICT", target_name)
    directory_fd = os.open(destination, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary_name = f".rei-stdlib-repair-{target_name}-{secrets.token_hex(12)}"
    temporary_fd: int | None = None
    archive_fd: int | None = None
    linked = False
    try:
        temporary_fd = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=directory_fd,
        )
        try:
            archive_before = os.lstat(archive)
            archive_fd = os.open(archive, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError as exc:
            _fail("ARCHIVE_OPEN_FAILED", f"{archive}: {exc}")
        archive_opened = os.fstat(archive_fd)
        if _fingerprint(archive_before)[:3] != _fingerprint(archive_opened)[:3]:
            _fail("ARCHIVE_REPLACED_BEFORE_COPY", str(archive))
        archive_digest = hashlib.sha256()
        while True:
            chunk = os.read(archive_fd, CHUNK_SIZE)
            if not chunk:
                break
            archive_digest.update(chunk)
        archive_after_hash = os.fstat(archive_fd)
        archive_path_after_hash = os.lstat(archive)
        if (
            _fingerprint(archive_before) != _fingerprint(archive_path_after_hash)
            or _fingerprint(archive_opened) != _fingerprint(archive_after_hash)
        ):
            _fail("ARCHIVE_MUTATED_BEFORE_COPY", str(archive))
        if archive_digest.hexdigest() != archive_sha256:
            _fail(
                "ARCHIVE_SHA256_MISMATCH",
                f"expected {archive_sha256}, observed {archive_digest.hexdigest()}",
            )
        os.lseek(archive_fd, 0, os.SEEK_SET)
        try:
            with os.fdopen(os.dup(archive_fd), "rb", closefd=True) as stream:
                with tarfile.open(fileobj=stream, mode="r:xz") as bundle:
                    try:
                        member = bundle.getmember(archive_path)
                    except KeyError:
                        _fail("ARCHIVE_SUPPLEMENT_MISSING", archive_path)
                    if not member.isfile():
                        _fail("ARCHIVE_MEMBER_NOT_REGULAR", archive_path)
                    source = bundle.extractfile(member)
                    if source is None:
                        _fail("ARCHIVE_MEMBER_UNREADABLE", archive_path)
                    digest = hashlib.sha256()
                    size = 0
                    with source:
                        while True:
                            chunk = source.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            digest.update(chunk)
                            size += len(chunk)
                            view = memoryview(chunk)
                            while view:
                                count = os.write(temporary_fd, view)
                                view = view[count:]
        except (tarfile.TarError, OSError) as exc:
            _fail("ARCHIVE_COPY_READ_FAILED", str(exc))
        archive_after_copy = os.fstat(archive_fd)
        archive_path_after_copy = os.lstat(archive)
        if (
            _fingerprint(archive_before) != _fingerprint(archive_path_after_copy)
            or _fingerprint(archive_opened) != _fingerprint(archive_after_copy)
        ):
            _fail("ARCHIVE_MUTATED_DURING_COPY", str(archive))
        if digest.hexdigest() != expected["sha256"] or size != expected["size_bytes"]:
            _fail("ARCHIVE_SUPPLEMENT_IDENTITY_MISMATCH", archive_path)
        os.fsync(temporary_fd)
        os.close(temporary_fd)
        temporary_fd = None
        try:
            os.link(temporary_name, target_name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd, follow_symlinks=False)
        except FileExistsError:
            _fail("SUPPLEMENT_TARGET_RACE", target_name)
        linked = True
        os.chmod(target_name, 0o444, dir_fd=directory_fd, follow_symlinks=False)
        os.fsync(directory_fd)
        os.unlink(temporary_name, dir_fd=directory_fd)
        os.fsync(directory_fd)
    finally:
        if temporary_fd is not None:
            os.close(temporary_fd)
        if archive_fd is not None:
            os.close(archive_fd)
        if not linked:
            # A failed create-only attempt leaves its uniquely named partial file for forensics.
            pass
        os.close(directory_fd)
    digest, size = _hash_regular_no_follow(destination / target_name, role="materialized supplement")
    if digest != expected["sha256"] or size != expected["size_bytes"]:
        _fail("POST_WRITE_SUPPLEMENT_MISMATCH", target_name)


def repair(*, stdlib_dir: Path, rust_archive: Path, contract_path: Path, apply: bool) -> dict[str, Any]:
    contract, contract_sha256 = _load_contract(contract_path)
    archive_data = contract["rust_archive"]
    supplements = contract["supplements"]
    base_rows, supplement_rows = _archive_rows(
        rust_archive,
        archive_sha256=archive_data["sha256"],
        base_prefix=archive_data["base_prefix"],
        supplements=supplements,
    )
    before = _directory_rows(stdlib_dir)
    missing, present = _preflight(
        base_rows=base_rows, supplement_rows=supplement_rows, directory_rows=before
    )
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "CREATE_ONLY_EXACT_ARCHIVE_COMPONENT_REPAIR_DIAGNOSTIC_ONLY",
        "contract_sha256": contract_sha256,
        "archive_sha256": archive_data["sha256"],
        "expected_closure_sha256": contract["expected_closure_sha256"],
        "base_member_count": len(base_rows),
        "supplement_member_count": len(supplement_rows),
        "missing_target_names": missing,
        "present_exact_target_names": present,
        "runtime_boundary": "NOT_RUN",
        "repository_or_native_execution": "NOT_RUN",
        "canonical_pilot": "NOT_RUN",
        "scientific_pass": "NOT_CLAIMED",
    }
    if missing and not apply:
        result["status"] = "REPAIR_READY_DRY_RUN"
        return result
    if missing:
        by_name = {item["target_name"]: item for item in supplements}
        for name in missing:
            _copy_one_from_archive(
                archive=rust_archive,
                archive_sha256=archive_data["sha256"],
                archive_path=by_name[name]["archive_path"],
                expected=by_name[name],
                destination=stdlib_dir,
            )
        status = "APPLIED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY"
    else:
        status = "ALREADY_MATERIALIZED_EXACT_SUPPLEMENTS_DIAGNOSTIC_ONLY"
    after = _directory_rows(stdlib_dir)
    missing_after, _ = _preflight(
        base_rows=base_rows, supplement_rows=supplement_rows, directory_rows=after
    )
    if missing_after:
        _fail("POST_REPAIR_SUPPLEMENT_MISSING", ",".join(missing_after))
    full_rows = [after[name] for name in sorted(after)]
    closure = _legacy_closure(full_rows)
    if closure != contract["expected_closure_sha256"]:
        _fail(
            "POST_REPAIR_CLOSURE_MISMATCH",
            f"expected {contract['expected_closure_sha256']}, observed {closure}",
        )
    result["status"] = status
    result["post_repair_closure_sha256"] = closure
    result["post_repair_member_count"] = len(full_rows)
    return result


def _write_create_only(path: Path, payload: dict[str, Any]) -> None:
    _require_real_directory(path.parent, role="receipt parent")
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
    except FileExistsError:
        _fail("RECEIPT_ALREADY_EXISTS", str(path))
    except OSError as exc:
        _fail("RECEIPT_OPEN_FAILED", str(exc))
    try:
        offset = 0
        while offset < len(raw):
            offset += os.write(fd, raw[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdlib-dir", type=Path, required=True)
    parser.add_argument("--rust-archive", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = repair(
            stdlib_dir=args.stdlib_dir,
            rust_archive=args.rust_archive,
            contract_path=args.contract,
            apply=args.apply,
        )
        exit_code = 0
    except RepairError as exc:
        result = {
            "schema": SCHEMA,
            "classification": "CREATE_ONLY_EXACT_ARCHIVE_COMPONENT_REPAIR_DIAGNOSTIC_ONLY",
            "status": "STOP_INVALID",
            "first_failing_gate": exc.code,
            "detail": exc.detail,
            "runtime_boundary": "NOT_RUN",
            "repository_or_native_execution": "NOT_RUN",
            "canonical_pilot": "NOT_RUN",
            "scientific_pass": "NOT_CLAIMED",
        }
        exit_code = 65
    try:
        _write_create_only(args.receipt, result)
    except RepairError as exc:
        result = {
            "schema": SCHEMA,
            "classification": "CREATE_ONLY_EXACT_ARCHIVE_COMPONENT_REPAIR_DIAGNOSTIC_ONLY",
            "status": "STOP_INVALID",
            "first_failing_gate": exc.code,
            "detail": exc.detail,
        }
        exit_code = 65
    print(json.dumps(result, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
