import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spin_projection import fractions,singlet_event_envelope,exploratory_langer_mixing
class TestSpinProjection(unittest.TestCase):
    def test_exact_normalized(self):
        for r,t in ((0,0),(1.65,0.2),(4,100)):
            self.assertAlmostEqual(sum(fractions(r,t).values()),1)
    def test_strict_pure_singlet_lower_zero(self):
        lo,hi=singlet_event_envelope(5,1.65,0.2)
        self.assertEqual(lo,0)
        self.assertGreater(hi,0)
    def test_negative_input_reject(self):
        for r,t in ((-1,.2),(1,-.2)):
            with self.assertRaises(ValueError):fractions(r,t)
    def test_nan_reject(self):
        with self.assertRaises(ValueError):fractions(float('nan'),0)
    def test_exploratory_fractions(self):
        f=exploratory_langer_mixing(1.65,.15,.1,.1)
        self.assertAlmostEqual(sum(f.values()),1)
    def test_incompatible_positivity(self):
        with self.assertRaises(ValueError):exploratory_langer_mixing(2,.1,.2,.8)
if __name__=='__main__':unittest.main()
