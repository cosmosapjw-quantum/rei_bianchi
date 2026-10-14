#!/usr/bin/env python3
"""PHYS25 conditional exact sign of the HeIII kernel third derivative.

This new-scope program reads fixed inputs and uses Fraction polynomial algebra.
It does not import or invoke any PHYS19--24 scientific program. Polynomial basis
utilities are explicitly adapted from the inherited PHYS24 source. The sign is
not assumed: both strict signs are tested, and all noncertifying attempts remain
in the result. Physical uncertainty of the serialized numerical J is excluded.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from math import comb
from pathlib import Path
import platform
import sys

EXPECTED_CONTRACT = '7fce1d8729a22b89b00d8116d237af3ddcddc0951901eaa46ba821d9ed07b1c3'
EXPECTED_J = '6c7a4f239ef48c2a7c60592fc048600317f1233f3028434ebd1b3c7e55682a79'
EXPECTED_ATOMIC_SOURCE = 'b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3'
Z_LO, Z_HI = F(49, 50), F(33, 25)
MAX_SUBDIVISION_DEPTH = 8


def binary(value):
    return F.from_float(float(value))


def trim(p):
    p = list(map(F, p))
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def add(p, q):
    out = [F(0)] * max(len(p), len(q))
    for i, value in enumerate(p):
        out[i] += value
    for i, value in enumerate(q):
        out[i] += value
    return trim(out)


def scale(p, factor):
    return trim([factor * value for value in p])


def sub(p, q):
    return add(p, scale(q, -1))


def mul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, first in enumerate(p):
        for j, second in enumerate(q):
            out[i+j] += first * second
    return trim(out)


def derivative(p):
    return trim([i*p[i] for i in range(1, len(p))] or [0])


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


def fs(value):
    return str(value.numerator)+'/'+str(value.denominator)


def packed(poly):
    return [fs(value) for value in poly]


def description(poly, lo, hi):
    coefficients = bernstein(poly, lo, hi)
    sign = (1 if all(value > 0 for value in coefficients) else
            -1 if all(value < 0 for value in coefficients) else 0)
    return {
        'interval': [fs(lo), fs(hi)],
        'degree': len(poly)-1,
        'bernstein_coefficients_ascending': packed(coefficients),
        'positive_coefficient_count': sum(value > 0 for value in coefficients),
        'negative_coefficient_count': sum(value < 0 for value in coefficients),
        'zero_coefficient_count': sum(value == 0 for value in coefficients),
        'coefficient_count': len(coefficients),
        'certified_strict_sign': sign,
        'basis_conversion_identity': bernstein_to_power(coefficients) == affine(poly, lo, hi),
        'min_bernstein_exact': fs(min(coefficients)),
        'max_bernstein_exact': fs(max(coefficients)),
        'min_bernstein_approx': float(min(coefficients)),
        'max_bernstein_approx': float(max(coefficients)),
    }


def signed_cover(poly):
    """Try both signs without a supplied expectation, preserving every attempt."""
    queue = [(Z_LO, Z_HI, 0)]
    attempts, leaves, unresolved = [], [], []
    while queue:
        lo, hi, depth = queue.pop(0)
        row = description(poly, lo, hi)
        row.update({'depth': depth, 'attempt_index': len(attempts)})
        attempts.append(row)
        if row['certified_strict_sign'] != 0:
            leaves.append(row['attempt_index'])
        elif depth == MAX_SUBDIVISION_DEPTH:
            unresolved.append(row['attempt_index'])
        else:
            midpoint = (lo+hi)/2
            queue.extend([(lo, midpoint, depth+1), (midpoint, hi, depth+1)])
    intervals = sorted((F(attempts[i]['interval'][0]), F(attempts[i]['interval'][1]))
                       for i in leaves)
    covers = bool(intervals) and not unresolved
    covers = covers and intervals[0][0] == Z_LO and intervals[-1][1] == Z_HI
    covers = covers and all(first[1] == second[0]
                            for first, second in zip(intervals, intervals[1:]))
    signs = {attempts[i]['certified_strict_sign'] for i in leaves}
    uniform_sign = next(iter(signs)) if covers and len(signs) == 1 else 0
    return {
        'method': 'Exact signed Bernstein sufficient condition, then bounded dyadic fallback',
        'sign_expectation_supplied': False,
        'max_subdivision_depth': MAX_SUBDIVISION_DEPTH,
        'attempts': attempts,
        'strict_sign_leaf_attempt_indices': leaves,
        'unresolved_leaf_attempt_indices': unresolved,
        'noncertifying_attempt_count': sum(row['certified_strict_sign'] == 0 for row in attempts),
        'actual_subdivision_count': sum(row['certified_strict_sign'] == 0 and
                                        row['depth'] < MAX_SUBDIVISION_DEPTH for row in attempts),
        'covers_entire_enclosure': covers,
        'certified_uniform_strict_sign': uniform_sign,
        'all_basis_conversion_identities': all(row['basis_conversion_identity'] for row in attempts),
    }


def build():
    root = Path(__file__).resolve().parents[2]
    paths = {
        'contract': root/'PHYSICS_CONTRACT.json',
        'numerical_J': root/'inputs/PHYS22_INITIAL_COEFFICIENTS.json',
        'atomic_source': root/'inputs/pinned_source/rust/rei_microphysics/src/atomic_provider.rs',
    }
    data = {name: path.read_bytes() for name, path in paths.items()}
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in data.items()}
    contract = json.loads(data['contract'])
    row = json.loads(data['numerical_J'])['results']['baseline_local']['J_nonphoto'][2]
    checks = []

    def check(name, ok, detail=None):
        checks.append({'id': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

    check('frozen_contract_sha256', hashes['contract'] == EXPECTED_CONTRACT, hashes['contract'])
    check('frozen_numerical_J_sha256', hashes['numerical_J'] == EXPECTED_J, hashes['numerical_J'])
    check('frozen_atomic_source_sha256', hashes['atomic_source'] == EXPECTED_ATOMIC_SOURCE,
          hashes['atomic_source'])
    check('contract_exact_decimal_domain',
          contract['energy_domain']['closed_compact_eV'] == ['13.61', '24.58'])
    if not all(item['status'] == 'PASS' for item in checks):
        raise RuntimeError('Frozen input mismatch; stop before scientific computation.')

    ya, fit_p, e0 = binary('32.88'), binary('2.963'), binary('0.4298')
    energy_scale = e0*ya
    chi = binary('13.598434599702')
    c_light, nh, xh = binary('29979245800'), binary('1e-4'), binary('0.9')
    kappa = c_light*nh*(1-xh)
    sigma0, cm2 = binary('5.475e4'), binary('1e-18')
    jx, jw = F(row[0]), F(row[3])
    eta = chi-jx/jw
    elo, ehi = F('13.61'), F('24.58')
    cut_lo, cut_hi = binary('13.60'), binary('24.59')
    photon_number = binary('0.05')
    shear_exact_real = (binary('1.01e-14')-binary('0.99e-14'))/2
    q = 2*shear_exact_real**2

    check('positive_fit_and_opacity_prefactors',
          all(value > 0 for value in [ya, fit_p, e0, energy_scale, kappa, sigma0, cm2]))
    check('serialized_J_signs', jx < 0 < jw)
    check('positive_fixed_response_normalization', photon_number > 0 and q > 0)
    check('strict_positive_rational_z_enclosure', 0 < Z_LO < Z_HI)
    check('energy_domain_enclosed', energy_scale*Z_LO**2 < elo < ehi < energy_scale*Z_HI**2,
          {'enclosing_energy_eV': [fs(energy_scale*Z_LO**2), fs(energy_scale*Z_HI**2)]})
    check('physical_domain_inside_smooth_HI_only_band', cut_lo < elo < ehi < cut_hi)
    check('positive_B_C_G_on_enclosure', ya*Z_LO**2-1 > 0 and 1+Z_LO > 0)
    check('positive_cross_section_on_enclosure', ya*Z_LO**2 > 1 and sigma0*cm2 > 0,
          'The algebraic HI fit has positive base factors; conclusion restricted to physical I.')

    z, z2 = [F(0), F(1)], [F(0), F(0), F(1)]
    bpoly, cpoly = [-F(1), F(0), ya], [F(1), F(1)]
    gpoly = mul(bpoly, cpoly)
    n = add(add(scale(gpoly, -7), scale(cpoly, 4)), scale(bpoly, fit_p))
    gp = derivative(gpoly)
    w = sub(mul(derivative(n), gpoly), mul(n, gp))
    pa = add(add(mul(n, n), scale(mul(n, gpoly), 6)), mul(z, w))
    p_eta = add(
        mul(add(scale(z2, energy_scale), [-eta]), pa),
        scale(mul(mul(z2, gpoly), add(n, scale(gpoly, 4))), 4*energy_scale),
    )

    # Route A: explicitly differentiate the curvature representation once.
    qp = sub(mul(derivative(p_eta), gpoly), scale(mul(p_eta, gp), 2))
    vp = add(sub(mul(n, n), scale(mul(n, gpoly), 2)), mul(z, w))
    rp = add(
        add(mul(vp, p_eta), scale(mul(mul(z, sub(n, gpoly)), qp), 2)),
        mul(z, sub(mul(add(qp, mul(z, derivative(qp))), gpoly),
                   scale(mul(mul(z, qp), gp), 3))),
    )
    tp = add(mul(sub(n, scale(gpoly, 4)), rp),
             mul(z, sub(mul(derivative(rp), gpoly), scale(mul(rp, gp), 4))))

    # Route B: act directly on sigma(E)*(E-eta) with all five log operators.
    # (D+s)[sigma*A/G^d] = sigma*L_s(A,d)/(2*G^(d+1)).
    def shifted_log_numerator(poly, denominator_power, shift):
        return add(
            mul(add(n, scale(gpoly, 2*shift)), poly),
            mul(z, sub(mul(derivative(poly), gpoly),
                       scale(mul(poly, gp), denominator_power))),
        )

    direct = add(scale(z2, energy_scale), [-eta])
    operator_stages = []
    for denominator_power, shift in enumerate([3, 0, 0, -1, -2]):
        direct = shifted_log_numerator(direct, denominator_power, shift)
        operator_stages.append(direct)
    check('original_fit_D_Dplus3_matches_shifted_kernel', operator_stages[1] == p_eta)
    check('third_derivative_two_algebraic_routes_identical', direct == tp)
    check('expected_third_derivative_polynomial_degree', len(tp)-1 == 17, len(tp)-1)

    certificate = signed_cover(tp)
    check('Bernstein_power_basis_inverse_identity', certificate['all_basis_conversion_identities'])
    check('continuum_uniform_strict_sign_certificate',
          certificate['covers_entire_enclosure'] and
          certificate['certified_uniform_strict_sign'] in [-1, 1],
          {'certified_uniform_strict_sign': certificate['certified_uniform_strict_sign'],
           'attempt_count': len(certificate['attempts']),
           'unresolved_leaf_count': len(certificate['unresolved_leaf_attempt_indices'])})
    passed = sum(item['status'] == 'PASS' for item in checks)
    successful = passed == len(checks)
    sign = certificate['certified_uniform_strict_sign'] if successful else 0
    return {
        'task': 'REI-PHYS25-20261011',
        'kind': 'exact_rational_Bernstein_HeIII_kernel_third_derivative_certificate',
        'evidence_status': ['derived', 'implementation-verified'],
        'status': 'PASS' if successful else 'NOT_CERTIFIED',
        'input_identity_sha256': hashes,
        'arithmetic': 'fractions.Fraction; binary64 source literals as exact real rationals; serialized numerical J decimals as exact rational inputs',
        'python': platform.python_version(),
        'python_requirement': '>=3.10; standard library only',
        'constants': {
            name: {'exact': fs(value), 'approx': float(value)}
            for name, value in [
                ('E0_eV', e0), ('ya', ya), ('fit_P', fit_p),
                ('energy_scale_E0_ya_eV', energy_scale), ('chi_HI_eV', chi),
                ('kappa_cm-2_s-1', kappa), ('J_h2_x_s-1', jx),
                ('J_h2_w_s-1_eV-1', jw), ('eta_eV', eta),
                ('N0_photon_per_H', photon_number), ('q_s-2', q),
            ]
        },
        'domain': {
            'energy_eV_closed': [fs(elo), fs(ehi)],
            'certificate_z_closed': [fs(Z_LO), fs(Z_HI)],
            'z_definition': 'sqrt(E/(E0*ya))',
            'smooth_extension_note': 'The rational z certificate uses only the algebraic smooth HI fit; physical conclusion is restricted to I inside the HI-only band.',
        },
        'definitions': {
            'D': 'E d/dE = z/2 d/dz; gas state fixed',
            'B': 'ya*z^2-1', 'C': '1+z', 'G': 'B*C',
            'N': '-7*G+4*C+fit_P*B',
            'alpha': 'D log(sigma)=N/(2*G)',
            'W': 'N_prime*G-N*G_prime',
            'PA': 'N^2+6*N*G+z*W',
            'eta': 'chi-Jx/Jw',
            'P_eta': '(energy_scale*z^2-eta)*PA+4*energy_scale*z^2*G*(N+4*G)',
            'g': 'kappa*sigma*Jw*P_eta/(16*G^2)',
            'Q': 'P_eta_prime*G-2*P_eta*G_prime',
            'V': 'N^2-2*N*G+z*W',
            'R': 'V*P_eta+2*z*(N-G)*Q+z*((Q+z*Q_prime)*G-3*z*Q*G_prime)',
            'g_second': 'kappa*sigma*Jw*R/(64*E^2*G^4); intermediate only, no old sign suite replay',
            'T': '(N-4*G)*R+z*(R_prime*G-4*R*G_prime)',
            'g_third': 'kappa*sigma*Jw*T/(128*E^3*G^5)',
            'k_third': '(q*N0/45)*g_third; no duplicate normalization in k',
            'direct_operator_identity': 'E^3*d^3/dE^3 = D*(D-1)*(D-2)',
            'L_shift': '(N+2*shift*G)*A+z*(A_prime*G-denominator_power*A*G_prime)',
            'direct_route': 'Start A=energy_scale*z^2-eta. Apply L shifts [3,0,0,-1,-2], denominator powers [0,1,2,3,4]; result equals T.',
            'Bernstein': 'T(L+(U-L)t)=sum b_j binom(n,j)t^j(1-t)^(n-j), 0<=t<=1',
        },
        'units': {
            'g': 's^-2', 'g_third': 's^-2 eV^-3',
            'k': 's^-4', 'k_third': 's^-4 eV^-3',
            'P_eta_Q_R_T': 'eV', 'G_N_W_PA_V': 'dimensionless',
            'normalization': 'Fixed q*N0/45 > 0, so g and k derivative signs agree.',
        },
        'polynomials': {
            name: {'degree': len(poly)-1, 'power_coefficients_ascending': packed(poly)}
            for name, poly in [('G', gpoly), ('N', n), ('PA', pa), ('P_eta', p_eta),
                               ('Q', qp), ('V', vp), ('R_intermediate', rp), ('T_third', tp)]
        },
        'third_derivative_certificate': certificate,
        'certified_conclusions': {
            'g_third_derivative_uniform_strict_sign_on_I': sign,
            'k_third_derivative_uniform_strict_sign_on_I': sign,
            'k_second_derivative_strictly_decreasing_on_I': sign == -1,
            'k_second_derivative_strictly_increasing_on_I': sign == 1,
            'scope': 'Exact continuum theorem conditional on fixed serialized numerical J; no J uncertainty enclosure.',
        },
        'checks': checks,
        'check_count': len(checks),
        'pass_count': passed,
        'execution_counters': {
            'old_main_invocations': 0, 'closed_proof_suite_replays': 0,
            'native_runs': 0, 'gas_IVP_runs': 0, 'large_campaigns': 0,
            'root_searches': 0, 'grid_optimizations': 0,
        },
        'scope_limits': [
            'Initial epsilon^2 t^4 coefficient only.',
            'Exact-real source semantics; not native floating-point execution equivalence.',
            'Serialized numerical J uncertainty is not enclosed.',
            'Exact rational implementation, not a proof-assistant kernel certificate.',
            'No finite-time or finite-epsilon remainder, source admission, or physical promotion.',
            'This derivative contribution does not certify variance optimality by itself.',
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Refusing to overwrite existing evidence; choose a fresh output path.')
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    certificate = result['third_derivative_certificate']
    print(json.dumps({
        'status': result['status'], 'passed': result['pass_count'], 'checks': result['check_count'],
        'third_derivative_degree': result['polynomials']['T_third']['degree'],
        'attempt_count': len(certificate['attempts']),
        'noncertifying_attempt_count': certificate['noncertifying_attempt_count'],
        'actual_subdivision_count': certificate['actual_subdivision_count'],
        'coefficient_sign_counts': [
            [row['positive_coefficient_count'], row['negative_coefficient_count'], row['coefficient_count']]
            for row in certificate['attempts']
        ],
        'conclusions': result['certified_conclusions'],
    }, ensure_ascii=False))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
