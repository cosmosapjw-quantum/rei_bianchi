"""Synthetic storage/accounting contracts; never launch scientific workers."""
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w3_strip_builder", HERE / "build_w3_strip_db.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class StripDatabaseContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root, self.prior, self.w1 = self.base / "new", self.base / "prior", self.base / "w1"
        for p in (self.root, self.prior, self.w1): p.mkdir()
        (self.root / "audit_database").mkdir()
        (self.root / "audit_database/schema.sql").write_bytes((HERE / "schema.sql").read_bytes())
        self.db, self.prompt = self.base / "prior.sqlite", self.base / "prompt.txt"
        self.prompt.write_text("Original synthetic fixture prompt\n")
        self.old_stage = {"stages": [{"id": f"G{i}", "current_status": f"PRIOR_{i}"} for i in range(10)]}
        self.put(self.prior / "STAGE_DELTA.json", self.old_stage)
        self.put(self.w1 / "00.json", self.native(True, "RADIUS_MET", "old-00"))
        with sqlite3.connect(self.db) as db:
            db.executescript("CREATE TABLE meta(key TEXT PRIMARY KEY,value_json TEXT); CREATE TABLE artifacts(artifact_id TEXT PRIMARY KEY,namespace TEXT,relative_path TEXT,bytes INTEGER,sha256 TEXT); CREATE TABLE w1_artifacts(artifact_id TEXT PRIMARY KEY,namespace TEXT,relative_path TEXT,bytes INTEGER,sha256 TEXT); CREATE TABLE w1_execution_records(tile_id TEXT,primitive_index INTEGER,accepted INTEGER,receipt_sha256 TEXT); CREATE TABLE w3_artifacts(artifact_id TEXT PRIMARY KEY,namespace TEXT,relative_path TEXT,bytes INTEGER,sha256 TEXT); CREATE TABLE w3_stage_delta(stage_id TEXT PRIMARY KEY,current_status TEXT); CREATE TABLE historical_payload(id INTEGER PRIMARY KEY,value BLOB); CREATE INDEX payload_index ON historical_payload(value); CREATE VIEW payload_view AS SELECT id FROM historical_payload;")
            db.execute("INSERT INTO meta VALUES (?,?)", ("original_prompt_sha256", json.dumps(M.sha(self.prompt))))
            p = self.prior / "STAGE_DELTA.json"
            db.execute("INSERT INTO w3_artifacts VALUES (?,?,?,?,?)", ("continuation:STAGE_DELTA.json", "continuation", "STAGE_DELTA.json", p.stat().st_size, M.sha(p)))
            p = self.w1 / "00.json"
            db.execute("INSERT INTO w1_artifacts VALUES (?,?,?,?,?)", ("continuation:00.json", "continuation", "00.json", p.stat().st_size, M.sha(p)))
            db.execute("INSERT INTO w1_execution_records VALUES (?,?,?,?)", ("00", 0, 1, M.sha(p)))
            db.executemany("INSERT INTO w3_stage_delta VALUES (?,?)", [(s["id"], s["current_status"]) for s in self.old_stage["stages"]])
            db.execute("INSERT INTO historical_payload VALUES (?,?)", (1, b"\x00\xff preserved"))
        self.addCleanup(patch.stopall)
        patch.object(M, "PRIOR_DB_SHA", M.sha(self.db)).start()
        patch.object(M, "PROMPT_SHA", M.sha(self.prompt)).start()
        patch.object(M, "PRIOR_STAGE_SHA", M.sha(self.prior / "STAGE_DELTA.json")).start()
        self.identities = {"base_commit": M.BASE_COMMIT, "original_prompt_sha256": M.PROMPT_SHA, "prior_database_sha256": M.PRIOR_DB_SHA}
        self.put(self.root / "RECOVERY_INVENTORY.json", {"base_commit": M.BASE_COMMIT})
        self.delta = {"schema": M.STAGE_SCHEMA, **self.identities, "stages": [{"id": s["id"], "prior_status": s["current_status"], "current_status": s["current_status"], "scope": "Synthetic contract only", "remaining_gates": ["Science remains open"], "evidence": [self.ref("prior", "STAGE_DELTA.json")]} for s in self.old_stage["stages"]]}
        self.put(self.root / "actual_raw.json", self.native(True, "RADIUS_MET", "new-20"))
        self.ledger = {"schema": M.LEDGER_SCHEMA, **self.identities, "records": [], "host_events": []}
        for name, kind, tile, observed, output in (("actual", M.NATIVE_KIND, "20", 1, self.ref("continuation", "actual_raw.json")), ("reused", M.REUSED_KIND, "00", 0, self.ref("inherited", "w1/00.json"))):
            receipt = {"kind": kind, "tile_id": tile, "accepted": True, "primitive_index": 0, "status": "RADIUS_MET", "native_integration_invocations": observed, "candidate_polynomial_evaluations": 0, "actual_worker_observed": kind == M.NATIVE_KIND, "output": output}
            self.put(self.root / (name + ".json"), receipt)
            self.ledger["records"].append({"record_id": name, **{k: v for k, v in receipt.items() if k != "output"}, "receipt": self.ref("continuation", name + ".json")})
        self.save()

    def native(self, accepted, status, tag):
        return {"accepted": accepted, "status": status, "index": 0, "fixture": tag, "wrapper": {"native_execution_observed": True}}

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

    def change_wrapper(self, index, changes):
        record = self.ledger["records"][index]
        path = self.root / record["receipt"]["path"]
        receipt = M.load(path); receipt.update(changes); self.put(path, receipt)
        record.update({k: v for k, v in changes.items() if k != "output"})
        record["receipt"] = self.ref("continuation", path.name); self.save()

    def change_raw(self, raw):
        self.put(self.root / "actual_raw.json", raw)
        self.change_wrapper(0, {"output": self.ref("continuation", "actual_raw.json")})

    def test_preservation_restore_and_new_vs_reused_counts(self):
        before = self.db.read_bytes(); report = self.build()
        self.assertEqual(self.db.read_bytes(), before)
        self.assertTrue(report["prior_tables_and_schema_preserved"])
        self.assertEqual(report["database_logical_sha256"], report["restored_logical_sha256"])
        self.assertEqual(report["execution_counts"], {"native_dispatch_attempts": 1, "observed_native_integrations": 1, "accepted_current_pilots": 1, "rejected_current_pilots": 0, "reused_W1_tiles": 1, "candidate_polynomial_evaluations": 0, "host_events_not_invocations": 0})
        with sqlite3.connect(self.base / "output/w3_strip_audit.sqlite") as db:
            self.assertEqual(db.execute("SELECT value FROM historical_payload").fetchone()[0], b"\x00\xff preserved")
            self.assertEqual(db.execute("SELECT count(*),sum(native_integration_invocations) FROM w3strip_execution_records").fetchone(), (2, 1))

    def test_observed_rejected_native_remains_counted(self):
        native = self.native(False, "RESOURCE_LIMIT", "new-20")
        self.change_raw({"accepted": False, "index": 0, "reason": "NONZERO_NATIVE_EXIT", "native_stdout": json.dumps(native), "wrapper": native["wrapper"]})
        self.change_wrapper(0, {"accepted": False, "status": "RESOURCE_LIMIT"})
        counts = self.build()["execution_counts"]
        self.assertEqual((counts["native_dispatch_attempts"], counts["observed_native_integrations"], counts["rejected_current_pilots"]), (1, 1, 1))

    def test_failed_dispatch_without_native_output_is_not_native_invocation(self):
        self.change_raw({"schema": M.NO_NATIVE_SCHEMA, "native_output_observed": False, "accepted": False, "primitive_index": 0, "status": "WORKER_FAILED_WITHOUT_NATIVE_OUTPUT"})
        self.change_wrapper(0, {"accepted": False, "native_integration_invocations": 0, "status": "WORKER_FAILED_WITHOUT_NATIVE_OUTPUT"})
        counts = self.build()["execution_counts"]
        self.assertEqual((counts["native_dispatch_attempts"], counts["observed_native_integrations"], counts["rejected_current_pilots"]), (1, 0, 1))

    def test_accepted_requires_native_output(self):
        self.change_wrapper(0, {"native_integration_invocations": 0})
        with self.assertRaisesRegex(ValueError, "accepted pilot requires"): self.build()

    def test_reuse_cannot_claim_current_native(self):
        self.change_wrapper(1, {"native_integration_invocations": 1})
        with self.assertRaisesRegex(ValueError, "zero for reuse"): self.build()

    def test_reuse_cannot_claim_current_worker(self):
        self.change_wrapper(1, {"actual_worker_observed": True})
        with self.assertRaisesRegex(ValueError, "distinguish actual and reused"): self.build()

    def test_actual_cannot_use_historical_raw_copy(self):
        self.change_raw(M.load(self.w1 / "00.json"))
        with self.assertRaisesRegex(ValueError, "historical output"): self.build()

    def test_reused_raw_must_be_hash_known(self):
        self.put(self.w1 / "00.json", self.native(True, "RADIUS_MET", "changed-not-known"))
        self.change_wrapper(1, {"output": self.ref("inherited", "w1/00.json")})
        with self.assertRaisesRegex(ValueError, "hash-known"): self.build()

    def test_reused_raw_cannot_be_current_namespace(self):
        self.change_wrapper(1, {"output": self.ref("continuation", "actual_raw.json")})
        with self.assertRaisesRegex(ValueError, "Raw output namespace"): self.build()

    def test_only_four_authorized_pilot_ids(self):
        self.change_wrapper(0, {"tile_id": "21"})
        with self.assertRaisesRegex(ValueError, "bounded pilot"): self.build()

    def test_duplicate_dispatch_for_same_tile_rejected(self):
        duplicate = copy.deepcopy(self.ledger["records"][0]); duplicate["record_id"] = "duplicate"
        self.ledger["records"].append(duplicate); self.save()
        with self.assertRaisesRegex(ValueError, "Duplicate tile"): self.build()

    def test_bool_is_not_native_count(self):
        self.change_wrapper(0, {"native_integration_invocations": True})
        with self.assertRaisesRegex(ValueError, "Observed native invocation count"): self.build()

    def test_endpoint_evaluation_count_forbidden(self):
        self.change_wrapper(0, {"candidate_polynomial_evaluations": 5})
        with self.assertRaisesRegex(ValueError, "outside this continuation"): self.build()

    def test_native_status_must_match_wrapper(self):
        self.change_wrapper(0, {"status": "MADE_UP"})
        with self.assertRaisesRegex(ValueError, "status.*native output"): self.build()

    def test_unobserved_failure_requires_explicit_missing_output_evidence(self):
        self.change_wrapper(0, {"native_integration_invocations": 0, "accepted": False})
        with self.assertRaisesRegex(ValueError, "missing-output evidence"): self.build()

    def test_observed_claim_needs_native_execution_evidence(self):
        raw = self.native(True, "RADIUS_MET", "new-20"); raw["wrapper"]["native_execution_observed"] = False
        self.change_raw(raw)
        with self.assertRaisesRegex(ValueError, "actual execution at its original time"): self.build()

    def test_reused_receipt_cannot_be_relabelled_as_another_W1_tile(self):
        self.change_wrapper(1, {"tile_id": "15"})
        with self.assertRaisesRegex(ValueError, "pinned W1 receipt identity"): self.build()

    def test_missing_output_cannot_contain_positive_native_evidence(self):
        raw = {"schema": M.NO_NATIVE_SCHEMA, "native_output_observed": False, "accepted": False,
               "primitive_index": 0, "status": "RESOURCE_LIMIT",
               "wrapper": {"native_execution_observed": True},
               "native_stdout": json.dumps(self.native(False, "RESOURCE_LIMIT", "new-20"))}
        self.change_raw(raw)
        self.change_wrapper(0, {"accepted": False, "native_integration_invocations": 0, "status": "RESOURCE_LIMIT"})
        with self.assertRaisesRegex(ValueError, "native receipt markers"): self.build()

    def test_tampered_raw_hash_rejected(self):
        (self.root / "actual_raw.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "evidence SHA"): self.build()

    def test_symlink_inherited_alias_is_rejected(self):
        (self.base / "new_alias").symlink_to(self.root, target_is_directory=True)
        self.delta["stages"][0]["evidence"].append(self.ref("inherited", "new_alias/actual.json")); self.save()
        with self.assertRaisesRegex(ValueError, "symlink component"): self.build()

    def test_prior_stage_status_cannot_drift(self):
        self.delta["stages"][0]["prior_status"] = "MISSING"; self.save()
        with self.assertRaisesRegex(ValueError, "Incorrect prior status"): self.build()

    def test_partial_or_no_dispatch_does_not_imply_missing_success(self):
        self.ledger["records"] = self.ledger["records"][1:]; self.save()
        counts = self.build()["execution_counts"]
        self.assertEqual(counts["native_dispatch_attempts"], 0)
        self.assertEqual(counts["accepted_current_pilots"], 0)
        self.assertEqual(counts["reused_W1_tiles"], 1)

    def test_create_only_and_snapshot_change(self):
        self.build()
        with self.assertRaises(FileExistsError): self.build()
        source_map = M.load(self.base / "output/W3_STRIP_SOURCE_MAP.json")
        self.put(self.root / "late.json", {})
        with self.assertRaisesRegex(ValueError, "file set changed"):
            M.verify_snapshot(self.root, self.prior, self.prompt, self.db, source_map)


if __name__ == "__main__": unittest.main()
