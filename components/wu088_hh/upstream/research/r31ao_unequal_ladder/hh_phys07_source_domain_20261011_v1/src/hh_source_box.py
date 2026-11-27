"""Source-derived FT03 + LCS91 + reduced-photon reference family.

This module evaluates arithmetic on supplied boxes.  It contains no native
callback, endpoint, backward-Euler point solve, root search, time integrator,
or permission issuer.  Its interval/second-jet backend is certified_interval.

The reduced-source AST is phys04_mixed.rs::phys04_reduced_residual, with the
zero-sigma FT03 baseline from ft03_interval.rs.  Binary64 literal leaves and
stored nHe are explicit.  Scalar charts and provider leaves must identify their
semantics separately; this port is not a native interval-byte reproduction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, Sequence

from certified_interval import I, J

NVAR = 6
GAS_SLOTS = (0, 1, 2, 3)
LAMBDA_SLOT = 4
B_SLOT = 5
CHI = (13.598_434_599_702, 24.587_389_011, 54.417_76)
C_CM_S = 29_979_245_800.0
KB_ERG_K = 1.380_649e-16
EV_ERG = 1.602_176_634e-12
FHE = 0.083
SOURCE_PER_H_S = 5e-15
BIRTH_EV = 13.7
DR_A = struct.unpack('>d', bytes.fromhex('3f5f8b1ba9b90acb'))[0]
DR_B1 = struct.unpack('>d', bytes.fromhex('411caf2e364afdee'))[0]
DR_B12 = struct.unpack('>d', bytes.fromhex('412135e886f9cb6f'))[0]


def as_i(value):
    return value if isinstance(value, I) else I(value)


def jc(value, n=NVAR):
    return J.constant(as_i(value), n=n)


def jproduct(items: Sequence[J]) -> J:
    if not items:
        return jc(1)
    out = jc(1, n=len(items[0].g))
    for item in items:
        out = out * item
    return out


def i_zero(value: I) -> bool:
    return value.lo == 0 and value.hi == 0


def fraction_json(value: Fraction) -> dict:
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def interval_json(value: I) -> dict:
    return {
        'lo': fraction_json(value.lo),
        'hi': fraction_json(value.hi),
        'display_float': [float(value.lo), float(value.hi)],
        'display_float_is_not_the_certified_endpoint': True,
    }


def jet_json(value: J, *, hessian=True) -> dict:
    out = {'value': interval_json(value.v), 'gradient': [interval_json(z) for z in value.g]}
    if hessian:
        out['hessian'] = [[interval_json(z) for z in row] for row in value.h]
    return out


def parse_fraction(value) -> Fraction:
    if isinstance(value, dict):
        return Fraction(int(value['numerator']), int(value['denominator']))
    if isinstance(value, float):
        return Fraction.from_float(value)
    return Fraction(value)


def parse_interval(value) -> I:
    if isinstance(value, dict) and 'lo' in value:
        return I(parse_fraction(value['lo']), parse_fraction(value['hi']))
    if isinstance(value, list) and len(value) == 2:
        return I(parse_fraction(value[0]), parse_fraction(value[1]))
    return I(parse_fraction(value))


@dataclass(frozen=True)
class Stage:
    n_h: I
    n_he_stored: I
    f_he: I
    h_mean: I
    c: I = field(default_factory=lambda: I(C_CM_S))
    kb: I = field(default_factory=lambda: I(KB_ERG_K))
    ev: I = field(default_factory=lambda: I(EV_ERG))
    thresholds: tuple = CHI

    def validate(self):
        if self.n_h.lo <= 0 or self.n_he_stored.lo <= 0 or self.f_he.lo <= 0:
            raise ValueError('PRIMARY_STAGE_DENSITY_DOMAIN')
        if self.h_mean.lo < 0 or self.kb.lo <= 0 or self.ev.lo <= 0 or self.c.lo <= 0:
            raise ValueError('PRIMARY_STAGE_CONSTANT_DOMAIN')


@dataclass(frozen=True)
class Family:
    stage: Stage
    old_gas: tuple
    energies: tuple
    sigma: tuple
    nbar: tuple
    birth: tuple
    dt: float
    metadata: dict = field(default_factory=dict)

    def validate(self):
        self.stage.validate()
        if not self.dt > 0 or len(self.old_gas) != 4:
            raise ValueError('PHYS07_FAMILY_LAYOUT')
        n = len(self.energies)
        if not n or any(len(x) != n for x in (self.sigma, self.nbar, self.birth)):
            raise ValueError('PHYS07_PHOTON_LAYOUT')
        if any(len(row) != 3 or any(z.lo < 0 for z in row) for row in self.sigma):
            raise ValueError('PHYS07_SIGMA_DOMAIN')
        if any(z.lo < 0 for z in (*self.nbar, *self.birth)):
            raise ValueError('PHYS07_PHOTON_CONE')
        if any(e <= 0 for e in self.energies):
            raise ValueError('PHYS07_ENERGY_DOMAIN')


def temperature(stage: Stage, gas: Sequence[J]) -> tuple[J, J]:
    """Source AST uses stored nHe/nH, not stage.f_he, in T and ne."""
    n = len(gas[0].g)
    c = lambda z: jc(z, n)
    one, two, three = c(1.0), c(2.0), c(3.0)
    nh, nhe = c(stage.n_h), c(stage.n_he_stored)
    fhe = nhe / nh
    particles = ((one + fhe) + gas[0]) + fhe * (gas[1] + two * gas[2])
    temp = ((two * c(stage.ev)) * gas[3]) / ((three * c(stage.kb)) * particles)
    return temp, particles


def ft03_nonphoto(stage: Stage, gas: Sequence[J]) -> dict:
    """Zero-sigma specialization of ft03_interval_rhs; all active AST kept.

    Original dummy photon variables have sigma=0 identically, so their exact
    contributions and derivatives are zero.  The three identically zero loops
    are omitted; no raw native interval width is claimed.
    """
    stage.validate()
    if len(gas) != 4:
        raise ValueError('FT03_GAS_LAYOUT')
    if any(x.v.lo <= 0 for x in gas):
        raise ValueError('FT03_INTERVAL_DOMAIN')
    if gas[0].v.hi >= 1 or gas[1].v.hi + gas[2].v.hi >= 1:
        raise ValueError('FT03_SIMPLEX_DOMAIN')
    n = len(gas[0].g)
    c = lambda z: jc(z, n)
    one, two = c(1.0), c(2.0)
    nh, nhe, ev, kb = c(stage.n_h), c(stage.n_he_stored), c(stage.ev), c(stage.kb)
    fhe = nhe / nh
    temp, particles = temperature(stage, gas)
    if temp.v.lo < 30_000 or temp.v.hi > 110_000:
        raise ValueError('FT03_TEMPERATURE_DOMAIN')
    ne = nh * gas[0] + nhe * (gas[1] + two * gas[2])
    lower = (nh * (one - gas[0]), nhe * ((one - gas[1]) - gas[2]), nhe * gas[1])
    upper = (nh * gas[0], nhe * gas[1], nhe * gas[2])
    lam = (315_614.0, 570_670.0, 1_263_030.0)
    ci_a = (21.11, 32.38, 19.95)
    ci_p = (-1.089, -1.146, -1.089)
    ci_c = (0.354, 0.416, 0.553)
    ci_r = (0.874, 0.987, 0.735)
    ci_d = (1.101, 1.056, 1.275)
    net, collisions, recombinations, kinetic_losses = [], [], [], []
    w = c(0.0)
    escape = c(0.0)
    for a in range(3):
        ell = c(lam[a]) / temp
        if a == 1:
            alpha = c(3e-14) * ell.powf(0.654)
            slope = c(-0.654)
        else:
            u = (ell / c(0.522)).powf(0.470)
            alpha = jproduct((c(2.0 if a == 2 else 1.0), c(1.269e-13), ell.powf(1.503))) / (one + u).powf(1.923)
            slope = c(-1.503) + jproduct((c(1.923), c(0.470), u)) / (one + u)
        beta = jproduct((c(ci_a[a]), temp.powf(-1.5), (-(ell / two)).exp(), ell.powf(ci_p[a]))) / (one + (ell / c(ci_c[a])).powf(ci_r[a])).powf(ci_d[a])
        kinetic = jproduct((kb, temp, alpha, c(1.5) + slope))
        ci = jproduct((lower[a], ne, beta)) / nh
        rr = jproduct((upper[a], ne, alpha)) / nh
        kinetic_loss = jproduct((upper[a], ne, kinetic)) / (nh * ev)
        net.append(ci - rr)
        collisions.append(ci)
        recombinations.append(rr)
        kinetic_losses.append(kinetic_loss)
        w = (w - c(stage.thresholds[a]) * ci) - kinetic_loss
        # Derived exact-real event-energy ledger, not a native raw escape call.
        escape = escape + c(stage.thresholds[a]) * rr + kinetic_loss
    dielectronic = []
    for factor, activation in ((1.0, DR_B1), (0.3, DR_B12)):
        dr = jproduct((upper[1], ne, c(factor), c(DR_A), temp.powf(-1.5), (-(c(activation) / temp)).exp())) / nh
        net[1] = net[1] - dr
        dr_energy = jproduct((dr, kb, c(activation))) / ev
        w = w - dr_energy
        escape = escape + c(stage.thresholds[1]) * dr + dr_energy
        dielectronic.append(dr)
    rhs = (net[0], (net[1] - net[2]) / fhe, net[2] / fhe, w)
    return {
        'rhs': rhs, 'temperature': temp, 'particles': particles, 'electron_density': ne,
        'collision_events_per_H_s': tuple(collisions),
        'recombination_events_per_H_s': tuple(recombinations),
        'rr_kinetic_ev_per_H_s': tuple(kinetic_losses),
        'dielectronic_events_per_H_s': tuple(dielectronic),
        'escaped_energy_ev_per_H_s': escape,
    }


def hh_q(stage: Stage, gas: Sequence[J]) -> J:
    """LCS91 source-specific HH jet, including neutral-fraction square."""
    n = len(gas[0].g)
    c = lambda z: jc(z, n)
    if gas[0].v.lo < 0 or gas[0].v.hi > 1 or gas[1].v.lo < 0 or gas[2].v.lo < 0:
        raise ValueError('HH_ON06_GAS_BOX_DOMAIN')
    if gas[1].v.hi + gas[2].v.hi > 1 or gas[3].v.lo <= 0:
        raise ValueError('HH_ON06_GAS_BOX_DOMAIN')
    temp, _ = temperature(stage, gas)
    if temp.v.lo < 35_000 or temp.v.hi > 60_000:
        raise ValueError('HH_ON06_TEMPERATURE_DOMAIN')
    neutral = c(1.0) - gas[0]
    # .powf is exp(log(T)*exact_binary64(1.2)); exponent is not decimal 6/5.
    return jproduct((c(stage.n_h), neutral, neutral, c(1.2e-17), temp.powf(1.2), (c(-157800.0) / temp).exp()))


def energy_project(stage: Stage, values: Sequence[J]) -> J:
    n = len(values[0].g)
    c = lambda z: jc(z, n)
    # Exact-real linear map: no pre-rounded CHI[1]+CHI[2] or f*CHI leaf.
    return values[3] + c(CHI[0]) * values[0] + c(stage.f_he) * c(CHI[1]) * values[1] + c(stage.f_he) * (c(CHI[1]) + c(CHI[2])) * values[2]


def reduced_residual(family: Family, gas: Sequence[J], lam: J, b: J) -> dict:
    """Full six-slot gas/lambda/b derivative export for first-stage N=Nbar+b B."""
    family.validate()
    if lam.v.lo < 0 or lam.v.hi > 1 or b.v.lo < 0 or b.v.hi > 1:
        raise ValueError('PHYS07_PARAMETER_DOMAIN')
    n = len(gas[0].g)
    c = lambda z: jc(z, n)
    stage = family.stage
    raw = ft03_nonphoto(stage, gas)
    nonphoto = raw['rhs']
    rhs = list(nonphoto)
    q = hh_q(stage, gas)
    rhs[0] = rhs[0] + lam * q
    rhs[3] = rhs[3] - jproduct((c(CHI[0]), lam, q))
    lower = (c(1.0) - gas[0], c(stage.f_he) * ((c(1.0) - gas[1]) - gas[2]), c(stage.f_he) * gas[1])
    incoming, photons, denominators, photo_rates = [], [], [], []
    photo_rhs = [c(0.0) for _ in range(4)]
    for nbar, born, energy, sigma in zip(family.nbar, family.birth, family.energies, family.sigma, strict=True):
        nn = c(nbar) + b * c(born)
        incoming.append(nn)
        opacity = c(0.0)
        for a in range(3):
            opacity = opacity + jproduct((c(stage.c), c(stage.n_h), lower[a], c(sigma[a])))
        den = c(1.0) + c(family.dt) * opacity
        if den.v.lo <= 0:
            raise ValueError('PHYS04_POSITIVE_DENOMINATOR_MISSING')
        ph = nn / den
        rates = []
        for a in range(3):
            rate = jproduct((c(stage.c), c(stage.n_h), lower[a], c(sigma[a]), ph))
            # phys04_mixed.rs uses ic(*e-CHI[a]); subtraction is rounded first.
            heat_leaf = float(energy) - CHI[a]
            rhs[3] = rhs[3] + rate * c(heat_leaf)
            photo_rhs[3] = photo_rhs[3] + rate * c(heat_leaf)
            rates.append(rate)
        rhs[0] = rhs[0] + rates[0]
        rhs[1] = rhs[1] + (rates[1] - rates[2]) / c(stage.f_he)
        rhs[2] = rhs[2] + rates[2] / c(stage.f_he)
        photo_rhs[0] = photo_rhs[0] + rates[0]
        photo_rhs[1] = photo_rhs[1] + (rates[1] - rates[2]) / c(stage.f_he)
        photo_rhs[2] = photo_rhs[2] + rates[2] / c(stage.f_he)
        photo_rates.append(tuple(rates))
        photons.append(ph)
        denominators.append(den)
    expansion = jproduct((c(2.0), c(stage.h_mean), gas[3]))
    rhs[3] = rhs[3] - expansion
    residual = tuple((gas[i] - c(family.old_gas[i])) - c(family.dt) * rhs[i] for i in range(4))
    direct_hh = (q, c(0.0), c(0.0), -(c(CHI[0]) * q))
    fhe_hat = c(stage.n_he_stored) / c(stage.n_h)
    density_correction = (c(stage.f_he) - fhe_hat) * (c(CHI[1]) * nonphoto[1] + (c(CHI[1]) + c(CHI[2])) * nonphoto[2])
    return {
        'residual': residual, 'rhs': tuple(rhs), 'nonphoto': nonphoto,
        'photo_rhs': tuple(photo_rhs), 'direct_hh': direct_hh,
        'temperature': raw['temperature'], 'particles': raw['particles'],
        'electron_density': raw['electron_density'], 'hh_q': q,
        'incoming': tuple(incoming), 'photons': tuple(photons),
        'denominators': tuple(denominators), 'photo_rates': tuple(photo_rates),
        'energy_rhs': energy_project(stage, rhs),
        'energy_residual': energy_project(stage, residual),
        'density_energy_correction': density_correction,
        'escaped_energy': raw['escaped_energy_ev_per_H_s'],
        'collision_events': raw['collision_events_per_H_s'],
        'recombination_events': raw['recombination_events_per_H_s'],
        'dielectronic_events': raw['dielectronic_events_per_H_s'],
        'native_root_certified': False,
        'native_source_tuple_bound': False,
    }


def evaluate_box(family: Family, gas_box: Sequence[I], lambda_box=None, b_box=None) -> dict:
    if len(gas_box) != 4:
        raise ValueError('PHYS07_GAS_BOX_LENGTH')
    gas = tuple(J.variable(as_i(gas_box[i]), i, n=NVAR) for i in range(4))
    lam = J.variable(I(0, 1) if lambda_box is None else as_i(lambda_box), LAMBDA_SLOT, n=NVAR)
    b = J.variable(I(0, 1) if b_box is None else as_i(b_box), B_SLOT, n=NVAR)
    return reduced_residual(family, gas, lam, b)


def family_json(family: Family) -> dict:
    return {
        'schema': 'WU088_HH_PHYS07_SOURCE_DERIVED_REFERENCE_FAMILY_V1',
        'dt_s': family.dt,
        'stage': {
            'n_h_cm3': interval_json(family.stage.n_h),
            'stored_n_he_cm3': interval_json(family.stage.n_he_stored),
            'f_he': interval_json(family.stage.f_he),
            'h_mean_per_s': interval_json(family.stage.h_mean),
        },
        'old_gas': list(family.old_gas), 'energies_ev': list(family.energies),
        'sigma_cm2': [[interval_json(z) for z in row] for row in family.sigma],
        'Nbar_per_H': [interval_json(z) for z in family.nbar],
        'B_per_H': [interval_json(z) for z in family.birth],
        'metadata': family.metadata,
    }


def family_from_json(data: dict) -> Family:
    st = data['stage']
    stage = Stage(parse_interval(st['n_h_cm3']), parse_interval(st['stored_n_he_cm3']), parse_interval(st['f_he']), parse_interval(st['h_mean_per_s']))
    family = Family(stage, tuple(data['old_gas']), tuple(data['energies_ev']), tuple(tuple(parse_interval(z) for z in row) for row in data['sigma_cm2']), tuple(parse_interval(z) for z in data['Nbar_per_H']), tuple(parse_interval(z) for z in data['B_per_H']), data['dt_s'], data.get('metadata', {}))
    family.validate()
    return family


def rn_binary64(value) -> float:
    """Correct nearest/even conversion of exact rational arithmetic to f64."""
    value = value if isinstance(value, Fraction) else Fraction(value)
    return float(value)


class ScalarChart:
    """Correct-rounding reference for scalar f64 leaves; never libm identity.

    Transcendental leaf values are accepted only when both rigorously enclosing
    rational endpoints round to the same binary64.  Native Rust libm was not
    executed and need not return this reference value.
    """
    def __init__(self):
        self.transcendental_leaves = []
        self.scalar_operations = []

    def op(self, label, operator, *args):
        q = tuple(Fraction.from_float(float(x)) for x in args)
        if operator == '+':
            exact = q[0] + q[1]
        elif operator == '-':
            exact = q[0] - q[1]
        elif operator == '*':
            exact = q[0] * q[1]
        elif operator == '/':
            exact = q[0] / q[1]
        elif operator == 'neg':
            exact = -q[0]
        else:
            raise ValueError('PHYS07_SCALAR_OPERATOR')
        value = rn_binary64(exact)
        self.scalar_operations.append({'label': label, 'operator': operator, 'input_hex': [float(x).hex() for x in args], 'output_hex': value.hex(), 'rounding': 'nearest_even_binary64_from_exact_rational'})
        return value

    def transcendental(self, label, operator, value, exponent=None):
        x = I(float(value))
        if operator == 'exp':
            out = x.exp()
        elif operator == 'sqrt':
            out = x.sqrt()
        elif operator == 'powf':
            out = x.powf(float(exponent))
        elif operator == 'log':
            out = x.log()
        else:
            raise ValueError('PHYS07_TRANSCENDENTAL_OPERATOR')
        lower, upper = float(out.lo), float(out.hi)
        if lower.hex() != upper.hex():
            raise ValueError('PHYS07_CORRECT_ROUNDING_NOT_UNIQUE:' + label)
        self.transcendental_leaves.append({'label': label, 'operator': operator, 'input_hex': float(value).hex(), 'exponent_hex': None if exponent is None else float(exponent).hex(), 'certified_exact_real_enclosure': interval_json(out), 'reference_f64_hex': lower.hex(), 'rounding_uniquely_determined': True, 'native_libm_identity': 'UNRESOLVED_NOT_CALLED'})
        return lower


def reference_cross_section(energy: float, species: int, chart: ScalarChart) -> float:
    """AtomicProvider::cross_section source order with declared CR libm leaves."""
    table = ((13.60, 0.4298, 5.475e4, 32.88, 2.963, 0.0, 0.0, 0.0),
             (24.59, 13.61, 949.2, 1.469, 3.188, 2.039, 0.4434, 2.136),
             (54.42, 1.720, 1.369e4, 32.88, 2.963, 0.0, 0.0, 0.0))
    if energy < 0 or energy > 50000 or species not in (0, 1, 2):
        raise ValueError('VERNER_ENERGY_DOMAIN')
    eth, e0, sigma0, ya, power, yw, y0, y1 = table[species]
    if energy < eth:
        return 0.0
    stem = f'sigma_E{energy.hex()}_a{species}'
    op = lambda suffix, operation, *args: chart.op(stem + ':' + suffix, operation, *args)
    tr = lambda suffix, operation, value, exponent=None: chart.transcendental(stem + ':' + suffix, operation, value, exponent)
    x = op('x', '-', op('E/e0', '/', energy, e0), y0)
    y = tr('y', 'sqrt', op('x2+y12', '+', op('x2', '*', x, x), op('y12', '*', y1, y1)))
    x_minus_one = op('x-1', '-', x, 1.0)
    shape = op('shape', '+', op('(x-1)^2', '*', x_minus_one, x_minus_one), op('yw2', '*', yw, yw))
    exponent = op('p/2-5.5', '-', op('p/2', '/', power, 2.0), 5.5)
    power_a = tr('y^exponent', 'powf', y, exponent)
    cutoff = op('1+sqrt(y/ya)', '+', 1.0, tr('sqrt(y/ya)', 'sqrt', op('y/ya', '/', y, ya)))
    power_b = tr('cutoff^-p', 'powf', cutoff, op('-p', 'neg', power))
    result = op('sigma0*shape', '*', sigma0, shape)
    result = op('*power_a', '*', result, power_a)
    result = op('*power_b', '*', result, power_b)
    result = op('*1e-18', '*', result, 1e-18)
    if result < 0:
        raise ValueError('VERNER_RESULT_DOMAIN')
    return result


def _hat_nonnegative(value: I) -> I:
    # The selected support chart proves the exact weight lies in [0,1].
    return I(max(Fraction(0), value.lo), min(Fraction(1), value.hi))


def isotropic_reference_family(archived: dict, dt: float, *, chart: ScalarChart | None = None, provider_sigmas=None) -> tuple[Family, dict]:
    """First-stage reference from a frozen directional stock and isotropic H.

    Transport uses the analytically reduced exact-real geometry chart.  Its
    normalized angular birth weights sum to one.  Scalar density/provider leaves
    follow source f64 operation order with correctly-rounded transcendental
    reference values.  These are two explicitly separate reference layers.
    """
    chart = ScalarChart() if chart is None else chart
    hubble = tuple(archived['hubble_per_s'])
    if len(hubble) != 3 or not hubble[0] == hubble[1] == hubble[2] or hubble[0] < 0:
        raise ValueError('PHYS07_ISOTROPIC_CHART_REQUIRED')
    if archived['grid'] != {'spectral_subdivisions': 8, 'n_mu': 8, 'n_phi': 16, 'directions': 128, 'energies': 33}:
        raise ValueError('PHYS07_FIXED_GRID')
    time0 = float(archived['time_s'])
    dt = float(dt)
    time1 = chart.op('stage.time_plus_dt', '+', time0, dt)
    if dt <= 0 or time0 < 0 or time1 > 1e13:
        raise ValueError('PHYS07_REFERENCE_CLOCK_DOMAIN')
    sumh = 0.0
    for i, hi in enumerate(hubble):
        sumh = chart.op(f'stage.iter_sum_h_{i}', '+', sumh, hi)
    arg = chart.op('stage.exp_argument', '*', chart.op('stage.neg_sumh', 'neg', sumh), time1)
    exp_leaf = chart.transcendental('stage.exp', 'exp', arg)
    nh = chart.op('stage.nH', '*', 1e-4, exp_leaf)
    nhe = chart.op('model.stored_nHe', '*', nh, FHE)
    hmean = chart.op('stage.hmean', '/', sumh, 3.0)
    born_leaf = chart.op('transport.dt_times_SOURCE', '*', dt, SOURCE_PER_H_S)
    stage = Stage(I(nh), I(nhe), I(FHE), I(hmean))
    energies = tuple(float(g['energy_eV']) for g in archived['groups'])
    if len(energies) != 33 or energies[24] != BIRTH_EV or energies[0] != 10.0 or energies[-1] != 20.0:
        raise ValueError('PHYS07_ARCHIVED_GRID_IDENTITY')
    old_counts = tuple(parse_fraction(g['direction_sum_exact']) for g in archived['groups'])
    if any(z < 0 for z in old_counts):
        raise ValueError('PHYS07_ARCHIVED_PHOTON_CONE')
    # Geometry .g_box uses interval products, hence no pre-rounded -H*dt here.
    elapsed_exact = Fraction.from_float(time1) - Fraction.from_float(time0)
    redshift_argument = -Fraction.from_float(hubble[0]) * elapsed_exact
    redshift = I(redshift_argument).exp()
    nbar = [I(0) for _ in energies]
    exported_n = I(0)
    exported_u = I(0)
    branches = []
    for j, (energy, old_count) in enumerate(zip(energies, old_counts, strict=True)):
        shifted = I(energy) * redshift
        if shifted.hi > 20:
            raise ValueError('PHYS04_UPPER_GUARD_UNSUPPORTED')
        if shifted.hi < 10:
            exported_n = exported_n + I(old_count)
            exported_u = exported_u + I(old_count) * shifted
            branches.append({'old_node': j, 'branch': 'lower_guard', 'energy_interval': interval_json(shifted), 'nonzero_old_stock': old_count != 0})
            continue
        if shifted.lo < 10:
            raise ValueError('PHYS04_GUARD_BRANCH_CROSSING')
        if any(shifted.lo < Fraction.from_float(k) < shifted.hi for k in energies):
            raise ValueError('PHYS04_HAT_BRANCH_CROSSING')
        support = next((k for k in range(32) if Fraction.from_float(energies[k]) <= shifted.lo and shifted.hi <= Fraction.from_float(energies[k + 1])), None)
        if support is None:
            raise ValueError('PHYS07_FIXED_HAT_SUPPORT_MISSING')
        lo, hi = I(energies[support]), I(energies[support + 1])
        left = _hat_nonnegative((hi - shifted) / (hi - lo))
        right = _hat_nonnegative((shifted - lo) / (hi - lo))
        nbar[support] = nbar[support] + I(old_count) * left
        nbar[support + 1] = nbar[support + 1] + I(old_count) * right
        branches.append({'old_node': j, 'branch': 'fixed_hat_segment', 'target_nodes': [support, support + 1], 'energy_interval': interval_json(shifted), 'weights': [interval_json(left), interval_json(right)], 'nonzero_old_stock': old_count != 0})
    birth = tuple(I(born_leaf if j == 24 else 0) for j in range(33))
    sigma = (tuple(tuple(I(reference_cross_section(e, a, chart)) for a in range(3)) for e in energies)
             if provider_sigmas is None else tuple(tuple(as_i(z) for z in row) for row in provider_sigmas))
    metadata = {
        'family_scope': 'FIRST_STAGE_SOURCE_DERIVED_REFERENCE_ONLY',
        'old_gas_choice': 'fixed archived gas_point.values, theta-independent; archived gas_box is retained as provenance, not an incoming uncertain family',
        'old_photon_choice': 'exact sum of archived directional binary64 stocks; not stored primary packet count and not PHYS06 frozen stock reused as Nbar',
        'theta': {'lambda': [0, 1], 'b': [0, 1]},
        'first_stage_incoming': 'N_j(b) = Nbar_j + b*B_j; N_lambda=N_lambdab=0 and B is fixed',
        'coefficient_enclosure_semantics': 'Nbar intervals enclose one fixed theta-independent vector defined by the analytic remap; their endpoints are not separately chosen as theta varies. Treating their boxes independently only enlarges the source enclosure.',
        'clock': {'time0_s': time0, 'dt_s': dt, 'time1_f64_s': time1, 'elapsed_exact': fraction_json(elapsed_exact)},
        'transport_chart': {'kind': 'analytically reduced exact-real isotropic g-ratio and normalized angular sum', 'r': interval_json(redshift), 'r_argument_exact': fraction_json(redshift_argument), 'formula': 'g(q,t1)/g(q,t0)=exp(-H*(t1-t0)); sum_d normalized source weights = 1', 'native_widened_weight_interval_reproduction': False, 'native_qhat_leaves_required_for_this_analytic_cancellation': False},
        'scalar_leaf_chart': {'kind': 'source binary64 operation order with uniquely correctly-rounded reference transcendental leaves', 'density_exp_argument_hex': arg.hex(), 'nH_hex': nh.hex(), 'stored_nHe_hex': nhe.hex(), 'fHe_hex': FHE.hex(), 'hmean_hex': hmean.hex(), 'birth_dt_SOURCE_hex': born_leaf.hex(), 'native_libm_bitwise_identity': 'UNRESOLVED_NOT_CALLED'},
        'native_Phys04PreBE_tuple': None,
        'provider_leaf_semantics': 'AtomicProvider source AST with correctly-rounded reference sqrt/pow leaves; native Rust libm identity OPEN',
        'provider_sigma_reused_in_this_call': provider_sigmas is not None,
        'native_Phys04PreBE_equivalence': 'OPEN',
        'actual_HH_W': None,
        'actual_native_root': None,
        'second_half_history': 'NOT_CONSTRUCTED_NOT_INHERITED',
        'source_model_change': 'No reaction or closure changed; this is a separately declared scalar/geometry reference chart and is not installed into native source.',
    }
    family = Family(stage, tuple(archived['gas_point']['values']), energies, sigma, tuple(nbar), birth, dt, metadata)
    family.validate()
    audit = {
        'schema': 'WU088_HH_PHYS07_REFERENCE_CHART_AUDIT_V1',
        'metadata': metadata,
        'branches': branches,
        'lower_guard_export_n_per_H': interval_json(exported_n),
        'lower_guard_export_u_ev_per_H': interval_json(exported_u),
        'source_birth_total_per_H': interval_json(I(born_leaf)),
        'source_birth_total_ev_per_H': interval_json(I(born_leaf) * I(BIRTH_EV)),
        'reference_transcendental_leaves': chart.transcendental_leaves,
        'reference_binary64_scalar_operations': chart.scalar_operations,
        'native_calls': {'provider': 0, 'preBE': 0, 'endpoint': 0, 'BE_point': 0, 'root': 0, 'IVP': 0},
    }
    return family, audit


def source_box_export(family: Family, gas_box: Sequence[I], result: dict) -> dict:
    return {
        'schema': 'WU088_HH_PHYS07_SOURCE_BOX_JET_EXPORT_V1',
        'family_metadata': family.metadata,
        'dt_s': family.dt,
        'derivative_slots': ['x_HII', 'x_HeII', 'x_HeIII', 'w_eV_per_H', 'lambda', 'b'],
        'gas_box': [interval_json(z) for z in gas_box],
        'theta': {'lambda': [0, 1], 'b': [0, 1]},
        'residual': [jet_json(z) for z in result['residual']],
        'rhs': [jet_json(z) for z in result['rhs']],
        'temperature_K': jet_json(result['temperature']),
        'particle_factor': jet_json(result['particles']),
        'electron_density_cm3': jet_json(result['electron_density']),
        'HH_events_per_H_s': jet_json(result['hh_q']),
        'photo_rhs': [jet_json(z) for z in result['photo_rhs']],
        'nonphoto_rhs': [jet_json(z) for z in result['nonphoto']],
        'energy_rhs_ev_per_H_s': jet_json(result['energy_rhs']),
        'energy_residual_ev_per_H': jet_json(result['energy_residual']),
        'density_energy_correction': jet_json(result['density_energy_correction']),
        'escaped_energy_ev_per_H_s': jet_json(result['escaped_energy']),
        'incoming_per_H': [jet_json(z, hessian=False) for z in result['incoming']],
        'photon_denominators': [interval_json(z.v) for z in result['denominators']],
        'outgoing_photon_values_per_H': [interval_json(z.v) for z in result['photons']],
        'structural_fixed_gas_G_lambdab_zero': all(i_zero(z.h[LAMBDA_SLOT][B_SLOT]) for z in result['residual']),
        'source_reference_arithmetic_only': True,
        'native_source_tuple_bound': False,
        'native_root_certified': False,
    }
