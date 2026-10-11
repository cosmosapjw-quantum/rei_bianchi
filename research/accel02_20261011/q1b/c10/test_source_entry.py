"""New source time-map fixtures; no previous source history is replayed."""
from decimal import Decimal, localcontext
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_entry import integrate_source, advance_source


class ExpandingBirth:
    def __init__(self, A=2., a=5., lam=.3):
        self.A, self.a, self.lam = A, a, lam

    def source(self, t):
        R = math.exp(-self.lam*t)
        N = np.array([[self.A*self.lam*t]])
        Q = np.array([[self.A*self.a*math.expm1(self.lam*t)]])
        return dict(N=N, Q_eV=Q, U_eV=R*Q, R=np.array([R]))


def analytic_birth(A, a, lam, t, kappa=0.):
    # High precision, independently integrated exponential source survival.
    with localcontext() as c:
        c.prec = 70
        A, a, l, t, k = [Decimal(str(v)) for v in (A, a, lam, t, kappa)]
        if not k:
            N = A*l*t*t/2
            Q = A*a*((l*t).exp()-1-l*t)/l
        else:
            N = A*l*(k*t-1+(-k*t).exp())/(k*k)
            Q = A*a*(((l*t).exp()-(-k*t).exp())/(k+l)-(1-(-k*t).exp())/k)
        return float(N), float(Q)


class TestSourceEntry(unittest.TestCase):
    def test_expanding_birth_actual_integrals(self):
        source = ExpandingBirth()
        for h in (.1, .01, .001):
            r = integrate_source(source, 0., h)
            n, q = analytic_birth(2., 5., .3, h)
            self.assertLess(abs(r['dN'][0,0]/n-1), 1e-12)
            self.assertLess(abs(r['dQ'][0,0]/q-1), 1e-12)
            out = advance_source(np.zeros((1,1)), np.zeros((1,1)), r)
            width = 5.*math.expm1(.3*h)
            fraction = (out['Q_eV'][0,0]/out['N'][0,0]-5.)/width
            # Independent expansion gives 1/3 - lambda*h/12 + O(h^2).
            self.assertLess(abs(fraction-1/3), .3*h/10)
            self.assertLess(out['diagnostics']['pairing_max_relative'], 1e-12)

    def test_zero_source_and_initial_radiation(self):
        source = ExpandingBirth(A=0.)
        r = integrate_source(source, 0., 1.)
        for key in ('dN','dQ','injected_energy_eV','radiation_source_work_eV'):
            self.assertTrue(np.array_equal(r[key], [[0.]]))
        out = advance_source(np.array([[3.]]), np.array([[17.]]), r)
        self.assertEqual(out['N'][0,0], 3.)
        self.assertEqual(out['U_eV'][0,0], 17.*math.exp(-.3))
        self.assertLess(out['diagnostics']['pairing_max_relative'], 1e-12)

    def test_explicit_event_split(self):
        class Jump:
            def source(self, t):
                N = np.array([[1. if t < .314159 else 9.]])
                return dict(N=N,Q_eV=7*N,U_eV=7*N,R=np.array([1.]))
        r = integrate_source(Jump(), 0., 1., event_times=(.314159,))
        self.assertLess(abs(r['dN'][0,0]-(.314159+9*(1-.314159))), 1e-13)
        with self.assertRaisesRegex(FloatingPointError, 'TIME_QUADRATURE'):
            integrate_source(Jump(), 0., 1.)

    def test_invalid_pair_and_state_refused(self):
        class Bad(ExpandingBirth):
            def source(self, t):
                r = super().source(t)
                r['U_eV'] += 1
                return r
        with self.assertRaisesRegex(ValueError, 'MOMENT_PAIR'):
            integrate_source(Bad(), 0., 1.)
        r = integrate_source(ExpandingBirth(), 0., 1.)
        with self.assertRaisesRegex(ValueError, 'INITIAL'):
            advance_source(np.array([[0.]]),np.array([[1.]]),r)

    def test_grey_birth_first_order_at_common_endpoint(self):
        exact = np.array(analytic_birth(2.,5.,.3,1.,kappa=1.7))
        errors = []
        for steps in (64,128,256):
            N, U = np.zeros((1,1)), np.zeros((1,1))
            h = 1./steps
            for j in range(steps):
                r = integrate_source(ExpandingBirth(), j*h, (j+1)*h)
                v = advance_source(N,U,r)
                # Independent grey implicit sink; no production absorption wrapper.
                N, U = v['N']/(1+1.7*h), v['U_eV']/(1+1.7*h)
            errors.append(np.max(np.abs(np.array([N.item(), U.item()/math.exp(-.3)])/exact-1)))
        ratios = np.array(errors[:-1])/errors[1:]
        self.assertTrue(np.all((ratios > 1.97) & (ratios < 2.03)), (errors,ratios))


if __name__ == '__main__':
    unittest.main(verbosity=2)
