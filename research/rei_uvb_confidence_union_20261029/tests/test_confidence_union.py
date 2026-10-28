"""New source/analytic oracles; no predecessor suite or box-corner replay."""
import copy
from fractions import Fraction as F
import math
import unittest

from confidence_union import (ATOL, RTOL, BLIND, BLIND_SHA, Model, dot, load_source,
                              mm, mv, numeric, quantiles, transpose, verify_blob)

EVIDENCE = {}
SOURCE_MODEL = None


def toy(d=None, v=None, lower=None, upper=None):
    return {"z": [2.6, 3.6, 4.6], "observed_dex": d or [0, 0, 0],
            "template_dex": [0, 0, 0], "covariance_dex_squared": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            "eos_response_dex": v or [0, 0, 0], "eos_theta_bounds": [-1, 1],
            "jeans_smoothing_lower_dex": lower or [0, 0, 0],
            "jeans_smoothing_upper_dex": upper or [0, 0, 0]}


class ScientificTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global SOURCE_MODEL
        SOURCE_MODEL = Model(load_source())
        cls.source = SOURCE_MODEL

    def close(self, actual, expected):
        actual, expected = float(actual), float(expected)
        self.assertTrue(math.isfinite(actual) and math.isfinite(expected))
        self.assertLessEqual(abs(actual - expected), ATOL + RTOL * abs(expected), (actual, expected))

    def test_source_gls_algebra_and_direct_nested_residuals(self):
        m = self.source
        self.assertEqual(mm(m.A, m.X), [[1, 0], [0, 1]])
        self.assertEqual(mm(mm(m.A, m.C), transpose(m.A)), m.V)
        direct = []
        witnesses = [m.nuisance_witness(s) for s in ([1, 0], [0, -1], [1, -2])]
        witnesses.append({"theta": F(1, 3), "j": m.jc})
        for witness in witnesses:
            theta, j = witness["theta"], witness["j"]
            r = m.response(theta, j)
            q0, q2, a = m.nested(theta, j)
            residual = [ri - pi for ri, pi in zip(r, mv(m.X, a))]
            self.assertEqual(mv(transpose(m.X), m.factor.solve(residual)), [0, 0])
            expected = a[1] ** 2 / m.V[1][1]
            self.assertEqual(q0 - q2, expected)
            # A displaced coefficient is a direct, independent quadratic completion check.
            displacement = [F(2, 7), F(-3, 11)]
            shifted = [ai + di for ai, di in zip(a, displacement)]
            self.assertEqual(m.q_residual(r, shifted) - q2, dot(displacement, mv(m.H, displacement)))
            direct.append({"theta": theta, "Q_intercept": q0, "Q_affine": q2,
                           "difference": q0 - q2, "kappa_squared_over_Vkk": expected})
        # Independently residualize x against the intercept; T must be 1/Vkk.
        w1, wx = m.factor.solve([F(1)] * m.n), m.factor.solve(m.x)
        t = dot(m.x, wx) - dot(m.x, w1) ** 2 / sum(w1)
        self.assertEqual(t, 1 / m.V[1][1])
        EVIDENCE["source_algebra"] = numeric({"AX_minus_I_max": 0, "ACAT_minus_V_max": 0,
            "normal_equation_and_completion_residual_max": 0, "slope_precision_T": t,
            "direct_nested_residuals": direct, "arithmetic": "exact rational decimal-input interpretation"})

    def test_source_support_and_ellipse_witnesses(self):
        m = self.source
        record = []
        q = quantiles()["joint2_95"]["q"]
        for s in ([1, 0], [-1, 0], [0, 1], [0, -1], [1, -2], [-1, 2]):
            w = m.nuisance_witness(s)
            self.assertTrue(-1 <= w["theta"] <= 1)
            self.assertTrue(all(lo <= j <= hi for lo, j, hi in zip(m.lower, w["j"], m.upper)))
            # Form the response afresh, then evaluate A*r, rather than using center+G.
            attained = dot(s, m.fit(w["theta"], w["j"]))
            self.assertEqual(attained, m.support(s))
            e = m.confidence_witness(s, q)
            delta = e["ellipsoid_displacement"]
            norm = dot(delta, mv(m.H, delta))
            self.close(norm, q)
            self.close(dot(s, e["endpoint"]), e["union_support"])
            self.close(e["union_support"] - float(attained), math.sqrt(q * float(dot(s, mv(m.V, s)))))
            record.append({"direction": s, "support_attainment_residual": 0,
                           "ellipse_quadratic_radius": float(norm), "q": q,
                           "union_attainment_residual": float(dot(s, e["endpoint"])) - e["union_support"]})
        for k in range(2):
            s = [int(i == k) for i in range(2)]
            low, high = m.deterministic_intervals()[k]
            self.assertEqual(high, m.support(s))
            self.assertEqual(low, -m.support([-v for v in s]))
            p = m.projections(q)[k]
            self.close(p[0], low - math.sqrt(q * float(m.V[k][k])))
            self.close(p[1], high + math.sqrt(q * float(m.V[k][k])))
        EVIDENCE["source_support_and_ellipse"] = record

    def test_source_delta_q_range_witnesses(self):
        m = self.source
        out = m.delta_q_range()
        for index, key in enumerate(("minimum_nuisance", "maximum_nuisance")):
            w = out[key]
            q0, q2, _ = m.nested(w["theta"], w["j"])
            self.assertEqual(q0 - q2, out["range"][index])
        lo, hi = m.deterministic_intervals()[1]
        expected_min = 0 if lo <= 0 <= hi else min(lo * lo, hi * hi) / m.V[1][1]
        self.assertEqual(out["range"], [expected_min, max(lo * lo, hi * hi) / m.V[1][1]])
        EVIDENCE["source_deltaQ"] = numeric(out)

    def test_tiny_analytic_gls_and_fixed_nuisance(self):
        m = Model(toy(d=[-1, 2, 4]))
        self.assertEqual(m.A, [[F(1, 3)] * 3, [F(-1, 2), 0, F(1, 2)]])
        self.assertEqual(m.V, [[F(1, 3), 0], [0, F(1, 2)]])
        self.assertEqual(m.a0, [F(5, 3), F(5, 2)])
        q0, q2, _ = m.nested(0, [0, 0, 0])
        self.assertEqual(q0, F(38, 3))
        self.assertEqual(q2, F(1, 6))
        self.assertEqual(q0 - q2, F(25, 2))
        self.assertTrue(all(g == 0 for row in m.G for g in row))
        q = quantiles()["joint2_95"]["q"]
        for s in ([1, 2], [-3, 1]):
            e = m.confidence_witness(s, q)
            self.close(e["union_support"], dot(s, m.a0) + math.sqrt(q * float(dot(s, mv(m.V, s)))))
            self.close(dot(e["ellipsoid_displacement"], mv(m.H, e["ellipsoid_displacement"])), q)
        # A second tiny analytic case has exactly two observations and no residual df.
        t = toy(d=[-1, 0, 1])
        for key in ("z", "observed_dex", "template_dex", "eos_response_dex", "jeans_smoothing_lower_dex", "jeans_smoothing_upper_dex"):
            t[key] = [t[key][0], t[key][2]]
        t["covariance_dex_squared"] = [[1, 0], [0, 1]]
        m2 = Model(t)
        self.assertEqual(m2.V, [[F(1, 2), 0], [0, F(1, 2)]])
        self.assertEqual(m2.a0, [0, 1])
        EVIDENCE["toy_analytic_fixed_nuisance"] = {"three_row_A_V_Q": "exact analytic equalities PASS",
            "two_row_no_residual_df_V": numeric(m2.V), "provenance": "synthetic; not source"}

    def test_zero_crossing_minimum_is_interior(self):
        m = Model(toy(v=[-1, 0, 1]))
        self.assertEqual(m.deterministic_intervals()[1], [-1, 1])
        out = m.delta_q_range()
        self.assertEqual(out["range"], [0, 2])
        self.assertEqual(out["minimum_nuisance"]["theta"], 0)
        self.assertEqual(out["minimum_nuisance"]["fit"][1], 0)
        for theta in (-1, 1):
            q0, q2, _ = m.nested(theta, [0, 0, 0])
            self.assertEqual(q0 - q2, 2)
        EVIDENCE["toy_interior_deltaQ_minimum"] = numeric(out)

    def test_positive_deterministic_statistical_crossing_counterexample(self):
        m = Model(toy(d=[-.1, 0, .1]))
        self.assertEqual(m.deterministic_intervals()[1], [F(1, 10), F(1, 10)])
        for label, item in quantiles().items():
            lo, hi = m.projections(item["q"])[1]
            self.assertLess(lo, 0)
            self.assertGreater(hi, 0)
        EVIDENCE["toy_deterministic_positive_statistical_crossing"] = {
            "deterministic_kappa": [.1, .1], "Vkk": .5,
            "scalar95": m.projections(quantiles()["scalar95"]["q"])[1],
            "joint2_95": m.projections(quantiles()["joint2_95"]["q"])[1],
            "provenance": "synthetic fixed nuisance counterexample; not source"}

    def test_quantile_labels_and_zero_limits(self):
        qs = quantiles()
        self.assertEqual(qs["scalar95"]["degrees_of_freedom"], 1)
        self.assertEqual(qs["joint2_95"]["degrees_of_freedom"], 2)
        # Independent tabulated controls, not a duplicate formula oracle.
        self.close(qs["scalar95"]["q"], 3.841458820694124)
        self.close(qs["joint2_95"]["q"], 5.991464547107982)
        m = self.source
        for s in ([1, 0], [1, -2], [0, 0]):
            e = m.confidence_witness(s, 0)
            self.assertEqual(e["ellipsoid_displacement"], [0, 0])
            self.close(e["union_support"], m.support(s))
        self.assertEqual(m.confidence_witness([0, 0], qs["joint2_95"]["q"])["union_support"], 0)
        self.assertEqual(m.projections(0), numeric(m.deterministic_intervals()))
        EVIDENCE["quantile_and_zero_controls"] = {"quantiles": qs, "q_zero": "PASS", "zero_direction": "PASS"}

    def test_invalid_inputs_and_immutable_source_mismatch(self):
        for q in (-1, float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(ValueError):
                self.source.confidence_witness([1, 0], q)
        cases = []
        t = toy(); t["covariance_dex_squared"][0][0] = -1; cases.append(t)
        t = toy(); t["covariance_dex_squared"][0][1] = .1; cases.append(t)
        t = toy(); t["z"] = [3.6, 3.6, 3.6]; cases.append(t)
        t = toy(); t["jeans_smoothing_lower_dex"][0] = 1; cases.append(t)
        t = toy(); t["observed_dex"][0] = float("nan"); cases.append(t)
        t = toy(); t["observed_dex"] = [0]; cases.append(t)
        t = toy(); t["covariance_dex_squared"] = [[1]]; cases.append(t)
        t = toy(); t["eos_theta_bounds"] = [0, 1]; cases.append(t)
        for t in cases:
            with self.assertRaises(ValueError):
                Model(copy.deepcopy(t))
        verify_blob(BLIND.read_bytes(), BLIND_SHA)
        with self.assertRaisesRegex(ValueError, "BYTE_IDENTITY_MISMATCH"):
            verify_blob(BLIND.read_bytes() + b" ", BLIND_SHA)
        EVIDENCE["rejection_controls"] = {"invalid_q_C_rank_bounds_finiteness_dimensions": "PASS",
                                         "frozen_source_byte_mismatch": "PASS"}


if __name__ == "__main__":
    unittest.main(verbosity=2)
