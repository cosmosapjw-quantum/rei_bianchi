#!/usr/bin/env python3
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
D=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("pr152_frozen_receipt",D/"verify_published_receipt.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class SourceFrozenWindowReceipt(unittest.TestCase):
 def test_original_source_firstflight_conditional(self):mod.verify()
 def test_source_hash_tamper_rejected(self):
  with tempfile.TemporaryDirectory() as temp:
   q=Path(temp)
   for n in mod.EXPECTED:shutil.copy2(D/"results"/n,q/n)
   p=q/"SCIENCE_RESULT.json"
   p.write_bytes(p.read_bytes()+b" ")
   with self.assertRaisesRegex(ValueError,"HASH_CHANGED"):mod.verify(q)
 def test_unconditional_claim_and_source_rules(self):
  a=json.loads((D/"results/SCIENCE_RESULT.json").read_text())
  self.assertTrue(a["original_causal_geometry_not_identified"])
  self.assertEqual(a["source_f_interval"],[0.1,1.0])
  self.assertEqual(a["canonical_delta"],0)
  self.assertEqual(a["original_tick161"],"NOT_ACCEPTED")
  self.assertEqual(a["original_line_transported"],"NO_SOURCE_RAY_PATHS")
if __name__=="__main__":unittest.main()
