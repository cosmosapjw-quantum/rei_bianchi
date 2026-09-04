#!/usr/bin/env python3
"""Fixed-authority global lease bound to protection and runtime paths."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Mapping
import urllib.error
import urllib.request

try:
    from .compat import old_common as _old
    from .protection_live import (
        GITHUB_API_BASE,
        GITHUB_API_VERSION,
        GITHUB_AUTHORITY,
        GITHUB_REPOSITORY,
        GLOBAL_ATTEMPT_REF,
        validate_fresh_attempt_ref_protection,
        validate_live_attempt_ref_protection,
    )
except ImportError:
    from compat import old_common as _old  # type: ignore
    from protection_live import (  # type: ignore
        GITHUB_API_BASE,
        GITHUB_API_VERSION,
        GITHUB_AUTHORITY,
        GITHUB_REPOSITORY,
        GLOBAL_ATTEMPT_REF,
        validate_fresh_attempt_ref_protection,
        validate_live_attempt_ref_protection,
    )


def acquire_global_lease(
    *,
    contract: Mapping[str, Any],
    release_head: str,
    successor_receipt_sha256: str,
    preflight_receipt_sha256: str,
    attempt_ref_protection_receipt_sha256: str,
    source_protection_receipt_sha256: str,
    source_protection_receipt: Path,
    live_protection_receipt: Path,
    prelease_toolchain_revalidation_sha256: str,
    runtime_toolchain_snapshot_sha256: str,
    token: str,
    output: Path,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Atomically create the fixed ref and bind protection plus path epochs."""

    for value in (
        successor_receipt_sha256,
        preflight_receipt_sha256,
        attempt_ref_protection_receipt_sha256,
        source_protection_receipt_sha256,
        prelease_toolchain_revalidation_sha256,
        runtime_toolchain_snapshot_sha256,
    ):
        if not _old._valid_hex(value, 64):
            raise _old.FirewallError("GLOBAL_LEASE_EVIDENCE_HASH_INVALID")
    if not token:
        raise _old.FirewallError("GLOBAL_LEASE_TOKEN_UNAVAILABLE")
    if not _old._valid_hex(release_head, 40):
        raise _old.FirewallError("FIREWALL_RELEASE_HEAD_INVALID")
    source_path = Path(source_protection_receipt).resolve(strict=True)
    live_path = Path(live_protection_receipt).resolve(strict=True)
    if _old.sha256_file(source_path) != source_protection_receipt_sha256:
        raise _old.FirewallError("SOURCE_PROTECTION_RECEIPT_HASH_MISMATCH")
    if _old.sha256_file(live_path) != attempt_ref_protection_receipt_sha256:
        raise _old.FirewallError("LIVE_PROTECTION_RECEIPT_HASH_MISMATCH")

    ref = contract["attempt_budget"]["global_lease_ref"]
    if ref != GLOBAL_ATTEMPT_REF:
        raise _old.FirewallError("GLOBAL_LEASE_REF_MISMATCH")
    short_ref = ref.removeprefix("refs/")
    endpoint = f"{GITHUB_API_BASE}/repos/{GITHUB_REPOSITORY}/git/refs"
    request = urllib.request.Request(
        endpoint,
        data=_old.canonical_bytes({"ref": ref, "sha": release_head}),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "rei-runtime-live-protection-path-bound/v1",
        },
    )
    open_request = opener or urllib.request.urlopen
    try:
        with open_request(request, timeout=30) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 422:
            raise _old.FirewallError("STOP_ATTEMPT_ALREADY_RESERVED") from exc
        raise _old.FirewallError(f"STOP_GLOBAL_LEASE_HTTP_{exc.code}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _old.FirewallError(
            "STOP_GLOBAL_LEASE_TRANSPORT_OR_RESPONSE"
        ) from exc
    if (
        status != 201
        or not isinstance(body, dict)
        or body.get("ref") not in {ref, short_ref}
        or body.get("object", {}).get("sha") != release_head
    ):
        raise _old.FirewallError("STOP_REMOTE_LEASE_RESPONSE_MISMATCH")

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
        "source_protection_receipt": str(source_path),
        "source_protection_receipt_sha256": source_protection_receipt_sha256,
        "live_attempt_ref_protection_readback": str(live_path),
        "live_attempt_ref_protection_readback_sha256": (
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
    _old.write_o_excl(output, record)
    return record


def validate_attempt_receipts_live(
    *,
    state_root: Path,
    dispatch_intent: Path,
    expected_head: str,
    expected_tree: str,
    contract: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    global_record, local_record, dispatch_record = _old.validate_attempt_receipts(
        state_root=state_root,
        dispatch_intent=dispatch_intent,
        expected_head=expected_head,
        expected_tree=expected_tree,
    )
    source_path = Path(global_record.get("source_protection_receipt", ""))
    live_path = Path(
        global_record.get("live_attempt_ref_protection_readback", "")
    )
    source_sha = global_record.get("source_protection_receipt_sha256")
    live_sha = global_record.get(
        "live_attempt_ref_protection_readback_sha256"
    )
    runtime_sha = global_record.get("runtime_toolchain_snapshot_sha256")
    if (
        not source_path.is_absolute()
        or not live_path.is_absolute()
        or not _old._valid_hex(source_sha, 64)
        or not _old._valid_hex(live_sha, 64)
        or not _old._valid_hex(runtime_sha, 64)
        or global_record.get("attempt_ref_protection_receipt_sha256")
        != live_sha
        or local_record.get("runtime_toolchain_snapshot_sha256")
        != runtime_sha
        or dispatch_record.get("runtime_toolchain_snapshot_sha256")
        != runtime_sha
    ):
        raise _old.FirewallError("GLOBAL_LEASE_LIVE_PROTECTION_BINDING_MISMATCH")
    source_resolved = source_path.resolve(strict=True)
    live_resolved = live_path.resolve(strict=True)
    if (
        _old.sha256_file(source_resolved) != source_sha
        or _old.sha256_file(live_resolved) != live_sha
    ):
        raise _old.FirewallError("GLOBAL_LEASE_LIVE_PROTECTION_HASH_MISMATCH")
    validate_fresh_attempt_ref_protection(
        source_resolved,
        contract=contract,
        expected_global_ref=GLOBAL_ATTEMPT_REF,
    )
    validate_live_attempt_ref_protection(
        live_resolved,
        source_protection_receipt=source_resolved,
        contract=contract,
        expected_global_ref=GLOBAL_ATTEMPT_REF,
        expected_release_head=expected_head,
    )
    return global_record, local_record, dispatch_record
