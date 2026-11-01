import importlib.util
import math
from pathlib import Path
import unittest

import numpy as np

SCRIPT=Path(__file__).resolve().parents[1]/"joint_stage.py"
spec=importlib.util.spec_from_file_location("rei_original_allx_stage_under_test",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def rate(n,c,j,e):
    S=np.sum(n,axis=0,dtype=np.longdouble).astype(float)
    return j*n*c[None,:]/(e+float(c@S))


class OriginalCommonMomentAlgebra(unittest.TestCase):
    def setUp(self):
        self.n=np.array([[5.0,2.0,3.0],[4.0,7.0,1.0],[3.0,6.0,2.0]],float)
        self.c=np.array([0.2,0.5,0.1],float)
        self.j=11.0
        self.e=0.3

    def test_directional_derivative_includes_local_and_global(self):
        dn=np.array([[1.,-0.3,0.1],[-0.2,0.4,-0.1],[-0.5,0.1,0.2]])*1e-5
        derivative=m.rational_rate_jvp(self.n,dn,self.c,np.sum(dn,axis=0),self.j,self.e)
        actual=rate(self.n+dn,self.c,self.j,self.e)-rate(self.n,self.c,self.j,self.e)
        self.assertLess(float(np.max(abs(actual-derivative))),2e-10)
        self.assertGreater(float(np.max(abs(derivative))),1e-8)

    def test_global_denominator_is_shared_among_nodes(self):
        dn=np.zeros_like(self.n)
        dn[-1,0]=0.3
        jac=m.rational_rate_jvp(self.n,dn,self.c,dn.sum(axis=0),self.j,self.e)
        self.assertLess(jac[0,0],0)
        self.assertLess(jac[1,1],0)
        self.assertGreater(jac[2,0],0)

    def test_exact_finite_remainder_enclosed_by_analytic_rectangle(self):
        perturb=np.array([[0.4,-0.2,0.1],[-0.1,0.25,-0.08],[-0.3,0.3,0.07]])
        low=np.minimum(self.n,self.n+perturb)
        high=np.maximum(self.n,self.n+perturb)
        rem, diag=m.rational_remainder_bound(self.n,low,high,self.c,self.j,self.e)
        d=m.rational_rate_jvp(self.n,perturb,self.c,perturb.sum(axis=0),self.j,self.e)
        exact=rate(self.n+perturb,self.c,self.j,self.e)-rate(self.n,self.c,self.j,self.e)
        self.assertTrue(np.all(abs(exact-d)<=rem+1e-13))
        self.assertGreater(diag["denominator_lower"],0)
        self.assertGreaterEqual(diag["denominator_center"],diag["denominator_lower"])
        self.assertLessEqual(diag["denominator_center"],diag["denominator_upper"])

    def test_zero_support_exactly_stays_zero(self):
        c=np.array([1.0,0.0,0.3])
        p=self.n
        dn=0.02*p
        jvp=m.rational_rate_jvp(p,dn,c,np.sum(dn,axis=0),self.j,self.e)
        rem,_=m.rational_remainder_bound(p,0.98*p,1.02*p,c,self.j,self.e)
        self.assertTrue(np.array_equal(jvp[:,1],np.zeros(3)))
        self.assertTrue(np.array_equal(rem[:,1],np.zeros(3)))

    def test_failure_on_nonpositive_denominator(self):
        with self.assertRaises(ValueError):
            m.rational_remainder_bound(self.n,self.n,self.n,np.zeros(3),3.0,0.0)

    def test_reject_not_in_parent(self):
        with self.assertRaises(ValueError):
            m.rational_remainder_bound(self.n,1.1*self.n,1.2*self.n,self.c,self.j,self.e)

    def test_no_false_original_certification_flag(self):
        import inspect
        code=inspect.getsource(m.run)
        self.assertIn('"joint_full_map_jacobian_remainder_certified":False',code)
        self.assertIn('"production":"HOLD"',code)
        self.assertIn('"canonical_delta":0',code)

    def test_stage_is_the_original_whole_box_not_point_probe(self):
        import inspect
        source=inspect.getsource(m.run)
        self.assertIn("decoded.population_lower,decoded.population_upper",source)
        self.assertIn('"half2"',source)
        self.assertIn('"full"',source)
        self.assertIn('"half1"',source)

if __name__=="__main__":
    unittest.main()
