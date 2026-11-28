#!/usr/bin/env python3
"""Exact saved-result comparison and direct finite-budget replacement.

No scientific kernel is imported or evaluated. All arithmetic in endpoint
comparison and reduction uses Fraction. Display decimals are descriptive.
"""
import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = (101, 102, 410, 413)
SP = ('HI', 'HeI', 'HeII')
MOM = ['Z_eV', 'QN', 'QE_eV'] + [p + '_' + s + ('_eV' if p != 'A' else '') for p in ('A', 'B', 'H') for s in SP]
EPS = F.from_float(1.602176634e-12)


def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        f.write('\n')


def box(x):
    b = F(x['lo']), F(x['hi'])
    if b[0] > b[1]:
        raise ValueError('inverted interval')
    return b


def enc(x):
    return {'lo': str(x[0]), 'hi': str(x[1])}


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sum_boxes(values):
    return tuple(sum((v[i] for v in values), F(0)) for i in (0, 1))


def times(a, weight):
    if weight <= 0:
        raise ValueError('weight must be positive')
    return a[0] * weight, a[1] * weight


def width(a):
    return a[1] - a[0]


def display(value):
    if value is None:
        return None
    with localcontext() as context:
        context.prec = 22
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def totals(d):
    for prefix in ('A', 'B', 'H'):
        suffix = '_eV' if prefix != 'A' else ''
        d[prefix + '_total' + suffix] = sum_boxes([d[prefix + '_' + s + suffix] for s in SP])
    return d


def old_metrics(path):
    lo, hi = box(path['weight'])
    if lo != hi or lo <= 0:
        raise ValueError('old weight must be positive point')
    absolute = {k: box(path['weighted_reduction'][k]) for k in ['P_final', 'anchor'] + MOM}
    correction = {k: times(box(path['cumulative_correction'][k]), lo) for k in MOM}
    correction['P_final'] = times(box(path['segments'][-1]['DP']), lo)
    correction['energy_eV'] = times(box(path['segments'][-1]['energy_endpoint_minus_captured_erg']), lo / EPS)
    return {'absolute': totals(absolute), 'correction': totals(correction)}


def new_metrics(track, weight):
    absolute = {k: times(box(track['true_moment_enclosures'][k]), weight) for k in MOM}
    absolute['P_final'] = times(box(track['final_photon']['true_absolute_interval']), weight)
    absolute['anchor'] = times(box(track['summed_true_anchor_eV']), weight)
    correction = {k: times(box(track['cumulative_moment_corrections'][k]['interval']), weight) for k in MOM}
    correction['P_final'] = times(box(track['final_photon']['true_minus_captured_interval']), weight)
    correction['energy_eV'] = times(box(track['final_energy_stock_eV']['true_minus_captured_interval']), weight)
    return {'absolute': totals(absolute), 'correction': totals(correction)}


def compare(old, new):
    wo, wn = width(old), width(new)
    overlap = max(old[0], new[0]) <= min(old[1], new[1])
    return {
        'old': enc(old), 'new_raw': enc(new), 'overlap': overlap,
        'new_subset_old': old[0] <= new[0] <= new[1] <= old[1],
        'old_width': str(wo), 'new_width': str(wn),
        'old_width_decimal': display(wo), 'new_width_decimal': display(wn),
        'width_gain': str(wo - wn), 'width_gain_decimal': display(wo - wn),
        'old_over_new_width': display(wo / wn if wn else None),
        'width_reduction_percent': display(100 * (wo - wn) / wo if wo else None),
        'width_nonincreasing': wn <= wo,
    }


def radius_components(track):
    rows = []
    for seg in track['segments']:
        for metric in ['P1'] + ['H_' + s + '_eV' for s in SP]:
            output = seg['outputs'][metric]
            numeric = F(output['numerical_and_representation_radius'])
            incoming = F(seg['remainder']['incoming_upper'][metric])
            coupling = F(seg['remainder']['nonlinear_upper'][metric])
            full = F(output['radius'])
            slack = full - numeric - incoming - coupling
            if slack < 0:
                raise ValueError('radius assembly misses a component')
            rows.append({'key': seg['key'], 'metric': metric,
                         'numeric_and_representation': str(numeric), 'incoming': str(incoming),
                         'coefficient_coupling': str(coupling), 'outward_assembly_slack': str(slack),
                         'radius': str(full),
                         'numeric_fraction_of_radius': display(numeric / full if full else None),
                         'incoming_fraction_of_radius': display(incoming / full if full else None),
                         'coupling_fraction_of_radius': display(coupling / full if full else None)})
    heat_rows = [r for r in rows if r['metric'].startswith('H_')]
    components = {k: sum((F(r[k]) for r in heat_rows), F(0)) for k in ('numeric_and_representation', 'incoming', 'coefficient_coupling', 'outward_assembly_slack')}
    heat_radius = sum((F(track['cumulative_moment_corrections']['H_' + s + '_eV']['radius']) for s in SP), F(0))
    accumulated = heat_radius - sum(components.values(), F(0))
    if accumulated < 0:
        raise ValueError('cumulative moment radius smaller than propagated components')
    return {'segments': rows,
            'final_photon': next(r for r in rows if r['key'][1] == 2 and r['metric'] == 'P1'),
            'species_sum_cumulative_heat': {**{k: str(v) for k, v in components.items()},
                'accumulation_rounding_slack': str(accumulated), 'radius': str(heat_radius),
                **{k + '_fraction_of_radius': display(v / heat_radius if heat_radius else None) for k, v in components.items()}},
            'interpretation': 'The second photon incoming component already carries first-segment uncertainty. Cumulative heat sums local moment radii without damping previously accumulated moments. Remainder floors are properties of this bound, not lower bounds on true solution error.'}


def analyze(result_path):
    result = read(result_path)
    # Rebuild the explicit numerical projection from the actual result, not
    # merely a supplied digest. This module imports no interval vendor.
    from dominant_complement import projection
    proj = projection(result)
    semantic = hashlib.sha256(b'bass-he-e13c6-off4-semantic-v1\n' + canonical(proj)).hexdigest()
    identity = read(result_path.parent / 'NUMERICAL_IDENTITY.json')
    if identity['semantic_sha256'] != semantic or identity['result_file_sha256'] != sha(result_path):
        raise ValueError('actual result / semantic identity mismatch')
    if result['source_lock_sha256'] != sha(ROOT / 'SOURCE_LOCK.json') or not result['source_unchanged_during_run']:
        raise ValueError('different numerical source lock')
    source_lock = read(ROOT / 'SOURCE_LOCK.json')
    if any(sha(ROOT / k) != v['sha256'] or (ROOT / k).stat().st_size != v['bytes'] for k, v in source_lock['files'].items()):
        raise ValueError('actual source/input bytes changed')
    old_paths = [json.loads(line) for line in (ROOT / 'inputs/OLD_PATHS_OFF4.jsonl').read_text().splitlines()]
    if [p['node'] for p in old_paths] != list(NODES) or [t['track'] for t in result['tracks']] != [{'mode': 'OFF', 'node': n} for n in NODES]:
        raise ValueError('target order mismatch')
    predecessor = read(ROOT / 'inputs/PREDECESSOR_BUDGET.json')
    pairs = []
    old_sum = {'absolute': {}, 'correction': {}}
    new_sum = {'absolute': {}, 'correction': {}}
    checks = {'old_selected_bridges': 0, 'full_predecessor_bridges': 0,
              'path_metric_pairs': 0, 'overlapping_pairs': 0, 'nested_pairs': 0, 'nonincreasing_width_pairs': 0}
    for old, new in zip(old_paths, result['tracks']):
        w = box(old['weight'])[0]
        om, nm = old_metrics(old), new_metrics(new, w)
        comparisons = {}
        for kind in ('absolute', 'correction'):
            if set(om[kind]) != set(nm[kind]) or set(om[kind]) != set(predecessor['budgets'][kind]):
                raise ValueError('observable representation mismatch')
            comparisons[kind] = {}
            for k in sorted(om[kind]):
                cmp = compare(om[kind][k], nm[kind][k])
                comparisons[kind][k] = cmp
                checks['path_metric_pairs'] += 1
                checks['overlapping_pairs'] += int(cmp['overlap'])
                checks['nested_pairs'] += int(cmp['new_subset_old'])
                checks['nonincreasing_width_pairs'] += int(cmp['width_nonincreasing'])
                if not cmp['overlap']:
                    raise ValueError('incompatible same-target intervals: ' + str(old['node']) + '/' + kind + '/' + k)
                old_sum[kind][k] = add(old_sum[kind].get(k, (F(0), F(0))), om[kind][k])
                new_sum[kind][k] = add(new_sum[kind].get(k, (F(0), F(0))), nm[kind][k])
        seam = new['seams'][0]
        dE = box(seam['DeltaE_eV'])
        pairs.append({'mode': 'OFF', 'node': old['node'], 'original_weight': str(w),
                      'metrics': comparisons, 'radius_components': radius_components(new),
                      'signed_seam': {'DeltaE_eV': seam['DeltaE_eV'], 'sign': 'positive' if dE[0] > 0 else 'negative' if dE[1] < 0 else 'contains_zero',
                                      'true_anchor_eV': seam['true_anchor_eV'], 'captured_photon_stitch_residual': seam['captured_photon_stitch_residual'], 'anchored_flag_is_not_a_zero_seam_proof': True}})
    global_values = {}
    for kind, values in predecessor['budgets'].items():
        global_values[kind] = {}
        for k, v in sorted(values.items()):
            old, retained, selected = [box(v[x]) for x in ('predecessor_full', 'retained_outside_K4', 'old_selected_K4')]
            if old_sum[kind][k] != selected:
                raise ValueError('selected old path sum mismatch')
            checks['old_selected_bridges'] += 1
            if add(retained, selected) != old:
                raise ValueError('full baseline bridge mismatch')
            checks['full_predecessor_bridges'] += 1
            new = add(retained, new_sum[kind][k])
            cmp = compare(old, new)
            wo, ws, wn = width(old), width(selected), width(new_sum[kind][k])
            global_values[kind][k] = {**cmp, 'retained_direct': enc(retained),
                'old_selected_K4': enc(selected), 'new_selected_K4_raw': enc(new_sum[kind][k]),
                'retained_count': 2436, 'selected_count': 4,
                'selected_width_reduction_percent': display(100 * (ws - wn) / ws if ws else None),
                'selected_old_over_new_width': display(ws / wn if wn else None),
                'maximum_full_gain_if_selected_zero_percent': display(100 * ws / wo if wo else None),
                'achieved_fraction_of_selected_zero_width_ceiling': display((ws - wn) / ws if ws else None),
                'retained_width_fraction_of_new_full': display(width(retained) / width(new) if width(new) else None),
                'no_interval_subtraction': True, 'intersection_used': False,
                'totals_definition': 'Minkowski sum of three species intervals on both sides'}
    if checks['path_metric_pairs'] != 136 or checks['old_selected_bridges'] != 34 or checks['full_predecessor_bridges'] != 34:
        raise ValueError('incomplete comparison coverage')
    return {'schema': 'bass-he-e13c6-exact-budget-analysis-v1',
            'status': 'PASS_SAME_TARGET_REPLACEMENT_CANDIDATE_PENDING_REVIEW',
            'source_numerical_semantic_sha256': semantic, 'source_lock_sha256': result['source_lock_sha256'],
            'work_unit': result['work_unit'], 'checks': checks, 'paths': pairs, 'global_OFF': global_values,
            'replacement_route': 'direct retained sum of 2434 old OFF nodes plus two already-admitted OFF nodes, then four new weighted same-target intervals',
            'intersection_used': False, 'analysis_scientific_kernel_calls': 0,
            'physical': 'HOLD', 'continuum': 'HOLD', 'production': 'HOLD', 'receiver': 'HOLD',
            'claim_ceiling': 'conditional finite captured OFF enclosures; width improvement is not a change in physical photon/heat yield or an asserted physical accuracy tolerance'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--result', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result = analyze(args.result.resolve())
    output = args.output_dir / 'GLOBAL_ANALYSIS.json'
    save(output, result)
    semantic = hashlib.sha256(b'bass-he-e13c6-budget-semantic-v1\n' + canonical(result)).hexdigest()
    save(args.output_dir / 'ANALYSIS_IDENTITY.json', {'schema': 'bass-he-e13c6-analysis-identity-v1', 'semantic_sha256': semantic, 'canonical_object_sha256': hashlib.sha256(canonical(result)).hexdigest(), 'analysis_file_sha256': sha(output), 'exclusions': [], 'analysis_scientific_kernel_calls': 0})
    rows = []
    for kind, values in result['global_OFF'].items():
        for metric, v in values.items():
            rows.append({'scope': 'full_OFF', 'kind': kind, 'metric': metric,
                         **{k: v[k] for k in ('old_width_decimal', 'new_width_decimal', 'width_reduction_percent', 'old_over_new_width', 'selected_old_over_new_width', 'selected_width_reduction_percent', 'maximum_full_gain_if_selected_zero_percent', 'new_subset_old', 'overlap')}})
    with (args.output_dir / 'GLOBAL_WIDTHS.csv').open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({'status': result['status'], 'checks': result['checks'], 'semantic_sha256': semantic,
                      'photon': result['global_OFF']['absolute']['P_final']['width_reduction_percent'],
                      'heat': result['global_OFF']['absolute']['H_total_eV']['width_reduction_percent']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
