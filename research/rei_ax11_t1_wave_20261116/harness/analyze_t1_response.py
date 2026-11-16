#!/usr/bin/env python3
"""Consume existing T0 samples and new T1 native brackets, without evolution."""
import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
OBS = ['x_HI', 'x_HII', 'x_HeI', 'x_HeII', 'x_HeIII', 'xe_per_H', 'temperature_K']
YEAR_S = 31557600.


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def owner_module():
    path = REPO / 'research/rei_axbi_owner_loop_20261115/physics_consumer.py'
    assert sha(path) == '36ab1556010cd182790e924b1042227b36496c7a17d6d55ddfbff5935a58cfb8'
    spec = importlib.util.spec_from_file_location('original_owner_physics_consumer', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def interpolate_window(owner, data, mode, item):
    """Reproduce owner interp(t,t_native,ln_a) then interp(ln_a,ln_a_native,X)."""
    headers = data['headers']
    columns = {key: np.array([row[i] for row in item['rows']], dtype=float)
               for i, key in enumerate(headers) if key != 'case_id'}
    u = np.log(columns['a'])
    assert len(u) >= 2 and np.all(np.diff(u) > 0)
    columns['xe_per_H'] = columns['ne_proper_cm3'] / columns['nH_proper_cm3']
    if mode == 'fixed_a':
        query = item['query']['ln_a']
        query_alt = query
    else:
        query = float(owner.interp(item['query']['elapsed_time_s'], columns['time_s'], u))
        target = np.clip(item['query']['elapsed_time_s'], columns['time_s'][0], columns['time_s'][-1])
        query_alt = float(PchipInterpolator(columns['time_s'], u)(target))
    tolerance = 8 * np.finfo(float).eps * max(1., abs(u[0]), abs(u[-1]))
    assert u[0] - tolerance <= query <= u[-1] + tolerance, 'NO_EXTRAPOLATION'
    query = float(np.clip(query, u[0], u[-1]))
    query_alt = float(np.clip(query_alt, u[0], u[-1]))
    primary = {field: float(owner.interp(query, u, columns[field]))
               for field in OBS + ['time_s']}
    alternative = {field: float(PchipInterpolator(u, columns[field])(query_alt))
                   for field in OBS}
    primary.update(a=float(np.exp(query)), zbar=float(np.exp(-query) - 1), ln_a=query)
    assert all(np.isfinite(value) for value in primary.values())
    return primary, alternative


def extrema(values, coordinates):
    values = np.asarray(values, dtype=float)
    assert len(values) and np.isfinite(values).all()
    i = int(np.argmax(np.abs(values)))
    return {'sampled_max_abs': float(abs(values[i])), 'signed_value_at_peak': float(values[i]),
            'peak_coordinate': float(coordinates[i]), 'sample_index': i,
            'last_represented_value': float(values[-1])}


def write_csv(path, rows):
    assert rows and not path.exists()
    if path.suffix == '.gz':
        import io
        with path.open('xb') as stream:
            with gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=0) as packed:
                with io.TextIOWrapper(packed, encoding='utf-8', newline='') as text:
                    writer = csv.DictWriter(text, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
    else:
        with path.open('x', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def compare_mode(owner, contract, native, baseline, mode, output):
    windows = {case: {item['query']['index']: item for item in
                     native[case]['samples'][mode]['windows']} for case in ['ZERO', 'PLUS']}
    ids = sorted(set(windows['ZERO']) & set(windows['PLUS']))
    assert ids == list(range(len(ids))), 'common samples must be an initial domain, without gaps'
    rows = []
    for i in ids:
        old = baseline[mode][i]
        a, ap = interpolate_window(owner, native['ZERO'], mode, windows['ZERO'][i])
        b, bp = interpolate_window(owner, native['PLUS'], mode, windows['PLUS'][i])
        row = {'sample_index': i, 'coordinate': float(old['coordinate']),
               'T1_ZERO_a': a['a'], 'T1_PLUS_a': b['a'],
               'T1_ZERO_zbar': a['zbar'], 'T1_PLUS_zbar': b['zbar'],
               'T1_ZERO_time_s': a['time_s'], 'T1_PLUS_time_s': b['time_s']}
        if mode == 'fixed_a':
            row['zbar'] = float(old['zbar'])
        else:
            row['elapsed_time_s'] = float(old['elapsed_time_s'])
        for field in OBS:
            z0, p0 = float(old[field + '_zero']), float(old[field + '_plus'])
            delta0 = float(old[field + '_plus_response'])
            assert delta0 == p0 - z0, 'published signed response identity'
            delta1 = b[field] - a[field]
            change = delta1 - delta0
            for suffix, value in [
                ('T0_ZERO', z0), ('T1_ZERO', a[field]), ('D01_ZERO', a[field] - z0),
                ('T0_PLUS', p0), ('T1_PLUS', b[field]), ('D01_PLUS', b[field] - p0),
                ('response_T0', delta0), ('response_T1', delta1), ('D01_pair', change),
                ('T1_pair_PCHIP_minus_linear', (bp[field] - ap[field]) - delta1),
                ('T1_ZERO_PCHIP_minus_linear', ap[field] - a[field]),
                ('T1_PLUS_PCHIP_minus_linear', bp[field] - b[field]),
            ]:
                row[field + '_' + suffix] = value
        rows.append(row)
    assert rows
    coords = [row['coordinate'] for row in rows]
    summary = {}
    for field in OBS:
        floor = contract['observable_mapping'][field]['original_response_floor']
        metrics = {suffix: extrema([row[field + '_' + suffix] for row in rows], coords)
                   for suffix in ['D01_ZERO', 'D01_PLUS', 'D01_pair', 'response_T0', 'response_T1',
                                  'T1_pair_PCHIP_minus_linear',
                                  'T1_ZERO_PCHIP_minus_linear', 'T1_PLUS_PCHIP_minus_linear']}
        represented = [row for row in rows if abs(row[field + '_response_T1']) >= floor]
        ratios = [abs(row[field + '_D01_pair'] / row[field + '_response_T1']) for row in represented]
        metrics.update(original_response_floor=floor, samples_above_response_floor=len(represented),
                       two_level_change_target_fraction=.1,
                       samples_above_floor_with_two_level_change_below_target=sum(v <= .1 for v in ratios),
                       maximum_two_level_change_over_response_above_floor=max(ratios) if ratios else None,
                       all_represented_above_floor_two_level_changes_below_target=
                           all(v <= .1 for v in ratios) if ratios else None,
                       interpretation='Two-level changes only. D12/order/error bound remain unavailable.')
        summary[field] = metrics
    write_csv(output / f'comparison_{mode}.csv.gz', rows)
    return {'rows': len(rows), 'baseline_rows': len(baseline[mode]),
            'represented_coordinate_domain': [coords[0], coords[-1]],
            'excluded_queries': len(baseline[mode]) - len(rows), 'observables': summary}


def milestone_rows(native):
    old = {}
    for name in ['research/rei_axbi_owner_loop_20261115/results/milestones.csv',
                 'research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/fifth_milestones.csv']:
        with (REPO / name).open() as stream:
            for row in csv.DictReader(stream):
                if row['case'] in ['ZERO', 'SHEAR_PLUS']:
                    case = 'PLUS' if row['case'] == 'SHEAR_PLUS' else 'ZERO'
                    old[(case, str(float(row['x_HII_level'])))] = row
    rows = []
    for case, data in native.items():
        keys = {key: i for i, key in enumerate(data['headers'])}
        for label, item in data['milestones'].items():
            lo, hi = item['rows']
            f = (item['level'] - lo[keys['x_HII']]) / (hi[keys['x_HII']] - lo[keys['x_HII']])
            u = (1 - f) * np.log(lo[keys['a']]) + f * np.log(hi[keys['a']])
            t = (1 - f) * lo[keys['time_s']] + f * hi[keys['time_s']]
            temperature = (1 - f) * lo[keys['temperature_K']] + f * hi[keys['temperature_K']]
            baseline = old[(case, label)]
            rows.append({'case': case, 'x_HII_level': item['level'], 'T0_time_s': float(baseline['time_s']),
                         'T1_time_s': t, 'D01_time_years': (t - float(baseline['time_s'])) / YEAR_S,
                         'T0_zbar': float(baseline['zbar']), 'T1_zbar': float(np.exp(-u) - 1),
                         'D01_zbar': float(np.exp(-u) - 1) - float(baseline['zbar']),
                         'T0_temperature_K': float(baseline['temperature_K']),
                         'T1_temperature_K': temperature,
                         'T1_native_bracket_years': (hi[keys['time_s']] - lo[keys['time_s']]) / YEAR_S,
                         'T1_lower_row': item['lower_row'], 'T1_upper_row': item['upper_row']})
    return rows


def crossing_rows(native):
    rows = []
    for case, data in native.items():
        keys = {key: i for i, key in enumerate(data['headers'])}
        for label, crossings in data['all_upward_crossings'].items():
            for ordinal, item in enumerate(crossings, start=1):
                lo, hi = item['rows']
                f = (float(label) - lo[keys['x_HII']]) / (hi[keys['x_HII']] - lo[keys['x_HII']])
                u = (1 - f) * np.log(lo[keys['a']]) + f * np.log(hi[keys['a']])
                t = (1 - f) * lo[keys['time_s']] + f * hi[keys['time_s']]
                rows.append({'case': case, 'x_HII_level': float(label), 'upward_crossing': ordinal,
                             'zbar': float(np.exp(-u) - 1), 'elapsed_time_s': t,
                             'native_lower_row': item['lower_row'], 'native_upper_row': item['upper_row']})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('native_input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    begin, cpu = time.monotonic(), time.process_time()
    contract = json.loads((UNIT / 'receipts/BASELINE_REUSE.json').read_text())
    grid_sha = sha(UNIT / 'inputs/SAMPLING_GRID.json')
    receipt = json.loads((args.native_input / 'EXTRACTION_RECEIPT.json').read_text())
    specs = {item['case']: item for item in receipt['cases']}
    baseline, native = {}, {}
    for mode, spec in contract['tables'].items():
        path = REPO / spec['repo_relative_path']
        assert sha(path) == spec['sha256']
        with gzip.open(path, 'rt') as stream:
            baseline[mode] = list(csv.DictReader(stream))
    for case in ['ZERO', 'PLUS']:
        path = args.native_input / (case + '_sample_brackets.json.gz')
        assert sha(path) == specs[case]['sha256']
        with gzip.open(path, 'rt') as stream:
            native[case] = json.load(stream)
        assert native[case]['grid_sha256'] == grid_sha
    owner = owner_module()
    args.output.mkdir()
    modes = {mode: compare_mode(owner, contract, native, baseline, mode, args.output)
             for mode in ['fixed_a', 'fixed_t']}
    milestones = milestone_rows(native)
    if milestones:
        write_csv(args.output / 'milestone_T0_T1.csv', milestones)
    crossings = crossing_rows(native)
    if crossings:
        write_csv(args.output / 'all_upward_crossings_T1.csv', crossings)
    result = {
        'status': 'T0_T1_NATIVE_RESPONSE_COMPARISON_COMPLETE_AT_REPRESENTED_SCOPE',
        'baseline_source_pin': contract['source_pin'], 'grid_sha256': grid_sha,
        'native_inputs': {case: {'sha256': specs[case]['sha256'],
                               'rows': native[case]['composed_rows'],
                               'endpoint_reached': native[case]['endpoint_reached']}
                          for case in ['ZERO', 'PLUS']},
        'modes': modes, 'milestones': milestones,
        'upward_crossing_counts': {case: {level: len(items) for level, items in
                                        data['all_upward_crossings'].items()}
                                  for case, data in native.items()},
        'scientific_status': 'numerically checked two-level discrepancies; evolution error bound unresolved',
        'T2_full_history_available': False, 'observed_order': None,
        'full_AX11_complete': False, 'original_DAG': '10/17', 'expansion_DAG': '28/88',
        'scope_limits': ['sampled maxima only, not a continuous supremum',
                         'PCHIP contrast changes T1 interpolation only; it is not an error bound',
                         'small paired discrepancy can coexist with larger common-mode state changes',
                         'dt two-level evidence does not close the dt/dE/dmu three-level requirement'],
        'consumer': 'REI scientific admission owner / AX11',
        'CPU_s': time.process_time() - cpu, 'wall_s': time.monotonic() - begin,
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'script_sha256': sha(__file__),
    }
    (args.output / 'SUMMARY.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': result['status'], 'modes': {k: v['rows'] for k, v in modes.items()},
                      'milestones': len(milestones), 'wall_s': result['wall_s']}))


if __name__ == '__main__':
    main()
