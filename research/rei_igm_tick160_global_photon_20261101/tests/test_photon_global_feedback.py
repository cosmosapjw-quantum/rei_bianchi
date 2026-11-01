import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from photon_global_feedback import shares,logmoment_jacobian,exact_interval_fraction,exact_fraction_line_integral,positive_outward_weight

class Physics(unittest.TestCase):
 def test_probability_with_external(self):
  p,e,_=shares([2,3,4],[.1,.1,.1],.1)
  self.assertAlmostEqual(float(np.sum(p)+e),1)
 def test_positivity(self):
  p,e,_=shares([2,3,4],[.1,.1,.1],.1)
  self.assertGreaterEqual(np.linalg.eigvalsh(logmoment_jacobian(p))[0],-1e-14)
 def test_determinant(self):
  p,e,_=shares([2,3,4],[.1,.1,.1],.1)
  self.assertAlmostEqual(np.linalg.det(logmoment_jacobian(p)),e*np.prod(p),delta=1e-14)
 def test_row_sum(self):
  p,e,_=shares([2,3,4],[.1,.1,.1],.1)
  np.testing.assert_allclose(logmoment_jacobian(p)@np.ones(3),e*p,rtol=1e-14,atol=1e-15)
 def test_zero_external(self):
  p,e,_=shares([2,3,4],[.1,.1,.1],0.)
  self.assertEqual(e,0)
  self.assertLess(abs(np.linalg.det(logmoment_jacobian(p))),1e-16)
 def test_log_jacobian_finite_difference(self):
  s=np.array([2.,3.,4.]);c=np.array([.1,.2,.3]);e=.15
  p,_,_=shares(s,c,e);j=logmoment_jacobian(p);h=1e-5
  for t in range(3):
   plus=s.copy();minus=s.copy();plus[t]*=math.exp(h);minus[t]*=math.exp(-h)
   pp,_,_=shares(plus,c,e);pm,_,_=shares(minus,c,e)
   np.testing.assert_allclose((pp-pm)/(2*h),j[:,t],rtol=2e-10,atol=2e-11)
 def test_source_path_conservation(self):
  e,d=exact_fraction_line_integral(np.array([2,3,4]),np.array([3,2,8]),np.array([.1,.4,.2]),.5)
  self.assertLess(e,2e-14)
 def test_monotone_interval_enclosure(self):
  lo,hi=exact_interval_fraction(np.array([1.,2.,3.]),np.array([2.,4.,6.]),1,3)
  for a in [[1,2,3],[1.5,3.1,4.5],[2,4,6]]:
   for e in (1,2,3):
    p,_,_=shares(a,[1,1,1],e)
    self.assertTrue(np.all(p>=lo-1e-15))
    self.assertTrue(np.all(p<=hi+1e-15))
 def test_structural_zero_source_weight(self):
  for upper in (False,True):
   a=positive_outward_weight(np.array([0.,1.,0.]),1.,np.array([2.,4.,7.]),upper)
   self.assertEqual(float(a[0]),0.)
   self.assertEqual(float(a[2]),0.)
   self.assertGreater(float(a[1]),0.)

 def test_source_decomposition(self):
  rng=np.random.default_rng(3);x=1+rng.random((9,3));s=x.sum(axis=0)
  j=np.array([10.,20.]);c=np.array([[.1,.2,.3],[.4,.3,.2]]);ex=np.array([.1,.2])
  flux=np.zeros_like(x);rem=np.zeros((9,3,3))
  for k in range(2):
   p,_,den=shares(s,c[k],ex[k]);f=x*j[k]*c[k]/den
   flux+=f;rem-=f[:,:,None]*p[None,None,:]
  # Exact nonlocal sensitivity factorization - not the local diagonal contribution.
  for target in range(3):
   eps=1e-5
   sp=s.copy();sm=s.copy();sp[target]*=math.exp(eps);sm[target]*=math.exp(-eps)
   fp=np.zeros_like(flux);fm=np.zeros_like(flux)
   for k in range(2):
    _,_,dp=shares(sp,c[k],ex[k]);_,_,dm=shares(sm,c[k],ex[k])
    fp+=x*j[k]*c[k]/dp;fm+=x*j[k]*c[k]/dm
   np.testing.assert_allclose((fp-fm)/(2*eps),rem[:,:,target],rtol=2e-10,atol=2e-11)
 def test_no_negative_source(self):
  with self.assertRaises(ValueError):shares([1,-1,1],[1,1,1],1)
 def test_no_zero_denominator(self):
  with self.assertRaises(ValueError):shares([0,0,0],[1,1,1],0)
 def test_wrong_shape(self):
  with self.assertRaises(ValueError):shares([1,2],[1,2,3],1)

if __name__=="__main__":unittest.main()
