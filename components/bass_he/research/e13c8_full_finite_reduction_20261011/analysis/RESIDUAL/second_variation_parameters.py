#!/usr/bin/env python3
"""Saved Volterra norm parameters only; no integration, candidate or promotion."""
import argparse
from fractions import Fraction as F
from pathlib import Path
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--predecessor-package', type=Path, required=True)
    ap.add_argument('--batch-dir', type=Path, required=True)
    ap.add_argument('--residual-dir', type=Path, required=True)
    a = ap.parse_args()
    start = time.monotonic()
    sys.path.insert(0, str(a.predecessor_package / 'code'))
    from common import read, save, sha, decimal_display
    local = read(a.predecessor_package / 'analysis/LOCAL/LOCAL_ADMITTED_CANDIDATE.json')
    paths = read(a.residual_dir / 'ACTUAL/PATH_RESIDUALS.json')['paths']
    weights = {x['node']: F(x['weight_exact']) for x in paths}
    tracks = []
    for filename in ('PRIOR_FOUR_RESULTS.json', 'PRIOR_TWO_RESULTS.json'):
        tracks.extend(read(a.residual_dir / 'inputs' / filename)['tracks'])
    for entry in local['paths']:
        tracks.append(read(a.predecessor_package / entry['path'] / 'RESULT.json')['track'])
    entries = read(a.batch_dir / 'BATCH_COMPLETE.json')['ordered_paths']
    segment_rows = []
    path_rows = []
    numerators = {'P_final_last_segment': F(0), 'H_species_segment_sum': F(0)}
    denominators = dict(numerators)

    def consume(track):
        node = track['track']['node']
        w = weights[node]
        ds = []
        for j, seg in enumerate(track['segments']):
            d = F(seg['local']['bounds']['D_L']['hi'])
            s = F(seg['remainder']['S_upper'])
            h = F(seg['local']['bounds']['H_h']['hi'])
            if d < 0 or s < 0 or h < 0:
                raise ValueError('nonnegative norm parameters required')
            ds.append(d)
            row = {'node': node, 'key': seg['key'], 'D_L_upper_exact': str(d),
                   'S_upper_exact': str(s), 'H_h_upper_exact': str(h),
                   'D_L_upper_display': decimal_display(d),
                   'uniform_K_squared_delta_upper_exact': str(d * d * s),
                   'endpoint_K_squared_delta_upper_exact': str(h * d * s),
                   'incoming_radius_exact': str(F(seg['incoming']['radius'])),
                   'frozen_Lh_upper_exact': seg['frozen_Lh']['hi']}
            segment_rows.append(row)
            if j == len(track['segments']) - 1:
                numerators['P_final_last_segment'] += w * h * d * s
                denominators['P_final_last_segment'] += w * F(seg['remainder']['nonlinear_upper']['P1'])
            for sp in ('HI', 'HeI', 'HeII'):
                k = 'H_' + sp + '_eV'
                t = F(seg['remainder']['T_upper'][k])
                numerators['H_species_segment_sum'] += w * t * d * s
                denominators['H_species_segment_sum'] += w * F(seg['remainder']['nonlinear_upper'][k])
        path_rows.append({'node': node, 'sum_D_L_upper_exact': str(sum(ds)),
                          'max_segment_D_L_upper_exact': str(max(ds))})

    for t in tracks:
        consume(t)
    for entry in entries:
        consume(read(a.batch_dir / entry['relative_directory'] / 'RESULT.json')['track'])
    ds = sorted(F(r['D_L_upper_exact']) for r in segment_rows)
    if len(segment_rows) != 4694 or len(path_rows) != 2345:
        raise ValueError('saved nonzero coverage mismatch')
    summary = {'schema': 'bass-he-e13c8-volterra-saved-parameters-v1',
               'status': 'DERIVED_NORM_PARAMETERS_ONLY_NO_SECOND_VARIATION_CANDIDATE',
               'scientific_kernel_calls': 0, 'second_variation_integrals': 0,
               'new_enclosure_admission': 'NOT_RUN', 'segments': len(ds), 'paths': len(path_rows),
               'definition': 'D_j is saved integral upper bound of |Delta Lambda|; sup_u integral_0^u exp(-Lambda_f*(u-v))*|Delta Lambda(v)| dv <= D_j. H_h is an endpoint kernel bound, not an operator sup norm.',
               'D_L_upper_distribution_display': {'min': decimal_display(ds[0]), 'median': decimal_display((ds[len(ds)//2 - 1] + ds[len(ds)//2]) / 2),
                    'p95_order_statistic': decimal_display(ds[(95 * len(ds) + 99)//100 - 1]), 'max': decimal_display(ds[-1])},
               'largest_segment_D_L': sorted(segment_rows, key=lambda r: F(r['D_L_upper_exact']), reverse=True)[:8],
               'largest_path_sum_D_L': sorted(path_rows, key=lambda r: F(r['sum_D_L_upper_exact']), reverse=True)[:8],
               'all_D_L_less_than_one': all(x < 1 for x in ds),
               'formal_direct_coupling_comparison': {k: {'old_saved_direct_coupling_upper_exact': str(denominators[k]),
                  'proposed_K_delta_replacement_upper_exact': str(numerators[k]),
                  'ratio_display': decimal_display(numerators[k]/denominators[k]),
                  'restriction': 'Compares only formal coupling terms using the existing saved S,T,D. Incoming transfer, second-variation integration enclosure, centering and representation remain uncomputed; this is not a prediction of a complete new radius.'} for k in numerators},
               'source_sha256': sha(Path(__file__)), 'elapsed_seconds': time.monotonic() - start}
    save(a.residual_dir / 'ACTUAL/SECOND_VARIATION_PARAMETERS.json', summary)
    save(a.residual_dir / 'ACTUAL/SECOND_VARIATION_SEGMENT_PARAMETERS.json', {'schema': 'bass-he-e13c8-volterra-segment-parameters-v1', 'segments': segment_rows, 'paths': path_rows})
    print({'segments': len(ds), 'D_distribution': summary['D_L_upper_distribution_display'],
           'formal_ratio': {k: v['ratio_display'] for k,v in summary['formal_direct_coupling_comparison'].items()},
           'elapsed_seconds': summary['elapsed_seconds'], 'kernel_calls': 0})


if __name__ == '__main__':
    main()
