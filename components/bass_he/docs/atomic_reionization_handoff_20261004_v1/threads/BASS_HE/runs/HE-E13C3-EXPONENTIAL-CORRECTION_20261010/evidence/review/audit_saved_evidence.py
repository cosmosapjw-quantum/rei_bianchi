"""Independent saved-output review arithmetic; imports no candidate solver."""
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal as D, getcontext
import hashlib
import json
import os
from pathlib import Path
import tempfile

getcontext().prec = 70
ROOT = Path('/workspace/scratch/7fd51143e473/BASS_HE_E13C3_EXPONENTIAL_CORRECTION_20261010_v1')
OUT = Path(__file__).resolve().parent
CHECKS = []
IDENTITIES = {}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(rel):
    p = ROOT / rel
    IDENTITIES[rel] = {'sha256': sha(p), 'bytes': p.stat().st_size}
    return json.loads(p.read_text())


def check(name, condition, observed=None):
    CHECKS.append({'name': name, 'pass': bool(condition), 'observed': observed})


def dec(x):
    return D.from_float(x) if isinstance(x, float) else D(x)


def atomic(path, obj):
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
        f.write('\n'); f.flush(); os.fsync(f.fileno()); temp = f.name
    os.replace(temp, path)


def attribute_calls(rel, names):
    p = ROOT / rel
    IDENTITIES[rel] = {'sha256': sha(p), 'bytes': p.stat().st_size}
    tree = ast.parse(p.read_text())
    return sorted({ast.unparse(n.func) for n in ast.walk(tree)
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and isinstance(n.func.value, ast.Name) and n.func.value.id in names})


def main():
    plan = read('PLAN.json')
    manifest = read('inputs/INPUT_MANIFEST.json')
    check('exactly_34_unique_pinned_inputs', len(manifest) == 34 and len({x['path'] for x in manifest}) == 34)
    for item in manifest:
        p = ROOT / item['path']
        check('input_identity:' + item['path'], sha(p) == item['sha256'] and p.stat().st_size == item['bytes'])
    calls = attribute_calls('code/exponential_correction.py', {'model', 'batch'})
    check('primary_only_named_physical_helpers', calls == ['batch.coeff', 'batch.frozen_stock', 'model.SegmentBatch', 'model.lift', 'model.projection', 'model.read_csv'], calls)
    calls_dec = attribute_calls('evidence/decimal/decimal_first_variation.py', {'helper'})
    check('decimal_only_named_shared_helpers', calls_dec == ['helper.Coefficients', 'helper.gauss_rule'], calls_dec)
    prod = sha(ROOT / 'code/exponential_correction.py')
    helper = sha(ROOT / 'inputs/e13c2/code/continuous_defect.py')
    manifest_sha = sha(ROOT / 'inputs/INPUT_MANIFEST.json')
    for label, order, stage in [('local_gl8', 8, 'local'), ('local_gl12', 12, 'local'), ('paths_gl8', 8, 'paths'), ('paths_gl12', 12, 'paths')]:
        result = read(f'evidence/{label}/RESULTS.json')
        started = read(f'evidence/{label}/RUN_STARTED.json')
        check(label + ':as_run_identity', result['producer_sha256'] == started['producer_sha256'] == prod
              and result['coefficient_helper_sha256'] == started['coefficient_helper_sha256'] == helper
              and result['input_manifest_sha256'] == started['input_manifest_sha256'] == manifest_sha)
        check(label + ':actual_order_stage_precision', result['order'] == started['order'] == order and result['stage'] == stage
              and result['longdouble_significand_bits'] >= 64 and result['execution_status'] == 'COMPLETED_NEW_CORRECTION_ONLY')
        groups = result['segment_groups'] if stage == 'paths' else [r['meta'] for r in result['local_controls']]
        check(label + ':coefficient_samples_consistent', all(g['order'] == order and g['physical_coefficient_samples'] == order*g['segments'] for g in groups)
              and sum(g['physical_coefficient_samples'] for g in groups) == result['physical_coefficient_samples'])
        check(label + ':nonnegative_endpoints_and_numerical_ledgers', min(g['min_corrected_photon_endpoint'] for g in groups) >= 0
              and max(g['max_number_first_variation_ledger'] for g in groups) <= plan['acceptance']['first_variation_number_ledger_absolute']
              and max(g['max_energy_first_variation_ledger_eV'] for g in groups) <= plan['acceptance']['first_variation_energy_ledger_eV_absolute'])
    for label, count in [('LOCAL_ACCEPTANCE', 104), ('FINAL_ACCEPTANCE', 136)]:
        packet = read(f'evidence/{label}.json')
        check(label + ':all_explicit_checks_wired_and_pass', packet['check_count'] == len(packet['checks']) == count
              and all(c['pass'] for c in packet['checks']) and packet['failed'] == [] and packet['verdict'] == 'PASS_SCOPED')
        check(label + ':verifier_code_as_run', packet['producer_sha256'] == sha(ROOT / 'code/verify_correction.py'))
        for rel, expected in packet['read_file_sha256'].items():
            check(label + ':read_identity:' + rel, sha(ROOT / rel) == expected)
    theory = read('evidence/theory/THEORY_CHECKS.json')
    kernel = read('evidence/KERNEL_CHECKS.json')
    decimal = read('evidence/decimal/DECIMAL_RESULTS.json')
    check('317_actual_theory_checks', theory['total_checks'] == theory['passed'] == len(theory['checks']) == 317
          and theory['failed'] == 0 and all(c['status'] == 'PASS' for c in theory['checks'])
          and theory['script_sha256'] == sha(ROOT / 'evidence/theory/check_theory_e13c3.py'))
    check('64_actual_primary_kernel_checks', kernel['total'] == kernel['passed'] == len(kernel['checks']) == 64
          and all(c['pass'] for c in kernel['checks']) and kernel['tested_code_sha256'] == prod
          and kernel['producer_sha256'] == sha(ROOT / 'code/kernel_checks.py'))
    check('decimal_nested_checks_not_only_summary', all(all(r['checks'].values()) for r in decimal['results'])
          and all(decimal['analytic_limit_checks'].values()) and all(c['pass'] for c in decimal['quadrature_rule_checks'].values())
          and all(decimal['input_checks'].values()) and not decimal['numerical_failures'] and not decimal['research_diagnostic_failures'])
    check('decimal_saved_ledger_numeric_tolerances', max(abs(dec(v['number_ledger'])) for r in decimal['results'] for v in r['calculated_by_degree'].values()) <= D('1e-45')
          and max(abs(dec(v['energy_ledger_eV'])) for r in decimal['results'] for v in r['calculated_by_degree'].values()) <= D('1e-45'))
    new = read('evidence/paths_gl12/RESULTS.json')
    coarse = read('evidence/paths_gl8/RESULTS.json')
    saved = read('inputs/e13c2/evidence/defect_rtol_2e11/RESULTS.json')
    saved_map = {(r['mode'], r['step']): r for r in saved['records']}
    coarse_map = {(r['mode'], r['step']): r for r in coarse['records']}
    nodes = read('evidence/paths_gl12/NODE_CORRECTIONS.json')
    check('14640_unique_saved_node_rows', len(nodes) == len({(x['mode'], x['step'], x['node']) for x in nodes}) == 14640)
    check('2440_nodes_per_macro', set(Counter((x['mode'],x['step']) for x in nodes).values()) == {2440})
    sums = defaultdict(lambda: [D(0)]*16)
    magnitude = defaultdict(lambda: [D(0)]*16)
    for n in nodes:
        key = (n['mode'], n['step']); weight = dec(n['weight'])
        for i, value in enumerate(n['defect']):
            term = weight * dec(value)
            sums[key][i] += term; magnitude[key][i] += abs(term)
    macro = []
    chi = list(map(dec, (13.598434599702,24.587389011,54.41776)))
    for row in new['records']:
        key = (row['mode'], row['step']); v = sums[key]; mag = magnitude[key]
        serialized = [row['delta_P'], *row['direct_A'], *row['response_A'], *row['direct_B_eV'], *row['response_B_eV'],
                      row['delta_redshift_eV'], row['delta_source_number'], row['delta_source_energy_eV']]
        gaps = [abs(dec(x)-y) for x,y in zip(serialized,v)]
        # A deliberately conservative arithmetic serialization allowance,
        # distinct from the predeclared scientific-accuracy acceptance.
        allowances = [D(4096) * D(2)**(-52) * max(m, abs(dec(x)), D('1e-100')) for m,x in zip(mag,serialized)]
        check(str(key) + ':independent_weighted_output_aggregation', all(g <= a for g,a in zip(gaps,allowances)),
              {'max_number_like_gap':str(max(gaps[:7] + [gaps[14]])), 'max_energy_like_gap':str(max(gaps[7:14]+[gaps[15]]))})
        derived_heat = sum(dec(b) - c*dec(a) for a,b,c in zip(row['delta_A'],row['delta_B_eV'],chi))
        check(str(key) + ':heat_channel_arithmetic', abs(derived_heat-dec(row['delta_total_heat_eV'])) <= D('1e-25'))
        ref = sum(dec(x) for x in saved_map[key]['delta_heat_eV_per_H'])
        approx = dec(row['delta_total_heat_eV'])
        relative = abs(approx-ref)/abs(ref)
        quadrature_gap = abs(dec(coarse_map[key]['delta_total_heat_eV'])-approx)/abs(approx)
        check(str(key) + ':independent_predeclared_heat_gate', abs(ref) >= dec(plan['acceptance']['heat_near_zero_floor_eV'])
              and relative <= dec(plan['acceptance']['expanded_macro_total_heat_defect_relative_error_max']))
        check(str(key) + ':independent_predeclared_GL_gate', quadrature_gap <= dec(plan['acceptance']['primary_GL8_12_heat_defect_relative_gap_max']))
        macro.append({'mode':key[0],'step':key[1],'relative_heat_defect_error':str(relative),'GL8_12_relative_gap':str(quadrature_gap)})
    check('actual_path_segment_count_both_orders', sum(g['segments'] for g in new['segment_groups']) == sum(g['segments'] for g in coarse['segment_groups']) == 14652)
    old_count = sum(g['segment_count']*g['nfev'] for g in saved['segment_groups'])
    check('scientific_coefficient_sample_counts', old_count == 2711100 and new['physical_coefficient_samples'] == 175824 and coarse['physical_coefficient_samples'] == 117216)
    passed = all(c['pass'] for c in CHECKS)
    result = {'schema':'bass-he-e13c3-independent-saved-evidence-audit-v1','role':'INDEPENDENT_DECISION_REVIEW_SUPPORT',
              'started_or_finished_utc':datetime.now(timezone.utc).isoformat(),'verdict':'PASS' if passed else 'FAIL',
              'producer_sha256_as_run':sha(Path(__file__)),'checks':CHECKS,'check_count':len(CHECKS),'failed':[c for c in CHECKS if not c['pass']],
              'independent_macro_metrics':macro,'identities':IDENTITIES,
              'execution_scope':'Saved evidence hashing, AST read and arithmetic only; no candidate or reference solver imported/executed.',
              'new_continuous_solves':0,'new_native_or_gas_runs':0,'old_suite_replays':0,
              'not_claimed':['Independent physical coefficient model','Per-node or uniform interval accuracy certificate','New scientific acceptance thresholds']}
    atomic(OUT/'SAVED_EVIDENCE_AUDIT.json', result)
    if not passed and not (OUT/'FIRST_REVIEW_AUDIT_FAILURE.json').exists():
        atomic(OUT/'FIRST_REVIEW_AUDIT_FAILURE.json', result)
    print(json.dumps({'verdict':result['verdict'],'checks':len(CHECKS),'failed':result['failed']}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
