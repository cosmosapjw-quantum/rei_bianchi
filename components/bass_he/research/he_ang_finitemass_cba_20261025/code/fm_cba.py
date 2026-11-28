"""Finite-mass labelled direct CBA, THEORY_KO equations 1-14.

Only this unit's composition is new. Immutable parent kernels supply matched
overlaps, Coulomb normalization, Jacobi maps and all positive radial roots.
No exchange-complete or calibrated physical provider is implied.
"""
import importlib.util
import math
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
RESEARCH = UNIT.parent


def _parent(name, relative):
    spec = importlib.util.spec_from_file_location(name, RESEARCH / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cba = _parent('immutable_parent100_cba', 'he_ang_cba_nordsieck_20261025/code/cba.py')
shell = _parent('immutable_parent99_shell', 'he_ang_finitemass_shell_20261024/code/shell.py')
MODEL = 'finite-M Jacobi C1 labelled direct CBA; spin factor1; exchange absent'


def finite_mass_parameters(M):
    M = cba._real(M, 'M')
    if M <= 0 or not math.isfinite(M + 2):
        raise ValueError('require positive finite representable mass M')
    mu, nu = M / (M + 1), (M + 1) / (M + 2)
    return {'M': M, 'mu': mu, 'nu': nu, 'a': mu, 'b': 1 / (M + 1),
            'lambda': mu, 'binding': mu / 2, 'T': M + 2}


def overlap_terms(M, Delta, kvec):
    z = finite_mass_parameters(M)
    Delta, kvec = cba._vector(Delta, 'Delta'), cba._vector(kvec, 'kvec')
    if math.hypot(*kvec) <= 0:
        raise ValueError('Coulomb continuum endpoint k=0 excluded')
    plus = cba.matched_overlap(z['mu'], tuple(z['a'] * d for d in Delta), kvec)
    minus = cba.matched_overlap(z['mu'], tuple(-z['b'] * d for d in Delta), kvec)
    return plus, minus


def finite_form_factor(M, Delta, kvec):
    """Eq9, two stable parent overlaps at a*Delta and -b*Delta."""
    z = finite_mass_parameters(M)
    kvec = cba._vector(kvec, 'kvec')
    k = math.hypot(*kvec)
    if k <= 0:
        raise ValueError('Coulomb continuum endpoint k=0 excluded')
    plus, minus = overlap_terms(M, Delta, kvec)
    return cba.coulomb_normalizer(z['mu'] / k) * math.sqrt(z['mu'] ** 3 / math.pi) * (plus - minus)


def _beam(E0, M):
    z = finite_mass_parameters(M)
    E0 = cba._real(E0, 'E0')
    if E0 <= 0:
        raise ValueError('require E0>0')
    P = math.sqrt(2 * E0)
    if not math.isfinite(P):
        raise ValueError('unrepresentable beam momentum')
    return {**z, 'E0': E0, 'P': (0., 0., P), 'qi': z['nu'] * P,
            'epsilon': z['nu'] * E0 - z['binding'], 'incident_speed': P}


def _weight_from_delta(z, Delta, kvec):
    delta2 = cba._dot(Delta, Delta)
    if delta2 <= 0:
        raise ValueError('Delta0 excluded from cross-section APIs')
    F = finite_form_factor(z['M'], Delta, kvec)
    W = 4 / z['incident_speed'] * abs(F) ** 2 / delta2 ** 2
    if not math.isfinite(W):
        raise ValueError('unrepresentable invariant weight')
    return W, F


def invariant_weight(E0, M, p_A, p_B):
    """Eq10 kernel weight; shell residual is reported, never silently projected."""
    z = _beam(E0, M)
    p_A, p_B = cba._vector(p_A, 'p_A'), cba._vector(p_B, 'p_B')
    j = shell.to_jacobi(E0, M, p_A, p_B)
    Delta = tuple(z['P'][i] - p_A[i] for i in range(3))
    W, F = _weight_from_delta(z, Delta, j['k'])
    state = shell.shell_state(E0, z['binding'], M, p_A, p_B)
    return {'model': MODEL, 'W': W, 'F': F, 'Delta': Delta, **j,
            'shell_residual': state['F'], 'units': 'a0^2*E_h/p0^6',
            'measure': 'W d^3p_A d^3p_B delta(F_shell)', 'binding': z['binding']}


def jacobi_tdcs(E0, Er, M, n_q, n_k):
    """Eq11: Er is pair-relative energy, not lab electron EB."""
    z = _beam(E0, M)
    Er = cba._real(Er, 'Er')
    if not 0 < Er < z['epsilon']:
        raise ValueError('require open Jacobi channel 0<Er<epsilon')
    nq, nk = shell.normalize_direction(n_q)['unit'], shell.normalize_direction(n_k)['unit']
    q, k = math.sqrt(2 * z['nu'] * (z['epsilon'] - Er)), math.sqrt(2 * z['mu'] * Er)
    qvec, kvec = tuple(q * x for x in nq), tuple(k * x for x in nk)
    Delta = tuple(z['qi'] * x - y for x, y in zip((0., 0., 1.), qvec))
    W, F = _weight_from_delta(z, Delta, kvec)
    lab = shell.from_jacobi(E0, M, qvec, kvec)
    return {**z, **lab, 'q': qvec, 'k': kvec, 'Er': Er, 'Delta': Delta,
            'W': W, 'F': F, 'tdcs_au': z['mu'] * z['nu'] * q * k * W,
            'units': 'a0^2/E_h', 'measure': 'dEr dOmega_k dOmega_q',
            'energy_label': 'Er relative (B,N) pair; not lab EB', 'model': MODEL}


def lab_tdcs(E0, M, p_A, n_B):
    """Eq12; all parent positive roots, unresolved caustic stays density=None."""
    z = _beam(E0, M)
    p_A = cba._vector(p_A, 'p_A')
    if math.hypot(*p_A) == 0:
        return {'model': MODEL, 'status': 'LAB_A_ZERO_ENDPOINT', 'density': None,
                'units': 'a0^2/E_h', 'measure': 'dEA dOmega_A dOmega_B',
                'binding': z['binding'], 'radial': None, 'branches': []}
    Delta = tuple(z['P'][i] - p_A[i] for i in range(3))
    if cba._dot(Delta, Delta) <= 0:
        raise ValueError('Delta0 excluded from cross-section APIs')
    radial = shell.solve_radial(E0, z['binding'], M, p_A, n_B)
    result = {'model': MODEL, 'status': radial['status'], 'density': None,
              'units': 'a0^2/E_h', 'measure': 'dEA dOmega_A dOmega_B',
              'binding': z['binding'], 'radial': radial, 'branches': []}
    if radial['status'] == 'NEAR_CAUSTIC_UNRESOLVED':
        return result
    if not radial['branches']:
        result['density'] = 0.
        return result
    endpoint = False
    for branch in radial['branches']:
        j = shell.to_jacobi(E0, M, p_A, branch['p_B'])
        if math.hypot(*j['k']) == 0:
            endpoint = True
            result['branches'].append({**branch, 'status': 'CONTINUUM_ENDPOINT_EXCLUDED', 'W': None})
            continue
        weight = invariant_weight(E0, M, p_A, branch['p_B'])
        result['branches'].append({**branch, **weight, 'status': 'SIMPLE_POSITIVE_BRANCH',
                                   'density_contribution': radial['p_A_norm'] * branch['radial_weight'] * weight['W']})
    if endpoint:
        result['status'] = 'CONTINUUM_ENDPOINT_EXCLUDED'
    else:
        result['density'] = math.fsum(x['density_contribution'] for x in result['branches'])
    return result
