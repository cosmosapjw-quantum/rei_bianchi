"""KF96 Table 1 He2+ nominal prescription as a separate, opt-in scenario.

Kingdon & Ferland (1996), DOI 10.1086/192335, pp. 206-207, Eq. (7),
Table 1: a=1.00(-5) in units of 1e-9 cm3/s; b=c=d=0. The printed lower
range marker is approximate. The strict numerical API window is a policy,
not a physical threshold. No precise total rate, uncertainty or spectrum
is inferred. The W82 ground-state reaction mapping is explicit and separate
from KF96's element/charge row; no isotope-dependent scaling is performed.
"""
from __future__ import annotations
from decimal import Decimal, localcontext
from typing import Any
from ._rate import ContractError, SourceUnavailable, _number

SOURCE_ID = 'KF96_HEIII_HI_RCT_NOMINAL_V1'
REACTION_ID = 'R_CX:He2+_H1s:He+1s_H+'
DISTRIBUTION = 'MAXWELL_COMMON_T_ZERO_DRIFT'
K_CGS = '1.00E-14'
K_SI = '1.00E-20'
TMIN = Decimal('1000')
TMAX = Decimal('10000000')


def rate(temperature: Any, *, source_id: str | None = None,
         distribution: str | None = None, acknowledge_source_conflict: bool = False,
         unit: str = 'm3 s-1', temperature_unit: str = 'K',
         initial_state: str = 'H1s', isotope_basis: str = 'SOURCE_W82_4HE_H',
         relative_drift_m_s: Any = 0,
         radiation_model: str = 'SPONTANEOUS_SINGLE_PHOTON') -> dict[str, Any]:
    """Return KF96's selected constant, never clamp or sum competing sources."""
    if source_id != SOURCE_ID:
        raise ContractError('EXPLICIT_SUPPORTED_SOURCE_SELECTION_REQUIRED')
    if acknowledge_source_conflict is not True:
        raise ContractError('ACKNOWLEDGE_UNRESOLVED_SOURCE_DISAGREEMENT')
    if distribution != DISTRIBUTION or _number(relative_drift_m_s, 'drift') != 0:
        raise ContractError('SOURCE_REQUIRES_ZERO_DRIFT_COMMON_T_MAXWELLIAN')
    if temperature_unit != 'K':
        raise ContractError('KELVIN_REQUIRED_NO_IMPLICIT_EV_CONVERSION')
    if initial_state != 'H1s' or isotope_basis != 'SOURCE_W82_4HE_H':
        raise ContractError('SOURCE_INITIAL_STATE_OR_ISOTOPE_NOT_SUPPORTED')
    if radiation_model != 'SPONTANEOUS_SINGLE_PHOTON':
        raise ContractError('STIMULATED_OR_MULTIPHOTON_EXTENSION_UNAVAILABLE')
    if unit not in ('m3 s-1', 'cm3 s-1'):
        raise ContractError('RATE_UNIT_REQUIRED')
    t = _number(temperature, 'temperature')
    if not TMIN <= t <= TMAX:
        raise ContractError('OUTSIDE_NOMINAL_TABLE_WINDOW_NO_EXTRAPOLATION')
    k = K_SI if unit == 'm3 s-1' else K_CGS
    side = 'right' if t == TMIN else ('left' if t == TMAX else 'two_sided')
    return {
        'schema': 'bass-he.rcx.rate.v1', 'source_id': SOURCE_ID,
        'reaction_id': REACTION_ID, 'T_K': str(t), 'rate_token': k,
        'source_location': {
            'doi': '10.1086/192335', 'equation': '7',
            'table': '1, He2+ row and footnote a', 'printed_pages': [206, 207],
            'row_reference': 'West, Lane & Cohen 1982',
            'mechanism_source_doi': '10.1103/PhysRevA.26.3164',
            'original_cross_section_integration_reproduced': False,
        },
        'rate_binary64': float(k), 'unit': unit,
        'data_kind': 'NOMINAL_COMPILATION_THERMAL_RATE_PRESCRIPTION',
        'rate_semantics': 'NOMINAL_COMPILATION_PRESCRIPTION_NOT_PRECISE_TOTAL_RATE',
        'reported_domain_K': ['1000', '10000000'],
        'table_temperature_token': '~1(3)-1(7)',
        'lower_endpoint_is_approximate_in_source': True,
        'boundary_policy': 'STRICT_NUMERIC_WINDOW_NO_CLAMP_OR_EXTRAPOLATION',
        'distribution': distribution, 'isotope_basis': isotope_basis,
        'isotope_note': 'KF96 isotope unresolved; explicit W82 scenario mapping, no mass rescaling',
        'isotope_source_resolved': False,
        'state_mapping_kind': 'EXPLICIT_W82_GROUND_STATE_RCT_SCENARIO',
        'dk_dT_token': '0', 'dk_dT_unit': unit + ' K-1', 'derivative_side': side,
        'derivative_semantics': 'CONSTANT_PRESCRIPTION_ONLY_NOT_PHYSICAL_SLOPE',
        'source_uncertainty': None, 'fit_error_bound': None,
        'source_disagreement': 'GM25 nominal coefficient is 17 times KF96 in common 1000-10000 K window',
        'conflict_resolved': False, 'coefficient_native_token': K_CGS,
        'coefficient_native_unit': 'cm3 s-1', 'cgs_to_si_exact_factor': '1E-6',
        'physical_accuracy_certified': False, 'new_scattering_calculation': False,
        'raw_sigma_available': False, 'production_admission': 'NOT_GRANTED_BY_THIS_ADAPTER',
        'photon_energy_moment': None, 'heat_moment': None, 'recoil_moment': None,
        'inverse_reaction_rate': None,
    }


def count_coefficients(temperature: Any, **kwargs: Any) -> dict[str, Any]:
    """Rate/count are two views of one reaction, not additive contributions."""
    result = rate(temperature, **kwargs)
    nu = [-1, 1, 0, 1, -1, 0]
    with localcontext() as ctx:
        ctx.prec = 34
        k = Decimal(result['rate_token'])
        coeff = [str(k * n) for n in nu]
    return {
        **result, 'data_kind': 'ATOMIC_EVENT_COUNT_COEFFICIENT_PACKET',
        'species_order': ['HI', 'HII', 'HeI', 'HeII', 'HeIII', 'e'],
        'stoichiometry': nu, 'species_rate_coefficients': coeff,
        'multiplying_density_pair': ['HI', 'HeIII'], 'free_electron_delta': 0,
        'photon_number_per_event': 1, 'photon_count_rate_token': result['rate_token'],
        'photon_count_semantics': 'EXPLICIT_W82_SINGLE_PHOTON_RCT_SCENARIO_NOT_KF96_SPECTRUM',
        'net_charge_delta': 0, 'H_nuclei_delta': 0, 'He_nuclei_delta': 0,
        'count_only_packet': True, 'zero_missing_moment_fill': False,
    }
