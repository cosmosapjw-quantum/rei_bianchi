#!/usr/bin/env python3
"""Intentional RED contract for stale server-protection evidence."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
OLD_PREFIX = "handoff.rei_runtime_prelease_import_firewall_green_20260903"
NEW_PREFIX = "handoff.rei_runtime_attempt_ref_protection_freshness_20260904"


class AttemptRefProtectionFreshnessExpectedRed(unittest.TestCase):
    def _new(self):
        return importlib.import_module(f"{NEW_PREFIX}.protection_live")

    def _old_common(self):
        return importlib.import_module(f"{OLD_PREFIX}.common_v2")

    def test_source_successor_module_exists(self) -> None:
        module = self._new()
        self.assertEqual(module.PROTECTION_RECEIPT_MAX_AGE_SECONDS, 300)

    def test_stale_receipt_is_rejected(self) -> None:
        module = self._new()
        common = self._old_common()
        contract = common.load_contract()
        rule = contract["attempt_ref_protection"]
        old = datetime.now(timezone.utc) - timedelta(hours=1)
        receipt = {
            "schema": rule["required_schema"],
            "status": rule["required_status"],
            "generated_at_utc": old.isoformat(),
            "expires_at_utc": (old + timedelta(minutes=5)).isoformat(),
            "authority": common.GITHUB_AUTHORITY,
            "repository": common.GITHUB_REPOSITORY,
            "global_ref": common.GLOBAL_ATTEMPT_REF,
            "target_pattern": rule["target_pattern"],
            "prospective_branch": common.GLOBAL_ATTEMPT_REF.removeprefix("refs/heads/"),
            "prospective_branch_rules_http_status": 200,
            "ruleset_id": 42,
            "ruleset_name": "rei-attempt-ledger-append-only-v1",
            "ruleset_detail_sha256": "1" * 64,
            "effective_rules_sha256": "2" * 64,
            "active_rules": list(rule["required_rules"]),
            "update_forbidden": True,
            "deletion_forbidden": True,
            "non_fast_forward_forbidden": True,
            "creation_restricted": False,
            "bypass_actors": [],
            "global_ref_http_status": 404,
            "global_ref_absent": True,
            "authorization_effect": "NONE",
            "mutation_effect": "NONE",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "protection.json"
            path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(
                common.FirewallError,
                "ATTEMPT_REF_PROTECTION_FRESHNESS_INVALID",
            ):
                module.validate_fresh_attempt_ref_protection(
                    path,
                    contract=contract,
                    expected_global_ref=common.GLOBAL_ATTEMPT_REF,
                )

    def test_live_revalidation_is_required_after_toolchain_and_before_reservation(self) -> None:
        controller = ROOT / NEW_PREFIX.replace(".", "/") / "successor_runtime_controller.py"
        source = controller.read_text(encoding="utf-8")
        toolchain = source.index("revalidate_successor_toolchain(")
        live = source.index("revalidate_attempt_ref_protection_live(")
        indeterminate = source.index("reservation_may_have_occurred = True")
        reserve = source.index("acquire_global_lease(")
        self.assertLess(toolchain, live)
        self.assertLess(live, indeterminate)
        self.assertLess(indeterminate, reserve)

    def test_global_lease_binds_live_snapshot_not_only_static_receipt(self) -> None:
        controller = ROOT / NEW_PREFIX.replace(".", "/") / "successor_runtime_controller.py"
        source = controller.read_text(encoding="utf-8")
        self.assertIn(
            "attempt_ref_protection_receipt_sha256=live_protection_sha",
            source,
        )
        self.assertIn("source_protection_receipt_sha256", source)

    def test_live_revalidator_has_no_mutation_or_production_import(self) -> None:
        module_path = ROOT / NEW_PREFIX.replace(".", "/") / "protection_live.py"
        source = module_path.read_text(encoding="utf-8")
        self.assertNotIn('method="POST"', source)
        self.assertNotIn('method="PATCH"', source)
        self.assertNotIn('method="DELETE"', source)
        self.assertNotIn("load_bridge", source)
        self.assertIn('method="GET"', source)

    def test_contract_forbids_stale_or_nonlive_protection(self) -> None:
        contract_path = ROOT / NEW_PREFIX.replace(".", "/") / "CONTRACT.json"
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self.assertEqual(contract["protection_receipt_max_age_seconds"], 300)
        self.assertTrue(contract["live_revalidation_immediately_before_reservation"])
        self.assertEqual(contract["native_runtime"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
