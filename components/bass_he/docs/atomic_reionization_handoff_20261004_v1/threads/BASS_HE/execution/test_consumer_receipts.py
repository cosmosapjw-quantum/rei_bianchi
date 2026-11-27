"""Focused receipt-boundary checks using the pinned, imported REI-F00 data."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
DATA = HERE / "HE_F2_INTAKE_20261004T131324Z/consumer"
PACKET = "docs/atomic_reionization_handoff_20261004_v1/"
RECEIPT_PATH = PACKET + "runtime_returns/REI-F00.json"
MODEL_PATH = PACKET + "runtime_inputs/rei_model_lock.json"
COMMIT = "5f3bfe2fc8fe275ab6a054ca9082f03c5b91427a"


def load_module(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if (HERE / "consumer_receipts.py").exists():
    import_scope_lock = load_module(HERE / "consumer_receipts.py").import_scope_lock
else:
    def import_scope_lock(*args):
        raise AssertionError("Verified scope-lock import has not been implemented")


class ScopeReceiptTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads((HERE / "HE_F2_INTAKE_20261004T130100Z/RESUME_STATE.json").read_bytes())
        self.receipt = json.loads((DATA / RECEIPT_PATH).read_bytes())
        self.files = {str(p.relative_to(DATA)): p.read_bytes() for p in DATA.rglob("*") if p.is_file()}

    def apply(self):
        return import_scope_lock(self.state, json.dumps(self.receipt).encode(), self.files, COMMIT)

    def replace_artifact(self, path, value):
        self.files[path] = json.dumps(value).encode()
        for artifact in self.receipt["artifacts"]:
            if artifact["path"] == path:
                artifact["sha256"] = hashlib.sha256(self.files[path]).hexdigest()

    def test_imports_verified_scope_only_and_preserves_input_state(self):
        before = copy.deepcopy(self.state)
        result = self.apply()
        self.assertEqual(result["completed_task_ids"], ["HE-P0", "HH-F0", "HE-F1", "REI-F00"])
        self.assertEqual(self.state, before)
        self.assertNotIn("REI-F01", result["completed_task_ids"])
        verified = result["runtime_results"][-1]
        self.assertEqual(verified["published_commit"], COMMIT)
        self.assertIs(verified["scope"]["rct_enabled"], False)
        self.assertIs(verified["scope"]["physical_provider_admitted"], False)

    def test_selector_leaves_only_provider_task_unmet(self):
        root = HERE.parents[2]
        selector = load_module(root / "tools/task_packet.py")
        program = json.loads((root / "PROGRAM.json").read_bytes())
        result = selector.select(program, self.apply(), "BASS_HE")
        task = next(t for t in result["waiting"] if t["id"] == "HE-F2")
        self.assertEqual(task["unmet"], ["REI-F01"])

    def test_rejects_uncompleted_receipt(self):
        self.receipt["state"] = "partial"
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_wrong_task(self):
        self.receipt["task_id"] = "REI-F01"
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_receipt_without_claim_ceiling(self):
        del self.receipt["claim"]["ceiling"]
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_changed_artifact_bytes(self):
        self.files[MODEL_PATH] += b" "
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_missing_artifact(self):
        del self.files[MODEL_PATH]
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_duplicate_artifact_paths(self):
        self.receipt["artifacts"].append(copy.deepcopy(self.receipt["artifacts"][0]))
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_failed_verification_command(self):
        self.receipt["commands"][0]["exit_code"] = 1
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_missing_command_evidence(self):
        del self.files[self.receipt["commands"][0]["evidence_path"]]
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_fixture_with_wrong_content_identity(self):
        path = self.receipt["input_identity"]["fixture_path"]
        self.files[path] += b" "
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_rehashed_model_from_different_consumer(self):
        model = json.loads(self.files[MODEL_PATH])
        model["model_id"] = "DIFFERENT_CONSUMER"
        self.replace_artifact(MODEL_PATH, model)
        with self.assertRaises(ValueError):
            self.apply()

    def test_rejects_rehashed_model_with_different_input_identity(self):
        model = json.loads(self.files[MODEL_PATH])
        model["identity"]["source_commit"] = "0" * 40
        self.replace_artifact(MODEL_PATH, model)
        with self.assertRaises(ValueError):
            self.apply()

    def test_repeated_receipt_does_not_duplicate_completion_or_evidence(self):
        first = self.apply()
        second = import_scope_lock(first, json.dumps(self.receipt).encode(), self.files, COMMIT)
        self.assertEqual(second, first)

    def test_preserves_conflicting_existing_completion(self):
        first = self.apply()
        before = copy.deepcopy(first)
        with self.assertRaises(ValueError):
            import_scope_lock(first, json.dumps(self.receipt).encode(), self.files, "0" * 40)
        self.assertEqual(first, before)


if __name__ == "__main__":
    unittest.main()
