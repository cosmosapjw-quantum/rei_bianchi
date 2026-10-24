"""UNEXECUTED single future fixture group; no execution authorization here."""
from fractions import Fraction
import json

from pressure_interval import (DomainError, pressure_interval_from_moments,
                               pressure_moment_from_atoms)


def independent_atom_reference(atoms, rest):
    rest = Fraction(rest)
    count = sum((Fraction(weight) for weight, _ in atoms), Fraction(0))
    energy = sum((Fraction(weight)*Fraction(k) for weight, k in atoms), Fraction(0))
    # Algebraically independent form of g(k): k+M-M^2/(k+M).
    pressure = sum((Fraction(weight)*(Fraction(k)+rest-rest**2/(Fraction(k)+rest))/3
                    for weight, k in atoms), Fraction(0))
    return count, energy, pressure


def main():
    interval = pressure_interval_from_moments(2, 2, 2, 1)
    assert interval.lower == Fraction(8, 9)
    assert interval.upper == Fraction(1)
    assert interval.width == Fraction(1, 9)
    assert interval.nr_pressure == Fraction(4, 3)
    assert interval.nr_error_upper == Fraction(4, 9)

    lower_atoms = [(1, 0), (1, 2)]
    upper_atoms = [(2, 1)]
    middle_atoms = [(Fraction(1, 2), 0), (Fraction(1, 2), 2), (1, 1)]
    for atoms, expected in ((lower_atoms, Fraction(8, 9)),
                             (upper_atoms, Fraction(1)),
                             (middle_atoms, Fraction(17, 18))):
        actual = pressure_moment_from_atoms(atoms, M=1, L=2)
        reference = independent_atom_reference(atoms, 1)
        assert (actual.N, actual.U, actual.pressure) == reference
        assert actual.N == 2 and actual.U == 2 and actual.pressure == expected
        assert interval.lower <= actual.pressure <= interval.upper
        error = interval.nr_pressure - actual.pressure
        assert 0 <= error <= interval.nr_error_upper

    for N, U, L in ((0, 0, 2), (0, 0, 0), (2, 0, 0), (2, 0, 2)):
        zero = pressure_interval_from_moments(N, U, L, 1)
        assert all(value == Fraction(0) for value in (
            zero.lower, zero.upper, zero.width, zero.nr_pressure, zero.nr_error_upper))
    empty = pressure_moment_from_atoms([], M=1, L=0)
    assert (empty.N, empty.U, empty.pressure) == (Fraction(0),)*3
    at_zero = pressure_moment_from_atoms([(2, 0)], M=1, L=0)
    assert (at_zero.N, at_zero.U, at_zero.pressure) == (Fraction(2), Fraction(0), Fraction(0))

    refused = False
    try:
        pressure_interval_from_moments(1, 3, 2, 1)
    except DomainError:
        refused = True
    assert refused

    factor = Fraction(7, 3)
    original = pressure_moment_from_atoms(middle_atoms, M=1, L=2)
    scaled_atoms = [(factor*weight, k) for weight, k in middle_atoms]
    scaled = pressure_moment_from_atoms(scaled_atoms, M=1, L=2)
    assert (scaled.N, scaled.U, scaled.pressure) == tuple(
        factor*value for value in (original.N, original.U, original.pressure))
    assert (scaled.N, scaled.U, scaled.pressure) == independent_atom_reference(scaled_atoms, 1)
    scaled_interval = pressure_interval_from_moments(scaled.N, scaled.U, 2, 1)
    for name in ('lower', 'upper', 'width', 'nr_pressure', 'nr_error_upper'):
        assert getattr(scaled_interval, name) == factor*getattr(interval, name)
    print(json.dumps({'fixture_group_count': 1, 'paper_endpoints_checked': True,
                      'independent_atom_reference_checked': True,
                      'half_mixture_checked': True, 'zero_boundaries_checked': True,
                      'invalid_moment_refused': refused, 'common_scaling_checked': True,
                      'interpretation': 'conditional positive-measure arithmetic only'}, sort_keys=True))


if __name__ == '__main__':
    main()
