"""Exact synthetic transcription checks; proofs are in T4, no HH data is loaded."""
from fractions import Fraction as F
from math import factorial
import unittest


def poch(a, n):
    out = F(1)
    for j in range(n):
        out *= a + j
    return out


def term(a, b, R, n):
    return abs(poch(a, n)) * R**n / (poch(b, n) * factorial(n))


class ConstructiveChecks(unittest.TestCase):
    def test_hypergeometric_geometric_tail_domination(self):
        # Nonterminating derivative parameters, including large |z|.
        for a, b, R in [(F(-1,2), F(3,2), F(20)), (F(-7,2), F(3,2), F(3)),
                        (F(1,2), F(5,2), F(11)), (F(3,2), F(7,2), F(1,8))]:
            N = 0
            while R*(1+abs(a))/(b+N) > F(1,2):
                N += 1
            q = R*(1+abs(a))/(b+N)
            first = term(a,b,R,N+1)
            partial = F(0)
            for k in range(1,31):
                t = term(a,b,R,N+k)
                self.assertLessEqual(t, first*q**(k-1))
                partial += t
            self.assertLessEqual(partial, first/(1-q))

    def test_terminating_parameters_need_no_ratio_through_zero(self):
        for m in range(5):
            self.assertNotEqual(poch(F(-m),m),0)
            self.assertEqual(poch(F(-m),m+1),0)
            self.assertEqual(term(F(-m),F(3,2),F(7),m+2),0)

    def test_half_integer_gamma_majorant_effective_decay(self):
        # P_m(x)=sum coeff[e] x^(e/2). x=4^n makes every term rational.
        poly = {-1:F(1)}
        for m in range(7):
            M = m+2
            def bound(n):
                return factorial(M)*sum(c*F(2)**(n*e) for e,c in poly.items()) / F(4)**(n*M)
            seq = [bound(n) for n in range(1,9)]
            self.assertTrue(all(y < x for x,y in zip(seq,seq[1:])))
            self.assertTrue(all(F(e,2)-M < 0 for e in poly))
            poly = {e:c*F(2*m+1,2) for e,c in poly.items()}
            poly[2*m+1] = poly.get(2*m+1,F(0))+1

    def test_shrinking_intervals_do_not_decide_equality(self):
        for n in range(1,32):
            lo, hi = -F(1,2**n), F(1,2**n)
            self.assertLess(lo,0)
            self.assertGreater(hi,0)
            self.assertFalse(lo>=0)
            self.assertFalse(hi<0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
