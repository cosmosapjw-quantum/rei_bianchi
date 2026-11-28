import unittest, sys, tempfile
from pathlib import Path
from fractions import Fraction as F
from math import pi, sin
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from exfor_envelope import *

class ExforEventNormalization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.da,cls.sig=load_source(ROOT/'source/M0475.x4')
        cls.p=rows330(cls.da)
    def test_source_identity_and_count(self):
        self.assertEqual((len(self.da),len(self.sig)),(12,6))
    def test_measured_330_rows(self):
        self.assertEqual([int(p.theta) for p in self.p],[46,61,73,87])
        self.assertEqual([p.value for p in self.p],list(map(F,['0.14','0.16','0.07','0.19'])))
    def test_total_330_absent(self):
        self.assertNotIn(F(330),[p.energy for p in self.sig])
        self.assertEqual([(p.energy,p.value) for p in self.sig[-2:]],[(F(320),F('0.61')),(F(359),F('0.55'))])
    def test_exact_minimum_L(self):
        self.assertEqual(min_L(self.p),F(1,700))
        self.assertEqual(min_L(self.p,False),F(3,350))
    def test_subcritical_infeasible(self):
        with self.assertRaises(ValueError):segments(self.p,F(1,1000),'lower')
    def test_boundary_feasible(self):
        for theta in list(range(91)):
            self.assertLessEqual(envelope(self.p,F(1,700),theta,'lower'),
                                 envelope(self.p,F(1,700),theta,'upper'))
    def test_sample_constraints(self):
        for p in self.p:
            l=envelope(self.p,F(1,200),p.theta,'lower')
            u=envelope(self.p,F(1,200),p.theta,'upper')
            self.assertLessEqual(p.lo,l)
            self.assertLessEqual(l,p.hi)
            self.assertLessEqual(p.lo,u)
            self.assertLessEqual(u,p.hi)
    def test_segments_cover_domain_and_affine(self):
        for kind in ['lower','upper']:
            pieces=segments(self.p,F(1,200),kind)
            self.assertEqual(pieces[0][0],0)
            self.assertEqual(pieces[-1][1],90)
            for (a,b,c,d),(a2,_,_,_) in zip(pieces,pieces[1:]):
                self.assertEqual(b,a2)
                self.assertLess(a,b)
                self.assertEqual(c+d*(a+b)/2,envelope(self.p,F(1,200),(a+b)/2,kind))
    def test_integral_monotonic_L(self):
        lo1=mp.mpf(angular_integral(self.p,F(1,700),'lower',60))
        lo2=mp.mpf(angular_integral(self.p,F(1,200),'lower',60))
        hi1=mp.mpf(angular_integral(self.p,F(1,700),'upper',60))
        hi2=mp.mpf(angular_integral(self.p,F(1,200),'upper',60))
        self.assertGreater(lo1,lo2)
        self.assertLess(hi1,hi2)
    def test_exact_angular_integral_independent_quad(self):
        with mp.workdps(65):
            L=F(1,200)
            for kind in ['lower','upper']:
                expected=mp.mpf(angular_integral(self.p,L,kind,70))
                theta=[mp.mpf(0)]+[mp.mpf(p.theta.numerator)/p.theta.denominator for p in self.p]+[mp.mpf(90)]
                # Independent pointwise max/min evaluation, not active-branch integral.
                def f(t):
                    vals=[]
                    for p in self.p:
                        a=mp.mpf(p.theta.numerator)/p.theta.denominator
                        z=mp.mpf((p.lo if kind=='lower' else p.hi).numerator)/ (p.lo if kind=='lower' else p.hi).denominator
                        vals.append(z+(-1 if kind=='lower' else 1)*mp.mpf(1)/200*abs(t-a))
                    return (max([mp.mpf(0)]+vals) if kind=='lower' else min(vals))*mp.sin(mp.pi*t/180)
                # Split at all exact active-branch breakpoints for robust adaptive quad.
                cuts=sorted({F(0),F(90)}|{p.theta for p in self.p}|
                            {z for a,b,_,_ in segments(self.p,L,kind) for z in (a,b)})
                quad=4*mp.pi*(mp.pi/180)*mp.fsum(mp.quad(f,[mp.mpf(x.numerator)/x.denominator,
                                                   mp.mpf(y.numerator)/y.denominator]) for x,y in zip(cuts,cuts[1:]))
                self.assertLess(abs(quad-expected),mp.mpf('1e-45'))
    def test_convention_ratio_and_nonadmission(self):
        a=conditional_sigma(self.p,'1/200','inclusive_D',50)
        b=conditional_sigma(self.p,'1/200','randomly_oriented_one_D',50)
        self.assertLess(abs(mp.mpf(a['conditional_sigma_lower_nb'])*2-
                            mp.mpf(b['conditional_sigma_lower_nb'])),mp.mpf('1e-35'))
        self.assertFalse(a['physical_activation'])
        self.assertIsNone(a['physical_rate_m3s'])
    def test_missing_convention(self):
        with self.assertRaises(ValueError):conditional_sigma(self.p,'1/200','PHYSICAL')
    def test_missing_rate_not_zero(self):
        a=conditional_sigma(self.p,'1/200','inclusive_D',50)
        self.assertIsNone(manufactured_rate(a,None,'2',source_class='MANUFACTURED_TEST_ONLY')['R_lower_m3s'])
    def test_manufactured_rate_dimension(self):
        a=conditional_sigma(self.p,'1/200','inclusive_D',50)
        r=manufactured_rate(a,'2','3',source_class='MANUFACTURED_TEST_ONLY')
        self.assertLess(abs(mp.mpf(r['R_lower_m3s'])-mp.mpf(a['conditional_sigma_lower_nb'])*6*mp.mpf('1e-37')),mp.mpf('1e-78'))
        self.assertFalse(r['physical_activation'])
    def test_unqualified_rate_rejected(self):
        a=conditional_sigma(self.p,'1/200','inclusive_D',50)
        with self.assertRaises(ValueError):manufactured_rate(a,1,1,source_class='PHYSICAL')
    def test_float_and_bool_rejected(self):
        for x in [0.5,True,False]:
            with self.assertRaises(ValueError):q(x)
    def test_source_mutation_rejected(self):
        raw=(ROOT/'source/M0475.x4').read_bytes()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.x4';p.write_bytes(raw.replace(b'0.14       0.03',b'0.15       0.03'))
            with self.assertRaises(ValueError):load_source(p)
    def test_no_confidence_claim(self):
        self.assertIn('not_joint_CI',sharp_bounds(self.p,'1/200')['uncertainty_type'])
        self.assertFalse(sharp_bounds(self.p,'1/200')['numeric_rounding_certified'])
    def test_nb_to_m2(self):
        self.assertEqual(NB_TO_M2,F(1,10**37))

if __name__=='__main__':unittest.main(verbosity=2)
