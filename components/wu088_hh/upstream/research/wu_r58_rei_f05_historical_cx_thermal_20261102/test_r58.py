"""R58 regression tests. Original REI/HHe owner is strictly read-only."""
import unittest,json,csv,gzip,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
D=ROOT/"results"

class R58(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((D/"R58_RESULTS.json").read_text())
  cls.a=json.loads((D/"R58_INDEPENDENT_AUDIT.json").read_text())
 def test_original_source(self):
  self.assertEqual(self.r["physical_contract"]["real_cells"],46080)
  self.assertEqual(self.a["original_REI_4epoch_source_rows_scanned"],184320)
  self.assertEqual(self.r["physical_contract"]["source_accepted_HHe_ticks"],[0,64,128,160])
 def test_cx_electron_photon_zero(self):
  for key in ["CX_dN_HII_plus_dN_DII_equals_0","CX_dNe_equals_0",
              "CX_photon_count_equals_0","CX_energy_binding_plus_gas_equals_0"]:
   self.assertTrue(self.r["physical_contract"][key],key)
   if key in ("CX_photon_count_equals_0","CX_energy_binding_plus_gas_equals_0"):
    self.assertTrue(self.a["microscopic_exchange_"+("photon_source_exact_zero" if "photon" in key else "gas_plus_binding_source_exact_zero")])
 def test_source_thermal(self):
  expected=-6.258030833149542e39
  self.assertLess(abs(self.a["native_owner_t160_thermal_power_erg_s"]/expected-1),2e-14)
 def test_real_history_sources(self):
  self.assertLess(self.a["scenarios"]["H_MATCHED"]["independent_rate_160_scaled_error"],1e-12)
  self.assertLess(self.a["scenarios"]["ALL_NEUTRAL"]["independent_power_160_rel_error"],1e-12)
  self.assertEqual(self.a["source_replayed_D_cells"],46080)
 def test_signs(self):
  sc=self.r["scenario_science"]
  self.assertGreater(sc["H_MATCHED"]["CX_history_0to160_signed_gas_energy_erg_per_cMpc3"],0)
  self.assertLess(sc["ALL_NEUTRAL"]["CX_history_0to160_signed_gas_energy_erg_per_cMpc3"],0)
  self.assertGreater(sc["H_MATCHED"]["CX_native_160to161_signed_gas_energy_erg_per_cMpc3"],0)
  self.assertLess(sc["ALL_NEUTRAL"]["CX_native_160to161_signed_gas_energy_erg_per_cMpc3"],0)
 def test_energy_materiality_diagnostic(self):
  sc=self.r["scenario_science"]
  self.assertLess(sc["ALL_NEUTRAL"]["CX_history_0to160_abs_over_original_abs_accepted_deltaU"],.001)
  self.assertLess(sc["H_MATCHED"]["CX_history_0to160_abs_over_original_abs_accepted_deltaU"],1e-7)
  for label,block in sc.items():
   for t in ("0","64","128","160"):
    self.assertEqual(block["instantaneous_original_epoch_CX"][t]["CX_local_abs_heat_over_original_abs_thermal_Udot_gt_one_pct_cells"],0)
 def test_Savin_native_delta_convention(self):
  c=self.r["physical_contract"]
  self.assertAlmostEqual(c["source_Savin_offset_consistent_chi_D_eV"]-c["REI_original_26event_chi_H_eV"],0.0037,places=12)
  self.assertAlmostEqual(c["legacy_D_photo_threshold_upshift_eV"],0.000434599702,places=12)
  self.assertGreater(c["legacy_D_photo_threshold_upshift_eV"],0.)
  self.assertTrue(c["photo_threshold_shift_only_at_fixed_events"])
 def test_photon_recount(self):
  for scenario in ("H_MATCHED","ALL_NEUTRAL"):
   v=self.a["scenarios"][scenario]["independently_reconstructed_parent_R57_photons"]
   s=self.r["scenario_science"][scenario]["first_tick_photon_events_gross_per_cMpc3"]
   self.assertLess(abs(v/s-1),2e-12)
 def test_full_data_integrity(self):
  file=D/self.r["files"]["full_original_source_conditional_46080_csv"]
  h=hashlib.sha256(file.read_bytes()).hexdigest()
  self.assertEqual(h,self.r["files"]["full_original_source_conditional_SHA256"])
  with gzip.open(file,"rt") as f:
   count=0
   for row in csv.DictReader(f):
    self.assertEqual(int(row["node"]),count)
    count+=1
  self.assertEqual(count,46080)
 def test_no_false_admission(self):
  self.assertEqual(self.r["gates"]["official_tick161"],"HOLD")
  self.assertEqual(self.r["DAG"]["new_canonical"],0)
  self.assertTrue(self.r["physical_contract"]["original_26event_HHe_photon_OTS_not_re_evolved"])
  self.assertEqual(self.a["distinct_author"],"NOT_RUN")
 def test_negative_byte_change(self):
  payload=(D/"R58_INDEPENDENT_AUDIT.json").read_bytes()
  altered=bytearray(payload);altered[40]^=1
  self.assertNotEqual(hashlib.sha256(payload).digest(),hashlib.sha256(altered).digest())

if __name__=="__main__":unittest.main()
