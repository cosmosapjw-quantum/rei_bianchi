#!/usr/bin/env python3
"""Exact rational photo-energy diagnostic at a frozen archived HH state.

This script does not evolve a state or evaluate a native endpoint, BE solver,
root, IVP, old suite, or native FT03/LCS callback. It takes the stored primary
packet counts as frozen N; these are not a new endpoint's preBE input.

All binary64 input leaves are converted to exact Fraction. Closed-form first
and second x derivatives are compared with an independent formal polynomial
quotient algorithm, without finite differences.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import resource
import time

INPUT_SHA256 = '1f462e7fa7c1d4251c5004194c42b0e471fe5c42303962f1a40d5d5062f1923d'
SOURCE_MANIFEST_SHA256 = '0de85417009cc43814c6db4eb92b77af322726a6d426f0119bad2f37ac153627'
SOURCE_COMMIT = '4b9231a0eff113701e7178ad98624233f387dd15'
SOURCE_FILE_PINS = {
    'candidate/src/atomic_provider.rs': 'b0b572d3940a7a1f740e09d5f43c60236ec61511e8bdbcc68e60395ec7e107d3',
    'candidate/src/phys04_mixed.rs': '283e9127ac8de081186db07aaf5b4437cf0ff01beb4a4b9df25ccb60f369f22f',
    'candidate/src/paired_runtime.rs': '5cfa65e67e4843ae6ae3ae3eb3d1d5a47e23c01db14eaf26feceb4692fe2e4db',
    'candidate/src/hh_paired_extension.rs': '92c90f43e3e30d8531e0b56aa9ae2ac41e1e961c41dfc3db5435ece3e14f3b71',
    'candidate/src/hhe_events.rs': 'c100b08e034089c2d67b2102769ccdd51f1d29a2f388d6bb2dfe7984af93b290',
}
DURATIONS_S = (625000000, 1250000000)


def fraction(value):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('nonfinite input leaf')
        return Q.from_float(value)
    if isinstance(value, int):
        return Q(value)
    raise TypeError('only frozen binary64 or integer leaves are admitted')


def canonical(value):
    return (('-' if value < 0 else '+') + hex(abs(value.numerator))
            + '/' + hex(value.denominator)).encode('ascii')


def display(value):
    with localcontext() as ctx:
        ctx.prec = 50
        return format(Decimal(value.numerator) / Decimal(value.denominator), '.24E')


def exact_record(value):
    record = {'decimal_25_significant_digits': display(value),
              'rational_sha256': hashlib.sha256(canonical(value)).hexdigest(),
              'numerator_bits': abs(value.numerator).bit_length(),
              'denominator_bits': value.denominator.bit_length()}
    if max(record['numerator_bits'], record['denominator_bits']) <= 12000:
        record['exact'] = {'numerator': str(value.numerator), 'denominator': str(value.denominator)}
    else:
        record['exact_storage'] = 'large rational hash; reproducible from frozen input and script'
    return record


def quotient_coefficients(numerator, denominator, degree):
    """Formal power-series long division; inputs are coefficient arrays."""
    if denominator[0] == 0:
        raise ZeroDivisionError('formal denominator constant is zero')
    coefficients = []
    for n in range(degree + 1):
        residual = numerator[n] if n < len(numerator) else Q(0)
        for j in range(1, min(n, len(denominator) - 1) + 1):
            residual -= denominator[j] * coefficients[n - j]
        coefficients.append(residual / denominator[0])
    return coefficients


def exact_rank(matrix):
    rows = [list(row) for row in matrix]
    rank = 0
    for col in range(len(rows[0])):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][col] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for r in range(rank + 1, len(rows)):
            scale = rows[r][col]
            rows[r] = [a - scale * z for a, z in zip(rows[r], rows[rank])]
        rank += 1
    return rank


def run(input_path, source_manifest_path):
    raw = input_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != INPUT_SHA256:
        raise ValueError('archived point input SHA mismatch')
    source_raw = source_manifest_path.read_bytes()
    if hashlib.sha256(source_raw).hexdigest() != SOURCE_MANIFEST_SHA256:
        raise ValueError('source manifest SHA mismatch')
    source_manifest = json.loads(source_raw)
    source_map = {r['relative_path']: r for r in source_manifest['files']}
    for path, digest in SOURCE_FILE_PINS.items():
        if source_map[path]['sha256'] != digest or source_map[path]['commit'] != SOURCE_COMMIT:
            raise ValueError('source pin mismatch: ' + path)
    data = json.loads(raw)
    if data['source_commit'] != SOURCE_COMMIT or len(data['groups']) != 33:
        raise ValueError('input source/grid mismatch')
    x, y1, y2, w = map(fraction, data['gas_point']['values'])
    const = {key: fraction(value) for key, value in data['constants_from_identity_words'].items()}
    c, nh, fhe = const['c_cm_per_s'], fraction(data['point_derived_n_H_cm3']), const['fHe']
    chi_h, chi_i, chi_ii = const['chi_HI_eV'], const['chi_HeI_eV'], const['chi_HeII_eV']
    e_matter = w + chi_h * x + fhe * chi_i * y1 + fhe * (chi_i + chi_ii) * y2
    if not (0 < x < 1 and 0 < y1 and 0 < y2 and y1 + y2 < 1 and w > 0):
        raise ValueError('archived gas point is outside required interior')
    leaves = []
    for row in data['groups']:
        E = fraction(row['energy_eV'])
        N = fraction(row['stored_primary_packet_count_per_H'])
        sigma = list(map(fraction, row['sigma_cm2_python_source_diagnostic']))
        if N < 0 or E <= 0 or any(s < 0 for s in sigma):
            raise ValueError('nonphysical frozen photo input')
        kappa = c * nh * ((1 - x) * sigma[0] + fhe * (1 - y1 - y2) * sigma[1] + fhe * y1 * sigma[2])
        a = [c * nh * (-sigma[0]), c * nh * fhe * (sigma[2] - sigma[1]),
             -c * nh * fhe * sigma[1], Q(0)]
        leaves.append((row['index'], E, N, sigma, kappa, a))
    if any(sigma[1] != 0 or sigma[2] != 0 for _, _, _, sigma, _, _ in leaves):
        raise ValueError('this archived-grid diagnostic requires HeI/HeII sigma=0')
    photon_energy = sum((E * N for _, E, N, _, _, _ in leaves), Q(0))
    per_group_equalities = 0
    aggregate_equalities = 0
    results = []
    for duration in DURATIONS_S:
        d = Q(duration)
        phi = Q(0)
        gradient = [Q(0) for _ in range(4)]
        hessian = [[Q(0) for _ in range(4)] for _ in range(4)]
        oracle_total = [Q(0) for _ in range(3)]
        remaining_photon_energy = Q(0)
        rank1_weight = Q(0)
        exact_evaluation_hash = hashlib.sha256()
        group_summary = []
        for idx, E, N, sigma, kappa, a in leaves:
            den = 1 + d * kappa
            if den <= 0:
                raise ValueError('positive denominator premise absent')
            closed_phi = E * N * kappa / den
            closed_gradient = [E * N * z / den ** 2 for z in a]
            closed_hessian = [[-2 * d * E * N * ai * aj / den ** 3 for aj in a] for ai in a]
            series = quotient_coefficients([E * N * kappa, E * N * a[0]],
                                           [den, d * a[0]], 2)
            expected = [closed_phi, closed_gradient[0], closed_hessian[0][0] / 2]
            for observed, wanted in zip(series, expected):
                if observed != wanted:
                    raise ArithmeticError('formal quotient derivative mismatch')
                per_group_equalities += 1
                exact_evaluation_hash.update(canonical(observed) + b'\n')
            phi += closed_phi
            for i in range(4):
                gradient[i] += closed_gradient[i]
                for j in range(4):
                    hessian[i][j] += closed_hessian[i][j]
            for i in range(3):
                oracle_total[i] += series[i]
            remaining_photon_energy += E * N / den
            rank1_weight += 2 * d * E * N * a[0] ** 2 / den ** 3
            group_summary.append({'index': idx, 'E_eV': display(E), 'N_per_H': display(N),
                                  'kappa_per_s': display(kappa), 'd_kappa': display(d * kappa),
                                  'positive_HI_sigma': sigma[0] > 0,
                                  'contributes_photo_energy': N > 0 and kappa > 0})
        for lhs, rhs in zip(oracle_total, [phi, gradient[0], hessian[0][0] / 2]):
            if lhs != rhs:
                raise ArithmeticError('aggregate quotient derivative mismatch')
            aggregate_equalities += 1
        if d * phi != photon_energy - remaining_photon_energy:
            raise ArithmeticError('frozen reduced matter+photon energy identity failed')
        direction = [Q(1), Q(0), Q(0), Q(0)]
        if any(hessian[i][j] != -rank1_weight * direction[i] * direction[j]
               for i in range(4) for j in range(4)):
            raise ArithmeticError('rank-one curvature factorization failed')
        rank = exact_rank(hessian)
        contributing = [r['index'] for r in group_summary if r['contributes_photo_energy']]
        if not (contributing and phi > 0 and gradient[0] < 0 and hessian[0][0] < 0 and rank == 1):
            raise ArithmeticError('expected archived-photo sign/rank premises failed')
        results.append({
            'diagnostic_duration_s': duration, 'duration_semantics': 'comparison parameter, not elapsed evolution or authorization',
            'phi_eV_per_H_per_s': exact_record(phi),
            'dphi_dx_eV_per_H_per_s': exact_record(gradient[0]),
            'd2phi_dx2_eV_per_H_per_s': exact_record(hessian[0][0]),
            'consumed_energy_dphi_eV_per_H': exact_record(d * phi),
            'remaining_frozen_photon_energy_eV_per_H': exact_record(remaining_photon_energy),
            'gradient_other_coordinates_exact_zero': all(z == 0 for z in gradient[1:]),
            'hessian_coordinate_order': ['x_HII', 'x_HeII', 'x_HeIII', 'e_matter_eV_per_H'],
            'hessian_all_except_xx_exact_zero': all(hessian[i][j] == 0 for i in range(4) for j in range(4) if (i, j) != (0, 0)),
            'hessian_rank': rank, 'negative_semidefinite': True,
            'rank1_factorization': {'formula': 'H=-weight*(1,0,0,0) outer (1,0,0,0)',
                                    'weight_positive': rank1_weight > 0,
                                    'weight_exact_equals_minus_reported_Hxx': rank1_weight == -hessian[0][0]},
            'provider_HI_active_groups': [idx for idx, _, _, sigma, _, _ in leaves if sigma[0] > 0],
            'positive_N_HI_contributing_groups': contributing,
            'frozen_matter_photon_energy_balance_exact': True,
            'group_polynomial_coefficients_sha256': exact_evaluation_hash.hexdigest(),
            'group_rounded_values': group_summary})
    nhe_rounded = float(data['point_derived_n_H_cm3']) * float(data['constants_from_identity_words']['fHe'])
    delta_f = fhe - fraction(nhe_rounded) / nh
    return {
        'schema': 'WU088_HH_PHYS06_ARCHIVED_PHOTO_ENERGY_POINT_V1',
        'status': 'EXACT_RATIONAL_POINT_DIAGNOSTIC_COMPLETE',
        'claim_ceiling': 'Frozen archived stock and gas only; no actual new endpoint, coupled root, uniform tube, finite mixed response or continuous error claim',
        'input_sha256': INPUT_SHA256, 'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
        'source_commit': SOURCE_COMMIT, 'source_file_sha256_pins': SOURCE_FILE_PINS,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_semantics': {'N': 'stored_primary_packet_count_per_H; frozen archived old stock, not next preBE',
                            'nH': 'frozen binary64 source-expression value at archived t0',
                            'sigma': 'frozen Python binary64 transcription of source provider; not new NCP Rust output attestation',
                            'coordinate_e': 'stage.fHe matter energy of existing ledger',
                            'all_floating_point_leaves_lifted_exactly': True,
                            'both_durations_are_comparison_parameters': True},
        'gas_point_exact': [exact_record(z) for z in [x, y1, y2, w]],
        'nH_cm3_exact': exact_record(nh), 'fHe_exact': exact_record(fhe),
        'matter_energy_eV_per_H': exact_record(e_matter),
        'stored_primary_photon_energy_eV_per_H': exact_record(photon_energy),
        'density_leaf_correction': {'delta_f_fstage_minus_f_tilde': exact_record(delta_f),
                                    'nonphoto_energy_identity_needs_delta_f_term': delta_f != 0,
                                    'source_model_renormalized': False},
        'duration_comparisons': results,
        'validation': {'oracle': 'formal polynomial quotient coefficient division through degree2',
                       'finite_differences_used': False, 'per_group_exact_equalities': per_group_equalities,
                       'aggregate_exact_equalities': aggregate_equalities, 'failed_equalities': 0,
                       'same_physical_source_inputs_shared': True,
                       'compiled_callback_independence_claimed': False,
                       'exact_photon_energy_balance_cases': 2, 'exact_rank_factorization_cases': 2},
        'actual_counters': {'native_science_dispatches': 0, 'macros_evolved': 0,
                            'native_endpoint_calls': 0, 'BE_point_solver_calls': 0,
                            'certificate_internal_point_solver_calls': 0, 'root_producer_calls': 0,
                            'receipt_added_endpoint_calls': 0, 'receipt_added_root_calls': 0,
                            'IVP_calls': 0, 'old_science_suite_replays': 0,
                            'native_FT03_LCS_RHS_calls': 0, 'native_Rust_provider_calls': 0,
                            'original_native_decoder_calls': 0},
        'separate_arithmetic_work': {'duration_cases': 2, 'rational_photo_group_evaluations': 66,
                                     'independent_polynomial_divisions': 66},
        'authority': {'native_authorization': None, 'native_budget': 0, 'new_permission_issued': False},
        'resource_contract': {'max_wall_seconds': 30, 'max_address_space_bytes': 256 * 1024 * 1024}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    start = time.monotonic()
    result = run(args.input, args.source_manifest)
    result['execution_measurements'] = {'wall_seconds': time.monotonic() - start,
                                         'max_rss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if result['execution_measurements']['wall_seconds'] > 30:
        raise RuntimeError('diagnostic exceeded bounded wall contract')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'output': str(args.output),
                      'validation': result['validation'], 'measurements': result['execution_measurements'],
                      'matter_energy': result['matter_energy_eV_per_H']['decimal_25_significant_digits'],
                      'durations': [{'d_s': r['diagnostic_duration_s'],
                                     'phi': r['phi_eV_per_H_per_s']['decimal_25_significant_digits'],
                                     'phi_x': r['dphi_dx_eV_per_H_per_s']['decimal_25_significant_digits'],
                                     'phi_xx': r['d2phi_dx2_eV_per_H_per_s']['decimal_25_significant_digits'],
                                     'd_phi': r['consumed_energy_dphi_eV_per_H']['decimal_25_significant_digits'],
                                     'rank': r['hessian_rank'], 'contributing': r['positive_N_HI_contributing_groups']}
                                    for r in result['duration_comparisons']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
