"""ExactFraction synthetic checks for T3; no actual scientific values."""
import itertools
import random
import unittest
from fractions import Fraction as Q

from t3_predicate_checks import (MAX_BITS, MAX_FINITE, SIGN, TAU, TAU_BITS,
    Refusal, canonical, interval_sufficient, midpoint, neighbor, oracle,
    point_predicates, representative_box, rn_relation, value)


class T3Tests(unittest.TestCase):
    def test_frozen_tolerance_exact_token_and_odd_parity(self):
        self.assertEqual(TAU, Q(7737125245533627, 77371252455336267181195264))
        self.assertEqual(TAU_BITS & 1, 1)
        self.assertNotEqual(TAU, Q(1, 10**10))

    def test_all_four_preimages_at_both_midpoints_and_adjacent_sides(self):
        positives = [0, 1, 2, 3, (1<<52)-1, 1<<52, (1<<52)+1,
                     TAU_BITS-1, TAU_BITS, TAU_BITS+1,
                     0x3fefffffffffffff, 0x3ff0000000000000, 0x3ff0000000000001,
                     MAX_BITS-1]
        thresholds = positives + [SIGN | b for b in positives if b] + [SIGN]
        for bits in thresholds:
            low, high = midpoint(bits, -1), midpoint(bits, 1)
            delta = min(value(bits)-low, high-value(bits))/4
            for x in (low-delta, low, low+delta, value(bits), high-delta, high, high+delta):
                if abs(x) > MAX_FINITE:
                    continue
                rounded = value(oracle.round_binary64(x))
                expected = {'>=': rounded >= value(bits), '>': rounded > value(bits),
                            '<=': rounded <= value(bits), '<': rounded < value(bits)}
                for relation, answer in expected.items():
                    self.assertEqual(rn_relation(x, bits, relation), answer, (bits, x, relation))

    def test_zero_signs_subnormals_and_normal_boundary(self):
        self.assertEqual(canonical(SIGN), 0)
        self.assertEqual(neighbor(SIGN, -1), SIGN|1)
        half_min = value(1)/2
        self.assertTrue(rn_relation(-half_min, 0, '>='))
        self.assertFalse(rn_relation(half_min, 0, '>'))
        self.assertTrue(rn_relation(value(3)/2, 1, '>'))
        self.assertEqual(value(oracle.round_binary64((value((1<<52)-1)+value(1<<52))/2)), value(1<<52))

    def test_primary_threshold_equality_and_parity(self):
        cut = midpoint(TAU_BITS, 1)
        self.assertTrue(rn_relation(cut, TAU_BITS, '>'))
        self.assertFalse(rn_relation((TAU+cut)/2, TAU_BITS, '>'))
        even = TAU_BITS+1
        self.assertFalse(rn_relation(midpoint(even, 1), even, '>'))

    def test_source_weak_equality_uses_lower_midpoint_parity(self):
        for bits in (TAU_BITS, TAU_BITS+1, 0x3ff0000000000000):
            self.assertEqual(rn_relation(midpoint(bits, -1), bits, '>='), bits % 2 == 0)

    def test_exact_gap_pareto_does_not_imply_primary(self):
        u = value(TAU_BITS+1)-TAU
        a, b = 3*u/4, value(TAU_BITS+1)
        ab, bb = oracle.round_binary64(a), TAU_BITS+1
        self.assertEqual(value(ab), a)
        self.assertEqual(b-a, TAU+u/4)
        self.assertGreater(b-a, TAU)
        self.assertEqual(point_predicates(ab, bb, 'PRIMARY'), (True, False))
        self.assertEqual(point_predicates(ab, bb, 'SECONDARY'), (True, True))
        self.assertFalse(oracle.audit_frozen_binary64((ab,0),(bb,0),comparison='PRIMARY')['frozen_binary64_supported'])
        self.assertTrue(oracle.audit_frozen_binary64((ab,0),(bb,0),comparison='SECONDARY')['frozen_binary64_supported'])

    def test_primary_true_secondary_false_at_other_boundary(self):
        a = oracle.round_binary64(Q(1)-TAU)
        b = 0x3ff0000000000000
        self.assertEqual(point_predicates(a,b,'PRIMARY'), (True,True))
        self.assertEqual(point_predicates(a,b,'SECONDARY'), (True,False))
        self.assertEqual(point_predicates(a-1,b,'SECONDARY'), (True,True))

    def test_machine_weak_does_not_imply_exact_weak(self):
        a = oracle.round_binary64(Q(1)+TAU)
        b = 0x3ff0000000000000
        self.assertGreater(value(a), Q(1)+TAU)
        self.assertTrue(point_predicates(a,b,'PRIMARY')[0])
        for comparison in ('PRIMARY','SECONDARY'):
            result = oracle.audit_frozen_binary64((a,0),(b,b),comparison=comparison)
            self.assertTrue(result['frozen_binary64_supported'])
            self.assertFalse(result['exact_gap_supported'])

    def test_scalar_formulas_match_frozen_pure_oracle_on_synthetic_bits(self):
        rng = random.Random(3103)
        cases = [(rng.randrange(0,0x4100000000000000), rng.randrange(0,0x4100000000000000)) for _ in range(240)]
        cases += [(0,0),(SIGN,0),(1,2),(TAU_BITS,TAU_BITS+1)]
        for a,b in cases:
            for comparison in ('PRIMARY','SECONDARY'):
                got = point_predicates(a,b,comparison)
                ref = oracle.audit_frozen_binary64((a,a),(b,b),comparison=comparison)
                self.assertEqual(got, (ref['weak_predicates'][0],ref['strict_predicates'][0]))

    def test_interval_projection_closed_endpoints_empty_and_zero(self):
        self.assertEqual(representative_box(Q(0),Q(0)), (0,0))
        self.assertEqual(representative_box(-value(1),value(1)), (0,1))
        self.assertEqual(representative_box(value(1),value(2)), (1,2))
        with self.assertRaises(Refusal):
            representative_box(value(1)/4,value(1)/2)

    def test_interval_worst_corner_against_exhaustive_small_boxes(self):
        base = 0x3feffffffff24190
        boxes = [(0,2),(TAU_BITS-1,TAU_BITS+1),(base-1,base+1),
                 (0x3ff0000000000000,0x3ff0000000000002)]
        for (al,au),(bl,bu) in itertools.product(boxes,repeat=2):
            for comparison in ('PRIMARY','SECONDARY'):
                got = interval_sufficient([(value(al),value(au)),(Q(0),Q(0))],
                                          [(value(bl),value(bu)),(Q(0),Q(0))],comparison)
                truth = all(all(point_predicates(a,b,comparison))
                            for a in range(al,au+1) for b in range(bl,bu+1))
                self.assertEqual(got['supported_for_every_scalar_in_box'],truth)

    def test_overflow_nonfinite_and_invalid_domain_refused(self):
        with self.assertRaises(Refusal):
            point_predicates(0,MAX_BITS,'PRIMARY')
        with self.assertRaises(Refusal):
            rn_relation(MAX_FINITE+1,TAU_BITS,'>')
        with self.assertRaises(oracle.ContractError):
            point_predicates(0x7ff0000000000000,0,'PRIMARY')
        with self.assertRaises(Refusal):
            point_predicates(SIGN|1,0,'SECONDARY')
        with self.assertRaises(Refusal):
            interval_sufficient([(Q(0),Q(0))]*2,[(MAX_FINITE,MAX_FINITE)]*2,'PRIMARY')
        self.assertEqual(point_predicates(MAX_BITS,0,'SECONDARY'), (False,False))


if __name__ == '__main__':
    unittest.main()
