"""Authored controls A-G; NOT_RUN until separately authorized."""
import unittest
from fractions import Fraction as Q
from deps.caloric_branch import CaloricBranch
from implementation.directional_pullback import (
    inverse_directional, inverse_linearization, callback_direction,
    DomainBoundary, NonDifferentiableKnot, MissingDerivativeInput,
)


def branch(knots=((1, 2), (2, 4), (4, 10))):
    return CaloricBranch(knots, "manufactured V0", "supplied thermal store", "contract A-G")


class DirectionalControls(unittest.TestCase):
    evidence = {}

    def test_A_open_segment_and_exact_difference_errors(self):
        b = branch()
        r = inverse_directional(b, 7, 5, (1, -1, 2), (3, -2, 4))
        self.assertEqual((r.temperature, r.temperature_direction), (3, Q(11, 6)))
        l = inverse_linearization(b, 7)
        self.assertEqual(l.energy_coefficient, Q(1, 3))
        self.assertEqual(l.temperature_knot_coefficients, (0, Q(1, 2), Q(1, 2)))
        self.assertEqual(l.energy_knot_coefficients, (0, -Q(1, 6), -Q(1, 6)))
        rows = []
        def independent_curve(h):
            return (18+29*h+15*h*h)/(6+6*h)
        for h in (Q(1, 4), Q(1, 8), Q(1, 16), Q(1, 32), Q(1, 64)):
            values = []
            for x in (h, -h):
                moved = branch(tuple((t+x*a, u+x*c) for (t, u), a, c in
                                     zip(b.knots, (1, -1, 2), (3, -2, 4))))
                val = moved.inverse(7+x*5)
                self.assertEqual(val, independent_curve(x))
                values.append(val)
            forward = (values[0]-3)/h-Q(11, 6)
            central = (values[0]-values[1])/(2*h)-Q(11, 6)
            self.assertEqual(forward, 2*h/(3*(1+h)))
            self.assertEqual(central, -2*h*h/(3*(1-h*h)))
            rows.append({"h": h, "forward_error": forward, "central_error": central})
        self.evidence["A"] = {"temperature": r.temperature, "direction": r.temperature_direction,
                              "difference_errors": rows}

    def test_B_kink_and_false_centered_candidate(self):
        b = branch()
        right = inverse_directional(b, 4, 1, (0,)*3, (0,)*3)
        left = inverse_directional(b, 4, -1, (0,)*3, (0,)*3)
        self.assertEqual(right.temperature_direction, Q(1, 3))
        self.assertEqual(left.temperature_direction, -Q(1, 2))
        self.assertFalse(right.unrestricted_linearization)
        with self.assertRaises(NonDifferentiableKnot):
            inverse_linearization(b, 4)
        for h in (Q(1, 4), Q(1, 16), Q(1, 64)):
            centered = (b.inverse(4+h)-b.inverse(4-h))/(2*h)
            self.assertEqual(centered, Q(5, 12))
            self.assertNotEqual(centered, Q(1, 3))
            self.assertNotEqual(centered, Q(1, 2))
        self.evidence["B"] = {"right_direction": Q(1, 3), "negative_direction": -Q(1, 2),
                              "false_centered_slope": Q(5, 12), "right_candidate_error": Q(1, 12),
                              "directional_map": [{"v": Q(v), "dT": inverse_directional(
                                  b, 4, v, (0,)*3, (0,)*3).temperature_direction}
                                  for v in range(-3, 4)]}

    def test_C_moving_knot(self):
        actual = [inverse_directional(branch(), 4, v, (0, 2, 0), (0, 3, 0))
                  for v in (5, 1, 3)]
        self.assertEqual(tuple(r.temperature_direction for r in actual), (Q(8, 3), 1, 2))
        self.assertEqual(tuple(r.status for r in actual), ("right", "left", "moving_knot"))

    def test_D_boundary_and_types(self):
        b = branch()
        for e, v in ((2, -1), (10, 1)):
            with self.assertRaises(DomainBoundary):
                inverse_directional(b, e, v, (0,)*3, (0,)*3)
        for e, v, dt in ((2, 1, Q(1, 2)), (10, -1, -Q(1, 3)), (2, 0, 0), (10, 0, 0)):
            self.assertEqual(inverse_directional(b, e, v, (0,)*3, (0,)*3).temperature_direction, dt)
            with self.assertRaises(DomainBoundary):
                inverse_linearization(b, e)
        for knots in (((1, 2), (1, 3)), ((1, 2), (2, 2)), ((0, 2), (1, 3))):
            with self.assertRaises(ValueError):
                branch(knots)
        with self.assertRaises(TypeError):
            inverse_directional(b, 7.0, 1, (0,)*3, (0,)*3)
        with self.assertRaises(TypeError):
            inverse_directional(b, 7, 1, (0, 0.0, 0), (0,)*3)
        with self.assertRaises(ValueError):
            inverse_directional(b, 7, 1, (), (0,)*3)

    def test_E_equal_slope_knot(self):
        b = branch(((1, 2), (2, 4), (3, 6)))
        l = inverse_linearization(b, 4)
        self.assertEqual(l.energy_coefficient, Q(1, 2))
        self.assertEqual(l.temperature_knot_coefficients, (0, 1, 0))
        self.assertEqual(l.energy_knot_coefficients, (0, -Q(1, 2), 0))
        self.assertTrue(inverse_directional(b, 4, 1, (0,)*3, (0,)*3).unrestricted_linearization)

    def test_F_moving_energy_coordinates(self):
        b = branch()
        transformed = branch(tuple((t, 3*u-17) for t, u in b.knots))
        bp = tuple(3*d+2*u+5 for d, u in zip((3, -2, 4), b.energies))
        r = inverse_directional(transformed, 3*7-17, 3*5+2*7+5, (1, -1, 2), bp)
        self.assertEqual((r.temperature, r.temperature_direction), (3, Q(11, 6)))
        wrong = inverse_directional(transformed, 4, 15, (1, -1, 2), bp)
        self.assertNotEqual(wrong.temperature_direction, Q(11, 6))

    def test_G_callback_and_missing_input(self):
        self.assertEqual(callback_direction(((2, -1), (0, 3)), (1, 2), (3, -2), Q(11, 6)),
                         (Q(11, 2), Q(7, 3)))
        with self.assertRaises(MissingDerivativeInput):
            callback_direction(((2, -1),), (1, 2), None, 1)
        for column in ((), (1, 2)):
            with self.assertRaises(ValueError):
                callback_direction(((2, -1),), (1, 2), column, 1)
        with self.assertRaises(TypeError):
            callback_direction(((2, -1),), (1, 2), (1.0,), 1)
        with self.assertRaises(ValueError):
            callback_direction(((2,),), (1, 2), (1,), 1)
