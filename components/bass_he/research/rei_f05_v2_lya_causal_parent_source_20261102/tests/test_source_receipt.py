#!/usr/bin/env python3
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("hei153_receipt",ROOT/"verify_published_receipt.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class OriginalV2HeIILya(unittest.TestCase):
 def test_photon_source_frozen_receipt(self):v.verify()
 def test_corrupted_origin_source_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   for f in v.EXPECTED:shutil.copy2(ROOT/"results"/f,p/f)
   f=p/"SCIENCE_RESULT.json";f.write_bytes(f.read_bytes()+b"\n")
   with self.assertRaisesRegex(ValueError,"HASH"):v.verify(p)
 def test_no_false_owner_admission(self):
  d=json.loads((ROOT/"results/SCIENCE_RESULT.json").read_text())
  self.assertEqual(d["source_escape_branch_f_interval"],[0.1,1.0])
  self.assertEqual(d["source_ticks161_162_official"],False)
  self.assertEqual(d["canonical_delta"],0)
  self.assertEqual(d["production"],"HOLD")
if __name__=="__main__":unittest.main()
