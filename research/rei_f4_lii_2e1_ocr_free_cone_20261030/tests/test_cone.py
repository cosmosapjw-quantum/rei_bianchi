import hashlib,importlib.util,pathlib,unittest
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cone',ROOT/'code/positive_cone.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ConePhysicsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r,cls.g,cls.b,cls.s,cls.a=m.calculate(8)
 def test_original_exact_source_identity(self):
  self.assertEqual(m.sha(m.UPSTREAM),m.SHA_PR284)
 def test_reject_modified_source(self):
  s=m.SHA_PR284
  try:
   m.SHA_PR284='0'*64
   with self.assertRaisesRegex(ValueError,'PR284_SOURCE_ZIP_SHA'):m.parent()
  finally:m.SHA_PR284=s
 def test_rows_and_native_gas(self):
  self.assertEqual((len(self.r),len(self.g),len(self.b)),(193,193*25,193*40))
 def test_parent_reconstruction(self):
  self.assertLess(self.s['audit']['numerically_checked_reconstruction_max_error'],1e-13)
 def test_probability_normalization_both_cones(self):
  for a in (self.a['positive'],self.a['monotone']):
   self.assertLess(np.max(abs(a.sum(axis=(2,3))-1)),1e-13)
   self.assertGreater(a.min(),-1e-14)
 def test_original_within_every_channel_bounds(self):
  for a in (self.a['positive'],self.a['monotone']):
   self.assertTrue(np.all(self.a['parent']>=a.min(axis=0)-4e-13))
   self.assertTrue(np.all(self.a['parent']<=a.max(axis=0)+4e-13))
 def test_monotone_is_subset_of_positive_for_all_linear_probabilities(self):
  a=self.a['positive'];b=self.a['monotone']
  self.assertTrue(np.all(b.min(axis=0)>=a.min(axis=0)-1e-13))
  self.assertTrue(np.all(b.max(axis=0)<=a.max(axis=0)+1e-13))
 def test_ocr_uncontrolled_hat_violates_monotone_bound(self):
  # Explicit adversarial counterexample: a1>0, other a_i=0 is positive but NOT monotone.
  j=self.a['positive'][0,0,1:,1:].sum()
  lo=self.a['monotone'][:,0,1:,1:].sum(axis=(1,2)).min()
  self.assertLess(j,lo-0.1)
 def test_HeII_low_energy_impossible(self):
  j=m.CATS.index('He_II')
  self.assertLess(np.max(abs(self.a['positive'][:,:,j,:])),1e-15)
  self.assertLess(np.max(abs(self.a['monotone'][:,:,j,:])),1e-15)
 def test_global_shape_is_shared_not_epoch_adaptive(self):
  # Source owner generates the same monotone source across all 193 saved epochs.
  g=self.s['integrated_conditional_source_bounds']['monotone']['P2']
  old=self.s['parent_source_integrated']['two_absorbed']
  self.assertLess(g['min'],old)
  self.assertGreater(g['max'],old)
  self.assertGreater(g['min'],0)
 def test_parent_endpoints(self):
  self.assertAlmostEqual(self.r[-1]['PR284_P2'],.001115920147001298,places=14)
  self.assertTrue(self.r[-1]['monotone_P2_min']<self.r[-1]['PR284_P2']<self.r[-1]['monotone_P2_max'])
 def test_no_promotions_and_no_ivp(self):
  self.assertEqual(self.s['DAG']['working'],'33/88');self.assertEqual(self.s['DAG']['central'],'28/88')
  self.assertEqual(self.s['DAG']['canonical_delta'],0)
  self.assertEqual(self.s['science']['new_IVPs'],0)
  txt=(ROOT/'code/positive_cone.py').read_text()
  self.assertNotIn('solve_ivp(',txt);self.assertNotIn('odeint(',txt)
 def test_quadrature_8_vs_16(self):
  rows,*_=m.calculate(16)
  keys=['positive_P2_max','monotone_P2_min','monotone_P2_max','monotone_N_min','monotone_N_max']
  d=max(abs(self.r[i][k]-rows[i][k]) for i in range(len(rows)) for k in keys)
  self.assertLess(d,2e-13)
 def test_source_scan_not_falsely_verified(self):
  self.assertEqual(self.s['audit']['source_1969_pdf_visual'],'NOT_VERIFIED')
  self.assertEqual(self.s['audit']['independent_author_R6_C9'],'NOT_RUN')

if __name__=='__main__':unittest.main()
