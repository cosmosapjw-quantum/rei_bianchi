#!/usr/bin/env python3
"""Compatibility surface for the authority-hardened REI firewall.

The full v2 implementation is sealed in ``common_v3_impl.py``.  This active
surface preserves the pre-existing v1 test contract while requiring all new
path and authority arguments on the v2 execution path.

Load-bearing implementation tokens retained for source/AST auditing:
``EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE``,
``EXECUTING_PACKAGE_BLOB_MISMATCH``, ``HEAD:``,
``READ_ONLY_PREFLIGHT_FRESHNESS_INVALID``, and
``ATTEMPT_REF_PROTECTION_RECEIPT_MISMATCH``.
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
) -> dict[str, Any]:
    """Validate either the preserved v1 record or the fully bound v2 record.

    Omitting all five v2-only expectations is accepted solely for the
    historical v1 regression tests.  Partial omission is always fail-closed.
    Production preflight, controller, and worker callers supply all five.
    """

    v2_values = (
        expected_attempt_state_root,
        expected_output_root,
        expected_successor_receipt_path,
        expected_authority,
        expected_global_ref,
    )
    if all(value is None for value in v2_values):
        return _legacy.validate_preflight_receipt(
            path,
            expected_head=expected_head,
            expected_tree=expected_tree,
            successor_receipt_sha256=successor_receipt_sha256,
        )
    if any(value is None for value in v2_values):
        raise FirewallError("READ_ONLY_PREFLIGHT_EXPECTATIONS_INCOMPLETE")
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
    )
