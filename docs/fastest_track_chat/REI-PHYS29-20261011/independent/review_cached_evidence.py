#!/usr/bin/env python3
"""Distinct PHYS29 reviewer: file checks and arithmetic on retained values only.

Never imports, compiles for execution, calls or replays candidate/old programs.
No physical function, derivative, root or new toy is evaluated. Decimal80 merely
checks serialized predicates, coefficients and display sums with frozen scales.
"""
from pathlib import Path
from decimal import Decimal as D, getcontext
from fractions import Fraction
from datetime import datetime, timezone
import ast
import difflib
import hashlib
import json
import re
import stat
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name('STATIC_CACHED_REVIEW.json')
getcontext().prec = 80
CHECKS, READS = [], {}
ZERO, ONE = D(0), D(1)
S = {j: D('1e-64') / D(18)**j for j in range(5)}
TOL = D('1e-60')


def data(path):
    p = Path(path)
    p = p if p.is_absolute() else ROOT / p
    b = p.read_bytes()
    key = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    READS[key] = {'path': key, 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
                  'scope': 'actual byte read; semantic scope separately recorded in decision'}
    return b


def js(path):
    return json.loads(data(path))


def identity(path):
    b = data(path)
    return {'path': str(path), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def check(name, passed, **details):
    CHECKS.append({'name': name, 'pass': bool(passed), **details})


def close(name, actual, expected, scale=None):
    a, b = D(actual), D(expected)
    scale = max(ONE, abs(a), abs(b)) if scale is None else D(scale)
    err = abs(a-b) / scale
    check(name, err <= TOL, scaled_error=str(err), frozen_tolerance=str(TOL))


def check_manifest(name, manifest, count):
    check(name+'__count', len(manifest['files']) == count)
    check(name+'__unique_paths', len({r['path'] for r in manifest['files']}) == count)
    for row in manifest['files']:
        check(name+'__'+row['path'], identity(row['path']) == {k: row[k] for k in ('path', 'bytes', 'sha256')})


def expected_scale(name, a, b):
    if name.startswith('inherited_constant__'):
        return max(abs(a), abs(b))
    field = name.split('__')[-1]
    fields = {'sigma_cm2': D('1e-18'), 'k_s-4': S[0], 'k_prime_s-4_eV-1': S[1],
              'k_second_s-4_eV-2': S[2], 'response_s-4': S[0], 'B_s-4_eV-1': S[1],
              'C_s-4_eV-2': S[2], 'Fdd_s-4_eV-2': S[2], 'FdW_s-4_eV-3': S[3], 'FWW_s-4_eV-4': S[4]}
    if any(t in name for t in ('kernel_expression__', 'cached_PHYS28_consistency__', '__chain_vs_bivariate__')) and field in fields:
        return fields[field]
    special = {'stored_root_response_small': S[0], 'stored_PHYS26_residual_consistency': S[0],
        'PHYS28_residual_consistency': S[0], 'PHYS28_B_consistency': S[1], 'PHYS28_C_consistency': S[2],
        'V_second_independent_C_identity': S[2], 'band_average_weighted_ksecond': S[2],
        'mixed_compact_identity': S[3], 'WW_compact_identity': S[4], 'Fdd_decomposition': S[2],
        'root_first_coefficient_cancels': S[1], 'root_second_coefficient_cancels': S[2]}
    if field in special:
        return special[field]
    if '__off_root_numerator_identity__' in name:
        return {'00': S[0]*18*18, '10': S[0]*18, '01': S[0], '20': S[0], '11': S[1], '02': S[2]}[field]
    return max(ONE, abs(a), abs(b))


def review():
    base = js('evidence/CANDIDATE_FROZEN.json')
    add = js('evidence/CANDIDATE_ADDENDUM_FROZEN.json')
    check('candidate_manifest_identity', identity('evidence/CANDIDATE_FROZEN.json')['sha256'] == '59bd747a874b4749330860420895b0abf00418293b4ad87c777bdd723c3c000c')
    check('addendum_manifest_identity', identity('evidence/CANDIDATE_ADDENDUM_FROZEN.json')['sha256'] == 'be2b2b652b8152fb5e82f85b8addd4471256873a9ac4d1c8c2ca28ff328f788c')
    check_manifest('base_119', base, 119)
    check_manifest('addendum_5', add, 5)
    check('addendum_binds_original_manifest', add['base_candidate'] == identity('evidence/CANDIDATE_FROZEN.json'))
    correction = js('evidence/REPORT_CORRECTION.json')
    original = data(correction['original']['path']).decode()
    corrected = data(correction['reviewed']['path']).decode()
    notice = corrected.split('\n\n', 2)[1]
    check('corrected_report_notice_is_explicit', notice.startswith('> **검토 반영본.**') and '새 과학 실행은 없다' in notice)
    changed = original.replace(correction['old_wording'], correction['corrected_wording'])
    changed = re.sub(r'\]\(([^)]+)\)', lambda m: m.group(0) if m.group(1).startswith(('http://', 'https://', '#')) else ']('+ '../'+m.group(1)+')', changed)
    check('report_exact_narrow_transformation', original.count(correction['old_wording']) == 1 and corrected.replace(notice+'\n\n', '', 1) == changed)
    diff = ''.join(difflib.unified_diff(original.splitlines(True), corrected.splitlines(True), fromfile=correction['original']['path'], tofile=correction['reviewed']['path']))
    check('report_recorded_patch_exact', data(correction['diff']['path']).decode() == diff)
    for key in ('original', 'reviewed', 'diff', 'original_candidate_freeze'):
        check('report_correction_identity__'+key, identity(correction[key]['path']) == correction[key])

    raw = js('contributions/numerics/SECOND_ORDER_FIRST.json')
    replay = js('portability/REPLAY_RESULT.json')
    protocol = js('contributions/numerics/PROTOCOL.json')
    freeze = js('contributions/numerics/PREEXECUTION_FROZEN.json')
    pm = js('portability/PORTABLE_MANIFEST.json')
    first = js('contributions/numerics/EXECUTION.json')
    receipt = js('portability/REPLAY_RECEIPT.json')
    summary = js('report/PHYS29_RESULTS_SUMMARY.json')
    figure = js('figures/DISPLAY_RECEIPT.json')
    old26 = js('inputs/PHYS26/contributions/numerics/FIXED_VARIANCE_ENVELOPE_FIRST.json')
    old27 = js('inputs/PHYS27/contributions/numerics/FINITE_WIDTH_FIRST.json')
    old28 = js('inputs/PHYS28/contributions/numerics/SMALL_WIDTH_FIRST.json')
    jraw = js('inputs/PHYS22_INITIAL_COEFFICIENTS.json')
    source = js('SOURCE_MANIFEST.json')
    for name, manifest, n in [('protocol', protocol, 20), ('preexecution', freeze, 25), ('portable', pm, 26)]:
        rows = manifest.get('files', manifest.get('inputs'))
        check_manifest(name, {'files': rows}, n)
    frozen_paths = {v['path'] for v in freeze['files']}
    runtime_paths = {v['path'] for v in pm['files']}
    check('protocol_freeze_closure', {v['path'] for v in protocol['inputs']} < frozen_paths)
    check('freeze_runtime_exact_closure', runtime_paths == frozen_paths | {'contributions/numerics/PREEXECUTION_FROZEN.json'})
    for path, sha in raw['identity_sha256'].items():
        check('raw_input_identity__'+path, identity(path)['sha256'] == sha)
    check('raw_identity_exact_runtime_set', set(raw['identity_sha256']) == runtime_paths)
    check('raw_replay_bytes_equal', data('contributions/numerics/SECOND_ORDER_FIRST.json') == data('portability/REPLAY_RESULT.json'))
    check('raw_replay_json_equal', raw == replay)
    check('raw_first_summary_receipt_equal', raw['summary'] == first['summary_from_actual_raw'] == receipt['result_summary'])
    for section, keys in [(first, ('raw_result', 'stdout', 'stderr')), (receipt, ('archive', 'runner', 'first_result', 'stdout', 'stderr', 'result'))]:
        for key in keys:
            check('execution_identity__'+key+'__'+section.get('status', ''), identity(section[key]['path']) == section[key])
    utc = datetime.fromisoformat
    check('execution_order', utc(protocol['written_utc']) < utc(freeze['frozen_utc']) < utc(first['start_utc']) < utc(first['end_utc']) < utc(pm['frozen_utc']) < utc(receipt['started_utc']) < utc(receipt['ended_utc']) < utc(base['frozen_utc']) < utc(add['frozen_utc']))
    check('execution_success_records', first['exit_code'] == receipt['actual_exit_code'] == 0 and not first['timed_out'] and not receipt['timed_out'] and receipt['launch_error'] is None and first['stderr']['bytes'] == receipt['stderr']['bytes'] == 0)
    check('first_frozen_hashes_before_after', first['frozen_sha256_before'] == first['frozen_sha256_after'] == {k: identity('contributions/numerics/'+k)['sha256'] for k in first['frozen_sha256_before']})
    destination = Path(receipt['destination'])
    expected_members = runtime_paths | {'PORTABLE_MANIFEST.json'}
    with zipfile.ZipFile(ROOT/'portability/PHYS29_PORTABLE_STAGE.zip') as z:
        check('archive_exact_27_members', len(z.infolist()) == 27 and set(z.namelist()) == expected_members)
        check('existing_restore_exact_27_files', {str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file() or p.is_symlink()} == expected_members)
        for path in sorted(expected_members):
            archive_bytes = z.read(path)
            original_bytes = data('portability/PORTABLE_MANIFEST.json' if path == 'PORTABLE_MANIFEST.json' else path)
            restored = destination/path
            restored_bytes = data(restored)
            check('archive_restore__'+path, archive_bytes == original_bytes == restored_bytes and (z.getinfo(path).external_attr >> 16) == 0o100644 and stat.S_IFMT(restored.lstat().st_mode) == stat.S_IFREG and stat.S_IMODE(restored.lstat().st_mode) == 0o644 and not restored.is_symlink())
    for phase in ('preexecution_restore', 'postexecution_restore'):
        rec = receipt[phase]
        check(phase+'__scope', rec['all_pass'] and rec['runtime_payload_count'] == 26 and rec['total_files_including_manifest'] == 27 and rec['exact_member_set'] and rec['manifest_byte_equal'] and rec['manifest_mode_100644'])
        for row in rec['files']:
            actual = identity(row['path'])
            check(phase+'__'+row['path'], actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256'] and all(row[k] for k in ('size_equal', 'sha256_equal', 'archive_byte_equal', 'regular_file', 'mode_100644')))
    dep = receipt['preexecution_dependency_chain']
    check('replay_dependency_receipt', dep['all_pass'] and dep['protocol_input_count'] == 20 and dep['frozen_identity_count'] == 25 and dep['runtime_file_count'] == 26 and all(v['pass'] for v in dep['checks']))

    code = data('contributions/numerics/second_order_width.py').decode()
    tree = ast.parse(code)
    constants = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.startswith('EXPECTED_')}
    imports = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names})
    check('candidate_imports_only_read_stdlib', imports == sorted(['__future__', 'argparse', 'decimal', 'fractions', 'hashlib', 'json', 'math', 'pathlib', 'platform', 'traceback']))
    series = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'envelope_series')
    check('scalar_bivariate_does_not_call_chain', not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('law_chain', 'validate_branch') for n in ast.walk(series)))
    counts = raw['summary']['actual_counts']
    nonzero = {'program_main_invocations_this_process': 1, 'planned_unique_energy_nodes': 4, 'actual_unique_energy_nodes': 4,
        'primary_jet_joint_evaluations': 4, 'independent_scalar_joint_evaluations': 4, 'combined_kernel_derivative_joint_evaluations': 8,
        'k_component_outputs': 8, 'k_prime_component_outputs': 8, 'k_second_component_outputs': 8, 'combined_k_kprime_ksecond_component_outputs': 24, 'sigma_auxiliary_outputs': 8,
        'physical_chain_branch_evaluations_from_cached_values': 2, 'physical_series_branch_evaluations_from_cached_values': 2,
        'moment_series_evaluations_without_physical_kernel': 2, 'exact_rational_quadratic_toy_branches': 2,
        'exact_rational_quadratic_chain_evaluations': 2, 'exact_rational_quadratic_series_evaluations': 2}
    check('all_recorded_counts_exact', counts == {k: nonzero.get(k, 0) for k in counts} and counts == receipt['actual_counts'])
    check('summary_total_counter_arithmetic', summary['total_execution']['all_summed_process_counters'] == {k: v*2 for k,v in counts.items() if k not in ('planned_unique_energy_nodes','actual_unique_energy_nodes')})
    roots, fs = old26['inherited_boundary_residuals'], old27['threshold_comparison']
    booleans = {
        'contract_expected_sha256': identity('PHYSICS_CONTRACT.json')['sha256'] == constants['EXPECTED_CONTRACT'],
        'protocol_expected_sha256': identity('contributions/numerics/PROTOCOL.json')['sha256'] == constants['EXPECTED_PROTOCOL'],
        'PHYS26_root_strings_unchanged_in_PHYS27': roots['Vstar_eV2'] == fs['PHYS26_Vstar0_eV2'] and roots['W0_eV2'] == fs['PHYS26_W00_eV2'],
        'PHYS26_root_strings_unchanged_in_PHYS28': roots['Vstar_eV2'] == old28['constants']['PHYS26_root_strings_consumed_exactly']['W_star_zero_eV2'] and roots['W0_eV2'] == old28['constants']['PHYS26_root_strings_consumed_exactly']['W_zero_zero_eV2'],
        'finite_root_raw_records_equal_summary': all(old27['new_physical_roots'][a]['midpoint_physical_variance_eV2'] == fs[b] for a,b in [('W_star_delta','W_star_delta_eV2'),('W_0_delta','W_0_delta_eV2')]),
        'frozen_half_width_support_mean': D(old27['constants']['half_width_eV']) == D('.05') and list(map(D,old27['constants']['photon_support_eV'])) == [D('13.61'),D('24.58')] and D(old27['constants']['mean_eV']) == D(18),
        'analytic_HI_support': D.from_float(13.60) < D('13.61') < D(18) < D('24.58') < D.from_float(24.59),
        'source_manifest_identity': identity('SOURCE_MANIFEST.json')['sha256'] == next(v['sha256'] for v in protocol['inputs'] if v['path'] == 'SOURCE_MANIFEST.json'),
        'exactly_four_distinct_supported_nodes': len(set(raw['energy_nodes_eV'].values())) == 4 and all(D('13.61') <= D(v) <= D('24.58') for v in raw['energy_nodes_eV'].values()),
        'four_nodes_match_serialized_PHYS28': raw['energy_nodes_eV'] == old28['energy_nodes_eV'],
        'actual_joint_evaluation_counts_match_freeze': all(counts[k] == nonzero[k] for k in ('primary_jet_joint_evaluations','independent_scalar_joint_evaluations','combined_kernel_derivative_joint_evaluations')),
        'actual_separate_component_output_counts': all(counts[k] == nonzero[k] for k in ('k_component_outputs','k_prime_component_outputs','k_second_component_outputs','combined_k_kprime_ksecond_component_outputs')),
        'actual_cached_and_exact_toy_counts': all(counts[k] == v for k,v in nonzero.items() if v == 2),
        'forbidden_execution_counts_zero': all(v == 0 for k,v in counts.items() if k not in nonzero),
    }
    for name, old in [('PHYS26',old26),('PHYS27',old27),('PHYS28',old28)]: booleans['inherited_'+name+'_all_pass'] = old['summary']['all_pass']
    for row in freeze['files']: booleans['frozen_identity__'+row['path']] = identity(row['path']) == row
    for branch, vals in raw['second_order']['jet_chain'].items():
        law, comp = vals['law'], raw['delta_005_comparison'][branch]
        booleans[branch+'__positive_simple_variance_slope'] = D(vals['C_s-4_eV-2']) > 0
        booleans[branch+'__supported_positive_law'] = ZERO < D(law['stored_W_eV2']) < D('4.39')*D('6.58') and D('13.61') <= D(law['center_eV']) <= D('24.58') and ZERO < D(law['p_endpoint']) < ONE and ZERO < D(law['p_center']) < ONE
        booleans[branch+'__comparison_nonzero_observed_denominators'] = D(comp['actual_shift_at_delta_005_eV2']) != 0 and D(comp['linear_residual_from_PHYS28_eV2']) != 0
    covered, categories = set(), {'scaled':0, 'exact_fraction':0, 'boolean_or_identity':0}
    for row in raw['checks']:
        name = row['name']
        covered.add(name)
        if 'scaled_error' in row:
            categories['scaled'] += 1
            a,b,scale,tol = map(D,(row['actual'],row['expected'],row['scale'],row['tolerance']))
            residual, error = a-b, abs(a-b)/scale
            check('cached_predicate__'+name, row['pass'] is True and residual == D(row['residual']) and error == D(row['scaled_error']) and error <= tol and tol == (D('1e-65') if name.endswith('__stored_root_response_small') else TOL) and scale == expected_scale(name,a,b))
        elif 'actual' in row:
            categories['exact_fraction'] += 1
            check('cached_predicate__'+name, row['pass'] is True and Fraction(str(row['actual'])) == Fraction(str(row['expected'])))
        else:
            categories['boolean_or_identity'] += 1
            check('cached_predicate__'+name, row['pass'] is True and booleans.get(name) is True, independently_resolved=name in booleans)
    check('all_238_predicates_covered', len(covered) == len(raw['checks']) == 238 and categories == {'scaled':152,'exact_fraction':38,'boolean_or_identity':48} and set(booleans) <= covered)
    check('raw_summary_238', raw['summary']['total_checks'] == raw['summary']['passed'] == 238 and raw['summary']['failed'] == 0 and raw['summary']['failed_names'] == [] and raw['summary']['all_pass'])
    for kind, key in [('kernel_expression__','maximum_scaled_kernel_expression_error'),('__chain_vs_bivariate__','maximum_scaled_independent_envelope_error')]:
        check('observed_maximum__'+key, max(D(v['scaled_error']) for v in raw['checks'] if kind in v['name']) == D(raw[key]) and raw[key] == summary[key])
    check('J_exact_serialized_inputs', [raw['constants']['J_h2_x'],raw['constants']['J_h2_w']] == [jraw['results']['baseline_local']['J_nonphoto'][2][i] for i in (0,3)])
    for rel, row in source['files'].items():
        b = data('inputs/pinned_source/'+rel)
        blob = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        check('local_source_git_blob__'+rel, blob == row['git_blob'] and len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256'] and row['git_mode'] == '100644')
    check('summary_primary_exact_transcription', summary['primary_second_order'] == raw['second_order']['jet_chain'])
    check('summary_diagnostic_exact_transcription', summary['delta_005_comparison'] == raw['delta_005_comparison'])
    check('summary_first_exact_transcription', summary['first_summary'] == raw['summary'])
    diagnostic = {}
    for branch, vals in raw['second_order']['jet_chain'].items():
        c,C,K,M,N,d = [D(vals[k]) for k in ('c_eV','C_s-4_eV-2','Fdd_s-4_eV-2','FdW_s-4_eV-3','FWW_s-4_eV-4','d_dimensionless')]
        close(branch+'__cached_d_formula', d, -(K+2*M*c+N*c*c)/(2*C))
        close(branch+'__cached_K_sum', sum(map(D, vals['Fdd_decomposition_s-4_eV-2'].values()),ZERO), K,S[2])
        terms = {k:D(v) for k,v in vals['d_decomposition_dimensionless'].items()}
        close(branch+'__cached_d_sum', sum(terms.values(),ZERO),d)
        for k,v in vals['Fdd_decomposition_s-4_eV-2'].items(): close(branch+'__cached_term_factor__'+k, terms[k],-D(v)/(2*C))
        close(branch+'__cached_implicit_mixed',terms['implicit_root_delta_W_cross'],-M*c/C)
        close(branch+'__cached_implicit_curvature',terms['implicit_root_W_curvature'],-N*c*c/(2*C))
        sec = raw['second_order']['scalar_bivariate'][branch]
        for field,mono,factor,j in [('response_s-4','(0, 0)',1,0),('B_s-4_eV-1','(1, 0)',1,1),('C_s-4_eV-2','(0, 1)',1,2),('Fdd_s-4_eV-2','(2, 0)',2,2),('FdW_s-4_eV-3','(1, 1)',1,3),('FWW_s-4_eV-4','(0, 2)',2,4)]:
            close(branch+'__series_factor__'+field,sec[field],D(sec['response_ordinary_series'][mono])*factor,S[j])
        toy = raw['exact_quadratic_toys'][branch]
        truth = {k:(1 if k == 'C_s-4_eV-2' else 0) for k in toy['chain_coefficients']}
        check(branch+'__cached_exact_toy_coefficients', all(Fraction(v) == truth[k] for p in ('chain_coefficients','series_coefficients') for k,v in toy[p].items()))
        check(branch+'__cached_exact_toy_d_sum',sum(map(Fraction,toy['d_decomposition'].values()),Fraction(0)) == 0 and Fraction(toy['d_decomposition']['uniform_band_averaging']) == Fraction(-1,3) and Fraction(toy['d_decomposition']['center_variance_V_second']) == Fraction(1,3))
        geometry = sum((v for k,v in terms.items() if k not in ('uniform_band_averaging','center_variance_V_second','implicit_root_delta_W_cross','implicit_root_W_curvature')),ZERO)
        groups = [terms['uniform_band_averaging'],terms['center_variance_V_second'],geometry,terms['implicit_root_delta_W_cross'],terms['implicit_root_W_curvature'],d]
        check(branch+'__figure_cached_groups',groups == list(map(D,figure['display_groups'][branch])))
        comp = raw['delta_005_comparison'][branch]
        old = old28['delta_005_comparison'][branch]
        check(branch+'__comparison_old_linear_kept', comp['linear_shift_from_PHYS28_eV2'] == old['linear_shift_at_delta_005_eV2'] and comp['serialized_PHYS28_c_eV'] == old['coefficient_c_eV'])
        inc = d*D('.05')*D('.05')
        linear, residual = D(comp['linear_shift_from_PHYS28_eV2']), D(comp['linear_residual_from_PHYS28_eV2'])
        new_residual = residual-inc
        check(branch+'__comparison_arithmetic_exact', inc == D(comp['quadratic_increment_d_delta_squared_eV2']) and linear+inc == D(comp['quadratic_predicted_shift_eV2']) and new_residual == D(comp['residual_actual_minus_quadratic_eV2']) and inc/residual == D(comp['signed_fraction_of_linear_residual_accounted_for']) and 100*abs(new_residual/D(comp['actual_shift_at_delta_005_eV2'])) == D(comp['absolute_quadratic_residual_relative_to_actual_shift_percent']))
        diagnostic[branch] = {'d':str(d),'residual_eV2':str(new_residual),'geometry_group':str(geometry)}
    check('figure_identity',identity('figures/'+figure['figure'])['sha256'] == figure['figure_sha256'] and figure['raw_sha256'] == identity('contributions/numerics/SECOND_ORDER_FIRST.json')['sha256'])
    co = raw['delta_005_comparison']['coexistence_width']
    du,dl = [D(diagnostic[k]['d']) for k in ('upper_root','lower_root')]
    close('cached_gap_coefficient',co['width_second_order_coefficient_dimensionless'],dl-du)
    close('cached_gap_residual',co['residual_actual_minus_quadratic_reduction_eV2'],D(diagnostic['upper_root']['residual_eV2'])-D(diagnostic['lower_root']['residual_eV2']))
    check('lower_overshoot_observed',D(raw['delta_005_comparison']['lower_root']['linear_residual_from_PHYS28_eV2']) < 0 < D(diagnostic['lower_root']['residual_eV2']) and D(raw['delta_005_comparison']['lower_root']['signed_fraction_of_linear_residual_accounted_for']) > 1)
    # Final base/addendum identity check; no candidate payload has been written.
    check_manifest('end_base_119',base,119)
    check_manifest('end_addendum_5',add,5)
    return {'cached_predicate_categories':categories,'observed_values':diagnostic,'candidate_imports_from_static_AST':imports}


if __name__ == '__main__':
    if OUT.exists():
        raise SystemExit('Refuse to overwrite a retained reviewer result')
    started = datetime.now(timezone.utc).isoformat()
    exception, extra = None, {}
    try:
        extra = review()
    except Exception:
        exception = traceback.format_exc()
    failed = [v['name'] for v in CHECKS if not v['pass']]
    result = {'task':'REI-PHYS29-20261011','reviewer':'/root/phys29_decision','NONBLIND':True,
        'started_utc':started,'ended_utc':datetime.now(timezone.utc).isoformat(),
        'status':'STATIC_CACHED_CHECKS_PASS' if not failed and not exception else 'STATIC_CACHED_CHECKS_FAILED',
        'script':identity(Path(__file__)),'checks':CHECKS,'failed_checks':failed,'exception':exception,
        'summary':{'checks':len(CHECKS),'passed':len(CHECKS)-len(failed),'failed':len(failed)},
        'actual_byte_reads':list(READS.values()),'cached_arithmetic_decimal_precision':80,
        'scientific_execution_counts':{'candidate_or_old_imports':0,'scientific_mains':0,'physical_kernel_evaluations':0,'physical_derivative_evaluations':0,'physical_roots_or_refinement':0,'new_toy_evaluations':0,'replays':0,'native':0,'gas_IVP':0,'quadrature':0,'finite_differences':0,'derivative_certificate_campaign':0},
        'limits':['Cached-value arithmetic and file consistency only. No new independent physical evidence.','Existing restoration inspected; no new restoration or program execution.','Historical execution counts are assessed from retained records and static program reading, not OS-wide tracing.'],**extra}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'summary':result['summary'],'failed_checks':failed,'exception':exception,'output':identity(OUT)},ensure_ascii=False))
    raise SystemExit(0 if result['status'] == 'STATIC_CACHED_CHECKS_PASS' else 1)
