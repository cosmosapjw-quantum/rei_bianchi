import sys,unittest,math
from pathlib import Path
from decimal import Decimal,localcontext
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from finite_source_remainder import D,algebraic_remainder,majorant,parent_sample,outward_positive
class TestSourceRemainder(unittest.TestCase):
 def test_exact_finite_source_identity(self):
  with localcontext() as ctx:
   ctx.prec=90
   for x in (D(.3),D(2),D(5.)):
    for v in (D(-.2),D(.1),D(.45)):
     for d in (D(-.1),D(.03)):
      lhs=(x+d)/(1+v)-x-(d-x*v)
      self.assertLess(abs(lhs-algebraic_remainder(x,d,v,D(1))),D("1e-80"))
 def test_uniform_bound_random(self):
  r=np.random.default_rng(4)
  with localcontext() as ctx:
   ctx.prec=90
   for _ in range(100):
    x=D(r.uniform(1,5));dx=D(r.uniform(-.01,.01))
    vm=D(-.02);vp=D(.03);v=D(r.uniform(-.02,.03))
    self.assertLessEqual(abs(algebraic_remainder(x,dx,v,D(1))),
        majorant(D(1),x,D(.011),max(abs(vm),abs(vp)),D(.98)))
 def test_zero_photon_channel(self):
  self.assertEqual(algebraic_remainder(D(1),D(.5),D(.2),D(0)),0)
 def test_denominator_guard(self):
  with self.assertRaises(ValueError):algebraic_remainder(D(1),D(1),D(-1),D(1))
 def test_outward_positive(self):
  a=D('0.10000000000000000000000000000000001')
  self.assertGreater(D(outward_positive(a)),a)
 def test_parent_conservation_and_hull(self):
  baseline=np.tile([2.,3.,4.,5.,6.],(46080,1))
  lower=baseline-.1;upper=baseline+.1
  sample=parent_sample(baseline,lower,upper,baseline)
  self.assertTrue(np.all(sample>=lower-1e-13))
  self.assertTrue(np.all(sample<=upper+1e-13))
  np.testing.assert_allclose(sample[:,0]+sample[:,1],baseline[:,0]+baseline[:,1])
  np.testing.assert_allclose(sample[:,2:].sum(axis=1),baseline[:,2:].sum(axis=1))
if __name__=="__main__":unittest.main()
