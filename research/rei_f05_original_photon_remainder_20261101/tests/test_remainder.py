import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[1]/"source_remainder.py"
s=importlib.util.spec_from_file_location("testable_26_event_photon_remainder",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

class PhotonSourceTests(unittest.TestCase):
 def test_exact_finite_identity(self):
  for u in (-.99,-.2,0,.4,3):
   for r in (-.8,-.1,0,.2,2.):
    actual,linear,remainder=m.quotient_remainder(u,r)
    self.assertAlmostEqual(actual,linear+remainder,delta=3e-14*max(1,abs(actual)))
 def test_supremum_includes_independent_rectangle_grid(self):
  rng=np.random.default_rng(20261101)
  for _ in range(40):
   ulo=float(rng.uniform(-.9,-.02));uhi=float(rng.uniform(.01,3.))
   rlo=float(rng.uniform(-.9,-.01));rhi=float(rng.uniform(.01,2.))
   upper=float(m.max_quotient_remainder_factor(np.array([ulo]),np.array([uhi]),rlo,rhi)[0])
   rr=np.linspace(rlo,rhi,150)
   lower=max(float(np.max(np.abs(rr*(u-rr)/(1+rr)))) for u in (ulo,uhi))
   self.assertGreaterEqual(upper+1e-12,lower)
 def test_zero_photon_source_delta(self):
  out=m.max_quotient_remainder_factor(np.array([-0.2,0.]),np.array([0.3,0.]),0.,0.)
  np.testing.assert_array_equal(out,np.zeros(2))
 def test_internal_stationary_point_needed(self):
  u=np.array([3.])
  v=m.max_quotient_remainder_factor(u,u,0.,2.)[0]
  self.assertAlmostEqual(v,1.,delta=1e-14)
 def test_denominator_vanishes_fail_closed(self):
  with self.assertRaises(ValueError):
   m.max_quotient_remainder_factor(np.array([0.]),np.array([1.]),-1.,0.5)
 def test_marginal_box_nonphysical_rejected(self):
  with self.assertRaises(ValueError):
   m.max_quotient_remainder_factor(np.array([-2.]),np.array([0.]),-.1,.1)
 def test_source_owner_geometry(self):
  self.assertEqual(m.N,46080)
  self.assertEqual(m.COLUMNS,(0,2,3))
  self.assertEqual(len(m.SPECIES),3)
 def test_group_wrong_input_count_fails(self):
  with self.assertRaises(ValueError):
   m.group_from_source(None,np.zeros((4,5)),np.zeros((4,5)),np.zeros((4,5)),np.zeros(3),1.,1.)
if __name__=="__main__":unittest.main()
