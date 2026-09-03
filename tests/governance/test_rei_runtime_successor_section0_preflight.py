#!/usr/bin/env python3
"""TDD contract for successor-host Section-0 re-attestation preflight."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
import urllib.error


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "handoff" / "rei_runtime_successor_section0_preflight_20260903"
SUBJECT_PATH = PACKAGE / "successor_section0_preflight.py"
CONTRACT_PATH = PACKAGE / "CONTRACT.json"
EXPECTED_HEAD = "eb1c05f3ea2bda910ddf85ef7f3bab08c73eca13"
EXPECTED_TREE = "0aa13dd9cb8630f208307342a933a8c68abf62c8"
EXPECTED_LOCK = "a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa"
EXPECTED_REF = (
    "refs/heads/attempt-ledger/"
    "rei-runtime-bridge-ntpath-rebind-20260903-attempt-3"
)


def load_subject():
    if not SUBJECT_PATH.is_file():
        raise AssertionError("EXPECTED_RED_SUCCESSOR_PREFLIGHT_IMPLEMENTATION_ABSENT")
    spec = importlib.util.spec_from_file_location(
        "rei_runtime_successor_section0_preflight", SUBJECT_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("SUCCESSOR_PREFLIGHT_IMPORT_SPEC_MISSING")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status: int, payload: dict[str, object]):
        self.status = status
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return self._payload


class SuccessorSection0PreflightTests(unittest.TestCase):
    def test_contract_binds_exact_pr42_release_and_one_attempt(self):
        load_subject()
        self.assertTrue(CONTRACT_PATH.is_file(), "PREFLIGHT_CONTRACT_MISSING")
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["executable_release"]["commit"], EXPECTED_HEAD)
        self.assertEqual(contract["executable_release"]["tree"], EXPECTED_TREE)
        self.assertEqual(contract["successor_section0"]["semantic_toolchain_lock_sha256"], EXPECTED_LOCK)
        self.assertEqual(contract["attempt_state"]["global_ref"], EXPECTED_REF)
        self.assertEqual(contract["attempt_state"]["remaining_before_reservation"], 1)

    def test_404_observation_is_informational_not_authorization(self):
        subject = load_subject()

        def opener(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", None, None)

        result = subject.observe_global_ref_read_only(
            ref=EXPECTED_REF,
            expected_target=EXPECTED_HEAD,
            opener=opener,
        )
        self.assertEqual(result["status"], "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED")
        self.assertEqual(result["authorization_effect"], "NONE")
        self.assertFalse(result["global_lease_acquired"])

    def test_existing_global_ref_stops_preflight(self):
        subject = load_subject()

        def opener(request, timeout):
            return FakeResponse(
                200,
                {
                    "ref": EXPECTED_REF,
                    "object": {"sha": EXPECTED_HEAD, "type": "commit"},
                },
            )

        with self.assertRaisesRegex(subject.PreflightError, "STOP_ATTEMPT_ALREADY_RESERVED"):
            subject.observe_global_ref_read_only(
                ref=EXPECTED_REF,
                expected_target=EXPECTED_HEAD,
                opener=opener,
            )

    def test_unexpected_ref_target_stops_preflight(self):
        subject = load_subject()

        def opener(request, timeout):
            return FakeResponse(
                200,
                {
                    "ref": EXPECTED_REF,
                    "object": {"sha": "0" * 40, "type": "commit"},
                },
            )

        with self.assertRaisesRegex(subject.PreflightError, "STOP_ATTEMPT_ALREADY_RESERVED"):
            subject.observe_global_ref_read_only(
                ref=EXPECTED_REF,
                expected_target=EXPECTED_HEAD,
                opener=opener,
            )

    def test_transport_failure_is_fail_closed(self):
        subject = load_subject()

        def opener(request, timeout):
            raise urllib.error.URLError("offline")

        with self.assertRaisesRegex(subject.PreflightError, "GLOBAL_REF_READ_ONLY_OBSERVATION_FAILED"):
            subject.observe_global_ref_read_only(
                ref=EXPECTED_REF,
                expected_target=EXPECTED_HEAD,
                opener=opener,
            )

    def test_attempt_state_root_under_tmp_is_rejected(self):
        subject = load_subject()
        with self.assertRaisesRegex(subject.PreflightError, "ATTEMPT_STATE_ROOT_FORBIDDEN"):
            subject.validate_attempt_state_root(
                Path("/tmp/rei-attempt-state"), repo=ROOT
            )

    def test_attempt_state_root_inside_repository_is_rejected(self):
        subject = load_subject()
        with self.assertRaisesRegex(subject.PreflightError, "ATTEMPT_STATE_ROOT_FORBIDDEN"):
            subject.validate_attempt_state_root(
                ROOT / ".attempt-state", repo=ROOT
            )

    def test_empty_persistent_attempt_state_is_accepted(self):
        subject = load_subject()
        base = Path("/var/tmp") if Path("/var/tmp").is_dir() else Path(tempfile.gettempdir())
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            root = Path(temporary)
            accepted = subject.validate_attempt_state_root(root, repo=ROOT)
            self.assertEqual(accepted, root.resolve(strict=True))
            self.assertEqual(subject.inspect_attempt_state(accepted), [])

    def test_existing_attempt_state_is_rejected(self):
        subject = load_subject()
        base = Path("/var/tmp") if Path("/var/tmp").is_dir() else Path(tempfile.gettempdir())
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            root = Path(temporary)
            (root / "attempt-3.global-lease.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(subject.PreflightError, "ATTEMPT_STATE_ALREADY_PRESENT"):
                subject.validate_attempt_state_root(root, repo=ROOT)

    def test_successor_receipt_requires_exact_status_schema_and_lock(self):
        subject = load_subject()
        contract = {
            "required_status": "PASS_EQUIVALENT_SECTION_0_SUCCESSOR",
            "required_schema": "rei-successor-section0-receipt/v1",
            "semantic_toolchain_lock_sha256": EXPECTED_LOCK,
            "semantic_toolchain_lock": {"target": "x86_64-unknown-linux-gnu"},
        }
        receipt = {
            "status": contract["required_status"],
            "schema": contract["required_schema"],
            "semantic_toolchain_lock_sha256": EXPECTED_LOCK,
            "observed_toolchain": contract["semantic_toolchain_lock"],
        }
        self.assertEqual(
            subject.validate_successor_receipt_mapping(receipt, contract)["status"],
            contract["required_status"],
        )
        hostile = dict(receipt, status="PASS_IMMUTABLE_SECTION_0")
        with self.assertRaisesRegex(subject.PreflightError, "SUCCESSOR_SECTION0_STATUS_MISMATCH"):
            subject.validate_successor_receipt_mapping(hostile, contract)

    def test_preflight_receipt_preserves_attempt_and_science_ceiling(self):
        subject = load_subject()
        receipt = subject.build_preflight_receipt(
            release_head=EXPECTED_HEAD,
            release_tree=EXPECTED_TREE,
            successor_receipt_sha256="1" * 64,
            first_ref_observation={"status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED"},
            second_ref_observation={"status": "GLOBAL_ATTEMPT_REF_ABSENT_OBSERVED"},
        )
        self.assertEqual(receipt["status"], "PASS_READ_ONLY_SUCCESSOR_SECTION0_PREFLIGHT")
        self.assertEqual(receipt["attempt_state"]["remaining_attempts"], 1)
        self.assertFalse(receipt["attempt_state"]["global_lease_acquired"])
        self.assertFalse(receipt["attempt_state"]["local_lease_created"])
        self.assertEqual(receipt["native_runtime"], "NOT_RUN")
        self.assertEqual(receipt["claim_ceiling"]["first_interval"], "NO_PASS_FIRST_CANONICAL_INTERVAL")
        self.assertEqual(receipt["claim_ceiling"]["provider_export"], "NOT_AUTHORIZED")

    def test_source_boundary_contains_no_mutating_execution_calls(self):
        load_subject()
        source = SUBJECT_PATH.read_text(encoding="utf-8")
        forbidden = (
            "acquire_global_lease(",
            "create_persistent_local_lease(",
            "reserve_then_dispatch(",
            "run_native_once(",
            'method="POST"',
            "git/refs",
        )
        for token in forbidden:
            self.assertNotIn(token, source)
        self.assertIn('method="GET"', source)
        self.assertIn("READ_ONLY_PREFLIGHT", source)


if __name__ == "__main__":
    unittest.main()
