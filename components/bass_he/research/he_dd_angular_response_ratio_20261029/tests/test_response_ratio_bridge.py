"""Targeted exact tests; no original IVP/science suite imported."""
import sys, unittest
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from response_ratio_bridge import (reweight_bounds,
                                   ratio_from_symmetric_relative_error,
                                   uniform_difference_bound,source_model_status)

class RatioBridgeTest(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(reweight_bounds(F(1,4), F(3,4), 1), (F(1,4),F(3,4)))
    def test_ratio_exact(self):
        self.assertEqual(ratio_from_symmetric_relative_error(F(1,20)),F(21,19))
    def test_moment_endpoint(self):
        self.assertEqual(reweight_bounds(0, 1, F(100)),(F(0),F(1)))
    def test_binary_sharpness(self):
        self.assertEqual(reweight_bounds(F(1,2), F(1,2),3),(F(1,4),F(3,4)))
    def test_ratio_invalid(self):
        for r in [-3,0,F(1,2)]:
            with self.assertRaises(ValueError):reweight_bounds('0.1','0.9',r)
    def test_delta_invalid(self):
        for d in [-1,1,2]:
            with self.assertRaises(ValueError):ratio_from_symmetric_relative_error(d)
    def test_float_or_bool_refused(self):
        for x in [.05,True,False]:
            with self.assertRaises(TypeError):ratio_from_symmetric_relative_error(x)
    def test_bad_b_order(self):
        for l,h in [(1,0),(-1,1),(0,2)]:
            with self.assertRaises(ValueError):reweight_bounds(l,h,2)
    def test_uniform_exact(self):
        self.assertEqual(uniform_difference_bound(F(9,4)),F(1,5))
        self.assertIsNone(uniform_difference_bound(2))
    def test_source_admission_hold(self):
        g=source_model_status()
        self.assertIsNone(g['R_event'])
        self.assertFalse(g['physical_activation'])
        self.assertEqual(g['production'],'HOLD')
    def test_exhaustive_rational_2point(self):
        # Unrelated exact enumeration, not LP or numerical integration.
        for a in range(1,8):
            for b in range(1,8):
                for v1i in range(5):
                    for v2i in range(5):
                        for q1i in range(1,6):
                            for q2i in range(1,6):
                                v1,v2=F(v1i,4),F(v2i,4)
                                p=F(a,a+b)
                                q1,q2=F(q1i),F(q2i)
                                base=p*v1+(1-p)*v2
                                r=max(q1,q2)/min(q1,q2)
                                weight=(p*q1*v1+(1-p)*q2*v2)/(p*q1+(1-p)*q2)
                                lower,upper=reweight_bounds(base,base,r)
                                self.assertLessEqual(lower,weight)
                                self.assertLessEqual(weight,upper)
    def test_monotonicity_exact(self):
        for r in [1,F(21,19),2,5,100]:
            last_lo,last_hi=F(0),F(0)
            for i in range(101):
                l,h=reweight_bounds(F(i,100),F(i,100),r)
                self.assertGreaterEqual(l,last_lo)
                self.assertGreaterEqual(h,last_hi)
                last_lo,last_hi=l,h

if __name__=='__main__': unittest.main()
