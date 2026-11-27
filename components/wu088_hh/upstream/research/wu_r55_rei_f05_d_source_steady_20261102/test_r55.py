"""Regression tests for source-conditional WU R55: no production promotion."""
import csv,gzip,hashlib,json,sys,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
RESULTS=HERE/"results"
sys.path.insert(0,str(HERE))
import audit_r55

class WU55(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((RESULTS/"R55_RESULTS.json").read_text())
 def test_source_locked_real_cells(self):
  r=self.r
  self.assertEqual(r["numeric"]["physical_real_cells"],46080)
  self.assertEqual(r["WU_immutable_parent_head"],"5933f3fb4432bee7f2268c62873132a0d741f054")
  self.assertEqual(r["R54_source_code_sha256"],"ded9c2542d05d4734370d10819d544986c89c06ef57064ea7e376f3580770885")
  self.assertEqual(len(r["original_source_sha256"]),12)
 def test_analytical_equilibrium_residuals(self):
  q=self.r["initial_condition_analysis"]
  self.assertLess(q["CX_start_rate_residual_relative"],1e-13)
  self.assertLess(q["full_start_rate_residual_relative"],1e-13)
  self.assertGreater(q["initial_FULL"]["min"],.99)
  self.assertLess(q["initial_FULL"]["max"],1)
 def test_photon_chemistry_bracket_and_materiality(self):
  n=self.r["numeric"];o=self.r["original_extremes"]
  self.assertLess(n["FULL_gross_DI_photons_per_cMpc3"],o["ALL_NEUTRAL_DI_gross_photons"])
  self.assertGreater(n["FULL_gross_DI_photons_per_cMpc3"],o["ALL_IONIZED_DI_gross_photons"])
  self.assertLess(n["FULL_photon_demand_over_R54_ALL_NEUTRAL"],.001)
  self.assertEqual(n["FULL_photoheat_exceeds_1pct_native_abs_deltaU_cells"],0)
  self.assertLess(n["FULL_gross_photoheat_over_abs_native_deltaU"]["max"],.001)
 def test_numerical_step_and_group_ledger(self):
  n=self.r["numeric"]
  self.assertLess(n["FULL_ion_fraction_RK32_vs_RK64_max_abs"],1e-10)
  self.assertLess(n["FULL_global_group_photon_ledger_max_rel"],1e-12)
  self.assertLess(n["FULL_cell_5flux_ledger_max_abs"],5e-12)
  self.assertLess(n["FULL_electron_created_since_initial_ledger_max_abs"],1e-16)
 def test_four_group_zero_last(self):
  rows=self.r["four_original_source_groups"]
  self.assertEqual([r["group"] for r in rows],["G1","G2a","G2b","G3"])
  self.assertEqual(rows[-1]["FULL_DI_gross_photoevents_per_cMpc3"],0)
 def test_output_own_sha256(self):
  f=self.r["files"]
  for name,digest in [("physical_full_csv","physical_full_csv_sha256"),
                      ("group_csv","group_csv_sha256"),("24_cell_witness","24_cell_witness_sha256")]:
   path=RESULTS/f[name+"_name"]
   self.assertEqual(audit_r55.sha(path),f[digest])
 def test_independent_readback_of_46080_cells(self):
  result=audit_r55.audit(RESULTS)
  self.assertEqual(result["rows"],46080)
  self.assertLess(result["max_photo_energy_ledger_erg_per_H"],2e-29)
 def test_science_nonadmission(self):
  r=self.r
  self.assertIn("NOT_HISTORICAL",r["status"])
  self.assertEqual(r["DAG"]["REI_central"],"28/88")
  self.assertEqual(r["DAG"]["WU"],"34/49")
  self.assertEqual(r["gates"]["historical_D_evolution"],"NOT_RUN")
  self.assertEqual(r["gates"]["official_tick161_acceptance"],"HOLD")
  self.assertEqual(r["gates"]["production"],"HOLD")

if __name__=="__main__":unittest.main()
