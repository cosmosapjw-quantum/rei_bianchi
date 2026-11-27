#!/usr/bin/env python3
"""E13C10 closed-form controls; no captured coefficient or old suite execution."""
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
ORACLE_PIN = '15806e4758038a788312dfe075f10a364682e3655a0ca35ed0ca602166ea091f'
SOURCE_LOCK_PIN = '386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f'
SPECIES = ('HI', 'HeI', 'HeII')
LEVELS = (8, 32)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    with Path(path).open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cases():
    base = {'h': Q('0.5'), 'lf': [Q('0.5'), Q('0.25'), Q('0.25')],
            'dl': [Q(0), Q(0), Q(0)], 'qf': Q('0.75'), 'dq': Q(0),
            'f0': Q('0.25'), 'c': Q('0.0625'), 'eta': Q('0.015625'),
            'e0': Q(10), 'chi': [Q(1), Q(2), Q(3)]}
    descriptions = [
        ('exact_zero_source_off', {'lf': [Q(0)] * 3, 'qf': Q(0), 'f0': Q(0), 'c': Q(0), 'eta': Q(0)}),
        ('frozen_match_nonzero_incoming', {}),
        ('positive_forcing_zero_L', {'lf': [Q(0)] * 3, 'dq': Q('0.125'), 'c': Q('-0.0625')}),
        ('positive_forcing_positive_L', {'dq': Q('0.125'), 'c': Q('-0.03125')}),
        ('positive_total_opacity_defect', {'dl': [Q('0.125'), Q(0), Q(0)]}),
        ('negative_total_opacity_defect', {'dl': [Q('-0.125'), Q(0), Q(0)]}),
        ('zero_total_opposite_species_defects', {'dl': [Q('0.125'), Q('-0.125'), Q(0)]}),
        ('zero_L_opacity_defect', {'lf': [Q(0)] * 3, 'dl': [Q('0.125'), Q(0), Q(0)], 'dq': Q('0.125')}),
        ('source_off_nonzero_stock', {'qf': Q(0), 'dl': [Q('0.125'), Q(0), Q(0)]}),
        ('positive_quadratic_forcing', {'lf': [Q(0)] * 3, 'qf': Q(0), 'qpoly': [Q(0), Q(0), Q(1)]}),
        ('negative_quadratic_forcing', {'lf': [Q(0)] * 3, 'qf': Q(1), 'qpoly': [Q(0), Q(0), Q(-1)]}),
        ('centered_cubic_sign_changing_curvature', {'lf': [Q(0)] * 3, 'qf': Q(1),
             'qpoly': [Q('-0.015625'), Q('0.1875'), Q('-0.75'), Q(1)]})]
    return [{'name': name, **base, **changes} for name, changes in descriptions]


def exponential_moment(oracle, n, rate, h):
    """Integral of u**n exp(-rate*u), independent exact closed-form recurrence."""
    B = oracle.B
    if rate == 0:
        return B(h ** (n + 1) / (n + 1))
    current = oracle.J(rate, h)
    endpoint = (-B(rate * h)).exp()
    for degree in range(1, n + 1):
        current = (B(degree) * current - B(h ** degree) * endpoint) / B(rate)
    return current


def first_oracle(oracle, case):
    """Integrated differential-response equations, not candidate integrands."""
    B = oracle.B
    L, d = sum(case['lf']), sum(case['dl'])
    h, e0 = case['h'], case['e0']
    stock0, stockE = oracle.stock_integrals(L, case['f0'], case['qf'], h, e0)
    if 'qpoly' in case:
        if L != 0 or d != 0 or any(case['dl']):
            raise ValueError('polynomial oracle is declared only for zero opacity')
        polynomial = case['qpoly']
        endpoint = B(sum(p * h ** (j + 1) / (j + 1) for j, p in enumerate(polynomial)))
        integral0 = B(sum(p * h ** (j + 2) / ((j + 1) * (j + 2)) for j, p in enumerate(polynomial)))
        integralE = B(e0) * sum((B(p / (j + 1)) * exponential_moment(oracle, j + 1, Q(1), h)
                                for j, p in enumerate(polynomial)), B(0))
        source0 = endpoint
        sourceE = B(e0) * sum((B(p) * exponential_moment(oracle, j, Q(1), h)
                              for j, p in enumerate(polynomial)), B(0))
    else:
        zero_incoming = {**case, 'c': Q(0)}
        endpoint = oracle.prefix_value(zero_incoming, h)
        integral0, integralE, _, _, _ = oracle.prefix_integrals(zero_incoming)
        source0 = B(case['dq'] * h)
        sourceE = B(e0 * case['dq']) * oracle.J(Q(1), h)
    out = {'P1': endpoint, 'Z_eV': integralE, 'QN': source0, 'QE_eV': sourceE}
    for species, lf, dl, chi in zip(SPECIES, case['lf'], case['dl'], case['chi']):
        a = B(dl) * stock0 + B(lf) * integral0
        b = B(dl) * stockE + B(lf) * integralE
        out['A_' + species] = a
        out['B_' + species + '_eV'] = b
        out['H_' + species + '_eV'] = b - B(chi) * a
    out['A_total'] = B(d) * stock0 + B(L) * integral0
    out['B_total_eV'] = B(d) * stockE + B(L) * integralE
    out['H_total_eV'] = (out['B_total_eV']
        - B(sum(chi * dl for chi, dl in zip(case['chi'], case['dl']))) * stock0
        - B(sum(chi * lf for chi, lf in zip(case['chi'], case['lf']))) * integral0)
    out['P1_energy_eV'] = B(e0) * (-B(h)).exp() * endpoint
    return out


def gain_oracle(oracle, case):
    B = oracle.B
    h, L, e0 = case['h'], sum(case['lf']), case['e0']
    j0, jE = oracle.J(L, h), B(e0) * oracle.J(L + 1, h)
    out = {'P1': (-B(L * h)).exp(), 'Z_eV': jE, 'QN': B(0), 'QE_eV': B(0)}
    for species, lf, chi in zip(SPECIES, case['lf'], case['chi']):
        a, b = B(lf) * j0, B(lf) * jE
        out['A_' + species] = a
        out['B_' + species + '_eV'] = b
        out['H_' + species + '_eV'] = b - B(chi) * a
    out['A_total'] = B(L) * j0
    out['B_total_eV'] = B(L) * jE
    out['H_total_eV'] = out['B_total_eV'] - B(sum(lf * chi for lf, chi in zip(case['lf'], case['chi']))) * j0
    out['P1_energy_eV'] = B(e0) * (-B(h)).exp() * out['P1']
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--e13c9-root', type=Path, required=True)
    parser.add_argument('--candidate-file', type=Path, required=True)
    parser.add_argument('--candidate-sha256', required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    root7, root9, candidate, contract, output = [p.resolve() for p in
        (args.source_root, args.e13c9_root, args.candidate_file, args.contract, args.output_dir)]
    output.mkdir(parents=True, exist_ok=False)
    oracle_path = root9 / 'tests/MANUFACTURED/run_manufactured_controls.py'
    start, cpu_start = time.perf_counter(), time.process_time()
    rows, checks, manufactured_calls = [], [], 0
    state = {'schema': 'bass-he-e13c10-first-integral-manufactured-v1',
        'role': 'CONTROL_CONTRIBUTOR_NOT_FINAL_INDEPENDENT_REVIEWER',
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'candidate_path': str(candidate), 'candidate_sha256': args.candidate_sha256,
        'contract_sha256': sha(contract), 'control_script_sha256': sha(__file__),
        'oracle_path': str(oracle_path), 'oracle_sha256': ORACLE_PIN,
        'original_source_lock_sha256': SOURCE_LOCK_PIN,
        'candidate_precision': 60, 'oracle_precision': 140, 'N_levels': list(LEVELS),
        'case_names': [c['name'] for c in cases()], 'cpu_seconds_limit': 20,
        'automatic_retries': 0, 'captured_coefficient_evaluations': 0,
        'captured_first_integral_invocations': 0, 'completed_scientific_work_replays': 0,
        'old_unchanged_manufactured_suite_invocations': 0, 'ODE_solves': 0, 'NCP_launches': 0,
        'host': platform.node(), 'python': sys.version, 'provider_attestation': 'NOT_ASSERTED',
        'oracle_independence': 'Integrated-response closed-form formula and separate P140 directed evaluator; shares exact parameters and Python Decimal exp primitive. Candidate uses unchanged original le.integrands. E13C9 oracle utilities imported, old main/suite never invoked.',
        'claim_ceiling': 'Manufactured first-integral computational validation only; stitched carry and captured/physical/full-population admission require separate evidence.'}
    save(output / 'START.json', state)

    def check(name, passed, evidence=None):
        checks.append({'check': name, 'pass': bool(passed)})
        if not passed:
            raise AssertionError(json.dumps({'check': name, 'evidence': evidence}, default=str))

    def contains(box, target):
        return box.lo <= target.lo <= target.hi <= box.hi

    def timeout(signum, frame):
        raise TimeoutError('declared 20 CPU-second manufactured-control limit reached')

    signal.signal(signal.SIGPROF, timeout)
    signal.setitimer(signal.ITIMER_PROF, 20)
    try:
        check('fixed_candidate_identity_before', sha(candidate) == args.candidate_sha256)
        check('fixed_oracle_identity', sha(oracle_path) == ORACLE_PIN)
        sys.path.insert(0, str(root7 / 'code'))
        from off_path_worker import Context
        ctx = Context(root7)
        check('original_source_lock_identity', ctx.source_lock_sha256 == SOURCE_LOCK_PIN)
        di, pe = ctx.di, ctx.pe
        oracle = load_module('e13c9_closed_form_utilities_for_e13c10', oracle_path)
        sys.path.insert(0, str(candidate.parent))
        method = load_module('e13c10_first_midpoint_under_control', candidate)
        check('candidate_api_callable', callable(method.integrate_signed))

        def interval_fraction(q):
            return di.IV(q.numerator) / q.denominator

        class ManufacturedCoefficients:
            def __init__(self, case):
                self.case = case
                for key in ('h', 'f0', 'qf', 'e0'):
                    setattr(self, key, interval_fraction(case[key]))
                self.lf = [interval_fraction(q) for q in case['lf']]
                self.L = sum(self.lf, di.IV(0))
                self.chi = [interval_fraction(q) for q in case['chi']]
                self.mask = [lf > 0 or lf + dl > 0 for lf, dl in zip(case['lf'], case['dl'])]
                self.endpoint_E = self.e0 * (-self.h).exp()
                self.evaluations = 0
                self.domain = {'manufactured_only': True}

            def __call__(self, x):
                self.evaluations += 1
                factory = di.Jet2 if isinstance(x, di.Jet2) else di.IV
                u = self.h * x
                energy = self.e0 * (-u).exp()
                if 'qpoly' in self.case:
                    dq = factory(0)
                    for coefficient in reversed(self.case['qpoly']):
                        dq = dq * u + interval_fraction(coefficient)
                    source = factory(self.qf) + dq
                else:
                    source = factory(interval_fraction(self.case['qf'] + self.case['dq']))
                rates = [factory(interval_fraction(lf + dl)) for lf, dl in zip(self.case['lf'], self.case['dl'])]
                return energy, source, rates

        for case in cases():
            check(case['name'] + '/nonnegative_actual_rates', all(lf + dl >= 0 for lf, dl in zip(case['lf'], case['dl'])))
            source_lower = (case['qf'] + sum(min(Q(0), p * case['h'] ** j) for j, p in enumerate(case['qpoly']))
                            if 'qpoly' in case else case['qf'] + case['dq'])
            check(case['name'] + '/nonnegative_source_and_initial', source_lower >= 0 and case['f0'] + case['c'] - case['eta'] >= 0)
            target = first_oracle(oracle, case)
            exact_gains = gain_oracle(oracle, case)
            for n in LEVELS:
                label = case['name'] + '/N' + str(n)
                di.configure(60)
                coefficients = ManufacturedCoefficients(case)
                computed = method.integrate_signed(coefficients, n)
                manufactured_calls += coefficients.evaluations
                signed = computed['signed']
                check(label + '/coefficient_call_count', coefficients.evaluations == 2 * n)
                check(label + '/seventeen_keys', len(signed) == 17 and set(signed) == set(target))
                for key in sorted(target):
                    check(label + '/first_integral/' + key, contains(signed[key], target[key]),
                          {'candidate': signed[key].json(), 'oracle': target[key].json()})
                ledgers = {'number': signed['P1'] + signed['A_total'] - signed['QN'],
                           'energy_eV': signed['P1_energy_eV'] + signed['B_total_eV'] + signed['Z_eV'] - signed['QE_eV']}
                for species, chi in zip(SPECIES, coefficients.chi):
                    ledgers['heat_' + species] = signed['H_' + species + '_eV'] - signed['B_' + species + '_eV'] + chi * signed['A_' + species]
                for key, box in ledgers.items():
                    check(label + '/ledger/' + key, box.contains(D(0)))
                if case['name'] == 'positive_total_opacity_defect':
                    check(label + '/negative_first_photon', signed['P1'].hi < 0)
                if case['name'] == 'negative_total_opacity_defect':
                    check(label + '/positive_first_photon', signed['P1'].lo > 0)
                if case['name'] == 'zero_total_opposite_species_defects':
                    check(label + '/exact_zero_photon_total_coupling', signed['P1'].lo == signed['P1'].hi == 0)
                    check(label + '/nonzero_opposite_species', signed['A_HI'].lo > 0 and signed['A_HeI'].hi < 0)
                if case['name'] in ('exact_zero_source_off', 'frozen_match_nonzero_incoming'):
                    check(label + '/all_local_integrals_exact_zero', all(box.lo == box.hi == 0 for box in signed.values()))
                if case['name'] == 'source_off_nonzero_stock':
                    check(label + '/source_outputs_exact_zero', all(signed[key].lo == signed[key].hi == 0 for key in ('QN', 'QE_eV')))
                if case['name'] in ('positive_quadratic_forcing', 'negative_quadratic_forcing'):
                    curvature = computed['curvature_correction']['P1']
                    check(label + '/curvature_sign_retained', curvature.lo > 0 if case['qpoly'][2] > 0 else curvature.hi < 0)
                    for key in ('P1', 'QN'):
                        check(label + '/quadratic_roundoff_only_width/' + key, signed[key].width() <= D('1e-48'))
                if case['name'] == 'centered_cubic_sign_changing_curvature':
                    check(label + '/exact_cubic_cancellation_oracle', target['P1'].lo == target['P1'].hi == 0)
                _, gains = pe.frozen_outputs_and_gains(coefficients)
                c, eta = interval_fraction(case['c']), interval_fraction(case['eta'])
                check(label + '/declared_exact_carry_points', c.lo == c.hi and eta.lo == eta.hi)
                carry_boxes = {key: signed[key] + gains[key] * c + pe.symmetric((abs(gains[key]) * eta).hi) for key in signed}
                carry_targets = []
                for key in sorted(gains):
                    check(label + '/independent_incoming_gain/' + key, contains(gains[key], exact_gains[key]))
                for error in (-case['eta'], Q(0), case['eta']):
                    targets = {key: target[key] + exact_gains[key] * oracle.B(case['c'] + error) for key in signed}
                    for key in sorted(targets):
                        check(label + '/incoming_error_' + str(error) + '/' + key, contains(carry_boxes[key], targets[key]),
                              {'candidate': carry_boxes[key].json(), 'oracle': targets[key].json()})
                    carry_targets.append({'incoming_error_exact': str(error), 'oracle': {key: value.json() for key, value in targets.items()}})
                rows.append({'case': {key: [str(v) for v in value] if isinstance(value, list) else str(value) for key, value in case.items()},
                    'N_first': n, 'manufactured_coefficient_evaluations': coefficients.evaluations,
                    'signed_candidate': {key: value.json() for key, value in signed.items()},
                    'signed_oracle': {key: value.json() for key, value in target.items()},
                    'midpoint_candidate': pe.pack(computed['midpoint']),
                    'curvature_correction_candidate': pe.pack(computed['curvature_correction']),
                    'ledger_enclosures': pe.pack(ledgers), 'incoming_candidate': pe.pack(carry_boxes),
                    'incoming_oracle': carry_targets, 'rounding_operation_counts': dict(di.COUNTS)})
        check('fixed_candidate_identity_after', sha(candidate) == args.candidate_sha256)
        check('fixed_oracle_identity_after', sha(oracle_path) == ORACLE_PIN)
        signal.setitimer(signal.ITIMER_PROF, 0)
        save(output / 'CONTROL_RESULTS.json', {'schema': state['schema'], 'rows': rows, 'checks': checks})
        receipt = {**state, 'status': 'PASS_MANUFACTURED_FIRST_INTEGRAL_CONTROLS',
            'checks_passed': len(checks), 'checks_failed': 0, 'executions_completed': len(rows),
            'manufactured_first_integral_invocations': len(rows), 'manufactured_coefficient_evaluations': manufactured_calls,
            'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start,
            'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'results_sha256': sha(output / 'CONTROL_RESULTS.json')}
        save(output / 'RECEIPT.json', receipt)
        print(json.dumps({key: receipt[key] for key in ('status', 'checks_passed', 'executions_completed',
            'manufactured_coefficient_evaluations', 'wall_seconds', 'cpu_seconds', 'results_sha256')}, sort_keys=True), flush=True)
    except BaseException as exc:
        signal.setitimer(signal.ITIMER_PROF, 0)
        save(output / 'PARTIAL_RESULTS.json', {'rows': rows, 'checks': checks})
        failure = {**state, 'status': 'FIRST_FAILURE_PRESERVED_NO_AUTOMATIC_RETRY', 'error_type': type(exc).__name__,
            'error': str(exc), 'traceback': traceback.format_exc(), 'executions_completed': len(rows),
            'manufactured_coefficient_evaluations': manufactured_calls, 'checks_completed': len(checks),
            'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start}
        save(output / 'FIRST_FAILURE.json', failure)
        print(json.dumps({'status': failure['status'], 'error': str(exc), 'executions_completed': len(rows)}), flush=True)
        raise


if __name__ == '__main__':
    main()
