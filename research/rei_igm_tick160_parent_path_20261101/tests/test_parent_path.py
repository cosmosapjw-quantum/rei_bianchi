import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import parent_path as m

class Interval:
 def __init__(self,lo,hi):self.lo=np.array(lo);self.hi=np.array(hi)

class Tests(unittest.TestCase):
 def test_endpoint(self):
  np.testing.assert_allclose(m.endpoint(.5,[1,3],[3,5]),[2,4])
  np.testing.assert_array_equal(m.endpoint(0,[1,3],[3,5]),[1,3])
  np.testing.assert_array_equal(m.endpoint(1,[1,3],[3,5]),[3,5])
 def test_bad_endpoint(self):
  for a in (-.01,1.01):
   with self.assertRaises(ValueError):m.endpoint(a,[0],[1])
 def test_reject_invalid_parent(self):
  with self.assertRaises(ValueError):m.endpoint(.5,[2],[1])
 def test_exact_equal_maps(self):
  r=m.interval_separation(Interval([1,2],[1,2]),Interval([1,2],[1,2]))
  np.testing.assert_array_equal(r['upper'],[0,0]);np.testing.assert_array_equal(r['lower'],[0,0])
 def test_equal_wide_boxes_have_spurious_upper(self):
  r=m.interval_separation(Interval([0],[1]),Interval([0],[1]))
  self.assertEqual(float(r['upper'][0]),1.)
  self.assertEqual(float(r['lower'][0]),0.)
 def test_strict_lower_positive_for_disjoint(self):
  r=m.interval_separation(Interval([2.],[2.5]),Interval([1.],[1.25]))
  self.assertAlmostEqual(float(r['lower'][0]),.75)
  self.assertAlmostEqual(float(r['upper'][0]),1.5)
 def test_phys_eos_identity(self):
  p=np.array([[3.,7.,10.,8.,2.]])
  r=m.source_coordinates(p,np.log([1e4]),np.array([10.]),np.array([20.]))
  self.assertAlmostEqual(float(r['xe'][0]),(7+8+4)/10)
  self.assertAlmostEqual(float(r['U_th_erg_per_H'][0]),1.5*m.KB_ERG_K*1e4*(1+2+1.9))
 def test_reject_zero_nuclei(self):
  with self.assertRaises(ValueError):m.ratio_safe(np.array([1.]),np.array([0.]))
 def test_locked_nonpromoting(self):
  self.assertEqual(m.GATE,2e-4);self.assertEqual(m.TICK,160)
  self.assertNotEqual(m.ORIGINAL_FAILURE,m.GATE)
  self.assertEqual(m.ALPHAS,(.05,.5,.95))
 def test_bad_interval(self):
  with self.assertRaises(ValueError):m.interval_separation(Interval([2],[1]),Interval([1],[2]))
 def test_source_rows_46080(self):
  with self.assertRaises(ValueError):m.quantiles([1,2,3])

if __name__=='__main__':unittest.main()
