#!/usr/bin/env python3
"""Fetch pinned continuation objects, materialize raw bytes, and validate once.

This locator authenticates transport and provenance only.  It never checks out
a commit, creates a worktree, changes a ref, runs scientific code, or promotes
the recorded first-interval result.
"""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import asdict, dataclass
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any, Iterable


SHA1_RE = re.compile(r"[0-9a-f]{40}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
PAYLOAD_ROOT = "research/continuation_20260830"

PRODUCTION_DELIVERY_PATHS = (
    f"{PAYLOAD_ROOT}/README.md",
    f"{PAYLOAD_ROOT}/CONTRACT.json",
    f"{PAYLOAD_ROOT}/CODEX_HANDOFF.md",
    f"{PAYLOAD_ROOT}/paired_budget.py",
    f"{PAYLOAD_ROOT}/verify_payload.py",
    f"{PAYLOAD_ROOT}/check_mutations.py",
    f"{PAYLOAD_ROOT}/tests/test_paired_budget.py",
    f"{PAYLOAD_ROOT}/tests/test_payload.py",
    f"{PAYLOAD_ROOT}/evidence/TESTS.log",
    f"{PAYLOAD_ROOT}/evidence/mutations/MUTATIONS.json",
    f"{PAYLOAD_ROOT}/evidence/mutations/drop_remainders.log",
    f"{PAYLOAD_ROOT}/evidence/mutations/reverse_difference.log",
    f"{PAYLOAD_ROOT}/evidence/mutations/relax_strict_limit.log",
)


@dataclass(frozen=True)
class ObjectPins:
    """All authority needed to validate one immutable publication graph."""

    repository: str
    source_branch: str
    pull_request_number: int
    source_commit: str
    source_tree: str
    helper_commit: str
    helper_tree: str
    helper_parent: str
    helper_path: str
    helper_blob: str
    payload_commit: str
    payload_tree: str
    payload_parent: str
    payload_path: str
    payload_subtree: str
    manifest_path: str
    manifest_blob: str
    manifest_sha256: str
    manifest_entries: int
    terminal_commit: str
    terminal_tree: str
    terminal_parent: str
    publication_path: str
    publication_blob: str
    publication_sha256: str
    validator_path: str
    validator_blob: str
    validator_sha256: str
    rec_lock_path: str
    rec_lock_blob: str
    blocked_archive_path: str
    blocked_archive_blob: str
    blocked_archive_sha256: str
    delivery_paths: tuple[str, ...]
    remote_branch: str
    source_parent: str | None = None
    terminal_subtree: str | None = None
    blocked_archive_size: int | None = None


PRODUCTION_PINS = ObjectPins(
    repository="cosmosapjw-quantum/rei_bianchi",
    source_branch="agent/implementation/rei-first-canonical-interval-20260829-r1",
    pull_request_number=18,
    source_commit="053b97c56e089e28a83f37d79a4128ed3cdae9f4",
    source_tree="46a96c789a691d671644685893a552cd9486788d",
    helper_commit="82c67218248cb896019b2bffc590da1260a214fc",
    helper_tree="dc801c78f01be32f6e6d74cc2d3f2abcfe2279d2",
    helper_parent="053b97c56e089e28a83f37d79a4128ed3cdae9f4",
    helper_path=f"{PAYLOAD_ROOT}/paired_budget.py",
    helper_blob="8d0920626f6f90b4e6997c3daf01c4cca7ff0eee",
    payload_commit="70330fa5e833411bfa9337691e5773431ccd5ac3",
    payload_tree="7e73bad7b2e6bd573136f6857b90a50a91944f14",
    payload_parent="82c67218248cb896019b2bffc590da1260a214fc",
    payload_path=PAYLOAD_ROOT,
    payload_subtree="c7307d1cbf46bbdf6ec60c273172848eb8e88566",
    manifest_path=f"{PAYLOAD_ROOT}/MANIFEST.sha256",
    manifest_blob="de1123618af296abb049d8d47ffebb21c720ebac",
    manifest_sha256="c06748e5347445b243f52558cf73046b199ad1434d30d817be99a122ef8db51c",
    manifest_entries=13,
    terminal_commit="1893f12d14b212eb4b6bd637332824f692e6f4b3",
    terminal_tree="773fcdc4d1ab115fa0542d26ba67af5c086f450b",
    terminal_parent="70330fa5e833411bfa9337691e5773431ccd5ac3",
    publication_path=f"{PAYLOAD_ROOT}/REMOTE_PUBLICATION.json",
    publication_blob="a52bf267eba2614646b9c6d1db223e4dd1cd1a48",
    publication_sha256="575aa68525bc22d8f556a0a857ad3c12714dc4baa44dab04c138e4dffa79e845",
    validator_path=f"{PAYLOAD_ROOT}/verify_payload.py",
    validator_blob="12b677b2ea5c2b602dc27b5211eef1507e247fd8",
    validator_sha256="e51ba74d2fb4355ac1cb3407cfa6a2e1ae2057696106610fdfa7f0ba20a5e0d3",
    rec_lock_path="external/rec_bianchi.lock.json",
    rec_lock_blob="d68cde8382f0c8c81e2747823bf11b6befb63f8b",
    blocked_archive_path=(
        "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_"
        "R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_"
        "ADAPTIVE_HISTORY/local_results/first_interval_r2_blocked_minimum_step.tar.gz"
    ),
    blocked_archive_blob="1804d8b16be81f4ccf11b8cc991faee60f8cb9ca",
    blocked_archive_sha256="a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b",
    delivery_paths=PRODUCTION_DELIVERY_PATHS,
    remote_branch="agent/continuation/research-followthrough-20260830-r1",
    source_parent="a35c8b3fceaf9c832b401bc01480f5e3b0b4af30",
    terminal_subtree="ad69943a5372cd0673203ef60dfd44260fc9edfe",
    blocked_archive_size=11_637_524,
)


EXPECTED_VALIDATOR_RESULT = {
    "status": "PASS_PAYLOAD_ONLY",
    "files": 13,
    "source_objects": "CHECKED",
    "claim": "NO_PASS_FIRST_CANONICAL_INTERVAL",
    "next": "REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER",
}

BASE_RESULT = {
    "transport_status": "PASS_IMMUTABLE_PAYLOAD_ONLY",
    "scientific_validation": "NOT_RUN",
    "canonical_adapter": "NOT_RUN",
    "pilot_46080x3": "NOT_RUN",
    "first_interval": "NO_PASS",
    "pr14_disposition": "RECORDED_BLOCKED_MINIMUM_STEP",
}


class LocatorError(RuntimeError):
    """Fail-closed locator error with a stable classification."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.undeleted_stage_pathname: str | None = None
        self.stage_path_status: str | None = None
        self.retained_stage_identity: dict[str, int | str] | None = None


@dataclass(frozen=True)
class RepositorySnapshot:
    head_symbolic: bytes
    head_commit: bytes
    refs: bytes
    worktrees: bytes
    index_sha256: str | None
    shallow_sha256: str | None
    status: bytes
    pseudorefs: tuple[tuple[str, str | None], ...]


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_type: str
    sha: str
    path: str


@dataclass(frozen=True)
class VerifiedGraph:
    payload_raw: tuple[tuple[str, str, bytes], ...]
    manifest_raw: bytes
    publication_raw: bytes


@dataclass(frozen=True)
class StageIdentity:
    device: int
    inode: int
    file_type: int
    mode: int


@dataclass(frozen=True)
class ReceiptAuthority:
    descriptor: int
    sha256: str
    size: int


@dataclass(frozen=True)
class ClosureDigest:
    sha256: str
    files: int
    directories: int


@dataclass(frozen=True)
class DestinationAuthority:
    descriptor: int
    path: Path
    identity: StageIdentity
    closure: ClosureDigest


class LocatorResult(dict[str, str]):
    """Mapping-compatible result with an out-of-band receipt digest."""

    receipt_sha256: str

    def __init__(self, result: dict[str, str], receipt_sha256: str) -> None:
        super().__init__(result)
        self.receipt_sha256 = receipt_sha256


CLOSURE_ALGORITHM = "sha256-nul-records-v1"
DESTINATION_BINDING_SCHEMA = "rei-materialized-directory-binding/v1"
RECEIPT_SCHEMA = "rei-local-immutable-payload-locator-receipt/v2"
RECEIPT_ATOMICITY = (
    "DESTINATION_AND_RECEIPT_EACH_ATOMIC_NOREPLACE; "
    "NO_CROSS_PATH_ATOMICITY; RECEIPT_BINDS_DESTINATION_IDENTITY_AND_CLOSURE; "
    "FRESH_CONSUMER_VERIFICATION_REQUIRED"
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


GIT_ROUTING_ENVIRONMENT = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_DIR",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_GRAFT_FILE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_QUARANTINE_PATH",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_SUPER_PREFIX",
        "GIT_WORK_TREE",
    }
)


def _git_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for name in tuple(environment):
        if name in GIT_ROUTING_ENVIRONMENT or name.startswith("GIT_CONFIG"):
            environment.pop(name, None)
    environment.update(
        {
            "LC_ALL": "C",
            "LANG": "C",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_NO_LAZY_FETCH": "1",
        }
    )
    return environment


def _run_git(
    repo: Path,
    *arguments: str,
    timeout: int = 60,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    try:
        process = subprocess.run(
            ["git", "--no-replace-objects", *arguments],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_git_environment(),
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LocatorError("GIT_FAILURE", f"Git invocation failed: {error}") from error
    if check and process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise LocatorError(
            "GIT_FAILURE", f"git {' '.join(arguments)} failed: {detail}"
        )
    return process


def _git_path(repo: Path, name: str) -> Path:
    raw = _run_git(repo, "rev-parse", "--git-path", name).stdout
    path = Path(raw.decode("utf-8", errors="strict").rstrip("\n"))
    return path if path.is_absolute() else (repo / path).resolve()


def _optional_git_output(repo: Path, *arguments: str) -> bytes:
    process = _run_git(repo, *arguments, check=False)
    return process.stdout if process.returncode == 0 else b""


def _file_digest(path: Path) -> str | None:
    try:
        return _sha256(path.read_bytes())
    except FileNotFoundError:
        return None


def snapshot_repository(repo: Path) -> RepositorySnapshot:
    """Capture ref/index/worktree/checkout state; object storage is excluded."""

    repo = Path(repo).resolve(strict=True)
    index_path = _git_path(repo, "index")
    pseudorefs = []
    for name in (
        "FETCH_HEAD",
        "ORIG_HEAD",
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_HEAD",
        "AUTO_MERGE",
    ):
        pseudorefs.append((name, _file_digest(_git_path(repo, name))))
    return RepositorySnapshot(
        head_symbolic=_optional_git_output(repo, "symbolic-ref", "-q", "HEAD"),
        head_commit=_optional_git_output(repo, "rev-parse", "--verify", "HEAD"),
        refs=_run_git(
            repo,
            "for-each-ref",
            "--format=%(refname)%00%(objecttype)%00%(objectname)%00%(symref)%00",
        ).stdout,
        worktrees=_run_git(repo, "worktree", "list", "--porcelain", "-z").stdout,
        index_sha256=_file_digest(index_path),
        shallow_sha256=_file_digest(_git_path(repo, "shallow")),
        status=_run_git(
            repo,
            "status",
            "--porcelain=v2",
            "-z",
            "--branch",
            "--untracked-files=all",
        ).stdout,
        pseudorefs=tuple(pseudorefs),
    )


def _validate_sha(value: str, length: int, field: str) -> None:
    pattern = SHA1_RE if length == 40 else SHA256_RE
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise LocatorError("INVALID_PIN", f"{field} must be lowercase {length}-hex")


def _validate_path(value: str, field: str) -> None:
    if not isinstance(value, str):
        raise LocatorError("INVALID_PIN", f"{field} is not text")
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in value
        or str(path) != value
    ):
        raise LocatorError("INVALID_PIN", f"{field} is not a safe Git path")


def _validate_pins(pins: ObjectPins) -> None:
    sha1_fields = (
        "source_commit",
        "source_tree",
        "helper_commit",
        "helper_tree",
        "helper_parent",
        "helper_blob",
        "payload_commit",
        "payload_tree",
        "payload_parent",
        "payload_subtree",
        "manifest_blob",
        "terminal_commit",
        "terminal_tree",
        "terminal_parent",
        "publication_blob",
        "validator_blob",
        "rec_lock_blob",
        "blocked_archive_blob",
    )
    for field in sha1_fields:
        _validate_sha(getattr(pins, field), 40, field)
    if pins.source_parent is not None:
        _validate_sha(pins.source_parent, 40, "source_parent")
    if pins.terminal_subtree is not None:
        _validate_sha(pins.terminal_subtree, 40, "terminal_subtree")
    for field in (
        "manifest_sha256",
        "publication_sha256",
        "validator_sha256",
        "blocked_archive_sha256",
    ):
        _validate_sha(getattr(pins, field), 64, field)
    paths = (
        ("helper_path", pins.helper_path),
        ("payload_path", pins.payload_path),
        ("manifest_path", pins.manifest_path),
        ("publication_path", pins.publication_path),
        ("validator_path", pins.validator_path),
        ("rec_lock_path", pins.rec_lock_path),
        ("blocked_archive_path", pins.blocked_archive_path),
    )
    for field, value in paths:
        _validate_path(value, field)
    for number, value in enumerate(pins.delivery_paths):
        _validate_path(value, f"delivery_paths[{number}]")
    if len(set(pins.delivery_paths)) != len(pins.delivery_paths):
        raise LocatorError("INVALID_PIN", "delivery paths are not unique")
    if pins.manifest_entries != len(pins.delivery_paths) or pins.manifest_entries <= 0:
        raise LocatorError("INVALID_PIN", "manifest entry count is inconsistent")
    prefix = pins.payload_path + "/"
    if any(not path.startswith(prefix) for path in pins.delivery_paths):
        raise LocatorError("INVALID_PIN", "delivery path is outside payload root")
    if pins.helper_path not in pins.delivery_paths:
        raise LocatorError("INVALID_PIN", "helper is outside delivery closure")
    if pins.validator_path not in pins.delivery_paths:
        raise LocatorError("INVALID_PIN", "validator is outside delivery closure")
    if pins.manifest_path in pins.delivery_paths:
        raise LocatorError("INVALID_PIN", "manifest must be externally pinned")
    if pins.publication_path in pins.delivery_paths:
        raise LocatorError("INVALID_PIN", "publication must be terminal metadata")
    if not pins.repository or not pins.remote_branch or not pins.source_branch:
        raise LocatorError("INVALID_PIN", "repository and branch labels are required")
    if pins.pull_request_number <= 0:
        raise LocatorError("INVALID_PIN", "pull request number must be positive")
    if pins.blocked_archive_size is not None and pins.blocked_archive_size < 0:
        raise LocatorError("INVALID_PIN", "blocked archive size is invalid")


def _repository_root(repo: Path) -> Path:
    try:
        resolved = Path(repo).resolve(strict=True)
    except OSError as error:
        raise LocatorError("REPOSITORY_POLICY", f"repository unavailable: {error}") from error
    if not resolved.is_dir():
        raise LocatorError("REPOSITORY_POLICY", "repository path is not a directory")
    process = _run_git(resolved, "rev-parse", "--show-toplevel", check=False)
    if process.returncode:
        raise LocatorError("REPOSITORY_POLICY", "a non-bare Git worktree is required")
    root = Path(process.stdout.decode("utf-8", errors="strict").rstrip("\n")).resolve()
    object_format = _run_git(root, "rev-parse", "--show-object-format").stdout.strip()
    if object_format != b"sha1":
        raise LocatorError("REPOSITORY_POLICY", "pinned publication requires SHA-1 Git objects")
    shallow = _run_git(root, "rev-parse", "--is-shallow-repository").stdout.strip()
    if shallow != b"false":
        raise LocatorError(
            "REPOSITORY_POLICY", "shallow repositories are unsupported; use a full history"
        )
    return root


def _absolute_git_dir(repo: Path, argument: str) -> Path:
    raw = _run_git(repo, "rev-parse", argument).stdout.decode("utf-8", errors="strict")
    path = Path(raw.rstrip("\n"))
    return path.resolve() if path.is_absolute() else (repo / path).resolve()


def _worktree_roots(repo: Path) -> tuple[Path, ...]:
    raw = _run_git(repo, "worktree", "list", "--porcelain", "-z").stdout
    roots = []
    for field in raw.split(b"\0"):
        if field.startswith(b"worktree "):
            roots.append(
                Path(field[len(b"worktree ") :].decode("utf-8", errors="strict")).resolve()
            )
    return tuple(roots)


def _is_within(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def _new_output_path(path: Path, label: str) -> Path:
    code = "DESTINATION_EXISTS" if label == "destination" else "RECEIPT_EXISTS"
    lexical = Path(path)
    if not lexical.is_absolute():
        lexical = Path.cwd() / lexical
    try:
        os.lstat(lexical)
    except FileNotFoundError:
        pass
    except OSError as error:
        raise LocatorError("OUTPUT_POLICY", f"cannot inspect {label}: {error}") from error
    else:
        raise LocatorError(code, f"{label} already exists: {lexical}")
    if not lexical.name:
        raise LocatorError("OUTPUT_POLICY", f"{label} has no final path component")
    try:
        parent = lexical.parent.resolve(strict=True)
    except OSError as error:
        raise LocatorError("OUTPUT_POLICY", f"{label} parent is unavailable: {error}") from error
    if not parent.is_dir():
        raise LocatorError("OUTPUT_POLICY", f"{label} parent is not a directory")
    resolved = parent / lexical.name
    try:
        os.lstat(resolved)
    except FileNotFoundError:
        return resolved
    except OSError as error:
        raise LocatorError("OUTPUT_POLICY", f"cannot inspect {label}: {error}") from error
    raise LocatorError(code, f"{label} already exists: {resolved}")


def _validate_output_locations(
    repo: Path, destination: Path, receipt: Path | None
) -> tuple[Path, Path]:
    destination = _new_output_path(destination, "destination")
    receipt = _new_output_path(
        receipt
        if receipt is not None
        else destination.with_name(destination.name + ".locator-receipt.json"),
        "receipt",
    )
    if destination == receipt or _is_within(receipt, destination):
        raise LocatorError("OUTPUT_POLICY", "receipt must be outside destination")
    protected = set(_worktree_roots(repo))
    protected.add(_absolute_git_dir(repo, "--git-dir"))
    protected.add(_absolute_git_dir(repo, "--git-common-dir"))
    for output in (destination, receipt):
        if any(_is_within(output, root) for root in protected):
            raise LocatorError("OUTPUT_POLICY", "outputs must be outside all Git worktrees")
    return destination, receipt


def _object_type(repo: Path, sha: str) -> str | None:
    process = _run_git(repo, "cat-file", "-t", sha, check=False)
    if process.returncode:
        return None
    try:
        return process.stdout.decode("ascii").rstrip("\n")
    except UnicodeDecodeError as error:
        raise LocatorError("OBJECT_MISMATCH", "non-ASCII Git object type") from error


def _require_object(repo: Path, sha: str, expected_type: str) -> None:
    actual = _object_type(repo, sha)
    if actual is None:
        raise LocatorError("OBJECT_UNAVAILABLE", f"required object unavailable: {sha}")
    if actual != expected_type:
        raise LocatorError(
            "OBJECT_MISMATCH",
            f"object {sha} is {actual}, expected {expected_type}",
        )


def _raw_object(repo: Path, object_type: str, sha: str) -> bytes:
    _require_object(repo, sha, object_type)
    process = _run_git(repo, "cat-file", object_type, sha, check=False)
    if process.returncode:
        raise LocatorError("OBJECT_UNAVAILABLE", f"cannot read object: {sha}")
    return process.stdout


def _commit_headers(raw: bytes) -> tuple[str, tuple[str, ...]]:
    header = raw.split(b"\n\n", 1)[0]
    tree: str | None = None
    parents: list[str] = []
    for line in header.splitlines():
        if line.startswith(b"tree "):
            tree = line[5:].decode("ascii", errors="strict")
        elif line.startswith(b"parent "):
            parents.append(line[7:].decode("ascii", errors="strict"))
    if tree is None or SHA1_RE.fullmatch(tree) is None:
        raise LocatorError("OBJECT_MISMATCH", "commit has no valid tree header")
    if any(SHA1_RE.fullmatch(parent) is None for parent in parents):
        raise LocatorError("OBJECT_MISMATCH", "commit has an invalid parent header")
    return tree, tuple(parents)


def _verify_commit(
    repo: Path,
    commit: str,
    expected_tree: str,
    expected_parents: tuple[str, ...],
) -> None:
    raw = _raw_object(repo, "commit", commit)
    tree, parents = _commit_headers(raw)
    if tree != expected_tree or parents != expected_parents:
        raise LocatorError(
            "OBJECT_MISMATCH",
            f"commit graph mismatch at {commit}",
        )
    _require_object(repo, expected_tree, "tree")


def _tree_entry(repo: Path, commit: str, path: str) -> TreeEntry:
    process = _run_git(
        repo,
        "ls-tree",
        "-z",
        "--full-tree",
        commit,
        "--",
        f":(literal){path}",
        check=False,
    )
    if process.returncode:
        raise LocatorError("OBJECT_UNAVAILABLE", f"cannot inspect path: {path}")
    rows = [row for row in process.stdout.split(b"\0") if row]
    if len(rows) != 1:
        raise LocatorError("OBJECT_MISMATCH", f"path is missing or ambiguous: {path}")
    try:
        metadata, raw_path = rows[0].split(b"\t", 1)
        mode, object_type, sha = metadata.decode("ascii").split(" ", 2)
        decoded_path = raw_path.decode("utf-8", errors="strict")
    except (ValueError, UnicodeDecodeError) as error:
        raise LocatorError("OBJECT_MISMATCH", f"malformed tree entry: {path}") from error
    if decoded_path != path or SHA1_RE.fullmatch(sha) is None:
        raise LocatorError("OBJECT_MISMATCH", f"unexpected tree entry: {path}")
    return TreeEntry(mode, object_type, sha, decoded_path)


def _require_entry(
    repo: Path,
    commit: str,
    path: str,
    mode: str,
    object_type: str,
    sha: str,
) -> None:
    entry = _tree_entry(repo, commit, path)
    if (entry.mode, entry.object_type, entry.sha) != (mode, object_type, sha):
        raise LocatorError("OBJECT_MISMATCH", f"tree binding mismatch: {path}")
    _require_object(repo, sha, object_type)


def _parse_manifest(raw: bytes, pins: ObjectPins) -> tuple[tuple[str, str], ...]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise LocatorError("OBJECT_MISMATCH", "manifest is not ASCII") from error
    entries: list[tuple[str, str]] = []
    names: set[str] = set()
    for line in text.splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise LocatorError("OBJECT_MISMATCH", "unsafe manifest syntax")
        digest, name = parts
        try:
            _validate_sha(digest, 64, "manifest digest")
            _validate_path(name, "manifest path")
        except LocatorError as error:
            raise LocatorError("OBJECT_MISMATCH", str(error)) from error
        if name in names:
            raise LocatorError("OBJECT_MISMATCH", "duplicate manifest path")
        names.add(name)
        entries.append((name, digest))
    expected = tuple(pins.delivery_paths)
    if len(entries) != pins.manifest_entries or tuple(name for name, _ in entries) != expected:
        raise LocatorError("OBJECT_MISMATCH", "manifest delivery closure mismatch")
    return tuple(entries)


def _json_no_duplicates(raw: bytes, label: str) -> dict[str, Any]:
    def pairs_hook(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LocatorError("PUBLICATION_MISMATCH", f"duplicate JSON key in {label}")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=pairs_hook)
    except LocatorError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LocatorError("PUBLICATION_MISMATCH", f"invalid JSON in {label}") from error
    if not isinstance(value, dict):
        raise LocatorError("PUBLICATION_MISMATCH", f"{label} is not an object")
    return value


def _nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise LocatorError("PUBLICATION_MISMATCH", f"missing publication field: {'.'.join(keys)}")
        current = current[key]
    return current


def _validate_publication(raw: bytes, pins: ObjectPins) -> None:
    publication = _json_no_duplicates(raw, "publication")
    expected = {
        ("schema",): "rei-research-followthrough-publication/v1",
        ("repository",): pins.repository,
        ("pull_request", "number"): pins.pull_request_number,
        ("pull_request", "state_at_binding"): "OPEN_DRAFT_UNMERGED",
        ("pull_request", "base_branch"): pins.source_branch,
        ("pull_request", "base_head"): pins.source_commit,
        ("pull_request", "head_branch"): pins.remote_branch,
        ("immutable_payload", "commit"): pins.payload_commit,
        ("immutable_payload", "tree"): pins.payload_tree,
        ("immutable_payload", "path"): pins.payload_path,
        ("immutable_payload", "subtree_sha1"): pins.payload_subtree,
        ("immutable_payload", "manifest_blob_sha1"): pins.manifest_blob,
        ("immutable_payload", "manifest_entries"): pins.manifest_entries,
        ("immutable_payload", "validator"): pins.validator_path,
        ("preserved_preimage", "commit"): pins.helper_commit,
        ("preserved_preimage", "tree"): pins.helper_tree,
        ("preserved_preimage", "helper_blob"): pins.helper_blob,
        ("preserved_preimage", "disposition"): "UNCHANGED_HELPER_AND_ANCESTRY_RETAINED",
        ("verification", "canonical_source_map_adapter"): "NOT_RUN",
        ("verification", "all_node_pilot"): "NOT_RUN",
        ("verification", "complete_interval"): "NOT_RUN",
        ("claims", "PR14"): "STOP_INVALID_RETAINED",
        ("claims", "current"): "NO_PASS_FIRST_CANONICAL_INTERVAL",
        ("claims", "rec_splice"): False,
        ("claims", "performance"): "NONE",
        ("source_rec_lock_blob",): pins.rec_lock_blob,
        ("exact_next_action",): "REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER",
        ("scope",): "REMOTE_METADATA_OUTSIDE_IMMUTABLE_PAYLOAD_MANIFEST",
        ("merge_or_ready_authorized",): False,
    }
    for keys, wanted in expected.items():
        if _nested(publication, *keys) != wanted:
            raise LocatorError(
                "PUBLICATION_MISMATCH",
                f"publication field mismatch: {'.'.join(keys)}",
            )


def _verify_graph(repo: Path, pins: ObjectPins) -> VerifiedGraph:
    source_parents = () if pins.source_parent is None else (pins.source_parent,)
    _verify_commit(repo, pins.source_commit, pins.source_tree, source_parents)
    _verify_commit(repo, pins.helper_commit, pins.helper_tree, (pins.helper_parent,))
    _verify_commit(repo, pins.payload_commit, pins.payload_tree, (pins.payload_parent,))
    _verify_commit(repo, pins.terminal_commit, pins.terminal_tree, (pins.terminal_parent,))

    _require_entry(
        repo, pins.payload_commit, pins.payload_path, "040000", "tree", pins.payload_subtree
    )
    if pins.terminal_subtree is not None:
        _require_entry(
            repo,
            pins.terminal_commit,
            pins.payload_path,
            "040000",
            "tree",
            pins.terminal_subtree,
        )
    _require_entry(
        repo, pins.helper_commit, pins.helper_path, "100644", "blob", pins.helper_blob
    )
    _require_entry(
        repo, pins.payload_commit, pins.helper_path, "100644", "blob", pins.helper_blob
    )
    _require_entry(
        repo, pins.payload_commit, pins.manifest_path, "100644", "blob", pins.manifest_blob
    )
    _require_entry(
        repo, pins.payload_commit, pins.validator_path, "100644", "blob", pins.validator_blob
    )
    _require_entry(
        repo,
        pins.terminal_commit,
        pins.publication_path,
        "100644",
        "blob",
        pins.publication_blob,
    )
    _require_entry(
        repo, pins.source_commit, pins.rec_lock_path, "100644", "blob", pins.rec_lock_blob
    )
    _require_entry(
        repo,
        pins.source_commit,
        pins.blocked_archive_path,
        "100644",
        "blob",
        pins.blocked_archive_blob,
    )

    manifest_raw = _raw_object(repo, "blob", pins.manifest_blob)
    if _sha256(manifest_raw) != pins.manifest_sha256:
        raise LocatorError("OBJECT_MISMATCH", "manifest raw digest mismatch")
    publication_raw = _raw_object(repo, "blob", pins.publication_blob)
    if _sha256(publication_raw) != pins.publication_sha256:
        raise LocatorError("OBJECT_MISMATCH", "publication raw digest mismatch")
    validator_raw = _raw_object(repo, "blob", pins.validator_blob)
    if _sha256(validator_raw) != pins.validator_sha256:
        raise LocatorError("OBJECT_MISMATCH", "validator raw digest mismatch")
    archive_raw = _raw_object(repo, "blob", pins.blocked_archive_blob)
    if _sha256(archive_raw) != pins.blocked_archive_sha256:
        raise LocatorError("OBJECT_MISMATCH", "blocked archive digest mismatch")
    if pins.blocked_archive_size is not None and len(archive_raw) != pins.blocked_archive_size:
        raise LocatorError("OBJECT_MISMATCH", "blocked archive size mismatch")

    manifest = _parse_manifest(manifest_raw, pins)
    payload_raw: list[tuple[str, str, bytes]] = []
    for path, digest in manifest:
        entry = _tree_entry(repo, pins.payload_commit, path)
        if entry.mode != "100644" or entry.object_type != "blob":
            raise LocatorError("OBJECT_MISMATCH", f"unsafe payload mode or type: {path}")
        raw = _raw_object(repo, "blob", entry.sha)
        if _sha256(raw) != digest:
            raise LocatorError("OBJECT_MISMATCH", f"payload digest mismatch: {path}")
        payload_raw.append((path, digest, raw))

    by_path = {path: (digest, raw) for path, digest, raw in payload_raw}
    if _sha256(by_path[pins.validator_path][1]) != pins.validator_sha256:
        raise LocatorError("OBJECT_MISMATCH", "validator is not the pinned payload blob")
    if _sha256(by_path[pins.helper_path][1]) != _sha256(
        _raw_object(repo, "blob", pins.helper_blob)
    ):
        raise LocatorError("OBJECT_MISMATCH", "helper bytes changed in payload")
    _validate_publication(publication_raw, pins)
    return VerifiedGraph(tuple(payload_raw), manifest_raw, publication_raw)


def _fetch_exact(repo: Path, remote: str, terminal_commit: str) -> None:
    if not remote or remote.startswith("-"):
        raise LocatorError("FETCH_UNAVAILABLE", "invalid remote name")
    process = _run_git(
        repo,
        "fetch",
        "--no-tags",
        "--no-write-fetch-head",
        "--no-recurse-submodules",
        "--no-auto-maintenance",
        "--no-write-commit-graph",
        "--no-filter",
        "--refetch",
        "--refmap=",
        remote,
        terminal_commit,
        timeout=180,
        check=False,
    )
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise LocatorError("FETCH_UNAVAILABLE", f"exact object fetch failed: {detail}")


def _remote_ref_status(repo: Path, remote: str, pins: ObjectPins) -> str:
    process = _run_git(
        repo,
        "ls-remote",
        "--heads",
        remote,
        f"refs/heads/{pins.remote_branch}",
        timeout=60,
        check=False,
    )
    if process.returncode:
        return "NOT_CHECKED"
    lines = [line for line in process.stdout.splitlines() if line]
    if len(lines) != 1:
        return "DRIFT"
    fields = lines[0].split(b"\t", 1)
    if len(fields) != 2:
        return "NOT_CHECKED"
    try:
        tip = fields[0].decode("ascii")
    except UnicodeDecodeError:
        return "NOT_CHECKED"
    return "MATCH" if tip == pins.terminal_commit else "DRIFT"


def _write_raw(root: Path, relative: str, raw: bytes) -> Path:
    path = PurePosixPath(relative)
    target = root.joinpath(*path.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(target, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)
    os.chmod(target, 0o644, follow_symlinks=False)
    return target


def _stage_payload(stage: Path, graph: VerifiedGraph, pins: ObjectPins) -> None:
    for path, digest, raw in graph.payload_raw:
        target = _write_raw(stage, path, raw)
        if target.is_symlink() or _sha256(target.read_bytes()) != digest:
            raise LocatorError("MATERIALIZATION_FAILURE", f"staged payload mismatch: {path}")
    manifest = _write_raw(stage, pins.manifest_path, graph.manifest_raw)
    publication = _write_raw(stage, pins.publication_path, graph.publication_raw)
    if _sha256(manifest.read_bytes()) != pins.manifest_sha256:
        raise LocatorError("MATERIALIZATION_FAILURE", "staged manifest mismatch")
    if _sha256(publication.read_bytes()) != pins.publication_sha256:
        raise LocatorError("MATERIALIZATION_FAILURE", "staged publication mismatch")
    for directory in sorted(
        (path for path in stage.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        os.chmod(directory, 0o755, follow_symlinks=False)


def _expected_stage_directories(paths: Iterable[str]) -> set[str]:
    directories: set[str] = set()
    for value in paths:
        parent = PurePosixPath(value).parent
        while str(parent) != ".":
            directories.add(parent.as_posix())
            parent = parent.parent
    return directories


def _read_stage_identity(path: Path) -> StageIdentity:
    try:
        metadata = os.lstat(path)
    except OSError as error:
        raise LocatorError(
            "VALIDATOR_AUTH_MISMATCH", f"materialized root unavailable: {error}"
        ) from error
    return StageIdentity(
        device=metadata.st_dev,
        inode=metadata.st_ino,
        file_type=stat.S_IFMT(metadata.st_mode),
        mode=stat.S_IMODE(metadata.st_mode),
    )


def _capture_stage_identity(path: Path) -> StageIdentity:
    identity = _read_stage_identity(path)
    if identity.file_type != stat.S_IFDIR or identity.mode != 0o700:
        raise LocatorError(
            "MATERIALIZATION_FAILURE", "staging root is not a private directory"
        )
    return identity


def _rehash_stage(
    stage: Path,
    graph: VerifiedGraph,
    pins: ObjectPins,
    expected_root: StageIdentity,
) -> None:
    if _read_stage_identity(stage) != expected_root:
        raise LocatorError(
            "VALIDATOR_AUTH_MISMATCH", "materialized root identity or mode changed"
        )
    expected_paths = {
        *(path for path, _, _ in graph.payload_raw),
        pins.manifest_path,
        pins.publication_path,
    }
    expected_directories = _expected_stage_directories(expected_paths)
    actual_paths: set[str] = set()
    actual_directories: set[str] = set()
    for root, directory_names, file_names in os.walk(stage, followlinks=False):
        root_path = Path(root)
        for name in (*directory_names, *file_names):
            target = root_path / name
            relative = target.relative_to(stage).as_posix()
            metadata = os.lstat(target)
            if stat.S_ISDIR(metadata.st_mode):
                actual_directories.add(relative)
                if stat.S_IMODE(metadata.st_mode) != 0o755:
                    raise LocatorError(
                        "VALIDATOR_AUTH_MISMATCH", f"staged directory mode changed: {relative}"
                    )
            elif stat.S_ISREG(metadata.st_mode):
                actual_paths.add(relative)
                if stat.S_IMODE(metadata.st_mode) != 0o644:
                    raise LocatorError(
                        "VALIDATOR_AUTH_MISMATCH", f"staged mode changed: {relative}"
                    )
            else:
                raise LocatorError(
                    "VALIDATOR_AUTH_MISMATCH", f"unsafe materialized entry: {relative}"
                )
    if actual_paths != expected_paths or actual_directories != expected_directories:
        raise LocatorError(
            "VALIDATOR_AUTH_MISMATCH", "materialized path closure changed"
        )
    for path, digest, _ in graph.payload_raw:
        target = stage.joinpath(*PurePosixPath(path).parts)
        if target.is_symlink() or not target.is_file() or _sha256(target.read_bytes()) != digest:
            raise LocatorError("VALIDATOR_AUTH_MISMATCH", f"staged payload changed: {path}")
    for path, digest in (
        (pins.manifest_path, pins.manifest_sha256),
        (pins.publication_path, pins.publication_sha256),
    ):
        target = stage.joinpath(*PurePosixPath(path).parts)
        if target.is_symlink() or not target.is_file() or _sha256(target.read_bytes()) != digest:
            raise LocatorError("VALIDATOR_AUTH_MISMATCH", f"staged metadata changed: {path}")


def _read_regular_nofollow(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise LocatorError(
            "VALIDATOR_AUTH_MISMATCH", f"cannot open validator safely: {error}"
        ) from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise LocatorError("VALIDATOR_AUTH_MISMATCH", "validator is not regular")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        os.close(descriptor)


def _run_validator(
    stage: Path,
    repo: Path,
    pins: ObjectPins,
    authenticated_validator: bytes,
) -> dict[str, Any]:
    validator = stage.joinpath(*PurePosixPath(pins.validator_path).parts)
    validator_raw = _read_regular_nofollow(validator)
    if (
        validator_raw != authenticated_validator
        or _sha256(validator_raw) != pins.validator_sha256
    ):
        raise LocatorError("VALIDATOR_AUTH_MISMATCH", "validator changed before execution")
    environment = _git_environment()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        process = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-",
                "--root",
                str(stage),
                "--repo",
                str(repo),
            ],
            cwd=stage,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            input=validator_raw,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LocatorError("VALIDATOR_FAILURE", f"validator invocation failed: {error}") from error
    if process.returncode:
        detail = process.stderr.decode("utf-8", errors="replace").strip()
        raise LocatorError("VALIDATOR_FAILURE", f"validator failed: {detail}")
    try:
        result = json.loads(process.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise LocatorError("VALIDATOR_FAILURE", "validator emitted invalid JSON") from error
    if result != EXPECTED_VALIDATOR_RESULT:
        raise LocatorError("VALIDATOR_FAILURE", "validator result contract mismatch")
    return result


def _open_directory(path: Path) -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        return os.open(path, flags)
    except OSError as error:
        raise LocatorError("OUTPUT_POLICY", f"cannot bind output parent: {error}") from error


def _close_quietly(descriptor: int) -> None:
    """Release a descriptor without changing an already committed outcome."""

    try:
        os.close(descriptor)
    except OSError:
        pass


def _restore_stage_privacy(descriptor: int, expected: StageIdentity) -> None:
    """Restore mode 0700 on the originally bound stage inode, never its name."""

    try:
        before = os.fstat(descriptor)
        if (
            before.st_dev,
            before.st_ino,
            stat.S_IFMT(before.st_mode),
        ) != (
            expected.device,
            expected.inode,
            expected.file_type,
        ) or not stat.S_ISDIR(before.st_mode):
            raise LocatorError(
                "STAGE_PRIVACY_FAILURE", "bound stage identity changed before privacy restore"
            )
        if stat.S_IMODE(before.st_mode) != 0o700:
            os.fchmod(descriptor, 0o700)
        after = os.fstat(descriptor)
    except LocatorError:
        raise
    except OSError as error:
        raise LocatorError(
            "STAGE_PRIVACY_FAILURE", f"cannot restore bound stage mode 0700: {error}"
        ) from error
    if (
        after.st_dev,
        after.st_ino,
        stat.S_IFMT(after.st_mode),
        stat.S_IMODE(after.st_mode),
    ) != (
        expected.device,
        expected.inode,
        expected.file_type,
        0o700,
    ):
        raise LocatorError(
            "STAGE_PRIVACY_FAILURE", "bound stage mode 0700 restore did not persist"
        )


def _stage_retention_report(
    stage: Path, descriptor: int, expected: StageIdentity
) -> tuple[str | None, str]:
    """Report a pathname only while it still names the held stage inode."""

    try:
        parent_descriptor = _open_directory(stage.parent)
    except BaseException:
        return None, "BOUND_IDENTITY_PATH_UNAVAILABLE"
    try:
        try:
            named = os.stat(
                stage.name, dir_fd=parent_descriptor, follow_symlinks=False
            )
            held = os.fstat(descriptor)
        except OSError:
            return None, "BOUND_IDENTITY_PATH_UNAVAILABLE"
        if (
            named.st_dev,
            named.st_ino,
            stat.S_IFMT(named.st_mode),
        ) == (
            held.st_dev,
            held.st_ino,
            stat.S_IFMT(held.st_mode),
        ) == (
            expected.device,
            expected.inode,
            expected.file_type,
        ):
            return str(stage), "MATCHES_BOUND_IDENTITY"
        return None, "SUBSTITUTED_DO_NOT_REMOVE_REPORTED_NAME"
    finally:
        _close_quietly(parent_descriptor)


def _attach_stage_report(
    error: LocatorError,
    pathname: str | None,
    status: str | None,
    identity: StageIdentity | None,
) -> LocatorError:
    error.undeleted_stage_pathname = pathname
    error.stage_path_status = status
    if identity is not None:
        error.retained_stage_identity = {
            "device": identity.device,
            "inode": identity.inode,
            "type": "directory" if identity.file_type == stat.S_IFDIR else identity.file_type,
        }
    return error


def _directory_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _regular_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    return flags


def _identity(metadata: os.stat_result) -> StageIdentity:
    return StageIdentity(
        metadata.st_dev,
        metadata.st_ino,
        stat.S_IFMT(metadata.st_mode),
        stat.S_IMODE(metadata.st_mode),
    )


def _same_named_object(left: os.stat_result, right: os.stat_result) -> bool:
    return (
        left.st_dev,
        left.st_ino,
        stat.S_IFMT(left.st_mode),
        stat.S_IMODE(left.st_mode),
        left.st_size,
    ) == (
        right.st_dev,
        right.st_ino,
        stat.S_IFMT(right.st_mode),
        stat.S_IMODE(right.st_mode),
        right.st_size,
    )


def _hash_regular_descriptor(
    descriptor: int, before: os.stat_result, relative: str
) -> tuple[str, int]:
    digest = hashlib.sha256()
    offset = 0
    while offset < before.st_size:
        try:
            chunk = os.pread(descriptor, min(1024 * 1024, before.st_size - offset), offset)
        except OSError as error:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH",
                f"cannot read bound file {relative}: {error}",
            ) from error
        if not chunk:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", f"bound file truncated: {relative}"
            )
        digest.update(chunk)
        offset += len(chunk)
    try:
        extra = os.pread(descriptor, 1, offset)
        after = os.fstat(descriptor)
    except OSError as error:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH",
            f"cannot finish bound file read {relative}: {error}",
        ) from error
    if extra or not _same_named_object(before, after):
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", f"bound file changed while read: {relative}"
        )
    return digest.hexdigest(), offset


def _closure_record(
    kind: str, mode: int, relative: str, digest: str = "", size: int | None = None
) -> bytes:
    try:
        relative_raw = relative.encode("utf-8", errors="strict")
    except UnicodeEncodeError as error:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "non-UTF-8 materialized path"
        ) from error
    if b"\0" in relative_raw:
        raise LocatorError("DESTINATION_BINDING_MISMATCH", "NUL in materialized path")
    return b"\0".join(
        (
            kind.encode("ascii"),
            f"{mode:04o}".encode("ascii"),
            relative_raw,
            digest.encode("ascii"),
            b"" if size is None else str(size).encode("ascii"),
        )
    ) + b"\n"


def _digest_closure_records(
    records: Iterable[tuple[bytes, bytes]], files: int, directories: int
) -> ClosureDigest:
    digest = hashlib.sha256(CLOSURE_ALGORITHM.encode("ascii") + b"\0")
    for _, record in sorted(records, key=lambda item: item[0]):
        digest.update(record)
    return ClosureDigest(digest.hexdigest(), files, directories)


def _expected_closure(graph: VerifiedGraph, pins: ObjectPins) -> ClosureDigest:
    file_authorities = {
        path: (digest, len(raw)) for path, digest, raw in graph.payload_raw
    }
    file_authorities[pins.manifest_path] = (
        pins.manifest_sha256,
        len(graph.manifest_raw),
    )
    file_authorities[pins.publication_path] = (
        pins.publication_sha256,
        len(graph.publication_raw),
    )
    directories = _expected_stage_directories(file_authorities)
    records: list[tuple[bytes, bytes]] = []
    for path in directories:
        records.append(
            (os.fsencode(path), _closure_record("directory", 0o755, path))
        )
    for path, (digest, size) in file_authorities.items():
        records.append(
            (
                os.fsencode(path),
                _closure_record("file", 0o644, path, digest, size),
            )
        )
    return _digest_closure_records(records, len(file_authorities), len(directories))


def _scan_bound_directory(root_descriptor: int) -> ClosureDigest:
    """Hash an exact no-follow directory closure through already-bound fds."""

    records: list[tuple[bytes, bytes]] = []
    files = 0
    directories = 0

    def walk(directory_descriptor: int, prefix: str) -> None:
        nonlocal files, directories
        try:
            directory_before = os.fstat(directory_descriptor)
            names_before = os.listdir(directory_descriptor)
        except OSError as error:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", f"cannot enumerate bound directory: {error}"
            ) from error
        if not stat.S_ISDIR(directory_before.st_mode):
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", "bound closure root is not a directory"
            )
        for name in sorted(names_before, key=os.fsencode):
            if name in (".", "..") or "/" in name or "\0" in name:
                raise LocatorError(
                    "DESTINATION_BINDING_MISMATCH", "unsafe materialized entry name"
                )
            relative = f"{prefix}/{name}" if prefix else name
            try:
                named_before = os.stat(
                    name, dir_fd=directory_descriptor, follow_symlinks=False
                )
            except OSError as error:
                raise LocatorError(
                    "DESTINATION_BINDING_MISMATCH",
                    f"cannot inspect bound entry {relative}: {error}",
                ) from error
            mode = stat.S_IMODE(named_before.st_mode)
            if stat.S_ISDIR(named_before.st_mode):
                try:
                    child_descriptor = os.open(
                        name, _directory_flags(), dir_fd=directory_descriptor
                    )
                except OSError as error:
                    raise LocatorError(
                        "DESTINATION_BINDING_MISMATCH",
                        f"cannot bind directory {relative}: {error}",
                    ) from error
                try:
                    opened = os.fstat(child_descriptor)
                    if not _same_named_object(named_before, opened):
                        raise LocatorError(
                            "DESTINATION_BINDING_MISMATCH",
                            f"directory changed while bound: {relative}",
                        )
                    records.append(
                        (os.fsencode(relative), _closure_record("directory", mode, relative))
                    )
                    directories += 1
                    walk(child_descriptor, relative)
                    named_after = os.stat(
                        name, dir_fd=directory_descriptor, follow_symlinks=False
                    )
                    if not _same_named_object(opened, named_after):
                        raise LocatorError(
                            "DESTINATION_BINDING_MISMATCH",
                            f"directory name changed while scanned: {relative}",
                        )
                finally:
                    _close_quietly(child_descriptor)
            elif stat.S_ISREG(named_before.st_mode):
                try:
                    file_descriptor = os.open(
                        name, _regular_flags(), dir_fd=directory_descriptor
                    )
                except OSError as error:
                    raise LocatorError(
                        "DESTINATION_BINDING_MISMATCH",
                        f"cannot bind file {relative}: {error}",
                    ) from error
                try:
                    opened = os.fstat(file_descriptor)
                    if not _same_named_object(named_before, opened):
                        raise LocatorError(
                            "DESTINATION_BINDING_MISMATCH",
                            f"file changed while bound: {relative}",
                        )
                    raw_digest, size = _hash_regular_descriptor(
                        file_descriptor, opened, relative
                    )
                    named_after = os.stat(
                        name, dir_fd=directory_descriptor, follow_symlinks=False
                    )
                    if not _same_named_object(opened, named_after):
                        raise LocatorError(
                            "DESTINATION_BINDING_MISMATCH",
                            f"file name changed while scanned: {relative}",
                        )
                    records.append(
                        (
                            os.fsencode(relative),
                            _closure_record("file", mode, relative, raw_digest, size),
                        )
                    )
                    files += 1
                finally:
                    _close_quietly(file_descriptor)
            else:
                raise LocatorError(
                    "DESTINATION_BINDING_MISMATCH",
                    f"unsafe bound entry type: {relative}",
                )
        try:
            names_after = os.listdir(directory_descriptor)
            directory_after = os.fstat(directory_descriptor)
        except OSError as error:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH",
                f"cannot finish bound directory scan: {error}",
            ) from error
        if sorted(names_before, key=os.fsencode) != sorted(names_after, key=os.fsencode):
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", "bound directory closure changed while scanned"
            )
        if _identity(directory_before) != _identity(directory_after):
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", "bound directory identity changed"
            )

    try:
        duplicate = os.open(".", _directory_flags(), dir_fd=root_descriptor)
    except OSError as error:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", f"cannot duplicate bound root: {error}"
        ) from error
    try:
        walk(duplicate, "")
    finally:
        _close_quietly(duplicate)
    return _digest_closure_records(records, files, directories)


def _bind_destination(
    path: Path, expected: StageIdentity, expected_closure: ClosureDigest
) -> DestinationAuthority:
    parent_descriptor = _open_directory(path.parent)
    try:
        try:
            descriptor = os.open(path.name, _directory_flags(), dir_fd=parent_descriptor)
        except OSError as error:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", f"cannot bind destination root: {error}"
            ) from error
    finally:
        _close_quietly(parent_descriptor)
    try:
        metadata = os.fstat(descriptor)
        if _identity(metadata) != expected:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", "destination root identity or mode mismatch"
            )
        closure = _scan_bound_directory(descriptor)
        if closure != expected_closure:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH",
                "destination closure does not match authenticated source bytes",
            )
        return DestinationAuthority(descriptor, path, expected, closure)
    except BaseException:
        _close_quietly(descriptor)
        raise


def _verify_destination_authority(authority: DestinationAuthority) -> None:
    try:
        current_identity = _identity(os.fstat(authority.descriptor))
    except OSError as error:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", f"bound destination unavailable: {error}"
        ) from error
    if current_identity != authority.identity:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "bound destination identity or mode changed"
        )
    if _scan_bound_directory(authority.descriptor) != authority.closure:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "bound destination closure changed"
        )
    parent_descriptor = _open_directory(authority.path.parent)
    try:
        try:
            named = os.stat(
                authority.path.name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except OSError as error:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH",
                f"destination pathname no longer names the bound root: {error}",
            ) from error
        if _identity(named) != authority.identity:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH",
                "destination pathname no longer names the bound root",
            )
    finally:
        _close_quietly(parent_descriptor)


def _destination_binding_payload(authority: DestinationAuthority) -> dict[str, Any]:
    return {
        "schema": DESTINATION_BINDING_SCHEMA,
        "canonical_path": str(authority.path),
        "root": {
            "device": authority.identity.device,
            "inode": authority.identity.inode,
            "type": "directory",
            "mode": f"{authority.identity.mode:04o}",
        },
        "closure": {
            "algorithm": CLOSURE_ALGORITHM,
            "sha256": authority.closure.sha256,
            "files": authority.closure.files,
            "directories": authority.closure.directories,
        },
        "consumer_requirement": "FRESH_VERIFY_RECEIPT_DESTINATION_BEFORE_USE",
    }


def _read_exact_descriptor(descriptor: int, size: int) -> bytes:
    chunks: list[bytes] = []
    offset = 0
    while offset < size:
        chunk = os.pread(descriptor, min(1024 * 1024, size - offset), offset)
        if not chunk:
            break
        chunks.append(chunk)
        offset += len(chunk)
    if offset != size or os.pread(descriptor, 1, offset):
        raise LocatorError("MATERIALIZATION_FAILURE", "receipt authority size changed")
    return b"".join(chunks)


def _validate_receipt_authority(source: ReceiptAuthority) -> None:
    try:
        metadata = os.fstat(source.descriptor)
        raw = _read_exact_descriptor(source.descriptor, source.size)
    except OSError as error:
        raise LocatorError(
            "MATERIALIZATION_FAILURE", f"cannot authenticate receipt authority: {error}"
        ) from error
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o644
        or metadata.st_size != source.size
        or metadata.st_nlink != 0
        or len(raw) != source.size
        or _sha256(raw) != source.sha256
    ):
        raise LocatorError("MATERIALIZATION_FAILURE", "receipt authority mismatch")


def _write_receipt_temp(
    receipt: Path,
    pins: ObjectPins,
    result: dict[str, str],
    validator_result: dict[str, Any],
    destination: DestinationAuthority,
) -> ReceiptAuthority:
    data = {
        "schema": RECEIPT_SCHEMA,
        "repository": pins.repository,
        "result": result,
        "pins": asdict(pins),
        "validator_result": validator_result,
        "destination_binding": _destination_binding_payload(destination),
        "atomicity": RECEIPT_ATOMICITY,
    }
    raw = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if os.name != "posix" or not hasattr(os, "O_TMPFILE") or not hasattr(os, "pread"):
        raise LocatorError(
            "OUTPUT_POLICY", "anonymous atomic receipt publication is unavailable"
        )
    flags = os.O_RDWR | os.O_TMPFILE
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    try:
        descriptor = os.open(receipt.parent, flags, 0o600)
    except OSError as error:
        raise LocatorError(
            "OUTPUT_POLICY", f"cannot create anonymous receipt authority: {error}"
        ) from error
    authority = ReceiptAuthority(descriptor, _sha256(raw), len(raw))
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.fchmod(descriptor, 0o644)
        _validate_receipt_authority(authority)
    except BaseException:
        _close_quietly(descriptor)
        raise
    return authority


def _publish_directory_noreplace(source: Path, target: Path) -> None:
    """Atomically rename a directory without ever replacing the target name."""

    if os.name != "posix" or not hasattr(os, "O_DIRECTORY"):
        raise LocatorError(
            "OUTPUT_POLICY", "atomic no-replace directory publication is unavailable"
        )
    source_parent = _open_directory(source.parent)
    try:
        target_parent = _open_directory(target.parent)
    except BaseException:
        os.close(source_parent)
        raise
    try:
        library = ctypes.CDLL(None, use_errno=True)
        renameat2 = getattr(library, "renameat2", None)
        if renameat2 is None:
            raise LocatorError(
                "OUTPUT_POLICY", "renameat2 no-replace publication is unavailable"
            )
        renameat2.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        renameat2.restype = ctypes.c_int
        outcome = renameat2(
            source_parent,
            os.fsencode(source.name),
            target_parent,
            os.fsencode(target.name),
            1,  # RENAME_NOREPLACE
        )
        if outcome == 0:
            return
        error_number = ctypes.get_errno()
        if error_number in (errno.EEXIST, errno.ENOTEMPTY):
            raise LocatorError(
                "DESTINATION_EXISTS", "destination appeared before atomic publication"
            )
        if error_number in (errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP):
            raise LocatorError(
                "OUTPUT_POLICY", "filesystem lacks atomic no-replace directory publication"
            )
        raise LocatorError(
            "MATERIALIZATION_FAILURE",
            f"atomic destination publication failed: {os.strerror(error_number)}",
        )
    finally:
        os.close(target_parent)
        os.close(source_parent)


def _receipt_link_arguments(
    source_descriptor: int, target_parent: int, target_name: str
) -> tuple[int, bytes, int, bytes, int]:
    """Build the unprivileged proc-fd linkat call (no CAP_DAC_READ_SEARCH)."""

    return (
        -100,  # AT_FDCWD
        os.fsencode(f"/proc/self/fd/{source_descriptor}"),
        target_parent,
        os.fsencode(target_name),
        0x400,  # AT_SYMLINK_FOLLOW
    )


def _link_receipt_fd(
    source_descriptor: int, target_parent: int, target_name: str
) -> int:
    """Return zero or errno from a capability-free anonymous-inode link."""

    library = ctypes.CDLL(None, use_errno=True)
    linkat = getattr(library, "linkat", None)
    if linkat is None:
        return errno.ENOSYS
    linkat.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
    )
    linkat.restype = ctypes.c_int
    outcome = linkat(
        *_receipt_link_arguments(source_descriptor, target_parent, target_name)
    )
    return 0 if outcome == 0 else ctypes.get_errno()


def _publish_file_noreplace(
    source: ReceiptAuthority,
    target: Path,
    destination: DestinationAuthority,
) -> None:
    """Commit the preauthenticated receipt with one final no-clobber link."""

    _validate_receipt_authority(source)
    target_parent = _open_directory(target.parent)
    try:
        # This is the last fallible destination observation.  A later same-UID
        # rename cannot invalidate the immutable binding stored in the receipt;
        # consumers must freshly verify that binding before use.
        _verify_destination_authority(destination)
        error_number = _link_receipt_fd(
            source.descriptor, target_parent, target.name
        )
        if error_number == 0:
            return
        if error_number in (errno.EEXIST, errno.ENOTEMPTY):
            raise LocatorError(
                "RECEIPT_EXISTS", "receipt appeared before atomic publication"
            )
        if error_number in (
            errno.ENOENT,
            errno.EACCES,
            errno.EPERM,
            errno.ENOSYS,
            errno.EINVAL,
            errno.EOPNOTSUPP,
        ):
            raise LocatorError(
                "OUTPUT_POLICY",
                "filesystem or procfs lacks unprivileged anonymous receipt publication",
            )
        raise LocatorError(
            "MATERIALIZATION_FAILURE",
            f"atomic receipt publication failed: {os.strerror(error_number)}",
        )
    finally:
        # After a successful link, descriptor release is non-semantic: a close
        # error must not turn an already committed PASS receipt into failure.
        _close_quietly(target_parent)


def _canonical_existing_final(path: Path, label: str) -> Path:
    lexical = Path(path)
    if not lexical.is_absolute():
        lexical = Path.cwd() / lexical
    if not lexical.name:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", f"{label} has no final path component"
        )
    try:
        parent = lexical.parent.resolve(strict=True)
    except OSError as error:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", f"{label} parent unavailable: {error}"
        ) from error
    return parent / lexical.name


def _read_receipt_nofollow(path: Path) -> bytes:
    parent_descriptor = _open_directory(path.parent)
    try:
        try:
            descriptor = os.open(path.name, _regular_flags(), dir_fd=parent_descriptor)
        except OSError as error:
            raise LocatorError(
                "DESTINATION_BINDING_MISMATCH", f"cannot bind receipt: {error}"
            ) from error
        try:
            before = os.fstat(descriptor)
            if (
                not stat.S_ISREG(before.st_mode)
                or stat.S_IMODE(before.st_mode) != 0o644
            ):
                raise LocatorError(
                    "DESTINATION_BINDING_MISMATCH", "receipt type or mode mismatch"
                )
            try:
                raw = _read_exact_descriptor(descriptor, before.st_size)
                after = os.fstat(descriptor)
                named_after = os.stat(
                    path.name, dir_fd=parent_descriptor, follow_symlinks=False
                )
            except (OSError, LocatorError) as error:
                raise LocatorError(
                    "DESTINATION_BINDING_MISMATCH", f"cannot read stable receipt: {error}"
                ) from error
            if (
                not _same_named_object(before, after)
                or not _same_named_object(after, named_after)
            ):
                raise LocatorError(
                    "DESTINATION_BINDING_MISMATCH", "receipt changed while read"
                )
            return raw
        finally:
            _close_quietly(descriptor)
    finally:
        _close_quietly(parent_descriptor)


def _binding_json(raw: bytes) -> dict[str, Any]:
    try:
        return _json_no_duplicates(raw, "locator receipt")
    except LocatorError as error:
        raise LocatorError("DESTINATION_BINDING_MISMATCH", str(error)) from error


def _require_plain_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", f"invalid receipt binding integer: {label}"
        )
    return value


def verify_receipt_destination(
    destination: Path,
    receipt: Path,
    *,
    expected_receipt_sha256: str,
    pins: ObjectPins = PRODUCTION_PINS,
) -> dict[str, Any]:
    """Freshly verify a v2 receipt and return only after fd-bound closure checks."""

    _validate_pins(pins)
    _validate_sha(expected_receipt_sha256, 64, "expected_receipt_sha256")
    destination = _canonical_existing_final(destination, "destination")
    receipt = _canonical_existing_final(receipt, "receipt")
    raw = _read_receipt_nofollow(receipt)
    if _sha256(raw) != expected_receipt_sha256:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "receipt digest is not the retained authority"
        )
    document = _binding_json(raw)
    expected_top = {
        "schema",
        "repository",
        "result",
        "pins",
        "validator_result",
        "destination_binding",
        "atomicity",
    }
    if set(document) != expected_top:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "receipt top-level closure mismatch"
        )
    normalized_pins = json.loads(json.dumps(asdict(pins), sort_keys=True))
    result = document.get("result")
    if not isinstance(result, dict):
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "receipt result is not an object"
        )
    remote_status = result.get("remote_ref_status")
    if remote_status not in {"MATCH", "DRIFT", "NOT_CHECKED"}:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "receipt remote status is invalid"
        )
    if {
        key: value for key, value in result.items() if key != "remote_ref_status"
    } != BASE_RESULT:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "receipt result contract mismatch"
        )
    if (
        document.get("schema") != RECEIPT_SCHEMA
        or document.get("repository") != pins.repository
        or document.get("pins") != normalized_pins
        or document.get("validator_result") != EXPECTED_VALIDATOR_RESULT
        or document.get("atomicity") != RECEIPT_ATOMICITY
    ):
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "receipt authority contract mismatch"
        )
    binding = document.get("destination_binding")
    if not isinstance(binding, dict) or set(binding) != {
        "schema",
        "canonical_path",
        "root",
        "closure",
        "consumer_requirement",
    }:
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "destination binding shape mismatch"
        )
    if (
        binding.get("schema") != DESTINATION_BINDING_SCHEMA
        or binding.get("canonical_path") != str(destination)
        or binding.get("consumer_requirement")
        != "FRESH_VERIFY_RECEIPT_DESTINATION_BEFORE_USE"
    ):
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "destination binding path or schema mismatch"
        )
    root = binding.get("root")
    closure = binding.get("closure")
    if (
        not isinstance(root, dict)
        or set(root) != {"device", "inode", "type", "mode"}
        or root.get("type") != "directory"
        or root.get("mode") != "0700"
        or not isinstance(closure, dict)
        or set(closure) != {"algorithm", "sha256", "files", "directories"}
        or closure.get("algorithm") != CLOSURE_ALGORITHM
        or not isinstance(closure.get("sha256"), str)
        or SHA256_RE.fullmatch(closure["sha256"]) is None
    ):
        raise LocatorError(
            "DESTINATION_BINDING_MISMATCH", "destination binding fields mismatch"
        )
    identity = StageIdentity(
        _require_plain_int(root.get("device"), "device"),
        _require_plain_int(root.get("inode"), "inode"),
        stat.S_IFDIR,
        0o700,
    )
    expected_closure = ClosureDigest(
        closure["sha256"],
        _require_plain_int(closure.get("files"), "files"),
        _require_plain_int(closure.get("directories"), "directories"),
    )
    authority = _bind_destination(destination, identity, expected_closure)
    try:
        _verify_destination_authority(authority)
    finally:
        _close_quietly(authority.descriptor)
    return {
        "status": "PASS_DESTINATION_BINDING",
        "receipt_sha256": expected_receipt_sha256,
        "closure_sha256": expected_closure.sha256,
        "files": expected_closure.files,
        "directories": expected_closure.directories,
    }


def fetch_and_validate(
    repo: Path,
    destination: Path,
    receipt: Path | None = None,
    pins: ObjectPins = PRODUCTION_PINS,
    remote: str = "origin",
) -> LocatorResult:
    """Authenticate, materialize, and run the pinned payload validator once."""

    _validate_pins(pins)
    repo = _repository_root(Path(repo))
    destination, receipt = _validate_output_locations(repo, Path(destination), receipt)
    before = snapshot_repository(repo)
    stage: Path | None = None
    stage_identity: StageIdentity | None = None
    stage_descriptor: int | None = None
    destination_authority: DestinationAuthority | None = None
    receipt_temporary: ReceiptAuthority | None = None
    try:
        try:
            graph = _verify_graph(repo, pins)
        except LocatorError as error:
            if error.code != "OBJECT_UNAVAILABLE":
                raise
            _fetch_exact(repo, remote, pins.terminal_commit)
            try:
                graph = _verify_graph(repo, pins)
            except LocatorError as retry_error:
                if retry_error.code == "OBJECT_UNAVAILABLE":
                    raise LocatorError(
                        "FETCH_UNAVAILABLE", "exact fetch did not close the pinned object graph"
                    ) from retry_error
                raise

        remote_ref_status = _remote_ref_status(repo, remote, pins)
        expected_closure = _expected_closure(graph, pins)
        stage = Path(
            tempfile.mkdtemp(prefix=f".{destination.name}.locator-", dir=destination.parent)
        )
        stage_identity = _capture_stage_identity(stage)
        stage_descriptor = _open_directory(stage)
        if _identity(os.fstat(stage_descriptor)) != stage_identity:
            raise LocatorError(
                "MATERIALIZATION_FAILURE", "staging root changed while binding descriptor"
            )
        _stage_payload(stage, graph, pins)
        _rehash_stage(stage, graph, pins, stage_identity)
        authenticated_validator = next(
            raw for path, _, raw in graph.payload_raw if path == pins.validator_path
        )
        validator_result = _run_validator(
            stage, repo, pins, authenticated_validator
        )
        _rehash_stage(stage, graph, pins, stage_identity)

        after_validation = snapshot_repository(repo)
        if after_validation != before:
            raise LocatorError("REPOSITORY_MUTATED", "repository state changed during locator run")

        result = {**BASE_RESULT, "remote_ref_status": remote_ref_status}

        if destination.exists() or destination.is_symlink():
            raise LocatorError("DESTINATION_EXISTS", "destination appeared during validation")
        if receipt.exists() or receipt.is_symlink():
            raise LocatorError("RECEIPT_EXISTS", "receipt appeared during validation")
        _publish_directory_noreplace(stage, destination)
        stage = None
        _rehash_stage(destination, graph, pins, stage_identity)
        destination_authority = _bind_destination(
            destination, stage_identity, expected_closure
        )
        _close_quietly(stage_descriptor)
        stage_descriptor = None

        if snapshot_repository(repo) != before:
            raise LocatorError("REPOSITORY_MUTATED", "repository state changed at publication")

        receipt_temporary = _write_receipt_temp(
            receipt, pins, result, validator_result, destination_authority
        )
        success = LocatorResult(result, receipt_temporary.sha256)
        _publish_file_noreplace(
            receipt_temporary, receipt, destination_authority
        )
        _close_quietly(receipt_temporary.descriptor)
        receipt_temporary = None
        _close_quietly(destination_authority.descriptor)
        destination_authority = None

        return success
    except BaseException as error:
        privacy_error: LocatorError | None = None
        retained_stage_pathname: str | None = None
        stage_path_status: str | None = None
        retained_stage_identity: StageIdentity | None = None
        if stage_descriptor is not None and stage_identity is not None:
            retained_stage_identity = stage_identity
            try:
                _restore_stage_privacy(stage_descriptor, stage_identity)
            except LocatorError as restore_error:
                privacy_error = restore_error
            if stage is not None:
                retained_stage_pathname, stage_path_status = _stage_retention_report(
                    stage, stage_descriptor, stage_identity
                )
        elif stage is not None:
            retained_stage_identity = stage_identity
            stage_path_status = "UNBOUND_NO_AUTHORITATIVE_PATH"
        if stage_descriptor is not None:
            _close_quietly(stage_descriptor)
        if receipt_temporary is not None:
            _close_quietly(receipt_temporary.descriptor)
        if destination_authority is not None:
            _close_quietly(destination_authority.descriptor)
        # Published names are never removed by pathname during error handling:
        # a concurrent owner may have exchanged either name.  In particular,
        # an authenticated destination remains available when receipt
        # publication loses a no-clobber race.
        try:
            after = snapshot_repository(repo)
        except BaseException:
            after = before
        repository_changed = after != before
        if privacy_error is not None:
            if repository_changed:
                privacy_error = LocatorError(
                    "STAGE_PRIVACY_FAILURE",
                    f"{privacy_error}; repository also changed while handling the failure",
                )
            raise _attach_stage_report(
                privacy_error,
                retained_stage_pathname,
                stage_path_status,
                retained_stage_identity,
            ) from error
        if repository_changed and not (
            isinstance(error, LocatorError) and error.code == "REPOSITORY_MUTATED"
        ):
            repository_error = LocatorError(
                "REPOSITORY_MUTATED",
                f"repository changed while handling {type(error).__name__}",
            )
            raise _attach_stage_report(
                repository_error,
                retained_stage_pathname,
                stage_path_status,
                retained_stage_identity,
            ) from error
        if isinstance(error, LocatorError):
            raise _attach_stage_report(
                error,
                retained_stage_pathname,
                stage_path_status,
                retained_stage_identity,
            )
        wrapped = LocatorError("MATERIALIZATION_FAILURE", str(error))
        raise _attach_stage_report(
            wrapped,
            retained_stage_pathname,
            stage_path_status,
            retained_stage_identity,
        ) from error


EXIT_CODES = {
    "INVALID_PIN": 10,
    "REPOSITORY_POLICY": 11,
    "OUTPUT_POLICY": 12,
    "DESTINATION_EXISTS": 13,
    "RECEIPT_EXISTS": 14,
    "FETCH_UNAVAILABLE": 20,
    "GIT_FAILURE": 21,
    "OBJECT_MISMATCH": 22,
    "PUBLICATION_MISMATCH": 23,
    "VALIDATOR_AUTH_MISMATCH": 30,
    "VALIDATOR_FAILURE": 31,
    "REPOSITORY_MUTATED": 32,
    "DESTINATION_BINDING_MISMATCH": 33,
    "MATERIALIZATION_FAILURE": 40,
    "STAGE_PRIVACY_FAILURE": 41,
}


def _error_payload(error: LocatorError) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "FAIL",
        "code": error.code,
        "message": str(error),
    }
    if error.undeleted_stage_pathname is not None:
        payload["undeleted_stage_pathname"] = error.undeleted_stage_pathname
    if error.stage_path_status is not None:
        payload["stage_path_status"] = error.stage_path_status
    if error.retained_stage_identity is not None:
        payload["retained_stage_identity"] = error.retained_stage_identity
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--verify-receipt", type=Path)
    parser.add_argument("--expected-receipt-sha256")
    parser.add_argument("--remote", default="origin")
    arguments = parser.parse_args(argv)
    if arguments.verify_receipt is not None:
        if arguments.repo is not None or arguments.receipt is not None:
            parser.error("--verify-receipt cannot be combined with --repo or --receipt")
        if arguments.expected_receipt_sha256 is None:
            parser.error("--verify-receipt requires --expected-receipt-sha256")
        try:
            verification = verify_receipt_destination(
                arguments.destination,
                arguments.verify_receipt,
                expected_receipt_sha256=arguments.expected_receipt_sha256,
            )
        except LocatorError as error:
            print(
                json.dumps(_error_payload(error), sort_keys=True),
                file=sys.stderr,
            )
            return EXIT_CODES.get(error.code, 1)
        print(json.dumps(verification, sort_keys=True))
        return 0
    if arguments.repo is None:
        parser.error("normal locator mode requires --repo")
    if arguments.expected_receipt_sha256 is not None:
        parser.error("--expected-receipt-sha256 requires --verify-receipt")
    try:
        result = fetch_and_validate(
            arguments.repo,
            arguments.destination,
            arguments.receipt,
            PRODUCTION_PINS,
            arguments.remote,
        )
    except LocatorError as error:
        print(
            json.dumps(_error_payload(error), sort_keys=True),
            file=sys.stderr,
        )
        return EXIT_CODES.get(error.code, 1)
    output = dict(result)
    output["receipt_sha256"] = result.receipt_sha256
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
