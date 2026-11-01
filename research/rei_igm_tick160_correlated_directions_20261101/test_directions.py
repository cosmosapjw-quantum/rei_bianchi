import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace
import numpy as np
p=Path(__file__).with_name('directional_probe.py')
spec=importlib.util.spec_from_file_location('directional_probe',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  # 4 physical nodes, all elements conserved; nonzero feasible uncertainties.
  self.h=np.full(4,1.)
  self.he=np.full(4,.079)
  self.mid=np.tile(np.array([.02,.98,.001,.075,.003]),(4,1))
  self.lo=self.mid-np.array([.0001,.0001,.00004,.00004,.00004])
  self.hi=self.mid+np.array([.0001,.0001,.00004,.00004,.00004])
  self.tlo=np.log(np.full(4,5000.))
  self.thi=np.log(np.full(4,5500.))
 def test_all_nine_candidates_conserve_and_contain(self):
  for c in m.CASES:
   p,t=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,c)
   self.assertTrue((p>0).all())
   self.assertTrue((p>=self.lo-1e-13).all())
   self.assertTrue((p<=self.hi+1e-13).all())
   np.testing.assert_allclose(p[:,:2].sum(axis=1),self.h,atol=1e-14)
   np.testing.assert_allclose(p[:,2:5].sum(axis=1),self.he,atol=1e-14)
   self.assertTrue((t>=self.tlo).all() and (t<=self.thi).all())
 def test_density_scaled_nuclei_preserved(self):
  scale=1e9
  for case in m.CASES:
   p,t=m.candidate(self.lo*scale,self.hi*scale,self.tlo,self.thi,self.h*scale,self.he*scale,case)
   np.testing.assert_allclose(p[:,0]+p[:,1],self.h*scale,rtol=3e-15,atol=3e-15)
   np.testing.assert_allclose(np.sum(p[:,2:5],axis=1),self.he*scale,rtol=3e-15,atol=3e-15)
 def test_thermal_variation_is_nontrivial(self):
  _,tm=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'logT_minus')
  _,tp=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'logT_plus')
  self.assertTrue((tp>tm).all())
 def test_hii_bounds_distinct(self):
  p0,_=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'HII_minus')
  p1,_=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'HII_plus')
  self.assertTrue((p1[:,1]>p0[:,1]).all())
 def test_hei_bounds_distinct(self):
  p0,_=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'HeII_minus')
  p1,_=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'HeII_plus')
  self.assertTrue((p1[:,3]>p0[:,3]).all())
 def test_heiii_bounds_distinct(self):
  p0,_=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'HeIII_minus')
  p1,_=m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'HeIII_plus')
  self.assertTrue((p1[:,4]>p0[:,4]).all())
 def test_invalid_conservation_reject(self):
  with self.assertRaises(ValueError):
   m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he*2,'center')
 def test_bad_case_reject(self):
  with self.assertRaises(ValueError):m.candidate(self.lo,self.hi,self.tlo,self.thi,self.h,self.he,'forged')
 def test_interval_difference_null_width(self):
  lo=np.array([1.,2.]);hi=lo.copy()
  a,b,u,c=m.difference_bounds((lo,hi),(lo,hi))
  self.assertLess(np.max(u),1e-14)
 def test_interval_difference_nonzero_same_box(self):
  a,b,u,c=m.difference_bounds((np.array([0.]),np.array([1.])),(np.array([0.]),np.array([1.])))
  self.assertGreater(u[0],.999999)
  self.assertAlmostEqual(float(c[0]),0.)
 def test_scope_enforced(self):
  self.assertEqual(len(m.CASES),9)
  self.assertEqual(m.STRESS_FRACTION,.8)
if __name__=='__main__':unittest.main()
