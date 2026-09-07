"""Ten DESIGNED, NOT YET EXECUTED obligations; synthetic rational fixtures only.

Run directly with Python 3.10+ and preserve stdout/stderr/actual exit.
The independent dual reference differentiates the TWO normalization stages.
It does not call the reduced JVP. No production module is imported.
"""
from fractions import Fraction as Q
import unittest

from owner_current_reference import coefficient_jvp, resolved_current_jvp


class Dual:
    def __init__(self, value, tangent=0):
        self.value, self.tangent = Q(value), Q(tangent)

    @staticmethod
    def lift(x):
        return x if isinstance(x, Dual) else Dual(x)

    def __add__(self, other):
        b = self.lift(other)
        return Dual(self.value + b.value, self.tangent + b.tangent)

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.value, -self.tangent)

    def __sub__(self, other):
        return self + (-self.lift(other))

    def __rsub__(self, other):
        return self.lift(other) - self

    def __mul__(self, other):
        b = self.lift(other)
        return Dual(self.value * b.value, self.tangent * b.value + self.value * b.tangent)

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = self.lift(other)
        return Dual(self.value / b.value,
                    (self.tangent * b.value - self.value * b.tangent) / (b.value * b.value))

    def __rtruediv__(self, other):
        return self.lift(other) / self


def staged(counts, d_counts, strengths, d_strengths, *, current, d_current=0,
           external, d_external=0, opacity, d_opacity=0):
    n = [[Dual(x, dx) for x, dx in zip(row, drow)] for row, drow in zip(counts, d_counts)]
    c = [Dual(x, dx) for x, dx in zip(strengths, d_strengths)]
    j, kappa = Dual(current, d_current), Dual(opacity, d_opacity)
    raw = [Dual(external, d_external)] + [c[s] * sum(n[s]) for s in range(3)]
    r = sum(raw)
    conditioned = [kappa * x / r for x in raw]
    owner_j = [j / kappa * x for x in conditioned]
    # Any fixed positive cross section cancels in the node normalization.
    sigma = (Q(2), Q(3), Q(5))
    out = []
    for s in range(3):
        measure = [x * sigma[s] for x in n[s]]
        q = [x / sum(measure) for x in measure]
        out.append(tuple(owner_j[s + 1] * x for x in q))
    return tuple(out), owner_j[0]


class OwnerCurrentTests(unittest.TestCase):
    def setUp(self):
        self.n = ((Q(2), Q(3)), (Q(5), Q(7)), (Q(11), Q(13)))
        self.dn = ((Q(1, 7), Q(-2, 9)), (Q(2, 11), Q(1, 13)), (Q(-1, 5), Q(2, 17)))
        self.c = (Q(1, 2), Q(1, 3), Q(1, 5))
        self.dc = (Q(1, 19), Q(-1, 23), Q(2, 29))
        self.kw = dict(current=Q(17), d_current=Q(2, 3), external=Q(19),
                       d_external=Q(-3, 7), opacity=Q(7))
        self.zero = ((0, 0),) * 3

    def evaluate(self, **overrides):
        kw = dict(self.kw)
        kw.update(overrides)
        return resolved_current_jvp(self.n, self.dn, self.c, self.dc, **kw)

    def test_O01_staged_primal(self):
        actual = self.evaluate()
        ref, sub = staged(self.n, self.dn, self.c, self.dc, **self.kw)
        self.assertEqual(actual.resolved, tuple(tuple(x.value for x in row) for row in ref))
        self.assertEqual(actual.subgrid_total, sub.value)

    def test_O02_HeII_per_hydrogen_not_helium(self):
        c, _ = coefficient_jvp((2, 3, 5), (0, 0, 0), hydrogen_total=7, helium_total=11)
        self.assertEqual(c, (Q(2, 7), Q(3, 11), Q(5, 7)))
        self.assertNotEqual(c[2], Q(5, 11))

    def test_O03_element_total_and_prefactor_directions(self):
        c, dc = coefficient_jvp((2, 3, 5), (1, 2, 3), hydrogen_total=7,
                               helium_total=11, d_hydrogen_total=2, d_helium_total=-1)
        ref = (Dual(2, 1) / Dual(7, 2), Dual(3, 2) / Dual(11, -1), Dual(5, 3) / Dual(7, 2))
        self.assertEqual(c, tuple(x.value for x in ref))
        self.assertEqual(dc, tuple(x.tangent for x in ref))

    def test_O04_full_JVP_against_two_stage_dual(self):
        actual = self.evaluate()
        ref, sub = staged(self.n, self.dn, self.c, self.dc, d_opacity=Q(5, 11), **self.kw)
        self.assertEqual(actual.d_resolved, tuple(tuple(x.tangent for x in row) for row in ref))
        self.assertEqual(actual.d_subgrid_total, sub.tangent)

    def test_O05_other_node_response_kills_frozen_global_normalizer(self):
        dn = ((0, 1), (0, 0), (0, 0))
        actual = resolved_current_jvp(self.n, dn, self.c, (0, 0, 0),
                                     current=17, external=19, opacity=7)
        expected = -Q(17) * self.c[0] * self.n[0][0] * self.c[0] / actual.raw_total**2
        self.assertEqual(actual.d_resolved[0][0], expected)
        self.assertLess(expected, 0)
        self.assertNotEqual(actual.d_resolved[0][0], 0)  # frozen-R mutant predicts zero

    def test_O06_augmented_current_and_tangent_conservation(self):
        result = self.evaluate()
        self.assertEqual(sum(x for row in result.resolved for x in row) + result.subgrid_total, 17)
        self.assertEqual(sum(x for row in result.d_resolved for x in row) + result.d_subgrid_total, Q(2, 3))

    def test_O07_structural_zero_owner_and_zero_current(self):
        out = resolved_current_jvp(self.n, self.dn, (1, 0, 1), (0, 0, 0),
                                  current=17, external=0, opacity=7)
        self.assertEqual(out.resolved[1], (0, 0))
        self.assertEqual(out.d_resolved[1], (0, 0))
        self.assertEqual(out.subgrid_total, 0)
        zero_j = self.evaluate(current=0, d_current=0)
        self.assertTrue(all(x == 0 for row in zero_j.d_resolved for x in row))

    def test_O08_domain_rejections(self):
        for kw in ({"opacity": 0}, {"current": -1}, {"external": -1},
                   {"external": 0}, {"current": 0}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.evaluate(**kw)
        with self.assertRaises(TypeError):
            self.evaluate(current=17.0)
        for n, dn, c, dc, e in ((self.zero, self.zero, self.c, (0, 0, 0), 1),
                                (((1,),) * 3, self.zero, self.c, (0, 0, 0), 1),
                                (self.n, self.zero, (0, 0, 0), (0, 0, 0), 0),
                                (self.n, self.zero, (1, 0, 1), (0, 1, 0), 1)):
            with self.subTest(n=n, c=c), self.assertRaises(ValueError):
                resolved_current_jvp(n, dn, c, dc, current=1, external=e, opacity=1)

    def test_O09_direction_bound_and_common_raw_scale_invariance(self):
        out = self.evaluate()
        norm = abs(out.d_subgrid_total) + sum(abs(x) for row in out.d_resolved for x in row)
        self.assertLessEqual(norm, out.augmented_l1_direction_bound)
        scale = resolved_current_jvp(self.n, self.zero, self.c, self.c,
                                    current=17, external=19, d_external=19, opacity=7)
        self.assertTrue(all(x == 0 for row in scale.d_resolved for x in row))
        self.assertEqual(scale.d_subgrid_total, 0)

    def test_O10_opacity_partial_and_group_additivity(self):
        a, b = self.evaluate(), self.evaluate(opacity=13)
        self.assertEqual(a, b)
        half = self.evaluate(current=Q(17, 2), d_current=Q(1, 3))
        self.assertEqual(a.resolved, tuple(tuple(2 * x for x in row) for row in half.resolved))
        self.assertEqual(a.d_resolved, tuple(tuple(2 * x for x in row) for row in half.d_resolved))


if __name__ == "__main__":
    unittest.main(verbosity=2)
