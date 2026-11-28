"""Execution-free independent range-host source/receipt review; never runs HH."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json

HERE = Path(__file__).resolve().parent
NEW = HERE.parent
BASE = NEW.parent
RUNTIME = NEW / 'runtime'
OWNER = NEW / 'range_native_driver'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def load(path):
    return json.loads(Path(path).read_text())


def seal(value, key):
    assert value[key] == digest(canonical({k: v for k, v in value.items() if k != key})), key


def check_artifacts(value):
    count = 0
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            path = Path(value['path'])
            assert sha(path) == value['sha256'], path
            if 'bytes' in value:
                assert path.stat().st_size == value['bytes'], path
            if 'size' in value:
                assert path.stat().st_size == value['size'], path
            count += 1
        count += sum(check_artifacts(v) for v in value.values())
    elif isinstance(value, list):
        count += sum(check_artifacts(v) for v in value)
    return count


def arf_dump(value):
    mantissa, exponent = value.split()
    return Q(int(mantissa, 16)) * Q(2) ** int(exponent, 16)


def write_new(name, value):
    path = HERE / name
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    return {'path': str(path), 'sha256': sha(path)}


def main():
    verification = load(OWNER / 'VERIFICATION.json')
    source = verification['source']
    assert source['sha256'] == 'de1e32d8a68146a49d269614c2259ec06f10a5294ffa05b15d375239518bcae1'
    assert source['sha256'] == digest(canonical(source['files']))
    for name, identity in source['files'].items():
        assert sha(BASE / name) == identity, name
    boundary = OWNER / 'BOUNDARY_FINAL.log'
    assert sha(boundary) == verification['boundary_log']['sha256']
    assert 'Ran 24 tests' in boundary.read_text() and boundary.read_text().rstrip().endswith('OK')
    fixtures = {}
    for tag, key in [('analytic_old_goal128', 'native_old_goal128_receipt'),
                     ('analytic_range_goal128', 'native_range_goal128_receipt')]:
        path = OWNER / tag / 'RECEIPT.json'
        assert sha(path) == verification[key]['sha256']
        receipt = load(path)
        count = check_artifacts(receipt)
        assert receipt['build']['returncode'] == receipt['run']['returncode'] == 0
        assert receipt['result'] == load(receipt['run']['stdout']['path'])
        assert receipt['result']['fixture_relative_goal'] == receipt['precision_bits'] == 128
        assert receipt['result']['status'] == 'PASS' and receipt['hh_evaluations'] == 0
        fixtures[tag] = {'receipt_sha256': sha(path), 'referenced_artifacts_checked': count,
                         'result': receipt['result']}
    oracle = Q(2)**40 * ((Q(2)**2-Q(1)**2)/2)**2
    assert oracle == 9 * Q(2)**38
    source_review = {
        'schema': 'WU088_FINITE_UNIFORM_ENCLOSURE_SOURCE_REVIEW_V1',
        'status': 'NO_BLOCKING_SOURCE_FINDING_FOR_PREDECLARED_BOUNDED_TILE_EXPERIMENT',
        'source_identity': source['sha256'], 'source_files_checked': len(source['files']),
        'source_files': source['files'], 'review_script_sha256': sha(__file__),
        'mathematical_contract_sha256': sha(HERE / 'UNIFORM_ENCLOSURE_CORRECTION_CONTRACT.md'),
        'owner_verification_sha256': sha(OWNER / 'VERIFICATION.json'),
        'boundary_log': {'path': str(boundary.relative_to(BASE)), 'sha256': sha(boundary), 'tests': 24},
        'native_synthetic_fixtures_inspected_not_repeated': fixtures,
        'independent_exact_oracle': str(oracle),
        'source_properties_reviewed': [
            'Full complex outer parameter ball, log map/Jacobian, physical formula and domain guards unchanged.',
            'enclosure_only=true is passed by nested code only when the existing uniform-inner plan is selected.',
            'ENCLOSURE_AVAILABLE is returned only after valid contracts, live shared budget, FLINT success and finite result.',
            'ENCLOSURE_AVAILABLE sets achieved_radius_accepted=false; no uncertainty is clipped or centered.',
            'Outer callback consumes ENCLOSURE_AVAILABLE only for selected uniform plan with FLINT success, finite value and live budget.',
            'Top-level integrate_1d defaults enclosure_only=false; tight point-inner and final radius gates remain strict.',
            'Order1 whole-inner-path/whole-outer-box holomorphy preflight is unchanged.',
            'Worker accepts only RADIUS_MET with achieved_radius_accepted and finite result; driver exact serialized halfwidth check remains.',
            'Point-width, nonfinite and FLINT-failure rejection assertions are present in the executed paired fixture source.',
            'Production default relative_goal=64 and precision128 unchanged; paired mechanism fixture tightens both old and new goal to128.'
        ],
        'limitations': [
            'Analytic fixture proves a controlled mechanism and exact oracle, not actual Frozen107 convergence.',
            'Goal64 failed synthetic attempt is preserved; final paired receipts bind current fixture bytes.',
            'Library/source byte readback is execution provenance, not independent HH recomputation.'
        ],
        'reviewer_new_hh_integrals': 0, 'scientific_admission': False, 'production_admission': False
    }
    source_output = write_new('RANGE_SOURCE_REVIEW.json', source_review)

    buildpath = RUNTIME / 'build_range_cached/BUILD.json'
    build = load(buildpath)
    seal(build, 'manifest_sha256')
    assert build['source'] == source
    assert build['manifest_sha256'] == '13965d2210e976f0d7a190fba58f8c3c1bf366521e8dd1bd5e9a28cdae9e9342'
    assert sha(buildpath.parent / build['binary']) == build['binary_sha256']
    assert sha(buildpath.parent / 'frozen107_generated.hpp') == build['generated_header_sha256']
    assert sha(build['backend_provenance']) == build['backend_provenance_sha256']
    check_artifacts(build['linkage'])
    assert sha(BASE / 'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz') == build['archive_sha256']
    planpath = RUNTIME / 'W1_TILED/plans/00.json'
    plan = load(planpath)
    seal(plan, 'plan_sha256')
    seal(plan['tasks'][0], 'task_sha256')
    contract = load(RUNTIME / 'RANGE_CORRECTION_CONTRACT.json')
    tightened = load(RUNTIME / 'RANGE_GOAL128_CONTRACT.json')
    assert tightened['prior_actual_receipt_sha256'] == sha(RUNTIME / 'RANGE_TILE00.json')
    assert tightened['source_identity'] == source['sha256']
    assert tightened['build_manifest_sha256'] == build['manifest_sha256']
    assert tightened['max_actual_HH_integral_invocations'] == 1 and tightened['no_sweep'] is True
    records = {}
    wrappers = []
    for name, goal in [('RANGE_TILE00', 64), ('RANGE_TILE00_GOAL128', 128)]:
        path = RUNTIME / (name + '.json')
        result = load(path)
        seal(result, 'result_sha256')
        wrapper = result['wrapper']
        wrappers.append(wrapper)
        native = json.loads(result['native_stdout'])
        assert result['accepted'] is False and native['accepted'] is False
        assert wrapper['returncode'] == result['returncode'] == 2 and result['reason'] == 'NONZERO_NATIVE_EXIT'
        assert native['status'] == 'RESOURCE_LIMIT' and native['rectangle'] is None
        assert native['flint_status'] == 2
        assert digest(result['native_stdout'].encode()) == wrapper['native_stdout_sha256']
        assert digest(result['native_stderr'].encode()) == wrapper['native_stderr_sha256']
        assert wrapper['build_source'] == source and wrapper['build_manifest_sha256'] == build['manifest_sha256']
        assert wrapper['binary_sha256'] == build['binary_sha256'] and wrapper['linkage'] == build['linkage']
        assert wrapper['backend_provenance_sha256'] == build['backend_provenance_sha256']
        assert wrapper['physical_window'] == plan['window']
        assert wrapper['log2_window'] == {'l_t': -4, 'T_t': -1, 'l_u': -4, 'T_u': -1}
        for key in ['archive_sha256', 'input_record_sha256']:
            assert native[key] == wrapper[key] == build[key] == plan[key]
        assert native['task_sha256'] == result['task_sha256'] == plan['tasks'][0]['task_sha256']
        assert native['plan_sha256'] == result['plan_sha256'] == plan['plan_sha256']
        assert native['build_source_sha256'] == source['sha256']
        limits = wrapper['native_limits']
        expected_limits = dict(contract['common_limits'], radius_exp=-52, relative_goal=goal)
        assert limits == expected_limits
        if goal == 128:
            assert limits == tightened['limits'] == load(RUNTIME / 'RANGE_GOAL128_LIMITS.json')
        expected_command = [str(buildpath.parent / build['binary']), '0',
                            *[plan['window'][k] for k in ('l_t', 'T_t', 'l_u', 'T_u')],
                            *[str(limits[k]) for k in ('precision_bits', 'radius_exp', 'relative_goal', 'max_evaluations',
                                                     'max_integration_calls', 'wall_seconds', 'queued_panels', 'degree_limit')],
                            result['task_sha256'], result['plan_sha256']]
        assert wrapper['command'] == expected_command
        assert native['dispatched_evaluations'] == limits['max_evaluations'] == 20000
        assert native['integration_calls'] <= limits['max_integration_calls']
        assert native['precision_bits'] == 128 and native['accepted_component_radius_exp'] == -52
        assert 0 < wrapper['elapsed_wall_ns'] < (limits['wall_seconds'] + 5) * 10**9
        for key in ['endpoint_included', 'normalization_applied', 'full_domain_integral', 'scientific_admission', 'production_admission']:
            assert native[key] is False
        diagnostics = native['diagnostics']
        counters = diagnostics['counters']
        matrix = diagnostics['inner_outcomes']
        assert sum(sum(sum(row) for row in group) for group in matrix) == native['integration_calls'] - 1
        samples = diagnostics['failure_samples']
        assert samples[-1]['reason'] == 'max_dispatched_evaluations' and samples[-1]['status'] == 'RESOURCE_LIMIT'
        point_samples = []
        for sample in samples:
            inner = sample['inner_return']
            if sample['status'] == 'RADIUS_TOO_WIDE':
                assert sample['uniform_inner'] is False and sample['relative_goal'] == goal
                assert inner['finite'] and inner['observed'] and not inner['truncated']
                assert inner['flint_status'] == sample['flint_status'] == 0
                rr, ir = arf_dump(inner['real_radius']), arf_dump(inner['imag_radius'])
                cap = Q(2) ** sample['accepted_component_radius_exp']
                assert max(rr, ir) > cap
                point_samples.append({'real_radius': str(rr), 'imag_radius': str(ir), 'cap': str(cap),
                                      'real_radius_to_cap': str(rr / cap), 'imag_radius_to_cap': str(ir / cap)})
        records[name] = {'receipt_sha256': sha(path), 'result_sha256': result['result_sha256'],
                         'status': native['status'], 'accepted': False, 'relative_goal': goal,
                         'dispatched_evaluations': native['dispatched_evaluations'], 'integration_calls': native['integration_calls'],
                         'elapsed_wall_ns': wrapper['elapsed_wall_ns'], 'counters': counters, 'inner_outcomes': matrix,
                         'exact_point_failure_radius_samples': point_samples}
    changed_limits = [k for k in wrappers[0]['native_limits'] if wrappers[0]['native_limits'][k] != wrappers[1]['native_limits'][k]]
    assert changed_limits == ['relative_goal']
    assert [(i, a, b) for i, (a, b) in enumerate(zip(wrappers[0]['command'], wrappers[1]['command'])) if a != b] == [(8, '64', '128')]
    first = records['RANGE_TILE00']['counters']
    second = records['RANGE_TILE00_GOAL128']['counters']
    assert (first['inner_radius_met'], first['inner_radius_too_wide']) == (0, 76)
    assert (second['inner_radius_met'], second['inner_radius_too_wide']) == (64, 0)
    evidence_paths = [buildpath, planpath, RUNTIME / 'RANGE_CORRECTION_CONTRACT.json', RUNTIME / 'RANGE_GOAL128_CONTRACT.json',
                      RUNTIME / 'RANGE_GOAL128_LIMITS.json', RUNTIME / 'DIAGNOSTIC_TILE00.json']
    actual_review = {
        'schema': 'WU088_FINITE_UNIFORM_RANGE_ACTUAL_PAIR_REVIEW_V1',
        'status': 'BOUND_RECEIPTS_VERIFIED_BOTH_REJECTED_AT_DISPATCH_CAP',
        'review_script_sha256': sha(__file__), 'source_review_sha256': source_output['sha256'],
        'build_source_identity': source['sha256'], 'build_manifest_sha256': build['manifest_sha256'],
        'binary_sha256': build['binary_sha256'], 'source_files_checked': len(source['files']),
        'evidence_sha256': {str(p.relative_to(BASE)): sha(p) for p in evidence_paths},
        'records': records, 'changed_native_limits_between_pair': changed_limits,
        'findings': [
            'The range correction removes the previous no-analytic-attempt state: both actual runs make10 outer order1 calls and return15 uniform enclosures.',
            'Goal64 reaches finite successful point inner outputs but76 fail their unchanged2^-68 achieved radius; one retained finite sample is exactly decoded.',
            'Changing only relative_goal64 to128 yields64 strict point-inner successes and zero width refusals before the common20k dispatch cap.',
            'Both receipts reject with RESOURCE_LIMIT, no rectangle, no final accuracy or scientific admission.',
            'Eight conservative outer analytic preflight refusals remain in both runs; they are handled refinably and are not proven the sole remaining bottleneck.',
            'More evaluations may be needed, but these receipts do not prove convergence under any larger budget or establish W1 coverage.'
        ],
        'reviewed_actual_invocations': 2, 'reviewed_accepted_invocations': 0, 'reviewer_new_hh_integrals': 0,
        'limitations': ['Source-bound native output and byte identity reviewed without replaying HH.',
                        'Times are single workspace executions, not NCP/MPI throughput or a speedup benchmark.',
                        'No full W1/W3 sum, endpoint composition, normalization, D/epsilon/gap or production solver admission.'],
        'scientific_admission': False, 'production_admission': False
    }
    actual_output = write_new('ACTUAL_RANGE_PAIR_REVIEW.json', actual_review)
    print(json.dumps({'source': source_output, 'actual': actual_output, 'accepted_actual_invocations': 0}, sort_keys=True))


if __name__ == '__main__':
    main()
