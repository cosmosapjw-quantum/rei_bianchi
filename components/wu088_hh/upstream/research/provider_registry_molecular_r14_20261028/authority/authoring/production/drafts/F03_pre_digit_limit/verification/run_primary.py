"""R14 frozen primary campaign; root alone authorizes its single process run.

All valid cases execute once. Analytic controls are independently hand-derived
and fixed in CASES.json. Every failed check/error is retained. No predecessor
runner is invoked. The external root wrapper measures full-process resources.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
LEAF = HERE.parent
sys.path.insert(0, str(LEAF / 'src'))
from quadratic_convolution import DomainError, derived, exact, precharge_work, run_case, serializable


def _surd_ge(value, a, b, radicand):
    """Exact value >= a+b*sqrt(radicand), for these fixed b>=0 controls."""
    if not b:
        return value >= a
    z = value - a
    return z >= 0 and z * z >= b * b * radicand


def _surd_le(value, a, b, radicand):
    if not b:
        return value <= a
    z = value - a
    return z <= 0 or z * z <= b * b * radicand


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=LEAF)
    parser.add_argument('--cases', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.root.resolve() != LEAF:
        parser.error('--root must match this frozen runner leaf')
    args.cases = args.cases or args.root / 'verification' / 'CASES.json'
    args.output = args.output or args.root / 'raw' / 'PRIMARY_RESULTS.json'
    if args.output.exists():
        parser.error('Output already exists; frozen results cannot be overwritten')
    started = time.process_time()
    fixtures = json.loads(args.cases.read_text())
    checks, records, by_id = [], [], {}

    def check(ident, passed, detail=None):
        row = {'id': ident, 'status': 'PASS' if bool(passed) else 'FAIL'}
        if detail is not None:
            row['detail'] = serializable(detail)
        checks.append(row)

    source_path = HERE / 'FIXTURE_SOURCE.json'
    source_bytes = source_path.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    source = json.loads(source_bytes)
    source_cases = {row['id']: row for row in source['cases']}
    source_fields = ('id', 'states', 'q', 'tau', 'c', 'd', 'initial', 'source_knots', 'observation_knots', 'g_r', 'g_e')
    check('actual_fixture_source_bytes_bound', all(case[key]['source_sha256'] == source_sha
          for case in fixtures['cases'] for key in ('binding', 'certificate')))
    check('original_forcing_hashes_bound', all(case[key]['whole_forcing_source_sha256']
          == source['whole_forcing_identities'][case['id']]
          for case in fixtures['cases'] for key in ('binding', 'certificate')))
    check('original_fixture_payload_identity', len(source_cases) == len(fixtures['cases'])
          and all(source_cases[case['id']] == {key: case[key] for key in source_fields} for case in fixtures['cases']))
    check('explicit_synthetic_premises', source['scientific_status'] == 'ARITHMETIC_CONTROL_PREMISE'
          and all(case[key]['scientific_status'] == 'ARITHMETIC_CONTROL_PREMISE'
                  for case in fixtures['cases'] for key in ('binding', 'certificate')))

    for case in fixtures['cases']:
        ident = case['id']
        try:
            result = run_case(case)
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc)}
            records.append({'id': ident, 'input': case, 'result': None, 'execution_error': error})
            check(ident + ':execution', False, error)
            continue
        records.append({'id': ident, 'input': case, 'result': result})
        by_id[ident] = result
        check(ident + ':execution', True)
        raw, exact_rows = result['raw'], result['exact']
        cells, weights, work = exact_rows['R_cubic_cells'], result['weights'], result['work']
        lo, hi = raw['refined_endpoints_lower'], raw['refined_endpoints_upper']
        wlo, whi = raw['refined_whole_cells_lower'], raw['refined_whole_cells_upper']
        check(ident + ':point_nonnegative_enclosures', all(0 <= a[j] <= b[j] for a, b in zip(lo, hi) for j in range(2)))
        check(ident + ':whole_interval_and_closed_endpoints',
              all(0 <= lower[j] <= upper[j] and upper[j] >= max(hi[i][j], hi[i + 1][j])
                  for i, (lower, upper) in enumerate(zip(wlo, whi)) for j in range(2)))
        check(ident + ':positive_effective_quadratic_coefficients',
              all(value >= 0 for key in ('g_r', 'g_e') for row in result['effective_source'][key] for value in row))
        check(ident + ':positive_cubic_overlap_and_forcing',
              all(value >= 0 for cell in cells for key in ('bernstein', 'F_bernstein', 'forcing_bernstein') for value in cell[key]))
        check(ident + ':actual_endpoint_and_left_limit_binding',
              all(cell['bernstein'][0] == exact_rows['R_at_refined'][i]
                  and cell['bernstein'][3] == cell['right_left_limit']
                  and cell['actual_right_endpoint'] == exact_rows['R_at_refined'][i + 1]
                  and cell['right_left_limit'] >= cell['actual_right_endpoint']
                  and whi[i][0] >= cell['right_left_limit'] for i, cell in enumerate(cells)))
        check(ident + ':global_F_continuity',
              all(cell['F_bernstein'][0] == exact_rows['F_at_refined'][i]
                  and cell['F_bernstein'][-1] == exact_rows['F_at_refined'][i + 1] for i, cell in enumerate(cells)))
        check(ident + ':certified_root_boxes',
              all(0 <= box['lo'] < box['hi'] <= 1
                  and box['hi'] - box['lo'] <= Fraction(1, 1 << 96)
                  and box['derivative_at_lo'] * box['derivative_at_hi'] < 0
                  and box['iterations'] == 96 for cell in cells for box in cell['critical']['root_boxes']))
        check(ident + ':finite_supremum_gaps',
              all(0 <= cell['supremum']['exact_gap'] == cell['supremum']['exact_upper'] - cell['supremum']['exact_lower']
                  <= cell['supremum']['proved_gap_bound'] == cell['supremum']['M_B'] / (1 << 96)
                  <= 3 * cell['supremum']['Cmax'] / (1 << 96)
                  and cell['supremum']['dyadic_lower'] <= cell['supremum']['exact_lower']
                  and cell['supremum']['dyadic_upper'] >= cell['supremum']['exact_upper']
                  and cell['supremum']['dyadic_upper'] - cell['supremum']['dyadic_lower']
                  <= cell['supremum']['proved_gap_bound'] + Fraction(2, 1 << 128) for cell in cells))
        check(ident + ':positive_weight_intervals',
              all(0 <= row[key][0] <= row[key][1] for row in weights for key in ('exp', 'W0', 'W1', 'W2', 'W3', 'phi')))
        check(ident + ':phi_is_sum_of_four_weights',
              all(row['phi'] == (sum(row['W' + str(i)][0] for i in range(4)),
                                 sum(row['W' + str(i)][1] for i in range(4))) for row in weights))
        check(ident + ':full_work_precharge',
              work['guard_applied_before_overlap'] and work['guard_applied_before_root_isolation']
              and work['overlap_terms_actual'] == work['overlap_terms_upper']
              == work['base_cells'] * work['effective_source_cells'] * (work['full_blocks'] + 1) <= 250000
              and work['root_bisections_actual'] <= work['root_bisections_upper'] == 192 * work['base_cells'] <= 98304
              and work['coefficient_cell_builds'] == work['base_cells'])
        check(ident + ':history_scope_and_rational_clock',
              result['R_history'] == 'GLOBAL_FROM_ORIGINAL_T0' and result['cap_application'] == 'NONE'
              and result['base_times'] == result['refined_times']
              and result['arithmetic']['root_boxes_are_propagation_clocks'] is False)
        check(ident + ':observation_coverage',
              set(result['requested_times']).issubset(set(result['base_times']))
              and len(raw['whole_cells_upper']) + 1 == len(result['requested_times']))
        if Fraction(case['d']) == 0:
            check(ident + ':zero_d_beta_integral_reduction',
                  all(row['exp'] == (Fraction(1), Fraction(1))
                      and all(row[key][0] <= (row['right'] - row['left']) / 4 <= row[key][1]
                              for key in ('W0', 'W1', 'W2', 'W3'))
                      and row['phi'][0] <= row['right'] - row['left'] <= row['phi'][1] for row in weights))
        controls = case.get('controls', {})
        endpoint = controls.get('endpoint', {})
        if 'R' in endpoint:
            check(ident + ':analytic_endpoint_R', raw['endpoints_lower'][-1][0] == Fraction(endpoint['R']),
                  {'expected': endpoint['R'], 'actual': raw['endpoints_lower'][-1][0]})
        if 'E' in endpoint:
            check(ident + ':analytic_endpoint_E', raw['endpoints_lower'][-1][1] <= Fraction(endpoint['E']) <= raw['endpoints_upper'][-1][1],
                  {'expected': endpoint['E'], 'lower': raw['endpoints_lower'][-1][1], 'upper': raw['endpoints_upper'][-1][1]})
        if controls.get('all_zero'):
            check(ident + ':zero_invariant', all(value == 0 for group in (lo, hi, wlo, whi) for row in group for value in row))
        if 'source_vertex_times' in controls:
            check(ident + ':exact_source_vertices', result['effective_source']['source_vertex_times']
                  == [Fraction(x) for x in controls['source_vertex_times']])
        for key in ('effective_source_cells', 'original_source_cells', 'full_blocks'):
            if key in controls:
                check(ident + ':declared_capacity:' + key, work[key] == controls[key])
        if 'observation_cells' in controls:
            check(ident + ':declared_observation_capacity', len(result['requested_times']) - 1 == controls['observation_cells'])
        if 'F_final' in controls:
            check(ident + ':analytic_global_memory_F', exact_rows['F_at_refined'][-1] == Fraction(controls['F_final']))
        if 'right_left_limit' in controls:
            check(ident + ':unattained_left_limit_distinct_from_actual_endpoint',
                  cells[-1]['right_left_limit'] == Fraction(controls['right_left_limit'])
                  and cells[-1]['right_left_limit'] > cells[-1]['actual_right_endpoint'])
        if 'whole_R_sup' in controls:
            control = controls['whole_R_sup']
            sup = exact_rows['observation_R_suprema'][control['observation_cell']]
            a = Fraction(control['rational'])
            b, radicand = Fraction(control.get('sqrt_coefficient', '0')), Fraction(control.get('radicand', '0'))
            check(ident + ':analytic_closed_cell_supremum',
                  _surd_le(sup['exact_lower'], a, b, radicand) and _surd_ge(sup['exact_upper'], a, b, radicand),
                  {'control': control, 'actual_exact_lower': sup['exact_lower'], 'actual_exact_upper': sup['exact_upper']})
        if 'critical_cell' in controls:
            control = controls['critical_cell']
            matched = [cell for cell in cells if cell['left'] == Fraction(control['left']) and cell['right'] == Fraction(control['right'])]
            check(ident + ':critical_control_cell_exists', len(matched) == 1)
            if matched:
                row = matched[0]
                check(ident + ':analytic_critical_count', len(row['critical']['root_boxes']) == control['root_boxes'])
                expected = [{**r, 'x': Fraction(r['x'])} for r in control['exact_roots']]
                check(ident + ':analytic_exact_critical_roots', row['critical']['exact_roots'] == expected)
                if 'bernstein' in control:
                    check(ident + ':analytic_cubic_coefficients', row['bernstein'] == [Fraction(x) for x in control['bernstein']])
                if 'M_B' in control:
                    check(ident + ':analytic_derivative_bound', row['supremum']['M_B'] == Fraction(control['M_B']))
                if 'constant_polynomial' in control:
                    check(ident + ':constant_derivative_classification', row['critical']['constant_polynomial'] is True and row['critical']['degree'] == -1)

    for case in fixtures['cases']:
        for relation in case.get('relations', []):
            ident = case['id'] + ':relation:' + relation['kind']
            left, right = by_id.get(case['id']), by_id.get(relation['other'])
            if left is None or right is None:
                check(ident, False, 'A relation case failed to execute')
                continue
            il = {t: i for i, t in enumerate(left['requested_times'])}
            ir = {t: i for i, t in enumerate(right['requested_times'])}
            common = sorted(set(il) & set(ir))
            check(ident + ':exact_R', bool(common) and all(left['raw']['endpoints_lower'][il[t]][0]
                  == right['raw']['endpoints_lower'][ir[t]][0] for t in common))
            check(ident + ':ideal_E_intervals_overlap', bool(common) and all(
                  max(left['raw']['endpoints_lower'][il[t]][1], right['raw']['endpoints_lower'][ir[t]][1])
                  <= min(left['raw']['endpoints_upper'][il[t]][1], right['raw']['endpoints_upper'][ir[t]][1]) for t in common))
    case_inputs = {case['id']: case for case in fixtures['cases']}
    for relation in fixtures.get('relations', []):
        ident = relation['left'] + ':compared_to:' + relation['right']
        left, right = by_id.get(relation['left']), by_id.get(relation['right'])
        if left is None or right is None:
            check(ident, False, 'A comparison case failed to execute')
            continue
        check(ident + ':endpoint_R_order', left['raw']['endpoints_lower'][-1][0] <= right['raw']['endpoints_lower'][-1][0])
        check(ident + ':endpoint_E_order_compatible', left['raw']['endpoints_lower'][-1][1] <= right['raw']['endpoints_upper'][-1][1])
        for component in ('R', 'E'):
            a = Fraction(case_inputs[relation['left']]['controls']['endpoint'][component])
            b = Fraction(case_inputs[relation['right']]['controls']['endpoint'][component])
            check(ident + ':analytic_ideal_relative_reduction_' + component,
                  b != 0 and (b - a) / b == Fraction(relation['endpoint_' + component + '_relative_reduction']),
                  'Analytic conditional comparison ratio; not a physical accuracy or measured speedup claim.')

    guard_results = []
    baseline = case_inputs[fixtures['guard_basis_case']]
    for guard in fixtures['guards']:
        error, error_class = None, None
        try:
            operation = guard.get('operation')
            if operation == 'derived_scalar_power_of_two':
                derived(1 << guard['exponent'])
            elif operation == 'input_scalar_power_of_two':
                exact(1 << guard['exponent'])
            elif operation == 'work_budget':
                precharge_work(*guard['counts'])
            elif operation in ('source_count', 'observation_count'):
                invalid = deepcopy(baseline)
                invalid['source_knots' if operation == 'source_count' else 'observation_knots'] = list(range(guard['cells'] + 1))
                run_case(invalid)
            else:
                run_case(guard['input'])
        except Exception as exc:
            error, error_class = str(exc), type(exc).__name__
        passed = error_class == 'DomainError' and guard['expected_error_substring'] in error
        row = {'id': guard['id'], 'expected_error_substring': guard['expected_error_substring'],
               'observed_error_class': error_class, 'observed_error': error,
               'status': 'PASS' if passed else 'FAIL',
               'guard_scope': 'DIRECT_FINITE_WORK_BUDGET_HELPER_NOT_ACCEPTED_DOMAIN_EXECUTION' if guard.get('operation') == 'work_budget' else 'INPUT_OR_SCALAR_REJECTION'}
        guard_results.append(row)
        check('guard:' + guard['id'], passed, row)
    check('input_scalar_256bit_boundary_accepted', exact(1 << 255).numerator.bit_length() == 256)
    check('derived_scalar_16384bit_boundary_accepted', derived(1 << 16383).numerator.bit_length() == 16384)
    check('direct_full_work_budget_arithmetic', precharge_work(512, 48, 8) == (221184, 98304),
          'Direct finite work-budget helper check; does not claim a realizable 512-base-cell fixture.')
    passed = sum(row['status'] == 'PASS' for row in checks)
    failed = len(checks) - passed
    identities = {}
    for path in (Path(__file__), args.cases, source_path, HERE / 'FIXTURE_DEFINITIONS.json', LEAF / 'src' / 'quadratic_convolution.py', LEAF / 'src' / 'cli.py'):
        identities[str(path.relative_to(LEAF)) if path.is_relative_to(LEAF) else str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    output = {'schema': 'WU_R14_PRIMARY_RESULTS_V1', 'status': 'PASS_SCOPED' if not failed else 'FAIL',
              'cases': records, 'checks': checks, 'guards': guard_results,
              'summary': {'valid_cases': len(fixtures['cases']), 'valid_case_executions_completed': len(by_id),
                          'guard_cases': len(guard_results), 'checks': len(checks), 'passed': passed, 'failed': failed},
              'execution': {'primary_process_runs': 1, 'old_science_or_ODE_replay': 0,
                            'internal_runner_CPU_s': time.process_time() - started,
                            'CPU_scope': 'runner body; root wrapper measures full process including imports and serialization'},
              'input_and_code_sha256': identities,
              'scope': 'Synthetic conditional quadratic comparison. Physical source remains INPUT_PENDING. No generic caps or physical admission.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(serializable(output), ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': output['status'], **output['summary'], 'output': str(args.output)}, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == '__main__':
    raise SystemExit(main())
