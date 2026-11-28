"""Research-only exact-arithmetic checks; imports no BASS_HE production code.

Input bands enclose nonnegative component magnitudes, not spectral roots.
Conditional conclusions do not supply or authenticate those input enclosures.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import random
import sys


def band(lo: F, hi: F, *, positive: bool = False) -> tuple[F, F]:
    if type(lo) is not F or type(hi) is not F:
        raise TypeError('exact Fraction endpoints required')
    if lo < 0 or hi < lo or (positive and lo <= 0):
        raise ValueError('invalid nonnegative/positive enclosure')
    return lo, hi


def normalized_norm2_bounds(magnitudes, scales):
    if not magnitudes or len(magnitudes) != len(scales):
        raise ValueError('compatible nonempty component bands required')
    lo = hi = F(0)
    for (al, au), (sl, su) in zip(magnitudes, scales):
        band(al, au)
        band(sl, su, positive=True)
        lo += (al / su) ** 2
        hi += (au / sl) ** 2
    return lo, hi


def bottleneck_squared(d):
    if len(d) != 4:
        raise ValueError('four squared distances in row-major order required')
    if any(type(x) is not F or x < 0 for x in d):
        raise ValueError('nonnegative exact squared distances required')
    return min(max(d[0], d[3]), max(d[1], d[2]))


def matching_bounds(distance_bands):
    if len(distance_bands) != 4:
        raise ValueError('four distance bands required')
    checked = [band(*b) for b in distance_bands]
    return (bottleneck_squared([x[0] for x in checked]),
            bottleneck_squared([x[1] for x in checked]))


def classify(eband, tau):
    lower, upper = band(*eband)
    if type(tau) is not F or tau <= 0:
        raise ValueError('positive exact policy threshold required')
    if upper <= tau * tau:
        return 'CONDITIONAL_PASS'
    if lower > tau * tau:
        return 'CONDITIONAL_REJECT'
    return 'UNRESOLVED'


def main(out: Path):
    rng = random.Random(20260929)
    checked_samples = 0
    checked_corners = 0
    for _ in range(1000):
        # Two common positive normalization scales, both uncertain.
        sl = [F(rng.randint(10, 40), 10) for _ in range(2)]
        su = [x + F(rng.randint(0, 10), 10) for x in sl]
        scales = list(zip(sl, su))
        s = [a + F(rng.randint(0, 16), 16) * (b - a) for a, b in scales]
        dbands, point = [], []
        for _pair in range(4):
            al = [F(rng.randint(0, 30), 100) for _ in range(2)]
            au = [x + F(rng.randint(0, 20), 1000) for x in al]
            abands = list(zip(al, au))
            a = [x + F(rng.randint(0, 16), 16) * (y - x) for x, y in abands]
            dbands.append(normalized_norm2_bounds(abands, scales))
            point.append(sum(((x / y) ** 2 for x, y in zip(a, s)), F(0)))
        lower, upper = matching_bounds(dbands)
        actual = bottleneck_squared(point)
        assert lower <= actual <= upper
        checked_samples += 1
        # Exhaustive scalar-distance box corners test the Min/Max enclosure.
        for corner in product(*dbands):
            assert lower <= bottleneck_squared(corner) <= upper
            checked_corners += 1

    # Use the exact binary64 policy value, not an assumed decimal equality.
    tau = F.from_float(5e-6)
    t2 = tau * tau
    boundaries = {
        'point_at_threshold': classify((t2, t2), tau),
        'upper_at_threshold': classify((F(0), t2), tau),
        'lower_at_threshold_upper_above': classify((t2, 2*t2), tau),
        'strictly_above': classify((2*t2, 3*t2), tau),
        'straddling': classify((t2/2, 2*t2), tau),
        'zero': classify((F(0), F(0)), tau),
    }
    assert list(boundaries.values()) == [
        'CONDITIONAL_PASS', 'CONDITIONAL_PASS', 'UNRESOLVED',
        'CONDITIONAL_REJECT', 'UNRESOLVED', 'CONDITIONAL_PASS']

    # Zero-width bands must return the exact scalar calculation.
    fixed = [F(1, 16), F(9, 16), F(1, 4), F(1, 8)]
    assert matching_bounds([(x, x) for x in fixed]) == (F(1, 8), F(1, 8))
    # Wrong-direction denominator would underestimate the upper bound.
    lower, upper = normalized_norm2_bounds([(F(1), F(1))], [(F(1), F(2))])
    assert (lower, upper) == (F(1, 4), F(1))
    assert (F(1) / F(2))**2 < F(1)  # deliberate frozen-scale counterexample

    invalid = 0
    for fn in [lambda: band(F(2), F(1)), lambda: band(F(-1), F(0)),
               lambda: normalized_norm2_bounds([(F(1), F(1))], [(F(0), F(1))]),
               lambda: band(True, F(1)), lambda: classify((F(0), F(1)), F(0))]:
        try:
            fn()
        except (ValueError, TypeError):
            invalid += 1
        else:
            raise AssertionError('invalid input was accepted')
    result = {
        'schema': 'bass_he.r7.exact_scaled_matching_checks.v1',
        'status': 'PASS',
        'scope': 'CONDITIONAL_RESEARCH_FORMULAS_ONLY',
        'arithmetic': 'Python fractions.Fraction; no floating-point bound arithmetic',
        'rational_samples': checked_samples,
        'distance_box_corners': checked_corners,
        'observed_enclosure_violations': 0,
        'boundary_cases': boundaries,
        'invalid_contracts_rejected': invalid,
        'zero_width_limit': 'PASS',
        'frozen_scale_negative_control_detected': True,
        'policy_float_hex': (5e-6).hex(),
        'policy_exact_fraction': str(tau),
        'seed': 20260929,
        'production_imports': 0,
        'spectral_solves': 0,
        'geometry_actions': 0,
        'actual_spectral_enclosures_available': False,
        'Eq55': 'NOT_RUN',
    }
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv)>1 else Path('EXACT_CHECKS.json'))
