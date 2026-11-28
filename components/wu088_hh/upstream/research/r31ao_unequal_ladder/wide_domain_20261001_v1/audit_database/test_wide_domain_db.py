"""Real SQLite/SQL/filesystem contracts; no scientific computation."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wide_audit", HERE / "build_wide_domain_db.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)
RESEARCH = HERE.parents[1]
PRIOR = RESEARCH / "native_execution_20261001_v1"
PROMPT = RESEARCH / "production_solver_20261001_v1/audit/ORIGINAL_USER_RESEARCH_PROMPT.txt"
PRIOR_DB = Path(os.environ.get("WU088_PRIOR_CONTINUATION_DB", "/workspace/scratch/6cf5f59cd2d1/native_execution_intake/continuation_db_final/continuation_audit.sqlite"))


class DatabaseContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="wu088_wide_audit_contract_")
        self.work = Path(self.temp.name)
        self.root = self.work / "source"
        (self.root / "audit_database").mkdir(parents=True)
        shutil.copyfile(HERE / "schema.sql", self.root / "audit_database/schema.sql")
        AUDIT.write_json(self.root / "RECOVERY_INVENTORY.json", {"base_commit": AUDIT.BASE_COMMIT})
        self.evidence = self.root / "runtime/receipt.json"
        self.evidence.parent.mkdir()
        AUDIT.write_json(self.evidence, {"status": "REJECTED", "returncode": 2, "nested": {"STATUS": "NOT_RUN", "exit_code": None}})
        prior_stages = AUDIT.load(PRIOR / AUDIT.STAGE_RELATIVE)["stages"]
        self.delta = {
            "schema": "WU088_WIDE_DOMAIN_STAGE_DELTA_V1", "base_commit": AUDIT.BASE_COMMIT,
            "original_prompt_sha256": AUDIT.PROMPT_SHA,
            "stages": [{"id": s["id"], "prior_status": s["current_status"], "current_status": s["current_status"],
                        "scope": "Contract fixture preserves prior stage; no new scientific conclusion",
                        "remaining_gates": ["Final root reconciliation and actual results remain separate"],
                        "evidence": [{"namespace": "prior", "path": AUDIT.STAGE_RELATIVE, "sha256": AUDIT.PRIOR_STAGE_SHA}]}
                       for s in prior_stages],
        }
        AUDIT.write_json(self.root / "STAGE_DELTA.json", self.delta)
        self.before = AUDIT.sha(PRIOR_DB)

    def tearDown(self):
        self.assertEqual(AUDIT.sha(PRIOR_DB), self.before)
        self.temp.cleanup()

    def rewrite_delta(self):
        (self.root / "STAGE_DELTA.json").write_text(json.dumps(self.delta), encoding="utf-8")

    def build(self, name="result"):
        return AUDIT.build(self.root, PRIOR, PRIOR_DB, PROMPT, self.work / name)

    def test_real_sqlite_integrity_fk_sql_restore_and_literal_statuses(self):
        AUDIT.write_json(self.root / "runtime/SUCCESS.json", {"status": "FAIL", "exit_code": 7})
        AUDIT.write_json(self.root / "runtime/PASS_PLAN.json", {"tasks": [{"ordinal": 0}]})
        report = self.build()
        self.assertEqual(report["integrity_check"], "ok")
        self.assertEqual(report["foreign_key_violations"], 0)
        self.assertEqual(report["logical_sha256"], report["restored_logical_sha256"])
        self.assertFalse(report["science_executed_by_builder"])
        with sqlite3.connect(self.work / "result/wide_domain_audit.sqlite") as db:
            rows = list(db.execute("SELECT source_artifact,json_pointer,status_fields_json,exit_fields_json FROM run_records ORDER BY source_artifact,json_pointer"))
            self.assertEqual(len(rows), 3)
            self.assertIn(("continuation:runtime/SUCCESS.json", "", '{"status":"FAIL"}', '{"exit_code":7}'), rows)
            self.assertIn(("continuation:runtime/receipt.json", "/nested", '{"STATUS":"NOT_RUN"}', '{"exit_code":null}'), rows)
            self.assertEqual(db.execute("SELECT count(*) FROM stage_delta").fetchone()[0], 10)
            self.assertEqual(db.execute("SELECT count(*) FROM stage_delta WHERE current_status!=prior_status").fetchone()[0], 0)
            db.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("DELETE FROM artifacts WHERE artifact_id='checkpoint:continuation_audit.sqlite'")

    def test_same_source_has_same_logical_identity(self):
        first = self.build("one")
        second = self.build("two")
        self.assertEqual(first["logical_sha256"], second["logical_sha256"])
        self.assertEqual(first["row_counts"], second["row_counts"])

    def test_create_only_does_not_modify_prior_output(self):
        self.build()
        before = {p.name: AUDIT.sha(p) for p in (self.work / "result").iterdir()}
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(before, {p.name: AUDIT.sha(p) for p in (self.work / "result").iterdir()})

    def test_late_evidence_detected_then_included_by_fresh_build(self):
        first = self.build("one")
        source_map = AUDIT.load(self.work / "one/WIDE_DOMAIN_SOURCE_MAP.json")
        AUDIT.write_json(self.root / "runtime/LATE.json", {"status": "NO_CONVERGENCE", "returncode": 2})
        with self.assertRaisesRegex(ValueError, "file set changed"):
            AUDIT.verify_snapshot(self.root, PRIOR, PROMPT, PRIOR_DB, source_map)
        second = self.build("two")
        self.assertEqual(second["row_counts"]["artifacts"], first["row_counts"]["artifacts"] + 1)
        self.assertEqual(second["row_counts"]["run_records"], first["row_counts"]["run_records"] + 1)
        self.assertNotEqual(first["logical_sha256"], second["logical_sha256"])

    def test_changed_source_bytes_detected(self):
        self.build()
        source_map = AUDIT.load(self.work / "result/WIDE_DOMAIN_SOURCE_MAP.json")
        self.evidence.write_text('{"status":"PASS"}\n')
        with self.assertRaisesRegex(ValueError, "Source bytes changed"):
            AUDIT.verify_snapshot(self.root, PRIOR, PROMPT, PRIOR_DB, source_map)

    def test_wrong_prior_db_hash_refused_before_output(self):
        changed = self.work / "changed.sqlite"
        changed.write_bytes(PRIOR_DB.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "Pinned prior source hash mismatch"):
            AUDIT.build(self.root, PRIOR, changed, PROMPT, self.work / "result")
        self.assertFalse((self.work / "result").exists())

    def test_stage_evidence_hash_mismatch_refused_before_output(self):
        self.delta["stages"][0]["evidence"][0]["sha256"] = "0" * 64
        self.rewrite_delta()
        with self.assertRaisesRegex(ValueError, "Stage evidence SHA mismatch"):
            self.build()
        self.assertFalse((self.work / "result").exists())

    def test_prior_stage_mismatch_refused_before_output(self):
        self.delta["stages"][0]["prior_status"] = "ALL_COMPLETE"
        self.rewrite_delta()
        with self.assertRaisesRegex(ValueError, "Incorrect prior status"):
            self.build()
        self.assertFalse((self.work / "result").exists())

    def test_output_inside_current_tree_refused(self):
        with self.assertRaisesRegex(ValueError, "outside current and prior"):
            AUDIT.build(self.root, PRIOR, PRIOR_DB, PROMPT, self.root / "output")
        self.assertFalse((self.root / "output").exists())

    def test_symlink_source_refused(self):
        (self.root / "linked").symlink_to(self.evidence)
        with self.assertRaisesRegex(ValueError, "Source symlink"):
            self.build()
        self.assertFalse((self.work / "result").exists())

    def test_missing_original_stage_refused(self):
        self.delta["stages"].pop()
        self.rewrite_delta()
        with self.assertRaisesRegex(ValueError, "G0 through G9 exactly once"):
            self.build()
        self.assertFalse((self.work / "result").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
