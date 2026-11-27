"""C1b changed-coordinate, direct-operator and Ritz-gap seams only."""
import json
from pathlib import Path
from types import SimpleNamespace
import time
import unittest

import numpy as np
from partialwave_centered import (solve, nuclear_positions, radial_mesh,
    projected_cartesian, direct_observables, direct_angular_coupling)


def analytic_atomic_pair(Z=3.):
    """Independent analytic hydrogenic radial functions, not FEM eigenstates."""
    shared = dict(R=2., ZA=1., ZB=2., degree=4,
                  metadata={"origin_center": "B", "origin_shift_center_to_O": 2/3})
    def ug(r, derivative=False):
        r = np.asarray(r)
        return (2*Z**1.5*np.exp(-Z*r)*((1-Z*r) if derivative else r))[None, :]
    def ub(r, derivative=False):
        r = np.asarray(r)
        return (Z**2.5/(2*np.sqrt(6))*np.exp(-Z*r/2)*
                ((2*r-Z*r*r/2) if derivative else r*r))[None, :]
    return (SimpleNamespace(**shared, m=0, ls=np.array([0]), radial=ug,
                            boundaries=np.array([0., 1., 3., 24.])),
            SimpleNamespace(**shared, m=1, ls=np.array([1]), radial=ub,
                            boundaries=np.array([0., 2., 4., 24.])))


class CenteredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One new atomic solve exercises the two-root interface at a B origin.
        # ZA=0 places the only nucleus exactly at B even though R is nonzero.
        cls.atom = solve(2., ZA=0., ZB=2., m=0, lmax=0, center="B",
                         elements=40, rmax=20., degree=4, nroots=2)

    def test_atomic_ritz_gap_and_origin(self):
        s = self.atom
        np.testing.assert_allclose(s.metadata["ritz_eigenvalues"], [-2., -.5], atol=4e-7, rtol=0)
        self.assertLess(abs(s.metadata["discrete_sector_gap"]-1.5), 4e-7)
        self.assertTrue(all(r < 1e-9 for r in s.metadata["ritz_residuals"]))
        self.assertEqual(s.metadata["origin_center"], "B")
        self.assertIn("not continuum", s.metadata["gap_scope"])

    def test_atomic_direct_cartesian_and_translation(self):
        Z = 3.
        g, b = analytic_atomic_pair(Z)
        obs = direct_observables(g, b, quadrature=40)
        d = 128*np.sqrt(2)/(243*Z)
        p = 3*Z*Z/8*d
        self.assertLess(abs(obs["dipole_x"]-d), 2e-13)
        self.assertLess(abs(obs["p_x_over_minus_i_hbar"]-p), 2e-13)
        self.assertEqual(obs["L_center_over_minus_i_hbar"], 0.)
        self.assertLess(abs(obs["L_O_over_minus_i_hbar"]-2*p/3), 2e-13)

    def test_direct_same_l_generator(self):
        g, b = analytic_atomic_pair()
        g.ls = np.array([1])
        g.radial = b.radial
        self.assertLess(abs(direct_angular_coupling(g, b, quadrature=40)-1), 2e-13)

    def test_tail_partition_preserves_inner_cells(self):
        mesh = radial_mesh(2., 1., 2., 24., 56, center="B")
        extended = np.r_[mesh, 26., 29., 32.]
        got = radial_mesh(2., 1., 2., 32., 56, center="B", boundaries=extended)
        np.testing.assert_array_equal(got[:len(mesh)], mesh)
        np.testing.assert_array_equal(nuclear_positions(2., 1., 2., "B"), [-2., 0.])
        np.testing.assert_allclose(nuclear_positions(2., 1., 2., "O"), [-4/3, 2/3])
        with self.assertRaises(ValueError):
            radial_mesh(2., 1., 2., 24., 56, center="B", boundaries=[0., 1., 24.])
        with self.assertRaises(ValueError):
            radial_mesh(2., 1., 2., 24., 56, center="B", boundaries=[0., 2., 2., 24.])

    def test_changed_interface_failures(self):
        for kw in ({"center": "C"}, {"nroots": 3}, {"nroots": True},
                   {"ZA": 0., "ZB": 0.}, {"boundaries": [0., 2., 10.]}):
            with self.assertRaises(ValueError):
                solve(2., **kw)
        g, b = analytic_atomic_pair()
        b.metadata = {**b.metadata, "origin_center": "O"}
        with self.assertRaises(ValueError):
            projected_cartesian(g, b)


if __name__ == "__main__":
    start = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CenteredTests))
    payload = {"status": "PASS" if result.wasSuccessful() else "FAIL",
               "tests_run": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "elapsed_seconds": time.perf_counter()-start,
               "scope": "changed origin/operator/mesh/gap seams; no H/He sequence",
               "atomic_state": {"energy": CenteredTests.atom.energy,
                   "residual": CenteredTests.atom.residual,
                   "metadata": CenteredTests.atom.metadata},
               "analytic_direct": direct_observables(*analytic_atomic_pair(), quadrature=40),
               "continuum_gap_certified": False}
    out = Path(__file__).resolve().parents[1]/"evidence"/"CENTERED_UNIT_RESULT.json"
    out.write_text(json.dumps(payload, indent=2)+"\n")
    raise SystemExit(0 if result.wasSuccessful() else 1)
