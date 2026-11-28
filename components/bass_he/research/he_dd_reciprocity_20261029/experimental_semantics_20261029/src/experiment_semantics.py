"""BASS_HE HE_EXFOR_DETECTOR_EVENT_SEMANTICS, fail-closed evidence gate.

This is a conditional experiment-identity checker, not a source of physical
4He(gamma,dd) rates. No default value of kappa or event/particle convention.
Parent Git HEAD: 9328ebc6f4601ec437054aeb1f60315abc8b00a4.
"""
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Literal

MA = Fraction('3727.3794118')  # frozen alpha rest energy [MeV]
MD = Fraction('1875.61294500')  # frozen deuteron rest energy [MeV]
SOURCE_COMMIT = '939a14d7bba1ddce51975cb5e8711ce96b3b0871'
SOURCE_SHA256 = 'b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f'
SOURCE_GIT_BLOB = 'c49433293921dbb012d7f1b0387745732a598efa'
MeasurementKind = Literal['PHOTON_ALPHA_TO_DD', 'DD_TO_ALPHA_PHOTON']


def exact(value: Fraction | int | str | Decimal) -> Fraction:
    if isinstance(value, (bool, float)):
        raise TypeError('rounded float and bool are not source-qualified')
    if not isinstance(value, (Fraction, int, str, Decimal)):
        raise TypeError('exact decimal/string/integer/fraction input required')
    return Fraction(value)


def s_forward(e_gamma):
    energy = exact(e_gamma)
    if energy < 0:
        raise ValueError('negative energy')
    return MA**2 + 2 * MA * energy


def s_inverse(t_deuteron):
    energy = exact(t_deuteron)
    if energy < 0:
        raise ValueError('negative kinetic energy')
    return 4 * MD**2 + 2 * MD * energy


def match_inverse_t(e_gamma):
    value = (s_forward(e_gamma) - 4 * MD**2) / (2 * MD)
    if value < 0:
        raise ValueError('forward channel below dd threshold')
    return value


def match_forward_e(t_deuteron):
    return (s_inverse(t_deuteron) - MA**2) / (2 * MA)


def exact_s_comparison(e_gamma, t_deuteron) -> dict:
    """Exact s equality, not detector energy-bin / energy-resolution equivalence."""
    sf, si = s_forward(e_gamma), s_inverse(t_deuteron)
    return {'same_s': sf == si, 'delta_s_MeV2': str(si - sf),
            'matched_Td_MeV': str(match_inverse_t(e_gamma)),
            'matched_Egamma_MeV': str(match_forward_e(t_deuteron))}


@dataclass(frozen=True)
class SourceQualification:
    doi: str
    measurement: MeasurementKind
    record_kind: Literal['EXFOR_COMPILATION', 'PUBLISHER_ABSTRACT', 'ORIGINAL_FULLTEXT']
    raw_DA_nb_sr: Fraction | None
    reported_incident_energy_MeV: Fraction | None = None
    reported_cm_angle_deg: Fraction | None = None
    angular_time_reversal_map: str | None = None
    original_fulltext_locator: str | None = None
    angular_acceptance_definition: str | None = None
    coincidence_efficiency_definition: str | None = None
    event_particle_normalization_definition: str | None = None
    beam_polarization_definition: str | None = None
    detector_calibration_identity: str | None = None

    def unresolved(self) -> tuple[str, ...]:
        fields = ('original_fulltext_locator', 'angular_time_reversal_map', 'angular_acceptance_definition',
                  'coincidence_efficiency_definition',
                  'event_particle_normalization_definition',
                  'beam_polarization_definition', 'detector_calibration_identity')
        return tuple(f for f in fields if getattr(self, f) is None)


ARENDS = SourceQualification(
    doi='10.1016/0370-2693(76)90671-7', measurement='PHOTON_ALPHA_TO_DD',
    record_kind='EXFOR_COMPILATION', raw_DA_nb_sr=Fraction('0.41'),
    reported_incident_energy_MeV=Fraction(213), reported_cm_angle_deg=Fraction(73),
)
SILVERMAN = SourceQualification(
    doi='10.1103/PhysRevC.29.35', measurement='DD_TO_ALPHA_PHOTON',
    record_kind='PUBLISHER_ABSTRACT', raw_DA_nb_sr=None,
    reported_incident_energy_MeV=Fraction(376), reported_cm_angle_deg=Fraction(73),
)


def examine_pair(
    forward: SourceQualification, inverse: SourceQualification,
    e_gamma, t_deuteron,
) -> dict:
    """No implied angular match, interpolation, polarization average or kappa."""
    if (forward.measurement != 'PHOTON_ALPHA_TO_DD'
            or inverse.measurement != 'DD_TO_ALPHA_PHOTON'):
        raise ValueError('forward/inverse physical channel identity mismatch')
    invariant = exact_s_comparison(e_gamma, t_deuteron)
    blocked = list(forward.unresolved()) + ['inverse_' + x for x in inverse.unresolved()]
    if forward.reported_incident_energy_MeV != exact(e_gamma):
        blocked.append('FORWARD_SOURCE_ROW_ENERGY_MISMATCH')
    if inverse.reported_incident_energy_MeV != exact(t_deuteron):
        blocked.append('INVERSE_SOURCE_ROW_ENERGY_MISMATCH')
    if not invariant['same_s']:
        blocked.append('EXACT_INVARIANT_S_MISMATCH')
    if inverse.raw_DA_nb_sr is None:
        blocked.append('INVERSE_RAW_DA_UNAVAILABLE')
    if forward.raw_DA_nb_sr is None:
        blocked.append('FORWARD_RAW_DA_UNAVAILABLE')
    return {**invariant,
            'inverse_raw_DA_source_qualified': inverse.raw_DA_nb_sr is not None,
            'evidence_gaps': tuple(dict.fromkeys(blocked)),
            'kappa': None, 'R_event': None, 'physical_activation': False,
            'L4': False, 'production': 'HOLD'}


REQUIRED_PHYSICAL_INPUTS = (
    'event_normalization_original_source', 'efficiency_and_acceptance_source',
    'polarization_density_matrix_source', 'inverse_raw_DA_same_s_source',
    'photon_phase_space_history', 'alpha_target_four_velocity_and_density',
    'daughter_phase_space_spectrum', 'D_fast_stopping_kernel',
    'deposition_thermalization_kernel', 'heat_capacity_Cv',
)


def physical_bridge_inventory(inputs: dict) -> dict:
    """Inventory only. A physical-rate engine must be authorized separately.

    For a target-rest photon density n_gamma^(alpha)(E,Omega,t) in
    m^-3 MeV^-1 sr^-1, target density n_alpha in m^-3, the formal
    per-volume rate is n_alpha*c*int(n_gamma*sigma_event dE dOmega).
    The event kernel and history are NOT evaluated here.
    """
    forbidden = {'kappa', 'R_event', 'physical_activation', 'L4', 'production'}
    if any(k in inputs for k in forbidden):
        raise ValueError('downstream may not write physical gate state')
    unknown = set(inputs).difference(REQUIRED_PHYSICAL_INPUTS)
    if unknown:
        raise ValueError('unregistered physical input key: ' + ','.join(sorted(unknown)))
    present = tuple(k for k in REQUIRED_PHYSICAL_INPUTS if inputs.get(k) is not None)
    missing = tuple(k for k in REQUIRED_PHYSICAL_INPUTS if inputs.get(k) is None)
    return {'present_fields': present, 'missing_fields': missing,
            'input_hints_not_verified': bool(present), 'kappa': None,
            'R_event': None, 'physical_activation': False, 'L4': False,
            'production': 'HOLD'}
