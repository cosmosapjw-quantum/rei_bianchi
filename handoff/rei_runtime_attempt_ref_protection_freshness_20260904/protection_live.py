#!/usr/bin/env python3
"""GET-only freshness and live GitHub protection revalidation.

This module never creates or mutates a GitHub ref or ruleset and never imports
the REI production bridge.  All remote authority is fixed to api.github.com.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping
import urllib.error
import urllib.parse
import urllib.request

try:
    from .compat import old_common as _old
except ImportError:
    from compat import old_common as _old  # type: ignore


PACKAGE = Path(__file__).resolve().parent
PACKAGE_RELATIVE = (
    "handoff/rei_runtime_attempt_ref_protection_freshness_20260904"
)
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
PACKAGE_INDEX_PATH = PACKAGE / "PACKAGE_INDEX.json"
PROTECTION_RECEIPT_MAX_AGE_SECONDS = 300
LIVE_READBACK_MAX_AGE_SECONDS = 120
FUTURE_CLOCK_SKEW_SECONDS = 30
GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_HOST = "api.github.com"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
GITHUB_OWNER, GITHUB_REPO = GITHUB_REPOSITORY.split("/", 1)
GITHUB_AUTHORITY = {
    "scheme": "https",
    "api_host": GITHUB_API_HOST,
    "repository": GITHUB_REPOSITORY,
    "api_version": GITHUB_API_VERSION,
}
GLOBAL_ATTEMPT_REF = (
    "refs/heads/attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)
REQUIRED_RULES = {"update", "deletion", "non_fast_forward"}


class ProtectionLiveError(_old.FirewallError):
    """Typed fail-closed error for protection freshness and live state."""


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = _old.load_json_file(path, "LIVE_PROTECTION_CONTRACT_UNREADABLE")
    required = {
        "schema",
        "classification",
        "repository",
        "parent",
        "authority_source",
        "fixed_authority",
        "global_ref",
        "required_rules",
        "protection_receipt_max_age_seconds",
        "live_readback_max_age_seconds",
        "future_clock_skew_seconds",
        "live_revalidation_immediately_before_reservation",
        "live_readback_must_observe_global_ref_absent",
        "live_readback_must_forbid_creation_rule",
        "global_receipt_must_bind_source_and_live_protection_hashes",
        "worker_must_validate_live_protection_hash",
        "native_runtime",
        "claim_ceiling",
    }
    if (
        set(value) != required
        or value.get("schema")
        != "rei-runtime-attempt-ref-protection-freshness/v1"
        or value.get("repository") != GITHUB_REPOSITORY
        or value.get("fixed_authority") != GITHUB_AUTHORITY
        or value.get("global_ref") != GLOBAL_ATTEMPT_REF
        or set(value.get("required_rules", [])) != REQUIRED_RULES
        or value.get("protection_receipt_max_age_seconds")
        != PROTECTION_RECEIPT_MAX_AGE_SECONDS
        or value.get("live_readback_max_age_seconds")
        != LIVE_READBACK_MAX_AGE_SECONDS
        or value.get("future_clock_skew_seconds")
        != FUTURE_CLOCK_SKEW_SECONDS
        or value.get("live_revalidation_immediately_before_reservation")
        is not True
        or value.get("native_runtime") != "NOT_RUN"
    ):
        raise ProtectionLiveError("LIVE_PROTECTION_CONTRACT_INVALID")
    return value


def _parse_utc(value: Any, classification: str) -> datetime:
    if not isinstance(value, str):
        raise ProtectionLiveError(classification)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProtectionLiveError(classification) from exc
    if parsed.tzinfo is None:
        raise ProtectionLiveError(classification)
    return parsed.astimezone(timezone.utc)


def _require_fresh(
    record: Mapping[str, Any],
    *,
    maximum_age_seconds: int,
    classification: str,
    now: datetime | None = None,
) -> None:
    generated = _parse_utc(record.get("generated_at_utc"), classification)
    expires = _parse_utc(record.get("expires_at_utc"), classification)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    age = (current - generated).total_seconds()
    lifetime = (expires - generated).total_seconds()
    if (
        age < -FUTURE_CLOCK_SKEW_SECONDS
        or age > maximum_age_seconds
        or lifetime <= 0
        or lifetime > maximum_age_seconds
        or current > expires
    ):
        raise ProtectionLiveError(classification)


def _canonical_existing_file(path: Path, classification: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise ProtectionLiveError(classification)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProtectionLiveError(classification) from exc
    if not resolved.is_file():
        raise ProtectionLiveError(classification)
    return resolved


def verify_executing_package_binding(repo: Path) -> Path:
    """Bind this successor package and every indexed byte to verified HEAD."""

    root = Path(repo).resolve(strict=True)
    expected = (root / PACKAGE_RELATIVE).resolve(strict=True)
    actual = PACKAGE.resolve(strict=True)
    if actual != expected:
        raise ProtectionLiveError("LIVE_EXECUTING_PACKAGE_OUTSIDE_VERIFIED_RELEASE")
    index = _old.load_json_file(
        PACKAGE_INDEX_PATH, "LIVE_PACKAGE_INDEX_UNREADABLE"
    )
    if (
        set(index) != {"schema", "git_object_format", "entries"}
        or index.get("schema")
        != "rei-runtime-attempt-ref-protection-freshness-package-index/v1"
        or index.get("git_object_format") != "sha1"
        or not isinstance(index.get("entries"), list)
    ):
        raise ProtectionLiveError("LIVE_PACKAGE_INDEX_INVALID")
    index_relative = f"{PACKAGE_RELATIVE}/PACKAGE_INDEX.json"
    if _old.git_text(root, "rev-parse", f"HEAD:{index_relative}") != _old.git_blob_sha1(
        PACKAGE_INDEX_PATH
    ):
        raise ProtectionLiveError("LIVE_PACKAGE_BLOB_MISMATCH:PACKAGE_INDEX.json")
    expected_paths: set[Path] = set()
    for row in index["entries"]:
        if not isinstance(row, dict) or set(row) != {"path", "blob_sha", "role"}:
            raise ProtectionLiveError("LIVE_PACKAGE_INDEX_INVALID")
        raw = row.get("path")
        blob = row.get("blob_sha")
        pure = PurePosixPath(raw) if isinstance(raw, str) else None
        if (
            pure is None
            or pure.is_absolute()
            or ".." in pure.parts
            or str(pure) != raw
            or not _old._valid_hex(blob, 40)
        ):
            raise ProtectionLiveError("LIVE_PACKAGE_INDEX_INVALID")
        relative = Path(raw)
        if relative in expected_paths or relative.name == "PACKAGE_INDEX.json":
            raise ProtectionLiveError("LIVE_PACKAGE_INDEX_INVALID")
        expected_paths.add(relative)
        target = (actual / relative).resolve(strict=True)
        target.relative_to(actual)
        head_blob = _old.git_text(
            root, "rev-parse", f"HEAD:{PACKAGE_RELATIVE}/{raw}"
        )
        if head_blob != blob or _old.git_blob_sha1(target) != blob:
            raise ProtectionLiveError(f"LIVE_PACKAGE_BLOB_MISMATCH:{raw}")
    actual_paths = {
        path.relative_to(actual)
        for path in actual.rglob("*")
        if path.is_file()
        and path.resolve(strict=True) != PACKAGE_INDEX_PATH.resolve(strict=True)
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }
    if actual_paths != expected_paths:
        raise ProtectionLiveError("LIVE_PACKAGE_SCOPE_MISMATCH")
    return actual


def validate_fresh_attempt_ref_protection(
    path: Path,
    *,
    contract: Mapping[str, Any],
    expected_global_ref: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    receipt = _old.validate_attempt_ref_protection(
        path,
        contract=contract,
        expected_global_ref=expected_global_ref,
    )
    _require_fresh(
        receipt,
        maximum_age_seconds=PROTECTION_RECEIPT_MAX_AGE_SECONDS,
        classification="ATTEMPT_REF_PROTECTION_FRESHNESS_INVALID",
        now=now,
    )
    return receipt


def _get_json(
    url: str,
    *,
    token: str,
    opener: Callable[..., Any],
) -> tuple[int, bytes, Any]:
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "rei-runtime-live-protection/v1",
        },
    )
    try:
        with opener(request, timeout=30) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
    except OSError as exc:
        raise ProtectionLiveError("LIVE_PROTECTION_TRANSPORT_ERROR") from exc
    try:
        body = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProtectionLiveError("LIVE_PROTECTION_RESPONSE_INVALID") from exc
    return status, raw, body


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _ruleset_rule_types(details: Mapping[str, Any]) -> set[str]:
    rows = details.get("rules")
    if not isinstance(rows, list):
        raise ProtectionLiveError("LIVE_RULESET_DETAILS_INVALID")
    result: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("type"), str):
            raise ProtectionLiveError("LIVE_RULESET_DETAILS_INVALID")
        result.add(row["type"])
    return result


def revalidate_attempt_ref_protection_live(
    *,
    source_protection_receipt: Path,
    contract: Mapping[str, Any],
    expected_global_ref: str,
    expected_release_head: str,
    token: str,
    output: Path,
    opener: Callable[..., Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Re-read effective GitHub rules and exact ref absence by GET only."""

    if not token:
        raise ProtectionLiveError("LIVE_PROTECTION_TOKEN_UNAVAILABLE")
    if expected_global_ref != GLOBAL_ATTEMPT_REF:
        raise ProtectionLiveError("LIVE_PROTECTION_GLOBAL_REF_MISMATCH")
    source_path = _canonical_existing_file(
        source_protection_receipt, "ATTEMPT_REF_PROTECTION_RECEIPT_UNREADABLE"
    )
    validate_fresh_attempt_ref_protection(
        source_path,
        contract=contract,
        expected_global_ref=expected_global_ref,
        now=now,
    )
    source_sha = _old.sha256_file(source_path)
    open_request = opener or urllib.request.urlopen
    branch = expected_global_ref.removeprefix("refs/heads/")
    encoded_branch = urllib.parse.quote(branch, safe="")
    rules_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/rules/branches/"
        f"{encoded_branch}"
    )
    rules_status, rules_raw, rules_body = _get_json(
        rules_url, token=token, opener=open_request
    )
    if rules_status != 200 or not isinstance(rules_body, list):
        raise ProtectionLiveError(
            f"LIVE_PROSPECTIVE_BRANCH_RULES_HTTP_{rules_status}"
        )
    active_types: set[str] = set()
    contributing_ids: set[int] = set()
    for row in rules_body:
        if not isinstance(row, dict) or not isinstance(row.get("type"), str):
            raise ProtectionLiveError("LIVE_PROSPECTIVE_BRANCH_RULES_INVALID")
        rule_type = row["type"]
        active_types.add(rule_type)
        ruleset_id = row.get("ruleset_id")
        if rule_type in REQUIRED_RULES:
            if not isinstance(ruleset_id, int) or ruleset_id <= 0:
                raise ProtectionLiveError(
                    "LIVE_PROSPECTIVE_BRANCH_RULESET_ID_INVALID"
                )
            contributing_ids.add(ruleset_id)
    if not REQUIRED_RULES.issubset(active_types):
        raise ProtectionLiveError("LIVE_PROSPECTIVE_BRANCH_RULES_MISSING")
    if "creation" in active_types:
        raise ProtectionLiveError("LIVE_PROTECTION_CREATION_RULE_FORBIDDEN")

    detail_hashes: list[dict[str, Any]] = []
    supplied_types: set[str] = set()
    for ruleset_id in sorted(contributing_ids):
        detail_url = (
            f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/rulesets/"
            f"{ruleset_id}"
        )
        detail_status, detail_raw, detail_body = _get_json(
            detail_url, token=token, opener=open_request
        )
        if detail_status != 200 or not isinstance(detail_body, dict):
            raise ProtectionLiveError(
                f"LIVE_RULESET_DETAILS_HTTP_{detail_status}:{ruleset_id}"
            )
        condition = detail_body.get("conditions", {}).get("ref_name", {})
        detail_types = _ruleset_rule_types(detail_body)
        if (
            detail_body.get("target") != "branch"
            or detail_body.get("enforcement") != "active"
            or detail_body.get("bypass_actors") != []
            or "refs/heads/attempt-ledger/**" not in condition.get("include", [])
            or condition.get("exclude") not in ([], None)
            or "creation" in detail_types
        ):
            raise ProtectionLiveError("LIVE_RULESET_DETAILS_INVALID")
        supplied_types.update(detail_types & REQUIRED_RULES)
        detail_hashes.append(
            {"ruleset_id": ruleset_id, "response_sha256": _sha256_bytes(detail_raw)}
        )
    if supplied_types != REQUIRED_RULES:
        raise ProtectionLiveError("LIVE_RULESET_DETAILS_REQUIRED_RULES_MISSING")

    ref_path = urllib.parse.quote("heads/" + branch, safe="/")
    ref_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/ref/{ref_path}"
    )
    ref_status, ref_raw, _ = _get_json(
        ref_url, token=token, opener=open_request
    )
    if ref_status != 404:
        raise ProtectionLiveError(
            f"LIVE_GLOBAL_ATTEMPT_REF_NOT_ABSENT_HTTP_{ref_status}"
        )

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    record = {
        "schema": "rei-runtime-live-attempt-ref-protection-readback/v1",
        "status": "PASS_LIVE_ATTEMPT_REF_SERVER_PROTECTION",
        "generated_at_utc": current.isoformat(),
        "expires_at_utc": (
            current + timedelta(seconds=LIVE_READBACK_MAX_AGE_SECONDS)
        ).isoformat(),
        "authority": GITHUB_AUTHORITY,
        "repository": GITHUB_REPOSITORY,
        "global_ref": expected_global_ref,
        "expected_target": expected_release_head,
        "prospective_branch": branch,
        "source_protection_receipt": str(source_path),
        "source_protection_receipt_sha256": source_sha,
        "prospective_branch_rules_http_status": rules_status,
        "prospective_branch_rules_response_sha256": _sha256_bytes(rules_raw),
        "contributing_ruleset_ids": sorted(contributing_ids),
        "ruleset_detail_response_sha256s": detail_hashes,
        "ruleset_details_response_sha256": _sha256_bytes(
            _old.canonical_bytes(detail_hashes)
        ),
        "global_ref_http_status": ref_status,
        "global_ref_absent": True,
        "global_ref_absence_response_sha256": _sha256_bytes(ref_raw),
        "active_rules": sorted(REQUIRED_RULES),
        "update_forbidden": True,
        "deletion_forbidden": True,
        "non_fast_forward_forbidden": True,
        "creation_forbidden": False,
        "bypass_actors": [],
        "authorization_effect": "NONE",
        "mutation_effect": "NONE",
        "native_runtime": "NOT_RUN",
    }
    target = _old.write_o_excl(output, record)
    return {
        **record,
        "receipt": str(target),
        "receipt_sha256": _old.sha256_file(target),
    }


def validate_live_attempt_ref_protection(
    path: Path,
    *,
    source_protection_receipt: Path,
    contract: Mapping[str, Any],
    expected_global_ref: str,
    expected_release_head: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    source_path = _canonical_existing_file(
        source_protection_receipt, "ATTEMPT_REF_PROTECTION_RECEIPT_UNREADABLE"
    )
    validate_fresh_attempt_ref_protection(
        source_path,
        contract=contract,
        expected_global_ref=expected_global_ref,
        now=now,
    )
    receipt = _old.load_json_file(
        path, "LIVE_ATTEMPT_REF_PROTECTION_RECEIPT_UNREADABLE"
    )
    _require_fresh(
        receipt,
        maximum_age_seconds=LIVE_READBACK_MAX_AGE_SECONDS,
        classification="LIVE_PROTECTION_FRESHNESS_INVALID",
        now=now,
    )
    hashes = (
        receipt.get("prospective_branch_rules_response_sha256"),
        receipt.get("ruleset_details_response_sha256"),
        receipt.get("global_ref_absence_response_sha256"),
    )
    if (
        receipt.get("schema")
        != "rei-runtime-live-attempt-ref-protection-readback/v1"
        or receipt.get("status")
        != "PASS_LIVE_ATTEMPT_REF_SERVER_PROTECTION"
        or receipt.get("authority") != GITHUB_AUTHORITY
        or receipt.get("repository") != GITHUB_REPOSITORY
        or receipt.get("global_ref") != expected_global_ref
        or receipt.get("expected_target") != expected_release_head
        or receipt.get("source_protection_receipt") != str(source_path)
        or receipt.get("source_protection_receipt_sha256")
        != _old.sha256_file(source_path)
        or receipt.get("prospective_branch_rules_http_status") != 200
        or receipt.get("global_ref_http_status") != 404
        or receipt.get("global_ref_absent") is not True
        or set(receipt.get("active_rules", [])) != REQUIRED_RULES
        or receipt.get("update_forbidden") is not True
        or receipt.get("deletion_forbidden") is not True
        or receipt.get("non_fast_forward_forbidden") is not True
        or receipt.get("creation_forbidden") is not False
        or receipt.get("bypass_actors") != []
        or receipt.get("authorization_effect") != "NONE"
        or receipt.get("mutation_effect") != "NONE"
        or receipt.get("native_runtime") != "NOT_RUN"
        or not all(_old._valid_hex(value, 64) for value in hashes)
    ):
        raise ProtectionLiveError("LIVE_PROTECTION_RECEIPT_MISMATCH")
    return receipt
