"""Focused independent arithmetic checks for RUN19 mathematical tools."""
import decimal
from fractions import Fraction as F
import math
from pathlib import Path
import unittest
from analytic_rate_curvature import bernstein, exact_polynomial, li_be_rows, rr
from cubic_rate_bound import cubic_relative_bound

class RateMathTests(unittest.TestCase):
    def test_bernstein_reconstruction_exact_and_parser_digits(self):
        # (x-1)^4 - 3(x-1)^2 + 2, checked against its factored expression.
        p=[F(0),F(2),F(3),F(-4),F(1)]
        b=bernstein(p,F(-1),F(2))
        for u in (F(0),F(1,7),F(1,2),F(9,10),F(1)):
            x=-1+3*u
            value=sum(b[k]*math.comb(4,k)*u**k*(1-u)**(4-k) for k in range(5))
            self.assertEqual(value,(x-1)**4-3*(x-1)**2+2)
        parsed=exact_polynomial("-32.71396786375 + 13.53655609057*l - 2.039149852002e-6*l.powi(8)")
        self.assertEqual(parsed[8],-F("2.039149852002e-6"))
        self.assertEqual(parsed[0],-F("32.71396786375"))
        with self.assertRaises(ValueError):
            exact_polynomial("l + unknown(l)")

    def test_primary_six_rows_independent_decimal_direct_denominator(self):
        rows=li_be_rows(Path(__file__).parent/"primary_sources/verner_ferland_table1.dat")
        self.assertEqual([(r["Z"],r["N_final"]) for r in rows],[(3,3),(3,2),(3,1),(4,3),(4,2),(4,1)])
        with decimal.localcontext() as ctx:
            ctx.prec=80
            D=decimal.Decimal
            for row in rows:
                a,b,t0,t1=(D(row[k]) for k in ("a_cm3_s","b","T0_K","T1_K"))
                for t in (3,10,100,10000,1000000,1000000000):
                    u=(D(t)/t0).sqrt();v=(D(t)/t1).sqrt()
                    value=a/(u*(1+u)**(1-b)*(1+v)**(1+b))
                    f64=D.from_float(rr(row,float(t)))
                    self.assertLess(abs(f64/value-1),D("1e-13"))
                for t in (float("nan"),0.0,2.999,1e9+1):
                    with self.assertRaises(ValueError):rr(row,t)

    def test_cubic_kernel_against_quartic_and_exponential_bound(self):
        # Four-node interpolant of x^4: exact error is the nodal product.
        for theta in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
            w=(-theta*(theta-1)*(theta-2)/6,(theta+1)*(theta-1)*(theta-2)/2,
               -(theta+1)*theta*(theta-2)/2,(theta+1)*theta*(theta-1)/6)
            self.assertEqual(sum(w),1)
            for k in range(1,4):
                self.assertEqual(sum(wj*F(x)**k for wj,x in zip(w,(-1,0,1,2))),theta**k)
            actual=theta**4-sum(wj*F(x)**4 for wj,x in zip(w,(-1,0,1,2)))
            product=(theta+1)*theta*(theta-1)*(theta-2)
            self.assertEqual(actual,product)
            self.assertLessEqual(abs(product)/24,F(3,128))
        # Independent high-precision manufactured exp(90x), steeper than most
        # physical channel logs. Compare central query against exact values.
        bound=cubic_relative_bound([F(90),F(0),F(0),F(0)],16385)
        rational=F(int(bound["relative_error_rational_upper"]["numerator"]),
                   int(bound["relative_error_rational_upper"]["denominator"]))
        with decimal.localcontext() as ctx:
            ctx.prec=80;D=decimal.Decimal
            h=D(1000000).ln()/D(16384)
            for theta in (D("0.1"),D("0.5"),D("0.9")):
                w=(-theta*(theta-1)*(theta-2)/6,(theta+1)*(theta-1)*(theta-2)/2,
                   -(theta+1)*theta*(theta-2)/2,(theta+1)*theta*(theta-1)/6)
                p=sum(wj*(D(90)*D(x)*h).exp() for wj,x in zip(w,(-1,0,1,2)))
                truth=(D(90)*theta*h).exp()
                self.assertLess(abs(p/truth-1),D(rational.numerator)/D(rational.denominator))

if __name__=="__main__":unittest.main()

