from __future__ import annotations
import hashlib,math,shutil,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import build_fastd_angular as m
ROOT=Path(__file__).resolve().parents[1]
class ScienceAndProvenanceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=m.build(ROOT)
 def test_source_exact_sha256_git_blobs(self):
  for k in m.SOURCE:self.assertTrue(m.checked_source(ROOT,k).startswith(b'ENTRY'))
 def test_tampered_source_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'sources').mkdir()
   for k in m.SOURCE:shutil.copy(ROOT/'sources'/f'{k}.x4',p/'sources')
   q=p/'sources'/'M0826.x4';q.write_bytes(q.read_bytes().replace(b'    30.        50.',b'    31.        50.',1))
   with self.assertRaises(ValueError):m.source_angular(p)
 def test_source_count_and_Esupport(self):
  self.assertEqual(len(self.d['angular_bins']),9)
  self.assertEqual(self.d['authority']['source_gamma_energy_support_MeV'],[30,50])
 def test_source_is_not_9_monochromatic_experiments(self):
  self.assertEqual(self.d['data_grain']['new_original_experiments'],0)
  self.assertTrue(all(not r['energy_is_source_reported_monochromatic'] for r in self.d['derived_pair_bin_atlas']))
 def test_source_units_and_reaction(self):
  rows=m.source_angular(ROOT)
  self.assertEqual(rows[4],[80.,100.,.338,.1])
 def test_4pi_source_integral_reproduces_pr122(self):
  self.assertAlmostEqual(self.d['normalized_angular_moments']['4pi_DA_reported_muB'],5.430601681837213,places=12)
 def test_angular_probability_closes(self):
  self.assertAlmostEqual(sum(x['nominal_P_bin_conditioned_on_DA_bin_mean'] for x in self.d['angular_bins']),1.0,places=14)
 def test_sharp_moment_bounds_order(self):
  x=self.d['normalized_angular_moments']
  self.assertLessEqual(x['mu2_ERR_S_cartesian_min'],x['mu2_nominal_low'])
  self.assertLessEqual(x['mu2_nominal_low'],x['mu2_flat_in_bin_reference'])
  self.assertLessEqual(x['mu2_flat_in_bin_reference'],x['mu2_nominal_high'])
  self.assertLessEqual(x['mu2_nominal_high'],x['mu2_ERR_S_cartesian_max'])
  self.assertLessEqual(x['mu2_ERR_S_cartesian_max'],1.0)
 def test_threshold_exact_parent(self):
  x=m.pair_kinematics(30)
  self.assertAlmostEqual(x['Q_MeV'],23.8464782,places=9)
  self.assertAlmostEqual(x['threshold_Egamma_MeV'],23.922758940396704,places=10)
 def test_below_threshold_fails(self):
  with self.assertRaises(ValueError):m.pair_kinematics(20)
 def test_daughter_four_vector_boost_mass_shell(self):
  for E in m.REFERENCE_E_MEV:
   k=m.pair_kinematics(E); q=k['q_cm_times_c_MeV']; s=k['s_MeV2']
   self.assertAlmostEqual(q*q+m.M_D_MEV*m.M_D_MEV,s/4,places=7)
   self.assertAlmostEqual(k['daughter_K_min_MeV']+k['daughter_K_max_MeV'],E-k['Q_MeV'],places=11)
 def test_pair_energy_conservation_across_all_rows(self):
  self.assertEqual(len(self.d['derived_pair_bin_atlas']),27)
  for row in self.d['derived_pair_bin_atlas']:
   lo,hi=row['one_daughter_K_support_MeV']
   plo,phi=row['partner_daughter_K_support_MeV']
   self.assertLessEqual(lo,hi);self.assertLessEqual(plo,phi)
   self.assertAlmostEqual(lo+phi,row['paired_kinetic_sum_MeV'],places=11)
   self.assertAlmostEqual(hi+plo,row['paired_kinetic_sum_MeV'],places=11)
 def test_energy_variance_increases_with_E(self):
  ks=self.d['reference_energy_evaluations']
  self.assertTrue(all(ks[i]['daughter_kinetic_variance_MeV2_bin_shape_max']<ks[i+1]['daughter_kinetic_variance_MeV2_bin_shape_max'] for i in range(2)))
 def test_all_typed_missing_rates_stay_null(self):
  p=self.d['production'];self.assertIsNone(p['R_event']);self.assertIsNone(p['heat_rate']);self.assertIsNone(p['kappa']);self.assertIsNone(p['D_fast_pool']);self.assertFalse(p['L4'])
 def test_DAG_not_inflated(self):
  self.assertEqual(self.d['DAG'],{'central':'28/88','HE_physical':'14/18','new_source_scoped':'2/2','physical_delta':0})
 def test_error_extrema_covers_reference_and_empty_zero(self):
  bins=self.d['angular_bins'];lo,hi=m.source_error_box_extrema(bins)
  self.assertGreaterEqual(lo,0);self.assertLessEqual(hi,1)
  self.assertGreaterEqual(hi,lo)
 if __name__=='__main__':unittest.main()
