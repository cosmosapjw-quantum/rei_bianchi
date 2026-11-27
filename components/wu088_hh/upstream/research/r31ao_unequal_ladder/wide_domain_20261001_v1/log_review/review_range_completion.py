"""Read-only exact validation of the final predeclared one-tile completion."""
import importlib.util
import json
from fractions import Fraction as Q
from review_range import HERE, NEW, BASE, RUNTIME, OWNER, load, sha, seal, check_artifacts, write_new


def interval(part):
    assert set(part) == {'lower_mantissa', 'upper_mantissa', 'exponent2'}
    low, high, exponent = (int(part[k]) for k in ('lower_mantissa', 'upper_mantissa', 'exponent2'))
    assert low <= high
    return Q(low) * Q(2)**exponent, Q(high) * Q(2)**exponent


def main():
    source_review = load(HERE / 'RANGE_SOURCE_REVIEW.json')
    buildpath = RUNTIME / 'build_range_cached/BUILD.json'
    build = load(buildpath)
    seal(build, 'manifest_sha256')
    assert build['source']['sha256'] == source_review['source_identity']
    assert build['source']['files'] == source_review['source_files']
    for name, identity in build['source']['files'].items():
        assert sha(BASE / name) == identity
    assert sha(buildpath.parent / build['binary']) == build['binary_sha256']
    assert sha(buildpath.parent / 'frozen107_generated.hpp') == build['generated_header_sha256']
    assert sha(build['backend_provenance']) == build['backend_provenance_sha256']
    check_artifacts(build['linkage'])
    assert sha(BASE / 'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz') == build['archive_sha256']
    planpath = RUNTIME / 'W1_TILED/plans/00.json'
    plan = load(planpath)
    seal(plan, 'plan_sha256')
    seal(plan['tasks'][0], 'task_sha256')
    path = RUNTIME / 'RANGE_TILE00_COMPLETION.json'
    result = load(path)
    seal(result, 'result_sha256')
    wrapper = result['wrapper']
    contractpath = RUNTIME / 'RANGE_COMPLETION_CONTRACT.json'
    contract = load(contractpath)
    assert contract['max_actual_HH_integral_invocations'] == 1 and contract['stop_after_this_attempt'] is True
    assert contract['prior_actual_receipt_sha256'] == sha(RUNTIME / 'RANGE_TILE00_GOAL128.json')
    assert contract['source_identity'] == build['source']['sha256']
    assert contract['build_manifest_sha256'] == build['manifest_sha256']
    assert contract['plan_sha256'] == plan['plan_sha256'] and contract['task_index'] == 0
    limits = wrapper['native_limits']
    assert limits == contract['limits'] == load(RUNTIME / 'RANGE_COMPLETION_LIMITS.json')
    previous = load(RUNTIME / 'RANGE_TILE00_GOAL128.json')['wrapper']
    changed = {k: {'before': previous['native_limits'][k], 'after': v}
               for k, v in limits.items() if previous['native_limits'][k] != v}
    assert changed == {'max_evaluations': {'before': 20000, 'after': 200000},
                       'wall_seconds': {'before': 30, 'after': 120}}
    for key in ('build_source', 'build_manifest_sha256', 'binary_sha256', 'archive_sha256',
                'input_record_sha256', 'backend_provenance_sha256', 'linkage', 'physical_window',
                'log2_window', 'coordinate_map', 'endpoint_plan_module_sha256'):
        assert wrapper[key] == previous[key], key
    assert wrapper['physical_window'] == plan['window']
    assert wrapper['build_source'] == build['source']
    assert wrapper['binary_sha256'] == build['binary_sha256']
    assert wrapper['linkage'] == build['linkage']
    for key in ('archive_sha256', 'input_record_sha256'):
        assert result[key] == wrapper[key] == build[key] == plan[key]
    assert result['plan_sha256'] == plan['plan_sha256']
    assert result['task_sha256'] == plan['tasks'][0]['task_sha256']
    expected_command = [str(buildpath.parent / build['binary']), '0',
                        *[plan['window'][k] for k in ('l_t', 'T_t', 'l_u', 'T_u')],
                        *[str(limits[k]) for k in ('precision_bits', 'radius_exp', 'relative_goal', 'max_evaluations',
                                                 'max_integration_calls', 'wall_seconds', 'queued_panels', 'degree_limit')],
                        result['task_sha256'], result['plan_sha256']]
    assert wrapper['command'] == expected_command
    assert wrapper['returncode'] == 0 and wrapper['native_execution_observed'] is True
    assert 0 < wrapper['elapsed_wall_ns'] < contract['native_hard_wall_seconds'] * 10**9
    native = {k: v for k, v in result.items() if k not in ('wrapper', 'result_sha256')}
    specification = importlib.util.spec_from_file_location('wu088_range_review_only', OWNER / 'driver.py')
    driver = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(driver)
    assert driver.validate_result(native, plan=plan, task=plan['tasks'][0], manifest=build, limits=limits) == native
    assert result['status'] == 'RADIUS_MET' and result['accepted'] is True and result['flint_status'] == 0
    assert result['precision_bits'] == 128 and result['accepted_component_radius_exp'] == -52
    rectangles = {}
    for part in ('real', 'imag'):
        low, high = interval(result['rectangle'][part])
        radius = (high - low) / 2
        assert radius <= Q(2)**-52
        rectangles[part] = {'lower': str(low), 'upper': str(high), 'midpoint': str((low + high) / 2),
                            'radius': str(radius), 'radius_to_cap': str(radius / (Q(2)**-52)),
                            'radius_below_cap': True}
    for key in ('endpoint_included', 'normalization_applied', 'full_domain_integral', 'scientific_admission', 'production_admission'):
        assert result[key] is False
    counters = result['diagnostics']['counters']
    matrix = result['diagnostics']['inner_outcomes']
    assert sum(sum(sum(outcomes) for outcomes in group) for group in matrix) == result['integration_calls'] - 1 == 307
    assert counters['inner_radius_met'] == counters['selected_point_inner'] == 284
    assert counters['inner_enclosure_available'] == 23
    assert counters['outer_order1_calls'] == counters['preflight_calls'] == 23
    assert counters['preflight_nonfinite'] == counters['outer_refinable_failures'] == 15
    for key in ('inner_radius_too_wide', 'inner_resource_limit', 'inner_no_convergence', 'inner_nonfinite', 'inner_invalid_contract', 'outer_fatal_failures'):
        assert counters[key] == 0
    assert result['dispatched_evaluations'] == 85915 <= limits['max_evaluations']
    assert result['integration_calls'] == 308 <= limits['max_integration_calls']
    assert result['callback_calls'] == 85593 <= result['dispatched_evaluations']
    paths = [path, buildpath, planpath, contractpath, RUNTIME / 'RANGE_COMPLETION_LIMITS.json',
             RUNTIME / 'RANGE_TILE00_GOAL128.json', HERE / 'RANGE_SOURCE_REVIEW.json', HERE / 'ACTUAL_RANGE_PAIR_REVIEW.json']
    review = {
        'schema': 'WU088_FINAL_RANGE_COMPLETION_INDEPENDENT_REVIEW_V1',
        'status': 'PASS_SOURCE_BOUND_ONE_TILE_SERIALIZED_RADIUS_REVIEW',
        'review_script_sha256': sha(__file__),
        'evidence_sha256': {str(p.relative_to(BASE)): sha(p) for p in paths},
        'build_source_identity': build['source']['sha256'], 'build_manifest_sha256': build['manifest_sha256'],
        'binary_sha256': build['binary_sha256'], 'source_files_checked': len(build['source']['files']),
        'plan_sha256': plan['plan_sha256'], 'task_sha256': result['task_sha256'], 'task_index': 0,
        'physical_window': wrapper['physical_window'], 'log2_window': wrapper['log2_window'],
        'strict_driver_validate_result_replayed_without_native_execution': True,
        'independent_exact_serialized_rectangle_check': rectangles,
        'accepted_component_radius_exp': -52, 'precision_bits': 128, 'relative_goal': 128,
        'changed_limits_from_prior_rejected_run': changed, 'native_limits': limits,
        'native_status': result['status'], 'native_primitive_accepted': True,
        'dispatched_evaluations': result['dispatched_evaluations'], 'integration_calls': result['integration_calls'],
        'native_callback_calls': result['callback_calls'], 'elapsed_wall_ns': wrapper['elapsed_wall_ns'],
        'diagnostic_counters': counters, 'reviewer_new_hh_integrals': 0,
        'scope': 'One compact tile [1/16,1/2]^2 of Frozen107 task0; exact serialized component halfwidths satisfy2^-52.',
        'limitations': [
            'No independently recomputed HH oracle exists for this tile; validation relies on reviewed interval algorithm and source-bound execution.',
            'Successful raw stdout is not separately retained: its wrapper digest is provenance, not independently recovered raw bytes.',
            'This tile is1/16 of the proposed W1 grid; other15 tiles have no accepted completion under this corrected source.',
            'The previous fixed-source tiled runner remains stopped with0 accepted tiles; this separate receipt does not mutate its collection result.',
            'No full W1/W3 enclosure, endpoint disk, normalization, final D/epsilon/gap or production/NCP admission follows.',
            'The40.148833522s measurement is one workspace native launch/wait duration, not an MPI64-core throughput benchmark.'
        ],
        'endpoint_included': False, 'normalization_applied': False, 'full_domain_integral': False,
        'scientific_admission': False, 'production_admission': False
    }
    output = write_new('FINAL_RANGE_COMPLETION_REVIEW.json', review)
    print(json.dumps({'review': output, 'radii': rectangles, 'native_primitive_accepted': True}, sort_keys=True))


if __name__ == '__main__':
    main()
