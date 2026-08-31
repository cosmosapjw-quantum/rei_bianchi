"""Fail-closed BASS/REC custody and reference-publication substrate.

This module deliberately does *not* implement a numerical BASS lock.  It
provides only the boundary needed before such a lock can be attempted:

* exact, local-only Git object custody checks for separately supplied BASS and
  REC authority pins;
* rejection of partial-clone/promisor configuration in both repository-common
  and worktree-local configuration scopes;
* a reference-only certificate graph with explicit wire/admitted authority
  separation (raw certificate payloads are not part of this representation);
  and
* descriptor-bound publication through an unnamed ``O_TMPFILE`` inode.  The
  validated inode is linked into the destination directory directly through
  ``/proc/self/fd`` so there is no validated-path/renamed-path swap window.

The exact BASS and REC physical authority pins are intentionally absent from
this repository.  Callers must supply both pins; absence is a typed blocker.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import stat
import subprocess
from typing import Callable, Iterable, Mapping, Sequence


REFERENCE_GRAPH_SCHEMA = "REI_BASS_REFERENCE_GRAPH_V1"
REFERENCE_GRAPH_REPRESENTATION = "REFERENCE_ONLY_NO_RAW_CERTIFICATE_PAYLOAD"
PUBLICATION_METHOD = "LINUX_O_TMPFILE_DESCRIPTOR_HARDLINK_V1"
_AUTHORITY_ADMISSION_TOKEN = object()
_GRAPH_ADMISSION_TOKEN = object()

_HEX_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
_HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_FORBIDDEN_RAW_KEYS = {
    "certificate",
    "certificate_bytes",
    "certificate_payload",
    "payload",
    "payload_bytes",
    "raw_certificate",
    "raw_certificate_payload",
}


class BassIntegrationError(RuntimeError):
    """A typed fail-closed integration error."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _fail(code: str, detail: str) -> "None":
    raise BassIntegrationError(code, detail)


def _require_sha256(value: str, field: str) -> str:
    if not isinstance(value, str) or _HEX_SHA256.fullmatch(value) is None:
        _fail("BASS_REFERENCE_IDENTITY_INVALID", f"{field} must be lowercase SHA-256")
    return value


def _require_oid(value: str, field: str) -> str:
    if not isinstance(value, str) or _HEX_OID.fullmatch(value) is None:
        _fail("BASS_GIT_AUTHORITY_INVALID", f"{field} must be a full lowercase Git OID")
    return value


def _require_project(value: str) -> str:
    if value not in {"BASS", "REC"}:
        _fail("BASS_GIT_AUTHORITY_INVALID", "project must be exactly BASS or REC")
    return value


def _require_relative_git_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("BASS_GIT_AUTHORITY_INVALID", "blob path must be non-empty")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value:
        _fail("BASS_GIT_AUTHORITY_INVALID", f"unsafe or non-canonical blob path: {value!r}")
    return value


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode(
        "ascii"
    )


@dataclass(frozen=True, slots=True)
class BlobPin:
    path: str
    oid: str

    def __post_init__(self) -> None:
        _require_relative_git_path(self.path)
        _require_oid(self.oid, f"blob[{self.path}].oid")

    def to_mapping(self) -> dict[str, str]:
        return {"oid": self.oid, "path": self.path}


@dataclass(frozen=True, slots=True)
class GitAuthorityPin:
    project: str
    repository_url: str
    commit_oid: str
    tree_oid: str
    blobs: tuple[BlobPin, ...]

    def __post_init__(self) -> None:
        _require_project(self.project)
        if not isinstance(self.repository_url, str) or not self.repository_url:
            _fail("BASS_GIT_AUTHORITY_INVALID", "repository_url must be non-empty")
        _require_oid(self.commit_oid, "commit_oid")
        _require_oid(self.tree_oid, "tree_oid")
        if not self.blobs:
            _fail("BASS_GIT_AUTHORITY_INVALID", "at least one load-bearing blob pin is required")
        paths = [item.path for item in self.blobs]
        if len(paths) != len(set(paths)):
            _fail("BASS_GIT_AUTHORITY_INVALID", "blob pin paths must be unique")

    def to_mapping(self) -> dict[str, object]:
        return {
            "blobs": [item.to_mapping() for item in sorted(self.blobs, key=lambda item: item.path)],
            "commit_oid": self.commit_oid,
            "project": self.project,
            "repository_url": self.repository_url,
            "tree_oid": self.tree_oid,
        }


@dataclass(frozen=True, slots=True)
class GitCustodyReceipt:
    """Serializable custody statement.

    The digest is an integrity checksum, not proof that Git objects were
    observed.  Claim-bearing graph construction requires the separate
    :class:`AdmittedGitAuthority` capability returned by
    :func:`validate_local_git_authority`.
    """

    authority: GitAuthorityPin
    common_config_sha256: str
    worktree_config_sha256: str | None
    receipt_sha256: str

    def identity_mapping(self) -> dict[str, object]:
        return {
            "authority": self.authority.to_mapping(),
            "common_config_sha256": self.common_config_sha256,
            "worktree_config_sha256": self.worktree_config_sha256,
        }

    def to_mapping(self) -> dict[str, object]:
        value = self.identity_mapping()
        value["receipt_sha256"] = self.receipt_sha256
        return value


@dataclass(frozen=True, slots=True, init=False)
class AdmittedGitAuthority:
    """Process-local capability minted only after local Git custody replay."""

    receipt: GitCustodyReceipt
    _admission_token: object

    @classmethod
    def _from_validated_receipt(
        cls,
        receipt: GitCustodyReceipt,
        token: object,
    ) -> "AdmittedGitAuthority":
        if token is not _AUTHORITY_ADMISSION_TOKEN:
            _fail("BASS_AUTHORITY_NOT_ADMITTED", "invalid authority admission token")
        instance = object.__new__(cls)
        object.__setattr__(instance, "receipt", receipt)
        object.__setattr__(instance, "_admission_token", token)
        return instance

    @property
    def authority(self) -> GitAuthorityPin:
        return self.receipt.authority

    @property
    def common_config_sha256(self) -> str:
        return self.receipt.common_config_sha256

    @property
    def worktree_config_sha256(self) -> str | None:
        return self.receipt.worktree_config_sha256

    @property
    def receipt_sha256(self) -> str:
        return self.receipt.receipt_sha256

    def to_mapping(self) -> dict[str, object]:
        return self.receipt.to_mapping()


def require_exact_bass_rec_pins(
    bass_pin: GitAuthorityPin | None,
    rec_pin: GitAuthorityPin | None,
) -> tuple[GitAuthorityPin, GitAuthorityPin]:
    """Require exact separately supplied BASS and REC authorities.

    The repository intentionally does not guess, reconstruct, or inherit these
    identities from branch names, pull requests, or endpoint-only fixtures.
    """

    missing: list[str] = []
    if bass_pin is None:
        missing.append("BASS")
    if rec_pin is None:
        missing.append("REC")
    if missing:
        _fail(
            "BASS_REC_EXACT_AUTHORITY_MISSING",
            "exact commit/tree/load-bearing-blob authority absent for " + ",".join(missing),
        )
    assert bass_pin is not None and rec_pin is not None
    if bass_pin.project != "BASS" or rec_pin.project != "REC":
        _fail("BASS_REC_EXACT_AUTHORITY_MISMATCH", "pins must be ordered as BASS then REC")
    return bass_pin, rec_pin


def _git_executable() -> str:
    executable = shutil.which("git")
    if executable is None:
        _fail("BASS_GIT_RUNTIME_MISSING", "git executable not found")
    return str(Path(executable).resolve())


def _git_environment() -> dict[str, str]:
    return {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
    }


def _run_git(
    repo: Path,
    *args: str,
    input_bytes: bytes | None = None,
    _pass_fds: Sequence[int] = (),
    _environment_overrides: Mapping[str, str] | None = None,
) -> bytes:
    environment = _git_environment()
    if _environment_overrides is not None:
        environment.update(_environment_overrides)
    command = [_git_executable(), "--no-replace-objects", "-C", str(repo), *args]
    completed = subprocess.run(
        command,
        check=False,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        pass_fds=tuple(_pass_fds),
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        _fail("BASS_GIT_CUSTODY_CHECK_FAILED", f"git {' '.join(args)}: {detail}")
    return completed.stdout


def _resolve_git_dirs(repo: Path, *, pass_fds: Sequence[int] = ()) -> tuple[Path, Path]:
    git_dir = Path(
        _run_git(
            repo,
            "rev-parse",
            "--absolute-git-dir",
            _pass_fds=pass_fds,
        ).decode("utf-8").strip()
    )
    common_output = _run_git(
        repo,
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
        _pass_fds=pass_fds,
    ).decode("utf-8").strip()
    common_dir = Path(common_output)
    if not git_dir.is_absolute() or not common_dir.is_absolute():
        _fail("BASS_GIT_REPOSITORY_INVALID", "Git directory resolution was not absolute")
    return git_dir, common_dir


@dataclass(frozen=True, slots=True)
class _StatIdentity:
    device: int
    inode: int
    mode: int
    size: int
    mtime_ns: int
    ctime_ns: int


def _stat_identity(value: os.stat_result) -> _StatIdentity:
    return _StatIdentity(
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


@dataclass(frozen=True, slots=True)
class _ConfigSnapshot:
    entries: tuple[tuple[str, str], ...]
    sha256: str
    identity: _StatIdentity


@dataclass(frozen=True, slots=True)
class _ObjectStoreSnapshot:
    objects_identity: _StatIdentity
    info_identity: _StatIdentity | None
    pack_identity: _StatIdentity | None


@dataclass(frozen=True, slots=True)
class _GitCustodySnapshot:
    repository_identity: _StatIdentity
    git_directory_identity: _StatIdentity
    common_directory_identity: _StatIdentity
    resolved_git_directory: str
    resolved_common_directory: str
    common_config: _ConfigSnapshot
    worktree_config: _ConfigSnapshot | None
    common_objects: _ObjectStoreSnapshot
    git_directory_objects: _ObjectStoreSnapshot | None


@dataclass(slots=True)
class _OpenedGitNamespace:
    repository_path: Path
    git_directory_path: Path
    common_directory_path: Path
    repository_fd: int
    git_directory_fd: int
    common_directory_fd: int
    common_objects_fd: int

    def pass_fds(self) -> tuple[int, ...]:
        return (
            self.repository_fd,
            self.git_directory_fd,
            self.common_directory_fd,
            self.common_objects_fd,
        )

    def exact_environment(self) -> dict[str, str]:
        return {
            "GIT_COMMON_DIR": f"/proc/self/fd/{self.common_directory_fd}",
            "GIT_DIR": f"/proc/self/fd/{self.git_directory_fd}",
            "GIT_OBJECT_DIRECTORY": f"/proc/self/fd/{self.common_objects_fd}",
            "GIT_WORK_TREE": f"/proc/self/fd/{self.repository_fd}",
        }

    def close(self) -> None:
        for name in (
            "common_objects_fd",
            "common_directory_fd",
            "git_directory_fd",
            "repository_fd",
        ):
            fd = getattr(self, name)
            if fd >= 0:
                os.close(fd)
                setattr(self, name, -1)


_DIRECTORY_OPEN_FLAGS = (
    os.O_RDONLY
    | os.O_DIRECTORY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)


def _open_directory(path: Path, scope: str) -> int:
    try:
        fd = os.open(path, _DIRECTORY_OPEN_FLAGS)
    except OSError as exc:
        _fail("BASS_CUSTODY_NAMESPACE_INVALID", f"{scope}: {exc}")
    if not stat.S_ISDIR(os.fstat(fd).st_mode):
        os.close(fd)
        _fail("BASS_CUSTODY_NAMESPACE_INVALID", f"{scope} is not a directory")
    return fd


def _open_directory_at(parent_fd: int, name: str, scope: str, *, required: bool) -> int | None:
    try:
        return os.open(name, _DIRECTORY_OPEN_FLAGS, dir_fd=parent_fd)
    except FileNotFoundError:
        if not required:
            return None
        _fail("BASS_CUSTODY_NAMESPACE_INVALID", f"{scope} is missing")
    except OSError as exc:
        _fail("BASS_CUSTODY_NAMESPACE_INVALID", f"{scope}: {exc}")


def _open_git_namespace(repo_path: str | os.PathLike[str]) -> _OpenedGitNamespace:
    repository_path = Path(repo_path).resolve(strict=True)
    repository_fd = _open_directory(repository_path, "repository")
    git_directory_fd = -1
    common_directory_fd = -1
    common_objects_fd = -1
    try:
        descriptor_path = Path(f"/proc/self/fd/{repository_fd}")
        git_directory_path, common_directory_path = _resolve_git_dirs(
            descriptor_path,
            pass_fds=(repository_fd,),
        )
        git_directory_fd = _open_directory(git_directory_path, "Git directory")
        common_directory_fd = _open_directory(common_directory_path, "Git common directory")
        opened_objects = _open_directory_at(
            common_directory_fd,
            "objects",
            "common objects directory",
            required=True,
        )
        assert opened_objects is not None
        common_objects_fd = opened_objects
        return _OpenedGitNamespace(
            repository_path,
            git_directory_path,
            common_directory_path,
            repository_fd,
            git_directory_fd,
            common_directory_fd,
            common_objects_fd,
        )
    except Exception:
        for fd in (common_objects_fd, common_directory_fd, git_directory_fd, repository_fd):
            if fd >= 0:
                os.close(fd)
        raise


def _read_config_snapshot_at(
    directory_fd: int,
    name: str,
    scope: str,
    *,
    required: bool,
) -> _ConfigSnapshot | None:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(name, flags, dir_fd=directory_fd)
    except FileNotFoundError:
        if not required:
            return None
        _fail("BASS_CUSTODY_CONFIG_MISSING", f"{scope} Git config is missing")
    except OSError as exc:
        _fail("BASS_CUSTODY_CONFIG_UNREADABLE", f"{scope} config: {exc}")
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            _fail("BASS_CUSTODY_CONFIG_INVALID", f"{scope} config is not a regular file")
        raw = b""
        offset = 0
        while True:
            chunk = os.pread(fd, 1024 * 1024, offset)
            if not chunk:
                break
            raw += chunk
            offset += len(chunk)
        digest = hashlib.sha256(raw).hexdigest()
        command = [
            _git_executable(),
            "config",
            "--no-includes",
            "--file",
            f"/proc/self/fd/{fd}",
            "--null",
            "--list",
        ]
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_git_environment(),
            pass_fds=(fd,),
        )
        if completed.returncode != 0:
            detail = completed.stderr.decode("utf-8", "replace").strip()
            _fail("BASS_CUSTODY_CONFIG_INVALID", f"{scope} config parse failed: {detail}")
        entries: list[tuple[str, str]] = []
        for record in completed.stdout.split(b"\0"):
            if not record:
                continue
            if b"\n" in record:
                key_bytes, value_bytes = record.split(b"\n", 1)
            else:
                key_bytes, value_bytes = record, b""
            entries.append(
                (
                    key_bytes.decode("utf-8", "strict"),
                    value_bytes.decode("utf-8", "strict"),
                )
            )
        after = os.fstat(fd)
        if _stat_identity(before) != _stat_identity(after):
            _fail("BASS_CUSTODY_VALIDATION_RACE", f"{scope} config changed while read")
        return _ConfigSnapshot(tuple(entries), digest, _stat_identity(after))
    finally:
        os.close(fd)


def _reject_lazy_config(entries: Iterable[tuple[str, str]], scope: str) -> None:
    for key, value in entries:
        lowered = key.lower()
        if (
            lowered.startswith("include.")
            or lowered == "include.path"
            or lowered.startswith("includeif.")
        ):
            _fail(
                "BASS_CUSTODY_CONFIG_INCLUDE_FORBIDDEN",
                f"{scope} config contains unresolved include key {key}",
            )
        forbidden = (
            lowered == "extensions.partialclone"
            or lowered == "core.partialclonefilter"
            or (lowered.startswith("remote.") and lowered.endswith(".promisor"))
            or (lowered.startswith("remote.") and lowered.endswith(".partialclonefilter"))
        )
        if forbidden:
            _fail(
                "BASS_CUSTODY_LAZY_OBJECT_CONFIG_FORBIDDEN",
                f"{scope} config contains {key}={value}",
            )


def _reject_worktree_authority_override(entries: Iterable[tuple[str, str]]) -> None:
    for key, value in entries:
        if key.lower() == "remote.origin.url":
            _fail(
                "BASS_GIT_AUTHORITY_REMOTE_MISMATCH",
                f"worktree config must not override remote.origin.url; observed {value!r}",
            )


def _one_config_value(entries: Sequence[tuple[str, str]], key: str, scope: str) -> str:
    matches = [value for current_key, value in entries if current_key.lower() == key.lower()]
    if len(matches) != 1:
        _fail(
            "BASS_GIT_AUTHORITY_REMOTE_MISMATCH",
            f"{scope} must contain exactly one {key}, found {len(matches)}",
        )
    return matches[0]


def _forbidden_namespace_code(phase: str, steady_code: str) -> str:
    if phase == "pre":
        return steady_code
    return "BASS_CUSTODY_VALIDATION_RACE"


def _reject_entry_at(
    directory_fd: int,
    name: str,
    detail: str,
    *,
    phase: str,
) -> None:
    try:
        os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as exc:
        _fail("BASS_CUSTODY_NAMESPACE_INVALID", f"{detail}: {exc}")
    _fail(
        _forbidden_namespace_code(
            phase,
            "BASS_CUSTODY_EXTERNAL_OR_SHALLOW_OBJECTS_FORBIDDEN",
        ),
        detail,
    )


def _scan_object_store(
    objects_fd: int,
    scope: str,
    *,
    phase: str,
) -> _ObjectStoreSnapshot:
    objects_before = _stat_identity(os.fstat(objects_fd))
    info_fd = _open_directory_at(objects_fd, "info", f"{scope} objects/info", required=False)
    info_identity: _StatIdentity | None = None
    if info_fd is not None:
        try:
            info_before = _stat_identity(os.fstat(info_fd))
            _reject_entry_at(
                info_fd,
                "alternates",
                f"{scope} objects/info/alternates",
                phase=phase,
            )
            _reject_entry_at(
                info_fd,
                "http-alternates",
                f"{scope} objects/info/http-alternates",
                phase=phase,
            )
            info_after = _stat_identity(os.fstat(info_fd))
            if info_after != info_before:
                _fail(
                    "BASS_CUSTODY_VALIDATION_RACE",
                    f"{scope} objects/info changed while scanned",
                )
            info_identity = info_after
        finally:
            os.close(info_fd)

    pack_fd = _open_directory_at(objects_fd, "pack", f"{scope} objects/pack", required=False)
    pack_identity: _StatIdentity | None = None
    if pack_fd is not None:
        try:
            pack_before = _stat_identity(os.fstat(pack_fd))
            try:
                names = os.listdir(pack_fd)
            except OSError as exc:
                _fail("BASS_CUSTODY_NAMESPACE_INVALID", f"{scope} objects/pack: {exc}")
            markers = sorted(name for name in names if name.endswith(".promisor"))
            if markers:
                _fail(
                    _forbidden_namespace_code(
                        phase,
                        "BASS_CUSTODY_PROMISOR_PACK_FORBIDDEN",
                    ),
                    f"{scope} promisor pack markers: {','.join(markers)}",
                )
            pack_after = _stat_identity(os.fstat(pack_fd))
            if pack_after != pack_before:
                _fail(
                    "BASS_CUSTODY_VALIDATION_RACE",
                    f"{scope} objects/pack changed while scanned",
                )
            pack_identity = pack_after
        finally:
            os.close(pack_fd)

    objects_after = _stat_identity(os.fstat(objects_fd))
    if objects_after != objects_before:
        _fail("BASS_CUSTODY_VALIDATION_RACE", f"{scope} objects changed while scanned")
    return _ObjectStoreSnapshot(objects_after, info_identity, pack_identity)


def _require_directory_path_matches_fd(path: Path, fd: int, scope: str, *, phase: str) -> None:
    try:
        current_fd = os.open(path, _DIRECTORY_OPEN_FLAGS)
    except OSError as exc:
        code = "BASS_CUSTODY_NAMESPACE_INVALID" if phase == "pre" else "BASS_CUSTODY_VALIDATION_RACE"
        _fail(code, f"{scope}: {exc}")
    try:
        current = os.fstat(current_fd)
        pinned = os.fstat(fd)
        if (current.st_dev, current.st_ino) != (pinned.st_dev, pinned.st_ino):
            code = (
                "BASS_CUSTODY_NAMESPACE_INVALID"
                if phase == "pre"
                else "BASS_CUSTODY_VALIDATION_RACE"
            )
            _fail(code, f"{scope} no longer names the descriptor-pinned directory")
    finally:
        os.close(current_fd)


def _capture_git_custody_snapshot(
    namespace: _OpenedGitNamespace,
    *,
    phase: str,
) -> _GitCustodySnapshot:
    _require_directory_path_matches_fd(
        namespace.repository_path,
        namespace.repository_fd,
        "repository path",
        phase=phase,
    )
    _require_directory_path_matches_fd(
        namespace.git_directory_path,
        namespace.git_directory_fd,
        "Git directory path",
        phase=phase,
    )
    _require_directory_path_matches_fd(
        namespace.common_directory_path,
        namespace.common_directory_fd,
        "Git common directory path",
        phase=phase,
    )
    _require_directory_path_matches_fd(
        namespace.common_directory_path / "objects",
        namespace.common_objects_fd,
        "common objects path",
        phase=phase,
    )

    resolved_git, resolved_common = _resolve_git_dirs(
        Path(f"/proc/self/fd/{namespace.repository_fd}"),
        pass_fds=(namespace.repository_fd,),
    )
    if resolved_git != namespace.git_directory_path or resolved_common != namespace.common_directory_path:
        code = "BASS_CUSTODY_NAMESPACE_INVALID" if phase == "pre" else "BASS_CUSTODY_VALIDATION_RACE"
        _fail(code, "repository Git directory resolution changed")

    common_config = _read_config_snapshot_at(
        namespace.common_directory_fd,
        "config",
        "common",
        required=True,
    )
    assert common_config is not None
    _reject_lazy_config(common_config.entries, "common")
    worktree_config = _read_config_snapshot_at(
        namespace.git_directory_fd,
        "config.worktree",
        "worktree",
        required=False,
    )
    if worktree_config is not None:
        _reject_lazy_config(worktree_config.entries, "worktree")
        _reject_worktree_authority_override(worktree_config.entries)

    _reject_entry_at(
        namespace.common_directory_fd,
        "shallow",
        "common shallow boundary",
        phase=phase,
    )
    if (
        os.fstat(namespace.git_directory_fd).st_dev,
        os.fstat(namespace.git_directory_fd).st_ino,
    ) != (
        os.fstat(namespace.common_directory_fd).st_dev,
        os.fstat(namespace.common_directory_fd).st_ino,
    ):
        _reject_entry_at(
            namespace.git_directory_fd,
            "shallow",
            "worktree shallow boundary",
            phase=phase,
        )

    common_objects = _scan_object_store(namespace.common_objects_fd, "common", phase=phase)
    git_objects: _ObjectStoreSnapshot | None = None
    same_git_common = (
        os.fstat(namespace.git_directory_fd).st_dev,
        os.fstat(namespace.git_directory_fd).st_ino,
    ) == (
        os.fstat(namespace.common_directory_fd).st_dev,
        os.fstat(namespace.common_directory_fd).st_ino,
    )
    if not same_git_common:
        git_objects_fd = _open_directory_at(
            namespace.git_directory_fd,
            "objects",
            "worktree Git-directory objects",
            required=False,
        )
        if git_objects_fd is not None:
            try:
                git_objects = _scan_object_store(
                    git_objects_fd,
                    "worktree Git-directory",
                    phase=phase,
                )
            finally:
                os.close(git_objects_fd)

    return _GitCustodySnapshot(
        _stat_identity(os.fstat(namespace.repository_fd)),
        _stat_identity(os.fstat(namespace.git_directory_fd)),
        _stat_identity(os.fstat(namespace.common_directory_fd)),
        str(resolved_git),
        str(resolved_common),
        common_config,
        worktree_config,
        common_objects,
        git_objects,
    )


def _require_unchanged_git_custody(
    namespace: _OpenedGitNamespace,
    baseline: _GitCustodySnapshot,
) -> None:
    observed = _capture_git_custody_snapshot(namespace, phase="guard")
    if observed != baseline:
        _fail(
            "BASS_CUSTODY_VALIDATION_RACE",
            "Git directory/config/object-store identity changed during authority validation",
        )


def _run_exact_git(
    namespace: _OpenedGitNamespace,
    baseline: _GitCustodySnapshot,
    *args: str,
) -> bytes:
    _require_unchanged_git_custody(namespace, baseline)
    output = _run_git(
        Path(f"/proc/self/fd/{namespace.repository_fd}"),
        *args,
        _pass_fds=namespace.pass_fds(),
        _environment_overrides=namespace.exact_environment(),
    )
    _require_unchanged_git_custody(namespace, baseline)
    return output


def validate_local_git_authority(
    repo_path: str | os.PathLike[str],
    pin: GitAuthorityPin,
) -> AdmittedGitAuthority:
    """Validate one exact Git authority without network or lazy object fetch.

    The repository, Git/common directories, and primary object store are held
    by descriptor for the complete validation. Config, directory metadata,
    alternates boundaries, and promisor-pack state are compared before and
    after every exact Git read. Any observable namespace mutation is a typed
    failure rather than a custody admission.
    """

    namespace = _open_git_namespace(repo_path)
    try:
        baseline = _capture_git_custody_snapshot(namespace, phase="pre")
        common_entries = baseline.common_config.entries
        common_digest = baseline.common_config.sha256
        worktree_digest = (
            None if baseline.worktree_config is None else baseline.worktree_config.sha256
        )

        origin_url = _one_config_value(common_entries, "remote.origin.url", "common config")
        if origin_url != pin.repository_url:
            _fail(
                "BASS_GIT_AUTHORITY_REMOTE_MISMATCH",
                f"expected {pin.repository_url!r}, observed {origin_url!r}",
            )

        observed_commit = _run_exact_git(
            namespace,
            baseline,
            "rev-parse",
            "--verify",
            f"{pin.commit_oid}^{{commit}}",
        ).decode("ascii").strip()
        if observed_commit != pin.commit_oid:
            _fail("BASS_GIT_AUTHORITY_COMMIT_MISMATCH", f"observed {observed_commit}")
        observed_tree = _run_exact_git(
            namespace,
            baseline,
            "show",
            "-s",
            "--format=%T",
            pin.commit_oid,
        ).decode("ascii").strip()
        if observed_tree != pin.tree_oid:
            _fail(
                "BASS_GIT_AUTHORITY_TREE_MISMATCH",
                f"expected {pin.tree_oid}, observed {observed_tree}",
            )

        for blob in pin.blobs:
            output = _run_exact_git(
                namespace,
                baseline,
                "ls-tree",
                "-z",
                "--full-tree",
                pin.commit_oid,
                "--",
                blob.path,
            )
            records = [record for record in output.split(b"\0") if record]
            if len(records) != 1 or b"\t" not in records[0]:
                _fail("BASS_GIT_AUTHORITY_BLOB_MISSING", f"{pin.project}:{blob.path}")
            metadata, observed_path = records[0].split(b"\t", 1)
            parts = metadata.split()
            if len(parts) != 3 or parts[1] != b"blob":
                _fail("BASS_GIT_AUTHORITY_BLOB_MISSING", f"{pin.project}:{blob.path}")
            observed_oid = parts[2].decode("ascii")
            if observed_path.decode("utf-8", "surrogateescape") != blob.path or observed_oid != blob.oid:
                _fail(
                    "BASS_GIT_AUTHORITY_BLOB_MISMATCH",
                    f"{pin.project}:{blob.path} expected {blob.oid}, observed {observed_oid}",
                )
            _run_exact_git(namespace, baseline, "cat-file", "-e", f"{blob.oid}^{{blob}}")

        _require_unchanged_git_custody(namespace, baseline)
        unsigned = {
            "authority": pin.to_mapping(),
            "common_config_sha256": common_digest,
            "worktree_config_sha256": worktree_digest,
        }
        receipt_digest = hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        receipt = GitCustodyReceipt(pin, common_digest, worktree_digest, receipt_digest)
        return AdmittedGitAuthority._from_validated_receipt(receipt, _AUTHORITY_ADMISSION_TOKEN)
    finally:
        namespace.close()


@dataclass(frozen=True, slots=True)
class CertificateReference:
    ref_id: str
    owner_project: str
    role: str
    media_type: str
    sha256: str
    size_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.ref_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]+", self.ref_id):
            _fail("BASS_REFERENCE_GRAPH_INVALID", "invalid ref_id")
        _require_project(self.owner_project)
        if not isinstance(self.role, str) or not self.role:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "reference role must be non-empty")
        if not isinstance(self.media_type, str) or not self.media_type:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "reference media_type must be non-empty")
        _require_sha256(self.sha256, f"reference[{self.ref_id}].sha256")
        if not isinstance(self.size_bytes, int) or isinstance(self.size_bytes, bool) or self.size_bytes < 0:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "reference size_bytes must be a non-negative integer")

    def to_mapping(self) -> dict[str, object]:
        return {
            "media_type": self.media_type,
            "owner_project": self.owner_project,
            "ref_id": self.ref_id,
            "role": self.role,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True, slots=True)
class ReferenceEdge:
    parent_ref: str
    child_ref: str
    relationship: str

    def __post_init__(self) -> None:
        for field, value in (("parent_ref", self.parent_ref), ("child_ref", self.child_ref)):
            if not isinstance(value, str) or not value:
                _fail("BASS_REFERENCE_GRAPH_INVALID", f"{field} must be non-empty")
        if self.parent_ref == self.child_ref:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "self edges are forbidden")
        if not isinstance(self.relationship, str) or not self.relationship:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "relationship must be non-empty")

    def to_mapping(self) -> dict[str, str]:
        return {
            "child_ref": self.child_ref,
            "parent_ref": self.parent_ref,
            "relationship": self.relationship,
        }


@dataclass(frozen=True, slots=True)
class ReferenceOnlyCertificateGraph:
    authorities: tuple[GitCustodyReceipt, GitCustodyReceipt]
    references: tuple[CertificateReference, ...]
    edges: tuple[ReferenceEdge, ...]
    graph_sha256: str

    def _unsigned_mapping(self) -> dict[str, object]:
        return {
            "authorities": [receipt.to_mapping() for receipt in self.authorities],
            "edges": [edge.to_mapping() for edge in self.edges],
            "raw_certificate_payloads": "NOT_ADMITTED",
            "references": [reference.to_mapping() for reference in self.references],
            "representation": REFERENCE_GRAPH_REPRESENTATION,
            "schema": REFERENCE_GRAPH_SCHEMA,
        }

    def to_mapping(self) -> dict[str, object]:
        value = self._unsigned_mapping()
        value["graph_sha256"] = self.graph_sha256
        return value

    def to_bytes(self) -> bytes:
        return _canonical_json(self.to_mapping())


def _validate_custody_receipt(receipt: GitCustodyReceipt) -> None:
    _require_sha256(receipt.common_config_sha256, "common_config_sha256")
    if receipt.worktree_config_sha256 is not None:
        _require_sha256(receipt.worktree_config_sha256, "worktree_config_sha256")
    _require_sha256(receipt.receipt_sha256, "receipt_sha256")
    expected = hashlib.sha256(_canonical_json(receipt.identity_mapping())).hexdigest()
    if receipt.receipt_sha256 != expected:
        _fail(
            "BASS_CUSTODY_RECEIPT_DIGEST_MISMATCH",
            f"{receipt.authority.project} custody receipt digest mismatch",
        )


def _assert_acyclic(reference_ids: set[str], edges: Sequence[ReferenceEdge]) -> None:
    children: dict[str, list[str]] = {ref_id: [] for ref_id in reference_ids}
    indegree = {ref_id: 0 for ref_id in reference_ids}
    for edge in edges:
        if edge.parent_ref not in reference_ids or edge.child_ref not in reference_ids:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "edge references an unknown node")
        children[edge.parent_ref].append(edge.child_ref)
        indegree[edge.child_ref] += 1
    queue = sorted(ref_id for ref_id, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        current = queue.pop(0)
        visited += 1
        for child in sorted(children[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
                queue.sort()
    if visited != len(reference_ids):
        _fail("BASS_REFERENCE_GRAPH_INVALID", "reference graph contains a cycle")


def _build_reference_graph_from_wire_receipts(
    bass_receipt: GitCustodyReceipt,
    rec_receipt: GitCustodyReceipt,
    references: Sequence[CertificateReference],
    edges: Sequence[ReferenceEdge],
) -> ReferenceOnlyCertificateGraph:
    _validate_custody_receipt(bass_receipt)
    _validate_custody_receipt(rec_receipt)
    if bass_receipt.authority.project != "BASS" or rec_receipt.authority.project != "REC":
        _fail("BASS_REC_EXACT_AUTHORITY_MISMATCH", "custody receipts must be ordered BASS then REC")
    if not references:
        _fail("BASS_REFERENCE_GRAPH_INVALID", "at least one certificate reference is required")
    reference_tuple = tuple(sorted(references, key=lambda item: item.ref_id))
    ids = [item.ref_id for item in reference_tuple]
    if len(ids) != len(set(ids)):
        _fail("BASS_REFERENCE_GRAPH_INVALID", "reference IDs must be unique")
    edge_tuple = tuple(
        sorted(edges, key=lambda item: (item.parent_ref, item.child_ref, item.relationship))
    )
    _assert_acyclic(set(ids), edge_tuple)
    provisional = ReferenceOnlyCertificateGraph(
        (bass_receipt, rec_receipt),
        reference_tuple,
        edge_tuple,
        "0" * 64,
    )
    digest = hashlib.sha256(_canonical_json(provisional._unsigned_mapping())).hexdigest()
    return ReferenceOnlyCertificateGraph(
        provisional.authorities,
        provisional.references,
        provisional.edges,
        digest,
    )


def _admitted_receipt(authority: object, expected_project: str) -> GitCustodyReceipt:
    if not isinstance(authority, AdmittedGitAuthority):
        _fail(
            "BASS_AUTHORITY_NOT_ADMITTED",
            f"{expected_project} authority must come from validate_local_git_authority",
        )
    try:
        token = object.__getattribute__(authority, "_admission_token")
        receipt = object.__getattribute__(authority, "receipt")
    except AttributeError:
        _fail("BASS_AUTHORITY_NOT_ADMITTED", f"{expected_project} capability is incomplete")
    if token is not _AUTHORITY_ADMISSION_TOKEN or not isinstance(receipt, GitCustodyReceipt):
        _fail("BASS_AUTHORITY_NOT_ADMITTED", f"{expected_project} capability token is invalid")
    _validate_custody_receipt(receipt)
    if receipt.authority.project != expected_project:
        _fail(
            "BASS_REC_EXACT_AUTHORITY_MISMATCH",
            f"expected {expected_project}, observed {receipt.authority.project}",
        )
    return receipt


def build_reference_only_graph(
    bass_authority: AdmittedGitAuthority,
    rec_authority: AdmittedGitAuthority,
    references: Sequence[CertificateReference],
    edges: Sequence[ReferenceEdge],
) -> ReferenceOnlyCertificateGraph:
    """Build a claim-bearing in-process graph from admitted authorities only."""

    bass_receipt = _admitted_receipt(bass_authority, "BASS")
    rec_receipt = _admitted_receipt(rec_authority, "REC")
    return _build_reference_graph_from_wire_receipts(
        bass_receipt,
        rec_receipt,
        references,
        edges,
    )


@dataclass(frozen=True, slots=True)
class ReferenceGraphWireValidation:
    """Structural wire replay that deliberately carries no authority claim."""

    envelope: Mapping[str, object]
    graph: ReferenceOnlyCertificateGraph
    payload_sha256: str
    claim_bearing: bool = False
    status: str = "WIRE_STRUCTURAL_ONLY_NOT_AUTHORITY_ADMISSION"

    def __getitem__(self, key: str) -> object:
        return self.envelope[key]


@dataclass(frozen=True, slots=True, init=False)
class AdmittedReferenceGraph:
    graph: ReferenceOnlyCertificateGraph
    payload_sha256: str
    _admission_token: object

    @classmethod
    def _from_external_admission(
        cls,
        graph: ReferenceOnlyCertificateGraph,
        payload_sha256: str,
        token: object,
    ) -> "AdmittedReferenceGraph":
        if token is not _GRAPH_ADMISSION_TOKEN:
            _fail("BASS_REFERENCE_GRAPH_NOT_ADMITTED", "invalid graph admission token")
        instance = object.__new__(cls)
        object.__setattr__(instance, "graph", graph)
        object.__setattr__(instance, "payload_sha256", payload_sha256)
        object.__setattr__(instance, "_admission_token", token)
        return instance

    @property
    def claim_bearing(self) -> bool:
        return object.__getattribute__(self, "_admission_token") is _GRAPH_ADMISSION_TOKEN

    @property
    def status(self) -> str:
        if not self.claim_bearing:
            _fail("BASS_REFERENCE_GRAPH_NOT_ADMITTED", "graph admission token is invalid")
        return "ADMITTED_EXTERNAL_AUTHORITY_AND_PAYLOAD_DIGEST"


def _reject_raw_payload_keys(value: object) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                _fail("BASS_REFERENCE_GRAPH_INVALID", "JSON object keys must be strings")
            if key.lower() in _FORBIDDEN_RAW_KEYS:
                _fail("BASS_RAW_CERTIFICATE_PAYLOAD_FORBIDDEN", f"forbidden key: {key}")
            _reject_raw_payload_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_raw_payload_keys(child)


def validate_reference_graph_bytes(data: bytes) -> ReferenceGraphWireValidation:
    """Replay syntax and self-consistency without admitting an authority claim."""

    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("BASS_REFERENCE_GRAPH_INVALID", f"invalid JSON: {exc}")
    _reject_raw_payload_keys(value)
    if not isinstance(value, dict):
        _fail("BASS_REFERENCE_GRAPH_INVALID", "graph must be a JSON object")
    expected_keys = {
        "authorities",
        "edges",
        "graph_sha256",
        "raw_certificate_payloads",
        "references",
        "representation",
        "schema",
    }
    if set(value) != expected_keys:
        _fail("BASS_REFERENCE_GRAPH_INVALID", "graph envelope keys are not closed")
    if value["schema"] != REFERENCE_GRAPH_SCHEMA:
        _fail("BASS_REFERENCE_GRAPH_INVALID", "wrong graph schema")
    if value["representation"] != REFERENCE_GRAPH_REPRESENTATION:
        _fail("BASS_REFERENCE_GRAPH_INVALID", "wrong graph representation")
    if value["raw_certificate_payloads"] != "NOT_ADMITTED":
        _fail("BASS_RAW_CERTIFICATE_PAYLOAD_FORBIDDEN", "raw payload admission is forbidden")
    if _canonical_json(value) != data:
        _fail("BASS_REFERENCE_GRAPH_NONCANONICAL", "graph bytes are not canonical JSON")

    try:
        authority_values = value["authorities"]
        reference_values = value["references"]
        edge_values = value["edges"]
        if not isinstance(authority_values, list) or len(authority_values) != 2:
            _fail("BASS_REFERENCE_GRAPH_INVALID", "exactly two authority receipts are required")
        receipts: list[GitCustodyReceipt] = []
        for receipt_value in authority_values:
            if not isinstance(receipt_value, dict) or set(receipt_value) != {
                "authority",
                "common_config_sha256",
                "receipt_sha256",
                "worktree_config_sha256",
            }:
                _fail("BASS_REFERENCE_GRAPH_INVALID", "custody receipt keys are not closed")
            authority_value = receipt_value["authority"]
            if not isinstance(authority_value, dict) or set(authority_value) != {
                "blobs",
                "commit_oid",
                "project",
                "repository_url",
                "tree_oid",
            }:
                _fail("BASS_REFERENCE_GRAPH_INVALID", "authority pin keys are not closed")
            blob_values = authority_value["blobs"]
            if not isinstance(blob_values, list):
                _fail("BASS_REFERENCE_GRAPH_INVALID", "authority blobs must be a list")
            blobs: list[BlobPin] = []
            for blob_value in blob_values:
                if not isinstance(blob_value, dict) or set(blob_value) != {"oid", "path"}:
                    _fail("BASS_REFERENCE_GRAPH_INVALID", "blob pin keys are not closed")
                blobs.append(BlobPin(blob_value["path"], blob_value["oid"]))
            pin = GitAuthorityPin(
                authority_value["project"],
                authority_value["repository_url"],
                authority_value["commit_oid"],
                authority_value["tree_oid"],
                tuple(blobs),
            )
            worktree_digest = receipt_value["worktree_config_sha256"]
            if worktree_digest is not None and not isinstance(worktree_digest, str):
                _fail("BASS_REFERENCE_GRAPH_INVALID", "worktree config digest must be string or null")
            receipt = GitCustodyReceipt(
                pin,
                receipt_value["common_config_sha256"],
                worktree_digest,
                receipt_value["receipt_sha256"],
            )
            _validate_custody_receipt(receipt)
            receipts.append(receipt)

        if not isinstance(reference_values, list):
            _fail("BASS_REFERENCE_GRAPH_INVALID", "references must be a list")
        references: list[CertificateReference] = []
        for reference_value in reference_values:
            if not isinstance(reference_value, dict) or set(reference_value) != {
                "media_type",
                "owner_project",
                "ref_id",
                "role",
                "sha256",
                "size_bytes",
            }:
                _fail("BASS_REFERENCE_GRAPH_INVALID", "reference keys are not closed")
            references.append(
                CertificateReference(
                    reference_value["ref_id"],
                    reference_value["owner_project"],
                    reference_value["role"],
                    reference_value["media_type"],
                    reference_value["sha256"],
                    reference_value["size_bytes"],
                )
            )

        if not isinstance(edge_values, list):
            _fail("BASS_REFERENCE_GRAPH_INVALID", "edges must be a list")
        edges: list[ReferenceEdge] = []
        for edge_value in edge_values:
            if not isinstance(edge_value, dict) or set(edge_value) != {
                "child_ref",
                "parent_ref",
                "relationship",
            }:
                _fail("BASS_REFERENCE_GRAPH_INVALID", "edge keys are not closed")
            edges.append(
                ReferenceEdge(
                    edge_value["parent_ref"],
                    edge_value["child_ref"],
                    edge_value["relationship"],
                )
            )
        rebuilt = _build_reference_graph_from_wire_receipts(
            receipts[0],
            receipts[1],
            references,
            edges,
        )
    except (KeyError, TypeError) as exc:
        _fail("BASS_REFERENCE_GRAPH_INVALID", f"invalid graph field type: {exc}")
    if rebuilt.graph_sha256 != _require_sha256(value["graph_sha256"], "graph_sha256"):
        _fail("BASS_REFERENCE_GRAPH_DIGEST_MISMATCH", "graph digest does not match envelope")
    if rebuilt.to_mapping() != value:
        _fail("BASS_REFERENCE_GRAPH_NONCANONICAL", "graph member order or values are non-canonical")
    return ReferenceGraphWireValidation(
        value,
        rebuilt,
        hashlib.sha256(data).hexdigest(),
    )


def admit_reference_graph_bytes(
    data: bytes,
    bass_authority: AdmittedGitAuthority,
    rec_authority: AdmittedGitAuthority,
    expected_payload_sha256: str,
) -> AdmittedReferenceGraph:
    """Admit serialized graph bytes against external authority capabilities.

    The graph's internal receipt and graph digests are self-consistency fields.
    A claim-bearing admission additionally requires independently admitted BASS
    and REC capabilities plus an externally supplied SHA-256 of the complete
    serialized payload.
    """

    _require_sha256(expected_payload_sha256, "expected_payload_sha256")
    validation = validate_reference_graph_bytes(data)
    if validation.payload_sha256 != expected_payload_sha256:
        _fail(
            "BASS_REFERENCE_GRAPH_EXTERNAL_DIGEST_MISMATCH",
            f"expected {expected_payload_sha256}, observed {validation.payload_sha256}",
        )
    admitted_bass = _admitted_receipt(bass_authority, "BASS")
    admitted_rec = _admitted_receipt(rec_authority, "REC")
    observed_authorities = validation.graph.authorities
    if observed_authorities != (admitted_bass, admitted_rec):
        _fail(
            "BASS_REFERENCE_GRAPH_EXTERNAL_AUTHORITY_MISMATCH",
            "wire authority receipts differ from admitted BASS/REC capabilities",
        )
    return AdmittedReferenceGraph._from_external_admission(
        validation.graph,
        validation.payload_sha256,
        _GRAPH_ADMISSION_TOKEN,
    )


@dataclass(frozen=True, slots=True)
class PublicationReceipt:
    destination: str
    sha256: str
    size_bytes: int
    device: int
    inode: int
    method: str = PUBLICATION_METHOD


@dataclass(slots=True)
class _PublishedHandle:
    receipt: PublicationReceipt
    directory_fd: int
    filename: str

    def close(self) -> None:
        if self.directory_fd >= 0:
            os.close(self.directory_fd)
            self.directory_fd = -1


def _read_fd(fd: int) -> bytes:
    size = os.fstat(fd).st_size
    chunks: list[bytes] = []
    offset = 0
    while offset < size:
        chunk = os.pread(fd, min(1024 * 1024, size - offset), offset)
        if not chunk:
            _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "unexpected EOF")
        chunks.append(chunk)
        offset += len(chunk)
    return b"".join(chunks)


def _sha256_fd(fd: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = os.fstat(fd).st_size
    offset = 0
    while offset < size:
        chunk = os.pread(fd, min(1024 * 1024, size - offset), offset)
        if not chunk:
            _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "unexpected EOF")
        digest.update(chunk)
        offset += len(chunk)
    return digest.hexdigest(), size


def _write_all(fd: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        count = os.write(fd, view)
        if count <= 0:
            _fail("BASS_DESCRIPTOR_PUBLICATION_FAILED", "short write")
        view = view[count:]


def _require_read_only_regular_file(fd: int, detail: str) -> os.stat_result:
    observed = os.fstat(fd)
    if not stat.S_ISREG(observed.st_mode) or stat.S_IMODE(observed.st_mode) != 0o444:
        _fail(
            "BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED",
            f"{detail} mode is {oct(stat.S_IMODE(observed.st_mode))}, expected 0o444",
        )
    return observed


def _require_publication_parent_matches_fd(parent: Path, expected_fd: int) -> None:
    try:
        current_fd = os.open(parent, _DIRECTORY_OPEN_FLAGS)
    except OSError as exc:
        _fail(
            "BASS_DESCRIPTOR_PUBLICATION_NAMESPACE_CHANGED",
            f"publication parent no longer resolves to its pinned namespace: {exc}",
        )
    try:
        current = os.fstat(current_fd)
        expected = os.fstat(expected_fd)
        if (current.st_dev, current.st_ino) != (expected.st_dev, expected.st_ino):
            _fail(
                "BASS_DESCRIPTOR_PUBLICATION_NAMESPACE_CHANGED",
                "publication parent no longer names its descriptor-pinned directory",
            )
    finally:
        os.close(current_fd)


def _restore_quarantined_regular_file(
    dir_fd: int,
    name: str,
    quarantine_fd: int,
    quarantined_name: str,
    expected_device: int,
    expected_inode: int,
) -> bool:
    """Best-effort create-only restoration; never replaces a directory entry."""

    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        unrelated_fd = os.open(quarantined_name, flags, dir_fd=quarantine_fd)
    except OSError:
        return False
    try:
        observed = os.fstat(unrelated_fd)
        if not stat.S_ISREG(observed.st_mode) or (observed.st_dev, observed.st_ino) != (
            expected_device,
            expected_inode,
        ):
            return False
        try:
            os.link(
                f"/proc/self/fd/{unrelated_fd}",
                name,
                dst_dir_fd=dir_fd,
                follow_symlinks=True,
            )
        except OSError:
            return False
        os.fsync(dir_fd)
        return True
    finally:
        os.close(unrelated_fd)


def _rollback_link_safely(
    dir_fd: int,
    name: str,
    expected_device: int,
    expected_inode: int,
) -> None:
    """Quarantine one directory entry before deciding whether it may be deleted.

    The atomic rename operates in the descriptor-pinned original directory. If
    a concurrent writer replaced ``name``, that unrelated inode is moved into a
    private quarantine and never unlinked. It is restored create-only when
    possible while the quarantine hard link is retained as evidence. The
    mismatch is always a typed rollback race.
    """

    quarantine_name = f".rei-rollback-{os.getpid()}-{secrets.token_hex(16)}"
    try:
        os.mkdir(quarantine_name, 0o700, dir_fd=dir_fd)
        quarantine_fd = os.open(
            quarantine_name,
            os.O_RDONLY
            | os.O_DIRECTORY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=dir_fd,
        )
    except OSError as exc:
        _fail("BASS_EVENT_TRANSACTION_ROLLBACK_FAILED", f"cannot create quarantine: {exc}")
    quarantined_name = "entry"
    try:
        try:
            os.rename(
                name,
                quarantined_name,
                src_dir_fd=dir_fd,
                dst_dir_fd=quarantine_fd,
            )
        except FileNotFoundError:
            os.fsync(quarantine_fd)
            os.fsync(dir_fd)
            os.close(quarantine_fd)
            return
        current = os.stat(quarantined_name, dir_fd=quarantine_fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) == (expected_device, expected_inode):
            os.fsync(quarantine_fd)
            os.fsync(dir_fd)
            os.close(quarantine_fd)
            return

        restored = _restore_quarantined_regular_file(
            dir_fd,
            name,
            quarantine_fd,
            quarantined_name,
            current.st_dev,
            current.st_ino,
        )
        os.fsync(quarantine_fd)
        os.close(quarantine_fd)
        _fail(
            "BASS_EVENT_TRANSACTION_ROLLBACK_RACE",
            "destination changed before rollback; unrelated inode was not deleted"
            + (
                f"; restored create-only and retained in {quarantine_name}"
                if restored
                else f"; retained in {quarantine_name}"
            ),
        )
    except BassIntegrationError:
        raise
    except OSError as exc:
        try:
            os.close(quarantine_fd)
        except OSError:
            pass
        _fail("BASS_EVENT_TRANSACTION_ROLLBACK_FAILED", f"quarantine rollback failed: {exc}")


def publish_validated_bytes(
    destination: str | os.PathLike[str],
    payload: bytes,
    expected_sha256: str,
    *,
    validator: Callable[[bytes], object] | None = None,
    _after_descriptor_validation: Callable[[int], None] | None = None,
    _retain_directory_handle: bool = False,
) -> PublicationReceipt | _PublishedHandle:
    """Publish one immutable file from the exact validated unnamed inode.

    ``O_TMPFILE`` and ``/proc/self/fd`` are mandatory.  Platforms lacking that
    boundary receive a typed failure; no pathname-based temporary fallback is
    permitted.
    """

    if not isinstance(payload, bytes):
        _fail("BASS_DESCRIPTOR_PUBLICATION_INVALID", "payload must be bytes")
    _require_sha256(expected_sha256, "expected_sha256")
    destination_path = Path(destination)
    name = destination_path.name
    if not name or name in {".", ".."} or os.sep in name:
        _fail("BASS_DESCRIPTOR_PUBLICATION_INVALID", "destination filename is invalid")
    parent = destination_path.parent.resolve(strict=True)
    absolute_destination = parent / name
    dir_flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    dir_fd: int | None = None
    try:
        dir_fd = os.open(parent, dir_flags)
    except OSError as exc:
        _fail("BASS_DESCRIPTOR_PUBLICATION_DIRECTORY_INVALID", str(exc))
    write_fd: int | None = None
    read_fd: int | None = None
    linked = False
    staged_device = -1
    staged_inode = -1
    try:
        tmp_flag = getattr(os, "O_TMPFILE", 0)
        if not tmp_flag or not Path("/proc/self/fd").is_dir():
            _fail(
                "BASS_DESCRIPTOR_PUBLICATION_UNAVAILABLE",
                "O_TMPFILE and /proc/self/fd are required",
            )
        try:
            write_fd = os.open(".", os.O_RDWR | tmp_flag | getattr(os, "O_CLOEXEC", 0), 0o600, dir_fd=dir_fd)
        except OSError as exc:
            _fail("BASS_DESCRIPTOR_PUBLICATION_UNAVAILABLE", f"O_TMPFILE: {exc}")
        _write_all(write_fd, payload)
        os.fsync(write_fd)
        observed_digest, observed_size = _sha256_fd(write_fd)
        if observed_digest != expected_sha256 or observed_size != len(payload):
            _fail(
                "BASS_DESCRIPTOR_PUBLICATION_DIGEST_MISMATCH",
                f"expected {expected_sha256}/{len(payload)}, observed {observed_digest}/{observed_size}",
            )
        if validator is not None:
            validator(_read_fd(write_fd))
        os.fchmod(write_fd, 0o444)
        os.fsync(write_fd)

        read_fd = os.open(f"/proc/self/fd/{write_fd}", os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
        write_stat = os.fstat(write_fd)
        read_stat = _require_read_only_regular_file(read_fd, "validated descriptor")
        if (write_stat.st_dev, write_stat.st_ino) != (read_stat.st_dev, read_stat.st_ino):
            _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "read descriptor inode changed")
        os.close(write_fd)
        write_fd = None
        staged_device, staged_inode = read_stat.st_dev, read_stat.st_ino
        if _sha256_fd(read_fd) != (expected_sha256, len(payload)):
            _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "read descriptor bytes changed")
        if _after_descriptor_validation is not None:
            _after_descriptor_validation(read_fd)
        if _sha256_fd(read_fd) != (expected_sha256, len(payload)):
            _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "descriptor mutated before link")
        _require_read_only_regular_file(read_fd, "descriptor after validation callback")
        _require_publication_parent_matches_fd(parent, dir_fd)

        try:
            os.link(
                f"/proc/self/fd/{read_fd}",
                name,
                dst_dir_fd=dir_fd,
                follow_symlinks=True,
            )
        except FileExistsError:
            _fail("BASS_DESCRIPTOR_PUBLICATION_DESTINATION_EXISTS", str(absolute_destination))
        except OSError as exc:
            _fail("BASS_DESCRIPTOR_PUBLICATION_FAILED", f"descriptor hard-link failed: {exc}")
        linked = True
        try:
            os.fsync(dir_fd)
        except OSError as exc:
            linked = False
            _rollback_link_safely(dir_fd, name, staged_device, staged_inode)
            _fail("BASS_DESCRIPTOR_PUBLICATION_FAILED", f"directory fsync failed: {exc}")

        final_fd = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=dir_fd,
        )
        try:
            final_stat = os.fstat(final_fd)
            if (final_stat.st_dev, final_stat.st_ino) != (staged_device, staged_inode):
                linked = False
                _rollback_link_safely(dir_fd, name, staged_device, staged_inode)
                _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "published inode changed")
            if _sha256_fd(final_fd) != (expected_sha256, len(payload)):
                linked = False
                _rollback_link_safely(dir_fd, name, staged_device, staged_inode)
                _fail("BASS_DESCRIPTOR_PUBLICATION_INTEGRITY_FAILED", "published bytes changed")
            _require_read_only_regular_file(final_fd, "published inode")
        finally:
            os.close(final_fd)
        _require_publication_parent_matches_fd(parent, dir_fd)
        receipt = PublicationReceipt(
            str(absolute_destination),
            expected_sha256,
            len(payload),
            staged_device,
            staged_inode,
        )
        if _retain_directory_handle:
            handle = _PublishedHandle(receipt, dir_fd, name)
            dir_fd = None
            return handle
        return receipt
    except BassIntegrationError:
        if linked:
            assert dir_fd is not None
            _rollback_link_safely(dir_fd, name, staged_device, staged_inode)
        raise
    except Exception as exc:
        if linked:
            assert dir_fd is not None
            _rollback_link_safely(dir_fd, name, staged_device, staged_inode)
        _fail("BASS_DESCRIPTOR_PUBLICATION_FAILED", f"unexpected publication failure: {exc}")
    finally:
        if write_fd is not None:
            os.close(write_fd)
        if read_fd is not None:
            os.close(read_fd)
        if dir_fd is not None:
            os.close(dir_fd)


def publish_reference_graph(
    destination: str | os.PathLike[str],
    graph: ReferenceOnlyCertificateGraph,
) -> PublicationReceipt:
    payload = graph.to_bytes()
    expected = hashlib.sha256(payload).hexdigest()
    receipt = publish_validated_bytes(
        destination,
        payload,
        expected,
        validator=validate_reference_graph_bytes,
    )
    assert isinstance(receipt, PublicationReceipt)
    return receipt


@dataclass(frozen=True, slots=True)
class PublicationItem:
    destination: str
    payload: bytes
    expected_sha256: str
    validator: Callable[[bytes], object] | None = None


def publish_event_transaction(items: Sequence[PublicationItem]) -> tuple[PublicationReceipt, ...]:
    """Publish an event set with descriptor-pinned quarantine rollback.

    Filesystems do not offer a multi-name atomic commit.  This function makes
    no such claim: it validates all in-memory identities first, publishes each
    descriptor-bound item, and retains every original parent directory handle.
    On failure, published names are atomically moved into private quarantine;
    automatic rollback does not unlink an inode. A detected replacement is a
    typed rollback race and its inode is retained.
    """

    if not items:
        _fail("BASS_EVENT_TRANSACTION_INVALID", "transaction must contain at least one item")
    resolved_parents = [Path(item.destination).parent.resolve(strict=True) for item in items]
    destinations = [
        str(parent / Path(item.destination).name)
        for parent, item in zip(resolved_parents, items, strict=True)
    ]
    if len(destinations) != len(set(destinations)):
        _fail("BASS_EVENT_TRANSACTION_INVALID", "transaction destinations must be unique")
    parent_fds: dict[str, int] = {}
    handles: list[_PublishedHandle] = []
    try:
        for parent in resolved_parents:
            key = str(parent)
            if key not in parent_fds:
                try:
                    parent_fds[key] = os.open(parent, _DIRECTORY_OPEN_FLAGS)
                except OSError as exc:
                    _fail("BASS_DESCRIPTOR_PUBLICATION_DIRECTORY_INVALID", str(exc))
            _require_publication_parent_matches_fd(parent, parent_fds[key])

        for item in items:
            _require_sha256(item.expected_sha256, "transaction expected_sha256")
            observed = hashlib.sha256(item.payload).hexdigest()
            if observed != item.expected_sha256:
                _fail("BASS_EVENT_TRANSACTION_PREVALIDATION_FAILED", item.destination)
            if item.validator is not None:
                item.validator(item.payload)

        try:
            for item, parent in zip(items, resolved_parents, strict=True):
                _require_publication_parent_matches_fd(parent, parent_fds[str(parent)])
                published = publish_validated_bytes(
                    item.destination,
                    item.payload,
                    item.expected_sha256,
                    validator=item.validator,
                    _retain_directory_handle=True,
                )
                assert isinstance(published, _PublishedHandle)
                handles.append(published)
                _require_publication_parent_matches_fd(parent, parent_fds[str(parent)])
            for parent in resolved_parents:
                _require_publication_parent_matches_fd(parent, parent_fds[str(parent)])
        except BassIntegrationError as primary:
            rollback_errors: list[BassIntegrationError] = []
            for handle in reversed(handles):
                try:
                    _rollback_link_safely(
                        handle.directory_fd,
                        handle.filename,
                        handle.receipt.device,
                        handle.receipt.inode,
                    )
                except BassIntegrationError as rollback_exc:
                    rollback_errors.append(rollback_exc)
                finally:
                    handle.close()
            if rollback_errors:
                races = [
                    error
                    for error in rollback_errors
                    if error.code == "BASS_EVENT_TRANSACTION_ROLLBACK_RACE"
                ]
                if races:
                    _fail(
                        "BASS_EVENT_TRANSACTION_ROLLBACK_RACE",
                        f"primary={primary}; rollback={' | '.join(str(error) for error in rollback_errors)}",
                    )
                _fail(
                    "BASS_EVENT_TRANSACTION_ROLLBACK_FAILED",
                    f"primary={primary}; rollback={' | '.join(str(error) for error in rollback_errors)}",
                )
            raise

        receipts = tuple(handle.receipt for handle in handles)
        for handle in handles:
            handle.close()
        return receipts
    finally:
        for handle in handles:
            handle.close()
        for fd in parent_fds.values():
            os.close(fd)


__all__ = [
    "AdmittedGitAuthority",
    "AdmittedReferenceGraph",
    "BassIntegrationError",
    "BlobPin",
    "CertificateReference",
    "GitAuthorityPin",
    "GitCustodyReceipt",
    "PublicationItem",
    "PublicationReceipt",
    "ReferenceEdge",
    "ReferenceGraphWireValidation",
    "ReferenceOnlyCertificateGraph",
    "admit_reference_graph_bytes",
    "build_reference_only_graph",
    "publish_event_transaction",
    "publish_reference_graph",
    "publish_validated_bytes",
    "require_exact_bass_rec_pins",
    "validate_local_git_authority",
    "validate_reference_graph_bytes",
]
