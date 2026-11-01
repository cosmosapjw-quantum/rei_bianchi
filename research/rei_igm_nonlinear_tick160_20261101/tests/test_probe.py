"""Original source independent mathematical controls, not fake physical passes."""
import importlib.util,sys,unittest
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parents[1]/"code"/"probe_nonlinear.py"
spec=importlib.util.spec_from_file_location("rei_original_nonlinear_probe",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class I:
    def __init__(self,lo,hi):self.lo=np.asarray(lo);self.hi=np.asarray(hi)
class Tests(unittest.TestCase):
    def test_independent_box_floor_even_identical_map(self):
        a=I([.2,.4],[.5,.8])
        self.assertTrue(np.allclose(m.cross(a,a),[.3,.4]))
    def test_exact_point_equal_is_zero(self):
        a=I([.3],[.3])
        self.assertEqual(float(m.cross(a,a)[0]),0.)
    def test_cross_distances_correct(self):
        a=I([0.],[1.]);b=I([.2],[.3])
        self.assertAlmostEqual(float(m.cross(a,b)[0]),.8)
    def test_fail_bad_box(self):
        with self.assertRaises(ValueError):m.cross(I([2.],[1.]),I([0.],[1.]))
        with self.assertRaises(ValueError):m.cross(I([0.],[float("nan")]),I([0.],[1.]))
    def test_physics_original_lock(self):
        self.assertEqual((m.N,m.L,m.R,m.NT),(46080,160,161,131072))
        self.assertEqual(m.LOCAL_ERROR_GATE,2e-4)
        self.assertEqual(m.PUBLIC_WIDTH_GATE,2e-3)
        self.assertGreater(m.ORIGINAL_ERROR,m.LOCAL_ERROR_GATE)
    def test_BE_same_parent_analytic_oracle(self):
        g=1e-12;r=2e-13;h=1e11;k=g+r;q=k*h;x=.2
        f=lambda y,H:(y+H*g)/(1+H*k)
        actual=f(x,h)-f(f(x,h/2),h/2)
        exact=(x-g/k)*q*q/(4*(1+q)*(1+q/2)**2)
        self.assertAlmostEqual(actual,exact,delta=1e-14)
    def test_width_finite(self):
        self.assertEqual(m.qtiles(np.array([1.,2.,3.]))["median"],2.)
        with self.assertRaises(ValueError):m.qtiles(np.array([float("inf")]))
if __name__=="__main__":unittest.main()
