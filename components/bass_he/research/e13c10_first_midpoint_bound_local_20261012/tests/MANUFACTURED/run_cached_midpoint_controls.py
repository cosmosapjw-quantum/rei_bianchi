#!/usr/bin/env python3
"""Narrow E13C10 cached-midpoint branch control; never rerun uncached work."""
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
CONTROL_SOURCE_PIN = '1b29d5a81d68df8ae58e2bcc4e41cfb02494bd3af9ba52f4f9de9d9daad10521'
OLD_RESULTS_PIN = '5014c049c9b900e77dbbd64557cf92872ac7dcf4c7ccdcd589475e461018beb4'
OLD_RECEIPT_PIN = '7c0aa57ac61774096611ea38255bb68d0f001926475d2482d64e307a42bf6233'
OLD_CANDIDATE_PIN = '29203c91e01b7a439cd56b620b603fbe8bf843b2fdeef00c5e2c4f98bd5f6e09'
N = 8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--e13c9-root', type=Path, required=True)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--candidate-sha256', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    source, root9, package, output = [path.resolve() for path in
        (args.source_root, args.e13c9_root, args.package, args.output_dir)]
    candidate = package / 'code/first_midpoint.py'
    contract = package / 'SCIENTIFIC_CONTRACT.md'
    prior = package / 'tests/MANUFACTURED/EXEC01'
    control_source = prior.parent / 'run_first_integral_controls.py'
    original = package / 'evidence/SOURCE_REVISIONS/INITIAL_N32'
    output.mkdir(parents=True, exist_ok=False)
    start, cpu_start = time.perf_counter(), time.process_time()
    rows, checks, coefficient_calls = [], [], 0
    state = {'schema': 'bass-he-e13c10-cached-midpoint-controls-v1',
        'role': 'CONTROL_CONTRIBUTOR_NOT_FINAL_INDEPENDENT_REVIEWER',
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'candidate_sha256': args.candidate_sha256, 'candidate_path': str(candidate),
        'contract_sha256': sha(contract), 'script_sha256': sha(__file__),
        'fixed_first_control_source_sha256': CONTROL_SOURCE_PIN,
        'fixed_original_control_results_sha256': OLD_RESULTS_PIN,
        'fixed_original_control_receipt_sha256': OLD_RECEIPT_PIN,
        'fixed_original_candidate_sha256': OLD_CANDIDATE_PIN,
        'N_first': N, 'candidate_precision': 60, 'oracle_precision': 140,
        'cached_branch_only': True, 'new_midpoint_evaluations': 0,
        'captured_coefficient_evaluations': 0, 'uncached_first_integral_invocations': 0,
        'old_control_suite_invocations': 0, 'completed_scientific_work_replays': 0,
        'ODE_solves': 0, 'NCP_launches': 0, 'automatic_retries': 0,
        'cpu_seconds_limit': 20, 'host': platform.node(), 'python': sys.version,
        'provider_attestation': 'NOT_ASSERTED',
        'purpose': 'Validate only the new cached aggregate branch against saved identical-input midpoint bytes and independent closed-form targets; the original uncached suite is not rerun.',
        'claim_ceiling': 'Manufactured cache branch only; actual captured cache provenance and stitched-path admission require independent path evidence.'}
    save(output / 'START.json', state)

    def check(name, value, evidence=None):
        checks.append({'check': name, 'pass': bool(value)})
        if not value:
            raise AssertionError(json.dumps({'check': name, 'evidence': evidence}, default=str))

    def contained(box, target):
        return box.lo <= target.lo <= target.hi <= box.hi

    def timeout(signum, frame):
        raise TimeoutError('declared 20 CPU-second cached-branch control budget reached')

    signal.signal(signal.SIGPROF, timeout)
    signal.setitimer(signal.ITIMER_PROF, 20)
    try:
        check('new_candidate_identity_before', sha(candidate) == args.candidate_sha256)
        check('original_control_source_identity', sha(control_source) == CONTROL_SOURCE_PIN)
        check('saved_original_results_identity', sha(prior / 'CONTROL_RESULTS.json') == OLD_RESULTS_PIN)
        check('saved_original_receipt_identity', sha(prior / 'RECEIPT.json') == OLD_RECEIPT_PIN)
        old_receipt = json.loads((prior / 'RECEIPT.json').read_bytes())
        check('saved_original_candidate_identity', sha(original / 'code/first_midpoint.py') == old_receipt['candidate_sha256'] == OLD_CANDIDATE_PIN)
        check('saved_original_contract_identity', sha(original / 'SCIENTIFIC_CONTRACT.md') == old_receipt['contract_sha256'])
        check('saved_original_receipt_success_and_precision', old_receipt['status'] == 'PASS_MANUFACTURED_FIRST_INTEGRAL_CONTROLS' and old_receipt['candidate_precision'] == 60 and old_receipt['oracle_precision'] == 140)
        original_rows = json.loads((prior / 'CONTROL_RESULTS.json').read_bytes())['rows']
        by_name = {row['case']['name']: row for row in original_rows if row['N_first'] == N}
        helpers = module('e13c10_original_control_functions_only', control_source)
        check('all_twelve_unique_same_N_rows', len(by_name) == 12 == len([r for r in original_rows if r['N_first'] == N]))
        oracle_path = root9 / 'tests/MANUFACTURED/run_manufactured_controls.py'
        check('fixed_closed_form_oracle', sha(oracle_path) == helpers.ORACLE_PIN)
        oracle = module('e13c9_closed_form_for_cached_e13c10', oracle_path)
        sys.path.insert(0, str(source / 'code'))
        from off_path_worker import Context
        ctx = Context(source)
        check('original_source_lock_identity', ctx.source_lock_sha256 == helpers.SOURCE_LOCK_PIN)
        di, pe = ctx.di, ctx.pe
        sys.path.insert(0, str(candidate.parent))
        method = module('e13c10_cached_midpoint_under_control', candidate)

        def iv(q):
            return di.IV(q.numerator) / q.denominator

        class ManufacturedCoefficients:
            def __init__(self, case):
                self.case = case
                for key in ('h', 'f0', 'qf', 'e0'):
                    setattr(self, key, iv(case[key]))
                self.lf = [iv(q) for q in case['lf']]
                self.L = sum(self.lf, di.IV(0))
                self.chi = [iv(q) for q in case['chi']]
                self.mask = [lf > 0 or lf + dl > 0 for lf, dl in zip(case['lf'], case['dl'])]
                self.endpoint_E = self.e0 * (-self.h).exp()
                self.evaluations = self.whole_cell_calls = self.point_calls = 0
                self.domain = {'manufactured_only': True}

            def __call__(self, x):
                self.evaluations += 1
                if isinstance(x, di.Jet2):
                    self.whole_cell_calls += 1
                    factory = di.Jet2
                else:
                    self.point_calls += 1
                    factory = di.IV
                u = self.h * x
                energy = self.e0 * (-u).exp()
                if 'qpoly' in self.case:
                    dq = factory(0)
                    for term in reversed(self.case['qpoly']):
                        dq = dq * u + iv(term)
                    source_value = factory(self.qf) + dq
                else:
                    source_value = factory(iv(self.case['qf'] + self.case['dq']))
                return energy, source_value, [factory(iv(lf + dl)) for lf, dl in zip(self.case['lf'], self.case['dl'])]

        for case in helpers.cases():
            label = case['name'] + '/CACHED_N8'
            saved = by_name[case['name']]
            serialized_case = {key: [str(v) for v in value] if isinstance(value, list) else str(value) for key, value in case.items()}
            check(label + '/identical_source_case_and_N', serialized_case == saved['case'] and saved['N_first'] == N)
            di.configure(60)
            coefficients = ManufacturedCoefficients(case)
            cache_json = saved['midpoint_candidate']
            cache = {key: pe.iv(value) for key, value in cache_json.items()}
            result = method.integrate_signed(coefficients, N, cached_midpoint=cache)
            coefficient_calls += coefficients.evaluations
            check(label + '/exactly_N_whole_cell_zero_point_calls', coefficients.evaluations == coefficients.whole_cell_calls == N and coefficients.point_calls == 0)
            check(label + '/declared_cached_branch_counts', result['new_coefficient_evaluations'] == N and result['cell_coverage']['whole_cell_derivative_evaluations'] == N and result['cell_coverage']['midpoint_evaluations'] == 0)
            check(label + '/cached_origin', result['midpoint_origin'] == 'REUSED_IDENTITY_BOUND_AGGREGATE')
            check(label + '/midpoint_aggregate_retained_exactly', pe.pack(result['midpoint']) == cache_json and pe.pack(cache) == cache_json)
            check(label + '/no_point_values_or_terms_fabricated', all(row['midpoint_value'] == row['midpoint_term'] == {} for row in result['cells']))
            check(label + '/same_curvature_as_saved_uncached', pe.pack(result['curvature_correction']) == saved['curvature_correction_candidate'])
            check(label + '/same_signed_result_as_saved_uncached', pe.pack(result['signed']) == saved['signed_candidate'])
            signed = result['signed']
            target = helpers.first_oracle(oracle, case)
            exact_gains = helpers.gain_oracle(oracle, case)
            check(label + '/seventeen_keys', len(signed) == 17 and set(signed) == set(target))
            for key in sorted(target):
                check(label + '/independent_first_oracle/' + key, contained(signed[key], target[key]), {'candidate': signed[key].json(), 'oracle': target[key].json()})
            if case['name'] == 'zero_total_opposite_species_defects':
                check(label + '/zero_photon_nonzero_opposite_species', signed['P1'].lo == signed['P1'].hi == 0 and signed['A_HI'].lo > 0 and signed['A_HeI'].hi < 0)
            if case['name'] in ('exact_zero_source_off', 'frozen_match_nonzero_incoming'):
                check(label + '/exact_local_zero', all(v.lo == v.hi == 0 for v in signed.values()))
            if case['name'] in ('positive_quadratic_forcing', 'negative_quadratic_forcing'):
                curvature = result['curvature_correction']['P1']
                check(label + '/quadratic_sign', curvature.lo > 0 if case['qpoly'][2] > 0 else curvature.hi < 0)
            _, gains = pe.frozen_outputs_and_gains(coefficients)
            center, eta = iv(case['c']), iv(case['eta'])
            carry_boxes = {key: signed[key] + gains[key] * center + pe.symmetric((abs(gains[key]) * eta).hi) for key in signed}
            carry_targets = []
            for error in (-case['eta'], Q(0), case['eta']):
                exact = {key: target[key] + exact_gains[key] * oracle.B(case['c'] + error) for key in signed}
                for key in sorted(exact):
                    check(label + '/incoming_' + str(error) + '/' + key, contained(carry_boxes[key], exact[key]))
                carry_targets.append({'incoming_error_exact': str(error), 'oracle': {key: value.json() for key, value in exact.items()}})
            rows.append({'case': serialized_case, 'N_first': N, 'midpoint_cache_sha256': hashlib.sha256(json.dumps(cache_json, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                'midpoint_retained': pe.pack(result['midpoint']), 'signed_candidate': pe.pack(signed),
                'signed_oracle': {key: value.json() for key, value in target.items()},
                'curvature_correction': pe.pack(result['curvature_correction']),
                'incoming_candidate': pe.pack(carry_boxes), 'incoming_oracle': carry_targets,
                'new_whole_cell_calls': coefficients.whole_cell_calls, 'new_midpoint_calls': coefficients.point_calls,
                'rounding_operation_counts': dict(di.COUNTS)})
        check('new_candidate_identity_after', sha(candidate) == args.candidate_sha256)
        check('original_results_unchanged', sha(prior / 'CONTROL_RESULTS.json') == OLD_RESULTS_PIN)
        signal.setitimer(signal.ITIMER_PROF, 0)
        save(output / 'CONTROL_RESULTS.json', {'schema': state['schema'], 'rows': rows, 'checks': checks})
        receipt = {**state, 'status': 'PASS_CACHED_MIDPOINT_BRANCH_CONTROLS',
            'executions_completed': len(rows), 'checks_passed': len(checks), 'checks_failed': 0,
            'manufactured_cached_integral_invocations': len(rows), 'manufactured_whole_cell_evaluations': coefficient_calls,
            'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start,
            'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'results_sha256': sha(output / 'CONTROL_RESULTS.json')}
        save(output / 'RECEIPT.json', receipt)
        print(json.dumps({key: receipt[key] for key in ('status', 'executions_completed', 'checks_passed', 'manufactured_whole_cell_evaluations', 'new_midpoint_evaluations', 'wall_seconds', 'cpu_seconds', 'results_sha256')}, sort_keys=True), flush=True)
    except BaseException as exc:
        signal.setitimer(signal.ITIMER_PROF, 0)
        save(output / 'PARTIAL_RESULTS.json', {'rows': rows, 'checks': checks})
        failure = {**state, 'status': 'FIRST_FAILURE_PRESERVED_NO_AUTOMATIC_RETRY', 'error_type': type(exc).__name__,
            'error': str(exc), 'traceback': traceback.format_exc(), 'executions_completed': len(rows),
            'manufactured_whole_cell_evaluations': coefficient_calls, 'checks_completed': len(checks),
            'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start}
        save(output / 'FIRST_FAILURE.json', failure)
        print(json.dumps({'status': failure['status'], 'error': str(exc), 'executions_completed': len(rows)}), flush=True)
        raise


if __name__ == '__main__':
    main()
