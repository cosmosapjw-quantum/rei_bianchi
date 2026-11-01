"""Independent local residual enclosure tests for original H/He Patankar blocks."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import numpy as np

HERE=Path(__file__).resolve().parents[1]
P=HERE/"residual_certificate.py"
s=importlib.util.spec_from_file_location("rei_f05_mmatrix_test",P)
c=importlib.util.module_from_spec(s);sys.modules[s.name]=c;s.loader.exec_module(c)

class TestMassContraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=c.load_original()
        edge=cls.original.load("rei_f05_mmatrix_edge",c.BASE/"research/rei_igm_original26_temperature_edges_20261101/edge_probe.py")
        worker=cls.original.load("rei_f05_mmatrix_worker",c.BASE/edge.REL_STAGE/"analysis/attempt_worker.py")
        worker.jax_guard.install_if_missing()
        cls.m=worker._kernel()

    def case(self):
        n=5
        p=np.array([10.,1.,5.,2.,.5],dtype=float)[None,:]*np.linspace(.7,1.4,n)[:,None]
        r=np.zeros((n,5,5))
        for dest,source,v in ((1,0,.7),(0,1,.3),(3,2,.1),(4,3,.2),(3,4,.15),(2,3,.04)):
            r[:,dest,source]=v*np.linspace(.7,1.4,n)
        m=self.m
        return m._I(p),m._I(r),m._I(p),0.2,p,r

    def test_actual_native_matrix_conserves_columns(self):
        parent,flux,den,dt,p,r=self.case()
        # The exact point matrix is the MPRK structure, not a guessed sign.
        A=np.zeros((len(p),5,5))
        for src in range(5):
            A[:,src,src]=1
            for dest in range(5):
                if dest==src:continue
                rate=dt*r[:,dest,src]/p[:,src]
                A[:,dest,src]=-rate
                A[:,src,src]+=rate
        self.assertTrue(np.allclose(np.sum(A,axis=1),np.ones((len(p),5))))
        self.assertTrue(np.all(np.linalg.inv(A[:,:2,:2])>=0))
        self.assertTrue(np.all(np.linalg.inv(A[:,2:5,2:5])>=0))
        delta,_=c.structural_residual_increment(self.m,parent,flux,den,dt,np.sum(p[:,:2],axis=1),np.sum(p[:,2:],axis=1),self.original)
        b=-np.einsum("nij,nj->ni",A-np.eye(5)[None,:,:],p)
        target=np.linalg.solve(A,b[...,None])[...,0]
        self.assertTrue(np.all(target>=delta.lo-1e-11))
        self.assertTrue(np.all(target<=delta.hi+1e-11))

    def test_bad_blas_trial_only_widens_certificate(self):
        parent,flux,den,dt,p,r=self.case()
        with patch.object(c.np.linalg,"solve",side_effect=lambda A,b:np.zeros_like(b)):
            dp,st=c.structural_residual_increment(self.m,parent,flux,den,dt,np.sum(p[:,:2],axis=1),np.sum(p[:,2:],axis=1),self.original)
        self.assertTrue(np.all(dp.lo<=0))
        self.assertTrue(np.all(dp.hi>=0))
        self.assertEqual(len(st),2)

    def test_reject_physical_negative_rate(self):
        parent,flux,den,dt,p,r=self.case()
        lo=np.asarray(flux.lo).copy()
        lo[:,1,0]=-1e-3
        with self.assertRaisesRegex(ArithmeticError,"RATE_NONNEGATIVITY"):
            c.structural_residual_increment(self.m,parent,self.m._I(lo,flux.hi),den,dt,p[:,0]+p[:,1],p[:,2:].sum(axis=1),self.original)

    def test_reject_nonpositive_denominator(self):
        parent,flux,den,dt,p,r=self.case()
        bad=np.asarray(den.lo).copy();bad[:,0]=0
        with self.assertRaisesRegex(ValueError,"DENOMINATOR"):
            c.structural_residual_increment(self.m,parent,flux,self.m._I(bad,den.hi),dt,p[:,0]+p[:,1],p[:,2:].sum(axis=1),self.original)

    def test_outward_zero_not_physical_negative(self):
        parent,flux,den,dt,p,r=self.case()
        self.assertEqual(np.min(flux.lo),0.0)
        dp,stats=c.structural_residual_increment(self.m,parent,flux,den,dt,p[:,0]+p[:,1],p[:,2:].sum(axis=1),self.original)
        self.assertTrue(np.isfinite(dp.lo).all())
        self.assertEqual([x["certified_nodes"] for x in stats],[5,5])

if __name__=="__main__":
    unittest.main()
