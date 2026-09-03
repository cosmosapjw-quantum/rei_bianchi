#!/usr/bin/env python3
"""GREEN behavior tests for fixed authority and exact execution binding."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
PREFIX = "handoff.rei_runtime_prelease_import_firewall_green_20260903"
HEAD = "1" * 40
TREE = "2" * 40
SHA_A = "3" * 64
SHA_B = "4" * 64


def load_modules():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    common = importlib.import_module(f"{PREFIX}.common_v2")
    preflight = importlib.import_module(f"{PREFIX}.successor_section0_preflight")
    controller = importlib.import_module(f"{PREFIX}.successor_runtime_controller")
    return common, preflight, controller


class FakeResponse:
    def __init__(self, status: int, payload: dict) -> None:
        self.status = status
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class AuthorityBindingGreenTests(unittest.TestCase):
    def test_contract_and_fixed_authority_load(self) -> None:
        common, _, _ = load_modules()
        contract = common.load_contract()
        self.assertEqual(contract["schema"], "rei-runtime-prelease-import-firewall/v2")
        self.assertEqual(common.GITHUB_API_BASE, "https://api.github.com")
        self.assertEqual(common.GITHUB_REPOSITORY, "cosmosapjw-quantum/rei_bianchi")
        self.assertTrue(
            contract["attempt_ref_protection"][
                "required_before_global_reservation"
            ]
        )

    def test_executing_package_is_the_package_in_checked_out_head(self) -> None:
        common, _, _ = load_modules()
        bound = common.verify_executing_package_binding(ROOT, common.load_contract())
        self.assertEqual(bound, (ROOT / common.FIREWALL_PACKAGE_RELATIVE).resolve())

    def test_fixed_global_lease_endpoint_and_evidence_hashes(self) -> None:
        common, _, _ = load_modules()
        contract = common.load_contract()
        captured = []

        def fake_open(request, timeout=0):
            captured.append((request.full_url, request.get_method(), timeout))
            return FakeResponse(
                201,
                {
                    "ref": contract["attempt_budget"]["global_lease_ref"],
                    "object": {"sha": HEAD},
                },
            )

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "global.json"
            with mock.patch.object(common.urllib.request, "urlopen", fake_open):
                record = common.acquire_global_lease(
                    contract=contract,
                    release_head=HEAD,
                    successor_receipt_sha256=SHA_A,
                    preflight_receipt_sha256=SHA_B,
                    attempt_ref_protection_receipt_sha256="5" * 64,
                    prelease_toolchain_revalidation_sha256="6" * 64,
                    token="test-token",
                    output=output,
                )
            self.assertEqual(
                captured,
                [
                    (
                        "https://api.github.com/repos/"
                        "cosmosapjw-quantum/rei_bianchi/git/refs",
                        "POST",
                        30,
                    )
                ],
            )
            self.assertEqual(record["authority"], common.GITHUB_AUTHORITY)
            self.assertEqual(
                record["attempt_ref_protection_receipt_sha256"], "5" * 64
            )
            self.assertEqual(
                record["prelease_toolchain_revalidation_sha256"], "6" * 64
            )

    def test_protection_receipt_requires_all_server_rules(self) -> None:
        common, _, _ = load_modules()
        contract = common.load_contract()
        rule = contract["attempt_ref_protection"]
        receipt = {
            "schema": rule["required_schema"],
            "status": rule["required_status"],
            "authority": common.GITHUB_AUTHORITY,
            "repository": common.GITHUB_REPOSITORY,
            "global_ref": common.GLOBAL_ATTEMPT_REF,
            "target_pattern": rule["target_pattern"],
            "prospective_branch_rules_http_status": 200,
            "active_rules": list(rule["required_rules"]),
            "update_forbidden": True,
            "deletion_forbidden": True,
            "non_fast_forward_forbidden": True,
            "bypass_actors": [],
            "authorization_effect": "NONE",
            "mutation_effect": "NONE",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "protection.json"
            path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            common.validate_attempt_ref_protection(
                path,
                contract=contract,
                expected_global_ref=common.GLOBAL_ATTEMPT_REF,
            )
            receipt["deletion_forbidden"] = False
            path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(
                common.FirewallError,
                "ATTEMPT_REF_PROTECTION_RECEIPT_MISMATCH",
            ):
                common.validate_attempt_ref_protection(
                    path,
                    contract=contract,
                    expected_global_ref=common.GLOBAL_ATTEMPT_REF,
                )

    def test_preflight_receipt_path_and_authority_mutation_is_rejected(self) -> None:
        common, _, _ = load_modules()
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            output = root / "output"
            state.mkdir()
            output.mkdir()
            successor = output / "successor.json"
            successor.write_text("{}\n", encoding="utf-8")
            observation = {
                "status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED",
                "ordinal": 1,
                "method": "GET",
                "http_status": 404,
                "authority": common.GITHUB_AUTHORITY,
                "api_host": common.GITHUB_API_HOST,
                "repository": common.GITHUB_REPOSITORY,
                "ref": common.GLOBAL_ATTEMPT_REF,
                "expected_target": HEAD,
                "authorization_effect": "NONE",
                "global_lease_acquired": False,
            }
            receipt = {
                "schema": "rei-runtime-prelease-import-firewall-preflight-receipt/v2",
                "status": "PASS_READ_ONLY_STATIC_PREFLIGHT",
                "generated_at_utc": now.isoformat(),
                "expires_at_utc": (now + timedelta(minutes=10)).isoformat(),
                "authority": common.GITHUB_AUTHORITY,
                "firewall_release": {"commit": HEAD, "tree": TREE},
                "successor_section0_receipt": str(successor.resolve()),
                "successor_section0_receipt_sha256": SHA_A,
                "global_ref_observations": [
                    observation,
                    {**observation, "ordinal": 2},
                ],
                "attempt_state": {
                    "global_lease_acquired": False,
                    "local_lease_created": False,
                    "dispatch_intent_created": False,
                    "remaining_attempts": 1,
                    "absence_is_authorization": False,
                },
                "static_checks": {
                    "production_module_loaded": False,
                    "standalone_clone_verified": True,
                    "pinned_source_bytes_verified": True,
                    "closed_runtime_package_verified": True,
                    "executing_package_bound_to_head": True,
                },
                "attempt_state_root": str(state.resolve()),
                "output_root": str(output.resolve()),
                "native_runtime": "NOT_RUN",
            }
            path = output / "preflight.json"
            path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            common.validate_preflight_receipt(
                path,
                expected_head=HEAD,
                expected_tree=TREE,
                successor_receipt_sha256=SHA_A,
                expected_attempt_state_root=state,
                expected_output_root=output,
                expected_successor_receipt_path=successor,
                expected_authority=common.GITHUB_AUTHORITY,
                expected_global_ref=common.GLOBAL_ATTEMPT_REF,
            )
            receipt["global_ref_observations"][1]["repository"] = "other/repo"
            path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(
                common.FirewallError,
                "READ_ONLY_PREFLIGHT_REF_OBSERVATIONS_INVALID",
            ):
                common.validate_preflight_receipt(
                    path,
                    expected_head=HEAD,
                    expected_tree=TREE,
                    successor_receipt_sha256=SHA_A,
                    expected_attempt_state_root=state,
                    expected_output_root=output,
                    expected_successor_receipt_path=successor,
                    expected_authority=common.GITHUB_AUTHORITY,
                    expected_global_ref=common.GLOBAL_ATTEMPT_REF,
                )

    def test_no_production_entry_is_performed_by_this_suite(self) -> None:
        _, preflight, controller = load_modules()
        self.assertFalse(hasattr(preflight, "load_bridge"))
        self.assertFalse(hasattr(controller, "load_bridge"))
        self.assertEqual(os.environ.get("REI_NATIVE_DISPATCH_FORBIDDEN"), "1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
