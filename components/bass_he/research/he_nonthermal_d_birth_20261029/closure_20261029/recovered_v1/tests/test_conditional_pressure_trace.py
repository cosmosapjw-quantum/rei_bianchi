import unittest
from fractions import Fraction as F
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from conditional_pressure_trace import *

class PressureTrace(unittest.TestCase):
    def test_frozen_m2(self):
        m=F(24377,71485)
        self.assertEqual(m*B2_MEV2,
            F(62574503954512379344012665,48306809029441085611817))
    def test_bounds_nontrivial(self):
        v=moment_trace_bounds(F(24377,71485))
        self.assertGreater(v['upper_MeV_per_event'],v['lower_MeV_per_event'])
        self.assertEqual(v['upper_MeV_per_event']-v['lower_MeV_per_event'],v['gap_MeV_per_event'])
    def test_jensen_constant_mu2(self):
        m=F(1,2)
        self.assertEqual(moment_trace_bounds(m)['upper_MeV_per_event'],event_pressure_trace_at_mu2(m))
    def test_secant_endpoint_mixture(self):
        m=F(1,2)
        exact_mix=(event_pressure_trace_at_mu2(0)+event_pressure_trace_at_mu2(1))/2
        self.assertEqual(moment_trace_bounds(m)['lower_MeV_per_event'],exact_mix)
    def test_endpoints(self):
        for m in (0,1):
            v=moment_trace_bounds(m)
            self.assertEqual(v['lower_MeV_per_event'],v['upper_MeV_per_event'])
            self.assertEqual(v['gap_MeV_per_event'],0)
    def test_invalid(self):
        for m in (F(-1,2),F(3,2),0.3):
            with self.assertRaises(ValueError):moment_trace_bounds(m)
    def test_midpoint_not_fixed(self):
        m=F(1,2)
        lower=F(1,2)*(event_pressure_trace_at_mu2(0)+event_pressure_trace_at_mu2(1))
        upper=event_pressure_trace_at_mu2(m)
        self.assertNotEqual(lower,upper)
    def test_manufactured_only(self):
        q=manufactured_pressure_trace_source(F(2,3),F(1,2),source_class='MANUFACTURED_TEST_ONLY')
        self.assertFalse(q['physical_activation'])
        self.assertLess(q['lower_J_m3s'],q['upper_J_m3s'])
        with self.assertRaises(ValueError): manufactured_pressure_trace_source(1,F(1,2),source_class='PHYSICAL')

if __name__=='__main__':unittest.main(verbosity=2)
