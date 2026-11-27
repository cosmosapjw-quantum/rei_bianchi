#!/usr/bin/env python3
"""One frozen PHYS91 primary. Resume exits before scientific imports or writes."""
import sys
sys.dont_write_bytecode = True
import json
from evidence import UNIT, REPO, identity, main_args, resume, fresh, publish, write_json

def compute(output):
    import time
    from kernel import load_inputs, generate, fixtures
    contract = json.loads((UNIT/'CONTRACT.json').read_text())
    table, inherited = load_inputs(REPO, contract)

    def retain(index, record):
        return write_json(output, 'CHECKPOINT_%03d.json' % index, record)

    generated = generate(table, inherited, contract['algorithm'], retain)
    exact_fixtures = fixtures()
    selected = {'selected_primal': generated['selected_primal'],
                'selected_dual': generated['selected_dual']}
    results = {
        'schema': 'PHYS91_EXACT_GLOBAL_PSD_DISTANCE_RESULTS_V1',
        'unit_id': contract['unit_id'],
        'enclosure': generated['enclosure'],
        'selected_primal_checkpoint': generated['selected_primal']['checkpoint'],
        'selected_dual_checkpoint': None if generated['selected_dual'] is None else generated['selected_dual']['checkpoint'],
        'n': table.n, 'upper_entries_checked': table.n*(table.n+1)//2,
        'all_H_strictly_positive_exact': True,
        'changed_candidate_eigh_calls': generated['changed_candidate_eigh_calls'],
        'raw_F_eigh_calls': 0, 'old_pair_rescans': 0,
        'retained_exact_checkpoints': generated['checkpoints'],
        'retained_primal_candidates': generated['checkpoints'],
        'retained_dual_candidates': generated['checkpoints'],
        'q': generated['q'], 'quantization': generated['quantization'],
        'termination': generated['termination'],
        'process_CPU_s_after_generation_and_checks': generated['process_CPU_s_after_generation_and_checks'],
        'process_CPU_s_after_fixtures': time.process_time(),
        'frozen_projection_caps': contract['algorithm']['maximum_projections_each'],
        'frozen_total_projection_cap': contract['algorithm']['maximum_projections_total'],
        'conditional_model': 'CLOSED_NEAREST_FORMATTING_CELL_NOT_ACTUAL_FORMATTER_GUARANTEE',
        'actual_matrix_repair': False, 'adopted_source_covariance': None,
        'physical_CI': False, 'actual_consumer_ACK': None, 'strong_physical_no_go': 'NOT_CLAIMED',
        'HH_R10': 'OFF', 'production': 'NOT_ISSUED', 'parent_status': 'PARTIAL_INPUT_DEPENDENCIES',
        'forbidden_operations': {'ENDF_decode': 0, 'old_scientific_callbacks': 0, 'old_pair_rescan': 0,
                                 'raw_F_eigh': 0, 'ODE': 0, 'integrals': 0, 'benchmark': 0,
                                 'nuclear_rate_activation': 0, 'fast_stopping': 0},
    }
    checkpoints = {'attempts': generated['attempts'], 'stages': generated['stages'],
                   'termination': generated['termination']}
    # The figure presents only already computed exact certificate values.
    from fractions import Fraction as R
    from io import BytesIO
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    attempts = generated['attempts']
    x = [row['checkpoint'] for row in attempts]
    upper = [float(row['alpha']) for row in attempts]
    lower = [float(max(inherited, R(0) if row['beta'] is None else row['beta'])) for row in attempts]
    figure, axis = plt.subplots(figsize=(7.2, 4.2), layout='constrained')
    axis.plot(x, upper, 'o-', color='#175b96', label='Exact primal upper bound')
    axis.plot(x, lower, 's-', color='#bd5723', label='Exact dual / inherited lower bound')
    axis.axhline(1, color='#555555', linewidth=1, linestyle='--', label='Conditional B1 radius')
    axis.set(xlabel='Retained exact checkpoint', ylabel='PSD distance bound (decimal presentation)',
             title='PHYS91 certified global PSD distance')
    axis.grid(alpha=.2)
    axis.legend(fontsize=8)
    images = {}
    for extension in ('png', 'pdf'):
        stream = BytesIO()
        figure.savefig(stream, format=extension, dpi=170)
        images['GLOBAL_PSD_BOUNDS.'+extension] = stream.getvalue()
    plt.close(figure)
    results['process_CPU_s_before_final_publish'] = time.process_time()
    return {'RESULTS.json': results, 'CERTIFICATES.json': selected,
            'CHECKPOINTS.json': checkpoints, 'FIXTURES_AND_GUARDS.json': exact_fixtures, **images}

def main():
    args = main_args('primary')
    binding = identity()
    if args.resume:
        print(json.dumps(resume(args.output, 'primary', binding)))
        return
    output = fresh(args.output)
    try:
        payloads = compute(output)
        publish(output, 'primary', binding, payloads)
    except BaseException as exc:
        import traceback
        write_json(output, 'FAILURE.json', {
            'status': 'STOP_NO_ADMISSION' if 'STOP_NO_ADMISSION' in str(exc) else 'PRIMARY_FAILED_PRESERVED',
            'exception': type(exc).__name__, 'reason': str(exc), 'traceback': traceback.format_exc(),
            'automatic_retry': False, 'identity': binding['sha256'],
            'actual_matrix_repair': False, 'HH_R10': 'OFF', 'production': 'NOT_ISSUED',
        })
        raise
    print(json.dumps({'status': 'COMPLETE', 'kind': 'primary', 'identity': binding['sha256']}))

if __name__ == '__main__':
    main()

