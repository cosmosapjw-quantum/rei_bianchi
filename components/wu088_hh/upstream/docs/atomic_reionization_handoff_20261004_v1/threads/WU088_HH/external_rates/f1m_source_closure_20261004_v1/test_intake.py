"""CLI checks with real pinned archives; damaged bytes are transport fixtures only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
F1M = Path(os.environ["WU088_F1M_ZIP"])
F1P = Path(os.environ["WU088_F1P_ZIP"])


class IntakeTests(unittest.TestCase):
    def call(self, *args):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "verify_f1m_intake.py"), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def test_original_bundle_cannot_close_missing_source(self):
        code, result = self.call("--f1m", F1M)
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "SOURCE_CLOSURE_INCOMPLETE")
        self.assertEqual(result["sources_verified"], 16)
        self.assertEqual(len(result["missing_sources"]), 1)
        self.assertEqual(result["missing_sources"][0]["sha256"], "2ccecac31e88d7b1802b08a084035a309d0ff31eb2b2ce189a8bcdf91e0e625e")

    def test_exact_parent_recovers_source_without_writes(self):
        before = [(p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in (F1M, F1P)]
        code, result = self.call("--f1m", F1M, "--f1p", F1P)
        self.assertEqual(code, 0)
        self.assertEqual(result["sources_verified"], 17)
        self.assertEqual(result["source_lock_scope"], "F1M_DIRECT_17_FILES_ONLY")
        self.assertEqual(result["missing_sources"], [])
        self.assertEqual(len(result["explicit_recoveries"]), 1)
        self.assertEqual(sum(r["origin"] == "F1P" for r in result["verified_sources"]), 1)
        self.assertEqual(result["science_executions"], 0)
        self.assertFalse(result["physical_admission"])
        self.assertEqual(before, [(p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in (F1M, F1P)])

    def damaged(self, archive, role):
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "corrupt-transport.zip"
            data = bytearray(archive.read_bytes()); data[100] ^= 1; bad.write_bytes(data)
            code, result = self.call("--f1m", bad if role == "F1M" else F1M, "--f1p", bad if role == "F1P" else F1P)
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "INTAKE_REJECTED")
            self.assertIn("ARCHIVE_IDENTITY_MISMATCH", result["reason"])

    def test_damaged_bundle_rejected_before_payload_use(self):
        self.damaged(F1M, "F1M")

    def test_damaged_parent_cannot_fill_missing_source(self):
        self.damaged(F1P, "F1P")


if __name__ == "__main__":
    unittest.main()
