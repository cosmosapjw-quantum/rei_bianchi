"""Future exact-rational controls. Authored only: no execution authorized.

The tiny-chain oracle enumerates Cartesian endpoint choices independently of
the production prefix DP. Kernel candidates have separate analytic controls.
"""
import unittest
from fractions import Fraction as Q
from itertools import product

from cohort_bounds import (AffineSegment, cohort_bounds, combined_cohort_bounds,
                           integrated_cohort, kernel)


BOX = (AffineSegment(Q(0), Q(1), Q(1), Q(0)),)
RISING = (AffineSegment(Q(0), Q(2), Q(0), Q(1)),)


def chain_oracle(coefficients, lower, upper):
    levels = sorted(set((Q(0),) + lower + upper))
    values = []
    for tail in product(levels, repeat=len(lower) - 1):
        chain = (Q(0),) + tail
        if (all(a <= b for a, b in zip(chain, chain[1:]))
                and all(lo <= x <= hi for lo, x, hi in zip(lower, chain, upper))):
            values.append(sum((c * (b - a) for c, a, b
                               in zip(coefficients, chain, chain[1:])), Q(0)))
    return min(values), max(values)


class CohortBoundsTests(unittest.TestCase):
    def bound(self, A=Q(0), B=Q(1), *, grid=(Q(0), Q(2)),
              lower=(Q(0), Q(1)), upper=(Q(0), Q(1)), cap=Q(1), segments=BOX):
        return cohort_bounds(grid, lower, upper, cap=cap, segments=segments, A=A, B=B)

    def test_box_three_windows_and_nonadditive_upper(self):
        first, second, full = (self.bound(Q(a), Q(b)) for a, b in ((0, 1), (1, 2), (0, 2)))
        for result in (first, second, full):
            self.assertEqual((result.lower, result.upper), (Q(0), Q(1)))
        self.assertGreater(first.upper + second.upper, full.upper)

    def test_combined_kernel_keeps_shared_atom(self):
        result = combined_cohort_bounds((Q(0), Q(2)), (Q(0), Q(1)), (Q(0), Q(1)),
                                       cap=Q(1), segments=BOX,
                                       windows=((Q(0), Q(1), Q(1)), (Q(1), Q(2), Q(1))))
        self.assertEqual((result.lower, result.upper), (Q(0), Q(1)))

    def test_actual_atom_window_values_add(self):
        for tau in (Q(0), Q(1, 3), Q(1), Q(3, 2), Q(2)):
            self.assertEqual(kernel(BOX, Q(0), Q(1), tau) + kernel(BOX, Q(1), Q(2), tau),
                             kernel(BOX, Q(0), Q(2), tau))

    def test_excluded_left_boundary_is_infimum_witness(self):
        result = self.bound(Q(1), Q(2), grid=(Q(0), Q(1), Q(2)),
                            lower=(Q(0), Q(1), Q(1)), upper=(Q(0), Q(1), Q(1)))
        self.assertEqual((result.lower, result.upper), (Q(0), Q(1)))
        self.assertEqual(result.lower_atom_locations[0], Q(0))
        self.assertTrue(result.cell_min[0].left_boundary_excluded)
        self.assertEqual(result.lower_semantics, 'INFIMUM')
        self.assertEqual(result.upper_semantics, 'SUPREMUM')

    def test_rising_frozen_examples(self):
        for window, expected in (((0, 1), (Q(0), Q(1))),
                                 ((1, 2), (Q(1, 2), Q(4))),
                                 ((0, 2), (Q(1, 2), Q(5)))):
            result = self.bound(Q(window[0]), Q(window[1]), grid=(Q(0), Q(1), Q(2)),
                                lower=(Q(0), Q(1), Q(3)), upper=(Q(0), Q(2), Q(4)),
                                cap=Q(4), segments=RISING)
            self.assertEqual((result.lower, result.upper), expected)

    def test_interior_quadratic_stationary_point(self):
        # For h(s)=s on [0,1], K for [1,2] peaks at tau=1:
        # the breakpoint is essential, with exact value 1/2.
        source = (AffineSegment(Q(0), Q(1), Q(0), Q(1)),)
        result = self.bound(Q(1), Q(2), segments=source)
        self.assertEqual(result.cell_max[0].location, Q(1))
        self.assertEqual(result.upper, Q(1, 2))
        # Triangular h gives an actual stationary point within a smooth piece:
        # K'=h(1-tau)-h(2-tau)=1-2*tau on (0,1).
        triangle = (AffineSegment(Q(0), Q(1), Q(0), Q(1)),
                    AffineSegment(Q(1), Q(2), Q(2), Q(-1)))
        result = self.bound(Q(1), Q(2), segments=triangle)
        self.assertEqual(result.cell_max[0].location, Q(1, 2))
        self.assertEqual(result.upper, Q(3, 4))

    def test_tiny_chain_cartesian_oracle(self):
        lower, upper = (Q(0), Q(1), Q(2), Q(2)), (Q(0), Q(2), Q(3), Q(4))
        for windows in (((Q(0), Q(3), Q(1)),),
                        ((Q(0), Q(1), Q(-2)), (Q(1), Q(3), Q(1)))):
            result = combined_cohort_bounds((Q(0), Q(1), Q(2), Q(3)), lower, upper,
                                           cap=Q(4), segments=BOX, windows=windows)
            self.assertEqual(result.lower, chain_oracle(tuple(e.value for e in result.cell_min), lower, upper)[0])
            self.assertEqual(result.upper, chain_oracle(tuple(e.value for e in result.cell_max), lower, upper)[1])

    def test_signed_combination_can_be_negative(self):
        result = combined_cohort_bounds((Q(0), Q(2)), (Q(0), Q(1)), (Q(0), Q(1)),
                                       cap=Q(1), segments=BOX, windows=((Q(0), Q(2), Q(-1)),))
        self.assertEqual((result.lower, result.upper), (Q(-1), Q(0)))

    def test_boundary_source_and_time_crossing(self):
        self.assertEqual([integrated_cohort(BOX, Q(x)) for x in (-1, 0, 1, 2)],
                         [Q(0), Q(0), Q(1), Q(1)])
        self.assertEqual(kernel(BOX, Q(1), Q(2), Q(3, 2)), Q(1, 2))

    def test_negative_slope_nonnegative_density(self):
        falling = (AffineSegment(Q(0), Q(1), Q(1), Q(-1)),)
        self.assertEqual(integrated_cohort(falling, Q(1)), Q(1, 2))
        self.assertEqual(self.bound(segments=falling).upper, Q(1, 2))

    def test_zero_width(self):
        result = self.bound(Q(1), Q(1))
        self.assertEqual((result.lower, result.upper), (Q(0), Q(0)))

    def test_empty_cohort(self):
        result = self.bound(segments=())
        self.assertEqual((result.lower, result.upper), (Q(0), Q(0)))

    def test_singleton_grid(self):
        result = self.bound(Q(0), Q(0), grid=(Q(0),), lower=(Q(0),), upper=(Q(0),), cap=Q(0))
        self.assertEqual((result.lower, result.upper, result.lower_chain), (Q(0), Q(0), (Q(0),)))
        self.assertEqual(result.cell_min, ())

    def test_strict_numeric_types_even_zero_case(self):
        for invalid in (0, 0.0, True, '0'):
            with self.assertRaises(TypeError):
                self.bound(Q(0), Q(0), cap=invalid, segments=())
        with self.assertRaises(TypeError):
            AffineSegment(Q(0), Q(1), 1, Q(0))

    def test_invalid_knots_and_bounds(self):
        for grid in ((Q(0), Q(0)), (Q(1), Q(2)), (Q(0), Q(-1))):
            with self.assertRaises(ValueError):
                self.bound(grid=grid)
        with self.assertRaises(ValueError):
            self.bound(lower=(Q(0), Q(2)), upper=(Q(0), Q(1)))
        with self.assertRaises(ValueError):
            self.bound(grid=(Q(0), Q(1), Q(2)), lower=(Q(0), Q(1), Q(0)),
                       upper=(Q(0), Q(1), Q(1)))

    def test_invalid_cap_and_window(self):
        with self.assertRaises(ValueError):
            self.bound(cap=Q(0))
        for A, B in ((Q(-1), Q(0)), (Q(2), Q(1)), (Q(0), Q(3))):
            with self.assertRaises(ValueError):
                self.bound(A, B)

    def test_source_gap_overlap_and_negative_endpoint(self):
        for source in ((AffineSegment(Q(1), Q(2), Q(1), Q(0)),),
                       BOX + (AffineSegment(Q(2), Q(3), Q(1), Q(0)),),
                       BOX + (AffineSegment(Q(1, 2), Q(2), Q(1), Q(0)),)):
            with self.assertRaises(ValueError):
                self.bound(segments=source)
        with self.assertRaises(ValueError):
            AffineSegment(Q(0), Q(1), Q(1), Q(-2))

    def test_large_integer_exactness(self):
        mass = Q(2 ** 60 + 3)
        result = self.bound(lower=(Q(0), mass), upper=(Q(0), mass), cap=mass)
        self.assertEqual(result.upper, mass)
        self.assertIs(type(result.upper), Q)

    def test_witness_chain_feasibility_and_objective(self):
        result = self.bound(Q(0), Q(2), grid=(Q(0), Q(1), Q(2)),
                            lower=(Q(0), Q(1), Q(3)), upper=(Q(0), Q(2), Q(4)),
                            cap=Q(4), segments=RISING)
        for objective, chain, cells in ((result.lower, result.lower_chain, result.cell_min),
                                        (result.upper, result.upper_chain, result.cell_max)):
            self.assertTrue(all(a <= b for a, b in zip(chain, chain[1:])))
            self.assertEqual(objective, sum((cell.value * (b - a)
                                             for cell, a, b in zip(cells, chain, chain[1:])), Q(0)))

    def test_dataclasses_frozen_and_deterministic_ties(self):
        result = self.bound(Q(1), Q(1))
        self.assertEqual(result.lower_atom_locations, (Q(0),))
        self.assertEqual(result.lower_chain, (Q(0), Q(1)))
        with self.assertRaises(AttributeError):
            result.lower = Q(1)


if __name__ == '__main__':
    unittest.main()
