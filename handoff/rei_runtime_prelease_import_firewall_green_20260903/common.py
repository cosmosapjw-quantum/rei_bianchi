#!/usr/bin/env python3
"""Shared fail-closed primitives for the REI pre-lease import firewall.

This module may inspect bytes, JSON and Git state.  It never imports the
production bridge.  The first operation allowed to enter that module lives in
the post-lease worker.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
from typing import Any, Mapping, Sequence
import urllib.error
import urllib.request


PACKAGE = Path(__file__).resolve().parent
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
PACKAGE_INDEX_PATH = PACKAGE / "PACKAGE_INDEX.json"
GIT = Path("/usr/bin/git")
PINNED_GIT_SHA256 = "2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668"


class FirewallError(RuntimeError):
    """Typed fail-closed error for the successor firewall."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _valid_hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_repo_file(repo: Path, relative: str, classification: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        raise FirewallError(classification)
    root = Path(repo).resolve(strict=True)
    candidate = root / relative
    if candidate.is_symlink():
        raise FirewallError(classification)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise FirewallError(classification) from exc
    if not resolved.is_file():
        raise FirewallError(classification)
    return resolved


def load_json_file(path: Path, classification: str) -> dict[str, Any]:
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise FirewallError(classification)
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FirewallError(classification) from exc
    if not isinstance(value, dict):
        raise FirewallError(classification)
    return value


def write_o_excl(path: Path, value: Mapping[str, Any]) -> Path:
    target = Path(path)
    if not target.is_absolute():
        raise FirewallError("CREATE_ONLY_PATH_NOT_ABSOLUTE")
    try:
        parent = target.parent.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FirewallError("CREATE_ONLY_PARENT_UNAVAILABLE") from exc
    resolved = parent / target.name
    if resolved.is_symlink():
        raise FirewallError("CREATE_ONLY_SYMLINK_FORBIDDEN")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(resolved, flags, 0o600)
    except FileExistsError as exc:
        raise FirewallError("CREATE_ONLY_PATH_ALREADY_EXISTS") from exc
    except OSError as exc:
        raise FirewallError("CREATE_ONLY_PATH_UNAVAILABLE") from exc
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(canonical_bytes(dict(value)) + b"\n")
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            resolved.unlink()
        except OSError:
            pass
        raise
    return resolved.resolve(strict=True)


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = load_json_file(path, "FIREWALL_CONTRACT_UNREADABLE")
    required = {
        "schema",
        "classification",
        "repository",
        "immutable_parent",
        "source_lineage",
        "successor_section0",
        "attempt_budget",
        "execution_context",
        "required_operations",
        "forbidden_operations",
        "claim_ceiling",
        "success_status",
        "failure_status",
    }
    if (
        set(value) != required
        or value.get("schema") != "rei-runtime-prelease-import-firewall/v1"
        or value.get("repository") != "cosmosapjw-quantum/rei_bianchi"
        or value.get("success_status") != "PASS_PRELEASE_IMPORT_FIREWALL_SOURCE"
        or value.get("failure_status") != "STOP_INVALID"
    ):
        raise FirewallError("FIREWALL_CONTRACT_SCHEMA_INVALID")
    budget = value.get("attempt_budget")
    if (
        not isinstance(budget, dict)
        or budget.get("ordinal") != 3
        or budget.get("prior_attempts") != 2
        or budget.get("remaining_native_attempts") != 1
        or budget.get("retries_after_outcome") != 0
        or budget.get("global_lease_target_relation")
        != "EXACT_FIREWALL_RELEASE_HEAD"
    ):
        raise FirewallError("FIREWALL_ATTEMPT_BUDGET_INVALID")
    return value


def verify_package_index(
    root: Path = PACKAGE,
    index_path: Path = PACKAGE_INDEX_PATH,
) -> None:
    index = load_json_file(index_path, "FIREWALL_PACKAGE_INDEX_UNREADABLE")
    if (
        set(index) != {"schema", "git_object_format", "entries"}
        or index.get("schema")
        != "rei-runtime-prelease-import-firewall-package-index/v1"
        or index.get("git_object_format") != "sha1"
        or not isinstance(index.get("entries"), list)
    ):
        raise FirewallError("FIREWALL_PACKAGE_INDEX_INVALID")

    expected: dict[Path, str] = {}
    for row in index["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            raise FirewallError("FIREWALL_PACKAGE_INDEX_INVALID")
        raw = row.get("path")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        blob = row.get("blob_sha")
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw
            or not _valid_hex(blob, 40)
        ):
            raise FirewallError("FIREWALL_PACKAGE_INDEX_INVALID")
        relative = Path(raw)
        if relative in expected or relative == Path(index_path.name):
            raise FirewallError("FIREWALL_PACKAGE_INDEX_INVALID")
        expected[relative] = blob

    package_root = Path(root).resolve(strict=True)
    index_resolved = Path(index_path).resolve(strict=True)
    actual: set[Path] = set()
    for candidate in package_root.rglob("*"):
        if candidate.is_symlink():
            raise FirewallError("FIREWALL_PACKAGE_SCOPE_MISMATCH")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(package_root)
        if "__pycache__" in relative.parts or candidate.suffix == ".pyc":
            continue
        if candidate.resolve(strict=True) != index_resolved:
            actual.add(relative)
    if set(expected) != actual:
        raise FirewallError(
            "FIREWALL_PACKAGE_SCOPE_MISMATCH:"
            f"missing={sorted(str(item) for item in set(expected)-actual)}:"
            f"extra={sorted(str(item) for item in actual-set(expected))}"
        )
    for relative, expected_blob in expected.items():
        target = package_root / relative
        if not target.is_file() or git_blob_sha1(target) != expected_blob:
            raise FirewallError(
                f"FIREWALL_PACKAGE_BLOB_MISMATCH:{relative.as_posix()}"
            )


def _preauthenticate_git() -> Path:
    try:
        resolved = GIT.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FirewallError("PINNED_GIT_UNAVAILABLE") from exc
    if not resolved.is_file() or sha256_file(resolved) != PINNED_GIT_SHA256:
        raise FirewallError("PINNED_GIT_IDENTITY_MISMATCH")
    return resolved


def git_text(repo: Path, *arguments: str) -> str:
    git = _preauthenticate_git()
    completed = subprocess.run(
        [str(git), "-C", str(Path(repo).resolve(strict=True)), *arguments],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise FirewallError(
            f"STATIC_GIT_COMMAND_FAILED:{arguments[0]}:{detail}"
        )
    return completed.stdout.strip()


def _resolve_git_report_path(repo: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = Path(repo) / candidate
    try:
        return candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise FirewallError("STANDALONE_CLONE_REQUIRED") from exc


def verify_standalone_repository_context(repo: Path) -> tuple[Path, ...]:
    root = Path(repo)
    if root.is_symlink():
        raise FirewallError("STANDALONE_CLONE_REQUIRED")
    root = root.resolve(strict=True)
    dot_git = root / ".git"
    if dot_git.is_symlink() or not dot_git.is_dir():
        raise FirewallError("STANDALONE_CLONE_REQUIRED")
    expected_git_dir = dot_git.resolve(strict=True)
    git_dir = _resolve_git_report_path(
        root, git_text(root, "rev-parse", "--absolute-git-dir")
    )
    common_dir = _resolve_git_report_path(
        root, git_text(root, "rev-parse", "--git-common-dir")
    )
    if git_dir != expected_git_dir or common_dir != expected_git_dir:
        raise FirewallError("STANDALONE_CLONE_REQUIRED")
    alternates = expected_git_dir / "objects/info/alternates"
    if alternates.is_symlink() or alternates.exists():
        raise FirewallError("REPOSITORY_ALTERNATES_FORBIDDEN")
    if git_text(root, "rev-parse", "--is-shallow-repository") != "false":
        raise FirewallError("SHALLOW_REPOSITORY_FORBIDDEN")

    report = git_text(root, "worktree", "list", "--porcelain")
    records = [record.splitlines() for record in report.split("\n\n") if record]
    if len(records) != 1:
        raise FirewallError("STANDALONE_CLONE_REQUIRED")
    record = records[0]
    if any(line == "bare" or line.startswith("prunable") for line in record):
        raise FirewallError("STANDALONE_CLONE_REQUIRED")
    roots = [
        line.removeprefix("worktree ")
        for line in record
        if line.startswith("worktree ")
    ]
    if len(roots) != 1 or _resolve_git_report_path(root, roots[0]) != root:
        raise FirewallError("STANDALONE_CLONE_REQUIRED")
    return (root,)


def verify_repo_package_index(
    repo: Path,
    *,
    package_path: str,
    index_blob_sha1: str,
) -> None:
    root = Path(repo).resolve(strict=True)
    index_relative = f"{package_path}/PACKAGE_INDEX.json"
    if git_text(root, "rev-parse", f"HEAD:{index_relative}") != index_blob_sha1:
        raise FirewallError("PINNED_RUNTIME_PACKAGE_INDEX_MISMATCH")
    index = load_json_file(
        _resolve_repo_file(root, index_relative, "PINNED_RUNTIME_PACKAGE_UNAVAILABLE"),
        "PINNED_RUNTIME_PACKAGE_INDEX_UNREADABLE",
    )
    entries = index.get("entries")
    if not isinstance(entries, list):
        raise FirewallError("PINNED_RUNTIME_PACKAGE_INDEX_INVALID")
    expected_names = {"PACKAGE_INDEX.json"}
    for row in entries:
        if not isinstance(row, dict):
            raise FirewallError("PINNED_RUNTIME_PACKAGE_INDEX_INVALID")
        raw = row.get("path")
        blob = row.get("blob_sha")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw
            or not _valid_hex(blob, 40)
        ):
            raise FirewallError("PINNED_RUNTIME_PACKAGE_INDEX_INVALID")
        relative = f"{package_path}/{raw}"
        if git_text(root, "rev-parse", f"HEAD:{relative}") != blob:
            raise FirewallError(f"PINNED_RUNTIME_PACKAGE_BLOB_MISMATCH:{raw}")
        expected_names.add(raw)
    actual = {
        line.removeprefix(package_path + "/")
        for line in git_text(
            root, "ls-tree", "-r", "--name-only", "HEAD", package_path
        ).splitlines()
        if line
    }
    if actual != expected_names:
        raise FirewallError("PINNED_RUNTIME_PACKAGE_SCOPE_MISMATCH")


def verify_static_release(
    repo: Path,
    contract: Mapping[str, Any],
    *,
    expected_head: str,
    expected_tree: str,
) -> tuple[str, str]:
    if not _valid_hex(expected_head, 40) or not _valid_hex(expected_tree, 40):
        raise FirewallError("EXPECTED_RELEASE_IDENTITY_INVALID")
    root = Path(repo).resolve(strict=True)
    verify_standalone_repository_context(root)
    head = git_text(root, "rev-parse", "HEAD")
    tree = git_text(root, "rev-parse", "HEAD^{tree}")
    if head != expected_head:
        raise FirewallError("FIREWALL_RELEASE_HEAD_MISMATCH")
    if tree != expected_tree:
        raise FirewallError("FIREWALL_RELEASE_TREE_MISMATCH")

    parent = contract["immutable_parent"]
    if git_text(root, "merge-base", "HEAD", parent["commit"]) != parent["commit"]:
        raise FirewallError("IMMUTABLE_PARENT_NOT_ANCESTOR")
    if git_text(root, "rev-parse", f'{parent["commit"]}^{{tree}}') != parent["tree"]:
        raise FirewallError("IMMUTABLE_PARENT_TREE_MISMATCH")

    lineage = contract["source_lineage"]
    runtime_package = lineage["runtime_package"]
    verify_repo_package_index(
        root,
        package_path=runtime_package["path"],
        index_blob_sha1=runtime_package["package_index_blob_sha1"],
    )
    for predecessor in lineage["required_ancestors"]:
        if git_text(root, "merge-base", "HEAD", predecessor["commit"]) != predecessor["commit"]:
            raise FirewallError(
                f'REQUIRED_ANCESTOR_MISSING:{predecessor["role"]}'
            )
        if git_text(root, "rev-parse", f'{predecessor["commit"]}^{{tree}}') != predecessor["tree"]:
            raise FirewallError(
                f'REQUIRED_ANCESTOR_TREE_MISMATCH:{predecessor["role"]}'
            )
    for record in lineage["static_files"]:
        path = _resolve_repo_file(root, record["path"], "SOURCE_INPUT_UNAVAILABLE")
        expected_blob = record.get("blob_sha1")
        expected_sha = record.get("sha256")
        if expected_blob is not None and git_text(
            root, "rev-parse", f'HEAD:{record["path"]}'
        ) != expected_blob:
            raise FirewallError(f'SOURCE_BLOB_MISMATCH:{record["path"]}')
        if expected_sha is not None and sha256_file(path) != expected_sha:
            raise FirewallError(f'SOURCE_SHA256_MISMATCH:{record["path"]}')

    git_text(root, "fsck", "--full")
    git_text(root, "diff", "--check")
    if git_text(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise FirewallError("FIREWALL_RELEASE_WORKTREE_NOT_CLEAN")
    return head, tree


def inspect_attempt_state(root: Path) -> list[str]:
    candidate = Path(root).resolve(strict=True)
    return sorted(
        path.relative_to(candidate).as_posix()
        for path in candidate.rglob("*")
        if path.is_file() or path.is_symlink()
    )


def validate_attempt_state_root(path: Path, *, repo: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise FirewallError("ATTEMPT_STATE_ROOT_UNAVAILABLE")
    resolved = candidate.resolve(strict=False)
    tmp = Path("/tmp").resolve(strict=True)
    repository = Path(repo).resolve(strict=True)
    if _is_under(resolved, tmp) or _is_under(resolved, repository):
        raise FirewallError("ATTEMPT_STATE_ROOT_FORBIDDEN")
    if not resolved.is_dir() or resolved.is_symlink():
        raise FirewallError("ATTEMPT_STATE_ROOT_UNAVAILABLE")
    if inspect_attempt_state(resolved):
        raise FirewallError("ATTEMPT_STATE_ALREADY_PRESENT")
    return resolved.resolve(strict=True)


def validate_new_output_root(
    path: Path,
    *,
    repo: Path,
    state_root: Path,
) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise FirewallError("OUTPUT_ROOT_INVALID")
    resolved = candidate.resolve(strict=False)
    tmp = Path("/tmp").resolve(strict=True)
    repository = Path(repo).resolve(strict=True)
    state = Path(state_root).resolve(strict=True)
    if (
        _is_under(resolved, tmp)
        or _is_under(resolved, repository)
        or _is_under(resolved, state)
        or _is_under(state, resolved)
    ):
        raise FirewallError("OUTPUT_ROOT_FORBIDDEN")
    if resolved.exists() or resolved.is_symlink():
        raise FirewallError("OUTPUT_ROOT_PREEXISTS")
    try:
        resolved.mkdir(mode=0o700, parents=False)
    except OSError as exc:
        raise FirewallError("OUTPUT_ROOT_UNAVAILABLE") from exc
    return resolved.resolve(strict=True)


def validate_successor_receipt(
    path: Path,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    receipt = load_json_file(path, "SUCCESSOR_SECTION0_UNREADABLE")
    rule = contract["successor_section0"]
    if receipt.get("schema") != rule["required_schema"]:
        raise FirewallError("SUCCESSOR_SECTION0_SCHEMA_MISMATCH")
    if receipt.get("status") != rule["required_status"]:
        raise FirewallError("SUCCESSOR_SECTION0_STATUS_MISMATCH")
    if (
        receipt.get("semantic_toolchain_lock_sha256")
        != rule["semantic_toolchain_lock_sha256"]
    ):
        raise FirewallError("SUCCESSOR_SECTION0_LOCK_MISMATCH")
    if receipt.get("observed_toolchain") != rule["semantic_toolchain_lock"]:
        raise FirewallError("SUCCESSOR_SECTION0_FIELD_MISMATCH")
    if sha256_file(path) == rule["historical_receipt_sha256"]:
        raise FirewallError("HISTORICAL_SECTION0_RECEIPT_REUSE_FORBIDDEN")
    return receipt


def validate_preflight_receipt(
    path: Path,
    *,
    expected_head: str,
    expected_tree: str,
    successor_receipt_sha256: str,
) -> dict[str, Any]:
    receipt = load_json_file(path, "READ_ONLY_PREFLIGHT_RECEIPT_UNREADABLE")
    if (
        receipt.get("schema")
        != "rei-runtime-prelease-import-firewall-preflight-receipt/v1"
        or receipt.get("status") != "PASS_READ_ONLY_STATIC_PREFLIGHT"
        or receipt.get("firewall_release")
        != {"commit": expected_head, "tree": expected_tree}
        or receipt.get("successor_section0_receipt_sha256")
        != successor_receipt_sha256
    ):
        raise FirewallError("READ_ONLY_PREFLIGHT_RECEIPT_MISMATCH")
    observations = receipt.get("global_ref_observations")
    if not isinstance(observations, list) or len(observations) != 2:
        raise FirewallError("READ_ONLY_PREFLIGHT_REF_OBSERVATIONS_INVALID")
    for observation in observations:
        if (
            not isinstance(observation, dict)
            or observation.get("status")
            != "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED"
            or observation.get("authorization_effect") != "NONE"
            or observation.get("global_lease_acquired") is not False
        ):
            raise FirewallError("READ_ONLY_PREFLIGHT_REF_OBSERVATIONS_INVALID")
    attempt = receipt.get("attempt_state")
    if (
        not isinstance(attempt, dict)
        or attempt.get("global_lease_acquired") is not False
        or attempt.get("local_lease_created") is not False
        or attempt.get("remaining_attempts") != 1
        or receipt.get("native_runtime") != "NOT_RUN"
    ):
        raise FirewallError("READ_ONLY_PREFLIGHT_ATTEMPT_STATE_INVALID")
    return receipt


def acquire_global_lease(
    *,
    contract: Mapping[str, Any],
    release_head: str,
    successor_receipt_sha256: str,
    preflight_receipt_sha256: str,
    token: str,
    output: Path,
    api_base: str = "https://api.github.com",
    opener: Any = urllib.request.urlopen,
) -> dict[str, Any]:
    budget = contract["attempt_budget"]
    if not token:
        raise FirewallError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")
    if not _valid_hex(release_head, 40):
        raise FirewallError("FIREWALL_RELEASE_HEAD_INVALID")
    ref = budget["global_lease_ref"]
    short_ref = ref.removeprefix("refs/")
    endpoint = (
        api_base.rstrip("/")
        + "/repos/cosmosapjw-quantum/rei_bianchi/git/refs"
    )
    request = urllib.request.Request(
        endpoint,
        data=canonical_bytes({"ref": ref, "sha": release_head}),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rei-runtime-prelease-import-firewall/v1",
        },
    )
    try:
        with opener(request, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            raise FirewallError("STOP_ATTEMPT_ALREADY_RESERVED") from exc
        raise FirewallError(f"STOP_GLOBAL_LEASE_HTTP_{exc.code}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FirewallError("STOP_GLOBAL_LEASE_TRANSPORT_OR_RESPONSE") from exc
    if (
        status != 201
        or not isinstance(body, dict)
        or body.get("ref") not in {ref, short_ref}
        or body.get("object", {}).get("sha") != release_head
    ):
        raise FirewallError("STOP_REMOTE_LEASE_RESPONSE_MISMATCH")
    record = {
        "schema": "rei-runtime-global-attempt-lease-receipt/v3",
        "status": "GLOBAL_ATTEMPT_RESERVED",
        "ordinal": 3,
        "ref": ref,
        "target_commit": release_head,
        "target_relation": "EXACT_FIREWALL_RELEASE_HEAD",
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "preflight_receipt_sha256": preflight_receipt_sha256,
        "mutation_policy": "CREATE_ONLY_NO_UPDATE_NO_DELETE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "native_runtime": "NOT_RUN",
    }
    write_o_excl(output, record)
    return record


def create_local_lease(
    *,
    output: Path,
    repo: Path,
    state_root: Path,
    release_head: str,
    release_tree: str,
    global_record: Mapping[str, Any],
    successor_receipt_sha256: str,
    preflight_receipt_sha256: str,
) -> dict[str, Any]:
    target = Path(output)
    state = Path(state_root).resolve(strict=True)
    repository = Path(repo).resolve(strict=True)
    if target.parent.resolve(strict=True) != state:
        raise FirewallError("LOCAL_LEASE_OUTSIDE_ATTEMPT_STATE_ROOT")
    if _is_under(target, Path("/tmp").resolve(strict=True)) or _is_under(
        target, repository
    ):
        raise FirewallError("LOCAL_LEASE_PATH_FORBIDDEN")
    if global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED":
        raise FirewallError("GLOBAL_LEASE_NOT_RESERVED")
    record = {
        "schema": "rei-runtime-persistent-local-attempt-lease/v2",
        "status": "LOCAL_ATTEMPT_RESERVED",
        "ordinal": 3,
        "firewall_release_head": release_head,
        "firewall_release_tree": release_tree,
        "global_lease_ref": global_record["ref"],
        "global_lease_receipt_sha256": sha256_file(
            state / "attempt-3.global-lease.json"
        ),
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "preflight_receipt_sha256": preflight_receipt_sha256,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "native_runtime": "NOT_RUN",
    }
    write_o_excl(target, record)
    return record


def create_dispatch_intent(
    *,
    output: Path,
    state_root: Path,
    release_head: str,
    release_tree: str,
    global_record: Mapping[str, Any],
    local_record: Mapping[str, Any],
    successor_receipt: Path,
    preflight_receipt: Path,
    evidence_root: Path,
) -> dict[str, Any]:
    state = Path(state_root).resolve(strict=True)
    target = Path(output)
    if target.parent.resolve(strict=True) != state:
        raise FirewallError("DISPATCH_INTENT_OUTSIDE_ATTEMPT_STATE_ROOT")
    if global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED":
        raise FirewallError("GLOBAL_LEASE_NOT_RESERVED")
    if local_record.get("status") != "LOCAL_ATTEMPT_RESERVED":
        raise FirewallError("LOCAL_LEASE_NOT_RESERVED")
    record = {
        "schema": "rei-runtime-native-dispatch-intent/v1",
        "status": "DISPATCH_INTENT_WRITTEN",
        "ordinal": 3,
        "firewall_release_head": release_head,
        "firewall_release_tree": release_tree,
        "global_lease_receipt": str(state / "attempt-3.global-lease.json"),
        "global_lease_receipt_sha256": sha256_file(
            state / "attempt-3.global-lease.json"
        ),
        "local_lease_receipt": str(state / "attempt-3.local-lease.json"),
        "local_lease_receipt_sha256": sha256_file(
            state / "attempt-3.local-lease.json"
        ),
        "successor_section0_receipt": str(Path(successor_receipt).resolve(strict=True)),
        "successor_section0_receipt_sha256": sha256_file(successor_receipt),
        "preflight_receipt": str(Path(preflight_receipt).resolve(strict=True)),
        "preflight_receipt_sha256": sha256_file(preflight_receipt),
        "evidence_root": str(Path(evidence_root).resolve(strict=False)),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "retries_after_outcome": 0,
    }
    write_o_excl(target, record)
    return record


def validate_attempt_receipts(
    *,
    state_root: Path,
    dispatch_intent: Path,
    expected_head: str,
    expected_tree: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state = Path(state_root).resolve(strict=True)
    global_path = state / "attempt-3.global-lease.json"
    local_path = state / "attempt-3.local-lease.json"
    dispatch_path = Path(dispatch_intent).resolve(strict=True)
    if dispatch_path.parent != state:
        raise FirewallError("DISPATCH_INTENT_OUTSIDE_ATTEMPT_STATE_ROOT")
    global_record = load_json_file(global_path, "GLOBAL_LEASE_RECEIPT_UNREADABLE")
    local_record = load_json_file(local_path, "LOCAL_LEASE_RECEIPT_UNREADABLE")
    dispatch_record = load_json_file(
        dispatch_path, "DISPATCH_INTENT_RECEIPT_UNREADABLE"
    )
    if (
        global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED"
        or global_record.get("target_commit") != expected_head
        or global_record.get("target_relation") != "EXACT_FIREWALL_RELEASE_HEAD"
    ):
        raise FirewallError("GLOBAL_LEASE_RECEIPT_MISMATCH")
    if (
        local_record.get("status") != "LOCAL_ATTEMPT_RESERVED"
        or local_record.get("firewall_release_head") != expected_head
        or local_record.get("firewall_release_tree") != expected_tree
        or local_record.get("global_lease_receipt_sha256")
        != sha256_file(global_path)
    ):
        raise FirewallError("LOCAL_LEASE_RECEIPT_MISMATCH")
    if (
        dispatch_record.get("status") != "DISPATCH_INTENT_WRITTEN"
        or dispatch_record.get("firewall_release_head") != expected_head
        or dispatch_record.get("firewall_release_tree") != expected_tree
        or dispatch_record.get("global_lease_receipt_sha256")
        != sha256_file(global_path)
        or dispatch_record.get("local_lease_receipt_sha256")
        != sha256_file(local_path)
        or dispatch_record.get("retries_after_outcome") != 0
    ):
        raise FirewallError("DISPATCH_INTENT_RECEIPT_MISMATCH")
    return global_record, local_record, dispatch_record


def remaining_attempts_after_stop(*, global_acquired: bool) -> int:
    return 0 if global_acquired else 1
