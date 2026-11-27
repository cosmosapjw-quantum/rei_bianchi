#!/usr/bin/env python3
"""Focused tests of fresh/cached-parent left-half Peano refinement only."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback

sys.dont_write_bytecode = True
FIRST_SCRIPT_PIN = '1b29d5a81d68df8ae58e2bcc4e41cfb02494bd3af9ba52f4f9de9d9daad10521'
FIRST_RESULTS_PIN = '5014c049c9b900e77dbbd64557cf92872ac7dcf4c7ccdcd589475e461018beb4'
FIRST_RECEIPT_PIN = '7c0aa57ac61774096611ea38255bb68d0f001926475d2482d64e307a42bf6233'
CACHED_RECEIPT_PIN = 'e79571396f3fe09afceb895d0c027f48f256f4c16f756cfebf2f96a2db5ee267'
SELECTED = ('exact_zero_source_off', 'positive_quadratic_forcing', 'negative_quadratic_forcing',
            'centered_cubic_sign_changing_curvature', 'zero_total_opposite_species_defects',
            'zero_L_opacity_defect')
N = 8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def save(path, data):
    with Path(path).open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--e13c9-root', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--candidate-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    source, root9, package, output = [p.resolve() for p in
        (args.source_root, args.e13c9_root, args.package, args.output_dir)]
    base = package / 'tests/MANUFACTURED'
    initial = package / 'evidence/SOURCE_REVISIONS/INITIAL_N32'
    unrefined = package / 'evidence/SOURCE_REVISIONS/SAME_N_UNREFINED'
    candidate = package / 'code/first_midpoint.py'
    output.mkdir(parents=True, exist_ok=False)
    start, cpu_start = time.perf_counter(), time.process_time()
    rows, checks, actual_whole, actual_left, actual_point = [], [], 0, 0, 0
    state = {'schema': 'bass-he-e13c10-left-half-controls-v1',
        'role': 'CONTROL_CONTRIBUTOR_NOT_FINAL_INDEPENDENT_REVIEWER',
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'candidate_sha256': args.candidate_sha256, 'candidate_path': str(candidate),
        'contract_sha256': sha(package / 'SCIENTIFIC_CONTRACT.md'), 'script_sha256': sha(__file__),
        'first_control_source_sha256': FIRST_SCRIPT_PIN, 'first_results_sha256': FIRST_RESULTS_PIN,
        'first_receipt_sha256': FIRST_RECEIPT_PIN, 'cached_receipt_sha256': CACHED_RECEIPT_PIN,
        'case_names': list(SELECTED), 'N_first': N, 'candidate_precision': 60, 'oracle_precision': 140,
        'branches': ['FRESH_PARENT_REFINED', 'CACHED_PARENT_REFINED'],
        'parent_cache_source': 'Actual fresh-parent refined result.cells, same case/N/P/source; no extra setup evaluation.',
        'additional_setup_coefficient_calls': 0, 'unrefined_integrator_invocations': 0,
        'new_midpoint_evaluations': 0, 'captured_coefficient_evaluations': 0,
        'old_control_suite_invocations': 0, 'completed_scientific_work_replays': 0,
        'ODE_solves': 0, 'NCP_launches': 0, 'automatic_retries': 0, 'cpu_seconds_limit': 20,
        'host': platform.node(), 'python': sys.version, 'provider_attestation': 'NOT_ASSERTED',
        'claim_ceiling': 'Manufactured validation of left-half positive Peano enclosure and parent-cache branch; no captured/full-population/physical admission.'}
    save(output / 'START.json', state)

    def check(name, passed, evidence=None):
        checks.append({'check': name, 'pass': bool(passed)})
        if not passed:
            raise AssertionError(json.dumps({'check': name, 'evidence': evidence}, default=str))

    def contains(box, exact):
        return box.lo <= exact.lo <= exact.hi <= box.hi

    def timeout(signum, frame):
        raise TimeoutError('declared 20 CPU-second half-cell control limit reached')

    signal.signal(signal.SIGPROF, timeout)
    signal.setitimer(signal.ITIMER_PROF, 20)
    try:
        check('candidate_identity_before', sha(candidate) == args.candidate_sha256)
        check('unchanged_first_control_source', sha(base / 'run_first_integral_controls.py') == FIRST_SCRIPT_PIN)
        check('unchanged_first_results', sha(base / 'EXEC01/CONTROL_RESULTS.json') == FIRST_RESULTS_PIN)
        check('unchanged_first_receipt', sha(base / 'EXEC01/RECEIPT.json') == FIRST_RECEIPT_PIN)
        check('unchanged_cached_receipt', sha(base / 'EXEC02_CACHED/RECEIPT.json') == CACHED_RECEIPT_PIN)
        first_receipt = json.loads((base / 'EXEC01/RECEIPT.json').read_bytes())
        cached_receipt = json.loads((base / 'EXEC02_CACHED/RECEIPT.json').read_bytes())
        check('preserved_initial_candidate_and_contract', sha(initial / 'code/first_midpoint.py') == first_receipt['candidate_sha256'] and sha(initial / 'SCIENTIFIC_CONTRACT.md') == first_receipt['contract_sha256'])
        check('preserved_unrefined_candidate_and_contract', sha(unrefined / 'code/first_midpoint.py') == cached_receipt['candidate_sha256'] and sha(unrefined / 'SCIENTIFIC_CONTRACT.md') == cached_receipt['contract_sha256'])
        helpers = module('e13c10_first_control_functions_for_half_cells', base / 'run_first_integral_controls.py')
        original_rows = json.loads((base / 'EXEC01/CONTROL_RESULTS.json').read_bytes())['rows']
        by_name = {r['case']['name']: r for r in original_rows if r['N_first'] == N}
        oracle_path = root9 / 'tests/MANUFACTURED/run_manufactured_controls.py'
        check('fixed_independent_oracle_source', sha(oracle_path) == helpers.ORACLE_PIN)
        oracle = module('e13c9_closed_form_for_half_cell_e13c10', oracle_path)
        sys.path.insert(0, str(source / 'code'))
        from off_path_worker import Context
        ctx = Context(source)
        check('original_scientific_source_lock', ctx.source_lock_sha256 == helpers.SOURCE_LOCK_PIN)
        di, pe = ctx.di, ctx.pe
        sys.path.insert(0, str(candidate.parent))
        method = module('e13c10_half_cell_candidate', candidate)

        def iv(q):
            return di.IV(q.numerator) / q.denominator

        class Manufactured:
            def __init__(self, case):
                self.case = case
                for key in ('h', 'f0', 'qf', 'e0'):
                    setattr(self, key, iv(case[key]))
                self.lf = [iv(q) for q in case['lf']]
                self.L = sum(self.lf, di.IV(0))
                self.chi = [iv(q) for q in case['chi']]
                self.mask = [lf > 0 or lf + dl > 0 for lf, dl in zip(case['lf'], case['dl'])]
                self.endpoint_E = self.e0 * (-self.h).exp()
                self.domain = {'manufactured_only': True}
                self.evaluations = self.whole_calls = self.left_calls = self.point_calls = 0

            def __call__(self, x):
                self.evaluations += 1
                if isinstance(x, di.Jet2):
                    span = Q(x.v.hi) - Q(x.v.lo)
                    if span == Q(1, N):
                        self.whole_calls += 1
                    elif span == Q(1, 2 * N):
                        self.left_calls += 1
                    else:
                        raise ArithmeticError('unexpected manufactured derivative cell width')
                    factory = di.Jet2
                else:
                    self.point_calls += 1
                    factory = di.IV
                u = self.h * x
                energy = self.e0 * (-u).exp()
                if 'qpoly' in self.case:
                    dq = factory(0)
                    for p in reversed(self.case['qpoly']):
                        dq = dq * u + iv(p)
                    q = factory(self.qf) + dq
                else:
                    q = factory(iv(self.case['qf'] + self.case['dq']))
                return energy, q, [factory(iv(lf + dl)) for lf, dl in zip(self.case['lf'], self.case['dl'])]

        selected_cases = [case for case in helpers.cases() if case['name'] in SELECTED]
        check('six_declared_cases', len(selected_cases) == 6 and set(c['name'] for c in selected_cases) == set(SELECTED))
        for case in selected_cases:
            serialized_case = {key: [str(v) for v in value] if isinstance(value, list) else str(value) for key, value in case.items()}
            saved = by_name[case['name']]
            check(case['name'] + '/identical_midpoint_case_N', serialized_case == saved['case'] and saved['N_first'] == N)
            target, oracle_gains = helpers.first_oracle(oracle, case), helpers.gain_oracle(oracle, case)
            parent_cache, fresh_signed, fresh_curvature = None, None, None
            for branch in ('FRESH_PARENT_REFINED', 'CACHED_PARENT_REFINED'):
                label = case['name'] + '/' + branch
                di.configure(60)
                coefficients = Manufactured(case)
                cache = {key: pe.iv(value) for key, value in saved['midpoint_candidate'].items()}
                parent_before = None if parent_cache is None else pe.pack(parent_cache)
                result = method.integrate_signed(coefficients, N, cached_midpoint=cache, refine_left=True, cached_parent_curvature=parent_cache)
                actual_whole += coefficients.whole_calls
                actual_left += coefficients.left_calls
                actual_point += coefficients.point_calls
                expected_whole = N if branch == 'FRESH_PARENT_REFINED' else 0
                check(label + '/actual_call_counts', coefficients.whole_calls == expected_whole and coefficients.left_calls == N and coefficients.point_calls == 0 and coefficients.evaluations == expected_whole + N)
                coverage = result['cell_coverage']
                check(label + '/declared_call_counts', coverage['whole_cell_derivative_evaluations'] == expected_whole and coverage['left_half_derivative_evaluations'] == N and coverage['midpoint_evaluations'] == 0 and result['new_coefficient_evaluations'] == expected_whole + N)
                check(label + '/refined_method', result['refine_left'] is True and result['method'] == 'positive_peano_kernel_left_half_refined_v2')
                check(label + '/midpoint_retained', pe.pack(result['midpoint']) == saved['midpoint_candidate'] and pe.pack(cache) == saved['midpoint_candidate'])
                signed = result['signed']
                check(label + '/seventeen_quantities', len(signed) == 17 and set(signed) == set(target))
                for key in sorted(target):
                    check(label + '/independent_oracle/' + key, contains(signed[key], target[key]), {'candidate': signed[key].json(), 'oracle': target[key].json()})
                ledgers = {'number': signed['P1'] + signed['A_total'] - signed['QN'],
                    'energy': signed['P1_energy_eV'] + signed['B_total_eV'] + signed['Z_eV'] - signed['QE_eV']}
                for species, chi in zip(helpers.SPECIES, coefficients.chi):
                    ledgers['heat_' + species] = signed['H_' + species + '_eV'] - signed['B_' + species + '_eV'] + chi * signed['A_' + species]
                for key, value in ledgers.items():
                    check(label + '/ledger/' + key, value.contains(D(0)))
                if case['name'] == 'exact_zero_source_off':
                    check(label + '/exact_zero', all(v.lo == v.hi == 0 for v in signed.values()))
                if case['name'] == 'zero_total_opposite_species_defects':
                    check(label + '/species_cancellation', signed['P1'].lo == signed['P1'].hi == 0 and signed['A_HI'].lo > 0 and signed['A_HeI'].hi < 0)
                if case['name'] in ('positive_quadratic_forcing', 'negative_quadratic_forcing'):
                    correction = result['curvature_correction']['P1']
                    check(label + '/quadratic_curvature_sign', correction.lo > 0 if case['qpoly'][2] > 0 else correction.hi < 0)
                    check(label + '/correct_half_kernel_mass_quadratic', signed['P1'].width() <= D('1e-48') and signed['QN'].width() <= D('1e-48'))
                if case['name'] == 'centered_cubic_sign_changing_curvature':
                    check(label + '/cubic_zero_target', target['P1'].lo == target['P1'].hi == 0)
                _, gains = pe.frozen_outputs_and_gains(coefficients)
                center, eta = iv(case['c']), iv(case['eta'])
                carry = {key: signed[key] + gains[key] * center + pe.symmetric((abs(gains[key]) * eta).hi) for key in signed}
                for error in (-case['eta'], Q(0), case['eta']):
                    for key in sorted(signed):
                        exact = target[key] + oracle_gains[key] * oracle.B(case['c'] + error)
                        check(label + '/incoming_' + str(error) + '/' + key, contains(carry[key], exact))
                if branch == 'FRESH_PARENT_REFINED':
                    parent_cache = [{key: row[key] for key in ('cell', 'x_left', 'x_right', 'second_derivative')} for row in result['cells']]
                    fresh_signed, fresh_curvature = pe.pack(signed), pe.pack(result['curvature_correction'])
                    parent_json = pe.pack(parent_cache)
                    save(output / (case['name'] + '_PARENT_CURVATURE.json'), {'case': serialized_case, 'N_first': N, 'precision': 60,
                         'source_candidate_sha256': args.candidate_sha256, 'source_control_script_sha256': state['script_sha256'],
                         'construction': 'Existing whole-cell fields from this actual fresh-parent refined execution, not an extra setup run.', 'cells': parent_json})
                else:
                    check(label + '/parent_cache_unchanged', pe.pack(parent_cache) == parent_before)
                    check(label + '/fresh_cached_signed_identical', pe.pack(signed) == fresh_signed)
                    check(label + '/fresh_cached_curvature_identical', pe.pack(result['curvature_correction']) == fresh_curvature)
                    check(label + '/parent_cache_origin', result['parent_curvature_origin'] == 'REUSED_IDENTITY_BOUND_WHOLE_CELL_RANGES' and coverage['reused_parent_curvature_cells'] == N)
                rows.append({'case': serialized_case, 'branch': branch, 'N_first': N,
                    'midpoint_cache_sha256': hashlib.sha256(canonical(saved['midpoint_candidate'])).hexdigest(),
                    'signed_candidate': pe.pack(signed), 'signed_oracle': {key: value.json() for key, value in target.items()},
                    'curvature_correction': pe.pack(result['curvature_correction']), 'ledger_enclosures': pe.pack(ledgers),
                    'incoming_candidate': pe.pack(carry), 'cells': pe.pack(result['cells']),
                    'actual_new_whole_cell_calls': coefficients.whole_calls, 'actual_new_left_half_calls': coefficients.left_calls,
                    'actual_new_point_calls': coefficients.point_calls, 'rounding_operation_counts': dict(di.COUNTS)})
        check('candidate_identity_after', sha(candidate) == args.candidate_sha256)
        check('first_results_retained', sha(base / 'EXEC01/CONTROL_RESULTS.json') == FIRST_RESULTS_PIN)
        check('cached_receipt_retained', sha(base / 'EXEC02_CACHED/RECEIPT.json') == CACHED_RECEIPT_PIN)
        signal.setitimer(signal.ITIMER_PROF, 0)
        save(output / 'CONTROL_RESULTS.json', {'schema': state['schema'], 'rows': rows, 'checks': checks})
        receipt = {**state, 'status': 'PASS_HALF_CELL_FRESH_AND_CACHED_PARENT_CONTROLS',
            'executions_completed': len(rows), 'checks_passed': len(checks), 'checks_failed': 0,
            'manufactured_coefficient_evaluations': actual_whole + actual_left + actual_point,
            'new_whole_cell_evaluations': actual_whole, 'new_left_half_evaluations': actual_left,
            'new_midpoint_evaluations': actual_point,
            'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start,
            'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'results_sha256': sha(output / 'CONTROL_RESULTS.json')}
        save(output / 'RECEIPT.json', receipt)
        print(json.dumps({key: receipt[key] for key in ('status', 'executions_completed', 'checks_passed',
            'manufactured_coefficient_evaluations', 'new_whole_cell_evaluations', 'new_left_half_evaluations',
            'new_midpoint_evaluations', 'wall_seconds', 'cpu_seconds', 'results_sha256')}, sort_keys=True), flush=True)
    except BaseException as exc:
        signal.setitimer(signal.ITIMER_PROF, 0)
        save(output / 'PARTIAL_RESULTS.json', {'rows': rows, 'checks': checks})
        failure = {**state, 'status': 'FIRST_FAILURE_PRESERVED_NO_AUTOMATIC_RETRY', 'error_type': type(exc).__name__,
            'error': str(exc), 'traceback': traceback.format_exc(), 'executions_completed': len(rows),
            'actual_new_whole_cell_calls': actual_whole, 'actual_new_left_half_calls': actual_left,
            'actual_new_midpoint_calls': actual_point, 'checks_completed': len(checks),
            'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start}
        save(output / 'FIRST_FAILURE.json', failure)
        print(json.dumps({'status': failure['status'], 'error': str(exc), 'executions_completed': len(rows)}), flush=True)
        raise


if __name__ == '__main__':
    main()
