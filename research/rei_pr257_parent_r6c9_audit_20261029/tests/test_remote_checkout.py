"""Clean-checkout PR257 compact geometry regression; no expensive IVPs."""
from pathlib import Path
import hashlib, itertools, json, sys, unittest
import numpy as np
from scipy.spatial import ConvexHull
HERE=Path(__file__).resolve()
UNIT=HERE.parents[1]
sys.path.insert(0, str(UNIT/'code'))
from compact_boundary import boundary
SOURCE=HERE.parents[3]/'research/rei_uvb_eos_jeans_box_20261029/source/FROZEN_BB13_SUPPORT_INPUT.json'
if not SOURCE.is_file(): SOURCE=UNIT/'source/FROZEN_BB13_SUPPORT_INPUT.json'
EXPECTED='13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b'
class TestSourceBound(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
  d=json.loads(SOURCE.read_text())
  cls.lo=np.array(d['jeans_smoothing_lower_dex']);cls.hi=np.array(d['jeans_smoothing_upper_dex'])
  z=np.array(d['z']);C=np.array(d['covariance_dex_squared']);X=np.column_stack((np.ones(7),z-3.6))
  L=np.linalg.cholesky(C);W=np.linalg.solve(L.T,np.linalg.solve(L,X))
  cls.A=np.linalg.solve(X.T@W,W.T)
  cls.r=np.array(d['observed_dex'])-np.array(d['template_dex'])
  cls.v=np.array(d['eos_response_dex'])
  cls.center=cls.A@(cls.r+(cls.lo+cls.hi)/2)
  cls.G=np.column_stack((cls.A@cls.v,cls.A*((cls.hi-cls.lo)/2)[None,:])).T
  cls.p=np.array(boundary(cls.center,cls.G))
  cls.allv=np.array([cls.A@(cls.r+t*cls.v+np.where(bits,cls.hi,cls.lo)) for t in [-1.,1.] for bits in itertools.product((0,1),repeat=7)])
 def test_ordered_boundary_vs_256(self):
  hull=self.allv[ConvexHull(self.allv).vertices]
  self.assertEqual(len(self.p),17)
  self.assertLess(max(min(np.linalg.norm(q-b) for b in hull) for q in self.p[:-1]),1e-14)
  self.assertLess(max(min(np.linalg.norm(q-b) for b in self.p[:-1]) for q in hull),1e-14)
 def test_source_expected_bounds(self):
  n=np.min(self.allv,axis=0);m=np.max(self.allv,axis=0)
  np.testing.assert_allclose(n,[-0.13087466565371772,0.053617504767915498],atol=2e-14,rtol=0)
  np.testing.assert_allclose(m,[0.051206812137275709,0.099225339666118351],atol=2e-14,rtol=0)
 def test_common_mode_and_gamma_sign(self):
  np.testing.assert_allclose(self.A@np.ones(7),[1,0],atol=1e-13,rtol=0)
  self.assertLess((self.A@self.v)[1],0) # theta +1 => BB13 gamma=1.6 reduces kappa
 def test_joint_rectangle_is_not_joint_set(self):
  m=np.max(self.allv,axis=0)
  self.assertLess(np.max(np.sum(self.allv,axis=1)),sum(m)-1e-4)
 def test_zero_generators_and_symmetric_sign(self):
  self.assertEqual(len(boundary((0,0),[(0,0),(1,0),(0,1)])),5)
  np.testing.assert_allclose(boundary((0,0),[(1,2),(-2,1)]),boundary((0,0),[(-1,-2),(2,-1)]),atol=0,rtol=0)
if __name__=='__main__': unittest.main()
