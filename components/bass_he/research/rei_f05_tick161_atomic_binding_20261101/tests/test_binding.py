import csv,gzip,hashlib,importlib.util,json,math,unittest
from decimal import Decimal,localcontext
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("binding_model",ROOT/"latent_energy.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def first(path):
 with gzip.open(path,"rt") as f:return next(csv.DictReader(f))
class TestNativeF05HeBinding(unittest.TestCase):
 def setUp(self):
  self.inc=first(m.S/"REI_ORIGINAL26_COMMON_PARENT_INCREMENT_46080.csv.gz")
  self.prev=first(m.S/"ORIGINAL_REI_F05_TICK161_HHE_T_ELECTRON_PREVIEW_46080.csv.gz")
 def test_original_authority_pinned(self):
  p,i,pr,old=m.pin()
  self.assertEqual(pr["official_state_161"],"NOT_ACCEPTED_OR_WRITTEN")
  self.assertEqual(old["original_local_error_gate"],2e-4)
 def test_source_identity_tamper_rejected(self):
  original=m.PREVIEW_CSV_SHA
  try:
   m.PREVIEW_CSV_SHA="0"*64
   with self.assertRaises(ValueError):m.pin()
  finally:m.PREVIEW_CSV_SHA=original
 def test_f05_he_abundance_mismatch_rejected(self):
  p=dict(self.prev)
  p["source_He_nuclei_N_lower"]=str(Decimal(p["source_He_nuclei_N_lower"])*Decimal("1.1"))
  with self.assertRaises(ValueError):m.atom(self.inc,p)
 def test_inverted_original_delta_rejected(self):
  a=dict(self.inc)
  a["x_HII_original_twohalf_increment_lower"]="1"
  a["x_HII_original_twohalf_increment_upper"]="-1"
  with self.assertRaises(ValueError):m.atom(a,self.prev)
 def test_he_two_stages_and_total_identity(self):
  with localcontext() as ctx:
   ctx.prec=90
   a=m.atom(self.inc,self.prev)
   for j in range(2):
    self.assertEqual(a["dB_He"][j],a["dB_He_first"][j]+a["dB_He_second"][j])
    self.assertEqual(a["dB_total"][j],a["dB_H"][j]+a["dB_He"][j])
    self.assertGreater(a["B161"][j],0)
 def test_original_electron_interval_overlap(self):
  with localcontext() as ctx:
   ctx.prec=90
   x=m.atom(self.inc,self.prev)["dNe"]
   target=m.I(self.prev,"tick160_to_161_delta_electron_N")
   self.assertLessEqual(x[0],target[1])
   self.assertGreaterEqual(x[1],target[0])
 def test_float_readback_outward_from_decimal(self):
  for d in [Decimal("0.12345678987654321"),Decimal("-1e43"),Decimal("3.33e-130")]:
   self.assertLessEqual(Decimal.from_float(float(m.conservative(d,False))),d)
   self.assertGreaterEqual(Decimal.from_float(float(m.conservative(d,True))),d)
 def test_all_46080_rows_and_digest(self):
  r=json.loads((ROOT/"results/RESULT.json").read_text())
  p=ROOT/"results/ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz"
  self.assertEqual(m.sha(p),r["output_sha256"])
  with gzip.open(p,"rt") as f:
   rd=csv.DictReader(f);n=0
   self.assertEqual(len(rd.fieldnames),19)
   for row in rd:
    self.assertEqual(int(row["node"]),n)
    for k in ("dB_H","dB_He_first","dB_He_second","dB_He",
              "dB_total","dNe","dB_total_eV_per_H","B161","U161"):
     self.assertLessEqual(float(row[k+"_lower"]),float(row[k+"_upper"]))
    n+=1
  self.assertEqual(n,46080)
 def test_physical_result_and_admission(self):
  q=json.loads((ROOT/"results/RESULT.json").read_text())
  self.assertTrue(q["global_intervals"]["dB_total"]["upper"]<0)
  self.assertTrue(q["global_intervals"]["dB_He"]["upper"]<0)
  self.assertLess(q["helium_share_of_global_ionization_storage_decline"]["lower"],.21)
  self.assertGreater(q["helium_share_of_global_ionization_storage_decline"]["lower"],.19)
  self.assertEqual(q["canonical_delta"],0)
  self.assertEqual(q["official_tick161"],"NOT_ACCEPTED")
  self.assertEqual(q["new_cosmological_IVPs"],0)
 def test_independent_audit_receipt(self):
  q=json.loads((ROOT/"results/INDEPENDENT_AUDIT.json").read_text())
  self.assertEqual(q["source_sample_count"],46080)
  self.assertLess(q["maximum_global_independent_relative_error"],1e-12)
  self.assertEqual(q["source_46080_rows_and_all_energy_outputs"],"PASS")
if __name__=="__main__":unittest.main()
