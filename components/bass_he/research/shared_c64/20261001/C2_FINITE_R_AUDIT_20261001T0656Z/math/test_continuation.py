"""Geometry and manufactured finite-spline checks; no eigensolves."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
from numpy.polynomial import Polynomial
from scipy.interpolate import BSpline

from continuation import (charge_center_positions, prolate_to_charge_center,
                          charge_center_to_prolate, values_at_charge_center,
                          pair_overlap, refinement_audit)


def manufactured_state(m=0, R=2.0):
    degree = 3

    def axis(edges, radial):
        edges = np.asarray(edges, float)
        knots = np.r_[np.repeat(edges[0], degree), edges,
                      np.repeat(edges[-1], degree)]
        n = len(knots)-degree-1
        basis = BSpline(knots, np.eye(n)[:, :n-int(radial)], degree,
                        extrapolate=False)
        greville = np.array([np.mean(knots[i+1:i+degree+1]) for i in range(n)])
        coefficients = ((edges[-1]-greville)[:-1] if radial else np.ones(n))
        return SimpleNamespace(edges=edges, basis=basis), coefficients

    radial, cr = axis([1, 1.5, 2, 3], True)
    angular, ca = axis([-1, -0.2, 0.7, 1], False)
    x = Polynomial([0, 1])
    f = (3-x)**2 * (x*x-1)**m
    g = (1-x*x)**m

    def integral(poly, lo, hi):
        a = poly.integ()
        return a(hi)-a(lo)

    norm2 = R**3/8 * (integral(f*x*x, 1, 3)*integral(g, -1, 1)
                      - integral(f, 1, 3)*integral(g*x*x, -1, 1))
    return SimpleNamespace(R=R, ZA=1.0, ZB=2.0, m=m, xi_max=3.0,
                           normalization=norm2**-0.5,
                           radial_coefficients=cr, angular_coefficients=ca,
                           _radial=radial, _angular=angular)


class ContinuationGeometryTests(unittest.TestCase):
    def test_round_trip_and_origin(self):
        self.assertEqual(charge_center_positions(3, 1, 2), (-2, 1, -0.5))
        rng = np.random.default_rng(314159)
        xi, eta = 1+20*rng.random(1000), 2*rng.random(1000)-1
        for R in (0.25, 2, 16):
            rho, z = prolate_to_charge_center(xi, eta, R, 1, 2)
            xx, yy = charge_center_to_prolate(rho, z, R, 1, 2)
            np.testing.assert_allclose(xx, xi, rtol=3e-15, atol=2e-14)
            np.testing.assert_allclose(yy, eta, rtol=0, atol=3e-14)
            # The *same* O point represented at another nuclear separation.
            xx, yy = charge_center_to_prolate(rho, z, R*1.5, 1, 2)
            rr, zz = prolate_to_charge_center(xx, yy, R*1.5, 1, 2)
            np.testing.assert_allclose(rr, rho, rtol=3e-12, atol=5e-12)
            np.testing.assert_allclose(zz, z, rtol=3e-12, atol=5e-12)

    def test_exact_polynomial_self_norm(self):
        for m in (0, 1):
            state = manufactured_state(m=m)
            result = pair_overlap(state, state, 10)
            self.assertLess(result["max_self_norm_error_abs"], 2e-13)
            self.assertLess(abs(result["overlap"]-1), 2e-13)
            self.assertLess(result["directional_difference_abs"], 1e-15)

    def test_zero_extension(self):
        state = manufactured_state()
        self.assertEqual(float(values_at_charge_center(state, 100, 100)), 0.0)

    def test_phase_gate(self):
        state = manufactured_state(m=1)
        flipped = copy.deepcopy(state)
        flipped.radial_coefficients *= -1
        low = pair_overlap(state, flipped, 8)
        high = pair_overlap(state, flipped, 12)
        audit = refinement_audit(low, high)
        self.assertTrue(audit["transport_pass"])
        self.assertEqual(audit["phase_factor"], -1)

    def test_sector_rejection(self):
        with self.assertRaises(ValueError):
            pair_overlap(manufactured_state(m=0), manufactured_state(m=1), 8)

    def test_fail_closed_transport_gate(self):
        state = manufactured_state()
        low = pair_overlap(state, state, 8)
        high = pair_overlap(state, state, 12)
        high["normalized_overlap"] = low["normalized_overlap"] = 0.49
        audit = refinement_audit(low, high)
        self.assertFalse(audit["transport_pass"])
        self.assertIsNone(audit["phase_factor"])
        high["normalized_overlap"] = low["normalized_overlap"] = 1
        high["directional_difference_abs"] = 1e-4
        self.assertFalse(refinement_audit(low, high)["quadrature_pass"])


if __name__ == "__main__":
    unittest.main()
