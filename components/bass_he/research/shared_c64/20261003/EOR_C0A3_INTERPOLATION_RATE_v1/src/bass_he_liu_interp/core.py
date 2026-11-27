"""Opt-in interpolation and finite-support Maxwell functionals, not source admission.

The immutable C0A2 loader owns native tokens/units. This layer never changes it.
All interpolated and integrated arithmetic is binary64; Decimal is used only
for exact energy identity and to form stable normalized interval coordinates.
"""
from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
import math
import sys
from typing import Any, Sequence

from bass_he_liu import Dataset, ContractError, SourceUnavailable, DomainError
from bass_he_liu.native import ENERGY_AXIS, _energy


def numerical_range(value: float, *, positive: bool = False) -> float:
    """Reject nonfinite and subnormal outputs instead of reporting false zero tails."""
    if not math.isfinite(value) or (positive and value <= 0):
        raise ContractError('NUMERICAL_RANGE_ERROR')
    if value != 0 and abs(value) < sys.float_info.min:
        raise ContractError('NUMERICAL_RANGE_ERROR: subnormal output')
    return value


def _finite(value: Any, *, positive: bool = True) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ContractError('FINITE_NUMERIC_INPUT_REQUIRED')
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ContractError('NUMERICAL_RANGE_ERROR') from exc
    if not math.isfinite(result) or result < 0 or (positive and result == 0):
        raise ContractError('POSITIVE_FINITE_INPUT_REQUIRED')
    return result


def maxwell_weights(a: float, b: float) -> tuple[float, float]:
    """Integrate the two linear endpoint hats against x exp(-x) on [a,b].

    Inputs are dimensionless. Both output weights are positive for b>a>=0.
    This computes an analytic real-arithmetic formula in binary64, not a
    certified outward-rounded interval and not an interpolation error bound.
    """
    a = _finite(a, positive=False)
    b = _finite(b)
    d = b - a
    if not d > 0:
        raise ContractError('NONEMPTY_ORDERED_INTERVAL_REQUIRED')
    if d <= 1:
        # Integrals of u^n exp(-d*u), 0<=u<=1. Differences are expanded
        # directly, rather than formed by cancellation of two moments.
        terms = [1.0]
        for k in range(1, 33):
            terms.append(terms[-1] * (-d / k))
        i1 = math.fsum(t / (k + 2) for k, t in enumerate(terms))
        i2 = math.fsum(t / (k + 3) for k, t in enumerate(terms))
        left0 = math.fsum(t / ((k + 1) * (k + 2)) for k, t in enumerate(terms))
        left1 = math.fsum(t / ((k + 2) * (k + 3)) for k, t in enumerate(terms))
        w0 = d * math.exp(-a) * math.fsum((a * left0, d * left1))
        w1 = d * math.exp(-a) * math.fsum((a * i1, d * i2))
    else:
        ed = math.exp(-d)
        j0 = -math.expm1(-d)
        # d*exp(-d) tends to zero; prevent inf*0 in unrepresentable d^2.
        dj = d * ed
        j1 = j0 - dj
        j2 = 2 * j1 - d * dj
        w0 = math.exp(-a) * math.fsum((a * (j0 - j1 / d), j1 - j2 / d))
        w1 = math.exp(-a) * (a * j1 + j2) / d
    return numerical_range(w0, positive=True), numerical_range(w1, positive=True)


@dataclass(frozen=True)
class KinematicBinding:
    """Explicit E_cm = scale * native_axis mapping; never auto-certified."""
    energy_scale_J_per_native: float
    reduced_mass_kg: float
    authority: str

    def __post_init__(self) -> None:
        _finite(self.energy_scale_J_per_native)
        _finite(self.reduced_mass_kg)
        if not isinstance(self.authority, str) or not self.authority.strip() or len(self.authority) > 4096:
            raise ContractError('EXPLICIT_KINEMATIC_AUTHORITY_REQUIRED')


class Interpolator:
    """Piecewise source interpolation with exact membership and gap semantics."""
    def __init__(self, dataset: Dataset, *, method: str | None = None,
                 scope: str = 'paper_domain'):
        if not isinstance(dataset, Dataset):
            raise ContractError('SOURCE_DATASET_REQUIRED')
        if method not in ('linear_E', 'loglog'):
            raise ContractError('EXPLICIT_INTERPOLATION_METHOD_REQUIRED')
        if scope not in ('paper_domain', 'payload_domain'):
            raise ContractError('UNKNOWN_SCOPE')
        self.dataset = dataset
        self.method = method
        self.scope = scope
        self._samples = {
            cid: tuple(s for s in c.samples if scope == 'payload_domain' or Decimal(1) <= s.energy <= Decimal(200))
            for cid, c in dataset.channels.items()
        }
        self._energies = {cid: tuple(s.energy for s in v) for cid, v in self._samples.items()}
        self._hashes = {t.name: t.sha256 for t in dataset.tables}

    def _atom(self, cid: str, e: Decimal, unit: str, accept: bool) -> dict[str, Any]:
        factor = self.dataset._query_contract(e, unit, accept, self.scope, ENERGY_AXIS)
        channel = self.dataset.channels[cid]
        missing = tuple(Decimal(m.energy_token) for m in channel.missing)
        if e in missing:
            raise SourceUnavailable('MISSING_VALUE: ' + cid)
        es = self._energies[cid]
        pos = bisect_left(es, e)
        if pos < len(es) and es[pos] == e:
            out = self.dataset.sample(cid, e, unit=unit, accept_contextual_unit=accept, scope=self.scope)
            return {**out, 'requested_interpolation_method': self.method, 'source_uncertainty': None}
        if pos == 0 or pos == len(es):
            raise DomainError('OUTSIDE_INTERPOLABLE_SUPPORT: both anchors must belong to scope')
        left, right = self._samples[cid][pos - 1:pos + 1]
        if any(left.energy < m < right.energy for m in missing):
            raise SourceUnavailable('MISSING_CELL_BLOCKS_INTERPOLATION')
        with localcontext() as ctx:
            ctx.prec = 80
            t = float((e - left.energy) / (right.energy - left.energy))
            y0 = float(Decimal(left.value_token) * factor)
            y1 = float(Decimal(right.value_token) * factor)
            relative_q = float((e - left.energy) / left.energy)
            relative_r = float((right.energy - left.energy) / left.energy)
        for y, s in ((y0, left), (y1, right)):
            numerical_range(y, positive=Decimal(s.value_token) > 0)
        if not 0 < t < 1:
            raise ContractError('NUMERICAL_RANGE_ERROR: unresolved interval coordinate')
        if self.method == 'linear_E':
            value = math.fsum(((1 - t) * y0, t * y1))
        else:
            if y0 <= 0 or y1 <= 0:
                raise ContractError('LOGLOG_REQUIRES_POSITIVE_ANCHORS')
            den = math.log1p(relative_r)
            if not den > 0:
                raise ContractError('NUMERICAL_RANGE_ERROR: log energy interval')
            t = math.log1p(relative_q) / den
            value = math.exp(math.fsum(((1 - t) * math.log(y0), t * math.log(y1))))
        numerical_range(value, positive=y0 > 0 or y1 > 0)
        return {'channel_id': cid, 'energy_token': str(e), 'value': repr(value), 'unit': unit,
                'energy_axis': ENERGY_AXIS, 'data_kind': 'INTERPOLATED_VALUE', 'interpolated': True,
                'method': self.method, 'scope': self.scope, 'bracket_energies': [left.energy_token, right.energy_token],
                'source_parts': [left.as_dict(), right.as_dict()], 'source_name': channel.source_name,
                'source_sha256': self._hashes[channel.source_name],
                'uses_outside_paper_anchor': not (Decimal(1) <= left.energy <= right.energy <= Decimal(200)),
                'unit_binding': 'CSV_ORDINATE_UNIT_UNDECLARED' if unit == 'source_native' else 'PDF_CONTEXTUAL_CM2_NOT_CSV_HEADER',
                'arithmetic': 'binary64', 'source_uncertainty': None, 'interpolation_error_bound': None,
                'physical_certificate': False, 'inclusive_all_bound': False}

    def evaluate(self, channel_id: str, energy: str | int | Decimal, *, unit: str = 'source_native',
                 accept_contextual_unit: bool = False) -> dict[str, Any]:
        e = _energy(energy)
        members = self.dataset.members(channel_id)
        if len(members) > 1:
            out = self.aggregate(members, e, unit=unit, accept_contextual_unit=accept_contextual_unit)
            return {**out, 'channel_id': channel_id}
        return {**self._atom(members[0], e, unit, accept_contextual_unit), 'requested_channel_id': channel_id}

    def aggregate(self, channel_ids: Sequence[str], energy: str | int | Decimal, *,
                  unit: str = 'source_native', accept_contextual_unit: bool = False) -> dict[str, Any]:
        if isinstance(channel_ids, str) or not channel_ids:
            raise ContractError('NONEMPTY_CHANNEL_LIST_REQUIRED')
        flat = [c for cid in channel_ids for c in self.dataset.members(cid)]
        if len({tuple(c.split(':')[:2]) for c in flat}) != 1:
            raise ContractError('INCOMPATIBLE_INITIAL_STATE_OR_PROCESS')
        if len(flat) != len(set(flat)) or (len(flat) > 1 and any(c.endswith(':total') for c in flat)):
            raise ContractError('OVERLAPPING_CHANNEL_SELECTION')
        e = _energy(energy)
        parts = [self._atom(c, e, unit, accept_contextual_unit) for c in flat]
        if not any(p['interpolated'] for p in parts):
            return self.dataset.aggregate(flat, e, unit=unit, accept_contextual_unit=accept_contextual_unit, scope=self.scope)
        value = math.fsum(float(p['value']) for p in parts)
        numerical_range(value, positive=any(Decimal(p['value']) > 0 for p in parts))
        return {'requested_channels': list(channel_ids), 'atomic_members': flat, 'energy_token': str(e),
                'value': repr(value), 'unit': unit, 'data_kind': 'DERIVED_SUM_OF_COMPONENT_INTERPOLANTS',
                'source_parts': parts, 'method': self.method, 'scope': self.scope,
                'interpolated': True, 'physical_certificate': False, 'inclusive_all_bound': False,
                'source_uncertainty': None, 'interpolation_error_bound': None}

    def _panels(self, cid: str, lo: Decimal, hi: Decimal) -> tuple[Decimal, ...]:
        if not lo < hi:
            raise ContractError('NONEMPTY_ORDERED_INTERVAL_REQUIRED')
        self.evaluate(cid, lo)
        self.evaluate(cid, hi)
        knots = {lo, hi}
        for c in self.dataset.members(cid):
            knots.update(e for e in self._energies[c] if lo < e < hi)
            if any(lo <= Decimal(m.energy_token) <= hi for m in self.dataset.channels[c].missing):
                raise SourceUnavailable('MISSING_CELL_BLOCKS_INTEGRATION')
        nodes = tuple(sorted(knots))
        for l, r in zip(nodes, nodes[1:]):
            self.evaluate(cid, (l + r) / 2)
        return nodes

    def maxwell_functional(self, channel_id: str, lo: str | int | Decimal, hi: str | int | Decimal,
                           *, theta_native: float, unit: str = 'source_native',
                           accept_contextual_unit: bool = False) -> dict[str, Any]:
        """Integral sigma(theta*x) x exp(-x) dx over explicit finite native support.

        theta_native is a SCALE ON THE SOURCE AXIS, not a gas temperature.
        No relative-speed prefactor is applied here. Zero/unknown tails remain
        distinct. This bounded implementation analytically integrates linear_E.
        """
        if self.method != 'linear_E':
            raise ContractError('ANALYTIC_RATE_REQUIRES_LINEAR_E')
        theta = _finite(theta_native)
        l, h = _energy(lo), _energy(hi)
        nodes = self._panels(channel_id, l, h)
        panels = []
        for left, right in zip(nodes, nodes[1:]):
            y0 = float(self.evaluate(channel_id, left, unit=unit, accept_contextual_unit=accept_contextual_unit)['value'])
            y1 = float(self.evaluate(channel_id, right, unit=unit, accept_contextual_unit=accept_contextual_unit)['value'])
            a, b = float(left) / theta, float(right) / theta
            w0, w1 = maxwell_weights(a, b)
            terms = (w0 * y0, w1 * y1)
            for term, y in zip(terms, (y0, y1)):
                numerical_range(term, positive=y > 0)
            contribution = math.fsum(terms)
            numerical_range(contribution, positive=y0 > 0 or y1 > 0)
            panels.append({'native_interval': [str(left), str(right)], 'weight_left': w0,
                           'weight_right': w1, 'endpoint_values': [y0, y1], 'contribution': contribution})
        value = math.fsum(p['contribution'] for p in panels)
        numerical_range(value, positive=any(p['contribution'] > 0 for p in panels))
        return {'schema': 'bass-he.c0a3.partial-maxwell-functional.v1', 'channel_id': channel_id,
                'data_kind': 'FINITE_SUPPORT_INTERPOLANT_FUNCTIONAL', 'value': value, 'unit': unit,
                'native_interval': [str(l), str(h)], 'theta_native': theta, 'method': self.method,
                'scope': self.scope, 'panels': panels, 'arithmetic': 'binary64_analytic_endpoint_weights',
                'full_functional': None, 'tail_bound': None, 'renormalized_to_support': False,
                'weight_mass_not_rate_fraction': math.fsum(p['weight_left'] + p['weight_right'] for p in panels),
                'source_uncertainty': None, 'interpolation_error_bound': None,
                'physical_certificate': False, 'source_hashes': self._hashes.copy()}

    def maxwell_partial_rate(self, channel_id: str, lo: str | int | Decimal, hi: str | int | Decimal,
                             *, theta_J: float, binding: KinematicBinding | None,
                             accept_contextual_unit: bool = False, require_full: bool = False) -> dict[str, Any]:
        """Conditional no-drift Maxwell rate on [lo,hi]; never infer missing tails."""
        if not isinstance(require_full, bool):
            raise ContractError('FULL_RATE_FLAG_MUST_BE_BOOLEAN')
        if require_full:
            raise SourceUnavailable('FULL_RATE_REQUIRES_UNSUPPLIED_LOW_HIGH_ENERGY_DATA')
        if not isinstance(binding, KinematicBinding):
            raise ContractError('KINEMATIC_BINDING_REQUIRED')
        theta = _finite(theta_J)
        scale = _finite(binding.energy_scale_J_per_native)
        mu = _finite(binding.reduced_mass_kg)
        theta_native = numerical_range(theta / scale, positive=True)
        result = self.maxwell_functional(channel_id, lo, hi, theta_native=theta_native,
                                        unit='m2', accept_contextual_unit=accept_contextual_unit)
        prefactor = numerical_range(math.exp(.5 * (math.log(8 / math.pi) + math.log(theta) - math.log(mu))), positive=True)
        rate = numerical_range(prefactor * result['value'], positive=result['value'] > 0)
        return {'schema': 'bass-he.c0a3.conditional-partial-rate.v1',
                'partial_rate_m3_s': rate, 'full_rate_m3_s': None, 'tail_bound_m3_s': None,
                'energy_scale_J_per_native': scale, 'reduced_mass_kg': mu, 'theta_J': theta,
                'binding_authority': binding.authority, 'binding_status': 'CONDITIONAL_USER_MAPPING',
                'source_energy_convention_verified': False, 'distribution': 'zero_relative_drift_Maxwell',
                'physical_certificate': False, 'renormalized_to_support': False, 'functional': result}

    def capture_consistency(self, initial: str) -> dict[str, Any]:
        """Exact rational order check of this PWL model on the common support.

        The difference is affine between UNION knots, not merely common knots.
        Its minimum is at a union knot. This proves an interpolant property;
        it does not bound the true cross section or its source uncertainty.
        """
        if self.method != 'linear_E':
            raise ContractError('ORDER_PROOF_REQUIRES_LINEAR_E')
        if initial not in ('1s', '2s'):
            raise ContractError('INVALID_INITIAL_STATE')
        total = f'NR_CX:{initial}:total'
        self.dataset.members(total)
        members = sorted(c for c in self.dataset.channels if c.startswith(f'NR_CX:{initial}:') and c != total)
        if not members:
            raise SourceUnavailable('NO_PARTIAL_CHANNELS')
        all_ids = [total] + members
        if any(not self._energies[c] for c in all_ids):
            raise SourceUnavailable('EMPTY_SCOPE')
        lo = max(self._energies[c][0] for c in all_ids)
        hi = min(self._energies[c][-1] for c in all_ids)
        if not lo < hi:
            raise DomainError('EMPTY_COMMON_SUPPORT')
        knots = {lo, hi}
        for c in all_ids:
            knots.update(self._panels(c, lo, hi))
        def exact(c: str, x: Decimal) -> Fraction:
            es = self._energies[c]
            j = bisect_left(es, x)
            sample = self._samples[c]
            if j < len(es) and es[j] == x:
                return Fraction(Decimal(sample[j].value_token))
            l, r = sample[j-1:j+1]
            t = (Fraction(x) - Fraction(l.energy)) / (Fraction(r.energy) - Fraction(l.energy))
            return (1-t)*Fraction(Decimal(l.value_token)) + t*Fraction(Decimal(r.value_token))
        margins = [(x, exact(total, x) - sum((exact(c, x) for c in members), Fraction(0))) for x in sorted(knots)]
        worst_x, worst = min(margins, key=lambda p: p[1])
        return {'arithmetic': 'exact_rational_decimal_inputs', 'method': 'linear_E', 'scope': self.scope,
                'initial': initial, 'proof_domain': [str(lo), str(hi)], 'union_knots': len(knots),
                'worst_energy': str(worst_x),
                'minimum_margin_fraction': {'numerator': worst.numerator, 'denominator': worst.denominator},
                'order_holds_for_declared_interpolant': worst >= 0,
                'partial_members': members, 'physical_certificate': False,
                'residual_meaning': 'UNASSIGNED_DIFFERENCE_NOT_IONIZATION_OR_HIGH_N_CERTIFICATE'}
