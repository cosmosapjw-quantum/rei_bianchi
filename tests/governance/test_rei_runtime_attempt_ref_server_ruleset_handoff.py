#!/usr/bin/env python3
"""Offline contract tests for the REI admin-only ruleset handoff."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "docs"
    / "rei_runtime_bridge_03a3r2_admin_ruleset"
    / "apply_and_attest_ruleset.py"
)
SPEC = importlib.util.spec_from_file_location("rei_admin_ruleset", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def exact_details() -> dict:
    value = json.loads(json.dumps(MOD.RULESET_PAYLOAD))
    value["id"] = 42
    return value


def effective_rules() -> list[dict]:
    return [
        {"type": "update", "ruleset_id": 42},
        {"type": "deletion", "ruleset_id": 42},
        {"type": "non_fast_forward", "ruleset_id": 42},
    ]


class AdminRulesetHandoffTests(unittest.TestCase):
    def test_payload_allows_initial_creation_and_forbids_later_mutation(self) -> None:
        types = {row["type"] for row in MOD.RULESET_PAYLOAD["rules"]}
        self.assertEqual(types, MOD.REQUIRED_RULES)
        self.assertNotIn("creation", types)
        self.assertEqual(MOD.RULESET_PAYLOAD["bypass_actors"], [])
        self.assertEqual(MOD.RULESET_PAYLOAD["enforcement"], "active")

    def test_exact_ruleset_details_pass(self) -> None:
        self.assertEqual(MOD.validate_ruleset_details(exact_details()), 42)

    def test_github_normalized_get_may_omit_update_parameters(self) -> None:
        value = exact_details()
        value["rules"][0] = {"type": "update"}
        self.assertEqual(MOD.validate_ruleset_details(value), 42)
        self.assertEqual(
            MOD.validate_update_rule(
                value,
                allow_omitted_parameters=True,
            ),
            "GITHUB_GET_NORMALIZED_PARAMETERS_OMITTED",
        )

    def test_creation_payload_still_requires_explicit_false_parameter(self) -> None:
        value = exact_details()
        value["rules"][0] = {"type": "update"}
        with self.assertRaisesRegex(MOD.AdminRulesetError, "UPDATE_POLICY"):
            MOD.validate_ruleset_details(
                value,
                allow_omitted_update_parameters=False,
            )

    def test_disabled_or_bypassed_ruleset_is_rejected(self) -> None:
        disabled = exact_details()
        disabled["enforcement"] = "disabled"
        with self.assertRaisesRegex(MOD.AdminRulesetError, "MISMATCH"):
            MOD.validate_ruleset_details(disabled)
        bypassed = exact_details()
        bypassed["bypass_actors"] = [{"actor_id": 1}]
        with self.assertRaisesRegex(MOD.AdminRulesetError, "MISMATCH"):
            MOD.validate_ruleset_details(bypassed)

    def test_creation_rule_or_wrong_pattern_is_rejected(self) -> None:
        creation = exact_details()
        creation["rules"].append({"type": "creation"})
        with self.assertRaisesRegex(MOD.AdminRulesetError, "MISMATCH"):
            MOD.validate_ruleset_details(creation)
        pattern = exact_details()
        pattern["conditions"]["ref_name"]["include"] = ["refs/heads/*"]
        with self.assertRaisesRegex(MOD.AdminRulesetError, "MISMATCH"):
            MOD.validate_ruleset_details(pattern)

    def test_update_policy_must_disable_fetch_and_merge(self) -> None:
        value = exact_details()
        value["rules"][0]["parameters"]["update_allows_fetch_and_merge"] = True
        with self.assertRaisesRegex(MOD.AdminRulesetError, "UPDATE_POLICY"):
            MOD.validate_ruleset_details(value)

    def test_effective_rules_must_come_from_the_exact_ruleset(self) -> None:
        self.assertEqual(
            MOD.validate_effective_rules(effective_rules(), ruleset_id=42),
            ["deletion", "non_fast_forward", "update"],
        )
        wrong = effective_rules()
        wrong[-1]["ruleset_id"] = 7
        with self.assertRaisesRegex(MOD.AdminRulesetError, "MISSING"):
            MOD.validate_effective_rules(wrong, ruleset_id=42)

    def test_effective_creation_restriction_is_rejected(self) -> None:
        value = effective_rules() + [{"type": "creation", "ruleset_id": 42}]
        with self.assertRaisesRegex(MOD.AdminRulesetError, "CREATION"):
            MOD.validate_effective_rules(value, ruleset_id=42)

    def test_source_receipt_is_get_only_and_fresh(self) -> None:
        now = datetime(2026, 9, 4, tzinfo=timezone.utc)
        record = MOD.build_source_protection_receipt(
            ruleset_id=42,
            details_raw=b"details",
            effective_raw=b"effective",
            ref_raw=b"ref-404",
            all_effective_rule_types=[
                "deletion",
                "non_fast_forward",
                "update",
            ],
            created_at=now,
        )
        self.assertEqual(
            record["schema"],
            "rei-runtime-attempt-ref-protection-receipt/v1",
        )
        self.assertEqual(
            record["status"], "PASS_ATTEMPT_REF_SERVER_PROTECTION"
        )
        self.assertEqual(record["mutation_effect"], "NONE")
        self.assertEqual(record["authorization_effect"], "NONE")
        self.assertTrue(record["global_ref_absent"])
        self.assertFalse(record["creation_restricted"])
        generated = datetime.fromisoformat(record["generated_at_utc"])
        expires = datetime.fromisoformat(record["expires_at_utc"])
        self.assertEqual((expires - generated).total_seconds(), 300)

    def test_only_ruleset_endpoint_is_postable(self) -> None:
        with self.assertRaisesRegex(MOD.AdminRulesetError, "POST_TARGET_FORBIDDEN"):
            MOD.request_json(
                "POST",
                f"/repos/{MOD.OWNER}/{MOD.REPO}/git/refs",
                token="not-used",
                payload={"ref": MOD.GLOBAL_REF, "sha": "0" * 40},
            )

    def test_source_contains_no_runtime_or_attempt_dispatch_surface(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("native_runtime_worker", source)
        self.assertNotIn("successor_runtime_controller", source)
        self.assertNotIn("load_bridge", source)
        self.assertNotIn("run_native_once", source)
        self.assertNotIn("FIRST_CANONICAL_INTERVAL", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
