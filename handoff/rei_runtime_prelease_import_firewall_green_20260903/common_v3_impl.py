#!/usr/bin/env python3
"""Runtime-path-bound authority layer for the REI one-attempt firewall.

The complete PR #54 authority implementation is preserved byte-for-byte in
``common_v3_impl_legacy.py``.  This active layer adds one narrow invariant:
Section-0, immediate pre-reservation re-attestation, every attempt receipt, and
the post-lease worker must refer to the same resolved files behind the exact
paths used by the unchanged production bridge.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping
import urllib.error
import urllib.request

try:
    from . import common as _base
    from .common import *  # noqa: F401,F403
    from . import common_v3_impl_legacy as _legacy
    from .common_v3_impl_legacy import *  # noqa: F401,F403
except ImportError:
    import common as _base  # type: ignore
    from common import *  # type: ignore # noqa: F401,F403
    import common_v3_impl_legacy as _legacy  # type: ignore
    from common_v3_impl_legacy import *  # type: ignore # noqa: F401,F403


PACKAGE = Path(__file__).resolve().parent
RUNTIME_TOOLCHAIN_PATHS: dict[str, str] = {
    "cc": "/usr/bin/x86_64-linux-gnu-gcc",
    "ld": "/usr/bin/ld",
    "mpfr": "/usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1",
    "gmp": "/usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0",
}
RUNTIME_TOOLCHAIN_PATH_AUTHORITY = "POSTLEASE_PRODUCTION_PATHS"


def load_contract(path: Path = PACKAGE / "CONTRACT.json") -> dict[str, Any]:
    value = _base.load_json_file(path, "FIREWALL_CONTRACT_UNREADABLE")
    required = {
        "schema",
        "classification",
        "repository",
        "immutable_parent",
        "source_lineage",
        "successor_section0",
        "runtime_toolchain_path_binding",
        "attempt_budget",
        "attempt_ref_protection",
        "execution_context",
        "required_operations",
        "forbidden_operations",
        "claim_ceiling",
        "success_status",
        "failure_status",
    }
    if (
        set(value) != required
        or value.get("schema") != "rei-runtime-prelease-import-firewall/v2"
        or value.get("repository") != GITHUB_REPOSITORY
        or value.get("success_status") != "PASS_AUTHORITY_BINDING_SOURCE"
        or value.get("failure_status") != "STOP_INVALID"
    ):
        raise _base.FirewallError("FIREWALL_CONTRACT_SCHEMA_INVALID")

    budget = value.get("attempt_budget")
    if (
        not isinstance(budget, dict)
        or budget.get("ordinal") != 3
        or budget.get("prior_attempts") != 2
        or budget.get("remaining_native_attempts") != 1
        or budget.get("retries_after_outcome") != 0
        or budget.get("global_lease_ref") != GLOBAL_ATTEMPT_REF
        or budget.get("global_lease_target_relation")
        != "EXACT_FIREWALL_RELEASE_HEAD"
    ):
        raise _base.FirewallError("FIREWALL_ATTEMPT_BUDGET_INVALID")

    protection = value.get("attempt_ref_protection")
    if (
        not isinstance(protection, dict)
        or protection.get("required_before_global_reservation") is not True
        or protection.get("required_schema")
        != "rei-runtime-attempt-ref-protection-receipt/v1"
        or protection.get("required_status")
        != "PASS_ATTEMPT_REF_SERVER_PROTECTION"
        or protection.get("authority") != GITHUB_AUTHORITY
        or protection.get("repository") != GITHUB_REPOSITORY
        or protection.get("global_ref") != GLOBAL_ATTEMPT_REF
        or protection.get("target_pattern") != "refs/heads/attempt-ledger/**"
        or set(protection.get("required_rules", []))
        != {"update", "deletion", "non_fast_forward"}
    ):
        raise _base.FirewallError("ATTEMPT_REF_PROTECTION_CONTRACT_INVALID")

    binding = value.get("runtime_toolchain_path_binding")
    if (
        not isinstance(binding, dict)
        or set(binding) != {"authority", "paths"}
        or binding.get("authority") != RUNTIME_TOOLCHAIN_PATH_AUTHORITY
        or binding.get("paths") != RUNTIME_TOOLCHAIN_PATHS
    ):
        raise _base.FirewallError("RUNTIME_TOOLCHAIN_PATH_BINDING_INVALID")
    return value


def _snapshot_payload(paths: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "rei-runtime-toolchain-path-snapshot/v1",
        "authority": RUNTIME_TOOLCHAIN_PATH_AUTHORITY,
        "paths": dict(paths),
    }


def _snapshot_sha256(paths: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        _base.canonical_bytes(_snapshot_payload(paths))
    ).hexdigest()


def validate_runtime_toolchain_witness_paths(
    contract: Mapping[str, Any],
    *,
    cc: Path,
    ld: Path,
    mpfr: Path,
    gmp: Path,
) -> dict[str, Any]:
    """Bind witness files to the actual resolved post-lease runtime paths."""

    binding = contract.get("runtime_toolchain_path_binding")
    if (
        not isinstance(binding, Mapping)
        or binding.get("authority") != RUNTIME_TOOLCHAIN_PATH_AUTHORITY
        or not isinstance(binding.get("paths"), Mapping)
    ):
        raise _base.FirewallError("RUNTIME_TOOLCHAIN_PATH_BINDING_INVALID")
    declared_paths = binding["paths"]
    lock = contract.get("successor_section0", {}).get(
        "semantic_toolchain_lock"
    )
    if not isinstance(lock, Mapping):
        raise _base.FirewallError("RUNTIME_TOOLCHAIN_HASH_LOCK_INVALID")

    supplied = {"cc": cc, "ld": ld, "mpfr": mpfr, "gmp": gmp}
    rows: dict[str, dict[str, Any]] = {}
    for role in ("cc", "ld", "mpfr", "gmp"):
        raw_declared = declared_paths.get(role)
        if not isinstance(raw_declared, str):
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_PATH_UNAVAILABLE:{role}"
            )
        declared = Path(raw_declared)
        if not declared.is_absolute():
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_PATH_UNAVAILABLE:{role}"
            )
        try:
            resolved = declared.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_PATH_UNAVAILABLE:{role}"
            ) from exc
        if not resolved.is_file():
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_PATH_UNAVAILABLE:{role}"
            )
        executable = role in {"cc", "ld"}
        if executable and not os.access(resolved, os.X_OK):
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_PATH_NOT_EXECUTABLE:{role}"
            )

        witness = Path(supplied[role])
        if not witness.is_absolute() or witness.is_symlink():
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH:{role}"
            )
        try:
            witness_resolved = witness.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH:{role}"
            ) from exc
        if witness_resolved != resolved:
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH:{role}"
            )

        expected_hash = lock.get(f"{role}_sha256")
        actual_hash = _base.sha256_file(resolved)
        if not _base._valid_hex(expected_hash, 64) or actual_hash != expected_hash:
            raise _base.FirewallError(
                f"RUNTIME_TOOLCHAIN_WITNESS_HASH_MISMATCH:{role}"
            )
        stat_result = resolved.stat()
        rows[role] = {
            "declared_path": str(declared),
            "resolved_path": str(resolved),
            "sha256": actual_hash,
            "size_bytes": stat_result.st_size,
            "executable": executable,
        }

    payload = _snapshot_payload(rows)
    return {**payload, "sha256": _snapshot_sha256(rows)}


def _validate_snapshot_record(snapshot: Mapping[str, Any]) -> None:
    paths = snapshot.get("paths")
    if (
        snapshot.get("schema") != "rei-runtime-toolchain-path-snapshot/v1"
        or snapshot.get("authority") != RUNTIME_TOOLCHAIN_PATH_AUTHORITY
        or not isinstance(paths, Mapping)
        or set(paths) != {"cc", "ld", "mpfr", "gmp"}
        or snapshot.get("sha256") != _snapshot_sha256(paths)
    ):
        raise _base.FirewallError("RUNTIME_TOOLCHAIN_SNAPSHOT_INVALID")


def validate_preflight_receipt(
    path: Path,
    *,
    expected_head: str,
    expected_tree: str,
    successor_receipt_sha256: str,
    expected_attempt_state_root: Path,
    expected_output_root: Path,
    expected_successor_receipt_path: Path,
    expected_authority: Mapping[str, Any],
    expected_global_ref: str,
    expected_runtime_toolchain_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    receipt = _legacy.validate_preflight_receipt(
        path,
        expected_head=expected_head,
        expected_tree=expected_tree,
        successor_receipt_sha256=successor_receipt_sha256,
        expected_attempt_state_root=expected_attempt_state_root,
        expected_output_root=expected_output_root,
        expected_successor_receipt_path=expected_successor_receipt_path,
        expected_authority=expected_authority,
        expected_global_ref=expected_global_ref,
    )
    if expected_runtime_toolchain_snapshot is not None:
        _validate_snapshot_record(expected_runtime_toolchain_snapshot)
        if (
            receipt.get("runtime_toolchain_paths")
            != expected_runtime_toolchain_snapshot["paths"]
            or receipt.get("runtime_toolchain_snapshot_sha256")
            != expected_runtime_toolchain_snapshot["sha256"]
        ):
            raise _base.FirewallError(
                "READ_ONLY_PREFLIGHT_RUNTIME_TOOLCHAIN_SNAPSHOT_MISMATCH"
            )
    return receipt


def revalidate_successor_toolchain(
    *,
    repo: Path,
    contract: Mapping[str, Any],
    rustc: Path,
    python: Path,
    mpfr: Path,
    gmp: Path,
    cc: Path,
    ld: Path,
    original_successor_receipt: Path,
    output: Path,
) -> dict[str, Any]:
    """Re-attest fields and actual runtime paths immediately pre-reservation."""

    snapshot = validate_runtime_toolchain_witness_paths(
        contract,
        cc=cc,
        ld=ld,
        mpfr=mpfr,
        gmp=gmp,
    )
    resolved = {
        role: Path(snapshot["paths"][role]["resolved_path"])
        for role in ("cc", "ld", "mpfr", "gmp")
    }
    result = _legacy.revalidate_successor_toolchain(
        repo=repo,
        contract=contract,
        rustc=rustc,
        python=python,
        mpfr=resolved["mpfr"],
        gmp=resolved["gmp"],
        cc=resolved["cc"],
        ld=resolved["ld"],
        original_successor_receipt=original_successor_receipt,
        output=output,
    )
    return {
        **result,
        "runtime_toolchain_paths": snapshot["paths"],
        "runtime_toolchain_snapshot_sha256": snapshot["sha256"],
    }


def acquire_global_lease(
    *,
    contract: Mapping[str, Any],
    release_head: str,
    successor_receipt_sha256: str,
    preflight_receipt_sha256: str,
    attempt_ref_protection_receipt_sha256: str,
    prelease_toolchain_revalidation_sha256: str,
    runtime_toolchain_snapshot_sha256: str,
    token: str,
    output: Path,
) -> dict[str, Any]:
    """Create the fixed GitHub ref and bind the canonical runtime paths."""

    budget = contract["attempt_budget"]
    for value in (
        successor_receipt_sha256,
        preflight_receipt_sha256,
        attempt_ref_protection_receipt_sha256,
        prelease_toolchain_revalidation_sha256,
        runtime_toolchain_snapshot_sha256,
    ):
        if not _base._valid_hex(value, 64):
            raise _base.FirewallError("GLOBAL_LEASE_EVIDENCE_HASH_INVALID")
    if not token:
        raise _base.FirewallError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")
    if not _base._valid_hex(release_head, 40):
        raise _base.FirewallError("FIREWALL_RELEASE_HEAD_INVALID")

    ref = budget["global_lease_ref"]
    short_ref = ref.removeprefix("refs/")
    endpoint = f"{GITHUB_API_BASE}/repos/{GITHUB_REPOSITORY}/git/refs"
    request = urllib.request.Request(
        endpoint,
        data=_base.canonical_bytes({"ref": ref, "sha": release_head}),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "rei-runtime-path-binding/v1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            raise _base.FirewallError("STOP_ATTEMPT_ALREADY_RESERVED") from exc
        raise _base.FirewallError(f"STOP_GLOBAL_LEASE_HTTP_{exc.code}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _base.FirewallError(
            "STOP_GLOBAL_LEASE_TRANSPORT_OR_RESPONSE"
        ) from exc
    if (
        status != 201
        or not isinstance(body, dict)
        or body.get("ref") not in {ref, short_ref}
        or body.get("object", {}).get("sha") != release_head
    ):
        raise _base.FirewallError("STOP_REMOTE_LEASE_RESPONSE_MISMATCH")

    record = {
        "schema": "rei-runtime-global-attempt-lease-receipt/v4",
        "status": "GLOBAL_ATTEMPT_RESERVED",
        "ordinal": 3,
        "authority": GITHUB_AUTHORITY,
        "ref": ref,
        "target_commit": release_head,
        "target_relation": "EXACT_FIREWALL_RELEASE_HEAD",
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "preflight_receipt_sha256": preflight_receipt_sha256,
        "attempt_ref_protection_receipt_sha256": (
            attempt_ref_protection_receipt_sha256
        ),
        "prelease_toolchain_revalidation_sha256": (
            prelease_toolchain_revalidation_sha256
        ),
        "runtime_toolchain_snapshot_sha256": (
            runtime_toolchain_snapshot_sha256
        ),
        "mutation_policy": "CREATE_ONLY_PROTECTED_NO_UPDATE_NO_DELETE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "native_runtime": "NOT_RUN",
    }
    _base.write_o_excl(output, record)
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
    runtime_toolchain_snapshot_sha256: str,
) -> dict[str, Any]:
    target = Path(output)
    state = Path(state_root).resolve(strict=True)
    repository = Path(repo).resolve(strict=True)
    if target.parent.resolve(strict=True) != state:
        raise _base.FirewallError("LOCAL_LEASE_OUTSIDE_ATTEMPT_STATE_ROOT")
    if _base._is_under(target, Path("/tmp").resolve(strict=True)) or _base._is_under(
        target, repository
    ):
        raise _base.FirewallError("LOCAL_LEASE_PATH_FORBIDDEN")
    if global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED":
        raise _base.FirewallError("GLOBAL_LEASE_NOT_RESERVED")
    if (
        not _base._valid_hex(runtime_toolchain_snapshot_sha256, 64)
        or global_record.get("runtime_toolchain_snapshot_sha256")
        != runtime_toolchain_snapshot_sha256
    ):
        raise _base.FirewallError("LOCAL_LEASE_RUNTIME_TOOLCHAIN_MISMATCH")

    record = {
        "schema": "rei-runtime-persistent-local-attempt-lease/v2",
        "status": "LOCAL_ATTEMPT_RESERVED",
        "ordinal": 3,
        "firewall_release_head": release_head,
        "firewall_release_tree": release_tree,
        "global_lease_ref": global_record["ref"],
        "global_lease_receipt_sha256": _base.sha256_file(
            state / "attempt-3.global-lease.json"
        ),
        "successor_section0_receipt_sha256": successor_receipt_sha256,
        "preflight_receipt_sha256": preflight_receipt_sha256,
        "runtime_toolchain_snapshot_sha256": (
            runtime_toolchain_snapshot_sha256
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "native_runtime": "NOT_RUN",
    }
    _base.write_o_excl(target, record)
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
    runtime_toolchain_snapshot_sha256: str,
) -> dict[str, Any]:
    state = Path(state_root).resolve(strict=True)
    target = Path(output)
    if target.parent.resolve(strict=True) != state:
        raise _base.FirewallError("DISPATCH_INTENT_OUTSIDE_ATTEMPT_STATE_ROOT")
    if global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED":
        raise _base.FirewallError("GLOBAL_LEASE_NOT_RESERVED")
    if local_record.get("status") != "LOCAL_ATTEMPT_RESERVED":
        raise _base.FirewallError("LOCAL_LEASE_NOT_RESERVED")
    if (
        not _base._valid_hex(runtime_toolchain_snapshot_sha256, 64)
        or global_record.get("runtime_toolchain_snapshot_sha256")
        != runtime_toolchain_snapshot_sha256
        or local_record.get("runtime_toolchain_snapshot_sha256")
        != runtime_toolchain_snapshot_sha256
    ):
        raise _base.FirewallError("DISPATCH_RUNTIME_TOOLCHAIN_MISMATCH")

    record = {
        "schema": "rei-runtime-native-dispatch-intent/v1",
        "status": "DISPATCH_INTENT_WRITTEN",
        "ordinal": 3,
        "firewall_release_head": release_head,
        "firewall_release_tree": release_tree,
        "global_lease_receipt": str(state / "attempt-3.global-lease.json"),
        "global_lease_receipt_sha256": _base.sha256_file(
            state / "attempt-3.global-lease.json"
        ),
        "local_lease_receipt": str(state / "attempt-3.local-lease.json"),
        "local_lease_receipt_sha256": _base.sha256_file(
            state / "attempt-3.local-lease.json"
        ),
        "successor_section0_receipt": str(
            Path(successor_receipt).resolve(strict=True)
        ),
        "successor_section0_receipt_sha256": _base.sha256_file(
            successor_receipt
        ),
        "preflight_receipt": str(Path(preflight_receipt).resolve(strict=True)),
        "preflight_receipt_sha256": _base.sha256_file(preflight_receipt),
        "runtime_toolchain_snapshot_sha256": (
            runtime_toolchain_snapshot_sha256
        ),
        "evidence_root": str(Path(evidence_root).resolve(strict=False)),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "retries_after_outcome": 0,
    }
    _base.write_o_excl(target, record)
    return record


def validate_attempt_receipts(
    *,
    state_root: Path,
    dispatch_intent: Path,
    expected_head: str,
    expected_tree: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    global_record, local_record, dispatch_record = _legacy.validate_attempt_receipts(
        state_root=state_root,
        dispatch_intent=dispatch_intent,
        expected_head=expected_head,
        expected_tree=expected_tree,
    )
    snapshots = [
        global_record.get("runtime_toolchain_snapshot_sha256"),
        local_record.get("runtime_toolchain_snapshot_sha256"),
        dispatch_record.get("runtime_toolchain_snapshot_sha256"),
    ]
    if any(value is not None for value in snapshots):
        if (
            any(not _base._valid_hex(value, 64) for value in snapshots)
            or len(set(snapshots)) != 1
        ):
            raise _base.FirewallError(
                "ATTEMPT_RUNTIME_TOOLCHAIN_SNAPSHOT_MISMATCH"
            )
    return global_record, local_record, dispatch_record
