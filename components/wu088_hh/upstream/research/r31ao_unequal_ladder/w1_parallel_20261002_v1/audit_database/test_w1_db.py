"""Synthetic storage contracts only; no HH kernels are launched."""
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w1_builder", HERE / "build_w1_db.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class DatabaseContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root, self.prior = self.base / "new", self.base / "prior"
        self.root.mkdir(); self.prior.mkdir()
        (self.root / "audit_database").mkdir()
        (self.root / "audit_database/schema.sql").write_bytes((HERE / "schema.sql").read_bytes())
        self.db = self.base / "prior.sqlite"
        self.prompt = self.base / "prompt.txt"
        self.prompt.write_text("Original synthetic fixture prompt\n")
        self.old_stage = {"stages": [{"id": f"G{i}", "current_status": f"PRIOR_{i}"} for i in range(10)]}
        self.put(self.prior / "STAGE_DELTA.json", self.old_stage)
        self.prior_receipt = self.receipt(True, "RADIUS_MET", 5)
        self.put(self.prior / "reused.json", self.prior_receipt)
        self.put(self.root / "actual.json", self.receipt(False, "RESOURCE_LIMIT", 11))
        with sqlite3.connect(self.db) as db:
            db.executescript("CREATE TABLE meta(key TEXT PRIMARY KEY,value_json TEXT); CREATE TABLE artifacts(artifact_id TEXT PRIMARY KEY,namespace TEXT,relative_path TEXT,bytes INTEGER,sha256 TEXT); CREATE TABLE stage_delta(stage_id TEXT PRIMARY KEY,current_status TEXT); CREATE TABLE historical_payload(id INTEGER PRIMARY KEY,value BLOB); CREATE INDEX payload_index ON historical_payload(value); CREATE VIEW payload_view AS SELECT id FROM historical_payload;")
            db.execute("INSERT INTO meta VALUES (?,?)", ("original_prompt_sha256", json.dumps(M.sha(self.prompt))))
            p = self.prior / "STAGE_DELTA.json"
            db.execute("INSERT INTO artifacts VALUES (?,?,?,?,?)", ("continuation:STAGE_DELTA.json", "continuation", "STAGE_DELTA.json", p.stat().st_size, M.sha(p)))
            p = self.prior / "reused.json"
            db.execute("INSERT INTO artifacts VALUES (?,?,?,?,?)", ("continuation:reused.json", "continuation", "reused.json", p.stat().st_size, M.sha(p)))
            db.executemany("INSERT INTO stage_delta VALUES (?,?)", [(s["id"], s["current_status"]) for s in self.old_stage["stages"]])
            db.execute("INSERT INTO historical_payload VALUES (?,?)", (1, b"\x00\xff preserved"))
        self.addCleanup(patch.stopall)
        patch.object(M, "PRIOR_DB_SHA", M.sha(self.db)).start()
        patch.object(M, "PROMPT_SHA", M.sha(self.prompt)).start()
        patch.object(M, "PRIOR_STAGE_SHA", M.sha(self.prior / "STAGE_DELTA.json")).start()
        self.identities = {"base_commit": M.BASE_COMMIT, "original_prompt_sha256": M.PROMPT_SHA, "prior_database_sha256": M.PRIOR_DB_SHA}
        self.put(self.root / "RECOVERY_INVENTORY.json", {"base_commit": M.BASE_COMMIT})
        self.delta = {"schema": M.STAGE_SCHEMA, **self.identities, "stages": [{"id": s["id"], "prior_status": s["current_status"], "current_status": s["current_status"], "scope": "Synthetic contract only", "remaining_gates": ["Science remains open"], "evidence": [self.ref("prior", "STAGE_DELTA.json")]} for s in self.old_stage["stages"]]}
        self.ledger = {"schema": M.LEDGER_SCHEMA, **self.identities, "records": [
            {"record_id": "reused-0", "kind": "REUSED_ACCEPTED_RECEIPT", "tile_id": "0", "primitive_index": 0, "accepted": True, "native_execution_observed": True, "receipt": self.ref("prior", "reused.json"), "status": "RADIUS_MET", "evaluations": 5},
            {"record_id": "actual-1", "kind": "ACTUAL_NATIVE_INVOCATION", "tile_id": "1", "primitive_index": 0, "accepted": False, "native_execution_observed": True, "receipt": self.ref("continuation", "actual.json"), "status": "RESOURCE_LIMIT", "evaluations": 11}], "host_events": [{"status": "SYNTHETIC_HOST_EVENT_NOT_AN_INVOCATION"}]}
        self.save()

    def put(self, path, value):
        path.write_text(json.dumps(value, sort_keys=True) + "\n")

    def ref(self, namespace, path):
        return {"namespace": namespace, "path": path, "sha256": M.sha((self.root if namespace == "continuation" else self.prior) / path)}

    def receipt(self, accepted, status, evaluations):
        return {"accepted": accepted, "status": status, "index": 0, "dispatched_evaluations": evaluations, "integration_calls": 2, "wrapper": {"native_execution_observed": True, "elapsed_wall_ns": 100}}

    def save(self):
        self.put(self.root / "STAGE_DELTA.json", self.delta)
        self.put(self.root / "EXECUTION_LEDGER.json", self.ledger)

    def build(self, name="output"):
        return M.build(self.root, self.prior, self.db, self.prompt, self.base / name)

    def test_restore_and_preservation_and_distinct_counts(self):
        before = self.db.read_bytes()
        report = self.build()
        self.assertEqual(self.db.read_bytes(), before)
        self.assertTrue(report["prior_tables_and_schema_preserved"])
        self.assertEqual(report["database_logical_sha256"], report["restored_logical_sha256"])
        self.assertEqual(report["execution_counts"], {"actual_native_invocations": 1, "accepted_current_invocations": 0, "rejected_current_invocations": 1, "reused_accepted_receipts": 1, "host_events_not_invocations": 1})
        with sqlite3.connect(self.base / "output/w1_parallel_audit.sqlite") as db:
            self.assertEqual(db.execute("SELECT value FROM historical_payload").fetchone()[0], b"\x00\xff preserved")
            self.assertEqual(db.execute("SELECT count(*) FROM w1_execution_records").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT count(*) FROM w1_stage_delta").fetchone()[0], 10)

    def test_tampered_prior_database_rejected(self):
        with self.db.open("ab") as stream: stream.write(b"tamper")
        with self.assertRaisesRegex(ValueError, "Pinned prior"): self.build()
        self.assertFalse((self.base / "output").exists())

    def test_tampered_evidence_rejected(self):
        (self.root / "actual.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "evidence SHA"): self.build()

    def test_duplicate_actual_receipt_rejected(self):
        duplicate = copy.deepcopy(self.ledger["records"][1]); duplicate["record_id"] = "duplicate"
        self.ledger["records"].append(duplicate); self.save()
        with self.assertRaisesRegex(ValueError, "Duplicate receipt"): self.build()

    def test_reused_receipt_cannot_count_as_current(self):
        self.ledger["records"][0]["kind"] = "ACTUAL_NATIVE_INVOCATION"; self.save()
        with self.assertRaisesRegex(ValueError, "namespace"): self.build()

    def test_receipt_claims_cross_checked(self):
        self.ledger["records"][1]["accepted"] = True; self.save()
        with self.assertRaisesRegex(ValueError, "accepted.*receipt"): self.build()

    def test_prior_status_cannot_drift(self):
        self.delta["stages"][0]["prior_status"] = "MADE_UP"; self.save()
        with self.assertRaisesRegex(ValueError, "prior status"): self.build()

    def test_create_only(self):
        self.build()
        with self.assertRaises(FileExistsError): self.build()

    def test_late_source_added_invalidates_snapshot(self):
        self.build()
        source_map = M.load(self.base / "output/W1_SOURCE_MAP.json")
        (self.root / "late.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "file set changed"):
            M.verify_snapshot(self.root, self.prior, self.prompt, self.db, source_map)

    def test_changed_source_invalidates_snapshot(self):
        self.build()
        source_map = M.load(self.base / "output/W1_SOURCE_MAP.json")
        (self.root / "actual.json").write_text("{}");
        with self.assertRaisesRegex(ValueError, "Source bytes changed"):
            M.verify_snapshot(self.root, self.prior, self.prompt, self.db, source_map)

    def test_symlink_rejected(self):
        (self.root / "linked").symlink_to(self.prompt)
        with self.assertRaisesRegex(ValueError, "symlink"): self.build()

    def test_rejected_native_stdout_fields_are_preserved(self):
        native = self.receipt(False, "RESOURCE_LIMIT", 11)
        wrapper = {"accepted": False, "index": 0, "reason": "NONZERO_NATIVE_EXIT", "native_stdout": json.dumps(native), "wrapper": native["wrapper"]}
        self.put(self.root / "actual.json", wrapper)
        self.ledger["records"][1]["receipt"] = self.ref("continuation", "actual.json"); self.save()
        self.assertEqual(self.build()["execution_counts"]["rejected_current_invocations"], 1)

    def test_no_science_executions_is_valid(self):
        self.ledger["records"] = []; self.save()
        self.assertEqual(self.build()["execution_counts"]["actual_native_invocations"], 0)

    def test_output_inside_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            M.build(self.root, self.prior, self.db, self.prompt, self.root / "output")

    def test_delivery_limit_failure_retains_inspectable_output(self):
        with patch.object(M, "MAX_DATABASE_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "delivery limit"): self.build()
        self.assertTrue((self.base / "output/w1_parallel_audit.sqlite").is_file())
        self.assertFalse((self.base / "output/W1_DB_VERIFICATION.json").exists())

    def test_historical_receipt_copy_is_not_new_execution(self):
        (self.root / "copied_old.json").write_bytes((self.prior / "reused.json").read_bytes())
        record = copy.deepcopy(self.ledger["records"][0])
        record.update(record_id="misattributed", kind="ACTUAL_NATIVE_INVOCATION", receipt=self.ref("continuation", "copied_old.json"))
        self.ledger["records"] = [record]; self.save()
        with self.assertRaisesRegex(ValueError, "historical receipt"): self.build()

    def test_reused_receipt_must_be_in_prior_snapshot(self):
        self.put(self.prior / "reused.json", self.receipt(True, "RADIUS_MET", 99))
        self.ledger["records"][0].update(receipt=self.ref("prior", "reused.json"), evaluations=99)
        self.save()
        with self.assertRaisesRegex(ValueError, "prior database"): self.build()


if __name__ == "__main__":
    unittest.main()
