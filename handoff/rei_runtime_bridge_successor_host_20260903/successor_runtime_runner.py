#!/usr/bin/env python3
"""Fail-closed successor-host runner for one REI native bridge attempt.

The runner accepts only a fresh successor Section-0 receipt, verifies the exact
published executable release, atomically reserves the fixed GitHub ref with
that release as its target, creates a persistent local O_EXCL lease, and only
then invokes the unchanged production bridge once. It does not accept or
reconstruct the historical raw Section-0 receipt.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence
import urllib.error
import urllib.request

PACKAGE = Path(__file__).resolve().parent
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
PACKAGE_INDEX_PATH = PACKAGE / "PACKAGE_INDEX.json"
PROTOCOL_PATH = PACKAGE / "GLOBAL_ATTEMPT_LEASE_PROTOCOL_V2.json"


class SuccessorHandoffError(RuntimeError):
    """Typed fail-closed successor-handoff error."""


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
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def write_o_excl(path: Path, value: Mapping[str, Any]) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise SuccessorHandoffError("STOP_LOCAL_ATTEMPT_ALREADY_RESERVED") from exc
    except OSError as exc:
        raise SuccessorHandoffError("CREATE_ONLY_RECEIPT_UNAVAILABLE") from exc
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(canonical_bytes(dict(value)) + b"\n")
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SuccessorHandoffError("SUCCESSOR_HANDOFF_CONTRACT_UNREADABLE") from exc
    required = {
        "schema",
        "classification",
        "repository",
        "immutable_governance_predecessor",
        "source_handoff",
        "successor_section0",
        "attempt_budget",
        "execution_context",
        "required_operations",
        "forbidden_operations",
        "residual_blockers",
        "success_status",
        "failure_status",
        "claim_ceiling",
    }
    if (
        not isinstance(value, dict)
        or set(value) != required
        or value.get("schema") != "rei-runtime-successor-host-handoff/v1"
        or value.get("repository") != "cosmosapjw-quantum/rei_bianchi"
    ):
        raise SuccessorHandoffError("SUCCESSOR_HANDOFF_CONTRACT_SCHEMA_INVALID")
    budget = value["attempt_budget"]
    if (
        budget.get("ordinal") != 3
        or budget.get("prior_attempts") != 2
        or budget.get("remaining_native_attempts") != 1
        or budget.get("retries_after_outcome") != 0
        or budget.get("global_lease_target_relation")
        != "EXACT_EXECUTABLE_RELEASE_HEAD"
    ):
        raise SuccessorHandoffError("SUCCESSOR_HANDOFF_ATTEMPT_BUDGET_INVALID")
    return value


def verify_package_index(
    root: Path = PACKAGE,
    index_path: Path = PACKAGE_INDEX_PATH,
) -> None:
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SuccessorHandoffError("SUCCESSOR_PACKAGE_INDEX_UNREADABLE") from exc
    if (
        not isinstance(index, dict)
        or set(index) != {"schema", "git_object_format", "entries"}
        or index["schema"] != "rei-runtime-successor-handoff-package-index/v1"
        or index["git_object_format"] != "sha1"
        or not isinstance(index["entries"], list)
    ):
        raise SuccessorHandoffError("SUCCESSOR_PACKAGE_INDEX_INVALID")
    expected: dict[Path, str] = {}
    for row in index["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            raise SuccessorHandoffError("SUCCESSOR_PACKAGE_INDEX_INVALID")
        pure = PurePosixPath(row["path"])
        if pure.is_absolute() or ".." in pure.parts or str(pure) != row["path"]:
            raise SuccessorHandoffError("SUCCESSOR_PACKAGE_INDEX_INVALID")
        relative = Path(row["path"])
        if relative in expected:
            raise SuccessorHandoffError("SUCCESSOR_PACKAGE_INDEX_INVALID")
        expected[relative] = row["blob_sha"]
    package_root = root.resolve(strict=True)
    actual = {
        path.relative_to(package_root)
        for path in package_root.rglob("*")
        if path.is_file() and path.resolve(strict=True) != index_path.resolve(strict=True)
    }
    if set(expected) != actual:
        raise SuccessorHandoffError("SUCCESSOR_PACKAGE_SCOPE_MISMATCH")
    for relative, blob_sha in expected.items():
        path = package_root / relative
        if path.is_symlink() or not path.is_file() or git_blob_sha1(path) != blob_sha:
            raise SuccessorHandoffError(
                f"SUCCESSOR_PACKAGE_BLOB_MISMATCH:{relative.as_posix()}"
            )


def load_successor_section0_receipt(
    path: Path,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise SuccessorHandoffError("SUCCESSOR_SECTION0_UNAVAILABLE")
    try:
        receipt = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SuccessorHandoffError("SUCCESSOR_SECTION0_UNREADABLE") from exc
    rule = contract["successor_section0"]
    if receipt.get("status") != rule["required_status"]:
        raise SuccessorHandoffError("SUCCESSOR_SECTION0_STATUS_MISMATCH")
    if receipt.get("schema") != rule["required_schema"]:
        raise SuccessorHandoffError("SUCCESSOR_SECTION0_SCHEMA_MISMATCH")
    if (
        receipt.get("semantic_toolchain_lock_sha256")
        != rule["semantic_toolchain_lock_sha256"]
    ):
        raise SuccessorHandoffError("SUCCESSOR_SECTION0_LOCK_MISMATCH")
    if receipt.get("observed_toolchain") != rule["semantic_toolchain_lock"]:
        raise SuccessorHandoffError("SUCCESSOR_SECTION0_FIELD_MISMATCH")
    if sha256_file(candidate) == rule["historical_receipt_sha256"]:
        raise SuccessorHandoffError("HISTORICAL_SECTION0_RECEIPT_REUSE_FORBIDDEN")
    return receipt


def _git_text(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        raise SuccessorHandoffError(
            f"EXECUTABLE_RELEASE_GIT_COMMAND_FAILED:{arguments[0]}"
        )
    return completed.stdout.strip()


def verify_exact_release_identity(
    repo: Path,
    expected_head: str,
    expected_tree: str,
    *,
    git_text: Callable[..., str] | None = None,
) -> tuple[str, str]:
    root = Path(repo).resolve(strict=True)
    runner = git_text or (lambda *args: _git_text(root, *args))
    head = runner("rev-parse", "HEAD")
    tree = runner("rev-parse", "HEAD^{tree}")
    if head != expected_head:
        raise SuccessorHandoffError("EXECUTABLE_RELEASE_HEAD_MISMATCH")
    if tree != expected_tree:
        raise SuccessorHandoffError("EXECUTABLE_RELEASE_TREE_MISMATCH")
    return head, tree


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_local_lease_path(
    path: Path,
    *,
    forbidden_roots: Sequence[Path],
) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise SuccessorHandoffError("LOCAL_LEASE_PATH_NOT_ABSOLUTE")
    parent = candidate.parent.resolve(strict=True)
    target = parent / candidate.name
    tmp = Path("/tmp").resolve(strict=True)
    if _is_under(target, tmp):
        raise SuccessorHandoffError("LOCAL_LEASE_UNDER_TMP_FORBIDDEN")
    for raw_root in forbidden_roots:
        root = Path(raw_root).resolve(strict=True)
        if _is_under(target, root):
            raise SuccessorHandoffError("LOCAL_LEASE_IN_FORBIDDEN_ROOT")
    if target.is_symlink():
        raise SuccessorHandoffError("LOCAL_LEASE_SYMLINK_FORBIDDEN")
    return target


def create_persistent_local_lease(
    path: Path,
    payload: Mapping[str, Any],
    *,
    forbidden_roots: Sequence[Path],
) -> Path:
    target = validate_local_lease_path(path, forbidden_roots=forbidden_roots)
    write_o_excl(target, payload)
    return target.resolve(strict=True)


def acquire_global_lease(
    *,
    contract: Mapping[str, Any],
    successor_receipt_sha256: str,
    expected_release_head: str,
    token: str,
    output: Path,
    api_base: str = "https://api.github.com",
    opener: Callable[..., Any] = urllib.request.urlopen,
    reservation_observer: Callable[[], None] | None = None,
) -> dict[str, Any]:
    budget = contract["attempt_budget"]
    if budget["global_lease_target_relation"] != "EXACT_EXECUTABLE_RELEASE_HEAD":
        raise SuccessorHandoffError("GLOBAL_LEASE_TARGET_RELATION_MISMATCH")
    if (
        len(expected_release_head) != 40
        or any(ch not in "0123456789abcdef" for ch in expected_release_head)
    ):
        raise SuccessorHandoffError("EXECUTABLE_RELEASE_HEAD_INVALID")
    if not token:
        raise SuccessorHandoffError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    ref = budget["global_lease_ref"]
    if protocol.get("lease_ref") != ref:
        raise SuccessorHandoffError("GLOBAL_LEASE_REF_MISMATCH")
    endpoint = api_base.rstrip("/") + protocol["acquisition"]["endpoint"]
    request = urllib.request.Request(
        endpoint,
        data=canonical_bytes({"ref": ref, "sha": expected_release_head}),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "rei-runtime-successor-host-handoff/v1",
        },
    )
    try:
        with opener(request, 30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            raise SuccessorHandoffError("STOP_ATTEMPT_ALREADY_RESERVED") from exc
        raise SuccessorHandoffError(f"STOP_GLOBAL_LEASE_HTTP_{exc.code}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SuccessorHandoffError(
            "STOP_GLOBAL_LEASE_TRANSPORT_OR_RESPONSE"
        ) from exc
    if (
        status != 201
        or body.get("ref") != ref
        or body.get("object", {}).get("sha") != expected_release_head
    ):
        raise SuccessorHandoffError("STOP_REMOTE_LEASE_RESPONSE_MISMATCH")
    if reservation_observer is not None:
        reservation_observer()
    record = {
        "schema": "rei-runtime-global-attempt-lease-receipt/v2",
        "status": "GLOBAL_ATTEMPT_RESERVED",
        "ref": ref,
        "target_commit": expected_release_head,
        "target_relation": "EXACT_EXECUTABLE_RELEASE_HEAD",
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "mutation_policy": "CREATE_ONLY_NO_UPDATE_NO_DELETE",
        "native_runtime": "NOT_RUN",
    }
    output_path = Path(output)
    if not output_path.is_absolute():
        raise SuccessorHandoffError("GLOBAL_LEASE_RECEIPT_PATH_NOT_ABSOLUTE")
    output_path.parent.resolve(strict=True)
    write_o_excl(output_path, record)
    return record


def remaining_attempts_after_stop(*, global_acquired: bool) -> int:
    """The atomic remote reservation consumes the only remaining attempt."""
    return 0 if global_acquired else 1


def reserve_then_dispatch(
    *,
    global_acquire: Callable[[], Mapping[str, Any]],
    local_lease_path: Path,
    local_lease_payload: Mapping[str, Any],
    forbidden_local_roots: Sequence[Path],
    native_dispatch: Callable[[], Any],
) -> Any:
    global_record = global_acquire()
    if global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED":
        raise SuccessorHandoffError("GLOBAL_LEASE_NOT_RESERVED")
    create_persistent_local_lease(
        local_lease_path,
        local_lease_payload,
        forbidden_roots=forbidden_local_roots,
    )
    return native_dispatch()


def _load_base_runner(repo: Path, contract: Mapping[str, Any]) -> Any:
    record = contract["source_handoff"]
    path = repo / record["base_runner_path"]
    if (
        path.is_symlink()
        or not path.is_file()
        or sha256_file(path) != record["base_runner_sha256"]
    ):
        raise SuccessorHandoffError("BASE_HANDOFF_RUNNER_IDENTITY_MISMATCH")
    spec = importlib.util.spec_from_file_location(
        "rei_runtime_successor_base", path
    )
    if spec is None or spec.loader is None:
        raise SuccessorHandoffError("BASE_HANDOFF_RUNNER_IMPORT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_repo_file(repo: Path, relative: str, classification: str) -> Path:
    root = repo.resolve(strict=True)
    path = root / relative
    if path.is_symlink():
        raise SuccessorHandoffError(classification)
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise SuccessorHandoffError(classification) from exc
    if not resolved.is_file():
        raise SuccessorHandoffError(classification)
    return resolved


def verify_source_inputs(repo: Path, contract: Mapping[str, Any]) -> None:
    record = contract["source_handoff"]
    checks = {
        record["patched_input_lock_path"]: record["patched_input_lock_sha256"],
        record["production_bridge_path"]: record["production_bridge_sha256"],
        f'{record["rust_stage_path"]}/rust/source_bound_thermal.rs': record[
            "rust_source_sha256"
        ],
    }
    for relative, expected in checks.items():
        path = _resolve_repo_file(repo, relative, "SOURCE_INPUT_UNAVAILABLE")
        if sha256_file(path) != expected:
            raise SuccessorHandoffError(
                f"SOURCE_INPUT_IDENTITY_MISMATCH:{relative}"
            )


def run_native_once(
    *,
    repo: Path,
    rustc: Path,
    evidence_root: Path,
    contract: Mapping[str, Any],
    successor_receipt: Mapping[str, Any],
    base_runner: Any | None = None,
    production_bridge: Any | None = None,
) -> tuple[dict[str, Any], Path]:
    base = base_runner or _load_base_runner(repo, contract)
    root = repo.resolve(strict=True)
    bridge = production_bridge or base.load_bridge(
        root, contract["source_handoff"]["production_bridge_path"]
    )
    base.verify_standalone_repository_context(bridge, root)
    predecessor = contract["immutable_governance_predecessor"]
    merge_base = base.git_checked(
        bridge, root, "merge-base", "HEAD", predecessor["commit"]
    ).strip()
    if merge_base != predecessor["commit"]:
        raise SuccessorHandoffError("GOVERNANCE_PREDECESSOR_NOT_ANCESTOR")
    if (
        base.git_checked(
            bridge, root, "rev-parse", f'{predecessor["commit"]}^{{tree}}'
        ).strip()
        != predecessor["tree"]
    ):
        raise SuccessorHandoffError("GOVERNANCE_PREDECESSOR_TREE_MISMATCH")
    if base.git_checked(
        bridge, root, "status", "--porcelain=v1", "--untracked-files=all"
    ):
        raise SuccessorHandoffError("RUNTIME_HANDOFF_WORKTREE_NOT_CLEAN")
    rustc_path = base.configure_rustc_locator(rustc)
    output_root = base.create_evidence_root(evidence_root, bridge, root)
    source = contract["source_handoff"]
    stage = root / source["rust_stage_path"]
    identity = bridge.authenticate_runtime(stage_dir=stage)
    if identity["source_sha256"] != source["rust_source_sha256"]:
        raise SuccessorHandoffError("RUNTIME_SOURCE_IDENTITY_MISMATCH")
    if identity["rustc_sha256"] != sha256_file(rustc_path):
        raise SuccessorHandoffError("RUSTC_LOCATOR_IDENTITY_BINDING_MISMATCH")
    if identity["abi_version"] != source["abi_version"]:
        raise SuccessorHandoffError("RUNTIME_ABI_IDENTITY_MISMATCH")
    if identity["precision_bits"] != source["precision_bits"]:
        raise SuccessorHandoffError("RUNTIME_PRECISION_IDENTITY_MISMATCH")
    if identity["rounding_policy"] != source["rounding_policy"]:
        raise SuccessorHandoffError("RUNTIME_ROUNDING_IDENTITY_MISMATCH")

    first = bridge.build_authenticated_backend(
        stage_dir=stage, output_dir=output_root / "build-a"
    )
    second = bridge.build_authenticated_backend(
        stage_dir=stage, output_dir=output_root / "build-b"
    )
    first_sha = sha256_file(first.artifact_path)
    second_sha = sha256_file(second.artifact_path)
    expected_artifact = source["expected_artifact_sha256"]
    if first_sha != expected_artifact or second_sha != expected_artifact:
        raise SuccessorHandoffError("RUNTIME_ARTIFACT_PIN_MISMATCH")
    if first.artifact_path.read_bytes() != second.artifact_path.read_bytes():
        raise SuccessorHandoffError("RUNTIME_BUILD_NOT_BYTE_IDENTICAL")
    if first.receipt.canonical_bytes() != second.receipt.canonical_bytes():
        raise SuccessorHandoffError("RUNTIME_RECEIPT_NOT_BYTE_IDENTICAL")

    quotient = bridge.interval_divide((1.0, 1.0), (2.0, 2.0), backend=first)
    if (
        len(quotient) != 2
        or not all(math.isfinite(value) for value in quotient)
        or quotient[0] > 0.5
        or quotient[1] < 0.5
    ):
        raise SuccessorHandoffError("RUNTIME_NONZERO_DIVISION_ENCLOSURE_MISMATCH")
    try:
        bridge.interval_divide((1.0, 1.0), (-1.0, 1.0), backend=first)
    except bridge.RustBackendError as exc:
        if "ZERO_DIVISOR_INTERVAL" not in str(exc):
            raise SuccessorHandoffError("RUNTIME_ZERO_DIVISION_WRONG_FAILURE") from exc
    else:
        raise SuccessorHandoffError("RUNTIME_ZERO_DIVISION_ACCEPTED")

    residual = contract["residual_blockers"]
    if bridge.PROCESS_BOUNDARY_BLOCKER != residual["process_boundary"]:
        raise SuccessorHandoffError("RUNTIME_PROCESS_BOUNDARY_CLASSIFICATION_MISMATCH")
    if bridge.PRESTART_RUNTIME_BLOCKER != residual["prestart_runtime"]:
        raise SuccessorHandoffError("RUNTIME_PRESTART_CLASSIFICATION_MISMATCH")

    result = {
        "schema": "rei-runtime-successor-host-result/v1",
        "status": contract["success_status"],
        "successor_section0": {
            "status": successor_receipt["status"],
            "semantic_toolchain_lock_sha256": successor_receipt[
                "semantic_toolchain_lock_sha256"
            ],
        },
        "runtime_identity": identity,
        "artifact_sha256": first_sha,
        "backend_receipt": first.receipt.to_mapping(),
        "backend_receipt_sha256": first.receipt.identity_sha256(),
        "two_builds_byte_identical": True,
        "nonzero_division_enclosure": list(quotient),
        "zero_containing_divisor_rejection": "ZERO_DIVISOR_INTERVAL",
        "residual_blockers": residual,
        "claim_ceiling": contract["claim_ceiling"],
    }
    return result, output_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--expected-release-head", required=True)
    parser.add_argument("--expected-release-tree", required=True)
    parser.add_argument("--successor-section0-receipt", type=Path, required=True)
    parser.add_argument("--rustc", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--attempt-state-root", type=Path, required=True)
    parser.add_argument("--api-base", default="https://api.github.com")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    options = parser.parse_args(argv)

    if os.environ.get("REI_NATIVE_DISPATCH_FORBIDDEN") == "1":
        print("STOP_INVALID: HOSTED_CI_NATIVE_DISPATCH_FORBIDDEN", file=sys.stderr)
        return 65

    state_root: Path | None = None
    dispatch_started = False
    global_acquired = False
    try:
        verify_package_index()
        contract = load_contract()
        repo = options.repo.resolve(strict=True)
        verify_source_inputs(repo, contract)
        successor = load_successor_section0_receipt(
            options.successor_section0_receipt, contract
        )
        base_runner = _load_base_runner(repo, contract)
        production_bridge = base_runner.load_bridge(
            repo, contract["source_handoff"]["production_bridge_path"]
        )
        standalone_roots = base_runner.verify_standalone_repository_context(
            production_bridge, repo
        )
        pinned_git_text = lambda *args: base_runner.git_checked(
            production_bridge, repo, *args
        ).strip()
        verify_exact_release_identity(
            repo,
            options.expected_release_head,
            options.expected_release_tree,
            git_text=pinned_git_text,
        )
        predecessor = contract["immutable_governance_predecessor"]
        if (
            pinned_git_text("merge-base", "HEAD", predecessor["commit"])
            != predecessor["commit"]
        ):
            raise SuccessorHandoffError("GOVERNANCE_PREDECESSOR_NOT_ANCESTOR")
        if (
            pinned_git_text(
                "rev-parse", f'{predecessor["commit"]}^{{tree}}'
            )
            != predecessor["tree"]
        ):
            raise SuccessorHandoffError("GOVERNANCE_PREDECESSOR_TREE_MISMATCH")
        pinned_git_text("fsck", "--full")
        pinned_git_text("diff", "--check")
        if pinned_git_text(
            "status", "--porcelain=v1", "--untracked-files=all"
        ):
            raise SuccessorHandoffError("RUNTIME_HANDOFF_WORKTREE_NOT_CLEAN")
        base_runner.configure_rustc_locator(options.rustc)
        evidence_candidate = options.evidence_root.resolve(strict=False)
        if evidence_candidate.exists() or evidence_candidate.is_symlink():
            raise SuccessorHandoffError("RUNTIME_EVIDENCE_ROOT_PREEXISTS")
        for worktree in standalone_roots:
            if _is_under(evidence_candidate, worktree):
                raise SuccessorHandoffError("RUNTIME_EVIDENCE_INSIDE_GIT_WORKTREE")
        state_root = options.attempt_state_root
        if (
            not state_root.is_absolute()
            or state_root.is_symlink()
            or not state_root.is_dir()
        ):
            raise SuccessorHandoffError("ATTEMPT_STATE_ROOT_UNAVAILABLE")
        state_root = state_root.resolve(strict=True)
        if _is_under(state_root, Path("/tmp").resolve(strict=True)) or _is_under(
            state_root, repo
        ):
            raise SuccessorHandoffError("ATTEMPT_STATE_ROOT_FORBIDDEN")
        global_receipt = state_root / "attempt-3.global-lease.json"
        local_lease = state_root / "attempt-3.local-lease.json"
        outcome = state_root / "attempt-3.outcome.json"
        for path in (global_receipt, local_lease, outcome):
            if path.exists() or path.is_symlink():
                raise SuccessorHandoffError("ATTEMPT_STATE_ALREADY_PRESENT")
        token = os.environ.get(options.token_env, "")
        successor_sha = sha256_file(options.successor_section0_receipt)

        def mark_global_acquired() -> None:
            nonlocal global_acquired
            global_acquired = True

        def global_acquire() -> Mapping[str, Any]:
            return acquire_global_lease(
                contract=contract,
                successor_receipt_sha256=successor_sha,
                expected_release_head=options.expected_release_head,
                token=token,
                output=global_receipt,
                api_base=options.api_base,
                reservation_observer=mark_global_acquired,
            )

        local_payload = {
            "schema": "rei-runtime-persistent-local-attempt-lease/v1",
            "status": "LOCAL_ATTEMPT_RESERVED",
            "ordinal": 3,
            "executable_release_head": options.expected_release_head,
            "executable_release_tree": options.expected_release_tree,
            "successor_section0_receipt_sha256": successor_sha,
            "global_lease_ref": contract["attempt_budget"]["global_lease_ref"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "native_runtime": "NOT_RUN",
        }

        def native_dispatch() -> Any:
            nonlocal dispatch_started
            dispatch_started = True
            return run_native_once(
                repo=repo,
                rustc=options.rustc,
                evidence_root=options.evidence_root,
                contract=contract,
                successor_receipt=successor,
                base_runner=base_runner,
                production_bridge=production_bridge,
            )

        result, output_root = reserve_then_dispatch(
            global_acquire=global_acquire,
            local_lease_path=local_lease,
            local_lease_payload=local_payload,
            forbidden_local_roots=(repo,),
            native_dispatch=native_dispatch,
        )
        result["execution_lineage"] = {
            "executable_release_head": options.expected_release_head,
            "executable_release_tree": options.expected_release_tree,
            "global_lease_receipt_sha256": sha256_file(global_receipt),
            "local_lease_sha256": sha256_file(local_lease),
            "attempt_ordinal": 3,
            "retries_after_outcome": 0,
        }
        runtime_receipt = output_root / "runtime_bridge_receipt.json"
        write_o_excl(runtime_receipt, result)
        write_o_excl(
            outcome,
            {
                "schema": "rei-runtime-successor-host-attempt-outcome/v1",
                "status": "NATIVE_ATTEMPT_COMPLETED",
                "dispatch_started": True,
                "exit_classification": "SUCCESS_EXIT_0",
                "runtime_receipt": str(runtime_receipt),
                "claim_ceiling": contract["claim_ceiling"],
            },
        )
    except SuccessorHandoffError as exc:
        if state_root is not None and state_root.is_dir():
            outcome = state_root / "attempt-3.outcome.json"
            if not outcome.exists():
                try:
                    write_o_excl(
                        outcome,
                        {
                            "schema": "rei-runtime-successor-host-attempt-outcome/v1",
                            "status": "STOP_INVALID",
                            "dispatch_started": dispatch_started,
                            "first_blocker": str(exc),
                            "global_lease_acquired": global_acquired,
                            "retries_remaining": remaining_attempts_after_stop(
                                global_acquired=global_acquired
                            ),
                        },
                    )
                except Exception:
                    pass
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        if state_root is not None and state_root.is_dir():
            outcome = state_root / "attempt-3.outcome.json"
            if not outcome.exists():
                try:
                    write_o_excl(
                        outcome,
                        {
                            "schema": "rei-runtime-successor-host-attempt-outcome/v1",
                            "status": "STOP_INVALID",
                            "dispatch_started": dispatch_started,
                            "first_blocker": (
                                "UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION:"
                                f"{type(exc).__name__}:{exc}"
                            ),
                            "global_lease_acquired": global_acquired,
                            "retries_remaining": remaining_attempts_after_stop(
                                global_acquired=global_acquired
                            ),
                        },
                    )
                except Exception:
                    pass
        print(
            "STOP_INVALID: UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION:"
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 65
    print(
        json.dumps(
            {
                "status": result["status"],
                "runtime_receipt": str(runtime_receipt),
                "outcome": str(outcome),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
