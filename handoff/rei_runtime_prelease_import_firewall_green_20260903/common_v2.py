#!/usr/bin/env python3
"""Authority-binding hardening for the REI one-attempt firewall.

The production bridge is never imported here.  This layer fixes the remote
GitHub authority, cross-binds the executing package to the verified Git HEAD,
validates path- and authority-bound preflight evidence, re-attests the complete
successor toolchain immediately before reservation, and requires an independent
server-side ref-protection receipt.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
from typing import Any, Mapping
import urllib.error
import urllib.request

try:
    from . import common as _base
    from .common import *  # noqa: F401,F403
    from . import common_v2_legacy as _legacy
except ImportError:
    import common as _base  # type: ignore
    from common import *  # type: ignore # noqa: F401,F403
    import common_v2_legacy as _legacy  # type: ignore


PACKAGE = Path(__file__).resolve().parent
FIREWALL_PACKAGE_RELATIVE = (
    "handoff/rei_runtime_prelease_import_firewall_green_20260903"
)
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_HOST = "api.github.com"
GITHUB_API_SCHEME = "https"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
GITHUB_AUTHORITY: dict[str, str] = {
    "scheme": GITHUB_API_SCHEME,
    "api_host": GITHUB_API_HOST,
    "repository": GITHUB_REPOSITORY,
    "api_version": GITHUB_API_VERSION,
}
GLOBAL_ATTEMPT_REF = (
    "refs/heads/attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)
PREFLIGHT_MAX_AGE_SECONDS = 1800


def load_contract(path: Path = PACKAGE / "CONTRACT.json") -> dict[str, Any]:
    value = _base.load_json_file(path, "FIREWALL_CONTRACT_UNREADABLE")
    required = {
        "schema",
        "classification",
        "repository",
        "immutable_parent",
        "source_lineage",
        "successor_section0",
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
    return value


def verify_executing_package_binding(
    repo: Path,
    contract: Mapping[str, Any] | None = None,
) -> Path:
    """Require the executing package to be the exact package in verified HEAD."""

    root = Path(repo).resolve(strict=True)
    expected = (root / FIREWALL_PACKAGE_RELATIVE).resolve(strict=True)
    actual = PACKAGE.resolve(strict=True)
    if actual != expected:
        raise _base.FirewallError(
            "EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE"
        )
    _base.verify_package_index(actual, actual / "PACKAGE_INDEX.json")
    index = _base.load_json_file(
        actual / "PACKAGE_INDEX.json",
        "FIREWALL_PACKAGE_INDEX_UNREADABLE",
    )
    index_relative = f"{FIREWALL_PACKAGE_RELATIVE}/PACKAGE_INDEX.json"
    if _base.git_text(root, "rev-parse", f"HEAD:{index_relative}") != _base.git_blob_sha1(
        actual / "PACKAGE_INDEX.json"
    ):
        raise _base.FirewallError(
            "EXECUTING_PACKAGE_BLOB_MISMATCH:PACKAGE_INDEX.json"
        )
    for row in index.get("entries", []):
        if not isinstance(row, dict):
            raise _base.FirewallError("FIREWALL_PACKAGE_INDEX_INVALID")
        raw = row.get("path")
        blob = row.get("blob_sha")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw
            or not _base._valid_hex(blob, 40)
        ):
            raise _base.FirewallError("FIREWALL_PACKAGE_INDEX_INVALID")
        target = (actual / raw).resolve(strict=True)
        target.relative_to(actual)
        relative = f"{FIREWALL_PACKAGE_RELATIVE}/{raw}"
        head_blob = _base.git_text(root, "rev-parse", f"HEAD:{relative}")
        if head_blob != blob or _base.git_blob_sha1(target) != blob:
            raise _base.FirewallError(
                f"EXECUTING_PACKAGE_BLOB_MISMATCH:{raw}"
            )
    return actual


def _parse_utc(value: Any, classification: str) -> datetime:
    if not isinstance(value, str):
        raise _base.FirewallError(classification)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _base.FirewallError(classification) from exc
    if parsed.tzinfo is None:
        raise _base.FirewallError(classification)
    return parsed.astimezone(timezone.utc)


def _canonical_existing(path: Path, classification: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise _base.FirewallError(classification)
    try:
        return candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise _base.FirewallError(classification) from exc


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
) -> dict[str, Any]:
    receipt = _base.load_json_file(
        path, "READ_ONLY_PREFLIGHT_RECEIPT_UNREADABLE"
    )
    state = _canonical_existing(
        expected_attempt_state_root, "ATTEMPT_STATE_ROOT_UNAVAILABLE"
    )
    output = _canonical_existing(
        expected_output_root, "OUTPUT_ROOT_UNAVAILABLE"
    )
    successor = _canonical_existing(
        expected_successor_receipt_path,
        "SUCCESSOR_SECTION0_UNREADABLE",
    )
    if (
        receipt.get("schema")
        != "rei-runtime-prelease-import-firewall-preflight-receipt/v2"
        or receipt.get("status") != "PASS_READ_ONLY_STATIC_PREFLIGHT"
        or receipt.get("firewall_release")
        != {"commit": expected_head, "tree": expected_tree}
        or receipt.get("successor_section0_receipt_sha256")
        != successor_receipt_sha256
        or receipt.get("successor_section0_receipt") != str(successor)
        or receipt.get("authority") != dict(expected_authority)
        or receipt.get("attempt_state_root") != str(state)
        or receipt.get("output_root") != str(output)
    ):
        raise _base.FirewallError("READ_ONLY_PREFLIGHT_RECEIPT_MISMATCH")
    if Path(path).resolve(strict=True).parent != output:
        raise _base.FirewallError("READ_ONLY_PREFLIGHT_OUTPUT_ROOT_MISMATCH")

    generated = _parse_utc(
        receipt.get("generated_at_utc"),
        "READ_ONLY_PREFLIGHT_FRESHNESS_INVALID",
    )
    expires = _parse_utc(
        receipt.get("expires_at_utc"),
        "READ_ONLY_PREFLIGHT_FRESHNESS_INVALID",
    )
    now = datetime.now(timezone.utc)
    age = (now - generated).total_seconds()
    lifetime = (expires - generated).total_seconds()
    if (
        age < -300
        or age > PREFLIGHT_MAX_AGE_SECONDS
        or lifetime <= 0
        or lifetime > PREFLIGHT_MAX_AGE_SECONDS
        or now > expires
    ):
        raise _base.FirewallError("READ_ONLY_PREFLIGHT_FRESHNESS_INVALID")

    observations = receipt.get("global_ref_observations")
    if not isinstance(observations, list) or len(observations) != 2:
        raise _base.FirewallError(
            "READ_ONLY_PREFLIGHT_REF_OBSERVATIONS_INVALID"
        )
    for ordinal, observation in enumerate(observations, start=1):
        if (
            not isinstance(observation, dict)
            or observation.get("status")
            != "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED"
            or observation.get("ordinal") != ordinal
            or observation.get("method") != "GET"
            or observation.get("http_status") != 404
            or observation.get("authority") != dict(expected_authority)
            or observation.get("api_host")
            != expected_authority.get("api_host")
            or observation.get("repository")
            != expected_authority.get("repository")
            or observation.get("ref") != expected_global_ref
            or observation.get("expected_target") != expected_head
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
        "executing_package_bound_to_head": True,
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


def validate_attempt_ref_protection(
    path: Path,
    *,
    contract: Mapping[str, Any],
    expected_global_ref: str,
) -> dict[str, Any]:
    receipt = _base.load_json_file(
        path, "ATTEMPT_REF_PROTECTION_RECEIPT_UNREADABLE"
    )
    rule = contract["attempt_ref_protection"]
    active = receipt.get("active_rules")
    if (
        receipt.get("schema") != rule["required_schema"]
        or receipt.get("status") != rule["required_status"]
        or receipt.get("authority") != GITHUB_AUTHORITY
        or receipt.get("repository") != GITHUB_REPOSITORY
        or receipt.get("global_ref") != expected_global_ref
        or receipt.get("target_pattern") != rule["target_pattern"]
        or receipt.get("prospective_branch_rules_http_status") != 200
        or not isinstance(active, list)
        or set(active) != set(rule["required_rules"])
        or receipt.get("update_forbidden") is not True
        or receipt.get("deletion_forbidden") is not True
        or receipt.get("non_fast_forward_forbidden") is not True
        or receipt.get("bypass_actors") != []
        or receipt.get("authorization_effect") != "NONE"
        or receipt.get("mutation_effect") != "NONE"
    ):
        raise _base.FirewallError(
            "ATTEMPT_REF_PROTECTION_RECEIPT_MISMATCH"
        )
    return receipt


def _require_locked_path(
    path: Path,
    *,
    executable: bool,
    classification: str,
) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise _base.FirewallError(classification)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise _base.FirewallError(classification) from exc
    if not resolved.is_file() or (executable and not os.access(resolved, os.X_OK)):
        raise _base.FirewallError(classification)
    return resolved


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
    """Re-run the complete 13-field emitter immediately before reservation."""

    root = Path(repo).resolve(strict=True)
    python_path = _require_locked_path(
        python, executable=True, classification="SUCCESSOR_PYTHON_UNAVAILABLE"
    )
    rustc_path = _require_locked_path(
        rustc, executable=True, classification="SUCCESSOR_RUSTC_UNAVAILABLE"
    )
    mpfr_path = _require_locked_path(
        mpfr, executable=False, classification="SUCCESSOR_MPFR_UNAVAILABLE"
    )
    gmp_path = _require_locked_path(
        gmp, executable=False, classification="SUCCESSOR_GMP_UNAVAILABLE"
    )
    cc_path = _require_locked_path(
        cc, executable=True, classification="SUCCESSOR_CC_UNAVAILABLE"
    )
    ld_path = _require_locked_path(
        ld, executable=True, classification="SUCCESSOR_LD_UNAVAILABLE"
    )
    rule = contract["successor_section0"]
    emitter = (root / rule["emitter_path"]).resolve(strict=True)
    policy = (root / rule["policy_path"]).resolve(strict=True)
    target = Path(output)
    if not target.is_absolute() or target.is_symlink() or target.exists():
        raise _base.FirewallError(
            "PRELEASE_TOOLCHAIN_REVALIDATION_OUTPUT_INVALID"
        )
    target.parent.resolve(strict=True)
    command = [
        str(python_path),
        "-I",
        "-S",
        "-B",
        str(emitter),
        "--policy",
        str(policy),
        "--rustc",
        str(rustc_path),
        "--python",
        str(python_path),
        "--mpfr",
        str(mpfr_path),
        "--gmp",
        str(gmp_path),
        "--cc",
        str(cc_path),
        "--ld",
        str(ld_path),
        "--output",
        str(target),
    ]
    completed = subprocess.run(
        command,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C", "LANG": "C"},
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise _base.FirewallError(
            "PRELEASE_TOOLCHAIN_REVALIDATION_FAILED:" + detail
        )
    original = _base.validate_successor_receipt(
        original_successor_receipt, contract
    )
    fresh = _base.validate_successor_receipt(target, contract)
    if (
        fresh.get("observed_toolchain") != original.get("observed_toolchain")
        or fresh.get("host_epoch_fingerprint")
        != original.get("host_epoch_fingerprint")
        or fresh.get("host_context") != original.get("host_context")
    ):
        raise _base.FirewallError(
            "PRELEASE_TOOLCHAIN_REVALIDATION_DRIFT"
        )
    return {
        "status": "PASS_PRELEASE_TOOLCHAIN_REVALIDATION",
        "receipt": str(target.resolve(strict=True)),
        "receipt_sha256": _base.sha256_file(target),
        "observed_toolchain": fresh["observed_toolchain"],
    }


def acquire_global_lease(
    *,
    contract: Mapping[str, Any],
    release_head: str,
    successor_receipt_sha256: str,
    preflight_receipt_sha256: str,
    attempt_ref_protection_receipt_sha256: str,
    prelease_toolchain_revalidation_sha256: str,
    token: str,
    output: Path,
) -> dict[str, Any]:
    """Create the fixed GitHub ref; no caller-selected authority is accepted."""

    budget = contract["attempt_budget"]
    for value in (
        successor_receipt_sha256,
        preflight_receipt_sha256,
        attempt_ref_protection_receipt_sha256,
        prelease_toolchain_revalidation_sha256,
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
            "User-Agent": "rei-runtime-authority-binding/v2",
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
        "mutation_policy": "CREATE_ONLY_PROTECTED_NO_UPDATE_NO_DELETE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "native_runtime": "NOT_RUN",
    }
    _base.write_o_excl(output, record)
    return record


def validate_attempt_receipts(
    *,
    state_root: Path,
    dispatch_intent: Path,
    expected_head: str,
    expected_tree: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    global_record, local_record, dispatch_record = (
        _legacy.validate_attempt_receipts(
            state_root=state_root,
            dispatch_intent=dispatch_intent,
            expected_head=expected_head,
            expected_tree=expected_tree,
        )
    )
    if (
        global_record.get("schema")
        != "rei-runtime-global-attempt-lease-receipt/v4"
        or global_record.get("authority") != GITHUB_AUTHORITY
        or not _base._valid_hex(
            global_record.get("attempt_ref_protection_receipt_sha256"), 64
        )
        or not _base._valid_hex(
            global_record.get("prelease_toolchain_revalidation_sha256"), 64
        )
    ):
        raise _base.FirewallError("GLOBAL_LEASE_AUTHORITY_BINDING_MISMATCH")
    return global_record, local_record, dispatch_record
