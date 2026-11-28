#!/usr/bin/env python3
import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
D=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("pr151_public_lya_verifier",D/"verify_published_receipt.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class HeIILyaReceiptTests(unittest.TestCase):
 def test_original_sourcefree_spectral_number_energy(self):
  mod.verify()
 def test_corrupted_published_energy_rejected(self):
  with tempfile.TemporaryDirectory() as root:
   src=Path(root)
   for n in mod.FILES:shutil.copy2(D/"results"/n,src/n)
   x=src/"SCIENCE_RESULT.json"
   x.write_bytes(x.read_bytes()+b" ")
   with self.assertRaisesRegex(ValueError,"SHA"):mod.verify(src)
 def test_no_new_IGM_ivp_or_causal_derived_photon(self):
  data=json.loads((D/"results/SCIENCE_RESULT.json").read_text())
  self.assertEqual(data["original_tick161"],"NOT_ACCEPTED")
  self.assertEqual(data["source_branch_f_range"],[0.1,1.0])
  self.assertEqual(data["canonical_delta"],0)
  self.assertEqual(data["original_spectrum_and_causal_transport"],"NOT_ADMITTED")
if __name__=="__main__":unittest.main()
