import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from implicit_thermal_moment import native_conditional_response
class Tests(unittest.TestCase):
 def test_linear_sign(self):
  low,hi=native_conditional_response(np.array([2.,4.]),np.array([4.,8.]),np.array([[-8.,0.,-2.],[0.,-4.,0.]]),2.)
  np.testing.assert_allclose(low[0],[-8.,0.,-2.],atol=1e-14)
  np.testing.assert_allclose(hi[0],[-4.,0.,-1.],atol=1e-14)
 def test_zeros_preserved(self):
  lo,hi=native_conditional_response(np.array([3.]),np.array([5.]),np.array([[0.,0.,0.]]),.5)
  self.assertTrue(np.all(lo==0.) and np.all(hi==0.))
 def test_positivity_guard(self):
  with self.assertRaises(ValueError):native_conditional_response(np.array([-1.]),np.array([2.]),np.zeros((1,3)),.5)
 def test_negative_dt(self):
  with self.assertRaises(ValueError):native_conditional_response(np.array([1.]),np.array([2.]),np.zeros((1,3)),-.5)
 def test_random_point_member(self):
  rng=np.random.default_rng(19)
  A=rng.uniform(.1,10,1000);B=A+rng.uniform(0,1,1000)
  P=-rng.uniform(0,2,(1000,3))
  l,h=native_conditional_response(A,B,P,.33)
  actual=.33*P/rng.uniform(A,B)[:,None]
  self.assertTrue(np.all(l<=actual))
  self.assertTrue(np.all(actual<=h))
 def test_shape(self):
  with self.assertRaises(ValueError):native_conditional_response(np.array([1.,2.]),np.array([2.,3.]),np.ones((2,2)),1.)
 def test_example_implicit_derivative(self):
  # F(z,Q)=a exp(z)-U-h*w*(Q - lambda z), derivative formula.
  a,U,h,w,lam=2.,3.,.1,.4,.2
  z=.3; Q=(a*math.exp(z)-U)/ (h*w)+lam*z
  d=a*math.exp(z)+h*w*lam
  calc=h*w/d
  for eps in (1e-4,1e-5):
   f=lambda x: a*math.exp(x)-U-h*w*(Q+eps-lam*x)
   x=z+eps*calc
   for _ in range(5):x-=f(x)/(a*math.exp(x)+h*w*lam)
   self.assertAlmostEqual((x-z)/eps,calc,delta=1e-5)
if __name__=="__main__":unittest.main()
