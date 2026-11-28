import unittest
from fractions import Fraction as F
from decimal import localcontext
from .decimal_oracle import dec, pi as decimal_pi, gamma_half, mass_diagnostics
from .engine import (Interval, sqrt_bounds, pi_bounds, exp_neg_bounds,
    gamma_half_bounds, radial_gaussian_moment, hermite_coefficient,
    lower_mass_bound, upper_mass_bound, interior_mass_bound,
    gaussian_field_majorant, complement_bound, ResourceLimit)

class EndpointTests(unittest.TestCase):
    def test_interval_outward_arithmetic(self):
        a,b=Interval(F(-2),F(3)),Interval(F(4),F(5))
        self.assertEqual(a*b,Interval(F(-10),F(15)))
        self.assertEqual(a+b,Interval(F(2),F(8)))
        with self.assertRaises(ValueError):a/Interval(F(-1),F(1))
    def test_sqrt_proof_inequalities(self):
        for x in [F(0),F(1),F(2),F(1,3),F(81,49),F(1,2**300)]:
            s=sqrt_bounds(x,80);self.assertLessEqual(s.lo*s.lo,x);self.assertGreaterEqual(s.hi*s.hi,x)
        self.assertEqual(sqrt_bounds(F(4),80),Interval(F(2),F(2)))
    def test_pi_independent_rational_brackets(self):
        p=pi_bounds(96)
        self.assertGreater(p.lo,F(103993,33102));self.assertLess(p.hi,F(104348,33215))
        self.assertLess(p.hi-p.lo,F(1,2**90))
    def test_exp_zero_and_range(self):
        self.assertEqual(exp_neg_bounds(F(0)),Interval(F(1),F(1)))
        for x in [F(1,4),F(1),F(10),F(1000)]:
            b=exp_neg_bounds(x);self.assertGreaterEqual(b.lo,0);self.assertLessEqual(b.hi,1)
        b=exp_neg_bounds(F(1));self.assertGreater(b.lo,F(3678794411714423,10**16));self.assertLess(b.hi,F(3678794411714424,10**16))
    def test_positive_half_gamma_recurrence(self):
        x=F(2);g=gamma_half_bounds(1,x);h=gamma_half_bounds(3,x)
        reference=F(1,2)*g+sqrt_bounds(x)*exp_neg_bounds(x)
        self.assertEqual(h,reference)
        with self.assertRaises(ValueError):gamma_half_bounds(2,x)
        with self.assertRaises(ValueError):gamma_half_bounds(1,F(0))
    def test_gaussian_moments(self):
        p=pi_bounds();m0=radial_gaussian_moment(0);m2=radial_gaussian_moment(2)
        self.assertEqual(m2,F(3,2)*m0)
        self.assertEqual(radial_gaussian_moment(1),2*p)
        self.assertEqual(radial_gaussian_moment(3),4*p)
    def test_hermite_i0_identity(self):
        a=hermite_coefficient(0,0,F(1));root=sqrt_bounds(pi_bounds().lo)
        self.assertGreater(a.lo,F(28,100));self.assertLess(a.hi,F(29,100))
        self.assertGreater(root.lo,1)
    def test_endpoint_monotonic_and_positive(self):
        self.assertGreater(lower_mass_bound(0,F(1),F(1),F(1)),0)
        self.assertGreater(upper_mass_bound(0,F(1),F(1)),upper_mass_bound(0,F(1),F(2)))
        self.assertGreaterEqual(interior_mass_bound(2,F(1),F(1),F(1,2),F(2),panels=4),0)
    def test_field_majorant_delta_pz(self):
        origin=(F(0),F(0),F(0))
        s=gaussian_field_majorant(F(1),F(1),origin,origin,0,'s','O')
        # Different valid interval expressions need not have identical upper endpoints.
        with localcontext() as ctx:
            ctx.prec=90
            self.assertGreaterEqual(dec(s),decimal_pi()**3)
        px=gaussian_field_majorant(F(1),F(1),origin,origin,0,'px','G1')
        pz=gaussian_field_majorant(F(1),F(1),origin,origin,0,'pz','G1')
        self.assertGreater(pz,px)
        with localcontext() as ctx:
            ctx.prec=90
            self.assertGreaterEqual(dec(px),3*decimal_pi()**3)
            self.assertGreaterEqual(dec(pz),4*decimal_pi()**3)
            self.assertGreaterEqual(dec(pz-px),decimal_pi()**3)
    def test_disjoint_accounting(self):
        r=complement_bound(0,0,F(1),F(1),F(1),F(1,4),F(4),F(1,3),F(5),F(2),panels=4)
        self.assertEqual(r['bound'],2*(r['E_t']*r['W_u']+r['J_t']*r['E_u']))
        self.assertNotIn('W_t_minus_E_t',r)
        self.assertNotIn('HH_evaluated',r)
        self.assertIsNone(r['actual_hh_evaluation_assertion'])
    def test_independent_high_precision_oracle(self):
        with localcontext() as ctx:
            ctx.prec=90
            for shape in [1,3,5,9]:
                x=F(7,3);g=gamma_half_bounds(shape,x)
                v=gamma_half(shape,x)
                self.assertLessEqual(dec(g.lo),v);self.assertGreaterEqual(dec(g.hi),v)
            for i in [0,1,3]:
                mu,a,l,T=F(3,2),F(5,4),F(1,3),F(3)
                diagnostic=mass_diagnostics(i,mu,a,l,T)
                bounds={'lower':lower_mass_bound(i,mu,a,l),
                        'upper':upper_mass_bound(i,mu,T),
                        'interior':interior_mass_bound(i,mu,a,l,T,panels=8)}
                for region,bound in bounds.items():
                    # Refinement separation is a diagnostic only; the bound's
                    # authority is the analytic positive-majorant proof.
                    row=diagnostic[region]
                    self.assertGreater(dec(bound)-row['value'],10*row['refinement_delta'])
    def test_caps_and_domain_fail_closed(self):
        with self.assertRaises(ValueError):lower_mass_bound(0,F(0),F(1),F(1))
        with self.assertRaises(ValueError):interior_mass_bound(0,F(1),F(1),F(2),F(1))
        with self.assertRaises(ValueError):gaussian_field_majorant(F(1),F(1),(F(0),)*3,(F(0),)*3,0,'bad','O')
        with self.assertRaises(ResourceLimit):exp_neg_bounds(F(1),max_terms=1)
        with self.assertRaises(ResourceLimit):sqrt_bounds(F(2),4097)
        with self.assertRaises(ResourceLimit):interior_mass_bound(0,F(1),F(1),F(1),F(2),panels=100000)

if __name__=='__main__':unittest.main()
