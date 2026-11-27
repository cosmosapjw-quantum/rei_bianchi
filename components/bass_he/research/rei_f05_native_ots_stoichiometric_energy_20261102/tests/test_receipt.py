#!/usr/bin/env python3
import importlib.util,shutil,tempfile,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("bass_he_ots_public_verifier",HERE/"verify_published_receipt.py")
ver=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ver)
class OriginalPhysicsReceiptTests(unittest.TestCase):
 def test_original_source_receipt(self):ver.verify()
 def test_mismatched_derived_json_refused(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)
   for f in ver.FIXED:shutil.copy2(HERE/"results"/f,out/f)
   p=out/"SCIENCE_RESULT.json";p.write_bytes(p.read_bytes()+b" ")
   with self.assertRaisesRegex(ValueError,"SHA_DRIFT"):ver.verify(out)
 def test_no_false_photon_or_canonical_claim(self):
  import json
  a=json.loads((HERE/"results/SCIENCE_RESULT.json").read_text())
  self.assertEqual(a["canonical_delta"],0)
  self.assertFalse(a["official_tick161"])
  self.assertFalse(a["photon_spectral_emissivity_admitted"])
  self.assertEqual(a["result"]["original_nodes"],46080)
if __name__=="__main__":unittest.main()
