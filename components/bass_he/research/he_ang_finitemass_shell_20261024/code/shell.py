"""Finite-mass labelled kinematic shell; no amplitude, flux or event cross section.

All APIs use electron atomic units and Cartesian lab momenta. The Jacobi
convention is A spectator / (B,nucleus) pair. Binary64 values are not directed
rounded enclosures. The discriminant guard preserves unresolved caustics.
"""
import itertools
import math
import sys

PROTON_ELECTRON_MASS_RATIO = 1836.152673426
NOMINAL_EV_PER_HARTREE = 27.2


def scalar(value, name, positive=False):
    if isinstance(value, bool):
        raise ValueError(name + ' must be a finite real scalar')
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(name + ' must be a finite real scalar') from exc
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError(name + ' is outside its finite positive domain')
    return value


def vector(value, name):
    try:
        result = tuple(scalar(x, name) for x in value)
    except TypeError as exc:
        raise ValueError(name + ' must have three finite components') from exc
    if len(result) != 3:
        raise ValueError(name + ' must have three finite components')
    return result


def normalize_direction(value):
    v = vector(value, 'direction')
    norm = math.hypot(*v)
    if not math.isfinite(norm) or norm == 0:
        raise ValueError('direction must have a finite nonzero norm')
    return {'unit': tuple(x / norm for x in v), 'input_norm': norm,
            'normalization_applied': norm != 1.0}


def dot(a, b):
    result = math.fsum(x * y for x, y in zip(a, b))
    if not math.isfinite(result):
        raise ValueError('derived dot product is outside binary64 range')
    return result


def parameters(E0, B, M):
    E0, B, M = (scalar(x, n, True) for x, n in ((E0, 'E0'), (B, 'B'), (M, 'M')))
    T = M + 2.0
    if not math.isfinite(T):
        raise ValueError('mass sum is outside binary64 range')
    mu, nu = M / (M + 1.0), (M + 1.0) / T
    P = (0.0, 0.0, math.sqrt(2.0) * math.sqrt(E0))
    epsilon = nu * E0 - B
    return {'E0': E0, 'B': B, 'M': M, 'T': T, 'mu': mu, 'nu': nu,
            'P': P, 'epsilon': epsilon, 'threshold_E0': B / nu}


def _mapping_parameters(E0, M):
    return parameters(E0, 0.5, M)


def to_jacobi(E0, M, p_A, p_B):
    z = _mapping_parameters(E0, M)
    a, b = vector(p_A, 'p_A'), vector(p_B, 'p_B')
    q = tuple(a[i] - z['P'][i] / z['T'] for i in range(3))
    k = tuple(b[i] + (a[i] - z['P'][i]) / (z['M'] + 1) for i in range(3))
    Q = tuple(z['P'][i] - a[i] - b[i] for i in range(3))
    return {'q': q, 'k': k, 'Q': Q, 'component_determinant': 1.0,
            'convention': 'A spectator / (B,nucleus) pair'}


def from_jacobi(E0, M, q, k):
    z = _mapping_parameters(E0, M)
    q, k = vector(q, 'q'), vector(k, 'k')
    a = tuple(q[i] + z['P'][i] / z['T'] for i in range(3))
    b = tuple(k[i] - q[i] / (z['M'] + 1) + z['P'][i] / z['T'] for i in range(3))
    Q = tuple(-k[i] - z['M'] * q[i] / (z['M'] + 1)
              + z['M'] * z['P'][i] / z['T'] for i in range(3))
    return {'p_A': a, 'p_B': b, 'Q': Q}


def shell_state(E0, B, M, p_A, p_B):
    z = parameters(E0, B, M)
    a, b = vector(p_A, 'p_A'), vector(p_B, 'p_B')
    j = to_jacobi(E0, M, a, b)
    EA, EB, ER = dot(a, a) / 2, dot(b, b) / 2, dot(j['Q'], j['Q']) / (2 * z['M'])
    internal = dot(j['k'], j['k']) / (2 * z['mu']) + dot(j['q'], j['q']) / (2 * z['nu'])
    return {**z, **j, 'p_A': a, 'p_B': b, 'EA': EA, 'EB': EB, 'ER': ER,
            'F': math.fsum([z['E0'], -z['B'], -EA, -EB, -ER]),
            'jacobi_internal_energy': internal,
            'energy_identity_residual': math.fsum([EA, EB, ER, -z['E0'] / z['T'], -internal]),
            'global_support': 'EMPTY' if z['epsilon'] < 0 else
                              'COLLAPSED_ZERO_MEASURE' if z['epsilon'] == 0 else 'S5'}


def conditional_sphere(E0, B, M, p_A):
    z = parameters(E0, B, M)
    a = vector(p_A, 'p_A')
    r = tuple(z['P'][i] - a[i] for i in range(3))
    alpha = (z['M'] + 1) / z['M']
    H = math.fsum([z['E0'], -z['B'], -dot(a, a) / 2, -dot(r, r) / (2 * (z['M'] + 1))])
    center = tuple(x / (z['M'] + 1) for x in r)
    radius_squared = 2 * H / alpha
    status = 'EMPTY' if H < 0 else 'COLLAPSED_ZERO_MEASURE' if H == 0 else 'SPHERE'
    radius = math.sqrt(radius_squared) if H > 0 else 0.0 if H == 0 else None
    return {'H': H, 'alpha': alpha, 'center': center, 'radius_squared': radius_squared,
            'radius': radius, 'status': status,
            'conditional_volume': 4 * math.pi * radius / alpha if H > 0 else 0.0}


def solve_coefficients(alpha, beta, gamma):
    """Solve alpha*p²/2-beta*p+gamma=0 without branch removal or root merging."""
    alpha = scalar(alpha, 'alpha', True)
    beta, gamma = scalar(beta, 'beta'), scalar(gamma, 'gamma')
    b2, ag = beta * beta, 2 * alpha * gamma
    D, scale = b2 - ag, b2 + abs(ag)
    if not all(math.isfinite(x) for x in (D, scale)):
        raise ValueError('quadratic discriminant outside binary64 range')
    result = {'alpha': alpha, 'beta': beta, 'gamma': gamma,
              'raw_discriminant': D, 'discriminant_scale': scale,
              'guard_threshold': 64 * sys.float_info.epsilon * scale,
              'algebraic_roots': [], 'positive_roots': [], 'zero_endpoints': [],
              'radial_weight_sum': None, 'sqrt_discriminant': None}
    if abs(D) <= result['guard_threshold']:
        result['status'] = 'NEAR_CAUSTIC_UNRESOLVED'
        result['exact_zero_raw_discriminant'] = D == 0
        return result
    if D < 0:
        result.update(status='NO_REAL_ROOTS', radial_weight_sum=0.0)
        return result
    sqrtD = math.sqrt(D)
    h = beta + math.copysign(sqrtD, beta)
    roots = sorted([h / alpha, 2 * gamma / h])
    if not all(math.isfinite(x) for x in roots):
        raise ValueError('radial roots outside binary64 range')
    positive = [x for x in roots if x > 0]
    result.update(status='SIMPLE_ROOTS' if positive else 'NO_POSITIVE_ROOTS',
                  sqrt_discriminant=sqrtD, algebraic_roots=roots,
                  positive_roots=positive, zero_endpoints=[x for x in roots if x == 0],
                  radial_weight_sum=math.fsum(x * x / sqrtD for x in positive))
    return result


def solve_radial(E0, B, M, p_A, direction):
    z = parameters(E0, B, M)
    a = vector(p_A, 'p_A'); n = normalize_direction(direction)
    r = tuple(z['P'][i] - a[i] for i in range(3))
    alpha, beta = (z['M'] + 1) / z['M'], dot(r, n['unit']) / z['M']
    gamma = math.fsum([dot(a, a) / 2, dot(r, r) / (2 * z['M']), -z['E0'], z['B']])
    result = solve_coefficients(alpha, beta, gamma)
    pA = math.hypot(*a)
    result.update(direction=n, p_A_norm=pA,
                  density_dEA_dOmegaA_dOmegaB=None if result['radial_weight_sum'] is None
                  else pA * result['radial_weight_sum'],
                  measure='labelled d^3pA d^3pB delta(F); no amplitude/flux/count/spin')
    result['branches'] = [{'p': p, 'p_B': tuple(p * v for v in n['unit']),
                           'inverse_radial_derivative': 1 / result['sqrt_discriminant'],
                           'radial_weight': p * p / result['sqrt_discriminant']}
                          for p in result['positive_roots']]
    return result


def phase_space_volume(E0, B, M):
    z = parameters(E0, B, M)
    if z['epsilon'] <= 0:
        return 0.0
    value = 4 * math.pi ** 3 * (z['M'] / z['T']) ** 1.5 * z['epsilon'] ** 2
    if not math.isfinite(value):
        raise ValueError('phase-space volume outside binary64 range')
    return value


def constant_weight_moments(E0, B, M):
    z = parameters(E0, B, M)
    if z['epsilon'] <= 0:
        return {'status': 'NO_NORMALIZED_POSITIVE_SHELL_MEASURE', 'means': None,
                'recoil_energy_variance': None}
    T, M, eps = z['T'], z['M'], z['epsilon']
    P2 = 2 * z['E0']
    eA = P2 / (2 * T * T) + (M + 1) * eps / (2 * T)
    eR = M * P2 / (2 * T * T) + eps / T
    variance = 2 * M * P2 * eps / (3 * T ** 3) + eps ** 2 / (4 * T * T)
    return {'status': 'CONSTANT_WEIGHT_KINEMATIC_FIXTURE_ONLY',
            'means': {'p_A': tuple(x / T for x in z['P']),
                      'p_B': tuple(x / T for x in z['P']),
                      'Q': tuple(M * x / T for x in z['P']),
                      'EA': eA, 'EB': eA, 'ER': eR},
            'recoil_energy_variance': variance,
            'energy_closure': math.fsum([2 * eA, eR, -z['E0'], z['B']])}


def sphere76_nodes():
    """Positive normalized S5 fixture, exact degree<=4; first3=q, last3=k."""
    nodes = []
    for i in range(6):
        for sign in (-1, 1):
            x = [0.0] * 6; x[i] = float(sign)
            nodes.append((tuple(x), 1 / 48))
    for signs in itertools.product((-1, 1), repeat=6):
        nodes.append((tuple(s / math.sqrt(6) for s in signs), 3 / 256))
    return nodes
