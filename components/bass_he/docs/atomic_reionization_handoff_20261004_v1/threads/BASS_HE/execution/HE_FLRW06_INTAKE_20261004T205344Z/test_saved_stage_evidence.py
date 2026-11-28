"""Corrupted imported evidence must fail before any new receipt is created."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = next(path for path in Path(__file__).resolve().parents if (path / ".git").exists())
RESTORED = ROOT / "runs/HE_FLRW06_INTAKE_20261004T205344Z/restored/rei_chat_flrw06_native_20261005"


class SavedEvidenceBoundary(unittest.TestCase):
    def reject_mutation(self, relative, transform):
        spec = importlib.util.spec_from_file_location("saved_check", RESTORED / "research/final_check_preserving_receipt.py")
        module = importlib.util.module_from_spec(spec)
        with patch.object(sys, "path", [str(RESTORED / "research"), *sys.path]):
            spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "inputs"
            shutil.copytree(RESTORED, root)
            path = root / relative
            path.write_bytes(transform(path.read_bytes()))
            module.ROOT = root
            out = Path(directory) / "verification.json"
            with patch.object(sys, "argv", ["saved_check", str(out)]):
                with self.assertRaises(AssertionError):
                    module.main()
            self.assertFalse(out.exists())

    def test_changed_stage_stdout(self):
        self.reject_mutation("results/stage_stdout.jsonl", lambda b: b + b"\n")

    def test_changed_stage_binary(self):
        self.reject_mutation("results/stage_probe", lambda b: b[:-1] + bytes([b[-1] ^ 1]))

    def test_changed_current_stage_source(self):
        self.reject_mutation("results/stage_build/coupled_primary.rs", lambda b: b + b"\n")

    def test_failed_stage_reference_record(self):
        def fail(data):
            record = json.loads(data)
            record["status"] = "FAIL"
            return json.dumps(record).encode()
        self.reject_mutation("results/STAGE_INDEPENDENT_CHECK.json", fail)


if __name__ == "__main__":
    unittest.main(verbosity=2)
