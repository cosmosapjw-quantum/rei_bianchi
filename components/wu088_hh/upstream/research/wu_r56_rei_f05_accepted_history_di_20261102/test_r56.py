"""WU R56 source-conditional original REI history science tests. Never promote owner."""
import gzip,json,csv,unittest,math
from pathlib import Path

HERE=Path(__file__).resolve().parent
RESULTS=HERE/"results"
class HistoryR56(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=json.loads((RESULTS/"R56_RESULTS.json").read_text())
  cls.a=json.loads((RESULTS/"R56_ADVERSARIAL_AUDIT.json").read_text())
 def test_real_accepted_history_source(self):
  q=self.r
  self.assertEqual(q["REC_original_history_PR"],195)
  self.assertEqual(q["physical_scope"]["source_accepted_ticks"],[0,64,128,160])
  self.assertEqual(q["physical_scope"]["source_original_HHe_cells"],46080)
  self.assertEqual(q["validation"]["original_source_cell_epoch_records"],184320)
  self.assertEqual(q["source_sha256"]["REI_states"]["160"],"74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6")
 def test_four_physical_initial_conditions(self):
  n=self.r["scenario_tick160_161"]
  self.assertEqual(set(n),{"ALL_NEUTRAL","H_MATCHED","CX_EQ","ALL_IONIZED"})
  self.assertLess(n["ALL_NEUTRAL"]["tick160_Dplus_initial"]["median"],.8)
  self.assertGreater(n["H_MATCHED"]["tick160_Dplus_initial"]["median"],.99)
  self.assertLess(n["H_MATCHED"]["tick160_Dplus_initial"]["median"],n["ALL_IONIZED"]["tick160_Dplus_initial"]["median"])
 def test_photon_energy_and_positive_chemistry(self):
  for label,z in self.r["scenario_tick160_161"].items():
   self.assertLess(z["max_photon_conservation_residual_rel"],1e-11,label)
   self.assertLess(z["max_full_population_ledger"],1e-11,label)
   self.assertLess(z["max_electron_compensation_ledger"],1e-16,label)
   self.assertGreaterEqual(z["first_tick_gross_photons_total"],0)
   self.assertGreaterEqual(z["first_tick_gross_heat_gt1pct_deltaU_cells"],0)
   self.assertLessEqual(z["first_tick_gross_heat_gt1pct_deltaU_cells"],46080)
 def test_historical_chemistry_materiality(self):
  n=self.r["scenario_tick160_161"]
  ratio=n["ALL_NEUTRAL"]["first_tick_gross_photons_total"]/n["H_MATCHED"]["first_tick_gross_photons_total"]
  self.assertGreater(ratio,1000.)
  self.assertEqual(n["H_MATCHED"]["first_tick_gross_heat_gt1pct_deltaU_cells"],0)
  self.assertGreater(n["ALL_NEUTRAL"]["first_tick_gross_heat_gt1pct_deltaU_cells"],10000)
 def test_donor_interpolation_not_exact_history(self):
  n=self.r["scenario_tick160_161"]["H_MATCHED"]["first_tick_gross_photons_total"]
  a=self.r["scenario_LEFT_HOLD_tick160_161"]["first_tick_gross_photons_total"]
  self.assertGreater(abs(a/n-1),.001)
  self.assertEqual(self.r["physical_scope"]["between_epochs"],"SOURCE_CONDITIONAL_LINEAR_X_NE_LOG_LINEAR_T")
 def test_same_author_independent_46080_readback(self):
  a=self.a
  self.assertEqual(a["native_source_original_46080_cells_read"],46080)
  self.assertLess(max(a["independent_first_tick_photon_recount_max_rel"].values()),1e-12)
  self.assertLess(a["independent_savin_cx_at_tick0_max_abs"],1e-12)
  self.assertTrue(a["native_original_state_hashes_match"])
  self.assertTrue(all(v==0 for v in a["DII_positivity_violations"].values()))
  self.assertEqual(a["separate_DOP853_fixed_original_photons_not_coupled"]["H_MATCHED"]["source_cells"],12)
 def test_different_numerical_method_observed(self):
  self.assertLess(self.r["validation"]["H_MATCHED_RK2_vs_RK4_DII_tick160_max_abs"],1e-10)
  self.assertLess(self.a["separate_DOP853_fixed_original_photons_not_coupled"]["ALL_NEUTRAL"]["max_abs"],1e-3)
 def test_dag_and_owner_hold(self):
  self.assertEqual(self.r["DAG"]["WU"],"34/49")
  self.assertEqual(self.r["DAG"]["REI_CENTRAL"],"28/88")
  self.assertEqual(self.r["DAG"]["new_canonical_nodes"],0)
  self.assertEqual(self.r["gates"]["official_tick161"],"HOLD")
  self.assertTrue(self.r["physical_scope"]["full_original_HHeDI_OTSPHOTON_EINSTEIN"]=="NOT_RUN")
  self.assertEqual(self.r["physical_scope"]["true_historical_D_initial"],"UNKNOWN_NOT_IN_REI_ORIGINAL_26EVENT")
 def test_actual_46080_rows(self):
  p=RESULTS/self.r["files"]["full_csv_name"]
  with gzip.open(p,"rt") as f:
   rec=csv.DictReader(f)
   count=0
   for row in rec:
    self.assertEqual(int(row["node"]),count)
    count+=1
  self.assertEqual(count,46080)

if __name__=="__main__":unittest.main()
