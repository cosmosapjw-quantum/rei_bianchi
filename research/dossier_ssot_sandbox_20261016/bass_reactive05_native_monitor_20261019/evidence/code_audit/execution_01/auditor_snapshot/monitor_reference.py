#!/usr/bin/env python3
"""Independent quadrature/opacity formulas for BR05 exported data.

W1 uses the quantile antiderivative (Rust uses CDF-space plateau integrals).
Verner literals reproduce the pinned owner contract, not a new atomic model.
"""
import math
from decimal import Decimal as D, localcontext


def expm1(x):
    if abs(x) >= D('.001'):
        return x.exp() - 1
    value = term = x
    k = 1
    while True:
        k += 1
        term *= x / k
        new = value + term
        if new == value:
            return value
        value = new


def phi(tau):
    return D(1) if tau == 0 else -expm1(-tau) / tau


def age_reference(tau, nodes, precision=90):
    """Unit born constant-opacity mass/conditional CDF and quantile W1."""
    with localcontext() as context:
        context.prec = precision
        t = D(str(tau))
        if not t.is_finite() or t < 0:
            raise ValueError('invalid tau')
        atoms = sorted((D(str(x)), D(str(w))) for x, w in nodes)
        if any(not x.is_finite() or not 0 <= x <= 1 or not w.is_finite() or w < 0 for x, w in atoms):
            raise ValueError('invalid atom')
        atoms = [(x, w) for x, w in atoms if w > 0]
        exact_mass = phi(t)
        weights = [w * (-t * x).exp() for x, w in atoms]
        mass = sum(weights, D(0))
        if not mass:
            return {'mass': 0.0, 'exact_mass': float(exact_mass), 'relative_mass_defect': -1.0,
                    'w1': None, 'cdf_sup': None, 'mean': None, 'second': None}
        norm = -expm1(-t) if t else D(1)

        def cdf(x):
            return x if not t else -expm1(-t*x) / norm

        def integrated_quantile(p):
            if not t:
                return p*p/2
            if t < D('.001'):
                # Integral of sum_k (norm*p)^k/(k*t). Avoid subtracting
                # nearly equal numbers when the reference approaches uniform.
                k = 1
                power = norm * p
                value = power * p / (2*t)
                while True:
                    k += 1
                    power *= norm*p
                    new = value + power*p/(k*(k+1)*t)
                    if new == value:
                        return value
                    value = new
            # z log z has limit zero, including exponentially tiny tails that
            # round away at the chosen arbitrary precision.
            z = max(D(0), 1 - norm*p)
            return ((z*z.ln() if z else 0) - z + 1) / (norm*t)

        c = D(0)
        ks = D(0)
        distance = D(0)
        for index, ((x, _), w) in enumerate(zip(atoms, weights)):
            next_c = D(1) if index == len(atoms)-1 else min(D(1), c + w/mass)
            fx = cdf(x)
            ks = max(ks, abs(c-fx), abs(next_c-fx))
            split = min(max(fx, c), next_c)
            distance += x*(split-c) - (integrated_quantile(split)-integrated_quantile(c))
            distance += integrated_quantile(next_c)-integrated_quantile(split) - x*(next_c-split)
            c = next_c
        if not t:
            exact_second = D(1)/3
        elif t < 1:
            k = 0
            term = D(1)
            integral = term/3
            while True:
                k += 1
                term *= -t/k
                new = integral + term/(k+3)
                if new == integral:
                    break
                integral = new
            exact_second = integral/exact_mass
        else:
            exact_second = 2/(t*t) - (1+2/t)*(-t).exp()/norm
        return {key: float(val) for key, val in {
            'mass': mass, 'exact_mass': exact_mass, 'relative_mass_defect': mass/exact_mass-1,
            'w1': distance, 'cdf_sup': ks,
            'exact_mean': integrated_quantile(D(1)), 'exact_second': exact_second,
            'mean': sum(w*x for (x, _), w in zip(atoms, weights))/mass,
            'second': sum(w*x*x for (x, _), w in zip(atoms, weights))/mass,
        }.items()}


VERNER = (
    (13.60, .4298, 5.475e4, 32.88, 2.963, 0., 0., 0.),
    (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, .4434, 2.136),
    (54.42, 1.720, 1.369e4, 32.88, 2.963, 0., 0., 0.),
)
CHI = (13.598434599702, 24.587389011, 54.41776, 13.602134599702)
SPECIES = (1, 10, 11, 3)
SPEED_OF_LIGHT = 299792458.0
EV_J = 1.602176634e-19


def cross_section_m2(energy, species):
    if not math.isfinite(energy) or not 0 <= energy <= 50000 or species not in range(4):
        raise ValueError('invalid photon/species')
    if energy < CHI[species]:
        return 0.0
    eth, e0, sigma0, ya, p, yw, y0, y1 = VERNER[0 if species == 3 else species]
    if energy < eth:
        return 0.0
    x = energy/e0-y0
    y = math.hypot(x, y1)
    return sigma0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+math.sqrt(y/ya))**(-p)*1e-22


def opacity(energy, density):
    return [density[sp] * cross_section_m2(energy, i) * SPEED_OF_LIGHT for i, sp in enumerate(SPECIES)]


def sfr_from_volume(volume):
    zp = volume**(-1/3)
    return .015*zp**2.7/(1+(zp/2.9)**5.6)


def ray_from_killing(killing, scale_factors):
    p = [k/a for k, a in zip(killing, scale_factors)]
    energy = math.sqrt(math.fsum(x*x for x in p))
    return energy, [x/energy for x in p]
