#!/usr/bin/env python3
"""Exact saved PR20 finite budget with two pinned saved N512 replacements.

One streamed path pass. No imports from any scientific producer or predecessor.
The enclosures remain conditional on the reviews of their constituent inputs.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback

MODES = ('OFF', 'KF', 'GM')
SP = ('HI', 'HeI', 'HeII')
SELECTED = (0, 700, 1620, 2344)
REPLACED = (('OFF', 0), ('OFF', 700))
LABELS = ('Z_eV', 'QN', 'QE_eV') + tuple(
    p + '_' + s + ('' if p == 'A' else '_eV') for s in SP for p in ('A', 'B', 'H'))
ABSOLUTE = ('P_final', 'anchor') + LABELS
CORRECTION = ('P_final', 'energy_eV') + LABELS
TOTALS = ('A_total', 'B_total_eV', 'H_total_eV')
METRICS = {'absolute': ABSOLUTE + TOTALS, 'correction': CORRECTION + TOTALS}
PARTITIONS = ('full', 'selected_S4', 'complement_R2436', 'replacement_K2', 'retained_outside_K2')
EPS = F.from_float(1.602176634e-12)
ZERO = (F(0), F(0))
LIMITS = {'processes': 1, 'threads': 1, 'memory_MiB': 1024,
          'wall_seconds': 300, 'stream_passes': 1, 'coefficient_evaluations': 0,
          'ODE_solves': 0, 'native_runs': 0, 'gas_advances': 0, 'automatic_retries': 0}
PINS = {
    'paths': (292932850, '175d8aa96d50965127ac61840991fc69e348e1acbb21e21cfed5eb7947441c94'),
    'full_results': (37367, '29dfaa5408cee99ccbefd25039f42bec80fec8268784cb81fa50920ce3449271'),
    'full_start': (5069, 'a913afb21384d219da34daeaac13e4e48bd92e5fca0499c627ac7fc5081a9403'),
    'full_code': (11898, '1f383e81d928d1afa3ecd5d22391d2a3ea82a289799dd54c9d4a18b741162ff8'),
    'prior': (950019, '418dcac9280947abc227c69f9178c0163bbdb00fa34bff1f9e34ab9eea35ece4'),
    'prior_code': (12327, 'aaae27a0d053d42ce6727593df676352697dd042486aa448d1e9104b16f979f6'),
    'current': (417016, '5a3b9f17c6d250afed0e4270e4cce71d22d930a482084bc12c3e7dcc66cb68d7'),
    'lineage_result': (870091, '2fd04e6c6f300bbe19344fcf7d0e000174241ebd719716f897f8f6c5104d6bd9'),
    'lineage_code': (28050, 'dd8796ae232d3d72384df14263658d1e48e87a8fad6982f64a6ab811ce2eb985'),
}


class ContractFailure(RuntimeError):
    pass


class Audit:
    def __init__(self):
        self.counts = {}
        self.failures = []

    def require(self, category, test, condition, detail=None):
        self.counts[category] = self.counts.get(category, 0) + 1
        if not condition:
            item = {'category': category, 'test': test, 'detail': detail}
            self.failures.append(item)
            raise ContractFailure(json.dumps(item, sort_keys=True, default=str))

    def summary(self):
        return {'check_count': sum(self.counts.values()), 'counts_by_category': self.counts,
                'failed_count': len(self.failures), 'failures': self.failures}


def box(value):
    if isinstance(value, tuple) and len(value) == 2:
        a, b = value
    elif isinstance(value, dict) and set(value) == {'lo', 'hi'}:
        a, b = F(value['lo']), F(value['hi'])
    else:
        raise ContractFailure('INVALID_INTERVAL_SCHEMA')
    if a > b:
        raise ContractFailure('REVERSED_INTERVAL')
    return a, b


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[1], a[1] - b[0]


def sum_boxes(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def scale(value, positive_weight):
    if positive_weight <= 0:
        raise ContractFailure('NONPOSITIVE_WEIGHT')
    return value[0] * positive_weight, value[1] * positive_weight


def width(value):
    return value[1] - value[0]


def contains(outer, inner):
    return outer[0] <= inner[0] and inner[1] <= outer[1]


def overlaps(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])


def sign(value):
    if value[0] > 0:
        return 'STRICT_POSITIVE'
    if value[1] < 0:
        return 'STRICT_NEGATIVE'
    if value == ZERO:
        return 'EXACT_ZERO'
    return 'UNRESOLVED'


def decimal_exact(value):
    """Finite exact decimal where possible, otherwise the exact rational a/b."""
    value = F(value)
    if not value:
        return '0'
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return str(value)
    places = max(twos, fives)
    digits = str(abs(value.numerator) * 2 ** (places - twos) * 5 ** (places - fives))
    if places:
        digits = digits.zfill(places + 1)
        digits = (digits[:-places] + '.' + digits[-places:]).rstrip('0').rstrip('.')
    return ('-' if value < 0 else '') + digits


def encode(value):
    if isinstance(value, F):
        return decimal_exact(value)
    if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, F) for v in value):
        return {'lo': decimal_exact(value[0]), 'hi': decimal_exact(value[1])}
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def canonical(value):
    return json.dumps(encode(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def write_json(path, value, compact=False):
    data = canonical(value) if compact else json.dumps(encode(value), sort_keys=True,
                                                     indent=2, ensure_ascii=False).encode()
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(data + b'\n')
    temporary.replace(path)


def file_identity(path):
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def stable_stat(path):
    stat = path.stat()
    return {'device': stat.st_dev, 'inode': stat.st_ino, 'size': stat.st_size,
            'mtime_ns': stat.st_mtime_ns, 'ctime_ns': stat.st_ctime_ns}


def positive_point(value):
    interval = box(value)
    if not interval[0] == interval[1] > 0:
        raise ContractFailure('WEIGHT_NOT_STRICTLY_POSITIVE_POINT')
    return interval[0]


def validate_key(mode, node, index, n_per_mode=2440, modes=MODES):
    if not isinstance(node, int) or isinstance(node, bool):
        raise ContractFailure('NODE_NOT_INTEGER')
    if index >= n_per_mode * len(modes):
        raise ContractFailure('EXCESS_OR_DUPLICATE_PATH')
    if (mode, node) != (modes[index // n_per_mode], index % n_per_mode):
        raise ContractFailure('KEY_ORDER_DUPLICATE_GAP_OR_MIXED_MODE')


def validate_complete(count, n_per_mode=2440, modes=MODES):
    if count != n_per_mode * len(modes):
        raise ContractFailure('INCOMPLETE_FINITE_COVERAGE')


def expected_segment_keys(mode, node):
    keys = [[mode, 1, node, 0], [mode, 2, node, 0]]
    if node in SELECTED:
        keys.append([mode, 2, node, 1])
    return keys


def add_species_totals(values):
    for prefix, total_name in zip(('A', 'B', 'H'), TOTALS):
        suffix = '' if prefix == 'A' else '_eV'
        values[total_name] = sum_boxes(values[prefix + '_' + s + suffix] for s in SP)
    return values


def old_values(path, w):
    absolute = {metric: box(path['weighted_reduction'][metric]) for metric in ABSOLUTE}
    last = path['segments'][-1]
    correction = {metric: scale(box(path['cumulative_correction'][metric]), w) for metric in LABELS}
    correction['P_final'] = scale(box(last['DP']), w)
    correction['energy_eV'] = scale(box(last['energy_endpoint_minus_captured_erg']), w / EPS)
    return {'absolute': add_species_totals(absolute), 'correction': add_species_totals(correction)}


def new_values(track, w):
    absolute = {metric: scale(box(track['true_moment_enclosures'][metric]), w) for metric in LABELS}
    absolute['P_final'] = scale(box(track['final_photon']['true_absolute_interval']), w)
    absolute['anchor'] = scale(box(track['summed_true_anchor_eV']), w)
    correction = {metric: scale(box(track['cumulative_moment_corrections'][metric]['interval']), w)
                  for metric in LABELS}
    correction['P_final'] = scale(box(track['final_photon']['true_minus_captured_interval']), w)
    correction['energy_eV'] = scale(box(track['final_energy_stock_eV']['true_minus_captured_interval']), w)
    return {'absolute': add_species_totals(absolute), 'correction': add_species_totals(correction)}


def path_character(path):
    return {'mode': path['mode'], 'node': path['node'], 'weight': path['weight'],
            'selected_S4': path['node'] in SELECTED,
            'replacement_K2': (path['mode'], path['node']) in REPLACED,
            'segments': [{'key': s['key'], 'source_on': s['source_on'], 'mask': s['mask'],
                          'anchored': s['anchored'],
                          'energy_min_eV': s['domain']['energy_min_eV'],
                          'energy_max_eV': s['domain']['energy_max_eV'],
                          'origin': s['origin']} for s in path['segments']]}


def same_reused_path(full, prior):
    if set(full) != set(prior):
        return False
    for key in full:
        if key != 'segments' and full[key] != prior[key]:
            return False
    if len(full['segments']) != len(prior['segments']):
        return False
    return all({k: v for k, v in a.items() if k != 'origin'} ==
               {k: v for k, v in b.items() if k != 'origin'}
               for a, b in zip(full['segments'], prior['segments']))


def synthetic_controls():
    checks = []

    def check(name, condition):
        checks.append({'id': name, 'status': 'PASS' if condition else 'FAIL'})
        if not condition:
            raise ContractFailure('TOY_FAILED/' + name)

    def rejected(name, function):
        try:
            function()
        except ContractFailure:
            check(name, True)
        else:
            check(name, False)

    for index, key in enumerate((('OFF', 0), ('OFF', 1), ('KF', 0), ('KF', 1))):
        validate_key(*key, index, 2, ('OFF', 'KF'))
    validate_complete(4, 2, ('OFF', 'KF'))
    check('complete_two_mode_keyed_cover', True)
    rejected('duplicate_rejected', lambda: validate_key('OFF', 0, 1, 2, ('OFF', 'KF')))
    rejected('gap_rejected', lambda: validate_key('OFF', 2, 1, 2, ('OFF', 'KF')))
    rejected('mixed_mode_rejected', lambda: validate_key('KF', 0, 0, 2, ('OFF', 'KF')))
    rejected('incomplete_final_coverage_rejected', lambda: validate_complete(3, 2, ('OFF', 'KF')))
    rejected('negative_weight_rejected', lambda: positive_point({'lo': '-1', 'hi': '-1'}))
    rejected('zero_weight_rejected', lambda: positive_point({'lo': '0', 'hi': '0'}))
    rejected('nonpoint_weight_rejected', lambda: positive_point({'lo': '1', 'hi': '2'}))
    rejected('reversed_interval_rejected', lambda: box({'lo': '2', 'hi': '1'}))
    a, b, new_a = (F(1), F(3)), (F(4), F(5)), (F(3, 2), F(2))
    direct = add(new_a, b)
    subtractive = add(sub(add(a, b), a), new_a)
    check('direct_hybrid_exact', direct == (F(11, 2), F(7)))
    check('interval_subtraction_inflates_width', width(subtractive) == width(direct) + 2 * width(a))
    check('exact_partition_width_additivity', width(add(a, b)) == width(a) + width(b))
    check('fixed_retained_width_floor', width(direct) >= width(b))
    check('weighted_sum', add(scale(a, F(2)), scale(b, F(3))) == (F(14), F(21)))
    check('dropped_weights_detected', add(a, b) != add(scale(a, F(2)), scale(b, F(3))))
    check('swapped_nodes_detected', add(scale(b, F(2)), scale(a, F(3))) !=
          add(scale(a, F(2)), scale(b, F(3))))
    frozen, captured, delta = F(100), F(98), (F(-1), F(-1, 2))
    absolute = add((frozen, frozen), delta)
    corrected_baseline = add(delta, (frozen - captured, frozen - captured))
    check('frozen_to_captured_baseline_bridge', corrected_baseline == (F(1), F(3, 2)))
    check('absolute_and_correction_distinct', absolute != corrected_baseline)
    check('absolute_positive_correction_can_negative', sign((F(2), F(3))) == 'STRICT_POSITIVE'
          and sign((F(-2), F(-1))) == 'STRICT_NEGATIVE')
    check('strict_positive_boundary', sign((F(0), F(1))) == 'UNRESOLVED')
    check('strict_negative_boundary', sign((F(-1), F(0))) == 'UNRESOLVED')
    check('exact_zero', sign(ZERO) == 'EXACT_ZERO')
    check('erg_conversion_once', scale((EPS, 2 * EPS), F(3) / EPS) == (F(3), F(6)))
    check('species_sum_definition', sum_boxes([(F(1), F(2)), (F(2), F(3)), ZERO]) == (F(3), F(5)))
    # Exercise the actual saved-output field mapper, with distinct stock,
    # correction and energy values. These are synthetic exact intervals.
    toy_path = {
        'weighted_reduction': {metric: {'lo': str(i + 10), 'hi': str(i + 11)}
                               for i, metric in enumerate(ABSOLUTE)},
        'cumulative_correction': {metric: {'lo': str(i + 1), 'hi': str(i + 2)}
                                  for i, metric in enumerate(LABELS)},
        'segments': [{'DP': {'lo': '2', 'hi': '3'},
                      'energy_endpoint_minus_captured_erg':
                          {'lo': decimal_exact(EPS * 7), 'hi': decimal_exact(EPS * 8)}}]}
    mapped = old_values(toy_path, F(3))
    check('mapper_absolute_already_weighted', mapped['absolute']['P_final'] == (F(10), F(11)))
    check('mapper_final_DP_weighted_once', mapped['correction']['P_final'] == (F(6), F(9)))
    check('mapper_energy_unit_weight_once', mapped['correction']['energy_eV'] == (F(21), F(24)))
    check('mapper_moment_label_swap_detected', mapped['correction']['Z_eV'] != mapped['correction']['QN'])
    check('mapper_correction_baseline_not_absolute', mapped['correction']['P_final'] != mapped['absolute']['P_final'])
    return {'status': 'PASS_SYNTHETIC_ONLY', 'checks': checks, 'count': len(checks),
            'direct_hybrid': encode(direct), 'subtractive_hybrid': encode(subtractive),
            'science_runs': 0, 'coefficient_evaluations': 0}


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def initialize_sums():
    return {m: {kind: {variant: {partition: {metric: ZERO for metric in metrics}
                                for partition in PARTITIONS}
                      for variant in ('old', 'hybrid')}
                for kind, metrics in METRICS.items()} for m in MODES}


def require_preflight(args, audit):
    paths = {name: getattr(args, name) for name in PINS}
    ids = {}
    for name, (expected_bytes, expected_sha) in PINS.items():
        if name == 'paths':
            ids[name] = {'bytes': paths[name].stat().st_size, 'sha256': expected_sha,
                         'sha256_status': 'PENDING_STREAM_VERIFICATION'}
            audit.require('identity', name + '/size', ids[name]['bytes'] == expected_bytes)
        else:
            ids[name] = file_identity(paths[name])
            audit.require('identity', name, ids[name] == {'bytes': expected_bytes, 'sha256': expected_sha})
    contract = json.loads(args.contract.read_text())
    audit.require('contract', 'schema', contract['schema'] == 'bass-he-e13c5-full-finite-budget-contract-v1')
    audit.require('contract', 'limits', contract['limits'] == LIMITS)
    audit.require('contract', 'pins', contract['pinned_inputs'] ==
                  {k: {'bytes': n, 'sha256': h} for k, (n, h) in PINS.items()})
    audit.require('contract', 'absolute_metrics', contract['absolute_observables'] == list(ABSOLUTE))
    audit.require('contract', 'correction_metrics', contract['correction_observables'] == list(CORRECTION))
    audit.require('contract', 'species_sum_metrics', contract['species_sum_diagnostics'] == list(TOTALS))
    data = {name: json.loads(path.read_text()) for name, path in paths.items()
            if name not in ('paths', 'full_code', 'prior_code', 'lineage_code')}
    full, start, lineage, current = (data[k] for k in ('full_results', 'full_start', 'lineage_result', 'current'))
    audit.require('lineage', 'full_coverage', (full['paths'], full['segments'], full['new_segments'],
                  full['reused_segments']) == (7320, 14652, 14616, 36))
    audit.require('lineage', 'raw_stream_identity', full['PATHS_sha256'] == PINS['paths'][1])
    audit.require('lineage', 'full_source_resolution', start['code_sha256'] == PINS['full_code'][1]
                  and (start['N'], start['precision']) == (128, 60))
    audit.require('lineage', 'prior_producer_in_full_start',
                  PINS['prior'][1] in start['hashes'].values() and PINS['prior_code'][1] in start['hashes'].values())
    audit.require('lineage', 'reviewed_reducer_status', lineage['status'] == 'PASS_SCOPED_POSTPROCESSING'
                  and lineage['failed_count'] == 0 and lineage['disjoint_count'] == 0)
    audit.require('lineage', 'reviewed_reducer_source', lineage['source_sha256'] == PINS['lineage_code'][1])
    audit.require('lineage', 'reviewed_reducer_prior_current',
                  lineage['inputs']['prior']['sha256'] == PINS['prior'][1]
                  and lineage['inputs']['current']['sha256'] == PINS['current'][1])
    audit.require('lineage', 'N512_source_contract', current['identity']['subdivisions'] == 512
                  and current['identity']['precision_digits'] == 60
                  and lineage['current_numerical_contract']['source_sha256_before_run'] ==
                  current['identity']['source_sha256_before_run'])
    audit.require('lineage', 'N512_no_native_gas', all(current['identity'][k] == 0 for k in
                  ('native_runs', 'gas_advances', 'old_continuous_solves')))
    audit.require('lineage', 'N512_exactly_two_tracks',
                  [(t['track']['mode'], t['track']['node']) for t in current['tracks']] == list(REPLACED))
    prior_by = {(p['mode'], p['node']): p for p in data['prior']['paths']}
    audit.require('lineage', 'prior_12_keys', len(prior_by) == len(data['prior']['paths']) == 12
                  and set(prior_by) == {(m, n) for m in MODES for n in SELECTED})
    new_by = {}
    lineage_by = {(p['mode'], p['node']): p for p in lineage['hybrid']['path_terms']}
    for track in current['tracks']:
        key = (track['track']['mode'], track['track']['node'])
        old = prior_by[key]
        w = positive_point(old['weight'])
        audit.require('lineage', str(key) + '/segment_keys',
                      [s['key'] for s in track['segments']] == expected_segment_keys(*key))
        new_by[key] = new_values(track, w)
        for metric in ABSOLUTE:
            audit.require('replacement_bridge', str(key) + '/' + metric,
                          new_by[key]['absolute'][metric] == box(lineage_by[key]['weighted_reduction'][metric]))
        audit.require('replacement_bridge', str(key) + '/provenance',
                      lineage_by[key]['provenance'] == 'CURRENT_N512_REPLACEMENT')
        audit.require('replacement_bridge', str(key) + '/preserved_baseline',
                      lineage_by[key]['preserved_captured_segments'] == [s['captured'] for s in old['segments']])
    return paths, ids, data, prior_by, new_by


def run_stream(args, audit, prior_by, new_by, started):
    sums = initialize_sums()
    rows = {m: {kind: {metric: [] for metric in metrics} for kind, metrics in METRICS.items()} for m in MODES}
    sign_counts = {m: {kind: {metric: {v: {s: 0 for s in ('STRICT_POSITIVE', 'STRICT_NEGATIVE',
                  'EXACT_ZERO', 'UNRESOLVED')} for v in ('old', 'hybrid')} for metric in metrics}
                  for kind, metrics in METRICS.items()} for m in MODES}
    characters = {m: {} for m in MODES}
    digest = hashlib.sha256()
    byte_count = path_count = segment_count = reused_count = replacements = 0
    stat_before = stable_stat(args.paths)
    with args.paths.open('rb') as stream:
        for raw in stream:
            digest.update(raw)
            byte_count += len(raw)
            path = json.loads(raw)
            mode, node = path['mode'], path['node']
            validate_key(mode, node, path_count)
            audit.require('coverage', f'{mode}/{node}/key', True)
            key = mode, node
            segments = path['segments']
            audit.require('coverage', f'{mode}/{node}/segment_keys',
                          [s['key'] for s in segments] == expected_segment_keys(mode, node))
            expected_origin = 'REUSED_REVIEWED_PR19' if node in SELECTED else 'NEW'
            audit.require('coverage', f'{mode}/{node}/origin', all(s['origin'] == expected_origin for s in segments))
            w = positive_point(path['weight'])
            audit.require('weights', f'{mode}/{node}', True)
            if node in SELECTED:
                audit.require('reused_path_identity', f'{mode}/{node}', same_reused_path(path, prior_by[key]))
                reused_count += len(segments)
            old = old_values(path, w)
            new = new_by[key] if key in new_by else old
            characters[mode][node] = path_character(path)
            membership = ['full', 'selected_S4' if node in SELECTED else 'complement_R2436',
                          'replacement_K2' if key in new_by else 'retained_outside_K2']
            if key in new_by:
                replacements += 1
            for kind, metrics in METRICS.items():
                for metric in metrics:
                    a, b = old[kind][metric], new[kind][metric]
                    audit.require('used_interval_order', f'{mode}/{node}/{kind}/{metric}', a[0] <= a[1] and b[0] <= b[1])
                    if key in new_by:
                        audit.require('replacement_consistency', f'{mode}/{node}/{kind}/{metric}', overlaps(a, b))
                    ow, nw = width(a), width(b)
                    rows[mode][kind][metric].append((node, ow, nw))
                    sign_counts[mode][kind][metric]['old'][sign(a)] += 1
                    sign_counts[mode][kind][metric]['hybrid'][sign(b)] += 1
                    for partition in membership:
                        sums[mode][kind]['old'][partition][metric] = add(sums[mode][kind]['old'][partition][metric], a)
                        sums[mode][kind]['hybrid'][partition][metric] = add(sums[mode][kind]['hybrid'][partition][metric], b)
            path_count += 1
            segment_count += len(segments)
            if path_count % 500 == 0:
                elapsed = time.monotonic() - started
                write_json(args.out / 'CHECKPOINT.json', {'completed_paths': path_count,
                           'completed_segments': segment_count, 'stream_bytes': byte_count,
                           'last_key': [mode, node], 'elapsed_seconds': elapsed})
                print(json.dumps({'paths': path_count, 'segments': segment_count, 'elapsed_seconds': elapsed}), flush=True)
    validate_complete(path_count)
    audit.require('coverage', 'final_segment_count', segment_count == 14652)
    audit.require('coverage', 'reused_segments', reused_count == 36)
    audit.require('coverage', 'replacement_count', replacements == 2)
    raw_id = {'bytes': byte_count, 'sha256': digest.hexdigest()}
    audit.require('identity', 'raw_stream_final_hash_size', raw_id ==
                  {'bytes': PINS['paths'][0], 'sha256': PINS['paths'][1]})
    audit.require('identity', 'raw_stream_metadata_unchanged', stable_stat(args.paths) == stat_before)
    return sums, rows, sign_counts, characters, raw_id, {
        'paths': path_count, 'segments': segment_count, 'reused_segments': reused_count,
        'replacement_paths': replacements, 'retained_paths': path_count - replacements,
        'paths_per_mode': {m: 2440 for m in MODES}, 'selected_per_mode': 4,
        'complement_per_mode': 2436, 'stream_passes': 1,
        'new_path_solves': 0, 'new_coefficients': 0, 'new_native_or_gas_runs': 0}


def summarize(args, audit, sums, rows, sign_counts, characters):
    budgets = {m: {} for m in MODES}
    ranks_path = args.out / 'WIDTH_RANKINGS.csv.gz'
    with ranks_path.open('xb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding='utf-8', newline='') as text_stream:
                writer = csv.writer(text_stream, lineterminator='\n')
                writer.writerow(('mode', 'kind', 'quantity', 'node', 'rank_old', 'rank_hybrid',
                                 'old_width_exact', 'hybrid_width_exact', 'selected_S4', 'replacement_K2'))
                for mode in MODES:
                    for kind, metrics in METRICS.items():
                        budgets[mode][kind] = {}
                        for metric in metrics:
                            old_parts = {p: sums[mode][kind]['old'][p][metric] for p in PARTITIONS}
                            new_parts = {p: sums[mode][kind]['hybrid'][p][metric] for p in PARTITIONS}
                            for variant, parts in (('old', old_parts), ('hybrid', new_parts)):
                                audit.require('partition_identity', f'{mode}/{kind}/{metric}/{variant}/S+R',
                                              parts['full'] == add(parts['selected_S4'], parts['complement_R2436']))
                                audit.require('partition_identity', f'{mode}/{kind}/{metric}/{variant}/K+retained',
                                              parts['full'] == add(parts['replacement_K2'], parts['retained_outside_K2']))
                            audit.require('unchanged_retained', f'{mode}/{kind}/{metric}',
                                          old_parts['retained_outside_K2'] == new_parts['retained_outside_K2']
                                          and old_parts['complement_R2436'] == new_parts['complement_R2436'])
                            ow, nw = width(old_parts['full']), width(new_parts['full'])
                            floor = width(old_parts['retained_outside_K2'])
                            old_k = width(old_parts['replacement_K2'])
                            new_k = width(new_parts['replacement_K2'])
                            audit.require('width_budget', f'{mode}/{kind}/{metric}/gain_identity', ow - nw == old_k - new_k)
                            audit.require('width_budget', f'{mode}/{kind}/{metric}/floor_identity', ow == floor + old_k and nw == floor + new_k)
                            audit.require('width_budget', f'{mode}/{kind}/{metric}/same_target_overlap',
                                          overlaps(old_parts['full'], new_parts['full']))
                            if mode != 'OFF':
                                audit.require('mode_isolation', f'{mode}/{kind}/{metric}', old_parts == new_parts)
                            metric_rows = rows[mode][kind][metric]
                            orders = {v: sorted(metric_rows, key=lambda x: (-x[i], x[0]))
                                      for v, i in (('old', 1), ('hybrid', 2))}
                            rank_maps = {v: {row[0]: index + 1 for index, row in enumerate(order)}
                                         for v, order in orders.items()}
                            concentration = {}
                            for variant, i, total_width in (('old', 1, ow), ('hybrid', 2, nw)):
                                order = orders[variant]
                                row_width_sum = sum((r[i] for r in metric_rows), F(0))
                                audit.require('ranking', f'{mode}/{kind}/{metric}/{variant}/width_sum', row_width_sum == total_width)
                                concentration[variant] = {
                                    'denominator_status': 'POSITIVE_FULL_WIDTH' if total_width else 'ZERO_FULL_WIDTH',
                                    'top_width_fractions': {str(k): ratio(sum((r[i] for r in order[:k]), F(0)), total_width)
                                                            for k in (1, 2, 4, 10, 100)},
                                    'top10': [{'rank': index + 1, 'node': row[0], 'width': row[i],
                                               'fraction_of_full_width': ratio(row[i], total_width),
                                               'old_width': row[1], 'hybrid_width': row[2],
                                               'character': characters[mode][row[0]]}
                                              for index, row in enumerate(order[:10])]}
                            for node, old_width, new_width in metric_rows:
                                writer.writerow((mode, kind, metric, node, rank_maps['old'][node],
                                                 rank_maps['hybrid'][node], decimal_exact(old_width),
                                                 decimal_exact(new_width), int(node in SELECTED),
                                                 int((mode, node) in REPLACED)))
                            budgets[mode][kind][metric] = {
                                'old': old_parts, 'hybrid': new_parts,
                                'width': {'old_full': ow, 'hybrid_full': nw, 'actual_gain': ow - nw,
                                          'old_over_hybrid': ratio(ow, nw), 'gain_fraction_of_old_full': ratio(ow - nw, ow),
                                          'old_K2': old_k, 'hybrid_K2': new_k,
                                          'old_K2_max_gain_at_zero_width': old_k,
                                          'further_K2_max_gain_at_zero_width': new_k,
                                          'fixed_retained_route_floor': floor,
                                          'floor_fraction_of_old_full': ratio(floor, ow),
                                          'old_selected_S4': width(old_parts['selected_S4']),
                                          'hybrid_selected_S4': width(new_parts['selected_S4']),
                                          'complement_R2436': width(old_parts['complement_R2436']),
                                          'old_selected_fraction': ratio(width(old_parts['selected_S4']), ow),
                                          'hybrid_selected_fraction': ratio(width(new_parts['selected_S4']), nw),
                                          'old_complement_fraction': ratio(width(old_parts['complement_R2436']), ow),
                                          'hybrid_complement_fraction': ratio(width(new_parts['complement_R2436']), nw)},
                                'consistency': {'full_overlap': overlaps(old_parts['full'], new_parts['full']),
                                                'old_full_contains_hybrid': contains(old_parts['full'], new_parts['full']),
                                                'hybrid_full_contains_old': contains(new_parts['full'], old_parts['full'])},
                                'full_sign': {'old': sign(old_parts['full']), 'hybrid': sign(new_parts['full'])},
                                'path_sign_counts': sign_counts[mode][kind][metric],
                                'concentration': concentration}
    return budgets, file_identity(ranks_path)


def published_aggregate_comparison(full_results, budgets, audit):
    """Compare distinct outward-rounded summation routes without cancellation.

    The final stock is step 2 only. The moments are transactions summed over
    steps 1 and 2. Per-step anchor omits the cross-step seam and is not compared.
    """
    comparisons = {}
    for mode in MODES:
        steps = full_results['all_node_per_step'][mode]
        published = {metric: add(box(steps['1'][metric]), box(steps['2'][metric]))
                     for metric in LABELS}
        published['P_final'] = box(steps['2']['P_endpoint'])
        add_species_totals(published)
        comparisons[mode] = {}
        for metric, interval in published.items():
            direct = budgets[mode]['absolute'][metric]['old']['full']
            hybrid = budgets[mode]['absolute'][metric]['hybrid']['full']
            audit.require('published_aggregate_bridge', mode + '/' + metric,
                          overlaps(interval, direct) and overlaps(interval, hybrid))
            comparisons[mode][metric] = {
                'published_interval': interval,
                'published_definition': 'step2 final endpoint stock' if metric == 'P_final'
                                         else 'sum of step1 and step2 transactions',
                'direct_path_sum': direct,
                'published_contains_direct_path_sum': contains(interval, direct),
                'direct_path_sum_contains_published': contains(direct, interval),
                'published_width_minus_direct_path_sum_width': width(interval) - width(direct),
                'published_width_minus_direct_definition': 'signed summation-route width difference; not a missing-node error estimate',
                'published_contains_hybrid_path_sum': contains(interval, hybrid),
                'both_routes_overlap': True}
    return {'by_mode': comparisons,
            'anchor_excluded_reason': 'Published per-step anchors omit the inter-step seam included by whole-path anchor.',
            'corrections_excluded_reason': 'PR20 per-step published entries are absolute and native aggregate baselines require distinct representation bridges.',
            'not_used_for_hybrid_replacement': True}


def timeout_handler(signum, frame):
    raise ContractFailure('WALL_RESOURCE_LIMIT_300_SECONDS')


def execute(args):
    if args.out.exists():
        raise ContractFailure('FRESH_OUTPUT_DIRECTORY_REQUIRED')
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    audit = Audit()
    terminal = 'FAIL'
    source_before = file_identity(Path(__file__).resolve())
    contract_before = file_identity(args.contract) if args.contract else None
    start = {'schema': 'bass-he-e13c5-full-budget-start-v1',
             'started_utc': datetime.now(timezone.utc).isoformat(), 'command_argv': sys.argv,
             'python': platform.python_version(), 'platform': platform.platform(),
             'source': source_before, 'contract': contract_before, 'limits': LIMITS,
             'execution_kind': 'SYNTHETIC_CONTROLS_ONLY' if args.controls_only else 'SAVED_RESULT_POSTPROCESSING',
             'new_coefficients': 0, 'new_native_or_gas_or_ODE_runs': 0}
    write_json(args.out / 'START.json', start)
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 ** 2, 1024 * 1024 ** 2))
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(300)
    try:
        controls = synthetic_controls()
        write_json(args.out / 'CONTROLS.json', controls)
        if args.controls_only:
            terminal = controls['status']
            print(json.dumps({'status': terminal, 'controls': controls['count']}), flush=True)
            return 0
        paths, identities, data, prior_by, new_by = require_preflight(args, audit)
        start['input_locations'] = {k: str(v.resolve()) for k, v in paths.items()}
        start['input_identities_before'] = identities
        write_json(args.out / 'START.json', start)
        sums, rows, sign_counts, characters, raw_identity, coverage = run_stream(args, audit, prior_by, new_by, started)
        identities['paths'] = raw_identity
        budgets, ranking_id = summarize(args, audit, sums, rows, sign_counts, characters)
        published_comparison = published_aggregate_comparison(data['full_results'], budgets, audit)
        for name, path in paths.items():
            if name != 'paths':
                audit.require('post_identity', name, file_identity(path) == identities[name])
        audit.require('post_identity', 'reducer_source', file_identity(Path(__file__).resolve()) == source_before)
        audit.require('post_identity', 'contract', file_identity(args.contract) == contract_before)
        terminal = 'PASS_SCOPED_SAVED_FULL_FINITE_BUDGET'
        projection = {
            'schema': 'bass-he-e13c5-full-finite-budget-numerical-projection-v1',
            'node': 'HE_E13C5_FULL_FINITE_BUDGET_AND_COMPLEMENT01', 'status': terminal,
            'source_sha256': source_before['sha256'], 'contract_sha256': contract_before['sha256'],
            'input_identities': identities, 'coverage': coverage, 'audit': audit.summary(),
            'synthetic_controls': controls, 'budgets_by_mode': budgets,
            'published_PR20_aggregate_comparison': published_comparison,
            'replacement_terms': [{'mode': mode, 'node': node, 'terms': new_by[(mode, node)]}
                                  for mode, node in REPLACED],
            'ranking_artifact': {'file': 'WIDTH_RANKINGS.csv.gz', **ranking_id,
                                 'rows': 7320 * (len(METRICS['absolute']) + len(METRICS['correction'])),
                                 'format': 'UTF-8 CSV, deterministic gzip mtime=0, exact widths and ranks by node'},
            'arithmetic': 'Exact Fraction endpoints; positive captured point weights; one exact binary64 erg/eV conversion for old correction energy',
            'finite_cover_status': 'DONE_INHERITED_PR20_ALL_2440_NODES_PER_MODE',
            'species_totals_definition': 'SUM_OF_SPECIES_INTERVALS; dedicated total certificates not substituted',
            'floor_scope': 'Fixed retained per-path Minkowski route only; not a universal floor for correlated/global/direct-total certificates',
            'correction_baseline': 'continuous minus captured segment moments or final captured segment stock; not native full aggregate correction',
            'intersection_used': False, 'mode_mixing': False, 'cross_mode_total': None,
            'new_coefficient_evaluations': 0, 'new_ODE_native_or_gas_runs': 0,
            'conditionality': 'Conditional on the already reviewed constituent interval enclosures and fixed captured model inputs. Reuse and overlap are consistency checks, not a new physical validation.',
            'holds': ['continuum_spectral_quadrature_error', 'physical_global_admission', 'production',
                      'new_gas_evolution', 'actual_photon_heat_recoil_delivery', 'receiver_adoption',
                      'new_full_first2_rerun'],
        }
        projection_bytes = canonical(projection)
        projection_file = projection_bytes + b'\n'
        projection_sha = hashlib.sha256(projection_bytes).hexdigest()
        projection_file_sha = hashlib.sha256(projection_file).hexdigest()
        (args.out / 'NUMERICAL_PROJECTION.json').write_bytes(projection_file)
        numerical_id = {'bytes': len(projection_file), 'sha256': projection_file_sha,
                        'canonical_object_sha256': projection_sha,
                        'definition': 'canonical sorted compact UTF-8 JSON; object digest excludes trailing newline; file digest includes it',
                        'excluded': ['absolute input paths', 'argv', 'host', 'runtime', 'timestamps', 'RSS'],
                        'included': 'all nine immutable input identities, exact partitions, budget metrics, sign results, ranking artifact identity and scoped checks'}
        write_json(args.out / 'NUMERICAL_IDENTITY.json', numerical_id)
        result = {**projection, 'runtime_start': start, 'numerical_identity': numerical_id,
                  'finished_utc': datetime.now(timezone.utc).isoformat()}
        write_json(args.out / 'RESULTS.json', result)
        write_json(args.out / 'CHECKPOINT.json', {'terminal': terminal, **coverage,
                   'elapsed_seconds': time.monotonic() - started})
        print(json.dumps({'status': terminal, 'coverage': coverage, 'checks': audit.summary(),
                          'numerical_identity': numerical_id}), flush=True)
        return 0
    except BaseException as exc:
        terminal = 'FAIL'
        write_json(args.out / 'FAILURE.json', {'status': terminal, 'exception_type': type(exc).__name__,
                   'message': str(exc), 'audit': audit.summary(),
                   'traceback': traceback.format_exc(), 'automatic_retry': False})
        print(json.dumps({'status': terminal, 'message': str(exc)}), file=sys.stderr, flush=True)
        return 1
    finally:
        signal.alarm(0)
        used = resource.getrusage(resource.RUSAGE_SELF)
        write_json(args.out / 'RESOURCE_RECEIPT.json', {
            'status': terminal, 'wall_seconds': time.monotonic() - started,
            'user_cpu_seconds': used.ru_utime, 'system_cpu_seconds': used.ru_stime,
            'max_RSS_KiB': used.ru_maxrss, 'limits': LIMITS,
            'host_kind': 'CALLER_PROVIDED_HOST_NOT_ATTESTED_AS_NCP',
            'execution_kind': start['execution_kind'], 'automatic_retry': False})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument('--' + name.replace('_', '-'), dest=name, type=Path)
    parser.add_argument('--contract', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    if not args.controls_only:
        missing = [name for name in (*PINS, 'contract') if getattr(args, name) is None]
        if missing:
            parser.error('required for saved analysis: ' + ', '.join(missing))
    return execute(args)


if __name__ == '__main__':
    raise SystemExit(main())
