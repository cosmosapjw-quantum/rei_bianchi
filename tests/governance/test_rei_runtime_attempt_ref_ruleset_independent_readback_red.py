#!/usr/bin/env python3
"""Contract tests for independent ruleset mutation/readback auditing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "docs"
    / "rei_runtime_bridge_03a3r3_independent_readback"
    / "independent_readback_audit_v2.py"
)


def _load_future():
    spec = importlib.util.spec_from_file_location("rei_ruleset_readback", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _records(module):
    t0 = datetime(2026, 9, 4, 0, 0, 0, tzinfo=timezone.utc)
    admin = {
        "schema": "rei-runtime-attempt-ref-ruleset-admin-mutation/v1",
        "status": "PASS_RULESET_CREATED_AND_READ_BACK",
        "created_at_utc": (t0 + timedelta(seconds=1)).isoformat(),
        "authority": module.AUTHORITY,
        "repository": module.REPOSITORY,
        "ruleset_id": 42,
        "ruleset_name": module.RULESET_NAME,
        "global_ref": module.GLOBAL_REF,
        "mutation_effect": "RULESET_CREATED_ONLY",
        "attempt_ref_created": False,
        "local_lease_created": False,
        "native_runtime": "NOT_RUN",
    }
    source = {
        "schema": "rei-runtime-attempt-ref-protection-receipt/v1",
        "status": "PASS_ATTEMPT_REF_SERVER_PROTECTION",
        "generated_at_utc": (t0 + timedelta(seconds=2)).isoformat(),
        "expires_at_utc": (t0 + timedelta(seconds=302)).isoformat(),
        "authority": module.AUTHORITY,
        "repository": module.REPOSITORY,
        "global_ref": module.GLOBAL_REF,
        "target_pattern": module.TARGET_PATTERN,
        "prospective_branch": module.ATTEMPT_BRANCH,
        "prospective_branch_rules_http_status": 200,
        "ruleset_id": 42,
        "ruleset_name": module.RULESET_NAME,
        "ruleset_enforcement": "active",
        "active_rules": sorted(module.REQUIRED_RULES),
        "all_effective_rule_types": sorted(module.REQUIRED_RULES),
        "update_forbidden": True,
        "deletion_forbidden": True,
        "non_fast_forward_forbidden": True,
        "creation_restricted": False,
        "bypass_actors": [],
        "ruleset_detail_response_sha256": "1" * 64,
        "prospective_branch_rules_response_sha256": "2" * 64,
        "global_ref_absence_response_sha256": "3" * 64,
        "global_ref_http_status": 404,
        "global_ref_absent": True,
        "authorization_effect": "NONE",
        "mutation_effect": "NONE",
        "native_runtime": "NOT_RUN",
    }
    evidence = {
        "schema": "rei-runtime-03a3r2-admin-operation-evidence/v1",
        "started_at_utc": t0.isoformat(),
        "completed_at_utc": (t0 + timedelta(seconds=3)).isoformat(),
        "repository": module.REPOSITORY,
        "mode": "APPLY_RULESET_ONLY",
        "global_ref": module.GLOBAL_REF,
        "attempt_ref_mutation_permitted": False,
        "native_runtime_permitted": False,
        "steps": [
            {"operation": "GET_RULESET_LIST", "http_status": 200, "response_sha256": "a" * 64},
            {
                "operation": "POST_CREATE_RULESET",
                "http_status": 201,
                "request_sha256": module.sha256_bytes(
                    module.canonical_bytes(module.RULESET_PAYLOAD)
                ),
                "response_sha256": "c" * 64,
            },
            {"operation": "GET_RULESET_DETAILS", "http_status": 200, "ruleset_id": 42, "response_sha256": "1" * 64},
            {"operation": "GET_PROSPECTIVE_BRANCH_RULES", "http_status": 200, "response_sha256": "2" * 64},
            {"operation": "GET_EXACT_GLOBAL_ATTEMPT_REF", "http_status": 404, "response_sha256": "3" * 64},
        ],
    }
    return admin, source, evidence, t0


def _live(module):
    details = json.loads(json.dumps(module.RULESET_PAYLOAD))
    details["id"] = 42
    listed = [{"id": 42, "name": module.RULESET_NAME}]
    effective = [
        {"type": "update", "ruleset_id": 42},
        {"type": "deletion", "ruleset_id": 42},
        {"type": "non_fast_forward", "ruleset_id": 42},
    ]
    return listed, details, effective


def _write_bundle(module, root, admin, source, evidence):
    paths = []
    for name, value in (
        ("ADMIN_MUTATION_RECEIPT.json", admin),
        ("SOURCE_PROTECTION_RECEIPT.json", source),
        ("RAW_OPERATION_EVIDENCE.json", evidence),
    ):
        path = root / name
        path.write_bytes(module.canonical_bytes(value) + b"\n")
        paths.append(path)
    return paths


class IndependentRulesetReadbackExpectedRed(unittest.TestCase):
    def test_future_auditor_module_exists(self) -> None:
        module = _load_future()
        self.assertEqual(module.RECEIPT_TTL_SECONDS, 300)

    def test_admin_mutation_receipt_is_validated_separately(self) -> None:
        module = _load_future()
        admin, _, _, _ = _records(module)
        self.assertEqual(module.validate_admin_receipt(admin)["ruleset_id"], 42)

    def test_controller_source_receipt_contract_is_validated(self) -> None:
        module = _load_future()
        _, source, _, t0 = _records(module)
        validated = module.validate_source_protection_receipt(
            source, now=t0 + timedelta(seconds=4), require_current_freshness=True
        )
        self.assertEqual(validated["global_ref_http_status"], 404)

    def test_retrospective_evidence_order_and_hashes_are_cross_bound(self) -> None:
        module = _load_future()
        admin, source, evidence, _ = _records(module)
        result = module.validate_operation_evidence(evidence, admin, source)
        self.assertEqual(result["operations"][-1], "GET_EXACT_GLOBAL_ATTEMPT_REF")

    def test_three_input_files_must_form_one_canonical_bundle(self) -> None:
        module = _load_future()
        admin, source, evidence, t0 = _records(module)
        with tempfile.TemporaryDirectory() as temporary:
            paths = _write_bundle(
                module, Path(temporary), admin, source, evidence
            )
            bundle = module.validate_input_bundle(
                admin_path=paths[0],
                source_path=paths[1],
                evidence_path=paths[2],
                now=t0 + timedelta(seconds=4),
            )
            self.assertEqual(bundle["status"], "PASS_RETROSPECTIVE_ADMIN_BUNDLE")
            self.assertEqual(len(bundle["input_sha256"]), 3)

    def test_expired_original_receipt_remains_valid_historical_provenance(self) -> None:
        module = _load_future()
        admin, source, evidence, t0 = _records(module)
        with tempfile.TemporaryDirectory() as temporary:
            paths = _write_bundle(
                module, Path(temporary), admin, source, evidence
            )
            bundle = module.validate_input_bundle(
                admin_path=paths[0],
                source_path=paths[1],
                evidence_path=paths[2],
                now=t0 + timedelta(hours=1),
            )
            self.assertEqual(bundle["status"], "PASS_RETROSPECTIVE_ADMIN_BUNDLE")
            self.assertTrue(
                bundle["temporal_semantics"][
                    "historical_receipt_may_be_expired_now"
                ]
            )

    def test_original_operation_must_finish_before_source_receipt_expiry(self) -> None:
        module = _load_future()
        admin, source, evidence, t0 = _records(module)
        evidence["completed_at_utc"] = (t0 + timedelta(seconds=400)).isoformat()
        with self.assertRaisesRegex(
            module.ReadbackAuditError, "TIME_ORDER_INVALID"
        ):
            module.validate_operation_evidence(evidence, admin, source)

    def test_live_snapshot_is_independent_and_exact(self) -> None:
        module = _load_future()
        listed, details, effective = _live(module)
        live = module.validate_live_snapshot(
            ruleset_list=listed,
            ruleset_details=details,
            effective_rules=effective,
            ref_http_status=404,
            expected_ruleset_id=42,
        )
        self.assertEqual(live["ruleset_id"], 42)
        self.assertTrue(live["global_ref_absent"])

    def test_fresh_get_only_receipt_binds_audit_and_live_hashes(self) -> None:
        module = _load_future()
        _, _, _, t0 = _records(module)
        receipt = module.build_fresh_source_protection_receipt(
            ruleset_id=42,
            details_raw=b"details",
            effective_raw=b"effective",
            ref_raw=b"ref-404",
            all_effective_rule_types=sorted(module.REQUIRED_RULES),
            independent_audit_receipt_sha256="4" * 64,
            original_admin_receipt_sha256="5" * 64,
            original_source_receipt_sha256="6" * 64,
            created_at=t0,
        )
        self.assertEqual(receipt["mutation_effect"], "NONE")
        self.assertEqual(receipt["independent_audit_receipt_sha256"], "4" * 64)
        generated = datetime.fromisoformat(receipt["generated_at_utc"])
        expires = datetime.fromisoformat(receipt["expires_at_utc"])
        self.assertEqual((expires - generated).total_seconds(), 300)

    def test_network_surface_is_get_only(self) -> None:
        module = _load_future()
        with self.assertRaisesRegex(module.ReadbackAuditError, "HTTP_METHOD_FORBIDDEN"):
            module.request_json("POST", "/repos/x/y/rulesets", token="unused")

    def test_no_attempt_or_native_execution_surface_exists(self) -> None:
        _load_future()
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (
            'method="POST"',
            'method="PATCH"',
            'method="DELETE"',
            "native_runtime_worker",
            "successor_runtime_controller",
            "acquire_global_lease",
            "create_local_lease",
            "create_dispatch_intent",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
