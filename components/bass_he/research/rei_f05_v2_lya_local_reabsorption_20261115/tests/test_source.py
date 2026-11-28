#!/usr/bin/env python3
"""Public derived source-free scoped tests; negative tamper and source gate."""
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
D=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("pr154_public_ots_receipt",D/"verify_published_receipt.py")
ver=importlib.util.module_from_spec(spec);spec.loader.exec_module(ver)
class HeIILocalOTSSource(unittest.TestCase):
 def test_original_OTS_all_92160_receipts(self):ver.verify()
 def test_untrusted_json_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   for name in ver.FIXED:shutil.copy2(D/"results"/name,p/name)
   src=p/"LOCAL_OTS_FEEDBACK_SCIENCE.json"
   src.write_bytes(src.read_bytes()+b"\n")
   with self.assertRaisesRegex(ValueError,"SHA_DRIFT"):ver.verify(p)
 def test_ots_not_double_count_or_causal_transport(self):
  j=json.loads((D/"results/LOCAL_OTS_FEEDBACK_SCIENCE.json").read_text())
  self.assertEqual(j["source_f_interval"],[.1,1.])
  self.assertTrue(j["actual_original_event_heat_preserved"])
  self.assertTrue(j["re_absorbed_OTS_photons_already_in_source_population_RHS"])
  self.assertTrue(j["source_no_spatial_cells_or_null_rays"])
  self.assertFalse(j["original_tick161_162_official"])
  self.assertEqual(j["canonical_delta"],0)
if __name__=="__main__":unittest.main()
