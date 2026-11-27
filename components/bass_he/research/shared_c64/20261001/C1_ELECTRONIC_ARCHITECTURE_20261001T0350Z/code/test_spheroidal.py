"""New C1 checks only: two single-center states and guarded API boundaries."""
import json
import unittest
from dataclasses import replace

import numpy as np
from spheroidal import solve, SpheroidalConfig


class SingleCenterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.states = {m: solve(2.0, ZA=0, ZB=2, m=m) for m in (0, 1)}

    def test_single_center_energies_and_wavefunctions(self):
        xi = np.array([1.2, 1.6, 2.5, 4.0])
        eta = np.array([-0.7, 0.1, 0.6, 0.9])
        rho = np.sqrt((xi**2-1)*(1-eta**2))  # R/2=1
        rB = xi-eta
        for m, state in self.states.items():
            with self.subTest(m=m):
                self.assertLess(abs(state.energy + 2/(m+1)**2), 2e-8)
                value, dx, de = state.evaluate(xi, eta)
                if m == 0:
                    exact = 4*np.exp(-2*rB)
                    ex_dx, ex_de = -2*exact, 2*exact
                else:
                    exact = rho*np.exp(-rB)
                    ex_dx = (xi/(xi**2-1)-1)*exact
                    ex_de = (-eta/(1-eta**2)+1)*exact
                np.testing.assert_allclose(value, exact, atol=2e-8, rtol=2e-7)
                np.testing.assert_allclose(dx, ex_dx, atol=1e-7, rtol=2e-6)
                np.testing.assert_allclose(de, ex_de, atol=1e-7, rtol=2e-6)

    def test_norm_phase_and_discrete_residuals(self):
        for m, state in self.states.items():
            with self.subTest(m=m):
                xi, eta = np.meshgrid(state._radial.nodes,
                                      state._angular.nodes, indexing="ij")
                weights = np.outer(state._radial.weights, state._angular.weights)
                values, _, _ = state.evaluate(xi, eta)
                norm = np.sum(weights*(xi**2-eta**2)*values**2)  # R^3/8=1
                self.assertAlmostEqual(norm, 1.0, places=11)
                self.assertGreater(float(state.evaluate(1.5, 0.2)[0]), 0)
                self.assertLess(state.root_derivative, 0)
                self.assertLess(state.residuals["matching_absolute"], 2e-9)
                self.assertLess(state.residuals["radial_discrete_relative"], 1e-12)
                self.assertLess(state.residuals["angular_discrete_relative"], 1e-12)


class InputTests(unittest.TestCase):
    def test_rejects_invalid_inputs(self):
        for kwargs in ({"R": 0}, {"R": np.nan}, {"R": 2, "ZA": -1},
                       {"R": 2, "ZA": 0, "ZB": 0}, {"R": 2, "m": -1},
                       {"R": 2, "m": 1.0}, {"R": 2, "m": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                solve(**kwargs)

    def test_rejects_underintegrated_or_invalid_configuration(self):
        for changes in ({"quadrature_order": 5}, {"radial_extent": 0},
                        {"radial_elements": 1.5}, {"degree": 1}):
            config = replace(SpheroidalConfig(), **changes)
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                solve(2.0, config=config)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({"states": {str(m): s.metadata() for m, s in
                                  getattr(SingleCenterTests, "states", {}).items()},
                      "tests_run": result.testsRun, "pass": result.wasSuccessful()},
                     indent=2))
    raise SystemExit(not result.wasSuccessful())
