#!/usr/bin/env python3
"""Behavior tests for freshness and live pre-reservation protection."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error


ROOT = Path(__file__).resolve().parents[2]
PREFIX = "handoff.rei_runtime_attempt_ref_protection_freshness_20260904"
OLD_PREFIX = "handoff.rei_runtime_prelease_import_firewall_green_20260903"
HEAD = "1" * 40


def modules():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    protection = importlib.import_module(f"{PREFIX}.protection_live")
    lease = importlib.import_module(f"{PREFIX}.lease_bound")
    old = importlib.import_module(f"{OLD_PREFIX}.common_v2")
    return protection, lease, old


class FakeResponse:
    def __init__(self, status: int, payload) -> None:
        self.status = status
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return self._raw


def static_receipt(old, path: Path, *, now: datetime) -> Path:
    contract = old.load_contract()
    rule = contract["attempt_ref_protection"]
    record = {
        "schema": rule["required_schema"],
        "status": rule["required_status"],
        "generated_at_utc": now.isoformat(),
        "expires_at_utc": (now + timedelta(minutes=5)).isoformat(),
        "authority": old.GITHUB_AUTHORITY,
        "repository": old.GITHUB_REPOSITORY,
        "global_ref": old.GLOBAL_ATTEMPT_REF,
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
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    return path


def fake_live_opener(*, include_creation: bool = False, bypass=False):
    calls = []

    def open_request(request, timeout=0):
        calls.append((request.full_url, request.get_method(), timeout))
        if "/rules/branches/" in request.full_url:
            rows = [
                {"type": "update", "ruleset_id": 42},
                {"type": "deletion", "ruleset_id": 42},
                {"type": "non_fast_forward", "ruleset_id": 42},
            ]
            if include_creation:
                rows.append({"type": "creation", "ruleset_id": 42})
            return FakeResponse(200, rows)
        if request.full_url.endswith("/rulesets/42"):
            rules = [
                {"type": "update"},
                {"type": "deletion"},
                {"type": "non_fast_forward"},
            ]
            if include_creation:
                rules.append({"type": "creation"})
            return FakeResponse(
                200,
                {
                    "id": 42,
                    "target": "branch",
                    "enforcement": "active",
                    "bypass_actors": [{"actor_id": 7}] if bypass else [],
                    "conditions": {
                        "ref_name": {
                            "include": ["refs/heads/attempt-ledger/**"],
                            "exclude": [],
                        }
                    },
                    "rules": rules,
                },
            )
        if "/git/ref/heads/" in request.full_url:
            raise urllib.error.HTTPError(
                request.full_url,
                404,
                "Not Found",
                {},
                io.BytesIO(b'{"message":"Not Found"}'),
            )
        raise AssertionError(f"UNEXPECTED_URL:{request.full_url}")

    return calls, open_request


class FreshnessLiveGreenTests(unittest.TestCase):
    def test_contract_is_nonexecuting_and_bounded(self) -> None:
        protection, _, _ = modules()
        contract = protection.load_contract()
        self.assertEqual(contract["protection_receipt_max_age_seconds"], 300)
        self.assertEqual(contract["live_readback_max_age_seconds"], 120)
        self.assertTrue(contract["live_revalidation_immediately_before_reservation"])
        self.assertEqual(contract["native_runtime"], "NOT_RUN")

    def test_stale_static_receipt_is_rejected(self) -> None:
        protection, _, old = modules()
        now = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as temporary:
            path = static_receipt(
                old,
                Path(temporary) / "source.json",
                now=now - timedelta(hours=1),
            )
            with self.assertRaisesRegex(
                old.FirewallError,
                "ATTEMPT_REF_PROTECTION_FRESHNESS_INVALID",
            ):
                protection.validate_fresh_attempt_ref_protection(
                    path,
                    contract=old.load_contract(),
                    expected_global_ref=old.GLOBAL_ATTEMPT_REF,
                    now=now,
                )

    def test_live_get_only_readback_is_hash_bound(self) -> None:
        protection, _, old = modules()
        now = datetime.now(timezone.utc)
        calls, opener = fake_live_opener()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = static_receipt(old, root / "source.json", now=now)
            output = root / "live.json"
            record = protection.revalidate_attempt_ref_protection_live(
                source_protection_receipt=source,
                contract=old.load_contract(),
                expected_global_ref=old.GLOBAL_ATTEMPT_REF,
                expected_release_head=HEAD,
                token="test-token",
                output=output,
                opener=opener,
                now=now,
            )
            self.assertEqual(
                record["status"],
                "PASS_LIVE_ATTEMPT_REF_SERVER_PROTECTION",
            )
            self.assertTrue(record["global_ref_absent"])
            self.assertFalse(record["creation_forbidden"])
            self.assertEqual(record["bypass_actors"], [])
            self.assertEqual({method for _, method, _ in calls}, {"GET"})
            self.assertEqual(len(calls), 3)
            protection.validate_live_attempt_ref_protection(
                output,
                source_protection_receipt=source,
                contract=old.load_contract(),
                expected_global_ref=old.GLOBAL_ATTEMPT_REF,
                expected_release_head=HEAD,
                now=now,
            )

    def test_live_creation_rule_and_bypass_actor_are_rejected(self) -> None:
        protection, _, old = modules()
        now = datetime.now(timezone.utc)
        for kwargs, expected in (
            ({"include_creation": True}, "CREATION_RULE_FORBIDDEN"),
            ({"bypass": True}, "LIVE_RULESET_DETAILS_INVALID"),
        ):
            _, opener = fake_live_opener(**kwargs)
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = static_receipt(old, root / "source.json", now=now)
                with self.assertRaisesRegex(old.FirewallError, expected):
                    protection.revalidate_attempt_ref_protection_live(
                        source_protection_receipt=source,
                        contract=old.load_contract(),
                        expected_global_ref=old.GLOBAL_ATTEMPT_REF,
                        expected_release_head=HEAD,
                        token="test-token",
                        output=root / "live.json",
                        opener=opener,
                        now=now,
                    )

    def test_global_lease_records_static_live_and_runtime_path_hashes(self) -> None:
        _, lease, old = modules()
        captured = []

        def opener(request, timeout=0):
            captured.append((request.full_url, request.get_method(), timeout))
            return FakeResponse(
                201,
                {
                    "ref": old.GLOBAL_ATTEMPT_REF,
                    "object": {"sha": HEAD},
                },
            )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            live = root / "live.json"
            source.write_text("source\n", encoding="utf-8")
            live.write_text("live\n", encoding="utf-8")
            source_sha = old.sha256_file(source)
            live_sha = old.sha256_file(live)
            output = root / "global.json"
            record = lease.acquire_global_lease(
                contract=old.load_contract(),
                release_head=HEAD,
                successor_receipt_sha256="3" * 64,
                preflight_receipt_sha256="4" * 64,
                attempt_ref_protection_receipt_sha256=live_sha,
                source_protection_receipt_sha256=source_sha,
                source_protection_receipt=source,
                live_protection_receipt=live,
                prelease_toolchain_revalidation_sha256="5" * 64,
                runtime_toolchain_snapshot_sha256="6" * 64,
                token="test-token",
                output=output,
                opener=opener,
            )
            self.assertEqual(
                record["source_protection_receipt_sha256"], source_sha
            )
            self.assertEqual(
                record["live_attempt_ref_protection_readback_sha256"],
                live_sha,
            )
            self.assertEqual(
                record["runtime_toolchain_snapshot_sha256"], "6" * 64
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

    def test_controller_order_and_worker_hash_guard(self) -> None:
        package = ROOT / PREFIX.replace(".", "/")
        controller = (package / "successor_runtime_controller.py").read_text()
        toolchain = controller.index("revalidate_successor_toolchain(")
        live = controller.index("revalidate_attempt_ref_protection_live(")
        indeterminate = controller.index("reservation_may_have_occurred = True")
        reserve = controller.index("acquire_global_lease(")
        self.assertLess(toolchain, live)
        self.assertLess(live, indeterminate)
        self.assertLess(indeterminate, reserve)
        self.assertIn(
            "attempt_ref_protection_receipt_sha256=live_protection_sha",
            controller,
        )
        self.assertIn("source_protection_receipt_sha256", controller)
        self.assertIn("runtime_toolchain_snapshot_sha256", controller)
        worker = (package / "native_runtime_worker.py").read_text()
        self.assertIn("validate_attempt_receipts_live", worker)
        self.assertIn(
            "live_attempt_ref_protection_readback_sha256", worker
        )
        self.assertIn("validate_runtime_toolchain_witness_paths", worker)

    def test_live_module_is_get_only_and_has_no_production_import(self) -> None:
        source = (
            ROOT / PREFIX.replace(".", "/") / "protection_live.py"
        ).read_text()
        self.assertIn('method="GET"', source)
        self.assertNotIn('method="POST"', source)
        self.assertNotIn('method="PATCH"', source)
        self.assertNotIn('method="DELETE"', source)
        self.assertNotIn("load_bridge", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
