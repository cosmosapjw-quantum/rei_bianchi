#!/usr/bin/env python3
"""Active semantic repair for independent REI ruleset readback auditing.

The v1 module remains the byte-pinned implementation donor. This active
surface separates historical receipt validity from current authorization and
also accepts GitHub's normalized GET representation of an active update rule,
which may omit request-only parameters. The locally owned creation payload
remains strict in the byte-pinned administrator client.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping
from urllib.parse import quote


PACKAGE = Path(__file__).resolve().parent
DONOR_PATH = PACKAGE / "independent_readback_audit.py"
DONOR_BLOB = "cafacff7090e10a1419a211a564d4da0fd484098"
SCRIPT_RELATIVE = (
    "docs/rei_runtime_bridge_03a3r3_independent_readback/"
    "independent_readback_audit_v2.py"
)
INDEX_RELATIVE = (
    "docs/rei_runtime_bridge_03a3r3_independent_readback/SOURCE_INDEX.json"
)

_spec = importlib.util.spec_from_file_location(
    "rei_runtime_independent_readback_v1_donor", DONOR_PATH
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("V1_DONOR_IMPORT_SPEC_UNAVAILABLE")
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

API_BASE = _v1.API_BASE
API_VERSION = _v1.API_VERSION
REPOSITORY = _v1.REPOSITORY
OWNER = _v1.OWNER
REPO = _v1.REPO
RULESET_NAME = _v1.RULESET_NAME
TARGET_PATTERN = _v1.TARGET_PATTERN
ATTEMPT_BRANCH = _v1.ATTEMPT_BRANCH
GLOBAL_REF = _v1.GLOBAL_REF
REQUIRED_RULES = _v1.REQUIRED_RULES
RECEIPT_TTL_SECONDS = _v1.RECEIPT_TTL_SECONDS
FUTURE_CLOCK_SKEW_SECONDS = _v1.FUTURE_CLOCK_SKEW_SECONDS
AUTHORITY = _v1.AUTHORITY
RULESET_PAYLOAD = _v1.RULESET_PAYLOAD
PARENT_ADMIN_RELATIVE = _v1.PARENT_ADMIN_RELATIVE
PARENT_ADMIN_BLOB = "0b1b56d6dcaf2bc4ed68ba938ad20feeaeab0ecf"

ReadbackAuditError = _v1.ReadbackAuditError
canonical_bytes = _v1.canonical_bytes
sha256_bytes = _v1.sha256_bytes
sha256_file = _v1.sha256_file
_parse_utc = _v1._parse_utc
_mapping = _v1._mapping
_valid_hex = _v1._valid_hex
validate_admin_receipt = _v1.validate_admin_receipt
validate_source_protection_receipt = _v1.validate_source_protection_receipt
find_named_ruleset = _v1.find_named_ruleset
build_fresh_source_protection_receipt = (
    _v1.build_fresh_source_protection_receipt
)
request_json = _v1.request_json


def validate_update_rule(details: Mapping[str, Any]) -> str:
    """Validate GitHub's active update-rule GET representation.

    GitHub currently returns either the explicit request-like representation
    or the normalized ``{"type":"update"}`` representation. Omission is
    accepted only here, on the fixed-authority GET-only independent readback
    surface. Explicit malformed or permissive parameters remain rejected.
    """

    rows = details.get("rules")
    if not isinstance(rows, list):
        raise ReadbackAuditError("LIVE_RULESET_RULES_INVALID")
    updates = [
        row
        for row in rows
        if isinstance(row, dict) and row.get("type") == "update"
    ]
    if len(updates) != 1:
        raise ReadbackAuditError("LIVE_RULESET_UPDATE_POLICY_MISMATCH")
    update = updates[0]
    if "parameters" not in update:
        if set(update) != {"type"}:
            raise ReadbackAuditError("LIVE_RULESET_UPDATE_POLICY_MISMATCH")
        return "GITHUB_GET_NORMALIZED_PARAMETERS_OMITTED"
    parameters = update["parameters"]
    if (
        not isinstance(parameters, Mapping)
        or set(parameters) != {"update_allows_fetch_and_merge"}
        or parameters.get("update_allows_fetch_and_merge") is not False
    ):
        raise ReadbackAuditError("LIVE_RULESET_UPDATE_POLICY_MISMATCH")
    return "EXPLICIT_FALSE"


def validate_ruleset_details(details: Mapping[str, Any]) -> int:
    value = _mapping(details, "LIVE_RULESET_DETAILS_NOT_OBJECT")
    condition = value.get("conditions", {}).get("ref_name", {})
    types = _v1._rule_types(value)
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
    validate_update_rule(value)
    ruleset_id = value.get("id")
    if not isinstance(ruleset_id, int) or ruleset_id <= 0:
        raise ReadbackAuditError("LIVE_RULESET_ID_INVALID")
    return ruleset_id


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
    supplied = set()
    all_types = set()
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
        "update_rule_readback": validate_update_rule(ruleset_details),
        "all_effective_rule_types": sorted(all_types),
        "global_ref_absent": True,
    }


def validate_operation_evidence(
    evidence: Mapping[str, Any],
    admin: Mapping[str, Any],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate original execution and require completion within its TTL."""

    result = _v1.validate_operation_evidence(evidence, admin, source)
    completed = _parse_utc(
        evidence.get("completed_at_utc"), "OPERATION_EVIDENCE_TIME_INVALID"
    )
    expires = _parse_utc(
        source.get("expires_at_utc"), "SOURCE_RECEIPT_TIME_INVALID"
    )
    if completed > expires:
        raise ReadbackAuditError("OPERATION_EVIDENCE_TIME_ORDER_INVALID")
    result = dict(result)
    result["original_source_receipt_valid_at_completion"] = True
    result["original_source_receipt_current_freshness_required"] = False
    return result


def validate_input_bundle(
    *,
    admin_path: Path,
    source_path: Path,
    evidence_path: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate historical evidence without imposing current-time freshness."""

    del now
    paths = [Path(admin_path), Path(source_path), Path(evidence_path)]
    if any(not path.is_absolute() or path.is_symlink() for path in paths):
        raise ReadbackAuditError("INPUT_BUNDLE_PATH_INVALID")
    try:
        resolved = [path.resolve(strict=True) for path in paths]
    except (OSError, RuntimeError) as exc:
        raise ReadbackAuditError("INPUT_BUNDLE_PATH_INVALID") from exc
    if len({path.parent for path in resolved}) != 1:
        raise ReadbackAuditError("INPUT_BUNDLE_NOT_COLOCATED")

    admin = _v1._load_canonical_json(
        paths[0], "ADMIN_RECEIPT_UNREADABLE"
    )
    source = _v1._load_canonical_json(
        paths[1], "SOURCE_RECEIPT_UNREADABLE"
    )
    evidence = _v1._load_canonical_json(
        paths[2], "OPERATION_EVIDENCE_UNREADABLE"
    )
    admin_value = validate_admin_receipt(admin)
    source_value = validate_source_protection_receipt(
        source,
        require_current_freshness=False,
    )
    operation = validate_operation_evidence(
        evidence, admin_value, source_value
    )
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
        "temporal_semantics": {
            "historical_receipt_may_be_expired_now": True,
            "historical_receipt_valid_at_operation_completion": True,
            "current_state_requires_fresh_live_get": True,
        },
    }


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
            "GIT_READ_FAILED:"
            + " ".join(args)
            + ":"
            + completed.stderr.strip()
        )
    return completed.stdout.strip()


def verify_executing_release(
    repo: Path,
    *,
    expected_head: str,
    expected_tree: str,
) -> Path:
    """Bind the active surface, donor, admin generator, and index to HEAD."""

    root = Path(repo).resolve(strict=True)
    if (
        not root.is_dir()
        or not _valid_hex(expected_head, 40)
        or not _valid_hex(expected_tree, 40)
    ):
        raise ReadbackAuditError("RELEASE_IDENTITY_ARGUMENT_INVALID")
    expected_script = (root / SCRIPT_RELATIVE).resolve(strict=True)
    if expected_script != Path(__file__).resolve(strict=True):
        raise ReadbackAuditError(
            "EXECUTING_AUDITOR_OUTSIDE_VERIFIED_RELEASE"
        )
    if (
        _git_text(root, "rev-parse", "HEAD") != expected_head
        or _git_text(root, "rev-parse", "HEAD^{tree}") != expected_tree
    ):
        raise ReadbackAuditError("EXECUTING_RELEASE_IDENTITY_MISMATCH")
    origin = _git_text(root, "config", "--get", "remote.origin.url")
    if "cosmosapjw-quantum/rei_bianchi" not in origin:
        raise ReadbackAuditError("EXECUTING_RELEASE_ORIGIN_MISMATCH")

    for relative, expected_blob in (
        (SCRIPT_RELATIVE, None),
        (
            "docs/rei_runtime_bridge_03a3r3_independent_readback/"
            "independent_readback_audit.py",
            DONOR_BLOB,
        ),
        (PARENT_ADMIN_RELATIVE, PARENT_ADMIN_BLOB),
    ):
        worktree_blob = _git_text(root, "hash-object", relative)
        head_blob = _git_text(root, "rev-parse", f"HEAD:{relative}")
        if worktree_blob != head_blob or (
            expected_blob is not None and head_blob != expected_blob
        ):
            raise ReadbackAuditError(
                f"EXECUTING_RELEASE_BLOB_MISMATCH:{relative}"
            )

    verifier = (root / INDEX_RELATIVE).with_name(
        "verify_source_index.py"
    )
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


def _live_readback(
    *, token: str, expected_ruleset_id: int
) -> tuple[dict[str, Any], dict[str, bytes]]:
    """Perform the fixed-authority GET-only live readback."""

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
    """Audit historical provenance, then establish current live evidence."""

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
    snapshot, raw = _live_readback(
        token=token, expected_ruleset_id=ruleset_id
    )
    now = datetime.now(timezone.utc)
    audit_record = {
        "schema": "rei-runtime-attempt-ref-ruleset-independent-readback/v2",
        "status": (
            "PASS_INDEPENDENT_ATTEMPT_REF_RULESET_READBACK_AUDIT"
        ),
        "generated_at_utc": now.isoformat(),
        "authority": AUTHORITY,
        "repository": REPOSITORY,
        "auditor_release": {
            "commit": expected_head,
            "tree": expected_tree,
        },
        "admin_bundle_root": bundle["root"],
        "input_sha256": bundle["input_sha256"],
        "retrospective_provenance": bundle["operation"]["status"],
        "temporal_semantics": bundle["temporal_semantics"],
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
        "next_gate": (
            "TARGET_HOST_STATIC_PREFLIGHT_AFTER_SEPARATE_REVIEW"
        ),
    }
    audit_payload = canonical_bytes(audit_record) + b"\n"
    audit_sha = sha256_bytes(audit_payload)
    fresh_record = build_fresh_source_protection_receipt(
        ruleset_id=ruleset_id,
        details_raw=raw["ruleset_details"],
        effective_raw=raw["effective_rules"],
        ref_raw=raw["global_ref"],
        all_effective_rule_types=snapshot[
            "all_effective_rule_types"
        ],
        independent_audit_receipt_sha256=audit_sha,
        original_admin_receipt_sha256=bundle["input_sha256"][
            "admin_mutation_receipt"
        ],
        original_source_receipt_sha256=bundle["input_sha256"][
            "source_protection_receipt"
        ],
        created_at=now,
    )
    target = _v1._validate_output_target(Path(output_root), repo=root)
    _v1._publish_atomic_bundle(
        target,
        audit_record=audit_record,
        fresh_record=fresh_record,
    )
    return {
        "status": audit_record["status"],
        "output_root": str(target),
        "audit_receipt_sha256": audit_sha,
        "fresh_source_receipt_sha256": sha256_bytes(
            canonical_bytes(fresh_record) + b"\n"
        ),
        "historical_receipt_current_freshness_required": False,
        "fresh_live_readback_completed": True,
        "update_rule_readback": snapshot["update_rule_readback"],
        "global_ref": "ABSENT_404",
        "native_runtime": "NOT_RUN",
    }


def _self_test() -> dict[str, Any]:
    result = dict(_v1._self_test())
    normalized = json.loads(json.dumps(RULESET_PAYLOAD))
    normalized["id"] = 42
    normalized["rules"][0] = {"type": "update"}
    result["status"] = "PASS_INDEPENDENT_READBACK_V2_SELF_TEST"
    result["historical_receipt_current_freshness_required"] = False
    result["original_operation_must_finish_before_expiry"] = True
    result["normalized_update_get"] = validate_update_rule(normalized)
    result["parent_admin_blob"] = PARENT_ADMIN_BLOB
    return result


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
