"""WU R57 tests: original 26-event state+RHS tangency, positivity and D materiality."""
import json,unittest,csv,gzip
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE/"results"
class TestR57(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.r=json.loads((ROOT/"R57_RESULTS.json").read_text())
    cls.a=json.loads((ROOT/"R57_INDEPENDENT_AUDIT.json").read_text())
 def test_native_source_184320_rows(self):
    self.assertEqual(self.a["original_source_rows"],184320)
    self.assertTrue(self.a["original_source_first_20_columns_byte_content_equal"])
 def test_source_derivative_particle_thermal_identities(self):
    self.assertLess(self.a["original_source_native_electron_identity_max_rel"],5e-13)
    self.assertLess(self.a["original_source_native_thermal_logT_identity_max_rel"],5e-12)
    self.assertLess(self.a["original_source_native_charge_state_identity_max_rel"],1e-12)
 def test_accepted_source_endpoint_and_tangent(self):
    q=self.r["accepted_source_derivative_consistency"]
    for e in q["endpoints"].values():
        self.assertLess(e["max_x_abs"],1e-13)
        self.assertLess(e["max_ne_rel"],5e-13)
        self.assertLess(e["max_T_rel"],5e-13)
    for d in q["source_slope_checks"].values():
        self.assertLess(d["dx_tick_abs"],2e-9)
        self.assertLess(d["dlogT_tick_abs"],2e-9)
 def test_source_initial_and_continuum_not_claimed(self):
    self.assertEqual(self.r["historical_initial_D"],"NOT_SOURCE_AUTHENTIC")
    self.assertEqual(self.r["continuous_original_26event_owner_trajectory"],"NOT_RECONSTRUCTED")
    self.assertEqual(self.r["original_rei_tick161"],"HOLD")
 def test_actual_46080_histories(self):
    self.assertEqual(self.r["real_original_source_cells"],46080)
    self.assertEqual(self.a["R57_full_physical_cells"],46080)
    self.assertEqual(self.a["R57_DI_positive_cone_violations"],0)
 def test_photon_number_5flux_and_energy(self):
    for key,x in self.r["results"].items():
        self.assertLess(x["max_photon_conservation_residual_rel"],5e-11,key)
        self.assertLess(x["max_full_population_ledger"],1e-11,key)
        self.assertGreaterEqual(x["first_tick_gross_photons_total"],0.)
        self.assertLess(max(self.a["first_tick_photons_independent_all_cell_recount_rel"].values()),5e-12)
 def test_original_science_not_fake_promotion(self):
    self.assertEqual(self.r["DAG"]["WU"],"34/49")
    self.assertEqual(self.r["DAG"]["REI_CENTRAL"],"28/88")
    self.assertEqual(self.r["DAG"]["canonical_delta"],0)
 def test_source_curve_changes_D_but_not_history_IC_ambiguity(self):
    a=self.r["results"]
    self.assertGreater(a["ALL_NEUTRAL_native_rhs_hermite"]["first_tick_gross_photons_total"],1000*a["H_MATCHED_native_rhs_hermite"]["first_tick_gross_photons_total"])
    self.assertLess(abs(a["H_MATCHED_native_rhs_hermite"]["first_tick_gross_photons_total"]/a["H_MATCHED_owner_point_linear"]["first_tick_gross_photons_total"]-1),0.001)
 def test_source_corrected_gross_heat_is_not_native_net(self):
    self.assertTrue(self.r["numerical"]["gross_not_net_heat"])
    self.assertEqual(self.r["results"]["H_MATCHED_native_rhs_hermite"]["first_tick_gross_heat_gt1pct_deltaU_cells"],0)

if __name__=="__main__":unittest.main()
