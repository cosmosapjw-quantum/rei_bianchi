"""New reference-discretization checks; not a C2 R-grid audit."""
import json
from pathlib import Path
import time
import unittest

import numpy as np
from numpy.polynomial.legendre import leggauss
from partialwave import solve, angular, direct_angular_coupling


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = solve(0., m=0, lmax=2, elements=40, degree=4, rmax=16.)
        cls.b = solve(0., m=1, lmax=2, elements=40, degree=4, rmax=16.)

    def test_united_atom_energies(self):
        self.assertLess(abs(self.g.energy+4.5), 5e-7)
        self.assertLess(abs(self.b.energy+1.125), 5e-7)
        # Ritz energies should be upper bounds up to quadrature/roundoff.
        self.assertGreater(self.g.energy, -4.5-1e-9)
        self.assertGreater(self.b.energy, -1.125-1e-9)

    def test_normalization_and_ritz_residual(self):
        for state in (self.g, self.b):
            self.assertLess(abs(state.mass_norm-1), 2e-13)
            self.assertLess(state.residual, 2e-10)
            self.assertLess(state.metadata["hamiltonian_relative_skew"], 1e-13)

    def test_united_atom_wavefunctions(self):
        r = np.array([0.05, 0.1, 0.3, 0.7, 1., 2.])
        # u_1s=2 Z^(3/2) r exp(-Zr); u_2p=Z^(5/2) r² exp(-Zr/2)/(2sqrt6).
        targetg = 2*3**1.5*r*np.exp(-3*r)
        targetb = 3**2.5/(2*np.sqrt(6))*r*r*np.exp(-1.5*r)
        np.testing.assert_allclose(self.g.radial(r)[0], targetg, atol=4e-5, rtol=0)
        np.testing.assert_allclose(self.b.radial(r)[0], targetb, atol=4e-5, rtol=0)
        self.assertGreater(self.g.phase_probe, 0.)
        self.assertGreater(self.b.phase_probe, 0.)

    def test_angular_orthonormality_and_axis(self):
        eta, w = leggauss(24)
        for m in (0, 1):
            A = np.stack([angular(l, m, eta) for l in range(m, 6)])
            np.testing.assert_allclose((A*w)@A.T, np.eye(len(A)), atol=2e-14, rtol=0)
        np.testing.assert_array_equal(angular(1, 1, np.array([-1., 1.])), 0.)
        self.assertGreater(float(angular(1, 1, 0.)), 0.)

    def test_united_atom_angular_selection_zero(self):
        self.assertLess(abs(direct_angular_coupling(self.g, self.b)), 1e-10)

    def test_failure_contract(self):
        for kw in ({"R": -1}, {"R": np.nan}, {"R": 1, "ZA": 0},
                   {"R": 1, "m": 2}, {"R": 1, "m": 1, "lmax": 0},
                   {"R": 1, "rmax": 0.1}, {"R": 1, "degree": 1}):
            with self.assertRaises(ValueError):
                solve(**kw)
        with self.assertRaises(ValueError):
            self.g.evaluate(0., 0.)
        with self.assertRaises(ValueError):
            self.g.evaluate(1., 1.)
        with self.assertRaises(ValueError):
            direct_angular_coupling(self.b, self.g)


if __name__ == "__main__":
    start = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    states = [ReferenceTests.g, ReferenceTests.b]
    payload = {"status": "PASS" if result.wasSuccessful() else "FAIL",
               "tests_run": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "elapsed_seconds": time.perf_counter()-start,
               "scope": "new hp-FEM reference analytic/invariant/failure checks only",
               "states": [{"m": s.m, "energy": s.energy, "residual": s.residual,
                           "mass_norm": s.mass_norm, "metadata": s.metadata} for s in states],
               "UA_direct_L_over_minus_i_hbar": direct_angular_coupling(*states),
               "C2_grid": "NOT_RUN", "production_accuracy": "NOT_CERTIFIED"}
    out = Path(__file__).resolve().parents[1]/"evidence"/"REFERENCE_FOCUSED_TESTS.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload, indent=2)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
