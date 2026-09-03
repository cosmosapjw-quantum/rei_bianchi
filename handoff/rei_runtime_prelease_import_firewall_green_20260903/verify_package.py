#!/usr/bin/env python3
"""Independent verifier for import ordering and authority binding."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

try:
    from .common_v2 import (
        FirewallError,
        GITHUB_API_BASE,
        GITHUB_REPOSITORY,
        PACKAGE,
        load_contract,
        verify_package_index,
    )
    from . import verify_package_legacy as _legacy
except ImportError:
    from common_v2 import (  # type: ignore
        FirewallError,
        GITHUB_API_BASE,
        GITHUB_REPOSITORY,
        PACKAGE,
        load_contract,
        verify_package_index,
    )
    import verify_package_legacy as _legacy  # type: ignore


def verify_authority_boundary() -> dict[str, object]:
    preflight = PACKAGE / "successor_section0_preflight.py"
    controller = PACKAGE / "successor_runtime_controller.py"
    common_v2 = PACKAGE / "common_v2.py"
    for path in (preflight, controller, common_v2):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    preflight_text = preflight.read_text(encoding="utf-8")
    controller_text = controller.read_text(encoding="utf-8")
    common_text = common_v2.read_text(encoding="utf-8")
    if "--api-base" in preflight_text or "--api-base" in controller_text:
        raise FirewallError("CONFIGURABLE_GITHUB_AUTHORITY_PRESENT")
    for token in (
        "verify_executing_package_binding",
        "revalidate_successor_toolchain",
        "validate_attempt_ref_protection",
    ):
        if token not in preflight_text + controller_text:
            raise FirewallError(f"AUTHORITY_BINDING_CALL_ABSENT:{token}")
    for token in (
        "EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE",
        "EXECUTING_PACKAGE_BLOB_MISMATCH",
        "READ_ONLY_PREFLIGHT_FRESHNESS_INVALID",
        "ATTEMPT_REF_PROTECTION_RECEIPT_MISMATCH",
    ):
        if token not in common_text:
            raise FirewallError(f"AUTHORITY_BINDING_GUARD_ABSENT:{token}")
    return {
        "fixed_api_base": GITHUB_API_BASE,
        "fixed_repository": GITHUB_REPOSITORY,
        "public_authority_override": False,
        "executing_package_head_binding": True,
        "prelease_full_toolchain_revalidation": True,
        "attempt_ref_protection_required": True,
    }


def main() -> int:
    try:
        verify_package_index()
        contract = load_contract()
        import_boundary = _legacy.verify_source_boundary()
        authority_boundary = verify_authority_boundary()
    except FirewallError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_PACKAGE_VERIFIER_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(
        json.dumps(
            {
                "status": contract["success_status"],
                "package": str(PACKAGE),
                "import_boundary": import_boundary,
                "authority_boundary": authority_boundary,
                "native_runtime": "NOT_RUN",
                "authority_effect": "NONE",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
