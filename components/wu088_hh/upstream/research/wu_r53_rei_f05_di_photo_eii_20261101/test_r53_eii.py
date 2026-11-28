"""Source-conditional EII branch test for original 46k REI H/D atomic kinetics."""
import csv,gzip,hashlib,json,unittest
from pathlib import Path
import numpy as np
import r53_eii_sensitivity as e
import r53_photo_chemistry as b

class TestEii(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((b.ROOT/"results/R53_EII_RESULTS.json").read_text())
  cls.v=b.load()
 def test_native_original_source_sha(self):
  z=e.source_check()
  self.assertEqual(b.sha(e.SRC/"REI_joint_sink_reservoir_history.py"),z["original_REI_module_SHA256"])
 def test_native_beta_rate_physical(self):
  T=np.array([2096.67,10000.,50000.,66261.76])
  self.assertTrue(np.all(e.beta_HI(T)>0))
  self.assertTrue(np.all(np.diff(e.beta_HI(T))>0))
 def test_no_EII_exact_original_R53_full_source(self):
  v=self.v
  kf,kr=b.savin(v["T0"],v["knots"],v["forward"],v["reverse"])
  y0=np.zeros(b.N)
  original=e.integrate(v,y0,eii=0.,steps=64)
  with gzip.open(e.OUT/b.FNAME,"rt") as f:
   expected=np.array([float(row["caseB_photo_y_final_neutral"]) for row in csv.DictReader(f)])
  self.assertLess(float(np.max(abs(original["y"]-expected))),2e-12)
 def test_EII_photons_nonnegative(self):
  self.assertGreater(self.r["total_DI_photo_reactions_with_EII_initial_neutral"],0)
  self.assertGreater(self.r["N_EII_exposure_gt_original_HI_photo_exposure"],0)
  self.assertGreater(self.r["N_EII_sink_gt1pct_native_F05_thermal"],0)
 def test_EII_effect_is_material_in_high_temperature_tail(self):
  self.assertGreater(self.r["EII_on_minus_off_initial_neutral_y"]["max"],.01)
  self.assertGreater(self.r["native_EII_exposure_start"]["max"],.1)
  self.assertLess(self.r["native_EII_exposure_start"]["median"],.0001)
 def test_EII_threshold_energy_correct(self):
  self.assertAlmostEqual(e.EII_CHI_E_V,13.6017,delta=1e-14)
  self.assertAlmostEqual(e.EV_ERG,1.602176634e-12,delta=0)
 def test_EII_source_file_46080_rows_and_5flux_ledger(self):
  path=e.OUT/"R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz"
  num=0
  with gzip.open(path,"rt") as f:
   for row in csv.DictReader(f):
    self.assertEqual(num,int(row["node"]));num+=1
    self.assertGreater(float(row["native_beta_HI_cm3_s"]),0)
    self.assertGreaterEqual(float(row["EII_collisional_ionizations_per_D_neutral"]),0)
    self.assertLessEqual(abs(float(row["EII_5flux_stoich_residual"])),2e-13)
    self.assertLessEqual(float(row["EII_thermal_threshold_sink_erg_per_H_neutral"]),0)
  self.assertEqual(num,b.N)
 def test_original_photo_budget_count_robustness(self):
  self.assertGreater(self.r["DI_photo_over_native_photon_emission_withEII"],.04)
  self.assertLess(self.r["DI_photo_over_native_photon_emission_withEII"],.06)
  self.assertLess(self.r["DI_photo_over_native_photon_emission_withEII"],
                  self.r["DI_photo_over_native_photon_emission_noEII"])
 def test_original_DAG_and_scope_not_admitted(self):
  self.assertEqual(self.r["canonical_DAG"]["WU"],"34/49")
  self.assertEqual(self.r["canonical_DAG"]["REI_central"],"28/88")
  self.assertEqual(self.r["status"],"SOURCE_CONDITIONAL_EII_UPPER_PHYSICAL_RISK_CHECK_NOT_ORIGINAL_OWNER_ADMISSION")
 def test_source_against_current_checksum(self):
  self.assertEqual(b.sha(e.OUT/"R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz"),
                   self.r["full_source_five_flux_sha256"])

if __name__=="__main__":unittest.main()
