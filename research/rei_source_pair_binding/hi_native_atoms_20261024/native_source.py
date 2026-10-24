"""Exact represented finite HI measure; no deposition or evolution solver.

All public numerical inputs accept finite int/float/Fraction, excluding bool.
The immutable structures retain exact values; ``jsonable`` encodes rationals
as numerator/denominator strings. Historical summary bytes/API are separate.
"""
from __future__ import annotations
from bisect import bisect_right
import csv
from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction
import hashlib
import io
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_SHA256 = 'f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3'
SUMMARY_SHA256 = '1b4077f58752b2112ebdac1661d19c7942612adcf65fa5e98a41bb9bdb3707dd'
CHI = Fraction(13.6)
ZERO = Fraction(0)
ENERGY_OWNERS = ('thermal', 'binding', 'UV', 'dynamic_escape', 'source_reservoir', 'primary_nonthermal')
PARTICLE_OWNERS = ('HI', 'HII', 'e_nt', 'e_th', 'photon')


def rational(value, label='value', *, nonnegative=False, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ValueError(label + ': finite int/float/Fraction required')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(label + ': finite value required')
    result = Fraction(value)
    if (nonnegative and result < 0) or (positive and result <= 0):
        raise ValueError(label + ': invalid sign')
    return result


def _atoms(rows, chi):
    result = tuple((rational(k, 'kinetic', nonnegative=True),
                    rational(w, 'weight', positive=True)) for k, w in rows)
    if not result or any(k + chi > 50000 for k, w in result):
        raise ValueError('positive nonempty measure within photon support required')
    return result


def load_selected_atoms(path=None, *, channel='HI', redshift=2.479):
    """Read exact pinned CSV, preserving file bytes/order and binary64 lift."""
    z = rational(redshift, 'redshift', nonnegative=True)
    if channel != 'HI' or z != Fraction(2.479):
        raise ValueError('only pinned HI/z2.479 selection supported')
    data = (Path(path) if path is not None else HERE/'inputs/photoelectron_atoms.csv').read_bytes()
    if len(data) != 1681578 or hashlib.sha256(data).hexdigest() != CSV_SHA256:
        raise ValueError('immutable CSV byte identity mismatch')
    selected = []
    for row in csv.DictReader(io.StringIO(data.decode('ascii'), newline='')):
        if row['channel'] == channel and float(row['redshift']) == float(redshift):
            selected.append((Fraction(float(row['kinetic_eV'])),
                             Fraction(float(row['number_weight_per_target_s']))))
    if len(selected) != 4368:
        raise ValueError('pinned selection requires 4368 rows')
    return _atoms(selected, CHI)


@dataclass(frozen=True)
class Moments:
    A: Fraction
    K: Fraction
    B: Fraction
    P: Fraction
    chi: Fraction
    atom_count: int
    maximum_kinetic: Fraction


def native_moments(atoms, *, threshold_eV=13.6):
    chi = rational(threshold_eV, 'threshold', nonnegative=True)
    rows = _atoms(atoms, chi)
    A = sum((w for k, w in rows), ZERO)
    K = sum((w*k for k, w in rows), ZERO)
    B = chi*A
    P = sum((w*(k+chi) for k, w in rows), ZERO)
    return Moments(A, K, B, P, chi, len(rows), max(k for k, w in rows))


def _rounded_component(exact):
    try:
        value = float(exact)
    except OverflowError as exc:
        raise ValueError('final binary64 overflow') from exc
    if not math.isfinite(value):
        raise ValueError('final binary64 overflow')
    represented = Fraction(value)
    gaps = [abs(Fraction(adj)-represented) for adj in
            (math.nextafter(value, -math.inf), math.nextafter(value, math.inf))
            if math.isfinite(adj)]
    # At finite extreme only the finite adjacent spacing participates.
    bound = max(gaps)/2
    error = represented-exact
    if abs(error) > bound:
        raise ArithmeticError('component RN half-adjacent-gap gate failed')
    tag = ('exact_zero' if exact == 0 else 'final_underflow_to_zero' if value == 0
           else 'subnormal' if abs(value) < float.fromhex('0x1p-1022') else 'normal')
    return value, error, bound, tag


@dataclass(frozen=True)
class Vector:
    exact: tuple
    rounded: tuple
    errors: tuple
    error_bounds: tuple
    tags: tuple
    exact_sum: Fraction
    rounded_sum_exact: Fraction
    rounding_budget: Fraction


def _vector(values):
    values = tuple(values)
    component = tuple(_rounded_component(v) for v in values)
    rounded, errors, bounds, tags = tuple(zip(*component))
    return Vector(values, rounded, errors, bounds, tags, sum(values, ZERO),
                  sum((Fraction(v) for v in rounded), ZERO), sum(bounds, ZERO))


@dataclass(frozen=True)
class Source:
    normalization: Fraction
    energy: Vector
    particles: Vector
    nuclei_residual_exact: Fraction
    charge_residual_exact: Fraction
    secondary_heat: None = None
    global_physical_error_bound: None = None


def _source(moment, multiplier):
    energy = _vector((ZERO, multiplier*moment.B, -multiplier*moment.P,
                      ZERO, ZERO, multiplier*moment.K))
    n = multiplier*moment.A
    particles = _vector((-n, n, n, ZERO, -n))
    return Source(multiplier, energy, particles,
                  particles.exact[0]+particles.exact[1],
                  particles.exact[1]-particles.exact[2]-particles.exact[3])


def source_per_href_native(moment, X_HI, *, a=1):
    """Href route: a*X_HI once; no physical-density normalization."""
    return _source(moment, rational(a, 'a', nonnegative=True)
                   * rational(X_HI, 'X_HI', nonnegative=True))


def source_jvp_native(moment, X_HI, dX_HI, *, a=1, da=0):
    X = rational(X_HI, 'X_HI', nonnegative=True)
    scale = rational(a, 'a', nonnegative=True)
    dm = scale*rational(dX_HI, 'dX_HI') + X*rational(da, 'da')
    return _source(moment, dm)


def rounding_decomposition(atoms, summary, *, threshold_eV=13.6, moment=None):
    """Provider operation-order deltas; finite data fsum certificate only.

    ``summary`` is the unchanged source-card dictionary. Scalar RN checks use
    direct binary64 additions/products; exact terms use original Fractions.
    """
    chi = rational(threshold_eV, 'threshold', nonnegative=True)
    rows = _atoms(atoms, chi)
    if any(Fraction(float(v)) != v for row in rows for v in row) or Fraction(float(chi)) != chi:
        raise ValueError('provider comparison requires binary64 represented inputs')
    if moment is None:
        moment = native_moments(rows, threshold_eV=chi)
    elif moment.chi != chi or moment.atom_count != len(rows):
        raise ValueError('reused native moment threshold/count mismatch')
    saved = summary['result']
    names = {'A': 'number_per_target_s', 'K': 'kinetic_eV_per_target_s',
             'B': 'binding_eV_per_target_s', 'P': 'absorbed_photon_eV_per_target_s'}
    hats = {key: rational(saved[name], name) for key, name in names.items()}
    rk, rp, photon_errors, product_errors = [], [], [], []
    scalar_checks = 0
    for k, w in rows:
        kf, wf, cf = float(k), float(w), float(chi)
        kr, er, pr = kf*wf, kf+cf, wf*(kf+cf)
        for exact, direct in ((k*w, kr), (k+chi, er), (w*Fraction(er), pr)):
            rounded, error, bound, tag = _rounded_component(exact)
            if rounded != direct:
                raise ArithmeticError('provider direct scalar RN mismatch')
            scalar_checks += 1
        rk.append(Fraction(kr)); rp.append(Fraction(pr))
        photon_errors.append(w*(Fraction(er)-(k+chi)))
        product_errors.append(Fraction(pr)-w*Fraction(er))
    SK, SP = sum(rk, ZERO), sum(rp, ZERO)
    subtotals = {'A': moment.A, 'K': SK, 'P': SP}
    fsum_deltas = {key: hats[key]-subtotal for key, subtotal in subtotals.items()}
    fsum_certificates = {key: abs(delta) <= Fraction(math.ulp(float(hats[key])))
                         for key, delta in fsum_deltas.items()}
    recomputed = {'A': math.fsum(float(w) for k, w in rows),
                  'K': math.fsum(float(x) for x in rk),
                  'P': math.fsum(float(x) for x in rp)}
    scalar_saved_agreement = all(Fraction(v) == hats[key] for key, v in recomputed.items())
    direct_b = float(chi)*float(hats['A'])
    rounded_b, _, _, _ = _rounded_component(chi*hats['A'])
    scalar_saved_agreement = scalar_saved_agreement and direct_b == rounded_b == float(hats['B'])
    scalar_checks += 1
    delta = {key: hats[key]-getattr(moment, key) for key in names}
    terms = {'A': (hats['A']-moment.A,),
             'K': (hats['K']-SK, sum(rk, ZERO)-moment.K),
             'B': (hats['B']-chi*hats['A'], chi*delta['A']),
             'P': (hats['P']-SP, sum(product_errors, ZERO), sum(photon_errors, ZERO))}
    identities = {key: delta[key]-sum(parts, ZERO) for key, parts in terms.items()}
    represented_r_E = hats['B']+hats['K']-hats['P']
    represented_r_B = hats['B']-chi*hats['A']
    bins = []
    for index in range(3):
        selected = tuple((k,w) for k,w in rows if bisect_right((10.0, 9937.21), float(k)) == index)
        sb = saved['bins'][index]
        bA = sum((w for k,w in selected), ZERO)
        bK = sum((k*w for k,w in selected), ZERO)
        rounded_A = math.fsum(float(w) for k,w in selected)
        rounded_K = math.fsum(float(k)*float(w) for k,w in selected)
        bins.append({'index': index, 'row_count': len(selected), 'A_exact': bA, 'K_exact': bK,
                     'saved_A': sb['number_per_target_s'], 'saved_K': sb['kinetic_eV_per_target_s'],
                     'provider_scalar_agreement': rounded_A == sb['number_per_target_s'] and rounded_K == sb['kinetic_eV_per_target_s']})
    return {'delta': delta, 'terms': terms, 'identity_residuals': identities,
            'fsum_stage_deltas': fsum_deltas, 'finite_fsum_ulp_certificates': fsum_certificates,
            'direct_scalar_checks': scalar_checks, 'saved_provider_scalars_agree': scalar_saved_agreement,
            'represented_r_E_B_plus_K_minus_P': represented_r_E,
            'represented_r_B_B_minus_chi_A': represented_r_B,
            'delta_r_E_identity': delta['B']+delta['K']-delta['P']-represented_r_E,
            'delta_r_B_identity': delta['B']-chi*delta['A']-represented_r_B,
            'donor_residual_operation': 'P-B-K sequential binary64',
            'donor_residual_saved': saved['energy_ledger_residual_eV_per_target_s'],
            'donor_residual_recomputed': float(hats['P'])-float(hats['B'])-float(hats['K']),
            'bins': bins}


def jsonable(value):
    if isinstance(value, Fraction):
        return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}
    if is_dataclass(value):
        return {field.name: jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [jsonable(v) for v in value]
    return value
