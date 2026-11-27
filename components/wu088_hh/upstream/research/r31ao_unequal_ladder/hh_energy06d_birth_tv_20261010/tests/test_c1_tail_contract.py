import pathlib,sys,unittest
from fractions import Fraction as F
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from c1_tail_contract import uniform_selected_kummer_tail,NotAdmitted
class C1FiniteSeriesMathematicalTests(unittest.TestCase):
    def test_existing_selected_odd_k_and_r_families_have_uniform_tail(self):
        for k in [1,3,5,7]:
            for r in [0,1,2]:
                z=uniform_selected_kummer_tail(k,r)
                self.assertTrue(z['conditional_series_tail_verified'])
                self.assertLess(z['ratio_q'],F(6656,26471))
                self.assertLess(z['factor'],F(26471,19815))
    def test_numerical_constants_not_falsely_relaxed(self):
        z=uniform_selected_kummer_tail(1,0)
        self.assertEqual(z['ratio_q'],F(64,257))
        self.assertEqual(z['factor'],F(257,193))
        self.assertEqual(z['n_start'],256)
        self.assertFalse(z['full_box_admitted'])
    def test_outside_legacy_selected_family_is_refused(self):
        for k,r in [(0,0),(2,1),(9,0),(1,3),(-1,0)]:
            with self.subTest(k=k,r=r), self.assertRaises(NotAdmitted):
                uniform_selected_kummer_tail(k,r)
    def test_insufficient_terms_or_uncontrolled_z_refused(self):
        for opts in [{'terms':255},{'abs_z_bound':65},{'abs_z_bound':-1}]:
            with self.subTest(opts=opts), self.assertRaises(NotAdmitted):
                uniform_selected_kummer_tail(1,0,**opts)
if __name__=='__main__': unittest.main()
