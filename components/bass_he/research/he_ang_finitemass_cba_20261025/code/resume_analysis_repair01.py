"""One authorized continuation: reuse exact saved prefix, then saved-data plot.

Original seven code files are unchanged. This script is launched only by the
new explicitly gated repair runner after root GO; it never calls the old main.
"""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import traceback
import run_analysis as analysis
import plot_results
from io_utils import atomic_json, identity

UNIT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((UNIT/'REPAIR_CONTRACT_01.json').read_bytes().decode('utf-8'))
PARTIAL = UNIT/CONTRACT['reuse']['partial_path']
EXPECTED = {'bytes': CONTRACT['reuse']['partial_bytes'], 'sha256': CONTRACT['reuse']['partial_sha256']}
RESULTS = UNIT/'results'


def prefix_bytes(report):
    return json.dumps({'generic': report['generic'], 'quadrature': report['quadrature'][:2]},
                      indent=2, allow_nan=False).encode('utf-8')


def validate_prefix(report, full_plan):
    if report['acceptance'] != full_plan:
        raise RuntimeError('retained acceptance plan differs from full frozen contract')
    expected = [(M, geometry) for M in full_plan['generic']['masses']
                for geometry in full_plan['generic']['geometries']]
    if len(report['generic']) != 12 or len(expected) != 12:
        raise RuntimeError('completed generic prefix count mismatch')
    for row, (M, geometry) in zip(report['generic'], expected):
        if row['M'] != M or row['geometry'] != geometry or row['pass'] is not True:
            raise RuntimeError('completed generic prefix identity/PASS mismatch')
    if len(report['quadrature']) != 2 or len(full_plan['quadrature']['cases']) != 3:
        raise RuntimeError('quadrature prefix or full fixture count mismatch')
    for row, fixture in zip(report['quadrature'], full_plan['quadrature']['cases'][:2]):
        if row['fixture'] != fixture or row['pass'] is not True:
            raise RuntimeError('completed quadrature fixture identity/PASS mismatch')
        if [term['term'] for term in row['terms']] != ['aDelta', 'minus_bDelta']:
            raise RuntimeError('completed quadrature term ordering mismatch')
        if any(term['pass'] is not True for term in row['terms']):
            raise RuntimeError('completed quadrature term lacks PASS')
    for category in ['tiny', 'kinematics_normalization', 'fold', 'illustration', 'mass_trend']:
        if report[category]:
            raise RuntimeError('unexpected retained later-category evidence: '+category)


def main():
    if identity(PARTIAL) != EXPECTED:
        raise RuntimeError('immutable failed partial identity mismatch')
    report = json.loads(PARTIAL.read_bytes().decode('utf-8'))
    full_plan = copy.deepcopy(analysis.PLAN)
    validate_prefix(report, full_plan)
    tests = json.loads((RESULTS/'TEST_REPORT.json').read_bytes().decode('utf-8'))
    if not (tests['tests_run'] == 17 and tests['successful'] is True
            and tests['failures'] == 0 and tests['errors'] == 0):
        raise RuntimeError('reused targeted-test result incomplete')
    retained_prefix = prefix_bytes(report)
    original_save = analysis.save
    def continuation_save(name='ANALYSIS_CONTINUATION_PARTIAL.json'):
        original_save(name)
    analysis.save = continuation_save
    analysis.REPORT = report
    report['continuation'] = {'repair_id': CONTRACT['repair_id'],
        'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reused_partial': EXPECTED, 'reused_generic_rows': 12, 'reused_quadrature_cases': 2,
        'reused_test_methods': 17, 'completed_case_reexecution': 0,
        'historical_attempt02_status': 'FAIL retained; resolution by separate continuation'}
    selected_plan = copy.deepcopy(full_plan)
    selected_plan['generic']['masses'] = []
    selected_plan['quadrature']['cases'] = full_plan['quadrature']['cases'][2:]
    analysis.PLAN = selected_plan
    try:
        # Existing kernel_checks now executes only the missing third quadrature
        # and the previously unreached tiny fixtures. Generic loop is empty.
        analysis.kernel_checks()
    finally:
        analysis.PLAN = full_plan
    if analysis.PLAN != full_plan:
        raise RuntimeError('full frozen PLAN restoration failed')
    analysis.kinematic_normalization_checks()
    analysis.fold_checks()
    analysis.illustrations()
    counts = {'generic': 12, 'quadrature': 3, 'tiny': 12, 'kinematics_normalization': 4,
              'fold': 3, 'illustration': 73, 'mass_trend': 8}
    for name, expected_count in counts.items():
        if len(report[name]) != expected_count:
            raise RuntimeError('full frozen output count mismatch: '+name)
    if [row['order'] for row in report['fold']] != full_plan['fold']['gauss_orders']:
        raise RuntimeError('fold order identity mismatch')
    if prefix_bytes(report) != retained_prefix or identity(PARTIAL) != EXPECTED:
        raise RuntimeError('saved prefix changed during continuation')
    categories = ['generic', 'quadrature', 'tiny', 'kinematics_normalization']
    report['checks_by_category'] = {name: {'rows': len(report[name]),
        'passed': sum(row['pass'] for row in report[name])} for name in categories}
    report['pass'] = all(row['pass'] is True for name in categories for row in report[name]) and report['fold_acceptance']['pass'] is True
    report['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report['continuation']['prefix_value_and_serialized_bytes_equal'] = True
    report['continuation']['retained_prefix_sha256'] = hashlib.sha256(retained_prefix).hexdigest()
    report['continuation']['full_PLAN_restored'] = True
    report['continuation']['exact_full_counts'] = counts
    analysis.save('ANALYSIS.json')
    if not report['pass']:
        raise RuntimeError('continuation numerical acceptance FAIL; plotting not launched')
    # Unchanged saved-JSON plot, in this same bounded process; no old03 child.
    plot_results.main()
    figures = ['results/figures/FINITE_M_CBA.png', 'results/figures/FINITE_M_CBA.svg',
               'results/figures/FIGURE_METADATA.json']
    if not all((UNIT/name).is_file() and (UNIT/name).stat().st_size > 0 for name in figures):
        raise RuntimeError('required saved-data figure missing')
    summary = {'repair_id': CONTRACT['repair_id'], 'pass': True, 'counts': counts,
        'retained_prefix_equal': True, 'original_partial_unchanged': identity(PARTIAL) == EXPECTED,
        'completed_case_reexecution': 0, 'tests_reexecuted': 0,
        'original_separate03_plot_executed': False, 'same_child_saved_JSON_plot': True,
        'outputs': {name: identity(UNIT/name) for name in figures+['results/ANALYSIS.json', 'results/ILLUSTRATION.csv']}}
    atomic_json(RESULTS/'REPAIR01_SUMMARY.json', summary)
    print(json.dumps(summary))
    return 0


if __name__ == '__main__':
    try: raise SystemExit(main())
    except Exception as exc:
        atomic_json(RESULTS/'REPAIR01_FAILURE.json', {'class': type(exc).__name__,
            'message': str(exc), 'traceback': traceback.format_exc(),
            'original_partial_identity_now': identity(PARTIAL) if PARTIAL.exists() else None})
        raise
