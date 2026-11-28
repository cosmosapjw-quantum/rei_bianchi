"""Synthetic only: no repository arrays, comparator imports or science calls."""
import math
import random
import struct
import unittest
from decimal import Decimal, localcontext
from fractions import Fraction as F

from exact_gram.engine import (
    Interval, Limits, ResourceLimit, ContractError, ComplexDisk,
    TOLERANCE_BITS, TOLERANCE, MATHEMATICAL_TOLERANCE,
    sqrt_interval, gram2, spectral_norm, adjoint, construct_k,
    represented_errors, represented_gaps, interval_max, source_error_bound_disk,
    direct_gap_lower, legacy_eta, legacy_gap_lower, pareto_sufficient,
    binary64_value, round_binary64, audit_frozen_binary64, from_decoded,
    propagate_epsilon,
)


def z(r=0, i=0):
    return F(r), F(i)


def bits(x):
    return int.from_bytes(struct.pack('>d', x), 'big')


def d(q):
    return Decimal(q.numerator) / Decimal(q.denominator)


class EngineTests(unittest.TestCase):
    def test_sqrt_exact_and_irrational(self):
        for q, expected in [(F(0), F(0)), (F(9, 16), F(3, 4)), (F(2**200), F(2**100))]:
            self.assertEqual(sqrt_interval(q), Interval(expected, expected))
        for q in (F(2), F(1, 3), F(17, 19), F(1, 2**2000)):
            a = sqrt_interval(q, precision=83)
            self.assertLessEqual(a.lo*a.lo, q)
            self.assertGreaterEqual(a.hi*a.hi, q)
            self.assertLessEqual(a.hi-a.lo, F(1, 2**83))

    def test_sqrt_adversarial_neighbors(self):
        for n in (1, 3, 19, 2**100 + 1):
            for delta in (-1, 0, 1):
                q = F(n*n*2**40 + delta, 2**40)
                s = sqrt_interval(q, precision=90)
                self.assertLessEqual(s.lo*s.lo, q)
                self.assertGreaterEqual(s.hi*s.hi, q)

    def test_complex_47_by_2_gram_and_row_orientation(self):
        a = [[z(), z()] for _ in range(47)]
        a[0] = [z(3), z(0, 4)]
        a[1] = [z(0, 4), z(3)]
        self.assertEqual(gram2(a), (F(25), z(), F(25)))
        self.assertEqual(spectral_norm(a), Interval(F(5), F(5)))
        self.assertEqual(spectral_norm(adjoint(a)), Interval(F(5), F(5)))
        b = [[z(1, 2), z(3, 4)], [z(-1, 3), z(2, -5)]]
        self.assertEqual(gram2(b), (F(15), z(-6, -3), F(54)))

    def test_rank_one_repeated_and_zero(self):
        a = [[z(), z()] for _ in range(47)]
        self.assertEqual(spectral_norm(a).hi, 0)
        a[0] = [z(3), z(4)]
        self.assertEqual(spectral_norm(a), Interval(F(5), F(5)))

    def test_random_independent_decimal_eigen_formula(self):
        rng = random.Random(20261001)
        with localcontext() as ctx:
            ctx.prec = 160
            for _ in range(24):
                a = [[z(F(rng.randrange(-16, 17), 8), F(rng.randrange(-16, 17), 8)) for _ in range(2)] for _ in range(47)]
                # Independent accumulation uses Decimal real/imag arithmetic, not gram2.
                aa = sum(d(x[0][0])**2 + d(x[0][1])**2 for x in a)
                dd = sum(d(x[1][0])**2 + d(x[1][1])**2 for x in a)
                br = sum(d(x[0][0])*d(x[1][0]) + d(x[0][1])*d(x[1][1]) for x in a)
                bi = sum(d(x[0][0])*d(x[1][1]) - d(x[0][1])*d(x[1][0]) for x in a)
                reference = ((aa+dd+((aa-dd)**2+4*(br*br+bi*bi)).sqrt())/2).sqrt()
                result = spectral_norm(a, precision=240)
                self.assertLessEqual(d(result.lo), reference)
                self.assertGreaterEqual(d(result.hi), reference)
                self.assertLess(d(result.hi-result.lo), Decimal('1e-70'))
                self.assertEqual(result, spectral_norm(adjoint(a), precision=240))

    def test_k_adjoint_and_frozen_prediction_not_recomputed(self):
        c = [[z(), z()] for _ in range(47)]
        r = [[z() for _ in range(47)] for _ in range(2)]
        c[0][0] = z(3, 4)
        r[0][0] = z(1, 2)
        self.assertEqual(construct_k(c, r)[0][0], z(1, 3))
        zeros_c = [[z(), z()] for _ in range(47)]
        zeros_r = adjoint(zeros_c)
        stored_k = [[z(), z()] for _ in range(47)]
        stored_k[0][0] = z(7)
        e = represented_errors({'D_col': zeros_c, 'D_row': zeros_r, 'K': stored_k}, zeros_c, zeros_r)
        self.assertEqual(e['K'], Interval(F(7), F(7)))
        self.assertEqual(e['Dmax'].hi, 0)

    def test_gap_sign_and_dmax_switch(self):
        c = [[z(), z()] for _ in range(47)]
        r = adjoint(c)
        models = {}
        for name, ck, cc, rr in [('R31AK', 2, 3, 4), ('R31Z', 5, 8, 6), ('R31AD', 4, 5, 7)]:
            model = {'K': [row[:] for row in c], 'D_col': [row[:] for row in c], 'D_row': [row[:] for row in r]}
            model['K'][0][0] = z(ck)
            model['D_col'][0][0] = z(cc)
            model['D_row'][0][0] = z(rr)
            models[name] = model
        out = represented_gaps(models, c, r)
        self.assertEqual(out['PRIMARY'], {'K': Interval(F(3), F(3)), 'Dmax': Interval(F(4), F(4))})
        self.assertEqual(out['SECONDARY'], {'K': Interval(F(2), F(2)), 'Dmax': Interval(F(3), F(3))})
        self.assertEqual(interval_max(Interval(F(1), F(4)), Interval(F(2), F(3))), Interval(F(2), F(4)))

    def test_source_bound_complex_disks(self):
        a = [[z(), z()], [z(), z()]]
        b = [[ComplexDisk(z(3,4), F(1)), ComplexDisk(z(), F(0))], [ComplexDisk(z(), F(0)), ComplexDisk(z(), F(0))]]
        self.assertEqual(source_error_bound_disk(a, b), F(6))

    def test_propagate_epsilon_no_double_count(self):
        self.assertEqual(propagate_epsilon(F(2),F(4)), {'K':F(3),'Dmax':F(4)})
        with self.assertRaises(ContractError):
            propagate_epsilon(F(-1),F(0))

    def test_direct_and_legacy_bound(self):
        gap = Interval(F(3), F(4))
        self.assertEqual(direct_gap_lower(gap, F(1,4)), F(5,2))
        for ghat in (F(7,2), F(10), F(-1)):
            eta = legacy_eta(ghat, gap)
            lower = legacy_gap_lower(ghat, eta, F(1,4))
            self.assertLessEqual(lower, direct_gap_lower(gap, F(1,4)))
            self.assertGreaterEqual(eta, abs(ghat-gap.lo))
            self.assertGreaterEqual(eta, abs(ghat-gap.hi))

    def test_pareto_strict_weak_and_crossing(self):
        t = TOLERANCE
        self.assertEqual(pareto_sufficient([Interval(-t, -t), Interval(2*t, 2*t)], [F(0), F(0)])['status'], 'CERTIFIED_REAL_PARETO_SUFFICIENT_CONDITION')
        self.assertEqual(pareto_sufficient([Interval(t, t), Interval(t, t)], [F(0), F(0)])['status'], 'DECISION_BOUND_UNRESOLVED')
        self.assertEqual(pareto_sufficient([Interval(-2*t, F(0)), Interval(2*t, 2*t)], [F(0), F(0)])['status'], 'DECISION_BOUND_UNRESOLVED')
        self.assertEqual(pareto_sufficient([Interval(3*t, 3*t), Interval(3*t, 3*t)], [2*t, 2*t])['status'], 'DECISION_BOUND_UNRESOLVED')

    def test_binary64_tolerance_identity(self):
        self.assertEqual(TOLERANCE_BITS, 0x3ddb7cdfd9d7bdbb)
        self.assertEqual(TOLERANCE, F(7737125245533627, 77371252455336267181195264))
        self.assertGreater(TOLERANCE, MATHEMATICAL_TOLERANCE)

    def test_binary64_roundtrip_and_subnormal_ties(self):
        samples = [0, 1, 2, (1<<52)-1, 1<<52, 0x3ff0000000000000, 0x7fefffffffffffff, TOLERANCE_BITS]
        for b in samples:
            self.assertEqual(round_binary64(binary64_value(b)), b)
            if b:
                self.assertEqual(round_binary64(binary64_value(b | (1<<63))), b | (1<<63))
        self.assertEqual(round_binary64(F(1, 2**1075)), 0)
        self.assertEqual(round_binary64(F(3, 2**1075)), 2)
        self.assertEqual(round_binary64(F(1) + F(1, 2**53)), 0x3ff0000000000000)
        self.assertEqual(round_binary64(F(1) + F(3, 2**53)), 0x3ff0000000000002)

    def test_binary64_rounding_against_independent_host(self):
        rng = random.Random(47192)
        for _ in range(1000):
            x = F(rng.randrange(-2**120, 2**120), 2**rng.randrange(0, 220))
            self.assertEqual(round_binary64(x), bits(float(x)))

    def test_binary64_frozen_addition_boundary_differs_from_real_gap(self):
        # local = rounded(1+tol): real local > 1+tol, but old machine weak predicate passes.
        local = (bits(1.0+1e-10), bits(0.0))
        other = (bits(1.0), bits(1.0))
        out = audit_frozen_binary64(local, other)
        self.assertTrue(out['frozen_binary64_supported'])
        self.assertFalse(out['exact_gap_supported'])
        self.assertTrue(out['rounding_changes_result'])
        next_local = (local[0]+1, local[1])
        self.assertFalse(audit_frozen_binary64(next_local, other)['frozen_binary64_supported'])

    def test_binary64_scalar_audit_host_expressions(self):
        rng = random.Random(123)
        for _ in range(400):
            local = [rng.random()*10, rng.random()*10]
            other = [v+rng.choice([-1, 1])*1e-10 for v in local]
            expected = all(a <= b+1e-10 for a,b in zip(local,other)) and any(b-a > 1e-10 for a,b in zip(local,other))
            self.assertEqual(audit_frozen_binary64(tuple(map(bits,local)),tuple(map(bits,other)))['frozen_binary64_supported'], expected)
            expected_secondary = all(a <= b+1e-10 for a,b in zip(local,other)) and any(a < b-1e-10 for a,b in zip(local,other))
            self.assertEqual(audit_frozen_binary64(tuple(map(bits,local)),tuple(map(bits,other)), comparison='SECONDARY')['frozen_binary64_supported'], expected_secondary)

    def test_primary_secondary_strict_machine_boundaries_differ(self):
        local = (bits(1.0-1e-10), bits(0.0))
        other = (bits(1.0), bits(0.0))
        self.assertTrue(audit_frozen_binary64(local,other,comparison='PRIMARY')['frozen_binary64_supported'])
        self.assertFalse(audit_frozen_binary64(local,other,comparison='SECONDARY')['frozen_binary64_supported'])
        self.assertTrue(audit_frozen_binary64((local[0]-1,local[1]),other,comparison='SECONDARY')['frozen_binary64_supported'])

    def test_independent_high_precision_power_crosscheck(self):
        rng = random.Random(19247)
        with localcontext() as ctx:
            ctx.prec = 140
            def cmul(x,y):
                return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])
            def cadd(x,y):
                return (x[0]+y[0],x[1]+y[1])
            def norm(v):
                return sum(x*x+y*y for x,y in v).sqrt()
            for _ in range(4):
                a = [[z(F(rng.randrange(-9,10), 16), F(rng.randrange(-9,10), 16)) for _ in range(2)] for _ in range(47)]
                matrix = [[(d(v[0]),d(v[1])) for v in row] for row in a]
                v = [(Decimal(1),Decimal(0)),(Decimal(1),Decimal(1))]
                for iteration in range(2000):
                    w = [cadd(cmul(row[0],v[0]),cmul(row[1],v[1])) for row in matrix]
                    next_v = []
                    for j in range(2):
                        products = [cmul((row[j][0],-row[j][1]),wi) for row,wi in zip(matrix,w)]
                        next_v.append((sum(p[0] for p in products),sum(p[1] for p in products)))
                    n = norm(next_v)
                    v = [(x/n,y/n) for x,y in next_v]
                # Independent power iteration applies A then A† directly, with
                # no Gram/eigenvalue formula. This numerical check is not proof.
                reference = norm([cadd(cmul(row[0],v[0]),cmul(row[1],v[1])) for row in matrix])
                result = spectral_norm(a, precision=220)
                self.assertLessEqual(d(result.lo), reference)
                self.assertGreaterEqual(d(result.hi), reference)

    def test_decoded_c_order_adapter(self):
        class Decoded:
            shape = (2,2)
            values_c_order = (z(1),z(2),z(3),z(4))
        self.assertEqual(from_decoded(Decoded()), [[z(1),z(2)],[z(3),z(4)]])

    def test_fail_closed_resource_and_bad_inputs(self):
        with self.assertRaises(ResourceLimit):
            sqrt_interval(F(2), precision=4097)
        with self.assertRaises(ResourceLimit):
            spectral_norm([[z(),z()]]*47, limits=Limits(max_entries=4))
        with self.assertRaises(ResourceLimit):
            spectral_norm([[z(1),z(2)]], limits=Limits(max_operations=1))
        with self.assertRaises(ResourceLimit):
            sqrt_interval(F(2**100), limits=Limits(max_integer_bits=32))
        for f in [lambda: sqrt_interval(F(-1)), lambda: sqrt_interval(0.5),
                  lambda: spectral_norm([[z(1)]*3]*3), lambda: spectral_norm([[z(1), z(2)], [z(1)]]),
                  lambda: spectral_norm([[(1.0, F(0)), z()]]), lambda: construct_k([[z(),z()]], [[z(),z()]]),
                  lambda: binary64_value(0x7ff0000000000000), lambda: binary64_value(0x7ff8000000000001),
                  lambda: round_binary64(F(2**1024)), lambda: direct_gap_lower(Interval(F(0),F(1)), F(-1)),
                  lambda: legacy_eta(0.1, Interval(F(0),F(1))), lambda: Interval(F(2),F(1))]:
            with self.assertRaises(ContractError):
                f()


if __name__ == '__main__':
    unittest.main()
