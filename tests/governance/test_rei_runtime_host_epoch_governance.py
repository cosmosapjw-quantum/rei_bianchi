from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / "docs" / "runtime_bridge_host_epoch_governance_20260903"

REQUIRED = {
    "README.md",
    "HOST_EPOCH_REATTESTATION_POLICY.json",
    "ATTEMPT_LINEAGE_LEDGER.json",
    "GLOBAL_ATTEMPT_LEASE_PROTOCOL.json",
    "RUNTIME_RECOVERY_INPUTS.json",
    "emit_successor_section0_receipt.py",
    "reserve_remote_attempt_lease.py",
    "verify_governance_patch.py",
    "WOLFRAM_DAG_ORACLE.wl",
    "WOLFRAM_DAG_RECEIPT.json",
    "SCISPACE_LITERATURE_LOCK.md",
    "PHYS_MATH_AUDIT.md",
    "PHYS_MATH_CODE_AUDIT.md",
    "GOVERNANCE_STATE.csv",
    "GOVERNANCE_STATE.svg",
    "render_governance_state.py",
    "RUST_1_94_1_ENV.sh",
    "TDD_RED_RECEIPT.json",
    "HASH_METHOD_CORRECTION_RECEIPT.json",
}

SEMANTIC_LOCK_ID = "a3da50241ed6423212ab40c79f7810b5eaad042acdff29eb40f330aa39d2d4fa"
OLD_SECTION0_SHA = "470fec225675a62a3c0121abcc4c568d345b088dd541a49fb18d91d6eacf104b"
SOURCE_HEAD = "3169d1b0554193ababfb568406764d53df29649d"
SOURCE_TREE = "1fa2da1a818bb311bf6cec42f76ff05693ed0903"
BACKUP_HEAD = "74f511f3bcd1cd5ee6b76fff892d796d5ce819a8"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


class HostEpochGovernanceContractTests(unittest.TestCase):
    def test_required_governance_files_exist(self) -> None:
        missing = sorted(name for name in REQUIRED if not (GOV / name).is_file())
        self.assertEqual(missing, [])

    def test_historical_receipt_is_preserved_but_not_reconstructed(self) -> None:
        policy = load("HOST_EPOCH_REATTESTATION_POLICY.json")
        historical = policy["historical_environment_epoch"]
        self.assertEqual(historical["section0_receipt_sha256"], OLD_SECTION0_SHA)
        self.assertEqual(historical["availability"], "UNAVAILABLE_EXACT_BYTES")
        self.assertFalse(historical["may_be_reconstructed"])
        self.assertFalse(historical["required_on_successor_host"])

    def test_successor_epoch_uses_semantic_equivalence_not_raw_identity(self) -> None:
        policy = load("HOST_EPOCH_REATTESTATION_POLICY.json")
        successor = policy["successor_environment_epoch"]
        self.assertEqual(successor["required_status"], "PASS_EQUIVALENT_SECTION_0_SUCCESSOR")
        self.assertEqual(successor["semantic_toolchain_lock_sha256"], SEMANTIC_LOCK_ID)
        self.assertEqual(successor["semantic_toolchain_lock_hash_method"], "SHA256_CANONICAL_UTF8_JSON_BYTES")
        self.assertEqual(successor["raw_receipt_relation"], "NEW_IDENTITY_REQUIRED")
        self.assertEqual(successor["host_identity_relation"], "DISTINCT_HOST_EPOCH_ALLOWED")
        self.assertGreaterEqual(len(successor["load_bearing_fields"]), 10)

    def test_prior_attempts_are_durable_evidence_not_ephemeral_mutexes(self) -> None:
        ledger = load("ATTEMPT_LINEAGE_LEDGER.json")
        attempts = ledger["historical_attempts"]
        self.assertEqual([row["ordinal"] for row in attempts], [1, 2])
        self.assertEqual([row["pull_request"] for row in attempts], [30, 32])
        self.assertTrue(all(row["status"] == "CONSUMED_HISTORICAL" for row in attempts))
        self.assertEqual(ledger["old_tmp_claim_policy"], "HISTORICAL_PATH_NOT_LOAD_BEARING_ON_SUCCESSOR_HOST")
        self.assertEqual(ledger["next_attempt"]["remaining_attempts"], 1)
        self.assertEqual(ledger["next_attempt"]["retries_after_outcome"], 0)

    def test_global_lease_is_atomic_create_only_and_precedes_native_dispatch(self) -> None:
        protocol = load("GLOBAL_ATTEMPT_LEASE_PROTOCOL.json")
        self.assertEqual(protocol["acquisition"]["operation"], "GITHUB_CREATE_REF")
        self.assertEqual(protocol["acquisition"]["required_http_status"], 201)
        self.assertEqual(protocol["acquisition"]["on_existing_ref"], "STOP_ATTEMPT_ALREADY_RESERVED")
        self.assertFalse(protocol["mutation_policy"]["update_allowed"])
        self.assertFalse(protocol["mutation_policy"]["delete_allowed"])
        order = protocol["ordering"]
        self.assertLess(order.index("PASS_SUCCESSOR_SECTION0"), order.index("ACQUIRE_GLOBAL_LEASE"))
        self.assertLess(order.index("ACQUIRE_GLOBAL_LEASE"), order.index("CREATE_LOCAL_O_EXCL_LEASE"))
        self.assertLess(order.index("CREATE_LOCAL_O_EXCL_LEASE"), order.index("NATIVE_DISPATCH_ONCE"))

    def test_recovery_manifest_pins_source_toolchain_and_compact_packet(self) -> None:
        recovery = load("RUNTIME_RECOVERY_INPUTS.json")
        self.assertEqual(recovery["source_handoff"]["commit"], SOURCE_HEAD)
        self.assertEqual(recovery["source_handoff"]["tree"], SOURCE_TREE)
        self.assertEqual(recovery["backup_source_packet_branch"]["commit"], BACKUP_HEAD)
        self.assertEqual(recovery["compact_packet"]["artifact_id"], 9877870910)
        self.assertEqual(recovery["compact_packet"]["zip_sha256"], "8dbb0898997b1122fdd0da8b575580b0ad8439d748bd2971a74d66ba0bb4c657")
        self.assertEqual(recovery["rust_archive"]["sha256"], "294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40")
        self.assertEqual(recovery["rust_signature_file"]["sha256"], "942bc6926af6a2130d70e77933e3df09d39beeedafad77710259e6df7eadee08")

    def test_governance_dag_has_no_bypass(self) -> None:
        policy = load("HOST_EPOCH_REATTESTATION_POLICY.json")
        edges = {tuple(edge) for edge in policy["dag"]["edges"]}
        required = {
            ("HISTORICAL_ATTEMPT_LEDGER", "PASS_SUCCESSOR_SECTION0"),
            ("SOURCE_PACKET_BACKUP", "PASS_SUCCESSOR_SECTION0"),
            ("PASS_SUCCESSOR_SECTION0", "ACQUIRE_GLOBAL_LEASE"),
            ("ACQUIRE_GLOBAL_LEASE", "CREATE_LOCAL_O_EXCL_LEASE"),
            ("CREATE_LOCAL_O_EXCL_LEASE", "NATIVE_DISPATCH_ONCE"),
            ("NATIVE_DISPATCH_ONCE", "RUNTIME_RESULT_AUDIT"),
            ("RUNTIME_RESULT_AUDIT", "FIRST_INTERVAL_ELIGIBILITY"),
            ("FIRST_INTERVAL_ELIGIBILITY", "PROVIDER_REVIEW"),
        }
        forbidden = {
            ("SOURCE_PACKET_BACKUP", "NATIVE_DISPATCH_ONCE"),
            ("PASS_SUCCESSOR_SECTION0", "NATIVE_DISPATCH_ONCE"),
            ("NATIVE_DISPATCH_ONCE", "FIRST_INTERVAL_ELIGIBILITY"),
            ("NATIVE_DISPATCH_ONCE", "PROVIDER_REVIEW"),
        }
        self.assertTrue(required.issubset(edges))
        self.assertTrue(edges.isdisjoint(forbidden))

    def test_scripts_are_stdlib_only_and_do_not_run_native_bridge(self) -> None:
        emit = (GOV / "emit_successor_section0_receipt.py").read_text(encoding="utf-8")
        reserve = (GOV / "reserve_remote_attempt_lease.py").read_text(encoding="utf-8")
        forbidden_tokens = ("import numpy", "import scipy", "import jax", "interval_divide(", "build_authenticated_backend(")
        for token in forbidden_tokens:
            self.assertNotIn(token, emit)
            self.assertNotIn(token, reserve)
        self.assertIn("os.O_EXCL", emit)
        self.assertIn("POST", reserve)
        self.assertIn("refs/heads/attempt-ledger/", reserve)

    def test_claim_ceiling_remains_fail_closed(self) -> None:
        policy = load("HOST_EPOCH_REATTESTATION_POLICY.json")
        ceiling = policy["claim_ceiling"]
        self.assertEqual(ceiling["native_runtime"], "NOT_RUN")
        self.assertEqual(ceiling["first_interval"], "NO_PASS_FIRST_CANONICAL_INTERVAL")
        self.assertEqual(ceiling["provider_export"], "NOT_AUTHORIZED")
        self.assertEqual(ceiling["scientific_pass"], "NOT_CLAIMED")

    def test_wolfram_receipt_is_non_authoritative_and_green(self) -> None:
        receipt = load("WOLFRAM_DAG_RECEIPT.json")
        self.assertEqual(receipt["status"], "PASS")
        self.assertTrue(receipt["acyclic"])
        self.assertEqual(receipt["path_count"], 1)
        self.assertTrue(receipt["forbidden_bypass_edges_absent"])
        self.assertEqual(receipt["semantic_toolchain_lock_sha256"], SEMANTIC_LOCK_ID)
        self.assertEqual(receipt["authority_effect"], "NONE")

    def test_hash_method_correction_is_explicit(self) -> None:
        receipt = load("HASH_METHOD_CORRECTION_RECEIPT.json")
        self.assertEqual(receipt["status"], "CORRECTED_TO_RAW_CANONICAL_BYTES")
        self.assertEqual(receipt["correct_raw_utf8_sha256"], SEMANTIC_LOCK_ID)
        self.assertNotEqual(receipt["incorrect_wolfram_expression_hash"], SEMANTIC_LOCK_ID)
        self.assertEqual(receipt["scientific_effect"], "NONE")

    def test_rust_environment_helper_is_locator_only(self) -> None:
        helper = (GOV / "RUST_1_94_1_ENV.sh").read_text(encoding="utf-8")
        self.assertIn("RUST_1_94_1_PREFIX=/mnt/data/rust-1.94.1-prefix", helper)
        self.assertIn("LD_LIBRARY_PATH", helper)
        self.assertNotIn("PASS_IMMUTABLE_SECTION_0", helper)

    def test_no_manifest_self_hash_cycle(self) -> None:
        manifest = GOV / "MANIFEST.sha256"
        self.assertTrue(manifest.is_file())
        rows = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line]
        names = [row.split("  ", 1)[1] for row in rows]
        self.assertNotIn("MANIFEST.sha256", names)
        self.assertEqual(len(names), len(set(names)))
        for row in rows:
            digest, name = row.split("  ", 1)
            self.assertEqual(hashlib.sha256((GOV / name).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
