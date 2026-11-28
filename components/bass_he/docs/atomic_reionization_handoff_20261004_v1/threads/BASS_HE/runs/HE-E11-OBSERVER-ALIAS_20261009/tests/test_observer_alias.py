import unittest
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal
from importlib import import_module

class TestE11(unittest.TestCase):
    def setUp(self):
        self.m = import_module('e11.observer_alias')

    def test_float_exact(self):
        self.assertEqual(self.m.f64('0.1'),F.from_float(0.1))
        with self.assertRaises(ValueError): self.m.f64('NaN')

    def test_photo_weights_include_heiii_and_neutral_he(self):
        w=self.m.photo_weights(F(1,5),F(1,10),F(1,20),F(9,10))
        self.assertEqual(w,(F(9,10), F(1,100), F(1,100)))

    def test_photo_rate_expected(self):
        f=F(3,38); weights=self.m.photo_weights(f,F(1,10),F(1,20),F(9,10))
        self.assertEqual(self.m.source(weights,(F(1),F(2),F(3))), sum((a*b for a,b in zip(weights,(F(1),F(2),F(3)))),F(0)))

    def test_symmetric_decomposition(self):
        a=(F(2),F(5),F(11)); b=(F(3),F(7),F(13)); w0=(F(3),F(4),F(1)); w1=(F(2),F(4),F(2))
        x=self.m.symmetric_pair(w0,w1,a,b)
        self.assertEqual(x['delta'],x['rate']+x['occupancy'])
        self.assertEqual(x['delta'],sum((b[i]*w1[i]-a[i]*w0[i] for i in range(3)),F(0)))

    def test_observer_alias_identity(self):
        wl=(F(2),F(3),F(4)); w0=(F(1),F(2),F(3))
        gl=(F(7),F(11),F(13)); g0=(F(5),F(7),F(11))
        el=(F(17),F(19),F(23)); e0=(F(13),F(17),F(19))
        c=self.m.paired_alias_decomposition(w0,wl,g0,gl,e0,el)
        self.assertEqual(c['total'],c['rate']+c['occupancy'])
        self.assertEqual(c['total'],self.m.source(wl,gl)-self.m.source(w0,g0)-(self.m.source(wl,el)-self.m.source(w0,e0)))

    def test_ratio_preserves_zero(self):
        self.assertEqual(self.m.allowance_ratio(F(0),F(0)),F(0))
        with self.assertRaises(ValueError):self.m.allowance_ratio(F(1),F(-1),F(0),F(0))

    def test_false_identity_refused(self):
        with self.assertRaises(ValueError): self.m.assert_same_bits('1.0','1.0000000000000002','s')
        self.m.assert_same_bits('1e0','1.00000000000000000e+00','s')

    def test_rows_guard(self):
        with TemporaryDirectory() as t:
            p=Path(t)/'x.csv';p.write_text('step,x\n0,1\n2,2\n')
            with self.assertRaises(ValueError):self.m.load_mode_csv(p,385)

    def test_no_zero_denominator_paired_claim(self):
        self.assertIsNone(self.m.condition(F(1), F(-1)))
        self.assertEqual(self.m.condition(F(1), F(-2)),F(3))

    def test_exact_decomposition_all_species(self):
        for n in range(1,8):
            a=tuple(F(n*i,11) for i in (1,2,3));b=tuple(F(n*i+1,13) for i in (1,2,3))
            w=tuple(F(i,19) for i in (1,2,3));wp=tuple(F(i,17) for i in (1,2,3))
            z=self.m.symmetric_pair(w,wp,a,b)
            self.assertEqual(z['rate']+z['occupancy'],z['delta'])

if __name__=='__main__':unittest.main()
