"""Single-owner energy accounting for AXBI primary absorption and F05 He II Lyα.

All counts belong to the same source site and proper-time interval. A count rate
may be supplied in place of a count when *all* inputs share that normalization.
The returned energies then have the corresponding rate normalization.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from typing import Sequence

EV_ERG = 1.602176634e-12
LINE_EV = 40.813320
BINDING_EV = {'HI': 13.598434599702, 'HeI': 24.587389011, 'HeII': 54.41776}
# Verner fit thresholds in the native AXBI absorber are distinct from binding energies.
FIT_THRESHOLD_EV = {'HI': 13.60, 'HeI': 24.59, 'HeII': 54.42}
F05_SOURCE = 'F05_V2_HEII_LYA_LOCAL_OTS'
AXBI_SOURCE = 'PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1'


@dataclass(frozen=True)
class EnergyLedger:
    source: str
    incoming_photons: float
    absorbed_hi: float
    absorbed_hei: float
    absorbed_heii: float
    escaped_photons: float
    incoming_energy_erg: float
    binding_erg: float
    heat_erg: float
    escaped_erg: float
    already_in_native_rhs: bool = True


def _nonnegative(value: float, name: str) -> float:
    if isinstance(value, bool) or not isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return float(value)


def _fraction(value: float, lower: float, name: str) -> float:
    value = _nonnegative(value, name)
    if not lower <= value <= 1:
        raise ValueError(f'{name} outside [{lower}, 1]')
    return value


def _energy(photons: float, ev: float) -> float:
    value = photons * (ev * EV_ERG)
    if not isfinite(value):
        raise OverflowError('Photon energy exceeds binary64 range in erg')
    return value


def f05_local_lya_ledger(cascade_events: float, two_photon_fraction: float,
                         absorbed_fraction: float, hydrogen_recipient_fraction: float) -> EnergyLedger:
    """Local OTS diagnostic at one realization of the PR155 source parameters.

    The source already includes these absorption events in A_H/A_HeI and heat in
    EventBox.resolved_heat. The result classifies that existing RHS contribution.
    """
    cascade = _nonnegative(cascade_events, 'cascade_events')
    v = _fraction(two_photon_fraction, 0., 'two_photon_fraction')
    f = _fraction(absorbed_fraction, .1, 'F05 absorbed_fraction')
    z = _fraction(hydrogen_recipient_fraction, 0., 'hydrogen_recipient_fraction')
    emitted = cascade * (1 - v)
    h, he, escaped = emitted * f * z, emitted * f * (1 - z), emitted * (1 - f)
    binding = _energy(h, BINDING_EV['HI']) + _energy(he, BINDING_EV['HeI'])
    heat = _energy(h, LINE_EV - BINDING_EV['HI']) + _energy(he, LINE_EV - BINDING_EV['HeI'])
    return EnergyLedger(F05_SOURCE, emitted, h, he, 0., escaped, _energy(emitted, LINE_EV),
                        binding, heat, _energy(escaped, LINE_EV))


def primary_case_a_ledger(species: str, photon_energy_ev: float, absorbed_photons: float) -> EnergyLedger:
    """Classify an existing native AXBI primary photoionization count.

    The donor sees the native absorbed event after opacity/transport and supplies
    its energetic decomposition. Recombination-line emission is a different source.
    """
    if species not in BINDING_EV:
        raise ValueError('species must be HI, HeI or HeII')
    energy = _nonnegative(photon_energy_ev, 'photon_energy_ev')
    photons = _nonnegative(absorbed_photons, 'absorbed_photons')
    if photons > 0 and energy < FIT_THRESHOLD_EV[species]:
        raise ValueError('Positive primary event below native Verner fit threshold')
    bound = BINDING_EV[species]
    return EnergyLedger(AXBI_SOURCE, photons, photons if species == 'HI' else 0.,
                        photons if species == 'HeI' else 0., photons if species == 'HeII' else 0.,
                        0., _energy(photons, energy), _energy(photons, bound),
                        _energy(photons, energy - bound) if photons else 0., 0.)


RInterval = tuple[Fraction, Fraction]
Scalar = str | float | int | Fraction
_EV = Fraction('1.602176634e-12')
_E = Fraction('40.813320')
_H = Fraction('13.598434599702')
_HE = Fraction('24.587389011')
_ZERO = Fraction(0)


def _endpoints(pair: Sequence[Scalar]) -> RInterval:
    if len(pair) != 2 or any(isinstance(v, bool) for v in pair):
        raise ValueError('Each channel requires two nonnegative ordered endpoints')
    # Passing CSV tokens preserves the decimal source representation exactly.
    lo, hi = (v if isinstance(v, Fraction) else Fraction(str(v)) for v in pair)
    if not 0 <= lo <= hi:
        raise ValueError('Invalid photon count interval')
    return lo, hi


def correlated_partition_bounds(emitted: Sequence[Scalar], h_i: Sequence[Scalar],
                                he_i: Sequence[Scalar], escaped: Sequence[Scalar]) -> dict[str, RInterval]:
    """Exact rational linear envelopes on the box intersected with photon conservation.

    Return energies in erg and photon counts. Each returned marginal has its own
    attaining feasible allocation. The real source may satisfy tighter common
    v/f/z constraints than this photon-conserving polytope.
    """
    emitted_lo, emitted_hi = _endpoints(emitted)
    boxes = tuple(map(_endpoints, (h_i, he_i, escaped)))
    lower, upper = zip(*boxes)
    sum_lower = sum(lower)
    min_total = max(emitted_lo, sum_lower)
    max_total = min(emitted_hi, sum(upper))
    if min_total > max_total:
        raise ValueError('Photon interval box has empty intersection with conservation')
    room = tuple(hi - lo for lo, hi in boxes)

    def evaluate(weights: tuple[Fraction, Fraction, Fraction]) -> RInterval:
        base = sum(w * n for w, n in zip(weights, lower))
        order = sorted(range(3), key=weights.__getitem__)
        def fill(total: Fraction, indices) -> Fraction:
            amount = total - sum_lower
            result = base
            for i in indices:
                difference = min(amount, room[i])
                result += weights[i] * difference
                amount -= difference
                if amount == 0:
                    break
            return result
        return fill(min_total, order), fill(max_total, reversed(order))

    local_lo = max(lower[0] + lower[1], emitted_lo - upper[2])
    local_hi = min(upper[0] + upper[1], emitted_hi - lower[2])
    return {'hydrogen_absorptions': (max(lower[0], local_lo - upper[1]), min(upper[0], local_hi - lower[1])),
            'helium_absorptions': (max(lower[1], local_lo - upper[0]), min(upper[1], local_hi - lower[0])),
            'emitted_photons': (min_total, max_total),
            'emitted_energy_erg': (min_total * (_E * _EV), max_total * (_E * _EV)),
            'local_absorptions': evaluate((Fraction(1), Fraction(1), _ZERO)),
            'binding_erg': evaluate((_H * _EV, _HE * _EV, _ZERO)),
            'heat_erg': evaluate(((_E - _H) * _EV, (_E - _HE) * _EV, _ZERO)),
            'escaped_erg': evaluate((_ZERO, _ZERO, _E * _EV))}
