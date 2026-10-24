"""UNEXECUTED future focused checks; requires a separately authorized budget.

This file is not a bounded runner. Do not launch it until root freezes and
releases a new one-child CPU/wall contract. No donor integration or L0 replay.
"""
from fractions import Fraction
import json
from pathlib import Path

from source_pair import (DomainError, ENERGY_OWNERS, PARTICLE_OWNERS,
                         load_selected_case, represented_residuals,
                         source_jvp_fixed_moments, source_per_href)


def exact_vector_reference(card, multiplier):
    # This reference starts from independently saved coefficients, never P-chi*A.
    return tuple(multiplier * Fraction(value) for value in (0, card.B, -card.P, 0, 0, card.K))


def check_vectors(card, rates, multiplier):
    exact_energy = exact_vector_reference(card, multiplier)
    rounded_energy = tuple(0 if i in (0, 3, 4) else float(value)
                           for i, value in enumerate(exact_energy))
    assert len(rates.energy_rates) == len(ENERGY_OWNERS) == 6
    assert all(Fraction(actual) == Fraction(expected)
               for actual, expected in zip(rates.energy_rates, rounded_energy))
    exact_reaction = multiplier * Fraction(card.A)
    reaction = float(exact_reaction)
    expected_particles = (-reaction, reaction, reaction, 0, -reaction)
    assert len(rates.particle_rates) == len(PARTICLE_OWNERS) == 5
    assert all(Fraction(actual) == Fraction(expected)
               for actual, expected in zip(rates.particle_rates, expected_particles))
    hi, hii, e_nt, e_th, absorbed = rates.particle_rates
    assert hi + hii == 0
    assert hii - (e_nt + e_th) == 0
    assert absorbed + hii == 0
    assert rates.e_all_rate == e_nt + e_th == hii
    assert e_th == 0 and rates.energy_rates[0] == 0
    assert rates.physical_secondary_heat_eV_per_target_s is None
    assert rates.isotropic_flux0 == (0, 0, 0)
    assert rates.isotropic_stf0 == ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    assert rates.multiplier_exact == multiplier
    r_e = Fraction(card.B) + Fraction(card.K) - Fraction(card.P)
    assert rates.expected_energy_sum_exact == multiplier * r_e == sum(exact_energy)
    # Final component rounding is distinct from the represented summary defect.
    # No tolerance or numerical acceptance is invented by this future fixture.
    return sum(map(Fraction, rates.energy_rates)) - rates.expected_energy_sum_exact


def fraction_record(value):
    return {'numerator': value.numerator, 'denominator': value.denominator}


def main():
    with Path(__file__).with_name('source_card.json').open(encoding='utf-8') as handle:
        raw = json.load(handle)
    card = load_selected_case()
    result = raw['result']
    assert (card.A, card.B, card.P, card.K) == (
        result['number_per_target_s'], result['binding_eV_per_target_s'],
        result['absorbed_photon_eV_per_target_s'], result['kinetic_eV_per_target_s'])
    assert card.K == result['kinetic_eV_per_target_s']
    assert card.physical_secondary_heat_eV_per_target_s is result['secondary_heat_eV_per_target_s'] is None
    assert card.global_error_bound is result['global_error_bound'] is None
    assert card.above_support_atomic_event_rate is raw['radiation_above_atomic_domain']['atomic_event_rate'] is None
    assert card.donor_energy_ledger_residual_eV_per_target_s == result['energy_ledger_residual_eV_per_target_s']
    residuals = represented_residuals(card)
    chi_a = Fraction(card.chi_eV) * Fraction(card.A)
    assert residuals.r_B == Fraction(card.B) - chi_a
    assert residuals.r_E == Fraction(card.B) + Fraction(card.K) - Fraction(card.P)
    assert residuals.gross_B == abs(Fraction(card.B)) + abs(chi_a)
    assert residuals.gross_E == sum(abs(Fraction(v)) for v in (card.B, card.K, card.P))

    x_hi, amplitude = Fraction(3, 7), 1.0
    source = source_per_href(card, x_hi, amplitude)
    source_rounding = check_vectors(card, source, Fraction(x_hi) * Fraction(amplitude))
    dx_hi, d_amplitude = Fraction(2, 9), Fraction(-1, 5)
    jvp = source_jvp_fixed_moments(card, x_hi, dx_hi, amplitude, d_amplitude)
    dm = Fraction(amplitude) * dx_hi + x_hi * d_amplitude
    jvp_rounding = check_vectors(card, jvp, dm)

    epsilon = Fraction(1, 2**54)
    cancellation = source_jvp_fixed_moments(card, 1, 1 + epsilon, 1.0, -1.0)
    assert cancellation.multiplier_exact == epsilon
    cancellation_rounding = check_vectors(card, cancellation, epsilon)

    refused = False
    try:
        load_selected_case(redshift=3)
    except DomainError:
        refused = True
    assert refused
    print(json.dumps({
        'fixture_group_count': 1,
        'exact_reference_source_checked': True,
        'exact_reference_fixed_moment_jvp_checked': True,
        'mixed_cancellation_direction_checked': True,
        'unsupported_z_refused': refused,
        'r_B_exact': fraction_record(residuals.r_B),
        'r_E_exact': fraction_record(residuals.r_E),
        'gross_B_exact': fraction_record(residuals.gross_B),
        'gross_E_exact': fraction_record(residuals.gross_E),
        'source_component_rounding_residual_exact': fraction_record(source_rounding),
        'jvp_component_rounding_residual_exact': fraction_record(jvp_rounding),
        'cancellation_component_rounding_residual_exact': fraction_record(cancellation_rounding),
        'ledger_tolerance_acceptance': 'NOT_EVALUATED_NO_FROZEN_CRITERION',
    }, sort_keys=True))


if __name__ == '__main__':
    main()
