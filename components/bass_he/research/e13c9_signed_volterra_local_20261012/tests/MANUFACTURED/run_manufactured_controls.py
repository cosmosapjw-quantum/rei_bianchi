#!/usr/bin/env python3
"""Independent closed-form manufactured controls for E13C9.

No captured coefficient evaluation or ODE solve. The oracle derives the exact
constant-coefficient solution and first-Volterra prefix algebraically, using a
separate 140-digit directed Decimal evaluator. Candidate primitives remain P60.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal as D, Context as DecimalContext, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback

sys.dont_write_bytecode = True
TASK = Path('/workspace/scratch/7fd51143e473/e13c9_research_20261012')
SOURCE = TASK / 'RESTORED_E13C8/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
CANDIDATE = TASK / 'BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1/code/signed_volterra.py'
CONTRACT = CANDIDATE.parents[1] / 'SCIENTIFIC_CONTRACT.md'
ORACLE_PRECISION = 140
DOWN = DecimalContext(prec=ORACLE_PRECISION, rounding=ROUND_FLOOR)
UP = DecimalContext(prec=ORACLE_PRECISION, rounding=ROUND_CEILING)
NEAR = DecimalContext(prec=ORACLE_PRECISION, rounding=ROUND_HALF_EVEN)


class B:
    """Independent interval evaluator for the closed-form oracle only."""
    __slots__ = ('lo', 'hi')

    def __init__(self, lo=0, hi=None):
        if isinstance(lo, B):
            assert hi is None
            self.lo, self.hi = lo.lo, lo.hi
        elif isinstance(lo, Q):
            assert hi is None
            self.lo = DOWN.divide(D(lo.numerator), D(lo.denominator))
            self.hi = UP.divide(D(lo.numerator), D(lo.denominator))
        else:
            assert not isinstance(lo, float)
            self.lo, self.hi = D(lo), D(lo if hi is None else hi)
        assert self.lo.is_finite() and self.hi.is_finite() and self.lo <= self.hi

    def __add__(self, other):
        v = B(other)
        return B(DOWN.add(self.lo, v.lo), UP.add(self.hi, v.hi))

    __radd__ = __add__

    def __neg__(self):
        return B(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + (-B(other))

    def __rsub__(self, other):
        return B(other) + (-self)

    def __mul__(self, other):
        v = B(other)
        pairs = [(a, b) for a in (self.lo, self.hi) for b in (v.lo, v.hi)]
        return B(min(DOWN.multiply(a, b) for a, b in pairs), max(UP.multiply(a, b) for a, b in pairs))

    __rmul__ = __mul__

    def __truediv__(self, other):
        v = B(other)
        if v.lo <= 0 <= v.hi:
            raise ZeroDivisionError('oracle division interval includes zero')
        return self * B(DOWN.divide(D(1), v.hi), UP.divide(D(1), v.lo))

    def __rtruediv__(self, other):
        return B(other) / self

    def __pow__(self, n):
        assert isinstance(n, int) and n >= 0
        result = B(1)
        for _ in range(n):
            result *= self
        return result

    def exp(self):
        if self.lo == self.hi == 0:
            return B(1)
        return B(NEAR.next_minus(NEAR.exp(self.lo)), NEAR.next_plus(NEAR.exp(self.hi)))

    def magnitude(self):
        return max(self.lo.copy_abs(), self.hi.copy_abs())

    def json(self):
        return {'lo': str(self.lo), 'hi': str(self.hi)}


def J(rate, h):
    return B(h) if rate == 0 else (1 - (-B(rate) * B(h)).exp()) / B(rate)


def U(rate, h):
    """Integral of u exp(-rate*u), closed form with its exact zero-rate limit."""
    return B(h) ** 2 / 2 if rate == 0 else (1 - (1 + B(rate) * B(h)) * (-B(rate) * B(h)).exp()) / (B(rate) ** 2)


def V(rate, h):
    """Integral of u^2 exp(-rate*u)."""
    if rate == 0:
        return B(h) ** 3 / 3
    z = B(rate) * B(h)
    return (2 - (z ** 2 + 2 * z + 2) * (-z).exp()) / (B(rate) ** 3)


def prefix_parameters(case):
    L, d = sum(case['lf']), sum(case['dl'])
    if L:
        a = (case['dq'] - d * case['qf'] / L) / L
        b = case['c'] - a
        g = -d * (case['f0'] - case['qf'] / L)
        return L, d, a, b, g
    return L, d, case['c'], case['dq'] - d * case['f0'], -d * case['qf']


def prefix_value(case, u):
    L, d, a, b, g = prefix_parameters(case)
    if not L:
        return B(a) + B(b) * B(u) + B(g) * B(u) ** 2 / 2
    return B(a) + (B(b) + B(g) * B(u)) * (-B(L) * B(u)).exp()


def prefix_range(case, left, right):
    """Exact extrema locations: at most one interior stationary point."""
    L, d, a, b, g = prefix_parameters(case)
    points = [left, right]
    critical = (g - L * b) / (L * g) if L and g else (-b / g if not L and g else None)
    if critical is not None and left < critical < right:
        points.append(critical)
    vals = [prefix_value(case, t) for t in points]
    return B(min(v.lo for v in vals), max(v.hi for v in vals)), points


def prefix_integrals(case):
    """I0=int delta1, IE=int E*delta1, C=int F(h-u)*delta1."""
    h, e0 = case['h'], case['e0']
    L, d, a, b, g = prefix_parameters(case)
    if L:
        i0 = B(a) * B(h) + B(b) * J(L, h) + B(g) * U(L, h)
        ie = B(e0) * (B(a) * J(1, h) + B(b) * J(L + 1, h) + B(g) * U(L + 1, h))
        conv = B(a) * J(L, h) + (-B(L) * B(h)).exp() * (B(b) * B(h) + B(g) * B(h) ** 2 / 2)
        kernel0 = (i0 - conv) / B(L)
    else:
        i0 = B(a) * B(h) + B(b) * B(h) ** 2 / 2 + B(g) * B(h) ** 3 / 6
        ie = B(e0) * (B(a) * J(1, h) + B(b) * U(1, h) + B(g) * V(1, h) / 2)
        conv = i0
        kernel0 = B(a) * B(h) ** 2 / 2 + B(b) * B(h) ** 3 / 6 + B(g) * B(h) ** 4 / 24
    eh = B(e0) * (-B(h)).exp()
    kernelE = (ie - eh * conv) / B(L + 1)
    return i0, ie, conv, kernel0, kernelE


def correction_oracle(case):
    L, d = sum(case['lf']), sum(case['dl'])
    i0, ie, conv, k0, ke = prefix_integrals(case)
    eh = B(case['e0']) * (-B(case['h'])).exp()
    ans = {'P1': -B(d) * conv, 'Z_eV': -B(d) * ke, 'QN': B(0), 'QE_eV': B(0)}
    for s, lf, dl, chi in zip(('HI', 'HeI', 'HeII'), case['lf'], case['dl'], case['chi']):
        av = B(dl) * i0 - B(lf * d) * k0
        bv = B(dl) * ie - B(lf * d) * ke
        ans['A_' + s], ans['B_' + s + '_eV'] = av, bv
        ans['H_' + s + '_eV'] = bv - B(chi) * av
    ans['A_total'] = B(d) * i0 - B(L * d) * k0
    ans['B_total_eV'] = B(d) * ie - B(L * d) * ke
    chi_dl = sum(x * y for x, y in zip(case['chi'], case['dl']))
    chi_lf = sum(x * y for x, y in zip(case['chi'], case['lf']))
    ans['H_total_eV'] = ans['B_total_eV'] - B(chi_dl) * i0 + B(chi_lf * d) * k0
    ans['P1_energy_eV'] = eh * ans['P1']
    return ans


def photon_solution(rate, initial, source, h):
    return B(initial) * (-B(rate) * B(h)).exp() + B(source) * J(rate, h)


def stock_integrals(rate, initial, source, h, e0):
    if rate == 0:
        return (B(initial) * B(h) + B(source) * B(h) ** 2 / 2,
                B(e0) * (B(initial) * J(1, h) + B(source) * U(1, h)))
    j0, jE = J(rate, h), J(rate + 1, h)
    return (B(initial) * j0 + B(source) * (B(h) - j0) / B(rate),
            B(e0) * (B(initial) * jE + B(source) * (J(1, h) - jE) / B(rate)))


def exact_remainder_oracle(case, e):
    """True constant-coefficient result minus frozen+first+signed second."""
    L, d = sum(case['lf']), sum(case['dl'])
    h, e0, f0, qf = (case[k] for k in ('h', 'e0', 'f0', 'qf'))
    true0, trueE = stock_integrals(L + d, f0 + case['c'] + e, qf + case['dq'], h, e0)
    frozen0, frozenE = stock_integrals(L, f0, qf, h, e0)
    i0, ie, conv, k0, ke = prefix_integrals(case)
    second = correction_oracle(case)
    trueP = photon_solution(L + d, f0 + case['c'] + e, qf + case['dq'], h)
    frozenP = photon_solution(L, f0, qf, h)
    out = {'P1': trueP - frozenP - prefix_value(case, h) - second['P1'],
           'Z_eV': trueE - frozenE - ie - second['Z_eV'], 'QN': B(0), 'QE_eV': B(0)}
    for s, lf, dl, chi in zip(('HI', 'HeI', 'HeII'), case['lf'], case['dl'], case['chi']):
        av = B(lf + dl) * true0 - B(lf) * frozen0 - (B(dl) * frozen0 + B(lf) * i0) - second['A_' + s]
        bv = B(lf + dl) * trueE - B(lf) * frozenE - (B(dl) * frozenE + B(lf) * ie) - second['B_' + s + '_eV']
        out['A_' + s], out['B_' + s + '_eV'], out['H_' + s + '_eV'] = av, bv, bv - B(chi) * av
    for prefix in ('A', 'B', 'H'):
        suffix = '_eV' if prefix != 'A' else ''
        out[prefix + '_total' + suffix] = sum((out[prefix + '_' + s + suffix] for s in ('HI', 'HeI', 'HeII')), B(0))
    out['P1_energy_eV'] = B(e0) * (-B(h)).exp() * out['P1']
    return out


def valid_bounds(case):
    """Independent constant-data integral upper bounds, no candidate fields."""
    L, d, h, e0 = sum(case['lf']), sum(case['dl']), case['h'], case['e0']
    pf0, pfE = stock_integrals(L, case['f0'], case['qf'], h, e0)
    Hh = B(abs(d)) * J(L, h)
    H0 = B(abs(d)) * ((B(h) - J(L, h)) / B(L) if L else B(h) ** 2 / 2)
    HE = B(abs(d)) * (B(e0) * J(1, h) - B(e0) * (-B(h)).exp() * J(L, h)) / B(L + 1)
    ans = {'D_L': B(abs(d) * h), 'B_r': B(abs(case['dq']) * h) + B(abs(d)) * pf0,
           'H_h': Hh, 'H_0': H0, 'H_E': HE}
    heat_sum = B(0)
    for s, lf, dl, chi in zip(('HI', 'HeI', 'HeII'), case['lf'], case['dl'], case['chi']):
        ta = B(abs(dl) * h) + B(lf) * H0
        tb = B(abs(dl) * e0) * J(1, h) + B(lf) * HE
        th = B(abs(dl) * (e0 + abs(chi)) * h) + B(lf) * (HE + B(abs(chi)) * H0)
        for prefix, value in [('A', ta), ('B', tb), ('H', th)]:
            ans['effective_' + prefix + '_' + s] = value
            ans['triangle_' + prefix + '_' + s] = value
        heat_sum += th
    ans['effective_B_total'] = B(abs(d) * e0) * J(1, h) + B(L) * HE
    ans['effective_H_total'] = ans['triangle_H_total'] = heat_sum
    return ans


def all_cases():
    common = {'h': Q('0.5'), 'lf': [Q('0.5'), Q('0.25'), Q('0.25')],
              'dl': [Q(0), Q(0), Q(0)], 'qf': Q('0.75'), 'dq': Q(0),
              'f0': Q('0.25'), 'c': Q('0.0625'), 'eta': Q('0.015625'),
              'e0': Q(10), 'chi': [Q(1), Q(2), Q(3)]}
    records = [
        ('exact_zero', {'lf': [Q(0)] * 3, 'qf': Q(0), 'f0': Q(0), 'c': Q(0), 'eta': Q(0)}),
        ('frozen_match_nonzero_c_eta', {}),
        ('constant_forcing_zero_L_sign_crossing_prefix', {'lf': [Q(0)] * 3, 'dq': Q('0.125'), 'c': Q('-0.0625')}),
        ('constant_forcing_positive_L', {'dq': Q('0.125'), 'c': Q('-0.03125')}),
        ('positive_total_opacity_defect', {'dl': [Q('0.125'), Q(0), Q(0)], 'dq': Q('0.125')}),
        ('negative_total_opacity_defect', {'dl': [Q('-0.125'), Q(0), Q(0)], 'dq': Q('0.0625')}),
        ('zero_total_nonzero_opposite_species_defects', {'dl': [Q('0.125'), Q('-0.125'), Q(0)], 'dq': Q('0.125')}),
        ('zero_L_with_opacity_defect_polynomial_prefix', {'lf': [Q(0)] * 3, 'dl': [Q('0.125'), Q(0), Q(0)], 'dq': Q('0.125')}),
        ('D_equals_one_no_contraction_requirement', {'dl': [Q(2), Q(0), Q(0)], 'dq': Q('0.125')})]
    return [{'name': name, **common, **changes} for name, changes in records]


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    out, start, cpu_start = args.output_dir, time.perf_counter(), time.process_time()
    source_hash = file_sha(CANDIDATE)
    checked, rows = [], []
    state = {'schema': 'bass-he-e13c9-manufactured-controls-v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
             'role': 'MANUFACTURED_VALIDATION_CONTRIBUTOR_NOT_FINAL_ADMISSION_REVIEWER',
             'candidate_sha256': source_hash, 'candidate_file': str(CANDIDATE),
             'contract_sha256': file_sha(CONTRACT), 'oracle_code_sha256': file_sha(__file__),
             'precision_candidate': 60, 'precision_independent_closed_form_oracle': ORACLE_PRECISION,
             'M_levels': [8, 32], 'cases': [x['name'] for x in all_cases()],
             'physics_coefficient_evaluations': 0, 'captured_baseline_reruns': 0,
             'ODE_solves': 0, 'full_population_inferences': 0, 'NCP_launches': 0,
             'cpu_seconds_limit': 20, 'automatic_retries': 0,
             'host': {'hostname': platform.node(), 'python': sys.version, 'provider_attestation': 'NOT_ASSERTED'},
             'oracle_limitation': 'Independent closed-form mathematics and interval evaluator; Python decimal exp primitive is shared. This is not formal proof-assistant verification or an independent physical coefficient model.'}
    write(out / 'START.json', state)

    def check(name, passed, evidence=None):
        checked.append({'check': name, 'pass': bool(passed)})
        if not passed:
            raise AssertionError(json.dumps({'check': name, 'evidence': evidence}, default=str))

    def contained(box, target):
        return box.lo <= target.lo <= target.hi <= box.hi

    def cpu_timeout(signum, frame):
        raise TimeoutError('20 CPU-second manufactured-control budget reached')

    signal.signal(signal.SIGPROF, cpu_timeout)
    signal.setitimer(signal.ITIMER_PROF, 20)
    try:
        sys.path.insert(0, str(SOURCE / 'code'))
        from off_path_worker import Context
        ctx = Context(SOURCE)
        di, le, pe = ctx.di, ctx.le, ctx.pe
        sys.path.insert(0, str(CANDIDATE.parent))
        import signed_volterra as sv
        check('candidate_module_path', Path(sv.__file__).resolve() == CANDIDATE.resolve())
        check('candidate_sha_before', file_sha(CANDIDATE) == source_hash)
        check('original_source_lock', ctx.source_lock_sha256 == '386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f')

        def iv_fraction(value):
            return di.IV(value.numerator) / value.denominator

        class Manufactured:
            def __init__(self, case):
                self.case = case
                for name in ('h', 'f0', 'qf', 'e0'):
                    setattr(self, name, iv_fraction(case[name]))
                self.lf = [iv_fraction(x) for x in case['lf']]
                self.L = sum(self.lf, di.IV(0))
                self.chi = [iv_fraction(x) for x in case['chi']]
                self.endpoint_E = self.e0 * (-self.h).exp()
                self.evaluations = 0
                self.domain = {'manufactured_only': True}

            def __call__(self, x):
                self.evaluations += 1
                factory = di.Jet2 if isinstance(x, di.Jet2) else di.IV
                E = self.e0 * (-self.h * x).exp()
                q = factory(iv_fraction(self.case['qf'] + self.case['dq']))
                rates = [factory(iv_fraction(lf + dl)) for lf, dl in zip(self.case['lf'], self.case['dl'])]
                return E, q, rates

        for case in all_cases():
            check(case['name'] + '/nonnegative_actual_rates', all(lf + dl >= 0 for lf, dl in zip(case['lf'], case['dl'])))
            check(case['name'] + '/nonnegative_actual_source_and_initial', case['qf'] + case['dq'] >= 0 and case['f0'] + case['c'] - case['eta'] >= 0)
            for m in (8, 32):
                label = case['name'] + '/M' + str(m)
                di.configure(60)
                coeff = Manufactured(case)
                cdecimal = iv_fraction(case['c']).lo
                etadecimal = iv_fraction(case['eta']).lo
                result = sv.prefix_and_correction(coeff, m, cdecimal)
                exact_signed = correction_oracle(case)
                check(label + '/new_coefficient_count', result['new_coefficient_evaluations'] == 2 * m)
                check(label + '/no_firstmethod_replay', result['firstvariation_quadrature_replays'] == 0)
                check(label + '/uncertainty_excluded_from_prefix', result['incoming_uncertainty_in_prefix'] is False)
                check(label + '/endpoint', contained(result['prefix_endpoint'], prefix_value(case, case['h'])))
                cells = []
                for j, saved in enumerate(result['cells']):
                    left, right = case['h'] * Q(j, m), case['h'] * Q(j + 1, m)
                    oracle_left, oracle_right = prefix_value(case, left), prefix_value(case, right)
                    whole, extrema = prefix_range(case, left, right)
                    check(label + '/cell' + str(j) + '/left', contained(saved['prefix_left'], oracle_left))
                    check(label + '/cell' + str(j) + '/right', contained(saved['prefix_right'], oracle_right))
                    check(label + '/cell' + str(j) + '/whole_range', contained(saved['prefix_whole_cell'], whole), {'candidate': saved['prefix_whole_cell'].json(), 'oracle': whole.json()})
                    cells.append({'cell': j, 'physical_left': str(left), 'physical_right': str(right),
                                  'prefix_oracle_left': oracle_left.json(), 'prefix_oracle_right': oracle_right.json(),
                                  'prefix_oracle_whole': whole.json(), 'extrema_locations_exact': list(map(str, extrema)),
                                  'candidate_left': saved['prefix_left'].json(), 'candidate_right': saved['prefix_right'].json(),
                                  'candidate_whole': saved['prefix_whole_cell'].json()})
                check(label + '/signed_keys', set(exact_signed) == set(result['signed']))
                for key, target in exact_signed.items():
                    check(label + '/signed/' + key, contained(result['signed'][key], target), {'candidate': result['signed'][key].json(), 'oracle': target.json()})
                if case['name'] == 'positive_total_opacity_defect':
                    check(label + '/negative_photon_correction', result['signed']['P1'].hi < 0)
                if case['name'] == 'negative_total_opacity_defect':
                    check(label + '/positive_photon_correction', result['signed']['P1'].lo > 0)
                if case['name'] == 'zero_total_nonzero_opposite_species_defects':
                    check(label + '/zero_photon_correction', result['signed']['P1'].lo == result['signed']['P1'].hi == 0)
                    check(label + '/nonzero_opposite_species_corrections', result['signed']['A_HI'].lo > 0 and result['signed']['A_HeI'].hi < 0)
                if case['name'] == 'exact_zero':
                    check(label + '/exact_zero_prefix_and_corrections', result['prefix_endpoint'].lo == result['prefix_endpoint'].hi == 0 and all(v.lo == v.hi == 0 for v in result['signed'].values()))
                oracle_bounds = valid_bounds(case)
                bounds = {k: di.IV(v.lo, v.hi) for k, v in oracle_bounds.items()}
                frozen, gains = pe.frozen_outputs_and_gains(coeff)
                rem = sv.remainder_bounds(coeff, bounds, gains, cdecimal, etadecimal)
                check(label + '/S_contains_new_center_eta_Br', Q(rem['S_upper']) >= abs(case['c']) + case['eta'] + Q(bounds['B_r'].hi))
                check(label + '/whole_D_not_endpoint_Hh', Q(rem['D_upper']) == abs(sum(case['dl'])) * case['h'])
                for k, t in rem['T_upper'].items():
                    gmag = max(Q(gains[k].lo).__abs__(), Q(gains[k].hi).__abs__())
                    inner = gmag * case['eta']
                    couple = Q(t) * case['eta']
                    second_required = Q(t) * Q(rem['D_upper']) * Q(rem['S_upper'])
                    check(label + '/remainder_second/' + k, Q(rem['second_volterra_remainder_upper'][k]) >= second_required)
                    check(label + '/incoming/' + k, Q(rem['incoming_upper'][k]) >= inner)
                    check(label + '/incoming_coupling/' + k, Q(rem['incoming_coupling_upper'][k]) >= couple)
                    check(label + '/total/' + k, Q(rem['total_before_numerical_upper'][k]) >= inner + couple + second_required)
                residual_rows = []
                for e in (-case['eta'], Q(0), case['eta']):
                    rr = exact_remainder_oracle(case, e)
                    for k, v in rr.items():
                        bound = D(rem['total_before_numerical_upper'][k])
                        check(label + '/true_remainder/e' + str(e) + '/' + k, v.magnitude() <= bound,
                              {'oracle': v.json(), 'bound': str(bound)})
                    residual_rows.append({'incoming_error_exact': str(e), 'true_remainder_oracle': {k: v.json() for k, v in rr.items()}})
                rows.append({'case': {k: [str(a) for a in v] if isinstance(v, list) else str(v) for k, v in case.items()},
                             'M_second': m, 'coefficient_evaluations_manufactured': coeff.evaluations,
                             'prefix_endpoint_candidate': result['prefix_endpoint'].json(),
                             'prefix_endpoint_oracle': prefix_value(case, case['h']).json(),
                             'signed_candidate': {k: v.json() for k, v in result['signed'].items()},
                             'signed_oracle': {k: v.json() for k, v in exact_signed.items()}, 'cells': cells,
                             'independent_integral_bounds': {k: v.json() for k, v in oracle_bounds.items()},
                             'remainder_candidate': pe.pack(rem), 'actual_residuals': residual_rows,
                             'rounding_operation_counts': dict(di.COUNTS)})
        check('candidate_sha_after', file_sha(CANDIDATE) == source_hash)
        signal.setitimer(signal.ITIMER_PROF, 0)
        write(out / 'CONTROL_RESULTS.json', {'schema': state['schema'], 'rows': rows, 'checks': checked})
        receipt = {**state, 'status': 'PASS_MANUFACTURED_CLOSED_FORM_CONTROLS',
                   'checks_passed': len(checked), 'checks_failed': 0, 'cases_completed': len(rows),
                   'manufactured_coefficient_evaluations': sum(x['coefficient_evaluations_manufactured'] for x in rows),
                   'wall_seconds': time.perf_counter() - start, 'cpu_seconds': time.process_time() - cpu_start,
                   'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'results_sha256': file_sha(out / 'CONTROL_RESULTS.json'),
                   'claim_ceiling': 'Manufactured computational validation only; no physical or full-population numerical admission.'}
        write(out / 'RECEIPT.json', receipt)
        print(json.dumps({k: receipt[k] for k in ['status', 'checks_passed', 'cases_completed', 'manufactured_coefficient_evaluations', 'wall_seconds', 'cpu_seconds', 'results_sha256', 'candidate_sha256']}, sort_keys=True))
    except BaseException as exc:
        signal.setitimer(signal.ITIMER_PROF, 0)
        write(out / 'PARTIAL_RESULTS.json', {'rows': rows, 'checks': checked})
        failure = {**state, 'status': 'FIRST_FAILURE_PRESERVED_NO_AUTOMATIC_RETRY', 'error': str(exc),
                   'traceback': traceback.format_exc(), 'cases_completed': len(rows),
                   'checks_completed': len(checked), 'wall_seconds': time.perf_counter() - start,
                   'cpu_seconds': time.process_time() - cpu_start}
        write(out / 'FIRST_FAILURE.json', failure)
        print(json.dumps({'status': failure['status'], 'error': str(exc), 'cases_completed': len(rows)}))
        raise


if __name__ == '__main__':
    main()
