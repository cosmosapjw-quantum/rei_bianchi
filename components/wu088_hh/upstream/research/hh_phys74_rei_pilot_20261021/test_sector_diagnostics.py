"""Sector tests use direct tensor contractions, not the owner's ODE solver."""
import unittest
import numpy as np
from sector_diagnostics import sector_tensor_norms, lrs_sector_norms

class SectorTests(unittest.TestCase):
    def test_nonzero_cancelled_sectors_are_not_lost(self):
        s=np.diag([-.2,-.2,.4]);m=np.diag([-1.,-1.,2.]);r=-m
        q=sector_tensor_norms(2.,s,m,r,kappa_time=7.)
        self.assertIn('Pi_m_F',q,'total-only output loses nonzero cancelling sectors')
        self.assertIn('Pi_r_F',q)
        self.assertAlmostEqual(q['Pi_m_F'],7*np.sqrt(6)/4)
        self.assertAlmostEqual(q['Pi_r_F'],q['Pi_m_F'])
        self.assertEqual(q['Pi_total_F'],0.)
        self.assertAlmostEqual(q['work_m'],-q['work_r'])
        self.assertAlmostEqual(q['mr_alignment'],-1.)
    def test_general_stf_rotation_and_cross_term(self):
        s=np.array([[.2,.1,0],[.1,-.3,.05],[0,.05,.1]])
        m=np.diag([1.,-1.,0.]);r=np.array([[0,2.,0],[2.,0,0],[0,0,0.]])
        q=sector_tensor_norms(3.,s,m,r,kappa_time=2.)
        self.assertAlmostEqual(q['Pi_total_F']**2,q['Pi_m_F']**2+q['Pi_r_F']**2+q['mr_cross'])
        self.assertAlmostEqual(q['work_m'],2*np.sum(s*m)/27.)
        self.assertAlmostEqual(q['work_r'],2*np.sum(s*r)/27.)
        self.assertAlmostEqual(q['work_total'],q['work_m']+q['work_r'])
        R,_=np.linalg.qr(np.array([[1.,2.,3.],[-3.,1.,2.],[2.,-1.,3.]]))
        qq=sector_tensor_norms(3.,R@s@R.T,R@m@R.T,R@r@R.T,kappa_time=2.)
        for key in ('Sigma_F','Pi_m_F','Pi_r_F','Pi_total_F','work_m','work_r','work_total'):
            np.testing.assert_allclose(q[key],qq[key],rtol=3e-15,atol=1e-16)
    def test_zero_norm_alignment_is_undefined(self):
        q=sector_tensor_norms(1.,np.zeros((3,3)),np.zeros((3,3)),np.diag([1.,-1.,0.]),kappa_time=1.)
        self.assertFalse(q['mr_alignment_defined']);self.assertTrue(np.isnan(q['mr_alignment']))
        self.assertFalse(q['shear_m_alignment_defined']);self.assertFalse(q['shear_r_alignment_defined'])
        self.assertEqual(q['work_total'],0.)
    def test_lrs_signed_batch_and_half_norm(self):
        h=np.array([2.,3.]);s=np.array([.2,-.1]);m=np.array([.01,.02]);r=np.array([-.02,.04])
        q=lrs_sector_norms(h,s,m,r,kappa_time=7.)
        np.testing.assert_allclose(q['Pi_m_signed'],7*np.sqrt(6)*m/h**2,rtol=2e-15)
        np.testing.assert_allclose(q['Pi_r_signed'],7*np.sqrt(6)*r/h**2,rtol=2e-15)
        np.testing.assert_allclose(q['Pi_total_signed'],q['Pi_m_signed']+q['Pi_r_signed'],rtol=2e-15)
        np.testing.assert_allclose(q['work_m'],6*7*s*m/h**3,rtol=2e-15)
        np.testing.assert_allclose(q['Pi_m_half']*np.sqrt(2),q['Pi_m_F'],rtol=2e-15)
    def test_invalid_shape_nonfinite_trace_or_H_rejected(self):
        z=np.zeros((3,3));m=np.diag([1.,-1.,0.])
        for h,s,a,b,k in [(0,z,m,m,1),(1,z,m,np.full((3,3),np.nan),1),(1,z,m,np.eye(3),1),(1,z,m,m,-1),(1,z,m,np.zeros((2,3,3)),1)]:
            with self.assertRaises(ValueError):sector_tensor_norms(h,s,a,b,kappa_time=k)
    def test_zero_radiation_does_not_erase_matter(self):
        q=lrs_sector_norms(1.,.2,1.,0.,kappa_time=1.)
        self.assertGreater(q['Pi_m_F'],0);self.assertEqual(q['Pi_r_F'],0)
        self.assertEqual(q['Pi_total_F'],q['Pi_m_F'])
    def test_matter_radiation_exchange_only_swaps_labels(self):
        a=lrs_sector_norms(2.,-.1,.02,-.07,kappa_time=7.)
        b=lrs_sector_norms(2.,-.1,-.07,.02,kappa_time=7.)
        for k in ('Pi','work'):
            suffix='_F' if k=='Pi' else ''
            self.assertEqual(a[k+'_m'+suffix],b[k+'_r'+suffix])
        self.assertEqual(a['Pi_total_F'],b['Pi_total_F'])

if __name__=='__main__':unittest.main()
