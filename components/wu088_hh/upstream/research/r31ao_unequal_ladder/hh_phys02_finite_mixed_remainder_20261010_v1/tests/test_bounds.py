import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from flint import arb, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from jet_algebra import HD, Jet, flow_jet
from frozen_source import FrozenSource
from bound_remainder import construct_tube, exact_endpoint, ROUND_FLOOR, ROUND_CEILING


class AlgebraTests(unittest.TestCase):
    def setUp(self):
        ctx.prec=256

    def enclosed(self, got, expected):
        self.assertTrue((got-expected).contains(0), str((got,expected)))

    def test_hyperdual_product(self):
        a=HD(2,3,5,7)*HD(11,13,17,19)
        self.assertEqual(a.c,(arb(22),arb(59),arb(89),arb(231)))

    def test_hyperdual_mixed_exponential(self):
        a=HD(2,1)*HD(3,0,1)
        mixed=a.exp().c[3]
        self.enclosed(mixed,7*arb(6).exp())

    def test_hyperdual_log_inverse(self):
        y=HD(3,2,5,7)
        self.enclosed(y.log().c[3],arb(7)/3-arb(10)/9)
        self.enclosed(y.inv().c[3],arb(20)/27-arb(7)/9)

    def test_hyperdual_noninteger_power(self):
        p=arb(1.2)
        y=HD(3,2,5,7)**p
        expected=p*arb(3)**(p-1)*7+p*(p-1)*arb(3)**(p-2)*10
        self.enclosed(y.c[3],expected)

    def test_time_exp_log_reciprocal(self):
        y=Jet([HD(2),HD(3),HD(5)],4)
        identity=y.exp().log()-y
        reciprocal=y*y.inv()-1
        for poly in [identity,reciprocal]:
            for a in poly.a:
                for v in a.c:
                    self.assertTrue(v.contains(0))

    def test_scalar_rational_flow_and_initial_mixed(self):
        z=flow_jet(lambda y,l,s:[y[0]**2],[HD(2,1,1)],HD(0),HD(0),4)[0]
        for n,a in enumerate(z.a):
            self.enclosed(a.c[0],arb(2)**(n+1))
            self.enclosed(a.c[3],0 if n==0 else n*(n+1)*arb(2)**(n-1))

    def test_scalar_exponential_parameter_flow(self):
        l=arb('0.7');s=arb('0.2')
        z=flow_jet(lambda y,lam,src:[lam*y[0]+src],[HD(1)],HD(l,1),HD(s,0,1),4)[0]
        factorial=1
        for n in range(1,5):
            factorial*=n
            expected=0 if n==1 else (n-1)*l**(n-2)/factorial
            self.enclosed(z.a[n].c[3],expected)

    def test_denominator_and_log_guard(self):
        with self.assertRaises(ValueError):
            HD(arb(0,1)).inv()
        with self.assertRaises(ValueError):
            HD(-1).log()

    def test_exact_endpoint_outward_decimal(self):
        x=arb('-1.1234567890123456789012345678901234567890123456789 +/- 1e-55')
        for endpoint,rounding,is_lower in [(x.lower(),ROUND_FLOOR,True),(x.upper(),ROUND_CEILING,False)]:
            display,dyad=exact_endpoint(endpoint,rounding)
            m=int(dyad['mantissa']);e=dyad['exponent_2']
            exact=Fraction(m)*(Fraction(2)**e)
            stored=Fraction(Decimal(display))
            self.assertTrue(stored<=exact if is_lower else stored>=exact)


class SourceTests(unittest.TestCase):
    def setUp(self):
        ctx.prec=256
        self.m=FrozenSource(ROOT/'inputs/SELECTED_SOURCE.json')

    def test_photon_inventory_exact_elimination(self):
        self.assertEqual(self.m.active,list(range(16,25)))
        self.assertEqual(self.m.inert,list(range(16)))
        self.assertEqual(len(self.m.initial),13)
        self.assertTrue(all(self.m.data['sigma_cm2'][j]==[0.,0.,0.] for j in self.m.inert))

    def test_HH_channel_energy_direction(self):
        y=[HD(a) for a in self.m.initial]
        f=self.m.rhs(y,HD(0,1),HD(0,0,1))
        self.assertTrue((f[3].c[1]+self.m.chi[0]*f[0].c[1]).contains(0))
        self.assertTrue(all(f[j].c[1]==0 for j in [1,2]+list(range(4,13))))

    def test_source_only_inserts_selected_photons(self):
        f=self.m.rhs([HD(a) for a in self.m.initial],HD(0,1),HD(0,0,1))
        self.assertTrue(all(row.c[2]==0 for row in f[:-1]))
        self.assertTrue((f[-1].c[2]-self.m.h*self.m.sstar).contains(0))

    def test_all_component_tube_and_rate_domain(self):
        box,lam,source,proof=construct_tube(self.m)
        self.assertEqual(len(proof['strict_components']),52)
        self.assertEqual(proof['invariant_zero_components'],[])
        self.assertTrue(proof['domain']['all_pass'])
        self.assertEqual(proof['iterations'][-1]['failed_components'],[])

    def test_fourth_coefficient_parameter_structure(self):
        vals={}
        for l,s in [(0,0),(0,1),(1,0),(1,1),(.5,.5)]:
            coeff=flow_jet(self.m.rhs,[HD(a) for a in self.m.initial],HD(l,1),HD(s,0,1),4)[0].a[4].c[3]
            vals[l,s]=coeff
        self.assertTrue((vals[0,0]-vals[0,1]).contains(0))
        self.assertTrue((vals[1,0]-vals[1,1]).contains(0))
        self.assertTrue((2*vals[.5,.5]-vals[0,0]-vals[1,0]).contains(0))
        self.assertTrue(all(v>0 for v in vals.values()))


if __name__=='__main__':
    unittest.main(verbosity=2)
