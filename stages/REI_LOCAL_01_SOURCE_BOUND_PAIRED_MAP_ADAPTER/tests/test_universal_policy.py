from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / "stages" / "REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER"
BASE_COMMIT = "1893f12d14b212eb4b6bd637332824f692e6f4b3"
BASE_TREE = "773fcdc4d1ab115fa0542d26ba67af5c086f450b"
RESEARCH_SHA = "9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934"
CODING_SHA = "6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4"
PASTED_MATH_SHA = "09e8a25a7aeeadc36fdf95fa974a9006ae16b6058f481694227b17be5d7ad8c0"
NONCODE_ZIP_SHA = "8546961bf9fa132fa00d7399d19da5bdc52f5932f97d5712e86403c512f709d8"
RECOVERY_CLASS = "RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL"


class UniversalPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lock = json.loads((STAGE / "INPUT_LOCK.json").read_text(encoding="utf-8"))
        cls.work = json.loads(
            (STAGE / "AUDIT_COMPILED_WORK_UNIT.json").read_text(encoding="utf-8")
        )
        cls.amendment = json.loads(
            (STAGE / "RUST_IMPLEMENTATION_AMENDMENT.json").read_text(encoding="utf-8")
        )
        cls.policy = (ROOT / "docs/harness/UNIVERSAL_EXECUTION_POLICY.md").read_text(
            encoding="utf-8"
        )
        cls.agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        cls.progress = (
            ROOT
            / ".superpowers/sdd/2026-08-30-rei-rust-rebuild-followthrough/progress.md"
        ).read_text(encoding="utf-8")

    def test_01_recovery_and_exact_base_are_explicit(self) -> None:
        self.assertEqual(self.lock["recovery_classification"], RECOVERY_CLASS)
        self.assertEqual(self.lock["authority"]["base_commit"], BASE_COMMIT)
        self.assertEqual(self.lock["authority"]["base_tree"], BASE_TREE)
        self.assertEqual(self.work["base"], {"commit": BASE_COMMIT, "tree": BASE_TREE})
        for text in (self.policy, self.agents, self.progress):
            self.assertIn(RECOVERY_CLASS, text)

    def test_02_harness_byte_identities_are_exact(self) -> None:
        harnesses = {item["sha256"]: item for item in self.lock["harnesses"]}
        self.assertEqual(set(harnesses), {RESEARCH_SHA, CODING_SHA})
        self.assertTrue(all(item["identity_class"] == "BYTE_IDENTITY" for item in harnesses.values()))
        external = {item["sha256"]: item for item in self.lock["external_inputs"]}
        self.assertEqual(set(external), {PASTED_MATH_SHA, NONCODE_ZIP_SHA})
        self.assertTrue(all(item["identity_class"] == "BYTE_IDENTITY" for item in external.values()))
        records = self.lock["runtime_closure"]["declared_paths"]
        keys = [(record["role"], record["path"]) for record in records]
        self.assertEqual(keys, sorted(keys))
        for record in records:
            path = ROOT / record["path"]
            self.assertTrue(path.is_file(), record["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])
        validation = self.lock["validation_sources"]
        validation_keys = [(record["role"], record["path"]) for record in validation]
        self.assertEqual(validation_keys, sorted(validation_keys))
        for record in validation:
            path = ROOT / record["path"]
            self.assertTrue(path.is_file(), record["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])

    def test_03_anti_meta_loop_budget_is_closed(self) -> None:
        budget = self.work["policy"]["attempt_budget_per_blocker"]
        self.assertEqual(budget["initial"], 1)
        self.assertEqual(budget["diagnostic_retry"], 1)
        self.assertEqual(budget["two_no_material_delta"], "STOP_META_LOOP")
        self.assertRegex(self.policy, r"two attempts without material delta")
        self.assertRegex(self.policy, r"does not reset the budget")

    def test_04_progress_checkpoint_is_durable_and_typed(self) -> None:
        for marker in ("OBSERVED", "IMPLEMENTED", "IN_PROGRESS", "BLOCKED"):
            self.assertIn(marker, self.progress)
        self.assertIn("Next executable action", self.progress)
        self.assertIn("PARTIAL_RUST_IMPLEMENTATION_STOP_INVALID", self.progress)

    def test_05_byte_and_semantic_identity_are_not_conflated(self) -> None:
        for marker in ("BYTE_IDENTITY", "SEMANTIC_IDENTITY", "does not claim byte identity"):
            self.assertIn(marker, self.policy)
        self.assertIn("byte_identity_not_semantic_identity", self.work["policy"])
        self.assertTrue(self.work["policy"]["byte_identity_not_semantic_identity"])

    def test_06_every_p0_p1_claim_is_compiled_to_a_gate(self) -> None:
        claims = self.work["claims"]
        self.assertGreaterEqual(len(claims), 8)
        ids = [claim["id"] for claim in claims]
        self.assertEqual(len(ids), len(set(ids)))
        for claim in claims:
            self.assertIn(claim["severity"], {"P0", "P1", "P2"})
            if claim["severity"] in {"P0", "P1"}:
                for key in ("invariant", "gate", "expected", "evidence", "status"):
                    self.assertIsInstance(claim[key], str)
                    self.assertTrue(claim[key].strip(), (claim["id"], key))

    def test_07_rust_first_boundary_and_authority_are_locked(self) -> None:
        authority = self.lock["rust_authority"]
        self.assertEqual(authority["version"], "1.94.1")
        self.assertEqual(authority["mpfr"]["precision_bits"], 256)
        self.assertEqual(authority["mpfr"]["rounding"], "DIRECTED")
        self.assertEqual(len(authority["environment_script"]["sha256"]), 64)
        self.assertEqual(self.amendment["schema"], "rei-rust-implementation-amendment/v2")
        self.assertEqual(
            set(self.amendment),
            {
                "schema",
                "backend_source",
                "backend_source_sha256",
                "abi_version",
                "precision_bits",
                "rounding_policy",
                "load_bearing_boundary",
                "claim_ceiling",
                "expected_artifact_sha256",
                "deterministic_build_contract_sha256",
                "rustc",
                "linker",
                "mpfr",
                "gmp",
                "native_layout",
            },
        )
        self.assertEqual(self.amendment["abi_version"], 4)
        self.assertEqual(self.amendment["rounding_policy"], "MPFR_RNDD_RNDU")
        self.assertFalse(self.lock["execution_scope"]["jax_load_bearing"])
        self.assertEqual(
            self.lock["seal_status"], "SEALED_RECONSTRUCTED_INPUT_SET_STOP_INVALID"
        )

    def test_08_claim_ceiling_excludes_canonical_pilot(self) -> None:
        checkpoint = self.work["checkpoint"]
        self.assertEqual(checkpoint["canonical_pilot"], "NOT_RUN")
        self.assertEqual(checkpoint["first_interval"], "NO_PASS_FIRST_CANONICAL_INTERVAL")
        self.assertEqual(checkpoint["scientific_pass"], "NOT_CLAIMED")
        self.assertEqual(
            self.lock["execution_scope"]["canonical_46080_by_3_pilot"], "NOT_RUN"
        )
        noncode = self.lock["noncode_math_authority"]
        self.assertEqual(noncode["status"], "FORMULA_CONTRACT_CLOSED")
        self.assertEqual(set(noncode["evidence_gates"].values()), {"NOT_RUN"})
        self.assertNotRegex(self.policy, re.compile(r"canonical[^\n]{0,40}\bPASS\b", re.I))


if __name__ == "__main__":
    unittest.main()
