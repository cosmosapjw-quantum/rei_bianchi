#!/usr/bin/env python3
"""Admin-only ruleset apply/readback for the final REI runtime attempt.

The script can create or read one repository ruleset.  It cannot create,
update, or delete the global attempt ref; it cannot import the REI production
bridge or invoke the native worker.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping
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
        "ref_name": {
            "include": [TARGET_PATTERN],
            "exclude": [],
        }
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


class AdminRulesetError(RuntimeError):
    """Typed fail-closed administrative error."""


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


def write_o_excl(path: Path, value: Mapping[str, Any]) -> None:
    payload = canonical_bytes(dict(value)) + b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(payload)
        output.flush()
        os.fsync(output.fileno())


def validate_output_root(path: Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise AdminRulesetError("OUTPUT_ROOT_MUST_BE_NEW_ABSOLUTE_PATH")
    resolved = candidate.resolve(strict=False)
    if resolved.exists() or resolved.is_symlink() or not resolved.parent.is_dir():
        raise AdminRulesetError("OUTPUT_ROOT_MUST_BE_NEW_ABSOLUTE_PATH")
    resolved.mkdir(mode=0o700)
    return resolved


def request_json(
    method: str,
    path: str,
    *,
    token: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[int, bytes, Any]:
    if method not in {"GET", "POST"}:
        raise AdminRulesetError("HTTP_METHOD_FORBIDDEN")
    if method == "POST" and path != f"/repos/{OWNER}/{REPO}/rulesets":
        raise AdminRulesetError("POST_TARGET_FORBIDDEN")
    data = None if payload is None else canonical_bytes(dict(payload))
    request = Request(
        API_BASE + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "rei-runtime-03a3r2-admin-ruleset/v1",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            status = response.status
            raw = response.read()
    except HTTPError as exc:
        status = exc.code
        raw = exc.read()
    except (URLError, OSError) as exc:
        raise AdminRulesetError(
            f"TRANSPORT_ERROR:{type(exc).__name__}:{exc}"
        ) from exc
    try:
        body = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise AdminRulesetError(
            f"NON_JSON_RESPONSE:{method}:{path}:{status}"
        ) from exc
    return status, raw, body


def rule_types(details: Mapping[str, Any]) -> set[str]:
    rows = details.get("rules")
    if not isinstance(rows, list):
        raise AdminRulesetError("RULESET_RULES_NOT_LIST")
    result: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("type"), str):
            raise AdminRulesetError("RULESET_RULE_INVALID")
        result.add(row["type"])
    return result


def validate_ruleset_details(details: Mapping[str, Any]) -> int:
    condition = details.get("conditions", {}).get("ref_name", {})
    bypass = details.get("bypass_actors", [])
    types = rule_types(details)
    if (
        details.get("name") != RULESET_NAME
        or details.get("target") != "branch"
        or details.get("enforcement") != "active"
        or bypass != []
        or condition.get("include") != [TARGET_PATTERN]
        or condition.get("exclude", []) != []
        or types != REQUIRED_RULES
        or "creation" in types
    ):
        raise AdminRulesetError("RULESET_DETAILS_MISMATCH")
    updates = [
        row
        for row in details.get("rules", [])
        if isinstance(row, dict) and row.get("type") == "update"
    ]
    if (
        len(updates) != 1
        or updates[0].get("parameters", {}).get(
            "update_allows_fetch_and_merge"
        )
        is not False
    ):
        raise AdminRulesetError("RULESET_UPDATE_POLICY_MISMATCH")
    ruleset_id = details.get("id")
    if not isinstance(ruleset_id, int) or ruleset_id <= 0:
        raise AdminRulesetError("RULESET_ID_INVALID")
    return ruleset_id


def find_named_ruleset(items: Any) -> Mapping[str, Any] | None:
    if not isinstance(items, list):
        raise AdminRulesetError("RULESET_LIST_NOT_LIST")
    matches = [
        item
        for item in items
        if isinstance(item, dict) and item.get("name") == RULESET_NAME
    ]
    if len(matches) > 1:
        raise AdminRulesetError("DUPLICATE_NAMED_RULESETS")
    return matches[0] if matches else None


def validate_effective_rules(rows: Any, *, ruleset_id: int) -> list[str]:
    if not isinstance(rows, list):
        raise AdminRulesetError("PROSPECTIVE_RULES_NOT_LIST")
    supplied: set[str] = set()
    all_types: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("type"), str):
            raise AdminRulesetError("PROSPECTIVE_RULE_INVALID")
        kind = row["type"]
        all_types.add(kind)
        if kind in REQUIRED_RULES and row.get("ruleset_id") == ruleset_id:
            supplied.add(kind)
    if "creation" in all_types:
        raise AdminRulesetError("PROSPECTIVE_CREATION_MUST_REMAIN_ALLOWED")
    if supplied != REQUIRED_RULES:
        raise AdminRulesetError("PROSPECTIVE_REQUIRED_RULES_MISSING")
    return sorted(all_types)


def build_source_protection_receipt(
    *,
    ruleset_id: int,
    details_raw: bytes,
    effective_raw: bytes,
    ref_raw: bytes,
    all_effective_rule_types: list[str],
    created_at: datetime | None = None,
) -> dict[str, Any]:
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
        "all_effective_rule_types": all_effective_rule_types,
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
        "authorization_effect": "NONE",
        "mutation_effect": "NONE",
        "native_runtime": "NOT_RUN",
    }


def validate_payload() -> None:
    synthetic = dict(RULESET_PAYLOAD)
    synthetic["id"] = 1
    if validate_ruleset_details(synthetic) != 1:
        raise AdminRulesetError("SELF_TEST_RULESET_DETAILS_FAILED")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--output-root", type=Path)
    options = parser.parse_args(argv)

    try:
        validate_payload()
        if options.self_test:
            print(
                json.dumps(
                    {
                        "status": "PASS_ADMIN_RULESET_HANDOFF_SELF_TEST",
                        "rules": sorted(REQUIRED_RULES),
                        "creation_allowed": True,
                        "attempt_ref_mutation": "FORBIDDEN",
                        "native_runtime": "NOT_RUN",
                    },
                    sort_keys=True,
                )
            )
            return 0
        if options.output_root is None:
            raise AdminRulesetError("OUTPUT_ROOT_REQUIRED")
        token = os.environ.get(options.token_env, "")
        if not token:
            raise AdminRulesetError("GITHUB_TOKEN_UNAVAILABLE")
        output = validate_output_root(options.output_root)
    except AdminRulesetError as exc:
        print(f"STOP_INVALID: {exc}", file=sys.stderr)
        return 65

    evidence: dict[str, Any] = {
        "schema": "rei-runtime-03a3r2-admin-operation-evidence/v1",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": REPOSITORY,
        "mode": "APPLY_RULESET_ONLY" if options.apply else "READ_ONLY_INSPECT",
        "global_ref": GLOBAL_REF,
        "attempt_ref_mutation_permitted": False,
        "native_runtime_permitted": False,
        "steps": [],
    }
    ruleset_created = False
    try:
        status, raw_list, body = request_json(
            "GET", f"/repos/{OWNER}/{REPO}/rulesets", token=token
        )
        evidence["steps"].append(
            {
                "operation": "GET_RULESET_LIST",
                "http_status": status,
                "response_sha256": sha256_bytes(raw_list),
            }
        )
        if status != 200:
            raise AdminRulesetError(f"RULESET_LIST_HTTP_{status}")
        named = find_named_ruleset(body)

        if named is None and options.apply:
            status, raw_create, created = request_json(
                "POST",
                f"/repos/{OWNER}/{REPO}/rulesets",
                token=token,
                payload=RULESET_PAYLOAD,
            )
            evidence["steps"].append(
                {
                    "operation": "POST_CREATE_RULESET",
                    "http_status": status,
                    "request_sha256": sha256_bytes(
                        canonical_bytes(RULESET_PAYLOAD)
                    ),
                    "response_sha256": sha256_bytes(raw_create),
                }
            )
            if status != 201 or not isinstance(created, dict):
                raise AdminRulesetError(f"RULESET_CREATE_HTTP_{status}")
            ruleset_created = True
            named = created

        if named is None:
            write_o_excl(
                output / "ADMIN_MUTATION_RECEIPT.json",
                {
                    "schema": "rei-runtime-attempt-ref-ruleset-admin-mutation/v1",
                    "status": "BLOCKED_RULESET_ABSENT",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "repository": REPOSITORY,
                    "global_ref": GLOBAL_REF,
                    "mutation_effect": "NONE",
                    "attempt_ref_created": False,
                    "native_runtime": "NOT_RUN",
                },
            )
            write_o_excl(output / "RAW_OPERATION_EVIDENCE.json", evidence)
            return 2

        ruleset_id = named.get("id")
        if not isinstance(ruleset_id, int) or ruleset_id <= 0:
            raise AdminRulesetError("NAMED_RULESET_ID_INVALID")

        status, raw_details, details = request_json(
            "GET",
            f"/repos/{OWNER}/{REPO}/rulesets/{ruleset_id}",
            token=token,
        )
        evidence["steps"].append(
            {
                "operation": "GET_RULESET_DETAILS",
                "http_status": status,
                "ruleset_id": ruleset_id,
                "response_sha256": sha256_bytes(raw_details),
            }
        )
        if status != 200 or not isinstance(details, dict):
            raise AdminRulesetError(f"RULESET_DETAILS_HTTP_{status}")
        validated_id = validate_ruleset_details(details)

        encoded_branch = quote(ATTEMPT_BRANCH, safe="")
        status, raw_effective, effective = request_json(
            "GET",
            f"/repos/{OWNER}/{REPO}/rules/branches/{encoded_branch}",
            token=token,
        )
        evidence["steps"].append(
            {
                "operation": "GET_PROSPECTIVE_BRANCH_RULES",
                "http_status": status,
                "response_sha256": sha256_bytes(raw_effective),
            }
        )
        if status != 200:
            raise AdminRulesetError(f"PROSPECTIVE_RULES_HTTP_{status}")
        effective_types = validate_effective_rules(
            effective, ruleset_id=validated_id
        )

        ref_path = quote("heads/" + ATTEMPT_BRANCH, safe="/")
        status, raw_ref, _ = request_json(
            "GET",
            f"/repos/{OWNER}/{REPO}/git/ref/{ref_path}",
            token=token,
        )
        evidence["steps"].append(
            {
                "operation": "GET_EXACT_GLOBAL_ATTEMPT_REF",
                "http_status": status,
                "response_sha256": sha256_bytes(raw_ref),
            }
        )
        if status != 404:
            raise AdminRulesetError(
                f"GLOBAL_ATTEMPT_REF_NOT_ABSENT_HTTP_{status}"
            )

        mutation_receipt = {
            "schema": "rei-runtime-attempt-ref-ruleset-admin-mutation/v1",
            "status": (
                "PASS_RULESET_CREATED_AND_READ_BACK"
                if ruleset_created
                else "PASS_EXISTING_RULESET_READ_BACK"
            ),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "authority": AUTHORITY,
            "repository": REPOSITORY,
            "ruleset_id": validated_id,
            "ruleset_name": RULESET_NAME,
            "global_ref": GLOBAL_REF,
            "mutation_effect": (
                "RULESET_CREATED_ONLY" if ruleset_created else "NONE"
            ),
            "attempt_ref_created": False,
            "local_lease_created": False,
            "native_runtime": "NOT_RUN",
        }
        source_receipt = build_source_protection_receipt(
            ruleset_id=validated_id,
            details_raw=raw_details,
            effective_raw=raw_effective,
            ref_raw=raw_ref,
            all_effective_rule_types=effective_types,
        )
        write_o_excl(
            output / "ADMIN_MUTATION_RECEIPT.json", mutation_receipt
        )
        write_o_excl(
            output / "SOURCE_PROTECTION_RECEIPT.json", source_receipt
        )
        evidence["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        write_o_excl(output / "RAW_OPERATION_EVIDENCE.json", evidence)
        print(
            json.dumps(
                {
                    "status": mutation_receipt["status"],
                    "source_protection_status": source_receipt["status"],
                    "ruleset_id": validated_id,
                    "global_ref": "ABSENT_404",
                    "native_runtime": "NOT_RUN",
                },
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        evidence["failed_at_utc"] = datetime.now(timezone.utc).isoformat()
        evidence["first_blocker"] = f"{type(exc).__name__}:{exc}"
        evidence["ruleset_creation_may_have_occurred"] = ruleset_created
        try:
            write_o_excl(output / "INDETERMINATE_ADMIN_EVIDENCE.json", evidence)
        except Exception:
            pass
        print(f"STOP_INVALID: {type(exc).__name__}:{exc}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main())
