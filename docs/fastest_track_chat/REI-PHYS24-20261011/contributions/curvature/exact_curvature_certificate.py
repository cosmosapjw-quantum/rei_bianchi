#!/usr/bin/env python3
"""PHYS24 exact HeIII-kernel curvature and endpoint-sign certificate.

Standard-library Fraction arithmetic only. Polynomial utility algorithms are
adapted from the frozen PHYS23 helper; no inherited main or proof suite is run.
Source binary64 constants are interpreted as exact real rationals. Serialized
PHYS22 numerical J entries are exact rational *inputs*, without uncertainty
enclosure. All output paths must be fresh.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from math import comb, isqrt
from pathlib import Path
import platform
import sys

EXPECTED_CONTRACT = 'fd60772fa082a651034b21b965133e57cc0c3e37bb14cdab531a5ca3965266e2'
EXPECTED_J = '6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79'
Z_LO, Z_HI = F(49, 50), F(33, 25)
MAX_SUBDIVISION_DEPTH = 8
ENDPOINT_SQRT_SCALE = 10**18


def binary(value):
    return F.from_float(float(value))


def trim(p):
    p = list(map(F, p))
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def add(p, q):
    out = [F(0)] * max(len(p), len(q))
    for i, v in enumerate(p):
        out[i] += v
    for i, v in enumerate(q):
        out[i] += v
    return trim(out)


def scale(p, c):
    return trim([v*c for v in p])


def sub(p, q):
    return add(p, scale(q, -1))


def mul(p, q):
    out = [F(0)] * (len(p)+len(q)-1)
    for i, u in enumerate(p):
        for j, v in enumerate(q):
            out[i+j] += u*v
    return trim(out)


def derivative(p):
    return trim([i*p[i] for i in range(1, len(p))] or [0])


def evaluate(p, x):
    value = F(0)
    for c in reversed(p):
        value = value*x+c
    return value


def affine(p, lo, hi):
    n = len(p)-1
    return trim([
        sum((p[j]*comb(j, i)*lo**(j-i)*(hi-lo)**i
             for j in range(i, n+1)), F(0))
        for i in range(n+1)
    ])


def bernstein(p, lo, hi):
    n = len(p)-1
    power = affine(p, lo, hi)
    power += [F(0)]*(n+1-len(power))
    return [
        sum((power[j]*F(comb(i, j), comb(n, j))
             for j in range(i+1)), F(0))
        for i in range(n+1)
    ]


def bernstein_to_power(coefficients):
    n = len(coefficients)-1
    out = [F(0)]*(n+1)
    for i in range(n+1):
        for j in range(n-i+1):
            out[i+j] += coefficients[i]*comb(n, i)*comb(n-i, j)*(-1)**j
    return trim(out)


def fs(x):
    return str(x.numerator)+'/'+str(x.denominator)


def packed(p):
    return [fs(v) for v in p]


def description(p, lo, hi, desired_sign):
    coefficients = bernstein(p, lo, hi)
    return {
        'interval': [fs(lo), fs(hi)],
        'degree': len(p)-1,
        'desired_strict_sign': desired_sign,
        'bernstein_coefficients_ascending': packed(coefficients),
        'strict_sign_count': sum(desired_sign*v > 0 for v in coefficients),
        'coefficient_count': len(coefficients),
        'all_coefficients_strict_sign': all(desired_sign*v > 0 for v in coefficients),
        'basis_conversion_identity': bernstein_to_power(coefficients) == affine(p, lo, hi),
        'min_bernstein_exact': fs(min(coefficients)),
        'max_bernstein_exact': fs(max(coefficients)),
        'min_bernstein_approx': float(min(coefficients)),
        'max_bernstein_approx': float(max(coefficients)),
    }


def bounded_positive_cover(p):
    """Frozen algorithm: parent attempt first, then at most 8 dyadic levels.

    A failed coefficient sufficient condition is preserved as non-certifying;
    it is not a counterexample to positivity. No tolerance or domain changes.
    """
    attempts, leaves, unresolved = [], [], []
    queue = [(Z_LO, Z_HI, 0)]
    while queue:
        lo, hi, depth = queue.pop(0)
        row = description(p, lo, hi, 1)
        row['depth'] = depth
        row['attempt_index'] = len(attempts)
        attempts.append(row)
        if row['all_coefficients_strict_sign']:
            leaves.append(row['attempt_index'])
        elif depth == MAX_SUBDIVISION_DEPTH:
            unresolved.append(row['attempt_index'])
        else:
            middle = (lo+hi)/2
            queue.extend([(lo, middle, depth+1), (middle, hi, depth+1)])
    leaf_intervals = sorted(
        [(F(attempts[i]['interval'][0]), F(attempts[i]['interval'][1]))
         for i in leaves]
    )
    covers = bool(leaf_intervals) and not unresolved
    covers = covers and leaf_intervals[0][0] == Z_LO and leaf_intervals[-1][1] == Z_HI
    covers = covers and all(a[1] == b[0] for a, b in zip(leaf_intervals, leaf_intervals[1:]))
    return {
        'method': 'Exact Bernstein sufficient-sign certificate, with frozen dyadic fallback',
        'max_subdivision_depth': MAX_SUBDIVISION_DEPTH,
        'attempts': attempts,
        'positive_leaf_attempt_indices': leaves,
        'unresolved_leaf_attempt_indices': unresolved,
        'noncertifying_attempt_count': sum(not a['all_coefficients_strict_sign'] for a in attempts),
        'covers_entire_enclosure': covers,
        'all_basis_conversion_identities': all(a['basis_conversion_identity'] for a in attempts),
    }


def sqrt_bracket(value):
    scaled_square = value*ENDPOINT_SQRT_SCALE**2
    integer = isqrt(scaled_square.numerator//scaled_square.denominator)
    return F(integer, ENDPOINT_SQRT_SCALE), F(integer+1, ENDPOINT_SQRT_SCALE)


def build():
    root = Path(__file__).resolve().parents[2]
    contract_path = root/'PHYSICS_CONTRACT.json'
    input_path = root/'inputs/PHYS22_INITIAL_COEFFICIENTS.json'
    contract_bytes, input_bytes = contract_path.read_bytes(), input_path.read_bytes()
    contract_hash = hashlib.sha256(contract_bytes).hexdigest()
    input_hash = hashlib.sha256(input_bytes).hexdigest()
    contract = json.loads(contract_bytes)
    row = json.loads(input_bytes)['results']['baseline_local']['J_nonphoto'][2]
    checks = []

    def check(name, ok, detail=None):
        checks.append({'id': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

    check('frozen_contract_sha256', contract_hash == EXPECTED_CONTRACT, contract_hash)
    check('frozen_numerical_J_sha256', input_hash == EXPECTED_J, input_hash)
    check('contract_exact_decimal_endpoints', contract['energy_domain']['closed_compact_eV'] == ['13.61', '24.58'])
    if not all(c['status'] == 'PASS' for c in checks):
        raise RuntimeError('Input identity mismatch: no science computation is authorized by this frozen script.')

    ya, fit_p, e0 = binary('32.88'), binary('2.963'), binary('0.4298')
    k = ya*e0
    chi = binary('13.598434599702')
    c_light, nh, xh = binary('29979245800'), binary('1e-4'), binary('0.9')
    kappa = c_light*nh*(1-xh)
    sig0, cm2 = binary('5.475e4'), binary('1e-18')
    jx, jw = F(row[0]), F(row[3])
    eta = chi-jx/jw
    elo, ehi = F('13.61'), F('24.58')
    cut_lo, cut_hi = binary('13.60'), binary('24.59')

    check('positive_fit_and_opacity_constants', all(v > 0 for v in [ya, fit_p, e0, k, kappa, sig0, cm2]))
    check('fixed_numerical_J_signs', jx < 0 < jw)
    check('strictly_positive_z_enclosure', 0 < Z_LO < Z_HI)
    check('compact_energy_domain_enclosed', k*Z_LO**2 < elo < ehi < k*Z_HI**2,
          {'enclosing_energy_eV': [fs(k*Z_LO**2), fs(k*Z_HI**2)]})
    check('compact_energy_domain_inside_smooth_HI_only_band', cut_lo < elo < ehi < cut_hi)
    check('B_C_and_G_strictly_positive', ya*Z_LO**2-1 > 0 and 1+Z_LO > 0)
    check('cross_section_positive_on_certificate_domain', ya*Z_LO**2 > 1 and 1+Z_LO > 0 and sig0 > 0 and cm2 > 0,
          'sigma=sig0*cm2*(X-1)^2*X^(P/2-11/2)*(1+z)^(-P), X=ya*z^2 > 1')

    z, z2 = [F(0), F(1)], [F(0), F(0), F(1)]
    b_poly, c_poly = [-F(1), F(0), ya], [F(1), F(1)]
    g_poly = mul(b_poly, c_poly)
    n_poly = add(add(scale(g_poly, -7), scale(c_poly, 4)), scale(b_poly, fit_p))
    gp, np = derivative(g_poly), derivative(n_poly)
    w_poly = sub(mul(np, g_poly), mul(n_poly, gp))
    a_poly = add(add(mul(n_poly, n_poly), scale(mul(n_poly, g_poly), 6)), mul(z, w_poly))

    def heat_poly(shift):
        return add(
            mul(add(scale(z2, k), [-shift]), a_poly),
            scale(mul(mul(z2, g_poly), add(n_poly, scale(g_poly, 4))), 4*k),
        )

    p_poly = heat_poly(eta)
    check('J_to_shifted_heat_kernel_polynomial_identity',
          scale(p_poly, jw) == add(scale(a_poly, jx), scale(heat_poly(chi), jw)))
    # H=P/(4G^2), DH=z Q/(8G^3), D^2H=z((Q+zQ')G-3zQG')/(16G^4).
    q_poly = sub(mul(derivative(p_poly), g_poly), scale(mul(p_poly, gp), 2))
    v_poly = add(sub(mul(n_poly, n_poly), scale(mul(n_poly, g_poly), 2)), mul(z, w_poly))
    term1 = mul(v_poly, p_poly)
    term2 = scale(mul(mul(z, sub(n_poly, g_poly)), q_poly), 2)
    term3 = mul(z, sub(
        mul(add(q_poly, mul(z, derivative(q_poly))), g_poly),
        scale(mul(mul(z, q_poly), gp), 3),
    ))
    curvature_poly = add(add(term1, term2), term3)
    # Independent expanded route: apply D to sigma*P/G^2 once, then D-1.
    u_poly = add(mul(n_poly, p_poly), mul(z, q_poly))
    curvature_alternative = add(
        mul(sub(n_poly, scale(g_poly, 2)), u_poly),
        mul(z, sub(mul(derivative(u_poly), g_poly), scale(mul(u_poly, gp), 3))),
    )
    check('two_symbolic_curvature_routes_identical', curvature_poly == curvature_alternative)

    curvature = bounded_positive_cover(curvature_poly)
    check('curvature_Bernstein_basis_identity', curvature['all_basis_conversion_identities'])
    check('curvature_strict_positive_coverage', curvature['covers_entire_enclosure'],
          {'attempts': len(curvature['attempts']),
           'positive_leaves': len(curvature['positive_leaf_attempt_indices']),
           'unresolved_leaves': len(curvature['unresolved_leaf_attempt_indices'])})

    endpoints = []
    for label, energy, sign in [('lower', elo, 1), ('upper', ehi, -1)]:
        lo, hi = sqrt_bracket(energy/k)
        exact_enclosure = Z_LO < lo and hi < Z_HI and lo**2 <= energy/k < hi**2
        check(label+'_endpoint_rational_sqrt_enclosure', exact_enclosure)
        endpoint = description(p_poly, lo, hi, sign)
        endpoint.update({'endpoint': label, 'exact_energy_eV': fs(energy),
                         'sqrt_scale': ENDPOINT_SQRT_SCALE,
                         'exact_sqrt_enclosure': exact_enclosure,
                         'kernel_sign': 'positive' if sign == 1 else 'negative'})
        endpoints.append(endpoint)
        check(label+'_endpoint_sign_Bernstein_basis_identity', endpoint['basis_conversion_identity'])
        check(label+'_endpoint_strict_kernel_sign', endpoint['all_coefficients_strict_sign'])

    pass_count = sum(c['status'] == 'PASS' for c in checks)
    successful = pass_count == len(checks)
    return {
        'task': 'REI-PHYS24-20261011',
        'kind': 'exact_rational_Bernstein_HeIII_kernel_curvature_certificate',
        'evidence_status': ['derived', 'implementation-verified'],
        'status': 'PASS' if successful else 'FAIL',
        'contract_sha256': contract_hash,
        'numerical_J_input_sha256': input_hash,
        'arithmetic': 'fractions.Fraction; binary64 source literals as exact reals; serialized numerical J decimals as exact rationals',
        'python': platform.python_version(),
        'python_requirement': '>=3.10; standard library only',
        'constants': {
            name: {'exact': fs(value), 'approx': float(value)}
            for name, value in [
                ('E0_eV', e0), ('ya', ya), ('fit_P', fit_p), ('k_E0_ya_eV', k),
                ('chi_HI_eV', chi), ('kappa_cm-2_s-1', kappa),
                ('J_h2_x_s-1', jx), ('J_h2_w_s-1_eV-1', jw), ('eta_eV', eta),
            ]
        },
        'domain': {
            'energy_eV_closed': [fs(elo), fs(ehi)],
            'certificate_z_closed': [fs(Z_LO), fs(Z_HI)],
            'z_definition': 'sqrt(E/(E0*ya))',
            'enclosing_energy_eV_closed': [fs(k*Z_LO**2), fs(k*Z_HI**2)],
            'note': 'The smooth algebraic HI fit is extended across the rational z enclosure only for polynomial sign certification; the physical conclusion is restricted to I within the HI-only band.',
        },
        'definitions': {
            'D': 'E d/dE = z/2 d/dz',
            'B': 'ya*z^2-1', 'C': '1+z', 'G': 'B*C',
            'N': '-7*G+4*C+P*B',
            'alpha': 'D log(sigma)=N/(2*G)',
            'W': 'N_prime*G-N*G_prime',
            'beta': 'D alpha=z*W/(4*G^2)',
            'PA': 'N^2+6*N*G+z*W',
            'A': 'alpha^2+3*alpha+beta=PA/(4*G^2)',
            'eta': 'chi-Jx/Jw',
            'P_eta': '(k*z^2-eta)*PA+4*k*z^2*G*(N+4*G)',
            'H_eta': '(E-eta)*A+E*(2*alpha+4)=P_eta/(4*G^2)',
            'g': 'kappa*sigma*Jw*H_eta/4=kappa*sigma*Jw*P_eta/(16*G^2)',
            'Q': 'P_eta_prime*G-2*P_eta*G_prime',
            'V': 'N^2-2*N*G+z*W',
            'R': 'V*P_eta+2*z*(N-G)*Q+z*((Q+z*Q_prime)*G-3*z*Q*G_prime)',
            'U': 'N*P_eta+z*Q',
            'R_alternative': '(N-2*G)*U+z*(U_prime*G-3*U*G_prime)',
            'g_second_derivative': 'kappa*sigma*Jw*R/(64*E^2*G^4)',
            'bernstein': 'p(L+(U-L)t)=sum b_j binom(n,j)t^j(1-t)^(n-j), 0<=t<=1',
        },
        'units': {
            'g': 's^-2', 'g_second_derivative': 's^-2 eV^-2',
            'P_eta_Q_R_U': 'eV', 'G_N_W_PA_V': 'dimensionless',
            'normalization': 'a4=(q*N0/45)*integral g dP; positive fixed factor preserves curvature and signs',
        },
        'polynomials': {
            name: {'degree': len(poly)-1, 'power_coefficients_ascending': packed(poly)}
            for name, poly in [
                ('G', g_poly), ('N', n_poly), ('PA', a_poly), ('P_eta', p_poly),
                ('Q', q_poly), ('V', v_poly), ('U', u_poly), ('R_curvature', curvature_poly),
            ]
        },
        'curvature_certificate': curvature,
        'endpoint_sign_certificates': endpoints,
        'certified_conclusions': {
            'g_second_derivative_strictly_positive_on_I': successful,
            'g_strictly_convex_on_I': successful,
            'g_lower_endpoint_strictly_positive': endpoints[0]['all_coefficients_strict_sign'],
            'g_upper_endpoint_strictly_negative': endpoints[1]['all_coefficients_strict_sign'],
            'g_unique_zero_in_open_I': successful,
            'scope': 'Exact continuum theorem conditional on the fixed serialized numerical J inputs; no uncertainty propagation for J.',
        },
        'checks': checks,
        'check_count': len(checks),
        'pass_count': pass_count,
        'execution_counters': {
            'old_main_invocations': 0, 'closed_proof_suite_replays': 0,
            'native_runs': 0, 'gas_IVP_runs': 0, 'large_campaigns': 0,
        },
        'scope_limits': [
            'Initial-time epsilon^2 t^4 coefficient only.',
            'Mathematical exactness is conditional on the serialized numerical J, not its physical or numerical uncertainty.',
            'Not a proof-assistant kernel certificate; exact rational implementation and explicit algebra are inspectable.',
            'No native floating-point execution equivalence.',
            'No finite-time or finite-epsilon remainder, source admission, or physical promotion.',
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing to overwrite existing evidence; choose a fresh output path.')
    data = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    cc = data['curvature_certificate']
    print(json.dumps({
        'status': data['status'], 'passed': data['pass_count'], 'checks': data['check_count'],
        'curvature_degree': data['polynomials']['R_curvature']['degree'],
        'curvature_attempt_count': len(cc['attempts']),
        'noncertifying_attempt_count': cc['noncertifying_attempt_count'],
        'positive_leaf_count': len(cc['positive_leaf_attempt_indices']),
        'curvature_strict_sign_counts': [
            [a['strict_sign_count'], a['coefficient_count']] for a in cc['attempts']
        ],
        'endpoint_sign_counts': [
            [a['kernel_sign'], a['strict_sign_count'], a['coefficient_count']]
            for a in data['endpoint_sign_certificates']
        ],
        'conclusions': data['certified_conclusions'],
    }, ensure_ascii=False))
    return 0 if data['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
