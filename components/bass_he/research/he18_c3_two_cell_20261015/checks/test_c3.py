"""Stage-local tests for an already computed HE18 C3 interval run.

The executable science is in interval_jet/run_evaluations/assemble_certificate;
this suite verifies the stored output without replaying heavy source evaluation.
"""
import json, unittest
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parents[1]
class C3Contracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((ROOT/'results/CERTIFICATE.json').read_text())
  cls.t=json.loads((ROOT/'results/TWO_CELL_VALIDATION.json').read_text())
  cls.n=json.loads((ROOT/'results/SECOND_ENDPOINT_MEMORY.json').read_text())
 def test_two_cell_interval(self):
  self.assertEqual(self.c['cell_s'],['6250000000','12500000000'])
  self.assertEqual(self.n['source_interval_s'],self.c['cell_s'])
  a,b=map(Q,self.t['two_cell_tau_interval_exact']);self.assertTrue(Q(0)<a<b<Q(1))
 def test_positive_gain_and_domain(self):
  self.assertLess(Q(self.c['gain']['rational']),Q(1,100))
  self.assertLess(Q(self.t['max_reference_plus_error_gas_box_fraction']),Q(1,10))
  self.assertEqual(self.c['transparent_count'],784)
 def test_real_nonzero_2904_photon_carry(self):
  self.assertEqual(len(self.n['outgoing_photon_error_end_raw_exact']),2904)
  self.assertEqual(self.n['nonzero_count'],2904)
  self.assertGreater(Q(self.n['error_sum_incoming']),0)
 def test_adjacent_clock_and_radiation(self):
  tau_first=Q(self.t['two_cell_tau_interval_exact'][0])-Q(self.c['true_depth_interval'][0]);self.assertGreater(tau_first,0)
  self.assertEqual(self.t['checks']['adjacent_clock_segments'],True)
  self.assertTrue(self.t['checks']['all_2904_incoming_photon_components_included'])
 def test_missing_physical_claim_stays_missing(self):
  self.assertIsNone(self.t['actual_cosmological_observer_foreground'])
  self.assertIsNone(self.n['provider_roundoff_budget'])
  self.assertFalse(self.t['all_16_cells_certified'])
if __name__=='__main__':unittest.main()
