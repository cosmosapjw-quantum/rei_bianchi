import unittest, math, json,sys, tempfile
from pathlib import Path
import numpy as np
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_science as s
class PhysicsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a,cls.b,cls.orig,cls.h,cls.meta,cls.match=s.load()
  cls.data,cls.result,cls.witness,cls.decile=s.calc(cls.a,cls.b,cls.orig,cls.h,cls.match)
 def test_source_sha(self):
  self.assertEqual(s.sha(ROOT/'source'/s.SOURCE_NAME),s.PR321_SHA)
  self.assertEqual(s.sha(ROOT/'source'/s.STATE_NAME),s.PR320_SHA)
 def test_immutable_head(self):
  self.assertEqual(self.result['origin_rei_pr321_head'],'9afee1ab4a45a7b4b277e183e7e18c59a8d39f4d')
 def test_one_physical_lane(self):
  self.assertEqual(self.meta['saved_model_diagnostic_rows'],276480)
  self.assertEqual(self.result['spatial_nodes'],46080)
 def test_valid_source_time(self):
  self.assertGreater(self.h,0)
  self.assertEqual(self.meta['accepted_tick'],160)
 def test_representative_intervals(self):
  self.assertLess(max(self.match.values()),1e-8)
 def test_original_logT_width(self):
  self.assertLess(np.max(self.data['original_logT_parent_width']),2e-4)
  self.assertGreater(np.max(self.data['original_logT_parent_width']),1.7e-4)
 def test_physical_state_bounds(self):
  for k in ('x_HII','x_HeII','x_HeIII'):
   self.assertTrue(np.all(self.b[k]>0));self.assertTrue(np.all(self.b[k]<1))
  self.assertTrue(np.all(self.b.temperature_K>0))
 def test_charge(self):
  self.assertAlmostEqual(self.result['he_to_h_number_ratio_inferred'],.079,places=11)
  self.assertLess(self.result['max_physical_charge_change_identity_abs'],2e-15)
 def test_HII_counterexample(self):
  x=self.result['channel_diagnostics']['HII']
  self.assertEqual(x['nominal_outside_original_accepted_interval_count'],32946)
  self.assertGreater(x['nominal_outside_original_accepted_interval_fraction'],.70)
 def test_HeII_counterexample(self):
  x=self.result['channel_diagnostics']['HeII']
  self.assertEqual(x['nominal_outside_original_accepted_interval_count'],41034)
 def test_HeIII_scope(self):
  x=self.result['channel_diagnostics']['HeIII']
  self.assertLess(x['nominal_outside_original_accepted_interval_fraction'],.05)
 def test_electron_counterexample(self):
  x=self.result['channel_diagnostics']['electron']
  self.assertEqual(x['nominal_outside_original_accepted_interval_count'],25284)
 def test_four_channels_defined(self):
  self.assertEqual(set(s.CHANNELS),set(self.result['channel_diagnostics']))
 def test_two_snapshot_scope(self):
  self.assertEqual(self.result['snapshots'],2)
  self.assertEqual(self.result['unique_node_snapshot_records'],92160)
 def test_hermite_identity(self):
  for c in s.CHANNELS:
   y=self.data[c+'_dx_difference'];h=self.h;a=self.data[c+'_hermite_start_curvature_per_s2'];b=self.data[c+'_hermite_end_curvature_per_s2'];rr=-h*h*(b-a)/12
   self.assertLess(float(np.max(abs(y-rr))),2e-15)
 def test_regression_chi(self):
  self.assertLess(self.result['channel_diagnostics']['HII']['sum_abs_residual_over_sum_abs_state_change'],.05)
  self.assertGreater(self.result['channel_diagnostics']['HII']['sum_abs_residual_over_sum_abs_state_change'],.035)
 def test_no_fake_promotion(self):
  self.assertEqual(self.result['DAG']['central_reported'],'28/88')
  self.assertEqual(self.result['DAG']['canonical_delta'],0)
  self.assertEqual(self.result['new_original_ivps'],0)
 def test_trapezoid_is_not_original_RHS(self):
  self.assertIn('not an exact or bounded',self.result['semantic_contract']['source_integral'])
  self.assertIn('not a violation',self.result['semantic_contract']['outside_interval'])
 def test_archive_negative(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):s.load(Path(td))
 def test_wrong_hash_reject(self):
  with patch.object(s,'PR321_SHA','0'*64):
   with self.assertRaises(ValueError):s.load()
 def test_no_overlap_scoped(self):
  self.assertEqual(self.result['top50_HII_gap_vs_top50_logT_width_overlap'],0)
 def test_temperature_deciles(self):
  self.assertEqual(len(self.decile),10)
  self.assertEqual(sum(z['n'] for z in self.decile),46080)
 def test_nonzero_dynamics(self):
  self.assertGreater(abs(self.result['channel_diagnostics']['HII']['representative_state_change_mean']),1e-5)
 def test_data_fields(self):
  self.assertIn('HII_nominal_trapezoid_outside_accepted_interval',self.data)
 def test_positive_thermal(self):
  self.assertTrue(np.all(self.b.thermal_erg_per_H>0))
if __name__=='__main__':unittest.main()
