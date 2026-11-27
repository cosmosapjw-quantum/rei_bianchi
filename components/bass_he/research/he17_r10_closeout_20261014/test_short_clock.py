import math,sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from axbi_short_clock import short_increment,truncation_relative_ceiling

class ClockContract(unittest.TestCase):
    def test_scoped_short_interval_and_positive_time(self):
        a=1.0/21
        b=a*math.exp(1.e-6)
        for q in (0.0,.005,-.005,.01,-.01):
            out=short_increment(a,b,q)
            self.assertGreater(out['dt_s'],0)
            self.assertEqual(out['model'],'PhysicalDensityFixed')
    def test_fourth_derivative_real_quadrature_bound(self):
        self.assertLess(truncation_relative_ceiling(.005),1e-8)
        self.assertGreater(truncation_relative_ceiling(.01),truncation_relative_ceiling(.005))
    def test_signed_shear_even_clock(self):
        a=.05;b=a*math.exp(.0001)
        self.assertEqual(short_increment(a,b,.01)['dt_s'],short_increment(a,b,-.01)['dt_s'])
    def test_same_h_clock_independent_of_shear(self):
        a=.05;b=a*math.exp(.0001)
        self.assertEqual(short_increment(a,b,.01,'SameHDiagnostic')['dt_s'],short_increment(a,b,0.0,'SameHDiagnostic')['dt_s'])
    def test_bad_interval_refused(self):
        with self.assertRaises(ValueError):short_increment(.06,.06,.01)
        with self.assertRaises(ValueError):short_increment(.2,.21,.01)
        with self.assertRaises(ValueError):short_increment(.05,.051,float('nan'))
if __name__=='__main__':unittest.main()
