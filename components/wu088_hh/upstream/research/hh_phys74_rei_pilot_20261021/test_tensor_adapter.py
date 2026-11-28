import unittest,numpy as np
from tensor_adapter import tensor_norms,lrs_tensors
class TensorTests(unittest.TestCase):
 def test_representation_factor_and_rotation(self):
  s,p=lrs_tensors(np.array([.2,-.1]),np.array([[1.,-.5],[.1,.2]]),stress_representation='delta_p')
  a=tensor_norms(np.array([2.,3.]),s,p,kappa_time=7.)
  q,_=np.linalg.qr(np.array([[1.,2.,3.],[-3.,1.,2.],[2.,-1.,3.]]))
  b=tensor_norms(np.array([2.,3.]),q@s@q.T,q@p@q.T,kappa_time=7.)
  for k in ('Sigma_F','Pi_F','work'):np.testing.assert_allclose(a[k],b[k],rtol=2e-15,atol=1e-16)
  np.testing.assert_allclose(a['Pi_F'],7*np.sqrt(6)*np.array([.5,.3])/3/np.array([4.,9.]))
 def test_cancellation_and_reject_missing_convention(self):
  s,p=lrs_tensors(.2,[1.,-1.],stress_representation='pi_s')
  a=tensor_norms(2.,s,p,kappa_time=7.)
  self.assertEqual(a['Pi_F'],0);self.assertFalse(a['alignment_defined'])
  with self.assertRaises(ValueError):lrs_tensors(.1,[1.],stress_representation='guess')
  with self.assertRaises(ValueError):tensor_norms(2.,np.eye(3),p,kappa_time=7.)
if __name__=='__main__':unittest.main()
