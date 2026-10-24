"""One prepared future fixture; a separate current root release is required."""
from fractions import Fraction
import json
from pathlib import Path

from work_bounds import diagonal_work_bounds, enclosure_work_bounds


def pair(values):
    return tuple(Fraction(value) for value in values)


def encoded(value):
    if isinstance(value, Fraction):
        return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}
    if isinstance(value, (tuple, list)):
        return [encoded(item) for item in value]
    return value


def beam_moments(radial, axis):
    """Independent +/-axis discrete measure with algebraically separate kernel."""
    particles = [(Fraction(weight)/2, Fraction(k), axis, sign)
                 for weight, k in radial for sign in (-1, 1)]
    n = u = Fraction(0)
    stress = [Fraction(0), Fraction(0), Fraction(0)]
    signed_weights = {}
    for weight, k, direction, sign in particles:
        n += weight
        u += weight*k
        stress[direction] += weight*(k+1-Fraction(1)/(k+1))
        key = (k, direction)
        signed_weights[key] = signed_weights.get(key, Fraction(0))+sign*weight
    assert all(value == 0 for value in signed_weights.values())
    return n, u, tuple(stress)


def contraction_witness(rates, lower_endpoint):
    axis = min(range(3), key=lambda index: rates[index]) if lower_endpoint else max(
        range(3), key=lambda index: rates[index])
    rate = rates[axis]
    use_low_trace = rate >= 0 if lower_endpoint else rate < 0
    radial = [(1, 0), (1, 2)] if use_low_trace else [(2, 1)]
    n, u, stress = beam_moments(radial, axis)
    assert n == 2 and u == 2
    assert sum(stress) == (Fraction(8, 3) if use_low_trace else Fraction(3))
    return sum((Fraction(rate)*component for rate, component in zip(rates, stress)),
               Fraction(0))


def refused(name, function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError as error:
        assert name in str(error)
    else:
        raise AssertionError(f'{name}: invalid input accepted')


def main():
    cases = [((-2, 1, 4), ('-6', '12'), ('-9', '9'), ('-18', '0')),
             ((1, 2, 3), ('8/3', '9'), ('-3', '3'), ('-21', '-44/3')),
             ((-3, -2, -1), ('-9', '-8/3'), ('-3', '3'), ('44/3', '21')),
             ((2, 2, 2), ('16/3', '6'), ('0', '0'), ('-18', '-52/3')),
             ((-2, -2, -2), ('-6', '-16/3'), ('0', '0'), ('52/3', '18')),
             ((0, 0, 0), ('0', '0'), ('0', '0'), ('0', '0'))]
    summaries = []
    for rates, work, shear, derivative in cases:
        result = diagonal_work_bounds(2, 2, 2, 1, rates)
        assert result.trace_interval == pair(('8/3', '3'))
        assert result.work_interval == pair(work)
        assert result.shear_work_interval == pair(shear)
        assert result.energy_derivative_interval == pair(derivative)
        assert result.anisotropy_norm_squared_upper == 6
        assert result.claim == 'sharp_given_exact_moments'
        theta = sum(rates)
        sigma = tuple(Fraction(rate)-Fraction(theta, 3) for rate in rates)
        assert result.theta == theta and result.shear_rates == sigma
        for lower in (True, False):
            index = 0 if lower else 1
            assert contraction_witness(rates, lower) == pair(work)[index]
            assert contraction_witness(sigma, lower) == pair(shear)[index]
        assert result.energy_derivative_interval == (
            -theta*2-pair(work)[1], -theta*2-pair(work)[0])
        summaries.append({'rates': encoded(result.rates),
                          'trace': encoded(result.trace_interval),
                          'work': encoded(result.work_interval),
                          'shear_work': encoded(result.shear_work_interval),
                          'derivative': encoded(result.energy_derivative_interval)})

    n, u, stress = beam_moments([(2, 1)], 1)
    assert (n, u, stress) == (2, 2, (0, 3, 0))
    norm2 = sum(((component-Fraction(1))**2 for component in stress), Fraction(0))
    assert norm2 == 6
    baseline = diagonal_work_bounds(2, 2, 2, 1, (-2, 1, 4))
    factor = Fraction(7, 3)
    scaled = diagonal_work_bounds(2*factor, 2*factor, 2, 1, (-2, 1, 4))
    assert scaled.number_density == factor*baseline.number_density
    for field in ('energy_interval', 'trace_interval', 'work_interval',
                  'shear_work_interval', 'energy_derivative_interval'):
        assert getattr(scaled, field) == tuple(factor*x for x in getattr(baseline, field))
    assert scaled.anisotropy_norm_squared_upper == factor**2*baseline.anisotropy_norm_squared_upper
    reverse = diagonal_work_bounds(2, 2, 2, 1, (2, -1, -4))
    for field in ('work_interval', 'shear_work_interval', 'energy_derivative_interval'):
        assert getattr(reverse, field) == tuple(-x for x in reversed(getattr(baseline, field)))
    permuted = diagonal_work_bounds(2, 2, 2, 1, (4, -2, 1))
    for field in ('trace_interval', 'work_interval', 'shear_work_interval',
                  'energy_derivative_interval', 'anisotropy_norm_squared_upper'):
        assert getattr(permuted, field) == getattr(baseline, field)
    saturated = diagonal_work_bounds(2, 4, 2, 1, (-2, 1, 4))
    assert saturated.trace_interval == (Fraction(16, 3), Fraction(16, 3))
    for n, u, limit in ((0, 0, 2), (0, 0, 0), (2, 0, 0), (2, 0, 2)):
        for zero in (diagonal_work_bounds(n, u, limit, 1, (-2, 1, 4)),
                     enclosure_work_bounds(n, (u, u), limit, 1, (-2, 1, 4))):
            for field in ('trace_interval', 'work_interval', 'shear_work_interval',
                          'energy_derivative_interval'):
                assert getattr(zero, field) == (Fraction(0), Fraction(0))
            assert zero.anisotropy_norm_squared_upper == 0
            assert zero.rates == (-2, 1, 4) and zero.theta == 3
    tiny = diagonal_work_bounds(1, Fraction(1, 1 << 1075), 1, 1, (1, 1, 1))
    assert 0 < tiny.trace_interval[0] <= tiny.trace_interval[1]
    assert 0 < tiny.work_interval[0] <= tiny.work_interval[1]
    assert diagonal_work_bounds(2.0, 2.0, 2.0, 1.0, (-2.0, 1.0, 4.0)) == baseline

    for key in ('N', 'U', 'L', 'M'):
        for bad in (True, -1, '1', complex(1), float('nan'), float('inf')):
            values = dict(N=2, U=2, L=2, M=1, rates=(-2, 1, 4))
            values[key] = bad
            refused(key, diagonal_work_bounds, **values)
    refused('M', diagonal_work_bounds, 2, 2, 2, 0, (-2, 1, 4))
    refused('U', diagonal_work_bounds, 1, 3, 2, 1, (-2, 1, 4))
    for bad in ((1, 2), (1, 2, 3, 4), '123', None):
        refused('rates', diagonal_work_bounds, 2, 2, 2, 1, bad)
        refused('rates', enclosure_work_bounds, 2, (1, 2), 2, 1, bad)
    for bad in (True, float('nan'), float('inf'), '1', complex(1)):
        refused('rates[1]', diagonal_work_bounds, 2, 2, 2, 1, (1, bad, 3))
        refused('rates[1]', enclosure_work_bounds, 2, (1, 2), 2, 1, (1, bad, 3))
    for bad in ((1,), (1, 2, 3), '12', (-1, 2), (2, 1), (1, 5),
                (True, 2), (1, float('inf')), (float('nan'), 2)):
        refused('energy_interval', enclosure_work_bounds, 2, bad, 2, 1, (-2, 1, 4))
    for key in ('N', 'L', 'M'):
        for bad in (True, -1, '1', float('nan'), float('inf')):
            values = dict(N=2, energy_interval=(1, 2), L=2, M=1, rates=(-2, 1, 4))
            values[key] = bad
            refused(key, enclosure_work_bounds, **values)
    refused('M', enclosure_work_bounds, 2, (1, 2), 2, 0, (-2, 1, 4))

    outer = enclosure_work_bounds(2, (1, 2), 2, 1, (-2, 1, 4))
    assert outer.trace_interval == pair(('4/3', '3'))
    assert outer.work_interval == pair(('-6', '12'))
    assert outer.energy_derivative_interval == pair(('-18', '3'))
    assert outer.claim == 'conservative_given_energy_enclosure'

    # Consume saved raw only. N and L are separately derived, not raw fields.
    stored = json.loads((Path(__file__).resolve().parent/'inputs/stock_stdout.jsonl').read_text())
    assert stored['claim'] == 'conditional_free_streaming_outer_bounds'
    assert stored['fixture_group_count'] == 1
    assert stored['expansion_contraction_mixed_squared_oracles_checked'] is True
    selected = stored['mixed_energy_interval']
    assert len(selected) == 2
    energy = tuple(Fraction(int(value['numerator']), int(value['denominator']))
                   for value in selected)
    n0 = Fraction(2)
    ratios = (Fraction(1, 2), Fraction(1), Fraction(2))
    dilution = ratios[0]*ratios[1]*ratios[2]
    nt = dilution*n0
    assert nt == 2 and dilution == 1
    assert 33 < 36  # sqrt(33)-1 < 5, frozen analytic support majorant.
    support_majorant = Fraction(5)
    consumed = enclosure_work_bounds(nt, energy, support_majorant, 1, (-2, 1, 4))
    assert energy[0] <= 2 <= energy[1]
    witness = {'trace_interval': Fraction(3), 'work_interval': Fraction(3),
               'shear_work_interval': Fraction(0), 'energy_derivative_interval': Fraction(-9)}
    for field, value in witness.items():
        lower, upper = getattr(consumed, field)
        assert lower <= value <= upper
    assert consumed.anisotropy_norm_squared_upper >= norm2
    print(json.dumps({'fixture_group_count': 1, 'literal_cases': summaries,
                      'independent_symmetric_beam_endpoints_checked': True,
                      'norm_squared_witness_checked': True,
                      'scaling_reversal_permutation_checked': True,
                      'zero_tiny_float_domain_controls_checked': True,
                      'enclosure_literal_case_checked': True,
                      'stored_stock_mixed_raw_consumed': True,
                      'stored_stock_selection_key': 'mixed_energy_interval',
                      'stored_energy_interval': encoded(energy),
                      'derived_number_density': encoded(nt),
                      'analytic_support_majorant': encoded(support_majorant),
                      'transported_axis2_witness_checked': True,
                      'consumed_trace_interval': encoded(consumed.trace_interval),
                      'consumed_work_interval': encoded(consumed.work_interval),
                      'consumed_derivative_interval': encoded(consumed.energy_derivative_interval),
                      'claim': consumed.claim}, sort_keys=True))


if __name__ == '__main__':
    main()
