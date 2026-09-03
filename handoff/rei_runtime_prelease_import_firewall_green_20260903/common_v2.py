#!/usr/bin/env python3
"""Hostile-audit hardening layer for the REI firewall primitives.

The original GREEN primitives remain preserved in ``common.py``. This module
adds strict semantic receipt checks and exact cross-receipt binding without
introducing any production-module import.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from . import common as _base
    from .common import *  # noqa: F401,F403
except ImportError:
    import common as _base  # type: ignore
    from common import *  # type: ignore # noqa: F401,F403


GLOBAL_ATTEMPT_REF = (
    "refs/heads/attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)


def validate_preflight_receipt(
    path: Path,
    *,
    expected_head: str,
    expected_tree: str,
    successor_receipt_sha256: str,
) -> dict[str, Any]:
    receipt = _base.load_json_file(
        path, "READ_ONLY_PREFLIGHT_RECEIPT_UNREADABLE"
    )
    if (
        receipt.get("schema")
        != "rei-runtime-prelease-import-firewall-preflight-receipt/v1"
        or receipt.get("status") != "PASS_READ_ONLY_STATIC_PREFLIGHT"
        or receipt.get("firewall_release")
        != {"commit": expected_head, "tree": expected_tree}
        or receipt.get("successor_section0_receipt_sha256")
        != successor_receipt_sha256
    ):
        raise _base.FirewallError("READ_ONLY_PREFLIGHT_RECEIPT_MISMATCH")

    observations = receipt.get("global_ref_observations")
    if not isinstance(observations, list) or len(observations) != 2:
        raise _base.FirewallError(
            "READ_ONLY_PREFLIGHT_REF_OBSERVATIONS_INVALID"
        )
    for observation in observations:
        if (
            not isinstance(observation, dict)
            or observation.get("status")
            != "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED"
            or observation.get("authorization_effect") != "NONE"
            or observation.get("global_lease_acquired") is not False
        ):
            raise _base.FirewallError(
                "READ_ONLY_PREFLIGHT_REF_OBSERVATIONS_INVALID"
            )

    expected_static_checks = {
        "production_module_loaded": False,
        "standalone_clone_verified": True,
        "pinned_source_bytes_verified": True,
        "closed_runtime_package_verified": True,
    }
    if receipt.get("static_checks") != expected_static_checks:
        raise _base.FirewallError(
            "READ_ONLY_PREFLIGHT_STATIC_CHECKS_INVALID"
        )

    attempt = receipt.get("attempt_state")
    if (
        not isinstance(attempt, dict)
        or attempt.get("global_lease_acquired") is not False
        or attempt.get("local_lease_created") is not False
        or attempt.get("dispatch_intent_created") is not False
        or attempt.get("remaining_attempts") != 1
        or attempt.get("absence_is_authorization") is not False
        or receipt.get("native_runtime") != "NOT_RUN"
    ):
        raise _base.FirewallError(
            "READ_ONLY_PREFLIGHT_ATTEMPT_STATE_INVALID"
        )
    return receipt


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
    expected_dispatch = state / "attempt-3.dispatch-intent.json"
    raw_dispatch = Path(dispatch_intent)
    if (
        not raw_dispatch.is_absolute()
        or raw_dispatch.is_symlink()
        or raw_dispatch != expected_dispatch
    ):
        raise _base.FirewallError("DISPATCH_INTENT_PATH_MISMATCH")
    dispatch_path = expected_dispatch.resolve(strict=True)

    global_record = _base.load_json_file(
        global_path, "GLOBAL_LEASE_RECEIPT_UNREADABLE"
    )
    local_record = _base.load_json_file(
        local_path, "LOCAL_LEASE_RECEIPT_UNREADABLE"
    )
    dispatch_record = _base.load_json_file(
        dispatch_path, "DISPATCH_INTENT_RECEIPT_UNREADABLE"
    )

    global_sha = _base.sha256_file(global_path)
    local_sha = _base.sha256_file(local_path)
    successor_sha = global_record.get("successor_section0_receipt_sha256")
    preflight_sha = global_record.get("preflight_receipt_sha256")

    if (
        global_record.get("status") != "GLOBAL_ATTEMPT_RESERVED"
        or global_record.get("ref") != GLOBAL_ATTEMPT_REF
        or global_record.get("target_commit") != expected_head
        or global_record.get("target_relation")
        != "EXACT_FIREWALL_RELEASE_HEAD"
        or not _base._valid_hex(successor_sha, 64)
        or not _base._valid_hex(preflight_sha, 64)
    ):
        raise _base.FirewallError("GLOBAL_LEASE_RECEIPT_MISMATCH")

    cross_successor = {
        successor_sha,
        local_record.get("successor_section0_receipt_sha256"),
        dispatch_record.get("successor_section0_receipt_sha256"),
    }
    cross_preflight = {
        preflight_sha,
        local_record.get("preflight_receipt_sha256"),
        dispatch_record.get("preflight_receipt_sha256"),
    }
    if len(cross_successor) != 1 or len(cross_preflight) != 1:
        raise _base.FirewallError("ATTEMPT_RECEIPT_CROSS_HASH_MISMATCH")

    if (
        local_record.get("status") != "LOCAL_ATTEMPT_RESERVED"
        or local_record.get("firewall_release_head") != expected_head
        or local_record.get("firewall_release_tree") != expected_tree
        or local_record.get("global_lease_ref") != GLOBAL_ATTEMPT_REF
        or local_record.get("global_lease_receipt_sha256") != global_sha
    ):
        raise _base.FirewallError("LOCAL_LEASE_RECEIPT_MISMATCH")

    if (
        dispatch_record.get("status") != "DISPATCH_INTENT_WRITTEN"
        or dispatch_record.get("firewall_release_head") != expected_head
        or dispatch_record.get("firewall_release_tree") != expected_tree
        or dispatch_record.get("global_lease_receipt_sha256") != global_sha
        or dispatch_record.get("local_lease_receipt_sha256") != local_sha
        or dispatch_record.get("retries_after_outcome") != 0
    ):
        raise _base.FirewallError("DISPATCH_INTENT_RECEIPT_MISMATCH")

    return global_record, local_record, dispatch_record
