#!/usr/bin/env python3
"""Read-only forensic audit for the REI Rust stdlib aggregate lock.

This is deliberately a diagnostic, not a replacement for the locked Section 0
gate.  It never invokes rustc, imports repository Python, executes an archive
member, or changes the locked build driver.  It emits enough evidence to decide
whether a fresh Section 0 replay is justified or an external aggregate witness
is still required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "rei-rust-stdlib-closure-forensic-audit/v1"
CHUNK_SIZE = 1024 * 1024


class AuditError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _fail(code: str, detail: str) -> None:
    raise AuditError(code, detail)


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
        if _fingerprint(opened)[:3] != _fingerprint(before)[:3]:
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
    if _fingerprint(opened) != _fingerprint(after_open) or _fingerprint(before) != _fingerprint(after):
        _fail("FILE_MUTATED_DURING_HASH", f"{role}: {path}")
    return digest.hexdigest(), before.st_size


def _safe_stdlib_name(name: str) -> None:
    raw = os.fsencode(name)
    if not raw or b"/" in raw or b"\x00" in raw:
        _fail("STDLIB_FILENAME_INVALID", repr(name))
    allowed = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if any(byte not in allowed for byte in raw):
        _fail("STDLIB_FILENAME_UNSAFE_FOR_LEGACY_TRANSCRIPT", repr(name))


def _stdlib_rows(stdlib_dir: Path) -> list[dict[str, Any]]:
    _require_real_directory(stdlib_dir, role="stdlib directory")
    rows: list[dict[str, Any]] = []
    with os.scandir(stdlib_dir) as entries:
        for entry in entries:
            entry_path = stdlib_dir / entry.name
            entry_stat = os.lstat(entry_path)
            if stat.S_ISDIR(entry_stat.st_mode):
                continue
            if stat.S_ISLNK(entry_stat.st_mode):
                _fail("STDLIB_SYMLINK_FORBIDDEN", entry.name)
            if not stat.S_ISREG(entry_stat.st_mode):
                _fail("STDLIB_SPECIAL_FILE_FORBIDDEN", entry.name)
            _safe_stdlib_name(entry.name)
            digest, size = _hash_regular_no_follow(entry_path, role="stdlib member")
            rows.append({"name": entry.name, "sha256": digest, "size_bytes": size})
    rows.sort(key=lambda row: os.fsencode(row["name"]))
    if not rows:
        _fail("STDLIB_EMPTY", str(stdlib_dir))
    if len({row["name"] for row in rows}) != len(rows):
        _fail("STDLIB_DUPLICATE_NAME", str(stdlib_dir))
    return rows


def _archive_rows(
    archive: Path,
    *,
    expected_archive_sha256: str,
    archive_prefix: str,
) -> list[dict[str, Any]]:
    if len(expected_archive_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in expected_archive_sha256
    ):
        _fail("ARCHIVE_DIGEST_INVALID", expected_archive_sha256)
    observed_archive_sha256, _ = _hash_regular_no_follow(archive, role="Rust archive")
    if observed_archive_sha256 != expected_archive_sha256:
        _fail(
            "ARCHIVE_SHA256_MISMATCH",
            f"expected {expected_archive_sha256}, observed {observed_archive_sha256}",
        )
    try:
        before = os.lstat(archive)
        fd = os.open(archive, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        _fail("ARCHIVE_OPEN_FAILED", str(exc))
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    try:
        opened = os.fstat(fd)
        if _fingerprint(before)[:3] != _fingerprint(opened)[:3]:
            _fail("ARCHIVE_REPLACED_BEFORE_READ", str(archive))
        with os.fdopen(os.dup(fd), "rb", closefd=True) as stream:
            with tarfile.open(fileobj=stream, mode="r:xz") as bundle:
                for member in bundle:
                    if not member.isfile() or not member.name.startswith(archive_prefix):
                        continue
                    name = member.name[len(archive_prefix) :]
                    if "/" in name:
                        continue
                    _safe_stdlib_name(name)
                    if name in seen:
                        _fail("ARCHIVE_STDLIB_DUPLICATE_NAME", name)
                    content = bundle.extractfile(member)
                    if content is None:
                        _fail("ARCHIVE_STDLIB_MEMBER_UNREADABLE", name)
                    digest = hashlib.sha256()
                    size = 0
                    with content:
                        while True:
                            chunk = content.read(CHUNK_SIZE)
                            if not chunk:
                                break
                            digest.update(chunk)
                            size += len(chunk)
                    if size != member.size:
                        _fail("ARCHIVE_STDLIB_MEMBER_SIZE_DRIFT", name)
                    rows.append({"name": name, "sha256": digest.hexdigest(), "size_bytes": size})
                    seen.add(name)
        after_open = os.fstat(fd)
    except (tarfile.TarError, OSError) as exc:
        _fail("ARCHIVE_READ_FAILED", str(exc))
    finally:
        os.close(fd)
    after = os.lstat(archive)
    if _fingerprint(opened) != _fingerprint(after_open) or _fingerprint(before) != _fingerprint(after):
        _fail("ARCHIVE_MUTATED_DURING_READ", str(archive))
    rows.sort(key=lambda row: os.fsencode(row["name"]))
    if not rows:
        _fail("ARCHIVE_STDLIB_EMPTY", archive_prefix)
    return rows


def _legacy_transcript(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        f"{row['sha256']}  ./{row['name']}\n".encode("ascii") for row in rows
    )


def _candidate_digests(rows: list[dict[str, Any]]) -> dict[str, str]:
    legacy = _legacy_transcript(rows)
    variants = {
        "legacy_gnu_sha256sum_transcript": legacy,
        "gnu_transcript_without_dot_prefix": b"".join(
            f"{row['sha256']}  {row['name']}\n".encode("ascii") for row in rows
        ),
        "gnu_transcript_single_separator": b"".join(
            f"{row['sha256']} ./{row['name']}\n".encode("ascii") for row in rows
        ),
        "gnu_transcript_nul_terminated": b"".join(
            f"{row['sha256']}  ./{row['name']}\0".encode("ascii") for row in rows
        ),
        "member_hex_digests_newline": b"".join(
            f"{row['sha256']}\n".encode("ascii") for row in rows
        ),
        "member_binary_digests": b"".join(bytes.fromhex(row["sha256"]) for row in rows),
        "name_nul_then_binary_digest": b"".join(
            row["name"].encode("ascii") + b"\0" + bytes.fromhex(row["sha256"])
            for row in rows
        ),
    }
    return {name: hashlib.sha256(data).hexdigest() for name, data in variants.items()}


def _utility(path: str) -> dict[str, str]:
    resolved = shutil.which(path, path="/usr/bin:/bin")
    if resolved is None:
        _fail("LEGACY_UTILITY_MISSING", path)
    real = Path(os.path.realpath(resolved))
    digest, _ = _hash_regular_no_follow(real, role=f"legacy utility {path}")
    return {"command": path, "resolved_path": str(real), "sha256": digest}


def _run_checked(args: list[str], *, cwd: Path, env: dict[str, str], input_bytes: bytes | None = None) -> bytes:
    process = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        _fail(
            "LEGACY_UTILITY_FAILED",
            f"{' '.join(args)} exit={process.returncode} stderr={process.stderr.decode('utf-8', 'replace').strip()}",
        )
    return process.stdout


def _shell_replay(stdlib_dir: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    utilities = {name: _utility(name) for name in ("find", "sort", "xargs", "sha256sum")}
    env = dict(os.environ)
    env["PATH"] = "/usr/bin:/bin"
    find_output = _run_checked(
        [utilities["find"]["resolved_path"], ".", "-maxdepth", "1", "-type", "f", "-print0"],
        cwd=stdlib_dir,
        env=env,
    )
    sort_output = _run_checked(
        [utilities["sort"]["resolved_path"], "-z"],
        cwd=stdlib_dir,
        env=env,
        input_bytes=find_output,
    )
    inner = _run_checked(
        [utilities["xargs"]["resolved_path"], "-0", utilities["sha256sum"]["resolved_path"]],
        cwd=stdlib_dir,
        env=env,
        input_bytes=sort_output,
    )
    outer = _run_checked(
        [utilities["sha256sum"]["resolved_path"]],
        cwd=stdlib_dir,
        env=env,
        input_bytes=inner,
    )
    fields = outer.decode("ascii", "strict").strip().split()
    if len(fields) != 2 or fields[1] != "-" or len(fields[0]) != 64:
        _fail("LEGACY_OUTER_OUTPUT_INVALID", repr(outer))
    expected_inner = _legacy_transcript(rows)
    return {
        "digest": fields[0],
        "inner_transcript_sha256": hashlib.sha256(inner).hexdigest(),
        "inner_transcript_matches_python": inner == expected_inner,
        "find_output_sha256": hashlib.sha256(find_output).hexdigest(),
        "sorted_name_stream_sha256": hashlib.sha256(sort_output).hexdigest(),
        "utilities": utilities,
        "locale": {name: os.environ.get(name) for name in ("LC_ALL", "LC_COLLATE", "LANG")},
    }


def _compare_rows(
    archive_rows: list[dict[str, Any]], stdlib_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    archive_by_name = {row["name"]: row for row in archive_rows}
    stdlib_by_name = {row["name"]: row for row in stdlib_rows}
    archive_only = sorted(set(archive_by_name) - set(stdlib_by_name))
    stdlib_only = sorted(set(stdlib_by_name) - set(archive_by_name))
    mismatches = []
    for name in sorted(set(archive_by_name) & set(stdlib_by_name)):
        if archive_by_name[name] != stdlib_by_name[name]:
            mismatches.append(
                {
                    "name": name,
                    "archive": archive_by_name[name],
                    "stdlib": stdlib_by_name[name],
                }
            )
    return {
        "archive_member_count": len(archive_rows),
        "stdlib_member_count": len(stdlib_rows),
        "archive_only": archive_only,
        "stdlib_only": stdlib_only,
        "member_mismatches": mismatches,
        "status": "PASS" if not archive_only and not stdlib_only and not mismatches else "FAIL",
    }


def run_audit(
    *,
    stdlib_dir: Path,
    rust_archive: Path,
    archive_prefix: str,
    expected_archive_sha256: str,
    expected_closure_sha256: str,
    reported_observed_sha256: str | None,
    shell_replay: bool,
) -> dict[str, Any]:
    if len(expected_closure_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in expected_closure_sha256
    ):
        _fail("CLOSURE_DIGEST_INVALID", expected_closure_sha256)
    archive_rows = _archive_rows(
        rust_archive,
        expected_archive_sha256=expected_archive_sha256,
        archive_prefix=archive_prefix,
    )
    stdlib_rows = _stdlib_rows(stdlib_dir)
    member_comparison = _compare_rows(archive_rows, stdlib_rows)
    candidates = _candidate_digests(stdlib_rows)
    python_legacy = candidates["legacy_gnu_sha256sum_transcript"]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "classification": "FAIL_CLOSED_SECTION_0_DIAGNOSTIC_ONLY",
        "archive": {
            "path": str(rust_archive),
            "sha256": expected_archive_sha256,
            "stdlib_prefix": archive_prefix,
        },
        "stdlib": {"path": str(stdlib_dir), "members": stdlib_rows},
        "member_comparison": member_comparison,
        "locked_closure_sha256": expected_closure_sha256,
        "python_legacy_replay_sha256": python_legacy,
        "non_normative_candidate_digests": candidates,
        "candidate_names_matching_locked_digest": sorted(
            name for name, digest in candidates.items() if digest == expected_closure_sha256
        ),
        "runtime_boundary": "NOT_RUN",
        "repository_or_native_execution": "NOT_RUN",
        "canonical_pilot": "NOT_RUN",
        "scientific_pass": "NOT_CLAIMED",
    }
    if reported_observed_sha256 is not None:
        result["reported_observed_sha256"] = reported_observed_sha256
        result["reported_digest_matches_python_legacy"] = reported_observed_sha256 == python_legacy
    if shell_replay:
        shell = _shell_replay(stdlib_dir, stdlib_rows)
        result["shell_legacy_replay"] = shell
        result["shell_digest_matches_python_legacy"] = shell["digest"] == python_legacy
        if reported_observed_sha256 is not None:
            result["reported_digest_matches_shell_legacy"] = reported_observed_sha256 == shell["digest"]
    if member_comparison["status"] != "PASS":
        result["status"] = "STOP_INVALID"
        result["first_failing_gate"] = "RUST_STDLIB_ARCHIVE_MEMBER_MISMATCH"
    elif shell_replay and not result["shell_digest_matches_python_legacy"]:
        result["status"] = "STOP_INVALID"
        result["first_failing_gate"] = "RUST_STDLIB_LEGACY_SHELL_PYTHON_DIVERGENCE"
    elif python_legacy != expected_closure_sha256:
        result["status"] = "STOP_INVALID"
        result["first_failing_gate"] = "RUST_STDLIB_CLOSURE_SHA256_MISMATCH_CONFIRMED"
    elif shell_replay and result["shell_legacy_replay"]["digest"] != expected_closure_sha256:
        result["status"] = "STOP_INVALID"
        result["first_failing_gate"] = "RUST_STDLIB_CLOSURE_SHA256_MISMATCH_CONFIRMED"
    else:
        result["status"] = "PASS_DIAGNOSTIC_ONLY"
        result["next_required_gate"] = "FRESH_FULL_SECTION_0_REPLAY_REQUIRED"
    return result


def _write_create_only(path: Path, payload: dict[str, Any]) -> None:
    parent = path.parent
    _require_real_directory(parent, role="receipt parent")
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
    except FileExistsError:
        _fail("RECEIPT_ALREADY_EXISTS", str(path))
    except OSError as exc:
        _fail("RECEIPT_OPEN_FAILED", str(exc))
    try:
        written = 0
        while written < len(raw):
            written += os.write(fd, raw[written:])
        os.fsync(fd)
    finally:
        os.close(fd)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdlib-dir", type=Path, required=True)
    parser.add_argument("--rust-archive", type=Path, required=True)
    parser.add_argument("--archive-prefix", required=True)
    parser.add_argument("--expected-archive-sha256", required=True)
    parser.add_argument("--expected-closure-sha256", required=True)
    parser.add_argument("--reported-observed-sha256")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--skip-shell-replay", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result: dict[str, Any]
    exit_code = 0
    try:
        result = run_audit(
            stdlib_dir=args.stdlib_dir,
            rust_archive=args.rust_archive,
            archive_prefix=args.archive_prefix,
            expected_archive_sha256=args.expected_archive_sha256,
            expected_closure_sha256=args.expected_closure_sha256,
            reported_observed_sha256=args.reported_observed_sha256,
            shell_replay=not args.skip_shell_replay,
        )
        if result["status"] == "STOP_INVALID":
            exit_code = 65
    except AuditError as exc:
        result = {
            "schema": SCHEMA,
            "classification": "FAIL_CLOSED_SECTION_0_DIAGNOSTIC_ONLY",
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
    except AuditError as exc:
        result = {
            "schema": SCHEMA,
            "classification": "FAIL_CLOSED_SECTION_0_DIAGNOSTIC_ONLY",
            "status": "STOP_INVALID",
            "first_failing_gate": exc.code,
            "detail": exc.detail,
        }
        exit_code = 65
    print(json.dumps(result, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
