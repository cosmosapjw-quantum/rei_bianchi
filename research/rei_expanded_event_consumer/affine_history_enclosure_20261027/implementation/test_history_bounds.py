"""Future stdlib tests.  These tests have not been executed by their author."""

from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest

from history_bounds import SourceIdentity, binding_issues, history_bounds


Q = Fraction


class HistoryBoundsTests(unittest.TestCase):
    def arguments(self, **updates):
        values = dict(
            grid=(Q(0), Q(1), Q(2)),
            lower=(Q(0), Q(1), Q(3)),
            upper=(Q(0), Q(2), Q(4)),
            cap=Q(4), A=Q(1), B=Q(2), alpha=Q(1), beta=Q(0),
        )
        values.update(updates)
        return values

    def test_affine_window_analytic_vector(self):
        result = history_bounds(**self.arguments())
        self.assertEqual(result.weights, (Q(1), Q(1, 2)))
        self.assertEqual(result.lower, Q(1, 2))
        self.assertEqual(result.upper, Q(4))
        self.assertEqual(result.scope, "INTERVAL_MONOTONICITY_AFFINE_HISTORY")
        self.assertEqual(result.upper_attainment, "SUPREMUM_NOT_GENERALLY_ATTAINED")
        self.assertIs(type(result.lower), Fraction)
        self.assertIs(type(result.upper), Fraction)
        self.assertTrue(all(type(weight) is Fraction for weight in result.weights))
        with self.assertRaises(FrozenInstanceError):
            result.lower = Q(0)

    def test_full_window_analytic_vector(self):
        result = history_bounds(**self.arguments(A=Q(0)))
        self.assertEqual(result.weights, (Q(3, 2), Q(1, 2)))
        self.assertEqual(result.lower, Q(1, 2))
        self.assertEqual(result.upper, Q(5))

    def test_constant_history_analytic_vector(self):
        result = history_bounds(**self.arguments(alpha=Q(0), beta=Q(1)))
        self.assertEqual(result.weights, (Q(0), Q(1)))
        self.assertEqual(result.lower, Q(1))
        self.assertEqual(result.upper, Q(4))

    def test_zero_width_window_inside_grid_interval(self):
        result = history_bounds(**self.arguments(A=Q(4, 3), B=Q(4, 3)))
        self.assertEqual(result.weights, (Q(0), Q(0)))
        self.assertEqual(result.lower, Q(0))
        self.assertEqual(result.upper, Q(0))

    def test_zero_source_and_singleton_zero_domain(self):
        zero_source = history_bounds(**self.arguments(alpha=Q(0), beta=Q(0)))
        self.assertEqual(zero_source.weights, (Q(0), Q(0)))
        self.assertEqual((zero_source.lower, zero_source.upper), (Q(0), Q(0)))
        point = history_bounds(**self.arguments(
            grid=(Q(0),), lower=(Q(0),), upper=(Q(0),),
            A=Q(0), B=Q(0), cap=Q(0),
        ))
        self.assertEqual(point.weights, ())
        self.assertEqual((point.lower, point.upper), (Q(0), Q(0)))

    def test_adjacent_windows_add_weights_and_both_endpoints(self):
        # Within this nonnegative affine class, a common lower staircase and
        # common upper-approximating sequence work for these windows together.
        for alpha, beta in ((Q(1), Q(0)), (Q(0), Q(1)), (Q(2, 3), Q(5, 7))):
            with self.subTest(alpha=alpha, beta=beta):
                first = history_bounds(**self.arguments(
                    A=Q(0), B=Q(1), alpha=alpha, beta=beta
                ))
                second = history_bounds(**self.arguments(alpha=alpha, beta=beta))
                whole = history_bounds(**self.arguments(
                    A=Q(0), B=Q(2), alpha=alpha, beta=beta
                ))
                self.assertEqual(
                    tuple(a + b for a, b in zip(first.weights, second.weights)),
                    whole.weights,
                )
                self.assertEqual(first.lower + second.lower, whole.lower)
                self.assertEqual(first.upper + second.upper, whole.upper)

    def test_exact_rational_above_binary64_integer_precision(self):
        large = Q(3 * (2 ** 53) + 1, 3)
        result = history_bounds(**self.arguments(
            lower=(Q(0), large, large + Q(1)),
            upper=(Q(0), large, large + Q(1)), cap=large + Q(1),
        ))
        self.assertGreater(large, Q(2 ** 53))
        self.assertEqual(result.lower, Q(1, 2) * large)
        self.assertEqual(result.upper, large + Q(1, 2) * (large + Q(1)))

    def test_invalid_closed_intervals_and_grids(self):
        invalid = (
            dict(grid=(), lower=(), upper=()),
            dict(lower=(Q(0), Q(1))),
            dict(grid=(Q(1), Q(2), Q(3))),
            dict(grid=(Q(0), Q(1), Q(1))),
            dict(grid=(Q(0), Q(2), Q(1))),
            dict(lower=(Q(1), Q(1), Q(3))),
            dict(upper=(Q(1), Q(2), Q(4))),
            dict(lower=(Q(0), Q(-1), Q(3))),
            dict(upper=(Q(0), Q(-1), Q(4))),
            dict(lower=(Q(0), Q(2), Q(1))),
            dict(upper=(Q(0), Q(4), Q(3))),
            dict(lower=(Q(0), Q(3), Q(3))),
            dict(cap=Q(3)),
            dict(cap=Q(-1)),
        )
        for update in invalid:
            with self.subTest(update=update):
                with self.assertRaises(ValueError):
                    history_bounds(**self.arguments(**update))

    def test_signed_kernel_and_extrapolation_refused(self):
        for update in (
            dict(alpha=Q(-1)), dict(beta=Q(-1)),
            dict(A=Q(-1)), dict(A=Q(2), B=Q(1)), dict(B=Q(3)),
        ):
            with self.subTest(update=update):
                with self.assertRaises(ValueError):
                    history_bounds(**self.arguments(**update))

    def test_cap_is_required_and_exact(self):
        arguments = self.arguments()
        del arguments["cap"]
        with self.assertRaises(TypeError):
            history_bounds(**arguments)
        with self.assertRaises(TypeError):
            history_bounds(**self.arguments(cap=None))
        result = history_bounds(**self.arguments(cap=Q(100)))
        self.assertEqual(result.upper, Q(4))

    def test_no_numeric_coercion(self):
        for invalid in (True, False, 1, 1.0, "1"):
            for field_name in ("cap", "A", "B", "alpha", "beta"):
                with self.subTest(invalid=invalid, field=field_name):
                    with self.assertRaises(TypeError):
                        history_bounds(**self.arguments(**{field_name: invalid}))
            for field_name in ("grid", "lower", "upper"):
                values = list(self.arguments()[field_name])
                values[1] = invalid
                with self.subTest(invalid=invalid, field=field_name):
                    with self.assertRaises(TypeError):
                        history_bounds(**self.arguments(**{field_name: values}))


class BindingIssuesTests(unittest.TestCase):
    def identity(self):
        return SourceIdentity("state", "template", "frame", "volume", "clock")

    def test_explicit_matching_metadata_and_declaration(self):
        identity = self.identity()
        self.assertEqual(binding_issues(
            identity, identity, frozen_linear_stationary_response=True
        ), ())
        with self.assertRaises(FrozenInstanceError):
            identity.state_id = "other"

    def test_unknown_fields_are_missing_not_mismatched(self):
        issues = binding_issues(
            SourceIdentity(), SourceIdentity(), frozen_linear_stationary_response=True
        )
        self.assertEqual(len(issues), 10)
        self.assertIn("missing:source.state_id", issues)
        self.assertIn("missing:response.proper_clock_id", issues)
        self.assertFalse(any(issue.startswith("mismatch:") for issue in issues))
        one_unknown = binding_issues(
            replace(self.identity(), state_id=None), self.identity(),
            frozen_linear_stationary_response=True,
        )
        self.assertEqual(one_unknown, ("missing:source.state_id",))

    def test_mismatch_preserves_field_name(self):
        for name in (
            "state_id", "spectral_template_id", "frame_id",
            "volume_convention_id", "proper_clock_id",
        ):
            with self.subTest(field=name):
                self.assertEqual(binding_issues(
                    self.identity(), replace(self.identity(), **{name: "other"}),
                    frozen_linear_stationary_response=True,
                ), ("mismatch:" + name,))

    def test_declaration_must_be_explicit_true(self):
        identity = self.identity()
        self.assertEqual(binding_issues(identity, identity), (
            "missing:frozen_linear_stationary_response",
        ))
        self.assertEqual(binding_issues(
            identity, identity, frozen_linear_stationary_response=False
        ), ("not_declared:frozen_linear_stationary_response",))
        self.assertEqual(binding_issues(
            identity, identity, frozen_linear_stationary_response=1
        ), ("invalid:frozen_linear_stationary_response",))

    def test_blank_and_invalid_identifiers_are_not_inferred(self):
        self.assertEqual(binding_issues(
            replace(self.identity(), frame_id=" "), self.identity(),
            frozen_linear_stationary_response=True,
        ), ("missing:source.frame_id",))
        self.assertEqual(binding_issues(
            self.identity(), replace(self.identity(), state_id=0),
            frozen_linear_stationary_response=True,
        ), ("invalid:response.state_id",))


if __name__ == "__main__":
    unittest.main()
