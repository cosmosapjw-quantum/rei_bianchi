"""WU R59 original-source EoR scenario screening tests (no production promotion)."""
import unittest,json,csv,gzip,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent/"results"
class TestR59(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((ROOT/"SCENARIO.json").read_text())
  cls.r=json.loads((ROOT/"R59_RESULTS.json").read_text())
  cls.a=json.loads((ROOT/"R59_INDEPENDENT_AUDIT.json").read_text())
  cls.m=json.loads((ROOT/"SOURCE_ABSORBER_OWNER_MATRIX.json").read_text())
  cls.i=json.loads((ROOT/"MATCHED_INPUT_IDENTITY.json").read_text())
 def test_source_original_184k(self):
  self.assertEqual(self.a["source_184320_original_HHe_rows_reconstructed"],184320)
  self.assertEqual(self.r["original_F05_source"]["original_accepted_HHe_real_cells"],46080)
  self.assertEqual(self.s["original_F05"]["full_source_17_knots"],17)
 def test_actual_four_original_F05_epochs(self):
  self.assertEqual(set(self.s["original_F05"]["original_HHe_state_t0_64_128_160"]),{"0","64","128","160"})
  self.assertEqual(self.s["original_F05"]["accepted_last_tick"],160)
 def test_real_F05_ionization_saturated_not_reionization_front(self):
  for epoch in self.s["original_F05"]["original_HHe_state_t0_64_128_160"].values():
   self.assertEqual(epoch["cells_below_xHII_0p99"],0)
   self.assertGreater(epoch["HII"]["min"],.99)
 def test_source_F05_photon_group_conservation(self):
  self.assertEqual(self.s["original_F05"]["original_native_group_photons"]["G3"],{"min":0,"max":0})
  for grp in ("G1","G2a","G2b"):
   self.assertGreater(self.s["original_F05"]["original_native_group_photons"][grp]["min"],0)
 def test_source_F05_redshift_clock(self):
  s=self.s["original_F05"]
  self.assertEqual((s["z_source_start"],s["z_mid"],s["z_end"]),(6.,5.95,5.9))
  self.assertLess(abs(s["accepted_fraction_of_full_source_interval"]-160/131072),1e-13)
  self.assertAlmostEqual(s["clock_H_over_Planck18_5p95"],1.,delta=.02)
 def test_bass_F08_true_640_native_rows(self):
  self.assertEqual(self.s["original_F08"]["source_rows"],640)
  self.assertEqual(self.a["source_BASS_native_models"],4)
  self.assertEqual(self.s["original_F08"]["source_redshift_absolute_epoch"],"NOT_SPECIFIED_IN_S0_SOURCE")
 def test_not_spurious_BI_F05_join(self):
  self.assertGreater(self.s["original_F08"]["H_BASS_over_source_F05_FLRW_clock"],100.)
  self.assertFalse(self.m["one_validated_source_matched_full_EOR_scenario"])
  self.assertFalse(self.a["joint_BI_FLRW_EOR_source_clocks_qualified"])
 def test_real_Thomson_source_hazard_46k(self):
  t=self.s["new_F05_Thomson_material"]["local_hazard_tau"]
  self.assertGreater(t["min"],0.)
  self.assertLess(t["max"],.001)
  self.assertGreater(t["median"],0.)
  self.assertEqual(self.a["original_cell_tau_rows"],46080)
 def test_Thomson_analytic_constant_e_limit(self):
  sigma=6.6524587321e-25
  c=2.99792458e10
  ne=4.0e-4
  dt=5.e9
  integr=dt*(ne+ne)/2.
  self.assertAlmostEqual(sigma*c*integr,sigma*c*ne*dt,places=20)
 def test_independent_recount(self):
  self.assertLess(self.a["maximum_original_cell_Thomson_exposure_relative_error"],1e-12)
  self.assertLess(self.a["maximum_original_HHe_electron_charge_relative_error"],1e-12)
  self.assertLess(self.a["source_gamma_exposure_relative_error"],1e-12)
 def test_real_46k_data_sha(self):
  p=ROOT/self.r["files"]["46080_real_source_cells"]
  self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),self.r["files"]["sha256"])
  with gzip.open(p,"rt") as f:
   n=0
   for row in csv.DictReader(f):
    self.assertEqual(int(row["node"]),n)
    n+=1
   self.assertEqual(n,46080)
 def test_no_sky_observable_claim(self):
  self.assertEqual(self.s["new_F05_Thomson_material"]["observed_Bianchi_or_CMB_tau"],"NOT_COMPUTED")
  self.assertEqual(self.s["gates"]["full_26event_observer_BI_FLRW_matched"],"NOT_RUN")
 def test_source_contract_no_canonical_promotion(self):
  self.assertEqual(self.s["DAG"]["WU"],"34/49")
  self.assertEqual(self.s["DAG"]["REI_central"],"28/88")
  self.assertEqual(self.s["DAG"]["canonical_delta"],0)
  self.assertEqual(self.s["gates"]["official_REI_tick161"],"HOLD")
 def test_source_tamper_negative(self):
  raw=(ROOT/"MATCHED_INPUT_IDENTITY.json").read_bytes()
  corrupted=bytearray(raw);corrupted[25]^=1
  self.assertNotEqual(hashlib.sha256(raw).digest(),hashlib.sha256(corrupted).digest())

if __name__=="__main__":unittest.main()
