"""One future fixture group. STATIC_PREPARED; no current execution release."""
from fractions import Fraction
import json

from stock_bounds import kinetic_map_interval, stock_bounds


def check_radical(enclosure, coefficient, radicand, offset):
    """Independent exact squared oracle for a*sqrt(q)+b, with a>0."""
    lower, upper = enclosure
    coefficient, radicand, offset = map(Fraction, (coefficient, radicand, offset))
    assert coefficient > 0 and lower <= upper
    left = (lower-offset)/coefficient
    right = (upper-offset)/coefficient
    assert right >= 0 and right*right >= radicand
    assert left <= 0 or left*left <= radicand


def refused(name, function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError as error:
        assert name in str(error)
    else:
        raise AssertionError(f'{name}: invalid input accepted')


def serial(interval):
    return [{'numerator': str(value.numerator), 'denominator': str(value.denominator)}
            for value in interval]


def main():
    identity = stock_bounds(2, 2, 2, 1, (1, 1, 1))
    assert identity.number_density == 2 and identity.dilution == 1
    assert identity.energy_interval == (Fraction(2), Fraction(2))
    assert identity.support_upper_enclosure == (Fraction(2), Fraction(2))
    assert identity.pressure_trace_interval == (Fraction(8, 9), Fraction(1))

    expansion = stock_bounds(2, 2, 2, 1, (Fraction(1, 2),)*3)
    assert expansion.dilution == Fraction(1, 8)
    check_radical(expansion.lower_energy_bound_enclosure, Fraction(1, 8), 7, Fraction(-1, 4))
    check_radical(expansion.upper_energy_bound_enclosure, Fraction(1, 8), 3, Fraction(-1, 8))
    contraction = stock_bounds(2, 2, 2, 1, (2, 2, 2))
    assert contraction.dilution == 8
    check_radical(contraction.lower_energy_bound_enclosure, 8, 33, -8)
    check_radical(contraction.upper_energy_bound_enclosure, 16, 13, -16)
    mixed = stock_bounds(2, 2, 2, 1, (Fraction(1, 2), 1, 2))
    assert mixed.dilution == 1
    check_radical(mixed.lower_energy_bound_enclosure, 1, 7, -2)
    check_radical(mixed.upper_energy_bound_enclosure, 2, 13, -2)
    check_radical(mixed.support_upper_enclosure, 1, 33, -1)

    tiny_k = Fraction(1, 1 << 200)
    tiny = kinetic_map_interval(tiny_k, 1, Fraction(1, 2), bits=64)
    assert 0 < tiny[0] <= tiny[1]
    Q = 1 + Fraction(1, 4)*tiny_k*(tiny_k+2)
    assert (tiny[0]+1)**2 <= Q <= (tiny[1]+1)**2

    for n, u, limit in ((0, 0, 2), (0, 0, 0), (2, 0, 0), (2, 0, 2)):
        zero = stock_bounds(n, u, limit, 1, (Fraction(1, 2), 1, 2))
        for field in ('energy_interval', 'lower_energy_bound_enclosure',
                      'upper_energy_bound_enclosure', 'pressure_trace_interval'):
            assert getattr(zero, field) == (Fraction(0), Fraction(0))
        assert zero.number_density == n
        check_radical(zero.support_upper_enclosure, 1, 1+4*limit*(limit+2), -1)

    refused('U', stock_bounds, 1, 3, 2, 1, (1, 1, 1))
    for bad in (0, -1):
        refused('M', stock_bounds, 2, 2, 2, bad, (1, 1, 1))
        refused('ratios[1]', stock_bounds, 2, 2, 2, 1, (1, bad, 1))
        refused('r', kinetic_map_interval, 1, 1, bad)
    for bad in ((1, 1), (1, 1, 1, 1), '111'):
        refused('ratios', stock_bounds, 2, 2, 2, 1, bad)
    for key in ('N', 'U', 'L', 'M'):
        values = dict(N=2, U=2, L=2, M=1, ratios=(1, 1, 1))
        values[key] = True
        refused(key, stock_bounds, **values)
    refused('ratios[0]', stock_bounds, 2, 2, 2, 1, (True, 1, 1))
    refused('k', kinetic_map_interval, True, 1, 1)
    for bad in (True, 0, 4097, 1.5):
        refused('bits', stock_bounds, 2, 2, 2, 1, (1, 1, 1), bits=bad)
        refused('bits', kinetic_map_interval, 1, 1, 1, bits=bad)

    factor = Fraction(7, 3)
    scaled = stock_bounds(2*factor, 2*factor, 2, 1, (Fraction(1, 2), 1, 2))
    assert scaled.number_density == factor*mixed.number_density
    assert scaled.dilution == mixed.dilution
    assert scaled.support_upper_enclosure == mixed.support_upper_enclosure
    for field in ('energy_interval', 'lower_energy_bound_enclosure',
                  'upper_energy_bound_enclosure', 'pressure_trace_interval'):
        assert getattr(scaled, field) == tuple(factor*x for x in getattr(mixed, field))
    print(json.dumps({'fixture_group_count': 1, 'identity_checked': True,
                      'expansion_contraction_mixed_squared_oracles_checked': True,
                      'tiny_positive_squared_oracle_checked': True,
                      'zero_and_invalid_inputs_checked': True,
                      'common_weight_scaling_checked': True,
                      'mixed_energy_interval': serial(mixed.energy_interval),
                      'mixed_sharp_lower_enclosure': serial(mixed.lower_energy_bound_enclosure),
                      'mixed_sharp_upper_enclosure': serial(mixed.upper_energy_bound_enclosure),
                      'claim': mixed.claim}, sort_keys=True))


if __name__ == '__main__':
    main()
