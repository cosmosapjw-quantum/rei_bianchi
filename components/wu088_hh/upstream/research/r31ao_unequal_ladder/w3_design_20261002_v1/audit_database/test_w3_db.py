"""Synthetic authority/storage tests only; no HH or endpoint science runs."""
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w3_builder", HERE / "build_w3_db.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class EndpointDatabaseContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root, self.prior = self.base / "new", self.base / "prior"
        self.root.mkdir(); self.prior.mkdir()
        (self.root / "audit_database").mkdir()
        (self.root / "audit_database/schema.sql").write_bytes((HERE / "schema.sql").read_bytes())
        self.db, self.prompt = self.base / "prior.sqlite", self.base / "prompt.txt"
        self.prompt.write_text("Original synthetic fixture prompt\n")
        self.old_stage = {"stages": [{"id": f"G{i}", "current_status": f"PRIOR_{i}"} for i in range(10)]}
        self.put(self.prior / "STAGE_DELTA.json", self.old_stage)
        self.put(self.prior / "historical.json", {"status": "HISTORICAL_ONLY"})
        with sqlite3.connect(self.db) as db:
            db.executescript("CREATE TABLE meta(key TEXT PRIMARY KEY,value_json TEXT); CREATE TABLE artifacts(artifact_id TEXT PRIMARY KEY,namespace TEXT,relative_path TEXT,bytes INTEGER,sha256 TEXT); CREATE TABLE w1_artifacts(artifact_id TEXT PRIMARY KEY,namespace TEXT,relative_path TEXT,bytes INTEGER,sha256 TEXT); CREATE TABLE w1_stage_delta(stage_id TEXT PRIMARY KEY,current_status TEXT); CREATE TABLE historical_payload(id INTEGER PRIMARY KEY,value BLOB); CREATE INDEX payload_index ON historical_payload(value); CREATE VIEW payload_view AS SELECT id FROM historical_payload;")
            db.execute("INSERT INTO meta VALUES (?,?)", ("original_prompt_sha256", json.dumps(M.sha(self.prompt))))
            for name in ("STAGE_DELTA.json", "historical.json"):
                p = self.prior / name
                db.execute("INSERT INTO w1_artifacts VALUES (?,?,?,?,?)", ("continuation:" + name, "continuation", name, p.stat().st_size, M.sha(p)))
            db.executemany("INSERT INTO w1_stage_delta VALUES (?,?)", [(s["id"], s["current_status"]) for s in self.old_stage["stages"]])
            db.execute("INSERT INTO historical_payload VALUES (?,?)", (1, b"\x00\xff preserved"))
        self.addCleanup(patch.stopall)
        patch.object(M, "PRIOR_DB_SHA", M.sha(self.db)).start()
        patch.object(M, "PROMPT_SHA", M.sha(self.prompt)).start()
        patch.object(M, "PRIOR_STAGE_SHA", M.sha(self.prior / "STAGE_DELTA.json")).start()
        self.identities = {"base_commit": M.BASE_COMMIT, "original_prompt_sha256": M.PROMPT_SHA, "prior_database_sha256": M.PRIOR_DB_SHA}
        self.put(self.root / "RECOVERY_INVENTORY.json", {"base_commit": M.BASE_COMMIT})
        self.delta = {"schema": M.STAGE_SCHEMA, **self.identities, "stages": [{"id": s["id"], "prior_status": s["current_status"], "current_status": s["current_status"], "scope": "Synthetic contract only", "remaining_gates": ["Science remains open"], "evidence": [self.ref("prior", "STAGE_DELTA.json")]} for s in self.old_stage["stages"]]}
        self.ledger = {"schema": M.LEDGER_SCHEMA, **self.identities, "records": [], "host_events": []}
        for name, kind, count in (("selection", "ACTUAL_ENDPOINT_SELECTION", 5), ("crosscheck", "ACTUAL_ENDPOINT_CROSSCHECK", 0)):
            self.put(self.root / (name + "_output.json"), {"status": "SYNTHETIC_ONLY", "name": name})
            receipt = {"kind": kind, "accepted": True, "primitive_index": 0, "status": "SYNTHETIC_ONLY", "native_integration_invocations": 0, "candidate_polynomial_evaluations": count, "actual_worker_observed": True, "output": self.ref("continuation", name + "_output.json")}
            self.put(self.root / (name + ".json"), receipt)
            self.ledger["records"].append({"record_id": name, **{k: v for k, v in receipt.items() if k != "output"}, "receipt": self.ref("continuation", name + ".json")})
        self.save()

    def put(self, path, value):
        path.write_text(json.dumps(value, sort_keys=True) + "\n")

    def ref(self, namespace, path):
        base = {"continuation": self.root, "prior": self.prior, "inherited": self.base}[namespace]
        return {"namespace": namespace, "path": path, "sha256": M.sha(base / path)}

    def save(self):
        self.put(self.root / "STAGE_DELTA.json", self.delta)
        self.put(self.root / "EXECUTION_LEDGER.json", self.ledger)

    def build(self, name="output"):
        return M.build(self.root, self.prior, self.db, self.prompt, self.base / name)

    def modify_receipt(self, index, change):
        record = self.ledger["records"][index]
        path = self.root / record["receipt"]["path"]
        receipt = M.load(path); change(receipt); self.put(path, receipt)
        record["receipt"] = self.ref("continuation", path.name)
        self.save()

    def test_exact_preservation_restore_and_distinct_counts(self):
        before = self.db.read_bytes()
        report = self.build()
        self.assertEqual(self.db.read_bytes(), before)
        self.assertTrue(report["prior_tables_and_schema_preserved"])
        self.assertEqual(report["database_logical_sha256"], report["restored_logical_sha256"])
        self.assertEqual(report["execution_counts"], {"actual_endpoint_selections": 1, "actual_endpoint_crosschecks": 1, "accepted_current_endpoint_records": 2, "rejected_current_endpoint_records": 0, "native_integration_invocations": 0, "candidate_polynomial_evaluations": 5, "host_events_not_invocations": 0})
        with sqlite3.connect(self.base / "output/w3_design_audit.sqlite") as db:
            self.assertEqual(db.execute("SELECT value FROM historical_payload").fetchone()[0], b"\x00\xff preserved")
            self.assertEqual(db.execute("SELECT count(*),sum(native_integration_invocations) FROM w3_execution_records").fetchone(), (2, 0))
            self.assertEqual(db.execute("SELECT count(*) FROM w3_stage_delta").fetchone()[0], 10)

    def test_endpoint_cannot_be_labeled_native(self):
        self.ledger["records"][0]["kind"] = "ACTUAL_NATIVE_INVOCATION"; self.save()
        with self.assertRaisesRegex(ValueError, "Unsupported endpoint"): self.build()
        self.assertFalse((self.base / "output").exists())

    def test_nonzero_native_count_rejected(self):
        self.ledger["records"][0]["native_integration_invocations"] = 1; self.save()
        with self.assertRaisesRegex(ValueError, "cannot claim native"): self.build()

    def test_bool_not_integer_count(self):
        self.ledger["records"][0]["candidate_polynomial_evaluations"] = True; self.save()
        with self.assertRaisesRegex(ValueError, "polynomial count"): self.build()

    def test_unobserved_worker_rejected(self):
        self.ledger["records"][0]["actual_worker_observed"] = False; self.save()
        with self.assertRaisesRegex(ValueError, "observed endpoint worker"): self.build()

    def test_receipt_counts_crosschecked(self):
        self.ledger["records"][0]["candidate_polynomial_evaluations"] = 10; self.save()
        with self.assertRaisesRegex(ValueError, "candidate_polynomial_evaluations.*receipt"): self.build()

    def test_tampered_raw_output_rejected(self):
        (self.root / "selection_output.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "evidence SHA"): self.build()

    def test_historical_output_not_new_science(self):
        (self.root / "copied.json").write_bytes((self.prior / "historical.json").read_bytes())
        self.modify_receipt(0, lambda r: r.update(output=self.ref("continuation", "copied.json")))
        with self.assertRaisesRegex(ValueError, "historical output"): self.build()

    def test_duplicate_outputs_are_not_double_counted(self):
        self.modify_receipt(1, lambda r: r.update(output=self.ref("continuation", "selection_output.json")))
        with self.assertRaisesRegex(ValueError, "Duplicate output"): self.build()

    def test_actual_output_must_be_current_namespace(self):
        self.modify_receipt(0, lambda r: r.update(output=self.ref("prior", "historical.json")))
        with self.assertRaisesRegex(ValueError, "output.*continuation namespace"): self.build()

    def test_inherited_evidence_safe_path(self):
        other = self.base / "earlier_source"; other.mkdir()
        self.put(other / "original.json", {"scope": "explicit reference only"})
        self.delta["stages"][0]["evidence"].append(self.ref("inherited", "earlier_source/original.json")); self.save()
        self.assertEqual(self.build()["execution_counts"]["actual_endpoint_selections"], 1)

    def test_inherited_namespace_cannot_alias_current(self):
        self.delta["stages"][0]["evidence"].append(self.ref("inherited", "new/selection.json")); self.save()
        with self.assertRaisesRegex(ValueError, "cannot alias"): self.build()

    def test_inherited_symlink_alias_current_rejected(self):
        (self.base / "new_alias").symlink_to(self.root, target_is_directory=True)
        self.delta["stages"][0]["evidence"].append(self.ref("inherited", "new_alias/selection.json")); self.save()
        with self.assertRaisesRegex(ValueError, "symlink component"): self.build()

    def test_inherited_symlink_alias_prior_rejected(self):
        (self.base / "prior_alias").symlink_to(self.prior, target_is_directory=True)
        self.delta["stages"][0]["evidence"].append(self.ref("inherited", "prior_alias/STAGE_DELTA.json")); self.save()
        with self.assertRaisesRegex(ValueError, "symlink component"): self.build()

    def test_prior_tables_and_stage_pins_enforced(self):
        self.delta["stages"][0]["prior_status"] = "MISSING"; self.save()
        with self.assertRaisesRegex(ValueError, "Incorrect prior status"): self.build()

    def test_create_only_and_snapshot_change(self):
        self.build()
        with self.assertRaises(FileExistsError): self.build()
        source_map = M.load(self.base / "output/W3_SOURCE_MAP.json")
        self.put(self.root / "late.json", {})
        with self.assertRaisesRegex(ValueError, "file set changed"):
            M.verify_snapshot(self.root, self.prior, self.prompt, self.db, source_map)

    def test_references_without_execution_remain_zero(self):
        self.ledger["records"] = []; self.save()
        report = self.build()
        self.assertEqual(report["execution_counts"]["candidate_polynomial_evaluations"], 0)
        self.assertEqual(report["execution_counts"]["native_integration_invocations"], 0)


if __name__ == "__main__":
    unittest.main()
