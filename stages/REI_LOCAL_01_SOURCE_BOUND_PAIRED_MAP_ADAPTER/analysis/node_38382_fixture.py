"""Fail-closed full-field predecessor replay fixture for node 38382.

Only the final predicate is node-local.  The predecessor must replay all 46,080
nodes because the required owner normalization and reduction context are global.
The canonical fixture artifacts are not present in this repository at the
1893f12 rebuild base, so the default loader intentionally stops with a typed
missing-fixture error.
"""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass
from enum import Enum
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from types import MappingProxyType, ModuleType
from typing import Any, BinaryIO, Mapping, NoReturn, Protocol


FULL_NODE_COUNT = 46_080
TARGET_NODE = 38_382
CANONICAL_ENDPOINT_STATE_SHA256 = (
    "8f698384cbeda3182ff347d6d1a7f39724896d06454e6002628c6e95c14ec877"
)
FIXTURE_SCHEMA = "rei-node-38382-fixture/v1"
NODE_38382_FIXTURE_MISSING = "NODE_38382_FIXTURE_MISSING"
NODE_38382_VERIFIED_REPLAY_ABI_MISSING = "NODE_38382_VERIFIED_REPLAY_ABI_MISSING"
NODE_38382_FIELD_PARENT_AUTHORITY_MISSING = (
    "NODE_38382_FIELD_PARENT_AUTHORITY_MISSING"
)
_CANONICAL_SHA256 = re.compile(r"[0-9a-f]{64}").fullmatch
_CANONICAL_GIT_OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})").fullmatch
_FIELD_SOURCE_PATH = re.compile(
    r"stages/[^/]*AFFINE_SET_PARAMETERIZED_TAYLOR_MODEL_CONTINUOUS_BRANCH_ENCLOSURE_LOCK/"
    r"analysis/field_trial\.py"
).fullmatch

# Linux fcntl.h constants are not exposed by every Python build.
_F_ADD_SEALS = getattr(fcntl, "F_ADD_SEALS", 1033)
_F_GET_SEALS = getattr(fcntl, "F_GET_SEALS", 1034)
_F_SEAL_SEAL = getattr(fcntl, "F_SEAL_SEAL", 0x0001)
_F_SEAL_SHRINK = getattr(fcntl, "F_SEAL_SHRINK", 0x0002)
_F_SEAL_GROW = getattr(fcntl, "F_SEAL_GROW", 0x0004)
_F_SEAL_WRITE = getattr(fcntl, "F_SEAL_WRITE", 0x0008)
_F_SEAL_FUTURE_WRITE = getattr(fcntl, "F_SEAL_FUTURE_WRITE", 0x0010)
_REQUIRED_CONTENT_SEALS = _F_SEAL_WRITE | _F_SEAL_GROW | _F_SEAL_SHRINK


class Node38382FixtureError(RuntimeError):
    """Fixture/replay failure carrying a stable machine-readable code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        suffix = f": {detail}" if detail else ""
        super().__init__(f"{code}{suffix}")


class FixtureRole(str, Enum):
    ENDPOINT = "endpoint"
    FULL_FIELD_CONTEXT = "full_field_context"
    FOUR_SITE_OWNER_CONTEXT = "four_site_owner_context"
    REDUCTION_SIDECAR = "reduction_sidecar"


def _require_sha256(value: object, code: str) -> str:
    if not isinstance(value, str) or _CANONICAL_SHA256(value) is None:
        raise Node38382FixtureError(code, "expected canonical lowercase SHA-256")
    return value


@dataclass(frozen=True)
class FieldSourceAuthority:
    """External byte and Git-blob pin for canonical ``field_trial.py``."""

    relative_path: str
    sha256: str
    git_blob_oid: str

    def __post_init__(self) -> None:
        if not isinstance(self.relative_path, str) or not self.relative_path:
            raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")
        path = PurePosixPath(self.relative_path)
        if path.is_absolute() or ".." in path.parts or str(path) != self.relative_path:
            raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")
        _require_sha256(self.sha256, "NODE_38382_FIELD_AUTHORITY_INVALID")
        if (
            not isinstance(self.git_blob_oid, str)
            or _CANONICAL_GIT_OID(self.git_blob_oid) is None
        ):
            raise Node38382FixtureError(
                "NODE_38382_FIELD_AUTHORITY_INVALID",
                "git_blob_oid must be a full lowercase SHA-1 or SHA-256 object ID",
            )


@dataclass(frozen=True)
class Node38382Authority:
    """Digests supplied externally to the fixture manifest."""

    authority_id: str
    endpoint_state_sha256: str
    artifact_sha256: Mapping[FixtureRole, str]
    field_source: FieldSourceAuthority

    def __post_init__(self) -> None:
        if not isinstance(self.authority_id, str) or not self.authority_id.strip():
            raise Node38382FixtureError("NODE_38382_FIXTURE_AUTHORITY_INVALID")
        endpoint = _require_sha256(
            self.endpoint_state_sha256, "NODE_38382_FIXTURE_AUTHORITY_INVALID"
        )
        if endpoint != CANONICAL_ENDPOINT_STATE_SHA256:
            raise Node38382FixtureError(
                "NODE_38382_FIXTURE_AUTHORITY_INVALID",
                "endpoint state identity is not the pinned predecessor authority",
            )
        try:
            normalized = {
                FixtureRole(role): _require_sha256(
                    digest, "NODE_38382_FIXTURE_AUTHORITY_INVALID"
                )
                for role, digest in self.artifact_sha256.items()
            }
        except (AttributeError, TypeError, ValueError) as exc:
            raise Node38382FixtureError("NODE_38382_FIXTURE_AUTHORITY_INVALID") from exc
        if set(normalized) != set(FixtureRole):
            raise Node38382FixtureError(
                "NODE_38382_FIXTURE_AUTHORITY_INVALID",
                "external pin must cover every required artifact role",
            )
        object.__setattr__(self, "artifact_sha256", MappingProxyType(normalized))
        if not isinstance(self.field_source, FieldSourceAuthority):
            raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")


@dataclass(frozen=True)
class ArtifactSnapshotReceipt:
    """Identity of the sealed descriptor consumed by predecessor replay."""

    role: FixtureRole
    sha256: str
    size_bytes: int
    device: int
    inode: int
    seals: int


@dataclass(frozen=True)
class FullFieldReplayResult:
    node_count: int
    endpoint_state_sha256: str
    hard_gates_pass: bool
    opaque: Any


class PredecessorReplay(Protocol):
    def replay(self, **kwargs: object) -> FullFieldReplayResult: ...

    def predicate_node(
        self, replay_result: FullFieldReplayResult, *, node_index: int
    ) -> Mapping[str, object]: ...


@dataclass(frozen=True)
class Node38382PredicateResult:
    replayed_node_count: int
    target_node: int
    predicate: Mapping[str, object]


@dataclass(frozen=True)
class Node38382Fixture:
    repo_root: Path
    fixture_root: Path
    authority: Node38382Authority
    trial_class: type
    artifact_paths: Mapping[FixtureRole, Path]

    def replay_and_predicate(
        self, predecessor: object | None = None
    ) -> NoReturn:
        """Reject self-attested replay until an independent verifier ABI exists."""

        del predecessor
        raise Node38382FixtureError(
            NODE_38382_VERIFIED_REPLAY_ABI_MISSING,
            "node count, endpoint identity, hard gates, and predicate require "
            "independent derivation from sealed inputs and calculation results",
        )


@dataclass(frozen=True)
class _TestOnlyNode38382Fixture(Node38382Fixture):
    """Synthetic test harness; it can never discharge a production gate."""

    def replay_and_predicate_for_test(
        self, predecessor: PredecessorReplay
    ) -> Node38382PredicateResult:
        """Exercise snapshot plumbing with deliberately non-authoritative fakes."""

        replay = getattr(predecessor, "replay", None)
        predicate_node = getattr(predecessor, "predicate_node", None)
        if not callable(replay) or not callable(predicate_node):
            raise Node38382FixtureError(
                "NODE_38382_PREDECESSOR_INTERFACE_INVALID",
                "replay and predicate_node methods are required",
            )
        with ExitStack() as stack:
            streams: dict[FixtureRole, BinaryIO] = {}
            receipts: dict[FixtureRole, ArtifactSnapshotReceipt] = {}
            for role, path in self.artifact_paths.items():
                stream, receipt = _sealed_artifact_snapshot(
                    role=role,
                    path=path,
                    expected_sha256=self.authority.artifact_sha256[role],
                )
                stream = stack.enter_context(stream)
                streams[role] = stream
                receipts[role] = receipt
            for role in FixtureRole:
                _verify_snapshot(streams[role], receipts[role])
            result = replay(
                repo_root=self.repo_root,
                trial_class=self.trial_class,
                artifact_streams=MappingProxyType(streams),
                artifact_receipts=MappingProxyType(receipts),
                node_count=FULL_NODE_COUNT,
            )
            for role in FixtureRole:
                _verify_snapshot(streams[role], receipts[role])
            if not isinstance(result, FullFieldReplayResult):
                raise Node38382FixtureError("NODE_38382_PREDECESSOR_INTERFACE_INVALID")
            if isinstance(result.node_count, bool) or result.node_count != FULL_NODE_COUNT:
                raise Node38382FixtureError(
                    "NODE_38382_PREDECESSOR_REPLAY_INCOMPLETE",
                    "one-node slices cannot recover global owner normalization",
                )
            if result.hard_gates_pass is not True:
                raise Node38382FixtureError("NODE_38382_PREDECESSOR_HARD_GATE_FAILED")
            digest = _require_sha256(
                result.endpoint_state_sha256, "NODE_38382_ENDPOINT_AUTHORITY_MISMATCH"
            )
            if digest != self.authority.endpoint_state_sha256:
                raise Node38382FixtureError("NODE_38382_ENDPOINT_AUTHORITY_MISMATCH")
            predicate = predicate_node(result, node_index=TARGET_NODE)
            if not isinstance(predicate, Mapping):
                raise Node38382FixtureError("NODE_38382_PREDICATE_RESULT_INVALID")
            return Node38382PredicateResult(
                replayed_node_count=FULL_NODE_COUNT,
                target_node=TARGET_NODE,
                predicate=MappingProxyType(dict(predicate)),
            )


def _git_blob_oid(data: bytes, *, oid_length: int) -> str:
    payload = f"blob {len(data)}\0".encode("ascii") + data
    if oid_length == 40:
        return hashlib.sha1(payload).hexdigest()
    if oid_length == 64:
        return hashlib.sha256(payload).hexdigest()
    raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")


def _head_blob_oid(repo_root: Path, relative_path: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", f"HEAD:{relative_path}"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise Node38382FixtureError(
            "NODE_38382_FIELD_AUTHORITY_INVALID",
            "field source is not an exact blob in the current HEAD",
        )
    try:
        return completed.stdout.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID") from exc


def _validate_field_source(
    repo_root: Path, authority: FieldSourceAuthority
) -> None:
    if _FIELD_SOURCE_PATH(authority.relative_path) is None:
        raise Node38382FixtureError(
            "NODE_38382_FIELD_AUTHORITY_INVALID",
            "field source path is outside the canonical predecessor stage grammar",
        )
    lexical = repo_root / PurePosixPath(authority.relative_path)
    path = lexical.resolve()
    if (
        path != lexical.absolute()
        or repo_root not in path.parents
        or not path.is_file()
    ):
        raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")
    with _open_artifact_no_follow(path) as stream:
        source = stream.read()
    observed_sha256 = hashlib.sha256(source).hexdigest()
    observed_blob = _git_blob_oid(source, oid_length=len(authority.git_blob_oid))
    if (
        observed_sha256 != authority.sha256
        or observed_blob != authority.git_blob_oid
        or _head_blob_oid(repo_root, authority.relative_path) != authority.git_blob_oid
    ):
        raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_MISMATCH")


def _safe_artifact_path(root: Path, raw: object) -> Path:
    if not isinstance(raw, str) or not raw:
        raise Node38382FixtureError("NODE_38382_FIXTURE_PATH_INVALID")
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise Node38382FixtureError("NODE_38382_FIXTURE_PATH_INVALID")
    candidate = (root / relative).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise Node38382FixtureError("NODE_38382_FIXTURE_PATH_INVALID")
    return candidate


def _open_artifact_no_follow(path: Path) -> BinaryIO:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise Node38382FixtureError(
            "NODE_38382_FIXTURE_OPEN_FAILED", str(path)
        ) from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise Node38382FixtureError(
                "NODE_38382_FIXTURE_OPEN_FAILED", "artifact is not a regular file"
            )
        return os.fdopen(descriptor, "rb", closefd=True)
    except Node38382FixtureError:
        os.close(descriptor)
        raise
    except OSError as exc:
        os.close(descriptor)
        raise Node38382FixtureError("NODE_38382_FIXTURE_OPEN_FAILED", str(path)) from exc
    except BaseException:
        os.close(descriptor)
        raise


def _sha256_stream(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    stream.seek(0)
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def _sha256_file(path: Path) -> str:
    with _open_artifact_no_follow(path) as stream:
        return _sha256_stream(stream)


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_FAILED")
        view = view[written:]


def _sha256_descriptor(descriptor: int) -> str:
    digest = hashlib.sha256()
    size = os.fstat(descriptor).st_size
    offset = 0
    while offset < size:
        chunk = os.pread(descriptor, min(1024 * 1024, size - offset), offset)
        if not chunk:
            raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_FAILED")
        digest.update(chunk)
        offset += len(chunk)
    return digest.hexdigest()


def _sealed_artifact_snapshot(
    *, role: FixtureRole, path: Path, expected_sha256: str
) -> tuple[BinaryIO, ArtifactSnapshotReceipt]:
    memfd_create = getattr(os, "memfd_create", None)
    allow_sealing = getattr(os, "MFD_ALLOW_SEALING", None)
    if not callable(memfd_create) or allow_sealing is None:
        raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_UNAVAILABLE")
    flags = int(allow_sealing) | int(getattr(os, "MFD_CLOEXEC", 0))
    try:
        descriptor = memfd_create(f"rei-node-38382-{role.value}", flags)
    except OSError as exc:
        raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_UNAVAILABLE") from exc
    try:
        with _open_artifact_no_follow(path) as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                _write_all(descriptor, chunk)
        fcntl.fcntl(descriptor, _F_ADD_SEALS, _REQUIRED_CONTENT_SEALS)
        seals = _REQUIRED_CONTENT_SEALS
        try:
            fcntl.fcntl(descriptor, _F_ADD_SEALS, _F_SEAL_FUTURE_WRITE)
            seals |= _F_SEAL_FUTURE_WRITE
        except OSError as exc:
            if exc.errno not in (errno.EINVAL, getattr(errno, "ENOTSUP", errno.EINVAL)):
                raise
        fcntl.fcntl(descriptor, _F_ADD_SEALS, _F_SEAL_SEAL)
        seals |= _F_SEAL_SEAL
        observed_seals = int(fcntl.fcntl(descriptor, _F_GET_SEALS))
        if observed_seals & seals != seals:
            raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_FAILED")
        metadata = os.fstat(descriptor)
        observed_sha256 = _sha256_descriptor(descriptor)
        if observed_sha256 != expected_sha256:
            raise Node38382FixtureError(
                "NODE_38382_FIXTURE_DIGEST_MISMATCH", role.value
            )
        os.lseek(descriptor, 0, os.SEEK_SET)
        stream = os.fdopen(descriptor, "rb", closefd=True)
        receipt = ArtifactSnapshotReceipt(
            role=role,
            sha256=observed_sha256,
            size_bytes=metadata.st_size,
            device=metadata.st_dev,
            inode=metadata.st_ino,
            seals=observed_seals,
        )
        return stream, receipt
    except Node38382FixtureError:
        os.close(descriptor)
        raise
    except OSError as exc:
        os.close(descriptor)
        raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_FAILED") from exc
    except BaseException:
        os.close(descriptor)
        raise


def _verify_snapshot(stream: BinaryIO, receipt: ArtifactSnapshotReceipt) -> None:
    try:
        descriptor = stream.fileno()
        metadata = os.fstat(descriptor)
        seals = int(fcntl.fcntl(descriptor, _F_GET_SEALS))
        observed_sha256 = _sha256_descriptor(descriptor)
    except (OSError, ValueError) as exc:
        raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_INVALID") from exc
    if (
        metadata.st_dev != receipt.device
        or metadata.st_ino != receipt.inode
        or metadata.st_size != receipt.size_bytes
        or observed_sha256 != receipt.sha256
        or seals != receipt.seals
        or seals & (_REQUIRED_CONTENT_SEALS | _F_SEAL_SEAL)
        != (_REQUIRED_CONTENT_SEALS | _F_SEAL_SEAL)
    ):
        raise Node38382FixtureError("NODE_38382_SEALED_SNAPSHOT_INVALID")


def _load_node_38382_fixture(
    *,
    repo_root: Path,
    fixture_root: Path,
    authority: Node38382Authority | None,
    field_module: ModuleType | object,
) -> Node38382Fixture:
    """Shared validated loader after the field-source boundary is resolved."""

    repo = Path(repo_root).resolve()
    root = Path(fixture_root).resolve()
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.is_file():
        raise Node38382FixtureError(
            NODE_38382_FIXTURE_MISSING,
            "canonical endpoint/context fixture has not been materialized",
        )
    if not isinstance(authority, Node38382Authority):
        raise Node38382FixtureError("NODE_38382_FIXTURE_AUTHORITY_REQUIRED")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Node38382FixtureError("NODE_38382_FIXTURE_MANIFEST_INVALID") from exc
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema",
        "node_count",
        "target_node",
        "endpoint_state_sha256",
        "artifacts",
    }:
        raise Node38382FixtureError("NODE_38382_FIXTURE_MANIFEST_INVALID")
    if manifest["schema"] != FIXTURE_SCHEMA:
        raise Node38382FixtureError("NODE_38382_FIXTURE_SCHEMA_INVALID")
    if (
        isinstance(manifest["node_count"], bool)
        or manifest["node_count"] != FULL_NODE_COUNT
        or isinstance(manifest["target_node"], bool)
        or manifest["target_node"] != TARGET_NODE
    ):
        raise Node38382FixtureError("NODE_38382_FIXTURE_DOMAIN_INVALID")
    if manifest["endpoint_state_sha256"] != authority.endpoint_state_sha256:
        raise Node38382FixtureError("NODE_38382_FIXTURE_AUTHORITY_MISMATCH")
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != {
        role.value for role in FixtureRole
    }:
        raise Node38382FixtureError("NODE_38382_FIXTURE_ROLE_SET_INVALID")
    paths: dict[FixtureRole, Path] = {}
    for role in FixtureRole:
        record = artifacts[role.value]
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise Node38382FixtureError("NODE_38382_FIXTURE_MANIFEST_INVALID")
        declared = _require_sha256(
            record["sha256"], "NODE_38382_FIXTURE_MANIFEST_INVALID"
        )
        if declared != authority.artifact_sha256[role]:
            raise Node38382FixtureError("NODE_38382_FIXTURE_AUTHORITY_MISMATCH")
        path = _safe_artifact_path(root, record["path"])
        observed = _sha256_file(path)
        if observed != declared:
            raise Node38382FixtureError(
                "NODE_38382_FIXTURE_DIGEST_MISMATCH", role.value
            )
        paths[role] = path
    factory = getattr(field_module, "make_trial_class", None)
    if not callable(factory):
        raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")
    dynamic_parent = factory(repo)  # binding rule: call field.make_trial_class(repo) exactly once
    if not isinstance(dynamic_parent, type):
        raise Node38382FixtureError("NODE_38382_FIELD_AUTHORITY_INVALID")

    class Node38382ReplayTrial(dynamic_parent):
        """Identity subclass preserving the complete predecessor solve interface."""

    return _TestOnlyNode38382Fixture(
        repo_root=repo,
        fixture_root=root,
        authority=authority,
        trial_class=Node38382ReplayTrial,
        artifact_paths=MappingProxyType(paths),
    )


def load_node_38382_fixture(
    *,
    repo_root: Path,
    fixture_root: Path,
    authority: Node38382Authority | None,
) -> Node38382Fixture:
    """Production loader requiring exact external field-source SHA/blob pins."""

    repo = Path(repo_root).resolve()
    root = Path(fixture_root).resolve()
    if not (root / "MANIFEST.json").is_file():
        raise Node38382FixtureError(
            NODE_38382_FIXTURE_MISSING,
            "canonical endpoint/context fixture has not been materialized",
        )
    if not isinstance(authority, Node38382Authority):
        raise Node38382FixtureError("NODE_38382_FIXTURE_AUTHORITY_REQUIRED")
    _validate_field_source(repo, authority.field_source)
    raise Node38382FixtureError(
        NODE_38382_FIELD_PARENT_AUTHORITY_MISSING,
        "field_trial.py parents use unpinned sys.modules/next(glob); exact parent "
        "source pins and an isolated loader are required before class construction",
    )


def load_node_38382_fixture_for_test(
    *,
    repo_root: Path,
    fixture_root: Path,
    authority: Node38382Authority | None,
    field_module: ModuleType | object,
) -> Node38382Fixture:
    """Explicit test-only injection seam; inadmissible for production claims."""

    return _load_node_38382_fixture(
        repo_root=repo_root,
        fixture_root=fixture_root,
        authority=authority,
        field_module=field_module,
    )


def load_canonical_node_38382_fixture(
    *, repo_root: Path, authority: Node38382Authority
) -> Node38382Fixture:
    root = (
        Path(repo_root).resolve()
        / "stages"
        / "REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
        / "fixtures"
        / "node_38382"
    )
    return load_node_38382_fixture(
        repo_root=repo_root, fixture_root=root, authority=authority
    )


build_node_38382_fixture = load_node_38382_fixture


__all__ = [
    "CANONICAL_ENDPOINT_STATE_SHA256",
    "FIXTURE_SCHEMA",
    "FULL_NODE_COUNT",
    "ArtifactSnapshotReceipt",
    "FieldSourceAuthority",
    "FixtureRole",
    "FullFieldReplayResult",
    "NODE_38382_FIXTURE_MISSING",
    "NODE_38382_FIELD_PARENT_AUTHORITY_MISSING",
    "NODE_38382_VERIFIED_REPLAY_ABI_MISSING",
    "Node38382Authority",
    "Node38382Fixture",
    "Node38382FixtureError",
    "Node38382PredicateResult",
    "PredecessorReplay",
    "TARGET_NODE",
    "build_node_38382_fixture",
    "load_canonical_node_38382_fixture",
    "load_node_38382_fixture",
    "load_node_38382_fixture_for_test",
]
