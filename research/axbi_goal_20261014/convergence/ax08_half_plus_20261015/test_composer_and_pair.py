#!/usr/bin/env python3
"""AX08 targeted synthetic join and frozen actual-legacy schema regression."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "research/axbi_goal_20261014/driver/full/compose_signed_history.py"
SPEC = importlib.util.spec_from_file_location("ax08_signed_compose", PATH)
compose = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compose)

class Ax08ComposerTest(unittest.TestCase):
    def test_streamed_boundary_once_and_rejection(self):
        with tempfile.TemporaryDirectory(prefix="ax08-fixture-") as scratch:
            root = Path(scratch)
            counts = {}
            for name in compose.FILES:
                prefix = root / ("prefix_" + name)
                segment = root / ("segment_" + name)
                target = root / name
                prefix.write_text("case_id,time_s,value\nSHEAR_HALF_PLUS,0,2\nSHEAR_HALF_PLUS,1,3\n")
                segment.write_text("case_id,time_s,value\nSHEAR_HALF_PLUS,1,3\nSHEAR_HALF_PLUS,2,4\n")
                counts[name] = compose.join_csv(prefix, segment, target, 1., "SHEAR_HALF_PLUS")
                self.assertEqual(counts[name]["composed_rows"], 3)
                with target.open() as stream:
                    self.assertEqual(len(list(csv.DictReader(stream))), 3)
            compose.check_counters({"accepted":"1","attempts":"3","rejections":"0","rhs_evaluations":"21","wall_s":"17"},
                                   {"accepted":"2","attempts":"6","rejections":"0","rhs_evaluations":"42","wall_s":"18"},
                                   counts["history.csv"])
            segment.write_text("case_id,time_s,value\nSHEAR_HALF_PLUS,1,999\nSHEAR_HALF_PLUS,2,4\n")
            with self.assertRaisesRegex(compose.NotReady, "HOLD_SHARED_BOUNDARY_VALUES"):
                compose.join_csv(prefix, segment, root/"bad.csv", 1., "SHEAR_HALF_PLUS")
    def test_source_epochs_are_scoped(self):
        compat = dict(old_source_sha256=compose.OLD,current_source_sha256=compose.NEW,
                      decision_sha256=compose.DECISION,review_sha256=compose.REVIEW,
                      relation="REVIEWED_RESOURCE_ONLY")
        compose.verify_epochs(compose.OLD, compose.NEW, compat)
        with self.assertRaisesRegex(compose.NotReady, "HOLD_SOURCE_EPOCH_COMPATIBILITY"):
            compose.verify_epochs(compose.OLD,"0"*64,compat)
    def test_real_original_v2_comparisons_without_return_field(self):
        orig = ROOT/"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_HALF_PLUS"
        ret = compose.terminal(orig/"RETURN.txt")
        cp = (orig/"checkpoint.txt").read_text().splitlines()
        self.assertNotIn("comparisons", ret)
        self.assertEqual(int(cp[2].split()[0]), int(ret["accepted"]))
        self.assertEqual(int(cp[2].split()[5]), 200018)
        self.assertTrue(int(ret["accepted"]) <= int(cp[2].split()[5]) <= int(ret["attempts"]))
if __name__ == "__main__":
    unittest.main(verbosity=2)
