"""Small independent controls for the conditional nuclear extension."""
import math
import unittest

import numpy as np
from scipy import constants as C
from scipy.linalg import expm

import nuclear_network as network
import postprocess as dd


class NuclearNetworkTests(unittest.TestCase):
    def test_source_labels_and_conservation(self):
        channels = network.channels()
        self.assertEqual(len(channels), 13)
        self.assertEqual(tuple(sorted(i for c in channels for i in c.ids)),
                         tuple(range(4, 20)))
        for c in channels:
            delta = c.vector()
            self.assertEqual(int(network.A @ delta), 0)
            self.assertEqual(int(network.Z @ delta),
                             1 if c.kind == "beta_minus" else 0)

    def test_generic_gamow_matches_independent_dd_kernel(self):
        mass = C.physical_constants["deuteron mass"][0]
        for t in (100., 1000., 10000.):
            actual = network.log_constant_s_rate(t, dd.SP, mass, mass, 1, 1)
            expected = dd.log_maxwell_kernel(t)[0] + dd.LOG_SP
            self.assertLess(abs(actual-expected), 1e-10)
        self.assertTrue(math.isfinite(actual))

    def test_structural_zero_and_finite_underflow_are_distinct(self):
        flux = network.log_binary_events(np.array([-1000., -1000.]),
                                         np.ones(2), np.array([0., 1e-5]),
                                         np.array([1e-5, 1e-5]), True)
        self.assertEqual(network.report_log_value(float(flux[0]))["state"],
                         "structural_zero")
        self.assertEqual(network.report_log_value(float(flux[1]))["state"],
                         "finite_underflow")
        self.assertEqual(network.report_log_value(float(flux[1]))["linear"], None)
        self.assertAlmostEqual(flux[1], -1000+2*math.log(1e-5)-math.log(2))

    def test_log_integral_and_near_equal_signed_difference(self):
        t = np.array([0., 1., 2.])
        r = np.full(3, -1000.)
        c = network.cumulative_log_events(t, r)
        self.assertAlmostEqual(c[-1], -1000.+math.log(2.))
        self.assertEqual(network.report_log_value(float(c[-1]))["state"],
                         "finite_underflow")
        sign, magnitude = network.signed_log_difference(0., -1e-12)
        self.assertEqual(sign, 1)
        self.assertAlmostEqual(math.exp(magnitude), 1e-12, delta=1e-16)
        steep = network.cumulative_log_events(np.array([0., 1.]),
                                                np.array([-1e6-100., -1e6]))
        self.assertAlmostEqual(float(steep[-1]), -1e6-math.log(100.), places=10)

    def test_coupled_constant_source_against_matrix_exponential(self):
        m = np.array([[-.2, .03], [.07, -.6]])
        s = np.array([2e-12, 5e-13])
        time = np.array([0., 1.3, 7.2])
        actual = np.exp(network.propagate_fast(time, np.repeat(m[None], 3, axis=0),
                                                np.repeat(np.log(s)[None], 3, axis=0)))
        exact = np.stack([np.linalg.solve(m, (expm(m*t)-np.eye(2))@s)
                          for t in time])
        np.testing.assert_allclose(actual[1:], exact[1:], rtol=1e-11, atol=0)

    def test_fast_stock_not_overwritten_by_cancelling_event_reconstruction(self):
        family = {"id": "t_beta", "dossier_ids": [9], "reactants": {"T": 1},
                  "products": {"He3": 1}, "kind": "beta_minus",
                  "reverse": "not_in_this_lowT_neutrino_free_model"}
        # Deliberately inconsistent independent event quadrature: its T
        # delta is negative, but the positive propagated fast state is known.
        cumulative = np.full((2, 1, 2), -math.inf)
        cumulative[-1, 0, 0] = math.log(2.)
        fast = np.full((2, 2), -math.inf)
        fast[-1, 0] = math.log(1.)
        ledger = network.endpoint_ledger({"log_cumulative": cumulative,
                                          "log_fast": fast}, [family],
                                         {"t_beta": 1e-15},
                                         np.zeros(len(network.SPECIES)))
        tritium = next(c for c in ledger["changes"] if c["species"] == "T")
        self.assertEqual(tritium["net_sign"], 1)
        self.assertAlmostEqual(tritium["net_abs"]["linear"], 1.)
        self.assertEqual(tritium["event_reconstruction_net"]["sign"], -1)


if __name__ == "__main__":
    unittest.main()
