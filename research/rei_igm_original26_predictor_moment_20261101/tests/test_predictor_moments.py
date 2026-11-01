"""Falsification tests for exact original MPRK22 predictor shared-source derivatives.

Synthetic positive PDS / 5-species H-He blocks. Real frozen original source
is separately required in the GitHub Actions physics job; no simulated PASS.
"""
import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parents[1]/"predictor_moments.py"
sp=importlib.util.spec_from_file_location("rei_pred_source_test",P)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)

class Predictor(unittest.TestCase):
    def setUp(self):
        self.parent=np.array([
          [0.6,0.4,0.22,0.31,0.47],
          [0.35,0.65,0.49,0.30,0.21]],float)
        self.n=2
        self.dt=.3
        self.group_rates=np.zeros((4,2,3))
        self.group_rates[0,:,0]=[.03,.02]
        self.group_rates[1,:,1]=[.07,.04]
        self.group_rates[2,:,0]=[.13,.07]
        self.group_rates[2,:,1]=[.03,.05]
        self.group_rates[3,:,2]=[.01,.02]
        self.group_shares=np.array([[.2,.1,.0],[.0,.25,.0],[.4,.3,.0],[.1,.1,.5]])
        A=np.tile(np.eye(5),(2,1,1))
        for s,(src,dest) in enumerate(zip(m.SRC_INDICES,m.DEST_INDICES)):
            d=self.dt*self.group_rates[:,:,s].sum(axis=0)/self.parent[:,src]
            A[:,src,src]+=d
            A[:,dest,src]-=d
        self.A=A
    def test_group_derivative_analytical(self):
        first,second=m.photo_moment_derivatives(self.group_rates,self.group_shares)
        self.assertEqual(first.shape,(2,3,3))
        self.assertEqual(second.shape,(2,3,3,3))
        self.assertLess(np.max(np.abs(second-second.transpose(0,1,3,2))),1e-15)
    def test_exact_finite_jac(self):
        b,J,H=m.implicit_predictor_derivatives(self.A,self.parent,self.group_rates,self.group_shares,self.dt)
        eps=2e-4
        for k in range(3):
            d=np.zeros(3);d[k]=eps
            v1=m.batch_solve(m.finite_source_matrix(self.A,self.parent,self.group_rates,self.group_shares,self.dt,d),self.parent)
            v2=m.batch_solve(m.finite_source_matrix(self.A,self.parent,self.group_rates,self.group_shares,self.dt,-d),self.parent)
            np.testing.assert_allclose((v1-v2)/(2*eps),J[:,k,:],rtol=1e-6,atol=1e-9)
    def test_exact_finite_hessian(self):
        b,J,H=m.implicit_predictor_derivatives(self.A,self.parent,self.group_rates,self.group_shares,self.dt)
        eps=.004
        for k,l in ((0,0),(0,1),(1,2),(2,2)):
            v=np.zeros(3);v[k]+=eps;v[l]+=eps
            w=np.zeros(3);w[k]-=eps;w[l]-=eps
            f=lambda d:m.batch_solve(m.finite_source_matrix(self.A,self.parent,self.group_rates,self.group_shares,self.dt,d),self.parent)
            exact=f(v)-b-np.einsum("nks,k->ns",J,v)
            quad=.5*np.einsum("nkls,k,l->ns",H,v,v)
            self.assertLess(np.max(abs(exact-quad)),1.5e-6)
    def test_nuclear_conservation(self):
        b,J,H=m.implicit_predictor_derivatives(self.A,self.parent,self.group_rates,self.group_shares,self.dt)
        for sl in (slice(0,2),slice(2,5)):
            np.testing.assert_allclose(b[:,sl].sum(axis=1),self.parent[:,sl].sum(axis=1),rtol=1e-14)
            np.testing.assert_allclose(J[:,:,sl].sum(axis=-1),0,atol=5e-16)
            np.testing.assert_allclose(H[:,:,:,sl].sum(axis=-1),0,atol=5e-15)
    def test_positive_predictor(self):
        b,J,H=m.implicit_predictor_derivatives(self.A,self.parent,self.group_rates,self.group_shares,self.dt)
        self.assertTrue(np.all(b>0))
        v=m.batch_solve(m.finite_source_matrix(self.A,self.parent,self.group_rates,self.group_shares,self.dt,[0.4,-0.2,0.3]),self.parent)
        self.assertTrue(np.all(v>0))
    def test_second_order_smallness(self):
        b,J,H=m.implicit_predictor_derivatives(self.A,self.parent,self.group_rates,self.group_shares,self.dt)
        d=np.array([.13,-.08,.02])
        new=m.batch_solve(m.finite_source_matrix(self.A,self.parent,self.group_rates,self.group_shares,self.dt,d),self.parent)
        lin=np.einsum("nks,k->ns",J,d)
        quad=.5*np.einsum("nkls,k,l->ns",H,d,d)
        self.assertLess(np.max(abs(new-b-lin-quad)),1e-4)
    def test_empty_photon_group(self):
        rates=self.group_rates.copy();rates[:]=0
        A=np.tile(np.eye(5),(2,1,1))
        b,J,H=m.implicit_predictor_derivatives(A,self.parent,rates,self.group_shares,self.dt)
        np.testing.assert_allclose(b,self.parent,rtol=1e-15)
        np.testing.assert_array_equal(J,np.zeros_like(J))
        np.testing.assert_array_equal(H,np.zeros_like(H))
    def test_no_invalid_parent(self):
        a=self.parent.copy();a[0,0]=0
        with self.assertRaises(ValueError):m.photo_matrix_derivatives(self.group_rates,self.group_shares,a,self.dt)
    def test_no_negative_source(self):
        r=self.group_rates.copy();r[0,0,0]=-1
        with self.assertRaises(ValueError):m.photo_moment_derivatives(r,self.group_shares)
    def test_schur_required_global_dimensions(self):
        self.assertEqual(len(m.SRC_INDICES),3)
        self.assertEqual(len(m.DEST_INDICES),3)
    def test_original_science_gates(self):
        self.assertEqual((m.STRICT_LOCAL_ERROR,m.STRICT_WIDTH),(0.0002,0.002))
        self.assertEqual(m.N,46080)
        self.assertEqual(len(m.STATE_SHA),64)
if __name__=="__main__":unittest.main(verbosity=2)
