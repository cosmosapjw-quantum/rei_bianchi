"""Manufactured mathematical controls only: no physical Li/RUN19 trajectories."""

import math
import random
import unittest

from rate_defect import (
    assemble_rate_defect, declared_common_relative_defect,
    observable_mixed_bound, panel_supremum_integral_bound,
    sampled_trapezoid_diagnostic,
)

METRICS = {}


def dense_generator(n, directed_rates):
    """Independent column assembly from directed transitions (no pair fluxes)."""
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for origin, destination, rate in directed_rates:
        matrix[destination][origin] += rate
        matrix[origin][origin] -= rate
    return matrix


class RateDefectTests(unittest.TestCase):
    def assertVectorClose(self, actual, expected, tol=1e-12):
        self.assertEqual(len(actual), len(expected))
        for x, y in zip(actual, expected):
            self.assertLessEqual(abs(x - y), tol * max(1.0, abs(x), abs(y)))

    def test_independent_dense_2_4_17_states(self):
        rng = random.Random(20261020)
        errors, mass_defects = [], []
        for n in (2, 4, 17):
            p = [rng.uniform(0.01, 1) for _ in range(n)]
            p = [x / sum(p) for x in p]
            pairs, df, db, truth, approximate = [], [], [], [], []
            for i in range(n):
                for j in range(i + 1, n):
                    i0, j0 = (i, j) if rng.random() < 0.5 else (j, i)
                    pairs.append((i0, j0))
                    f, b, fh, bh = [rng.uniform(0, 7) for _ in range(4)]
                    df.append(fh - f)
                    db.append(bh - b)
                    truth.extend(((i0, j0, f), (j0, i0, b)))
                    approximate.extend(((i0, j0, fh), (j0, i0, bh)))
            k, kh = dense_generator(n, truth), dense_generator(n, approximate)
            expected = [math.fsum((kh[i][j] - k[i][j]) * p[j] for j in range(n)) for i in range(n)]
            result = assemble_rate_defect(n, pairs, p, delta_forward=df, delta_backward=db)
            self.assertVectorClose(result.exact_defect, expected)
            self.assertLessEqual(result.exact_l1, result.pair_triangle_bound + 1e-12)
            self.assertLessEqual(result.pair_triangle_bound, result.independent_rate_majorant + 1e-12)
            errors.append(max(abs(x-y) for x, y in zip(result.exact_defect, expected)))
            mass_defects.append(abs(math.fsum(result.exact_defect)))
            self.assertLessEqual(mass_defects[-1], 1e-13)
        METRICS["dense_max_abs_difference_2_4_17"] = errors
        METRICS["edge_mass_roundoff_2_4_17"] = mass_defects

    def test_orientation_and_adjacent_cancellation(self):
        pairs, p = [(0, 1), (1, 2), (2, 3)], [1, 1, 1, 1]
        result = assemble_rate_defect(4, pairs, p, delta_forward=[1, 1, 1], delta_backward=[0, 0, 0])
        reversed_result = assemble_rate_defect(4, [(j, i) for i, j in pairs], p,
                                              delta_forward=[0, 0, 0], delta_backward=[1, 1, 1])
        self.assertEqual(result.exact_defect, (-1, 0, 0, 1))
        self.assertEqual(result.exact_defect, reversed_result.exact_defect)
        self.assertEqual(result.exact_l1, 2)
        self.assertEqual(result.pair_triangle_bound, 6)
        self.assertVectorClose(result.signed_pair_defects, [-x for x in reversed_result.signed_pair_defects])

    def test_bounds_only_negative_population_and_sources(self):
        result = assemble_rate_defect(2, [(0, 1)], [-0.25, 1.25],
                                      absolute_forward=[2], absolute_backward=[3],
                                      source_difference=[0.2, 0.3])
        self.assertIsNone(result.exact_defect)
        self.assertIsNone(result.exact_l1)
        self.assertEqual(result.negative_population_indices, (0,))
        self.assertEqual(result.independent_rate_majorant, 8.5)
        self.assertEqual(result.source_mass_difference, 0.5)
        self.assertEqual(result.combined_majorant, 9)
        signed = assemble_rate_defect(2, [(0, 1)], [-0.25, 1.25], delta_forward=[2],
                                      delta_backward=[3], source_difference=[0.2, 0.3])
        self.assertEqual(signed.exact_defect, (4.25, -4.25))
        self.assertEqual(signed.negative_population_indices, (0,))
        self.assertAlmostEqual(math.fsum(signed.combined_defect), 0.5)
        self.assertEqual(signed.combined_l1, 8.4)

    def test_explicit_common_perturbation_near_equilibrium(self):
        p = [0.5000000005, 0.4999999995]
        common = declared_common_relative_defect(2, [(0, 1)], p, [1e6], [1e6], [0.01])
        r = common.edge_result
        self.assertLess(r.exact_l1, 2.1e-5)
        self.assertGreater(r.independent_rate_majorant, 19999)
        self.assertAlmostEqual(r.signed_pair_defects[0], 0.01 * common.unperturbed_net_fluxes[0], delta=1e-12)
        # Same independent magnitudes allow opposite actual perturbations:
        independent = assemble_rate_defect(2, [(0, 1)], p,
            delta_forward=[1e4], delta_backward=[-1e4],
            absolute_forward=[1e4], absolute_backward=[1e4])
        self.assertEqual(independent.exact_l1, independent.independent_rate_majorant)
        METRICS["near_balance_common_l1"] = r.exact_l1
        METRICS["near_balance_independent_majorant"] = r.independent_rate_majorant
        METRICS["near_balance_gross_to_common_ratio"] = r.independent_rate_majorant / r.exact_l1

    def test_analytic_two_state_ode_and_integrated_bound(self):
        # Exact rates 2,1; approximate 2.2,0.9; p0(0)=0.8.
        a, b, ah, bh, initial, final_t = 2.0, 1.0, 2.2, 0.9, 0.8, 2.0
        lam, stationary = ah + bh, bh / (ah + bh)
        df, db = ah - a, bh - b
        def exact_pop(t):
            return b/(a+b) + (initial-b/(a+b))*math.exp(-(a+b)*t)
        def approx_pop(t):
            return stationary + (initial-stationary)*math.exp(-lam*t)
        def integrated_bound(t):
            # d=(df+db)*p_hat0-db is strictly positive on this interval.
            return 2 * (((df+db)*stationary-db)*t
                        + (df+db)*(initial-stationary)*(-math.expm1(-lam*t))/lam)
        errors, ratios = [], []
        for step in range(1, 101):
            t = final_t * step / 100
            ph = approx_pop(t)
            defect = assemble_rate_defect(2, [(0, 1)], [ph, 1-ph],
                                          delta_forward=[df], delta_backward=[db])
            self.assertGreater(defect.signed_pair_defects[0], 0)
            error = 2 * abs(exact_pop(t)-ph)
            bound = integrated_bound(t)
            self.assertLessEqual(error, bound + 1e-14)
            errors.append(error)
            ratios.append(error/bound)
        h = final_t / 20
        suprema = [2*((df+db)*approx_pop(i*h)-db) for i in range(20)]
        panel = panel_supremum_integral_bound([h]*20, supremum_bounds=suprema,
                    supremum_provenance="Analytic d(t)>0 decreases; left endpoints are panel maxima.",
                    clock="proper_seconds")
        self.assertGreaterEqual(panel.total, integrated_bound(final_t))
        self.assertEqual(panel.status, "conditional_certificate")
        METRICS["analytic_two_state_final_l1_error"] = errors[-1]
        METRICS["analytic_two_state_integrated_upper_bound"] = integrated_bound(final_t)
        METRICS["analytic_two_state_panel_upper_bound"] = panel.total
        METRICS["analytic_two_state_max_error_to_bound_ratio"] = max(ratios)

    def test_mass_mismatch_observable_counterexample(self):
        error, weights, E, M = [0.2, 0.2], [1, 1], 0.4, 0.4
        actual = math.fsum(w*e for w, e in zip(weights, error))
        wrong_zero_mass = observable_mixed_bound(weights, E, mass_error_bound=0)
        valid_mixed = observable_mixed_bound(weights, E, mass_error_bound=M)
        self.assertGreater(actual, wrong_zero_mass)
        self.assertEqual(actual, valid_mixed)
        self.assertEqual(observable_mixed_bound(weights, E), 0.4)
        self.assertAlmostEqual(observable_mixed_bound([0, 1, 2, 3], 0.2, mass_error_bound=0), 0.3)
        self.assertEqual(observable_mixed_bound([0, 1], 0.2, mass_error_bound=0), 0.1)
        METRICS["mass_mismatch_counterexample_actual"] = actual
        METRICS["mass_mismatch_incorrect_zero_mass_bound"] = wrong_zero_mass
        METRICS["mass_mismatch_valid_mixed_bound"] = valid_mixed

    def test_jump_and_source_mass(self):
        # K=0; approximate trajectory jumps by (+0.3,-0.5). Exact is constant.
        jump = [0.3, -0.5]
        exact_error = [-x for x in jump]
        event_l1 = math.fsum(map(abs, exact_error))
        bound = panel_supremum_integral_bound([0.5, 0.5], supremum_bounds=[0, 0],
                 supremum_provenance="Zero generator and zero smooth residual on both panels.",
                 event_l1_bounds=[event_l1], clock="proper_seconds")
        self.assertEqual(bound.total, event_l1)
        self.assertAlmostEqual(math.fsum(exact_error), 0.2)
        self.assertAlmostEqual(observable_mixed_bound([1, 1], bound.total,
                              mass_error_bound=0.2), 0.2)
        METRICS["jump_l1_event_bound"] = bound.total

    def test_samples_do_not_certify_and_clock_units(self):
        unresolved = panel_supremum_integral_bound([1], samples=[0, 0], clock="proper_seconds")
        diagnostic = sampled_trapezoid_diagnostic([1], [0, 0], clock="proper_seconds")
        # Smooth hidden bump f(t)=6t(1-t) has integral 1 despite zero endpoints.
        self.assertEqual(unresolved.status, "unresolved_samples_only")
        self.assertIsNone(unresolved.total)
        self.assertEqual(diagnostic.status, "sampled_diagnostic")
        self.assertEqual(diagnostic.total, 0)
        physical = panel_supremum_integral_bound([2], supremum_bounds=[3],
                     supremum_provenance="Constant norm 3 per second.", clock="proper_seconds")
        alternate = panel_supremum_integral_bound([0.5], supremum_bounds=[12],
                     supremum_provenance="dt/dx=4 included exactly once in 12.", clock="x")
        self.assertEqual(physical.total, alternate.total)
        self.assertEqual(physical.total, 6)

    def test_zero_and_empty_network(self):
        result = assemble_rate_defect(0, [], [], delta_forward=[], delta_backward=[])
        self.assertEqual(result.exact_defect, ())
        self.assertEqual(result.exact_l1, 0)
        self.assertEqual(result.independent_rate_majorant, 0)
        isolated = assemble_rate_defect(3, [], [0, 0, 0], absolute_forward=[], absolute_backward=[])
        self.assertEqual(isolated.independent_rate_majorant, 0)
        self.assertEqual(observable_mixed_bound([], 0), 0)
        bound = panel_supremum_integral_bound([], supremum_bounds=[],
                     supremum_provenance="Empty interval.", clock="proper_seconds")
        self.assertEqual(bound.total, 0)
        self.assertEqual(sampled_trapezoid_diagnostic([], [0], clock="proper_seconds").total, 0)

    def test_invalid_network_and_numeric_inputs(self):
        base = dict(n=2, pairs=[(0, 1)], population=[0.4, 0.6], delta_forward=[1], delta_backward=[2])
        bad = [dict(n=-1), dict(n=2.0), dict(n=True), dict(pairs=[(0, 0)]),
               dict(pairs=[(0, 2)]), dict(pairs=[(0, 1), (1, 0)]),
               dict(pairs=[(0, 1), (0, 1)]), dict(pairs=[(False, 1)]),
               dict(pairs=[(0, 1.0)]), dict(pairs=[(0,)]),
               dict(population=[0.4]), dict(population=[math.nan, 1]),
               dict(population=[1, math.inf]), dict(delta_forward=[math.inf]),
               dict(delta_backward=[-math.inf]), dict(delta_forward=[]),
               dict(delta_backward=None), dict(absolute_forward=[-1], absolute_backward=[2]),
               dict(absolute_forward=[0], absolute_backward=[2]), dict(absolute_forward=[1]),
               dict(delta_forward=["1"]), dict(delta_forward=[True]),
               dict(source_difference=[math.nan, 1]), dict(source_difference=[1]),
               dict(population=[1e308, 1e308], delta_forward=[1e308]),
               dict(absolute_forward=[math.inf], absolute_backward=[2])]
        for patch in bad:
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    assemble_rate_defect(**(base | patch))
        with self.assertRaises(ValueError):
            assemble_rate_defect(2, [(0, 1)], [0.5, 0.5])
        for kwargs in (dict(forward_rates=[-1], backward_rates=[1], relative_perturbations=[0]),
                       dict(forward_rates=[1], backward_rates=[1], relative_perturbations=[-1.1]),
                       dict(forward_rates=[1], backward_rates=[1], relative_perturbations=[math.nan])):
            with self.assertRaises(ValueError):
                declared_common_relative_defect(2, [(0, 1)], [0.5, 0.5], **kwargs)

    def test_invalid_integral_and_observable_inputs(self):
        for weights, E, M in (([math.nan], 1, 0), ([1], -1, 0), ([1], 1, -1),
                              ([1], math.inf, 0), ([1], 1, math.nan)):
            with self.assertRaises(ValueError):
                observable_mixed_bound(weights, E, mass_error_bound=M)
        base = dict(widths=[1], supremum_bounds=[2], supremum_provenance="Analytic.", clock="seconds")
        for patch in (dict(widths=[-1]), dict(widths=[math.inf]), dict(supremum_bounds=[-2]),
                      dict(supremum_bounds=[math.nan]), dict(supremum_bounds=[]),
                      dict(supremum_provenance=""), dict(event_l1_bounds=[-1]),
                      dict(clock=""), dict(samples=[1, 2]),
                      dict(widths=[1e308], supremum_bounds=[1e308])):
            with self.assertRaises(ValueError):
                panel_supremum_integral_bound(**(base | patch))
        for widths, samples in (([1], [1]), ([-1], [1, 2]), ([1], [1, -2]), ([1], [1, math.inf])):
            with self.assertRaises(ValueError):
                sampled_trapezoid_diagnostic(widths, samples, clock="seconds")


if __name__ == "__main__":
    unittest.main(verbosity=2)
