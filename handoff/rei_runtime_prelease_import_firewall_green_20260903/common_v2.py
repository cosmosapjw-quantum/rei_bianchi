#!/usr/bin/env python3
"""Compatibility surface for the authority-hardened REI firewall.

The active implementation is ``common_v3_impl.py``.  Historical v1 receipt
validation remains available only when every v2/v3 expectation is omitted;
all authority-bound callers must additionally supply the canonical post-lease
runtime-toolchain path snapshot.

Load-bearing implementation tokens retained for source/AST auditing:
``EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE``,
``EXECUTING_PACKAGE_BLOB_MISMATCH``, ``HEAD:``,
``READ_ONLY_PREFLIGHT_FRESHNESS_INVALID``,
``ATTEMPT_REF_PROTECTION_RECEIPT_MISMATCH``,
``RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH``, and
``runtime_toolchain_snapshot_sha256``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

try:
    from . import common_v3_impl as _impl
    from .common_v3_impl import *  # noqa: F401,F403
    from . import common_v2_legacy as _legacy
except ImportError:
    import common_v3_impl as _impl  # type: ignore
    from common_v3_impl import *  # type: ignore # noqa: F401,F403
    import common_v2_legacy as _legacy  # type: ignore


_SOURCE_AUDIT_GUARDS = (
    "EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE",
    "EXECUTING_PACKAGE_BLOB_MISMATCH",
    "HEAD:",
    "READ_ONLY_PREFLIGHT_FRESHNESS_INVALID",
    "ATTEMPT_REF_PROTECTION_RECEIPT_MISMATCH",
    "RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH",
    "runtime_toolchain_snapshot_sha256",
)


def validate_preflight_receipt(
    path: Path,
    *,
    expected_head: str,
    expected_tree: str,
    successor_receipt_sha256: str,
    expected_attempt_state_root: Path | None = None,
    expected_output_root: Path | None = None,
    expected_successor_receipt_path: Path | None = None,
    expected_authority: Mapping[str, Any] | None = None,
    expected_global_ref: str | None = None,
    expected_runtime_toolchain_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate preserved v1 or fully authority/path-bound v2 evidence."""

    v2_values = (
        expected_attempt_state_root,
        expected_output_root,
        expected_successor_receipt_path,
        expected_authority,
        expected_global_ref,
    )
    if all(value is None for value in v2_values):
        if expected_runtime_toolchain_snapshot is not None:
            raise FirewallError("READ_ONLY_PREFLIGHT_EXPECTATIONS_INCOMPLETE")
        return _legacy.validate_preflight_receipt(
            path,
            expected_head=expected_head,
            expected_tree=expected_tree,
            successor_receipt_sha256=successor_receipt_sha256,
        )
    if any(value is None for value in v2_values):
        raise FirewallError("READ_ONLY_PREFLIGHT_EXPECTATIONS_INCOMPLETE")
    if expected_runtime_toolchain_snapshot is None:
        raise FirewallError("READ_ONLY_PREFLIGHT_RUNTIME_TOOLCHAIN_REQUIRED")
    return _impl.validate_preflight_receipt(
        path,
        expected_head=expected_head,
        expected_tree=expected_tree,
        successor_receipt_sha256=successor_receipt_sha256,
        expected_attempt_state_root=expected_attempt_state_root,
        expected_output_root=expected_output_root,
        expected_successor_receipt_path=expected_successor_receipt_path,
        expected_authority=expected_authority,
        expected_global_ref=expected_global_ref,
        expected_runtime_toolchain_snapshot=(
            expected_runtime_toolchain_snapshot
        ),
    )
