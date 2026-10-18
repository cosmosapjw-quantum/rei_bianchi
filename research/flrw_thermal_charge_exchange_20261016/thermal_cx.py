#!/usr/bin/env python3
"""Isolated fixed-volume H/D thermal CX. Units: cm^-3, eV cm^-3, K, s.

One extent owns every density and energy change. The adaptive local estimator
is heuristic. Savin fits are literature rates, not cosmological histories.
"""
from dataclasses import dataclass
import argparse
import json
import math
from typing import Callable

KB_EV_K = 1.380649e-23 / 1.602176634e-19

@dataclass(frozen=True)
class State:
    h0: float
    hp: float
    d0: float
    dp: float
    thermal_eV_cm3: float

@dataclass(frozen=True)
class Defect:
    delta_chi_eV: float
    source: str

@dataclass(frozen=True)
class RateProvider:
    source: str
    minimum_K: float
    maximum_K: float
    rates: Callable[[float], tuple[float, float]]

@dataclass(frozen=True)
class Controls:
    rtol: float = 1e-7
    atol_normalized: float = 1e-11
    event_atol_normalized: float = 1e-12
    max_attempts: int = 20000
    max_rhs_calls: int = 200000
    max_consecutive_rejections: int = 80
    trace_rows_max: int = 512


def _savin_rates(t):
    return (2.00e-10*t**0.402*math.exp(-37.1/t)-3.31e-17*t**1.48,
            2.06e-10*t**0.396*math.exp(-33.0/t)+2.03e-9*t**(-0.332))

SAVIN2002 = RateProvider(
    'Savin (2002), ApJ 566 599-603, DOI 10.1086/324218, Eq. (6), Table 2',
    2.7, 200000.0, _savin_rates)

class StageOutside(ValueError):
    pass

class WorkLimit(RuntimeError):
    pass

class FieldFailure(ArithmeticError):
    pass


def _finite(*values):
    return all(isinstance(x, (int, float)) and math.isfinite(x) for x in values)


class ReducedSystem:
    """Validated algebraic reduction. No state increments and no clipping."""
    def __init__(self, state, defect, provider):
        self.state, self.defect, self.provider = state, defect, provider
        a, b, c, d, u = (state.h0, state.hp, state.d0, state.dp, state.thermal_eV_cm3)
        if not _finite(a, b, c, d, u) or min(a, b, c, d, u) < 0:
            raise ValueError('Densities and thermal inventory must be finite nonnegative')
        if not _finite(defect.delta_chi_eV) or not isinstance(defect.source, str) or not defect.source:
            raise ValueError('Defect must be finite signed with source')
        if (not isinstance(provider.source, str) or not provider.source or
            not callable(provider.rates) or not _finite(provider.minimum_K, provider.maximum_K) or
            not 0 < provider.minimum_K <= provider.maximum_K):
            raise ValueError('Provider requires named finite ordered positive domain')
        self.scale = max(a, b, c, d)
        self.nth = a+b+c+d+b+d
        if not _finite(self.nth):
            raise ValueError('Nonfinite particle inventory')
        self.capacity = 1.5*KB_EV_K*self.nth
        self.physical = (-min(a, d), min(b, c))
        self.admissible = self.physical
        self.provider_bounds = {}
        if self.scale == 0:
            if u != 0:
                raise ValueError('Empty density state cannot carry nonzero thermal inventory')
            self.t0 = None
            self.ceiling = None
            self.interval = (0.0, 0.0)
            return
        self.t0 = u/self.capacity
        if not _finite(self.t0) or not provider.minimum_K <= self.t0 <= provider.maximum_K:
            raise ValueError('Initial temperature outside provider domain')
        delta = defect.delta_chi_eV
        self.ceiling = abs(delta)*(c+d)/self.capacity
        if not _finite(self.ceiling):
            raise ValueError('Nonfinite thermal amplitude ceiling')
        if delta != 0:
            ends = [(u-self.capacity*provider.minimum_K)/delta,
                    (u-self.capacity*provider.maximum_K)/delta]
            if not _finite(*ends):
                raise ValueError('Nonfinite thermal interval')
            thermal_lo, thermal_hi = sorted(ends)
            lo, hi = max(self.physical[0], thermal_lo), min(self.physical[1], thermal_hi)
            self.admissible = (lo, hi)
            for side, x, domain_x in [('lower', lo, thermal_lo), ('upper', hi, thermal_hi)]:
                if x == domain_x:
                    self.provider_bounds[side] = {'extent_cm3': x,
                        'temperature_K': provider.minimum_K if delta*x == delta*ends[0] else provider.maximum_K}
        if not self.admissible[0] <= 0 <= self.admissible[1]:
            raise ValueError('Initial extent outside admissible interval')
        self.interval = tuple(x/self.scale for x in self.admissible)

    def reconstruct(self, z):
        s = self.state
        xi = self.scale*z
        chemical = self.defect.delta_chi_eV*xi
        u = s.thermal_eV_cm3-chemical
        density = (s.h0+xi, s.hp-xi, s.d0-xi, s.dp+xi)
        t = u/self.capacity if self.scale else None
        return xi, density, u, t, chemical

    def check_stage(self, z):
        if not _finite(z):
            raise FieldFailure('Nonfinite stage extent')
        if not self.interval[0] <= z <= self.interval[1]:
            raise StageOutside('Euler stage outside admissible interval')
        xi, density, u, t, chemical = self.reconstruct(z)
        if not _finite(xi, *density, u, t, chemical):
            raise FieldFailure('Nonfinite valid-domain reconstruction')
        if min(density) < 0 or u < 0 or not self.provider.minimum_K <= t <= self.provider.maximum_K:
            raise StageOutside('Reconstructed state outside density/temperature domain')
        return density, t

    def field(self, z):
        density, t = self.check_stage(z)
        try:
            kf, kr = self.provider.rates(t)
            if not _finite(kf, kr) or min(kf, kr) < 0:
                raise FieldFailure('Provider returned nonfinite or negative rate')
            a, b, c, d = density
            g = (kf*c*b-kr*d*a)/self.scale
            if not _finite(g):
                raise FieldFailure('Nonfinite valid-domain field')
            return g
        except FieldFailure:
            raise
        except Exception as exc:
            raise FieldFailure('Provider evaluation failed: '+str(exc)) from exc


def heun_step(system, z, h, rhs):
    """Frozen SSP form; both Euler states checked before convex endpoint."""
    e = z+h*rhs(z)
    system.check_stage(e)
    v = e+h*rhs(e)
    system.check_stage(v)
    endpoint = (z+v)/2
    system.check_stage(endpoint)
    return endpoint


def integrate(state, defect, provider, t_requested_s, controls=Controls()):
    """Return typed complete/partial result; supplied state is never mutated."""
    counts = dict(accepted_steps=0, rejected_steps=0, attempts=0, rhs_calls=0)
    t, z, maximum_ratio, trace, boundary, reason = 0.0, 0.0, 0.0, [], None, None
    try:
        if not _finite(t_requested_s) or t_requested_s < 0:
            raise ValueError('Requested time must be finite nonnegative')
        if (not _finite(controls.rtol, controls.atol_normalized, controls.event_atol_normalized) or
            controls.rtol < 0 or controls.atol_normalized <= 0 or controls.event_atol_normalized <= 0):
            raise ValueError('Invalid tolerances')
        for name in ('max_attempts', 'max_rhs_calls', 'max_consecutive_rejections', 'trace_rows_max'):
            value = getattr(controls, name)
            if type(value) is not int or value < (0 if name == 'trace_rows_max' else 1):
                raise ValueError('Invalid finite integer control: '+name)
        system = ReducedSystem(state, defect, provider)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError, AttributeError) as exc:
        return dict(status='INVALID_INPUT', full_interval_complete=False, t_reached_s=0.0,
                    t_requested_s=t_requested_s if _finite(t_requested_s) else None,
                    reason=str(exc), **counts)

    def result(status, message=None):
        xi, density, u, temp, chemical = system.reconstruct(z)
        return dict(status=status, full_interval_complete=status.startswith('COMPLETE'),
            t_reached_s=t, t_requested_s=t_requested_s, extent_cm3=xi, normalized_extent=z,
            four_densities=dict(zip(('h0','hp','d0','dp'), density)), thermal_eV_cm3=u,
            temperature_K=temp, chemical_delta_eV_cm3=chemical, thermal_delta_eV_cm3=-chemical,
            electron_delta_cm3=0.0, temperature_amplitude_ceiling_K=system.ceiling,
            physical_interval=list(system.physical), admissible_interval=list(system.admissible),
            provider_boundary_if_approached=boundary,
            distance_to_boundary_cm3=abs(boundary['extent_cm3']-xi) if boundary else None,
            event_atol_normalized=controls.event_atol_normalized,
            maximum_accepted_local_error_ratio=maximum_ratio,
            degenerate_temperature_null_reason='Empty pure H/D inventory; EOS undefined' if system.scale == 0 else None,
            reason=message, rate_source=provider.source, defect_source=defect.source,
            trace=trace, trace_rows_max=controls.trace_rows_max, **counts)

    if system.scale == 0:
        t = t_requested_s
        return result('COMPLETE_EMPTY')
    if t_requested_s == 0:
        return result('COMPLETE')

    def rhs(value):
        if counts['rhs_calls'] >= controls.max_rhs_calls:
            raise WorkLimit('RHS call cap')
        counts['rhs_calls'] += 1
        return system.field(value)

    def trace_row():
        if len(trace) < controls.trace_rows_max:
            xi, _, u, temperature, _ = system.reconstruct(z)
            trace.append(dict(time_s=t, extent_cm3=xi, thermal_eV_cm3=u, temperature_K=temperature))

    trace_row()
    h, consecutive = t_requested_s/16, 0
    while t < t_requested_s:
        if counts['attempts'] >= controls.max_attempts or consecutive >= controls.max_consecutive_rejections:
            return result('WORK_LIMIT', 'Attempt or consecutive rejection cap')
        try:
            g = rhs(z)
            if g == 0:
                t = t_requested_s
                return result('COMPLETE_EQUILIBRIUM')
            side, bound = ('upper', system.interval[1]) if g > 0 else ('lower', system.interval[0])
            distance = abs(bound-z)
            if side in system.provider_bounds and distance <= controls.event_atol_normalized:
                boundary = dict(system.provider_bounds[side], interval_side=side)
                return result('DOMAIN_BOUNDARY_APPROACH')
            h = min(h, t_requested_s-t, 0.8*distance/abs(g))
            if not _finite(h) or h <= 0 or t+h == t:
                return result('STEP_UNDERFLOW')
            counts['attempts'] += 1
            try:
                coarse = heun_step(system, z, h, rhs)
                half = heun_step(system, z, h/2, rhs)
                fine = heun_step(system, half, h/2, rhs)
            except StageOutside:
                counts['rejected_steps'] += 1
                consecutive += 1
                h *= 0.5
                continue
            err = abs(fine-coarse)/3
            tolerance = controls.atol_normalized+controls.rtol*max(abs(z),abs(fine))
            ratio = err/tolerance
            factor = 2.0 if err == 0 else max(0.2, min(2.0, 0.9*(tolerance/err)**(1/3)))
            if err <= tolerance:
                z, t = fine, t+h
                counts['accepted_steps'] += 1
                consecutive = 0
                maximum_ratio = max(maximum_ratio, ratio)
                trace_row()
                h *= factor
            else:
                counts['rejected_steps'] += 1
                consecutive += 1
                h *= min(0.8, factor)
        except WorkLimit as exc:
            return result('WORK_LIMIT', str(exc))
        except (FieldFailure, StageOutside, ArithmeticError, ValueError) as exc:
            return result('ARITHMETIC_FAILURE', str(exc))
    return result('COMPLETE')


def state_at_temperature(h0, hp, d0, dp, temperature_K):
    """Convenience initializer; the integration API only accepts thermal inventory."""
    nth = h0+hp+d0+dp+hp+dp
    return State(h0,hp,d0,dp,1.5*KB_EV_K*nth*temperature_K)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='JSON state, defect, t_requested_s; Savin2002 only')
    parser.add_argument('--output', help='JSON destination; otherwise stdout')
    args = parser.parse_args()
    with open(args.input) as handle:
        item = json.load(handle)
    answer = integrate(State(**item['state']), Defect(**item['defect']), SAVIN2002,
                       item['t_requested_s'], Controls(**item.get('controls', {})))
    payload = json.dumps(answer, indent=2, allow_nan=False)+'\n'
    if args.output:
        with open(args.output, 'w') as handle: handle.write(payload)
    else:
        print(payload, end='')
    return 0 if answer['full_interval_complete'] else 2

if __name__ == '__main__':
    raise SystemExit(main())
