"""He2+ + H(1s) radiative charge-transfer thermal-rate adapter.

Source: Garcia Munoz et al., arXiv:2511.21966v1, Appendix B.3, PDF page 9.
The authors quote a constant approximation to their integration of West et al.
(1982), NOT a table of original cross sections or a quantified uncertainty.
No automatic choice between conflicting source compilations is made.
"""
from __future__ import annotations
from collections.abc import Sequence
from decimal import Decimal, InvalidOperation, localcontext
import re
from typing import Any

SOURCE_ID = 'GM25_W82_RCX_CONSTANT_200_10000_K_V1'
DISTRIBUTION = 'MAXWELL_COMMON_T_ZERO_DRIFT'
REACTION_ID = 'R_CX:He2+_H1s:He+1s_H+'
K_CGS = '1.70E-13'
K_SI = '1.70E-19'
TMIN = Decimal('200')
TMAX = Decimal('10000')

class ContractError(ValueError):
    """Input contradicts the source-limited API."""

class SourceUnavailable(ContractError):
    """Requested physical information is absent from the admitted rate source."""


def parse_fit_excerpt(text: str) -> dict[str, str]:
    """Parse the recorded author sentence; never silently retune source values.

    The caller must separately bind the excerpt provenance. A matching sentence
    or its locally computed SHA alone does not prove publisher byte identity.
    """
    if not isinstance(text, str) or len(text) > 4096:
        raise ContractError('INVALID_FIT_EXCERPT')
    s = ' '.join(text.split())
    pattern = (r'Its value is well approximated from ([0-9,]+) to ([0-9,]+) K by the '
               r'temperature-independent value ([0-9]+\.[0-9]+)×10([−-][0-9]+) cm3s[−-]1\.')
    m = re.fullmatch(pattern, s)
    if m is None:
        raise ContractError('SOURCE_SENTENCE_FORMAT_MISMATCH')
    lo, hi, mantissa, exponent = m.groups()
    lo, hi = lo.replace(',', ''), hi.replace(',', '')
    token = mantissa + 'E' + exponent.replace('−', '-')
    if (lo, hi, token) != ('200', '10000', K_CGS):
        raise ContractError('SOURCE_PARAMETERS_CHANGED_REVIEW_REQUIRED')
    return {'coefficient_token': token, 'Tmin_K': lo, 'Tmax_K': hi,
            'native_unit': 'cm3 s-1', 'source_id': SOURCE_ID}


def _number(value: Any, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise ContractError(name + ': REAL_SCALAR_REQUIRED')
    s = str(value)
    if len(s) > 128:
        raise ContractError(name + ': EXCESSIVE_TOKEN_LENGTH')
    try:
        v = Decimal(s)
    except InvalidOperation as exc:
        raise ContractError(name + ': INVALID_NUMBER') from exc
    if not v.is_finite():
        raise ContractError(name + ': FINITE_NUMBER_REQUIRED')
    return v


def rate(temperature: Any, *, source_id: str | None = None,
         distribution: str | None = None, acknowledge_source_conflict: bool = False,
         unit: str = 'm3 s-1', temperature_unit: str = 'K',
         initial_state: str = 'H1s', isotope_basis: str = 'SOURCE_W82_4HE_H',
         relative_drift_m_s: Any = 0,
         radiation_model: str = 'SPONTANEOUS_SINGLE_PHOTON') -> dict[str, Any]:
    """Evaluate the explicitly selected author fit on 200 <= T/K <= 10000.

    Zero temperature derivative is a property of this approximation only.
    Inferred photon energy, heating, inverse reaction and nonthermal rates are
    intentionally not part of the returned data.
    """
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
        raise ContractError('OUTSIDE_REPORTED_FIT_DOMAIN_NO_EXTRAPOLATION')
    k = K_SI if unit == 'm3 s-1' else K_CGS
    endpoint = 'right' if t == TMIN else ('left' if t == TMAX else 'two_sided')
    return {
        'schema': 'bass-he.rcx.rate.v1', 'source_id': SOURCE_ID,
        'reaction_id': REACTION_ID, 'T_K': str(t), 'rate_token': k,
        'source_location': {'arxiv':'2511.21966v1','section':'Appendix B.3','pdf_page':9,
            'ancestral_cross_section_doi':'10.1103/PhysRevA.26.3164',
            'original_cross_section_integration_reproduced':False},
        'rate_binary64': float(k), 'unit': unit,
        'data_kind': 'AUTHOR_REANALYSIS_THERMAL_RATE_FIT',
        'reported_domain_K': ['200', '10000'], 'distribution': distribution,
        'isotope_basis': isotope_basis, 'isotope_note': 'W82 ancestry; no mass rescaling performed',
        'dk_dT_token': '0', 'dk_dT_unit': unit + ' K-1', 'derivative_side': endpoint,
        'derivative_semantics': 'CONSTANT_FIT_ONLY_NOT_PHYSICAL_SLOPE',
        'source_uncertainty': None, 'fit_error_bound': None,
        'source_disagreement': 'GM25 reports more than order-of-magnitude difference from KF96',
        'conflict_resolved': False, 'coefficient_native_token': K_CGS,
        'coefficient_native_unit': 'cm3 s-1',
        'cgs_to_si_exact_factor': '1E-6', 'physical_accuracy_certified': False,
        'new_scattering_calculation': False, 'raw_sigma_available': False,
        'production_admission': 'NOT_GRANTED_BY_THIS_ADAPTER',
        'photon_energy_moment': None, 'heat_moment': None, 'recoil_moment': None,
        'inverse_reaction_rate': None,
    }


def batch(temperatures: Sequence[Any], **kwargs: Any) -> list[dict[str, Any]]:
    """Strict whole-batch operation; any bad element rejects the batch."""
    if isinstance(temperatures, (str, bytes)) or not isinstance(temperatures, Sequence):
        raise ContractError('FINITE_SEQUENCE_REQUIRED')
    if not 1 <= len(temperatures) <= 100000:
        raise ContractError('BATCH_SIZE_OUTSIDE_1_TO_100000')
    return [rate(t, **kwargs) for t in temperatures]


def count_coefficients(temperature: Any, **kwargs: Any) -> dict[str, Any]:
    """Species/photon number coefficients to multiply by n_HI * n_HeIII.

    No densities, cosmological clock, transport or fluid evolution are supplied.
    One emitted photon follows from the single-photon radiative mechanism,
    not from a photon-spectrum moment extracted from the thermal rate.
    """
    result = rate(temperature, **kwargs)
    nu = [-1, 1, 0, 1, -1, 0]
    with localcontext() as ctx:
        ctx.prec = 34
        k = Decimal(result['rate_token'])
        coeff = [str(k * v) for v in nu]
    return {**result, 'data_kind': 'ATOMIC_EVENT_COUNT_COEFFICIENT_PACKET',
            'species_order': ['HI', 'HII', 'HeI', 'HeII', 'HeIII', 'e'],
            'stoichiometry': nu, 'species_rate_coefficients': coeff,
            'multiplying_density_pair': ['HI', 'HeIII'],
            'free_electron_delta': 0, 'photon_number_per_event': 1,
            'photon_count_rate_token': result['rate_token'],
            'photon_count_semantics': 'DERIVED_SINGLE_PHOTON_RC_X_MECHANISM',
            'net_charge_delta': 0, 'H_nuclei_delta': 0, 'He_nuclei_delta': 0,
            'count_only_packet': True, 'zero_missing_moment_fill': False}


def require_moment(name: str, *, source_id: str | None = None) -> None:
    """Deliberately fail closed instead of inverting a thermal fit into spectra."""
    if source_id != SOURCE_ID:
        raise ContractError('EXPLICIT_SUPPORTED_SOURCE_SELECTION_REQUIRED')
    known = {'cross_section', 'heat', 'mean_photon_energy', 'photon_spectrum', 'recoil', 'inverse_rate'}
    if name not in known:
        raise ContractError('UNKNOWN_MOMENT')
    raise SourceUnavailable(name + ': NOT_DETERMINED_BY_THERMAL_RATE_FIT')
