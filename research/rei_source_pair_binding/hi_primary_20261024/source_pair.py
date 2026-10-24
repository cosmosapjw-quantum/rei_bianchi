"""Selected elemental-HI summary adapter; static preparation, not L1 admission.

Six energy owners, prescribed snapshot, explicit no-deposition model. All saved
moments stay independent. Exact arithmetic represents supplied operands; it does
not recover upstream precision or qualify the physical source.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

Number = int | float | Fraction
MODEL = 'NO_DEPOSITION_SELECTED_MODEL'
ENERGY_OWNERS = ('gas_thermal', 'binding', 'uv_radiation',
                 'dynamic_escape_radiation', 'source_reservoir', 'primary_nonthermal')
PARTICLE_OWNERS = ('HI', 'HII', 'e_nt', 'e_th', 'absorbed_photon')
SOURCE_CARD_SHA256 = '1b4077f58752b2112ebdac1661d19c7942612adcf65fa5e98a41bb9bdb3707dd'
READ_COMMIT = 'b8882d026887f375acf90768d4e3740eb03da226'
CASES_BLOB = '61bcbc0b44206f496534da6bdffcdfe1731ad063'


class DomainError(ValueError):
    """Input is outside this fixed selected model."""


class NumericalRangeError(ArithmeticError):
    """A final float-containing result cannot be represented as finite binary64."""


def _number(value: Number, name: str, *, nonnegative: bool = False) -> Number:
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise DomainError(f'{name}: finite int, float or Fraction required')
    if isinstance(value, float) and not math.isfinite(value):
        raise DomainError(f'{name}: nonfinite input')
    if nonnegative and value < 0:
        raise DomainError(f'{name}: nonnegative input required')
    return value


def _finish(exact: Fraction, float_containing: bool) -> Number:
    if not float_containing:
        return exact
    try:
        value = float(exact)
    except OverflowError as exc:
        raise NumericalRangeError('final rate outside binary64 range') from exc
    if not math.isfinite(value):
        raise NumericalRangeError('final rate is not finite')
    return value


@dataclass(frozen=True)
class SourceCard:
    """Independent per-target saved moments and fixed source metadata."""
    A: Number
    B: Number
    P: Number
    K: Number
    chi_eV: Number
    redshift: Number
    channel: str
    photon_support_eV: tuple[Number, Number]
    frame: str
    normalization: str
    donor_energy_ledger_residual_eV_per_target_s: Number
    physical_secondary_heat_eV_per_target_s: None
    global_error_bound: None
    above_support_atomic_event_rate: None
    source_card_sha256: str
    species_semantics: str = 'elemental ground-state HI; no H1/D/T identification'
    recoil: str = 'zero approximation'

    def __post_init__(self):
        for name in ('A', 'B', 'P', 'K', 'chi_eV', 'redshift'):
            _number(getattr(self, name), name, nonnegative=True)
        _number(self.donor_energy_ledger_residual_eV_per_target_s, 'donor residual')
        if self.channel != 'HI' or self.redshift != 2.479 or self.chi_eV != 13.6:
            raise DomainError('only pinned elemental-HI z=2.479, chi=13.6 eV is supported')
        if self.photon_support_eV != (13.6, 50000):
            raise DomainError('only pinned finite photon support is supported')
        if self.frame != 'bath_frame_rest_target':
            raise DomainError('only bath-frame rest target is supported')
        if self.normalization != 'per_absorbing_target_per_proper_second':
            raise DomainError('unsupported source normalization')
        if (self.physical_secondary_heat_eV_per_target_s is not None
                or self.global_error_bound is not None
                or self.above_support_atomic_event_rate is not None):
            raise DomainError('unavailable selected-source quantities must remain None')
        if self.source_card_sha256 != SOURCE_CARD_SHA256:
            raise DomainError('source card does not have the pinned byte identity')
        if self.species_semantics != 'elemental ground-state HI; no H1/D/T identification':
            raise DomainError('isotope identification is unsupported')
        if self.recoil != 'zero approximation':
            raise DomainError('only the declared zero-recoil approximation is supported')


def load_selected_case(*, redshift: Number = 2.479, channel: str = 'HI') -> SourceCard:
    """Read the exact local saved row with ordinary json.load binary64 parsing.

    No interpolation, re-integration, isotope mapping or alternate source path.
    The original donor card, including unused diagnostic fields, is preserved.
    """
    _number(redshift, 'redshift', nonnegative=True)
    if redshift != 2.479 or channel != 'HI':
        raise DomainError('unsupported selection; only elemental HI at z=2.479 is bound')
    path = Path(__file__).resolve().with_name('source_card.json')
    if hashlib.sha256(path.read_bytes()).hexdigest() != SOURCE_CARD_SHA256:
        raise DomainError('saved source card byte identity mismatch')
    with path.open(encoding='utf-8') as handle:
        row = json.load(handle)
    try:
        result = row['result']
        return SourceCard(
            A=result['number_per_target_s'], B=result['binding_eV_per_target_s'],
            P=result['absorbed_photon_eV_per_target_s'], K=result['kinetic_eV_per_target_s'],
            chi_eV=row['threshold_eV'], redshift=row['redshift'], channel=row['channel'],
            photon_support_eV=tuple(row['photon_support_eV']),
            frame=result['frame'], normalization=result['normalization'],
            donor_energy_ledger_residual_eV_per_target_s=result['energy_ledger_residual_eV_per_target_s'],
            physical_secondary_heat_eV_per_target_s=result['secondary_heat_eV_per_target_s'],
            global_error_bound=result['global_error_bound'],
            above_support_atomic_event_rate=row['radiation_above_atomic_domain']['atomic_event_rate'],
            source_card_sha256=SOURCE_CARD_SHA256)
    except (KeyError, TypeError) as exc:
        raise DomainError('required selected source fields are missing or malformed') from exc


@dataclass(frozen=True)
class RepresentedResiduals:
    """Exact represented-input diagnostics, distinct from donor floating residual."""
    r_B: Fraction
    r_E: Fraction
    gross_B: Fraction
    gross_E: Fraction


def represented_residuals(card: SourceCard) -> RepresentedResiduals:
    a, b, p, k, chi = map(Fraction, (card.A, card.B, card.P, card.K, card.chi_eV))
    chi_a = chi * a
    return RepresentedResiduals(r_B=b-chi_a, r_E=b+k-p,
                                gross_B=abs(b)+abs(chi_a), gross_E=abs(b)+abs(k)+abs(p))


@dataclass(frozen=True)
class PairRates:
    energy_rates: tuple[Number, ...]
    particle_rates: tuple[Number, ...]
    multiplier_exact: Fraction
    expected_energy_sum_exact: Fraction
    residuals: RepresentedResiduals
    model: str = MODEL
    closure: str = 'declared isotropic scalar closure; not measured angular data'
    isotropic_flux0: tuple[int, int, int] = (0, 0, 0)
    isotropic_stf0: tuple[tuple[int, int, int], ...] = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
    physical_secondary_heat_eV_per_target_s: None = None

    @property
    def e_all_rate(self) -> Number:
        """One electron count: e_nt + e_th, not a third independent pool."""
        return self.particle_rates[2] + self.particle_rates[3]


def _rates(card: SourceCard, multiplier: Fraction, normalization_has_float: bool) -> PairRates:
    def scaled(coefficient: Number) -> Number:
        return _finish(multiplier * Fraction(coefficient),
                       normalization_has_float or isinstance(coefficient, float))
    reaction = scaled(card.A)
    energy = (0, scaled(card.B), scaled(-card.P), 0, 0, scaled(card.K))
    particles = (-reaction, reaction, reaction, 0, -reaction)
    residuals = represented_residuals(card)
    return PairRates(energy_rates=energy, particle_rates=particles,
                     multiplier_exact=multiplier,
                     expected_energy_sum_exact=multiplier * residuals.r_E,
                     residuals=residuals)


def source_per_href(card: SourceCard, x_hi: Number, amplitude: Number = 1) -> PairRates:
    """Proper-time rates per fixed Href; x_hi and amplitude applied once.

    Adopted physical source amplitude is 1. Other values describe linear
    normalization sensitivity and do not establish a new source calibration.
    """
    _number(x_hi, 'x_hi', nonnegative=True)
    _number(amplitude, 'amplitude', nonnegative=True)
    multiplier = Fraction(x_hi) * Fraction(amplitude)
    return _rates(card, multiplier, any(isinstance(v, float) for v in (x_hi, amplitude)))


def source_jvp_fixed_moments(card: SourceCard, x_hi: Number, dx_hi: Number,
                             amplitude: Number = 1, d_amplitude: Number = 0) -> PairRates:
    """Full fixed-moment JVP: dm=a*dX+X*da, without rounding dm first.

    Tangents may be signed finite; no z/chi/support/angular derivatives exist.
    A tangent at a physical boundary must be interpreted within that domain.
    """
    _number(x_hi, 'x_hi', nonnegative=True)
    _number(amplitude, 'amplitude', nonnegative=True)
    _number(dx_hi, 'dx_hi')
    _number(d_amplitude, 'd_amplitude')
    multiplier = Fraction(amplitude) * Fraction(dx_hi) + Fraction(x_hi) * Fraction(d_amplitude)
    operands = (x_hi, dx_hi, amplitude, d_amplitude)
    return _rates(card, multiplier, any(isinstance(v, float) for v in operands))
