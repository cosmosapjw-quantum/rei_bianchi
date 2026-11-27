import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import build_reconciliation as m

ROOT=Path(__file__).resolve().parents[1]
class TestRice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.v=m.build(ROOT)
    def test_source_git_identity_final(self): self.assertEqual(m.git_blob(ROOT/'inputs/RICE2000_TABLE_I_AUTHORITATIVE_PR126.json'),m.PUBLISHED_SOURCE_GIT_BLOB)
    def test_source_git_identity_prelim_low(self): self.assertEqual(m.git_blob(ROOT/'inputs/RICE1998_TABLE_5_1_PRELIMINARY_PR125.json'),m.PRELIMINARY_LOW_GIT_BLOB)
    def test_image_source_identity(self): self.assertEqual(self.v['source_table_1998_52_image_sha256'],'103022f4d890519ee9273e8ddc5d7a632a93ada30ab4a5259216f600b2e10de2')
    def test_one_campaign(self): self.assertEqual(self.v['independent_experimental_campaigns'],1)
    def test_12_matched_rows(self): self.assertEqual(len(self.v['rows']),12)
    def test_1998_table_52_exact_6(self): self.assertEqual([r['prelim_1998_DA_nb_sr'] for r in self.v['rows'][6:]],[.118,.486,1.17,.921,.566,.594])
    def test_1998_table_52_yields_exact_6(self): self.assertEqual([r['thesis_yield'] for r in self.v['rows'][6:]],[249,951,1977,1394,771,735])
    def test_1998_table_52_errors_exact_6(self): self.assertEqual([r['prelim_1998_stat_nb_sr'] for r in self.v['rows'][6:]],[.091,.122,.144,.131,.097,.107])
    def test_reflected_angles_unique(self):
        self.assertEqual([r['theta_cm_reflected_deg'] for r in self.v['rows'][6:]],[134.6,116.4,88.6,71.6,55.6,40.3]);self.assertEqual(len(self.v['rows']),12)
    def test_final_2000_high(self):self.assertEqual([r['published_2000_DA_nb_sr'] for r in self.v['rows'][6:]],[.14,.59,1.42,1.11,.68,.43])
    def test_last_ratio(self): self.assertAlmostEqual(self.v['last_high_angle_ratio'],.43/.594,places=13)
    def test_11_ratio_range(self): self.assertTrue(1.18<self.v['empirical_ratio_first_11_min_max'][0] and self.v['empirical_ratio_first_11_min_max'][1]<1.22)
    def test_rounding_robust_disjoint(self): self.assertLess(self.v['last_high_angle_ratio_printing_only_bounds'][1],self.v['first_high_angle_ratio_printing_only_lower_bound'])
    def test_fractional_yield_error_propagation(self): self.assertLess(self.v['max_fractional_stat_sd_ratio_difference_high_bin'],.0012)
    def test_energy_birth_support_exact(self):
        r=self.v['rows'][-1];self.assertAlmostEqual(r['prelim_pair_birth_energy_weighted_DA_interval_nb_MeV_sr'][0],.594*(190-m.Q),places=11)
    def test_R_event_unfilled(self): self.assertIsNone(self.v['R_event']);self.assertIsNone(self.v['heat_rate']);self.assertFalse(self.v['L4'])
    def test_new_source_not_independent(self): self.assertTrue(all(not r['probabilistic_independence_asserted'] for r in self.v['rows']))
    def test_multiplicity(self):self.assertTrue(all(r['daughter_multiplicity_per_dd_event']==2 for r in self.v['rows']))
    def test_central_unchanged(self): self.assertEqual(self.v['central_DAG'],'28/88');self.assertEqual(self.v['HE_physical_DAG'],'14/18')
if __name__=='__main__':unittest.main()
