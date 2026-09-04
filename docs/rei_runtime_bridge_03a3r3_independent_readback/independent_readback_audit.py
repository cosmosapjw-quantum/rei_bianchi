#!/usr/bin/env python3
"""Independent GET-only audit of the REI attempt-ledger ruleset state.

This module validates the administrator's three-record bundle, independently
re-reads GitHub server state, writes a retrospective audit receipt, and then
writes a new controller-compatible source-protection receipt.  It has no
repository-mutation or native-execution surface.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_BASE = "https://api.github.com"
API_VERSION = "2022-11-28"
REPOSITORY = "cosmosapjw-quantum/rei_bianchi"
OWNER, REPO = REPOSITORY.split("/", 1)
RULESET_NAME = "REI immutable attempt-ledger refs v1"
TARGET_PATTERN = "refs/heads/attempt-ledger/**"
ATTEMPT_BRANCH = (
    "attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)
GLOBAL_REF = f"refs/heads/{ATTEMPT_BRANCH}"
REQUIRED_RULES = {"update", "deletion", "non_fast_forward"}
RECEIPT_TTL_SECONDS = 300
FUTURE_CLOCK_SKEW_SECONDS = 30
AUTHORITY = {
    "scheme": "https",
    "api_host": "api.github.com",
    "repository": REPOSITORY,
    "api_version": API_VERSION,
}
RULESET_PAYLOAD: dict[str, Any] = {
    "name": RULESET_NAME,
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {
        "ref_name": {"include": [TARGET_PATTERN], "exclude": []}
    },
    "rules": [
        {
            "type": "update",
            "parameters": {"update_allows_fetch_and_merge": False},
        },
        {"type": "deletion"},
        {"type": "non_fast_forward"},
    ],
}
PACKAGE = Path(__file__).resolve().parent
SCRIPT_RELATIVE = (
    "docs/rei_runtime_bridge_03a3r3_independent_readback/"
    "independent_readback_audit.py"
)
INDEX_RELATIVE = (
    "docs/rei_runtime_bridge_03a3r3_independent_readback/SOURCE_INDEX.json"
)
PARENT_ADMIN_RELATIVE = (
    "docs/rei_runtime_bridge_03a3r2_admin_ruleset/"
    "apply_and_attest_ruleset.py"
)
PARENT_ADMIN_BLOB = "ec51301b06058b47f4e1cb3ba8c2502d954abe19"


class ReadbackAuditError(RuntimeError):
    """Typed fail-closed error for independent readback auditing."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _valid_hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def _parse_utc(value: Any, classification: str) -> datetime:
    if not isinstance(value, str):
        raise ReadbackAuditError(classification)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReadbackAuditError(classification) from exc
    if parsed.tzinfo is None:
        raise ReadbackAuditError(classification)
    return parsed.astimezone(timezone.utc)


def _mapping(value: Any, classification: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ReadbackAuditError(classification)
    return value


def validate_admin_receipt(record: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(_mapping(record, "ADMIN_RECEIPT_NOT_OBJECT"))
    status = value.get("status")
    effects = {
        "PASS_RULESET_CREATED_AND_READ_BACK": "RULESET_CREATED_ONLY",
        "PASS_EXISTING_RULESET_READ_BACK": "NONE",
    }
    if (
        value.get("schema")
        != "rei-runtime-attempt-ref-ruleset-admin-mutation/v1"
        or status not in effects
        or value.get("authority") != AUTHORITY
        or value.get("repository") != REPOSITORY
        or not isinstance(value.get("ruleset_id"), int)
        or value["ruleset_id"] <= 0
        or value.get("ruleset_name") != RULESET_NAME
        or value.get("global_ref") != GLOBAL_REF
        or value.get("mutation_effect") != effects[status]
        or value.get("attempt_ref_created") is not False
        or value.get("local_lease_created") is not False
        or value.get("native_runtime") != "NOT_RUN"
    ):
        raise ReadbackAuditError("ADMIN_RECEIPT_MISMATCH")
    _parse_utc(value.get("created_at_utc"), "ADMIN_RECEIPT_TIME_INVALID")
    return value


def validate_source_protection_receipt(
    record: Mapping[str, Any],
    *,
    now: datetime | None = None,
    require_current_freshness: bool = False,
) -> dict[str, Any]:
    value = dict(_mapping(record, "SOURCE_RECEIPT_NOT_OBJECT"))
    generated = _parse_utc(
        value.get("generated_at_utc"), "SOURCE_RECEIPT_TIME_INVALID"
    )
    expires = _parse_utc(
        value.get("expires_at_utc"), "SOURCE_RECEIPT_TIME_INVALID"
    )
    lifetime = (expires - generated).total_seconds()
    active = value.get("active_rules")
    all_effective = value.get("all_effective_rule_types")
    if (
        value.get("schema")
        != "rei-runtime-attempt-ref-protection-receipt/v1"
        or value.get("status") != "PASS_ATTEMPT_REF_SERVER_PROTECTION"
        or value.get("authority") != AUTHORITY
        or value.get("repository") != REPOSITORY
        or value.get("global_ref") != GLOBAL_REF
        or value.get("target_pattern") != TARGET_PATTERN
        or value.get("prospective_branch") != ATTEMPT_BRANCH
        or value.get("prospective_branch_rules_http_status") != 200
        or not isinstance(value.get("ruleset_id"), int)
        or value["ruleset_id"] <= 0
        or value.get("ruleset_name") != RULESET_NAME
        or value.get("ruleset_enforcement") != "active"
        or not isinstance(active, list)
        or set(active) != REQUIRED_RULES
        or not isinstance(all_effective, list)
        or not REQUIRED_RULES.issubset(set(all_effective))
        or "creation" in set(all_effective)
        or value.get("update_forbidden") is not True
        or value.get("deletion_forbidden") is not True
        or value.get("non_fast_forward_forbidden") is not True
        or value.get("creation_restricted") is not False
        or value.get("bypass_actors") != []
        or value.get("global_ref_http_status") != 404
        or value.get("global_ref_absent") is not True
        or value.get("authorization_effect") != "NONE"
        or value.get("mutation_effect") != "NONE"
        or value.get("native_runtime") != "NOT_RUN"
        or lifetime != RECEIPT_TTL_SECONDS
    ):
        raise ReadbackAuditError("SOURCE_RECEIPT_MISMATCH")
    for key in (
        "ruleset_detail_response_sha256",
        "prospective_branch_rules_response_sha256",
        "global_ref_absence_response_sha256",
    ):
        if not _valid_hex(value.get(key), 64):
            raise ReadbackAuditError(f"SOURCE_RECEIPT_HASH_INVALID:{key}")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if generated - current > timedelta(seconds=FUTURE_CLOCK_SKEW_SECONDS):
        raise ReadbackAuditError("SOURCE_RECEIPT_FUTURE_DATED")
    if require_current_freshness and not (
        generated - timedelta(seconds=FUTURE_CLOCK_SKEW_SECONDS)
        <= current
        <= expires
    ):
        raise ReadbackAuditError("SOURCE_RECEIPT_NOT_CURRENTLY_FRESH")
    return value


def validate_operation_evidence(
    evidence: Mapping[str, Any],
    admin: Mapping[str, Any],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    value = dict(_mapping(evidence, "OPERATION_EVIDENCE_NOT_OBJECT"))
    admin_value = validate_admin_receipt(admin)
    source_value = validate_source_protection_receipt(source)
    created = admin_value["status"] == "PASS_RULESET_CREATED_AND_READ_BACK"
    expected_operations = ["GET_RULESET_LIST"]
    if created:
        expected_operations.append("POST_CREATE_RULESET")
    expected_operations.extend(
        [
            "GET_RULESET_DETAILS",
            "GET_PROSPECTIVE_BRANCH_RULES",
            "GET_EXACT_GLOBAL_ATTEMPT_REF",
        ]
    )
    rows = value.get("steps")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ReadbackAuditError("OPERATION_EVIDENCE_STEPS_INVALID")
    operations = [row.get("operation") for row in rows]
    if (
        value.get("schema")
        != "rei-runtime-03a3r2-admin-operation-evidence/v1"
        or value.get("repository") != REPOSITORY
        or value.get("global_ref") != GLOBAL_REF
        or value.get("mode") not in {"APPLY_RULESET_ONLY", "READ_ONLY_INSPECT"}
        or value.get("attempt_ref_mutation_permitted") is not False
        or value.get("native_runtime_permitted") is not False
        or operations != expected_operations
        or rows[0].get("http_status") != 200
        or rows[-1].get("http_status") != 404
    ):
        raise ReadbackAuditError("OPERATION_EVIDENCE_MISMATCH")
    if created:
        post = rows[1]
        if (
            value.get("mode") != "APPLY_RULESET_ONLY"
            or post.get("http_status") != 201
            or post.get("request_sha256")
            != sha256_bytes(canonical_bytes(RULESET_PAYLOAD))
            or not _valid_hex(post.get("response_sha256"), 64)
        ):
            raise ReadbackAuditError("OPERATION_CREATE_STEP_MISMATCH")
    details = next(row for row in rows if row["operation"] == "GET_RULESET_DETAILS")
    effective = next(
        row for row in rows if row["operation"] == "GET_PROSPECTIVE_BRANCH_RULES"
    )
    ref = rows[-1]
    if (
        details.get("http_status") != 200
        or details.get("ruleset_id") != admin_value["ruleset_id"]
        or details.get("response_sha256")
        != source_value["ruleset_detail_response_sha256"]
        or effective.get("http_status") != 200
        or effective.get("response_sha256")
        != source_value["prospective_branch_rules_response_sha256"]
        or ref.get("response_sha256")
        != source_value["global_ref_absence_response_sha256"]
        or source_value["ruleset_id"] != admin_value["ruleset_id"]
    ):
        raise ReadbackAuditError("OPERATION_SOURCE_CROSS_BINDING_MISMATCH")
    started = _parse_utc(
        value.get("started_at_utc"), "OPERATION_EVIDENCE_TIME_INVALID"
    )
    completed = _parse_utc(
        value.get("completed_at_utc"), "OPERATION_EVIDENCE_TIME_INVALID"
    )
    admin_time = _parse_utc(
        admin_value.get("created_at_utc"), "ADMIN_RECEIPT_TIME_INVALID"
    )
    source_time = _parse_utc(
        source_value.get("generated_at_utc"), "SOURCE_RECEIPT_TIME_INVALID"
    )
    if not started <= admin_time <= source_time <= completed:
        raise ReadbackAuditError("OPERATION_EVIDENCE_TIME_ORDER_INVALID")
    return {
        "status": "PASS_RETROSPECTIVE_OPERATION_EVIDENCE",
        "operations": operations,
        "ruleset_id": admin_value["ruleset_id"],
    }


def _load_canonical_json(path: Path, classification: str) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise ReadbackAuditError(classification)
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ReadbackAuditError(classification) from exc
    if not resolved.is_file():
        raise ReadbackAuditError(classification)
    raw = resolved.read_bytes()
    try:
        value = json.loads(raw.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReadbackAuditError(classification) from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value) + b"\n":
        raise ReadbackAuditError(f"{classification}:NONCANONICAL_BYTES")
    return value


def validate_input_bundle(
    *,
    admin_path: Path,
    source_path: Path,
    evidence_path: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    paths = [Path(admin_path), Path(source_path), Path(evidence_path)]
    resolved = [path.resolve(strict=True) for path in paths]
    if any(path.is_symlink() or not path.is_absolute() for path in paths):
        raise ReadbackAuditError("INPUT_BUNDLE_PATH_INVALID")
    if len({path.parent for path in resolved}) != 1:
        raise ReadbackAuditError("INPUT_BUNDLE_NOT_COLOCATED")
    admin = _load_canonical_json(paths[0], "ADMIN_RECEIPT_UNREADABLE")
    source = _load_canonical_json(paths[1], "SOURCE_RECEIPT_UNREADABLE")
    evidence = _load_canonical_json(paths[2], "OPERATION_EVIDENCE_UNREADABLE")
    admin_value = validate_admin_receipt(admin)
    source_value = validate_source_protection_receipt(
        source,
        now=now,
        require_current_freshness=True,
    )
    operation = validate_operation_evidence(evidence, admin_value, source_value)
    hashes = {
        "admin_mutation_receipt": sha256_file(resolved[0]),
        "source_protection_receipt": sha256_file(resolved[1]),
        "raw_operation_evidence": sha256_file(resolved[2]),
    }
    return {
        "status": "PASS_RETROSPECTIVE_ADMIN_BUNDLE",
        "root": str(resolved[0].parent),
        "admin": admin_value,
        "source": source_value,
        "operation": operation,
        "input_sha256": hashes,
    }


def _rule_types(details: Mapping[str, Any]) -> set[str]:
    rows = details.get("rules")
    if not isinstance(rows, list):
        raise ReadbackAuditError("LIVE_RULESET_RULES_INVALID")
    result: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("type"), str):
            raise ReadbackAuditError("LIVE_RULESET_RULE_INVALID")
        result.add(row["type"])
    return result


def validate_ruleset_details(details: Mapping[str, Any]) -> int:
    value = _mapping(details, "LIVE_RULESET_DETAILS_NOT_OBJECT")
    condition = value.get("conditions", {}).get("ref_name", {})
    types = _rule_types(value)
    if (
        value.get("name") != RULESET_NAME
        or value.get("target") != "branch"
        or value.get("enforcement") != "active"
        or value.get("bypass_actors", []) != []
        or condition.get("include") != [TARGET_PATTERN]
        or condition.get("exclude", []) != []
        or types != REQUIRED_RULES
        or "creation" in types
    ):
        raise ReadbackAuditError("LIVE_RULESET_DETAILS_MISMATCH")
    updates = [row for row in value["rules"] if row.get("type") == "update"]
    if (
        len(updates) != 1
        or updates[0].get("parameters", {}).get(
            "update_allows_fetch_and_merge"
        )
        is not False
    ):
        raise ReadbackAuditError("LIVE_RULESET_UPDATE_POLICY_MISMATCH")
    ruleset_id = value.get("id")
    if not isinstance(ruleset_id, int) or ruleset_id <= 0:
        raise ReadbackAuditError("LIVE_RULESET_ID_INVALID")
    return ruleset_id


def find_named_ruleset(items: Any) -> Mapping[str, Any] | None:
    if not isinstance(items, list):
        raise ReadbackAuditError("LIVE_RULESET_LIST_INVALID")
    matches = [
        item
        for item in items
        if isinstance(item, dict) and item.get("name") == RULESET_NAME
    ]
    if len(matches) > 1:
        raise ReadbackAuditError("LIVE_DUPLICATE_NAMED_RULESETS")
    return matches[0] if matches else None


def validate_live_snapshot(
    *,
    ruleset_list: Any,
    ruleset_details: Mapping[str, Any],
    effective_rules: Any,
    ref_http_status: int,
    expected_ruleset_id: int,
) -> dict[str, Any]:
    named = find_named_ruleset(ruleset_list)
    if named is None or named.get("id") != expected_ruleset_id:
        raise ReadbackAuditError("LIVE_NAMED_RULESET_MISSING_OR_REPLACED")
    ruleset_id = validate_ruleset_details(ruleset_details)
    if ruleset_id != expected_ruleset_id:
        raise ReadbackAuditError("LIVE_RULESET_ID_DRIFT")
    if not isinstance(effective_rules, list):
        raise ReadbackAuditError("LIVE_EFFECTIVE_RULES_INVALID")
    supplied: set[str] = set()
    all_types: set[str] = set()
    for row in effective_rules:
        if not isinstance(row, dict) or not isinstance(row.get("type"), str):
            raise ReadbackAuditError("LIVE_EFFECTIVE_RULE_INVALID")
        kind = row["type"]
        all_types.add(kind)
        if kind in REQUIRED_RULES and row.get("ruleset_id") == ruleset_id:
            supplied.add(kind)
    if "creation" in all_types:
        raise ReadbackAuditError("LIVE_CREATION_RULE_FORBIDDEN")
    if supplied != REQUIRED_RULES:
        raise ReadbackAuditError("LIVE_REQUIRED_RULES_MISSING")
    if ref_http_status != 404:
        raise ReadbackAuditError(
            f"LIVE_GLOBAL_ATTEMPT_REF_NOT_ABSENT_HTTP_{ref_http_status}"
        )
    return {
        "status": "PASS_INDEPENDENT_LIVE_RULESET_SNAPSHOT",
        "ruleset_id": ruleset_id,
        "all_effective_rule_types": sorted(all_types),
        "global_ref_absent": True,
    }


def build_fresh_source_protection_receipt(
    *,
    ruleset_id: int,
    details_raw: bytes,
    effective_raw: bytes,
    ref_raw: bytes,
    all_effective_rule_types: list[str],
    independent_audit_receipt_sha256: str,
    original_admin_receipt_sha256: str,
    original_source_receipt_sha256: str,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    for value in (
        independent_audit_receipt_sha256,
        original_admin_receipt_sha256,
        original_source_receipt_sha256,
    ):
        if not _valid_hex(value, 64):
            raise ReadbackAuditError("FRESH_RECEIPT_BINDING_HASH_INVALID")
    all_types = set(all_effective_rule_types)
    if not REQUIRED_RULES.issubset(all_types) or "creation" in all_types:
        raise ReadbackAuditError("FRESH_RECEIPT_EFFECTIVE_RULES_INVALID")
    now = (created_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return {
        "schema": "rei-runtime-attempt-ref-protection-receipt/v1",
        "status": "PASS_ATTEMPT_REF_SERVER_PROTECTION",
        "generated_at_utc": now.isoformat(),
        "expires_at_utc": (
            now + timedelta(seconds=RECEIPT_TTL_SECONDS)
        ).isoformat(),
        "authority": AUTHORITY,
        "repository": REPOSITORY,
        "global_ref": GLOBAL_REF,
        "target_pattern": TARGET_PATTERN,
        "prospective_branch": ATTEMPT_BRANCH,
        "prospective_branch_rules_http_status": 200,
        "ruleset_id": ruleset_id,
        "ruleset_name": RULESET_NAME,
        "ruleset_enforcement": "active",
        "active_rules": sorted(REQUIRED_RULES),
        "all_effective_rule_types": sorted(all_types),
        "update_forbidden": True,
        "deletion_forbidden": True,
        "non_fast_forward_forbidden": True,
        "creation_restricted": False,
        "bypass_actors": [],
        "ruleset_detail_response_sha256": sha256_bytes(details_raw),
        "prospective_branch_rules_response_sha256": sha256_bytes(
            effective_raw
        ),
        "global_ref_absence_response_sha256": sha256_bytes(ref_raw),
        "global_ref_http_status": 404,
        "global_ref_absent": True,
        "independent_audit_receipt_sha256": (
            independent_audit_receipt_sha256
        ),
        "original_admin_receipt_sha256": original_admin_receipt_sha256,
        "original_source_receipt_sha256": original_source_receipt_sha256,
        "authorization_effect": "NONE",
        "mutation_effect": "NONE",
        "native_runtime": "NOT_RUN",
    }


def _allowed_get_path(path: str) -> bool:
    prefix = f"/repos/{OWNER}/{REPO}"
    encoded_branch = quote(ATTEMPT_BRANCH, safe="")
    ref_path = quote("heads/" + ATTEMPT_BRANCH, safe="/")
    return (
        path == f"{prefix}/rulesets"
        or re.fullmatch(rf"{re.escape(prefix)}/rulesets/[1-9][0-9]*", path)
        is not None
        or path == f"{prefix}/rules/branches/{encoded_branch}"
        or path == f"{prefix}/git/ref/{ref_path}"
    )


def request_json(
    method: str,
    path: str,
    *,
    token: str,
    opener: Callable[..., Any] | None = None,
) -> tuple[int, bytes, Any]:
    if method != "GET":
        raise ReadbackAuditError("HTTP_METHOD_FORBIDDEN")
    if not _allowed_get_path(path):
        raise ReadbackAuditError("GET_TARGET_FORBIDDEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "rei-runtime-03a3r3-independent-readback/v1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(API_BASE + path, method=method, headers=headers)
    open_request = opener or urlopen
    try:
        with open_request(request, timeout=30) as response:
            status = response.status
            raw = response.read()
    except HTTPError as exc:
        status = exc.code
        raw = exc.read()
    except (URLError, OSError) as exc:
        raise ReadbackAuditError(
            f"LIVE_TRANSPORT_ERROR:{type(exc).__name__}:{exc}"
        ) from exc
    try:
        body = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReadbackAuditError(
            f"LIVE_NON_JSON_RESPONSE:{path}:{status}"
        ) from exc
    return status, raw, body


def _git_text(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise ReadbackAuditError(
            "GIT_READ_FAILED:" + " ".join(args) + ":" + completed.stderr.strip()
        )
    return completed.stdout.strip()


def verify_executing_release(
    repo: Path,
    *,
    expected_head: str,
    expected_tree: str,
) -> Path:
    root = Path(repo).resolve(strict=True)
    if not root.is_dir() or not _valid_hex(expected_head, 40) or not _valid_hex(
        expected_tree, 40
    ):
        raise ReadbackAuditError("RELEASE_IDENTITY_ARGUMENT_INVALID")
    expected_script = (root / SCRIPT_RELATIVE).resolve(strict=True)
    if expected_script != Path(__file__).resolve(strict=True):
        raise ReadbackAuditError("EXECUTING_AUDITOR_OUTSIDE_VERIFIED_RELEASE")
    if (
        _git_text(root, "rev-parse", "HEAD") != expected_head
        or _git_text(root, "rev-parse", "HEAD^{tree}") != expected_tree
    ):
        raise ReadbackAuditError("EXECUTING_RELEASE_IDENTITY_MISMATCH")
    origin = _git_text(root, "config", "--get", "remote.origin.url")
    if "cosmosapjw-quantum/rei_bianchi" not in origin:
        raise ReadbackAuditError("EXECUTING_RELEASE_ORIGIN_MISMATCH")
    script_blob = _git_text(root, "hash-object", SCRIPT_RELATIVE)
    if script_blob != _git_text(root, "rev-parse", f"HEAD:{SCRIPT_RELATIVE}"):
        raise ReadbackAuditError("EXECUTING_AUDITOR_BLOB_MISMATCH")
    parent_blob = _git_text(root, "rev-parse", f"HEAD:{PARENT_ADMIN_RELATIVE}")
    if parent_blob != PARENT_ADMIN_BLOB:
        raise ReadbackAuditError("PARENT_ADMIN_SOURCE_BLOB_MISMATCH")
    verifier = (root / INDEX_RELATIVE).with_name("verify_source_index.py")
    completed = subprocess.run(
        [sys.executable, str(verifier)],
        cwd=root,
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise ReadbackAuditError(
            "SOURCE_INDEX_VERIFICATION_FAILED:"
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    return root


def _validate_output_target(target: Path, *, repo: Path) -> Path:
    candidate = Path(target)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise ReadbackAuditError("OUTPUT_ROOT_INVALID")
    resolved = candidate.resolve(strict=False)
    if resolved.exists() or resolved.is_symlink() or not resolved.parent.is_dir():
        raise ReadbackAuditError("OUTPUT_ROOT_INVALID")
    try:
        resolved.relative_to(repo)
    except ValueError:
        pass
    else:
        raise ReadbackAuditError("OUTPUT_ROOT_INSIDE_REPOSITORY")
    return resolved


def _publish_atomic_bundle(
    target: Path,
    *,
    audit_record: Mapping[str, Any],
    fresh_record: Mapping[str, Any],
) -> None:
    audit_payload = canonical_bytes(dict(audit_record)) + b"\n"
    fresh_payload = canonical_bytes(dict(fresh_record)) + b"\n"
    manifest = (
        f"{sha256_bytes(audit_payload)}  INDEPENDENT_AUDIT_RECEIPT.json\n"
        f"{sha256_bytes(fresh_payload)}  AUDITED_FRESH_SOURCE_PROTECTION_RECEIPT.json\n"
    ).encode("ascii")
    staging = Path(
        tempfile.mkdtemp(prefix=target.name + ".staging-", dir=target.parent)
    )
    try:
        for name, payload in (
            ("INDEPENDENT_AUDIT_RECEIPT.json", audit_payload),
            ("AUDITED_FRESH_SOURCE_PROTECTION_RECEIPT.json", fresh_payload),
            ("SHA256SUMS", manifest),
        ):
            destination = staging / name
            descriptor = os.open(
                destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
            with os.fdopen(descriptor, "wb") as output:
                output.write(payload)
                output.flush()
                os.fsync(output.fileno())
        directory = os.open(staging, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        os.rename(staging, target)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _live_readback(
    *, token: str, expected_ruleset_id: int
) -> tuple[dict[str, Any], dict[str, bytes]]:
    prefix = f"/repos/{OWNER}/{REPO}"
    list_status, list_raw, listed = request_json(
        "GET", f"{prefix}/rulesets", token=token
    )
    if list_status != 200:
        raise ReadbackAuditError(f"LIVE_RULESET_LIST_HTTP_{list_status}")
    named = find_named_ruleset(listed)
    if named is None or named.get("id") != expected_ruleset_id:
        raise ReadbackAuditError("LIVE_NAMED_RULESET_MISSING_OR_REPLACED")
    details_status, details_raw, details = request_json(
        "GET", f"{prefix}/rulesets/{expected_ruleset_id}", token=token
    )
    if details_status != 200 or not isinstance(details, dict):
        raise ReadbackAuditError(f"LIVE_RULESET_DETAILS_HTTP_{details_status}")
    encoded_branch = quote(ATTEMPT_BRANCH, safe="")
    effective_status, effective_raw, effective = request_json(
        "GET",
        f"{prefix}/rules/branches/{encoded_branch}",
        token=token,
    )
    if effective_status != 200:
        raise ReadbackAuditError(
            f"LIVE_PROSPECTIVE_RULES_HTTP_{effective_status}"
        )
    ref_path = quote("heads/" + ATTEMPT_BRANCH, safe="/")
    ref_status, ref_raw, _ = request_json(
        "GET", f"{prefix}/git/ref/{ref_path}", token=token
    )
    snapshot = validate_live_snapshot(
        ruleset_list=listed,
        ruleset_details=details,
        effective_rules=effective,
        ref_http_status=ref_status,
        expected_ruleset_id=expected_ruleset_id,
    )
    raw = {
        "ruleset_list": list_raw,
        "ruleset_details": details_raw,
        "effective_rules": effective_raw,
        "global_ref": ref_raw,
    }
    return snapshot, raw


def run_audit(
    *,
    repo: Path,
    expected_head: str,
    expected_tree: str,
    admin_receipt: Path,
    source_receipt: Path,
    operation_evidence: Path,
    output_root: Path,
    token: str,
) -> dict[str, Any]:
    root = verify_executing_release(
        repo, expected_head=expected_head, expected_tree=expected_tree
    )
    if not token:
        raise ReadbackAuditError("GITHUB_TOKEN_UNAVAILABLE")
    bundle = validate_input_bundle(
        admin_path=admin_receipt,
        source_path=source_receipt,
        evidence_path=operation_evidence,
    )
    ruleset_id = bundle["admin"]["ruleset_id"]
    snapshot, raw = _live_readback(token=token, expected_ruleset_id=ruleset_id)
    now = datetime.now(timezone.utc)
    audit_record = {
        "schema": "rei-runtime-attempt-ref-ruleset-independent-readback/v1",
        "status": "PASS_INDEPENDENT_ATTEMPT_REF_RULESET_READBACK_AUDIT",
        "generated_at_utc": now.isoformat(),
        "authority": AUTHORITY,
        "repository": REPOSITORY,
        "auditor_release": {"commit": expected_head, "tree": expected_tree},
        "admin_bundle_root": bundle["root"],
        "input_sha256": bundle["input_sha256"],
        "retrospective_provenance": bundle["operation"]["status"],
        "live_snapshot": snapshot,
        "live_response_sha256": {
            key: sha256_bytes(value) for key, value in raw.items()
        },
        "global_ref": GLOBAL_REF,
        "global_ref_absent": True,
        "attempt_ref_created": False,
        "local_lease_created": False,
        "dispatch_intent_created": False,
        "authorization_effect": "NONE",
        "mutation_effect": "NONE",
        "native_runtime": "NOT_RUN",
        "next_gate": "TARGET_HOST_STATIC_PREFLIGHT_AFTER_SEPARATE_REVIEW",
    }
    audit_payload = canonical_bytes(audit_record) + b"\n"
    audit_sha = sha256_bytes(audit_payload)
    fresh_record = build_fresh_source_protection_receipt(
        ruleset_id=ruleset_id,
        details_raw=raw["ruleset_details"],
        effective_raw=raw["effective_rules"],
        ref_raw=raw["global_ref"],
        all_effective_rule_types=snapshot["all_effective_rule_types"],
        independent_audit_receipt_sha256=audit_sha,
        original_admin_receipt_sha256=bundle["input_sha256"][
            "admin_mutation_receipt"
        ],
        original_source_receipt_sha256=bundle["input_sha256"][
            "source_protection_receipt"
        ],
        created_at=now,
    )
    target = _validate_output_target(Path(output_root), repo=root)
    _publish_atomic_bundle(
        target, audit_record=audit_record, fresh_record=fresh_record
    )
    return {
        "status": audit_record["status"],
        "output_root": str(target),
        "audit_receipt_sha256": audit_sha,
        "fresh_source_receipt_sha256": sha256_bytes(
            canonical_bytes(fresh_record) + b"\n"
        ),
        "global_ref": "ABSENT_404",
        "native_runtime": "NOT_RUN",
    }


def _self_test() -> dict[str, Any]:
    details = json.loads(json.dumps(RULESET_PAYLOAD))
    details["id"] = 42
    listed = [{"id": 42, "name": RULESET_NAME}]
    effective = [
        {"type": "update", "ruleset_id": 42},
        {"type": "deletion", "ruleset_id": 42},
        {"type": "non_fast_forward", "ruleset_id": 42},
    ]
    snapshot = validate_live_snapshot(
        ruleset_list=listed,
        ruleset_details=details,
        effective_rules=effective,
        ref_http_status=404,
        expected_ruleset_id=42,
    )
    receipt = build_fresh_source_protection_receipt(
        ruleset_id=42,
        details_raw=b"details",
        effective_raw=b"effective",
        ref_raw=b"ref-404",
        all_effective_rule_types=snapshot["all_effective_rule_types"],
        independent_audit_receipt_sha256="1" * 64,
        original_admin_receipt_sha256="2" * 64,
        original_source_receipt_sha256="3" * 64,
    )
    validate_source_protection_receipt(
        receipt, require_current_freshness=True
    )
    return {
        "status": "PASS_INDEPENDENT_READBACK_SELF_TEST",
        "ruleset_id": snapshot["ruleset_id"],
        "global_ref": "ABSENT_404",
        "network_surface": "GET_ONLY",
        "native_runtime": "NOT_RUN",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--expected-head")
    parser.add_argument("--expected-tree")
    parser.add_argument("--admin-receipt", type=Path)
    parser.add_argument("--source-receipt", type=Path)
    parser.add_argument("--operation-evidence", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    options = parser.parse_args(argv)
    try:
        if options.self_test:
            print(json.dumps(_self_test(), sort_keys=True))
            return 0
        required = (
            options.repo,
            options.expected_head,
            options.expected_tree,
            options.admin_receipt,
            options.source_receipt,
            options.operation_evidence,
            options.output_root,
        )
        if any(value is None for value in required):
            raise ReadbackAuditError("REQUIRED_ARGUMENT_MISSING")
        result = run_audit(
            repo=options.repo,
            expected_head=options.expected_head,
            expected_tree=options.expected_tree,
            admin_receipt=options.admin_receipt,
            source_receipt=options.source_receipt,
            operation_evidence=options.operation_evidence,
            output_root=options.output_root,
            token=os.environ.get(options.token_env, ""),
        )
    except ReadbackAuditError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65
    except Exception as exc:
        print(
            "STOP_INVALID: UNEXPECTED_READBACK_EXCEPTION:"
            f"{type(exc).__name__}:{exc}",
            file=sys.stderr,
        )
        return 65
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
