#!/usr/bin/env python3
"""Independent exact replay of saved intervals; does not import candidate code.

This checks the new reduction, conditional on inherited enclosure validity.
No coefficient evaluation, exp, ODE, native, gas or N512 execution occurs.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import resource
import time

F = Fraction
ROOT = Path('/workspace/scratch/7fd51143e473')
PKG = ROOT / 'BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1'
OUT = PKG / 'evidence/independent_review'
PR20 = ROOT / 'e13c5b_materialization_repair01/tmp/HE-E13C5-full-first2-reviewed-20261011/research/e13c5_full_first2_20261011'
PR19 = ROOT / 'BASS_HE_E13C5_INCOMING_ANCHOR_ENCLOSURE_20261011_v1'
INPUTS = {
    'paths': PR20 / 'runs/EXEC01/PATHS.jsonl',
    'full_results': PR20 / 'runs/EXEC01/RESULTS.json',
    'full_start': PR20 / 'runs/EXEC01/START.json',
    'full_code': PR20 / 'full_first2.py',
    'prior': PR19 / 'inputs/pr19_lineage/first2/RESULTS.json',
    'prior_code': PR19 / 'inputs/pr19_lineage/first2/cover.py',
    'current': PR19 / 'evidence/N512_P60.json',
    'lineage_result': PR19 / 'evidence/lineage_control/output_v2/RESULTS.json',
    'lineage_code': PR19 / 'code/lineage_reduction.py',
}
MODES = ('OFF', 'KF', 'GM')
SPECIAL = {0, 700, 1620, 2344}
MOMENTS = ('Z_eV', 'QN', 'QE_eV') + tuple(p + '_' + s + ('' if p == 'A' else '_eV') for s in ('HI', 'HeI', 'HeII') for p in ('A', 'B', 'H'))
EPS = F.from_float(1.602176634e-12)
COUNTS = Counter()
FAILURES = []

def check(kind, good, detail=None):
    COUNTS[kind] += 1
    if not good:
        FAILURES.append({'category': kind, 'detail': detail})

def interval(x):
    a, b = F(x['lo']), F(x['hi'])
    check('ordered_interval', a <= b)
    return a, b

def plus(a, b):
    return a[0] + b[0], a[1] + b[1]

def times(a, w):
    assert w > 0
    return a[0] * w, a[1] * w

def isum(xs):
    ans = F(0), F(0)
    for x in xs:
        ans = plus(ans, x)
    return ans

def width(x):
    return x[1] - x[0]

def overlap(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])

def contains(a, b):
    return a[0] <= b[0] and b[1] <= a[1]

def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, tuple) and len(x) == 2 and all(isinstance(v, F) for v in x):
        return {'lo': str(x[0]), 'hi': str(x[1])}
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x

def dump(name, obj):
    with (OUT / name).open('x') as f:
        json.dump(encode(obj), f, indent=2, sort_keys=True)
        f.write('\n')

def raw_sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def add_totals(values):
    for family in ('absolute', 'correction'):
        for p in ('A', 'B', 'H'):
            suffix = '' if p == 'A' else '_eV'
            values[family + '/' + p + '_total' + suffix] = isum(values[family + '/' + p + '_' + s + suffix] for s in ('HI', 'HeI', 'HeII'))
    return values

def old_values(path, w):
    v = {'absolute/' + k: interval(path['weighted_reduction'][k]) for k in (*MOMENTS, 'P_final', 'anchor')}
    v.update({'correction/' + k: times(interval(path['cumulative_correction'][k]), w) for k in MOMENTS})
    v['correction/P_final'] = times(interval(path['segments'][-1]['DP']), w)
    v['correction/energy_eV'] = times(interval(path['segments'][-1]['energy_endpoint_minus_captured_erg']), w / EPS)
    return add_totals(v)

def new_values(track, w):
    v = {'absolute/' + k: times(interval(track['true_moment_enclosures'][k]), w) for k in MOMENTS}
    v['absolute/P_final'] = times(interval(track['final_photon']['true_absolute_interval']), w)
    v['absolute/anchor'] = times(interval(track['summed_true_anchor_eV']), w)
    v.update({'correction/' + k: times(interval(track['cumulative_moment_corrections'][k]['interval']), w) for k in MOMENTS})
    v['correction/P_final'] = times(interval(track['final_photon']['true_minus_captured_interval']), w)
    v['correction/energy_eV'] = times(interval(track['final_energy_stock_eV']['true_minus_captured_interval']), w)
    return add_totals(v)

def same_except_origin(full, prior):
    def clean(p):
        return {**p, 'segments': [{k: v for k, v in s.items() if k != 'origin'} for s in p['segments']]}
    return clean(full) == clean(prior)

def classify(x):
    if x[0] > 0:
        return 'STRICTLY_POSITIVE'
    if x[1] < 0:
        return 'STRICTLY_NEGATIVE'
    if x == (0, 0):
        return 'EXACT_ZERO'
    return 'UNRESOLVED'

def main():
    resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024**2, 1024 * 1024**2))
    began = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    contract = json.loads((PKG / 'SCIENTIFIC_CONTRACT.json').read_text())
    before = {}
    for name, p in INPUTS.items():
        ident = {'bytes': p.stat().st_size}
        if name != 'paths':
            ident['sha256'] = raw_sha(p)
            check('input_pin', ident == contract['pinned_inputs'][name], name)
        before[name] = ident
    prior_obj = json.loads(INPUTS['prior'].read_text())
    prior = {(p['mode'], p['node']): p for p in prior_obj['paths']}
    current_obj = json.loads(INPUTS['current'].read_text())
    current = {(t['track']['mode'], t['track']['node']): t for t in current_obj['tracks']}
    lineage = json.loads(INPUTS['lineage_result'].read_text())
    lineage_terms = {(t['mode'], t['node']): t for t in lineage['hybrid']['path_terms']}
    check('current_keys', set(current) == {('OFF', 0), ('OFF', 700)})
    check('current_resolution', current_obj['identity']['subdivisions'] == 512 and current_obj['identity']['precision_digits'] == 60)
    sums = {m: {v: {p: {} for p in ('full', 'selected4', 'complement2436', 'K2', 'retained')} for v in ('original', 'hybrid')} for m in MODES}
    ranking_inputs = {m: {} for m in MODES}
    count = Counter()
    segments = Counter()
    saved_selected = []
    replacements = []
    raw_stat_before = INPUTS['paths'].stat()
    h = hashlib.sha256()
    with INPUTS['paths'].open('rb') as raw:
        for idx, line in enumerate(raw):
            h.update(line)
            path = json.loads(line)
            key = path['mode'], path['node']
            expected = MODES[idx // 2440], idx % 2440
            check('ordered_complete_coverage', key == expected, {'expected': expected, 'actual': key})
            m, n = key
            count[m] += 1
            segments[m] += len(path['segments'])
            expected_keys = [[m, 1, n, 0], [m, 2, n, 0]] + ([[m, 2, n, 1]] if n in SPECIAL else [])
            check('segment_identity', [s['key'] for s in path['segments']] == expected_keys, key)
            wlo, whi = interval(path['weight'])
            check('positive_point_weight', wlo == whi and wlo > 0, key)
            w = wlo
            old = old_values(path, w)
            new = old
            if n in SPECIAL:
                check('inherited_path_exact_except_origin', same_except_origin(path, prior[key]), key)
                saved_selected.append({'mode': m, 'node': n, 'weight': w, 'values': old})
            if key in current:
                track = current[key]
                check('replacement_segment_identity', [s['key'] for s in track['segments']] == expected_keys, key)
                for si, (s, t) in enumerate(zip(path['segments'], track['segments'])):
                    for label in MOMENTS:
                        check('captured_baseline_overlap', overlap(interval(s['captured'][label]), interval(t['captured'][label])), [*key, si, label])
                new = new_values(track, w)
                for label in (*MOMENTS, 'P_final', 'anchor'):
                    check('exact_previous_lineage_replacement', new['absolute/' + label] == interval(lineage_terms[key]['weighted_reduction'][label]), [*key, label])
                comps = {}
                for label in old:
                    comps[label] = {'overlap': overlap(old[label], new[label]), 'old_contains_new': contains(old[label], new[label]), 'old': old[label], 'new': new[label]}
                    check('replacement_compatible', comps[label]['overlap'], [*key, label])
                    check('replacement_nested', comps[label]['old_contains_new'], [*key, label])
                replacements.append({'mode': m, 'node': n, 'metrics': comps})
            parts = ['full', 'selected4' if n in SPECIAL else 'complement2436', 'K2' if key in current else 'retained']
            for variant, values in (('original', old), ('hybrid', new)):
                for part in parts:
                    dest = sums[m][variant][part]
                    for label, value in values.items():
                        dest[label] = plus(dest.get(label, (F(0), F(0))), value)
            for label, value in old.items():
                ranking_inputs[m].setdefault(label, []).append((n, width(value), width(new[label])))
    before['paths']['sha256'] = h.hexdigest()
    check('input_pin', before['paths'] == contract['pinned_inputs']['paths'], 'paths')
    check('raw_source_unchanged', (raw_stat_before.st_ino, raw_stat_before.st_size, raw_stat_before.st_mtime_ns) == (INPUTS['paths'].stat().st_ino, INPUTS['paths'].stat().st_size, INPUTS['paths'].stat().st_mtime_ns))
    check('total_paths', sum(count.values()) == 7320)
    check('total_segments', sum(segments.values()) == 14652)
    rankings = {}
    diagnostics = {}
    for m in MODES:
        check('mode_path_count', count[m] == 2440, m)
        check('mode_segment_count', segments[m] == 4884, m)
        rankings[m] = {}
        diagnostics[m] = {}
        for label in sums[m]['original']['full']:
            for variant in ('original', 'hybrid'):
                d = sums[m][variant]
                k2 = d['K2'].get(label, (F(0), F(0)))
                check('exact_partition_selected_complement', plus(d['selected4'][label], d['complement2436'][label]) == d['full'][label], [m, variant, label])
                check('exact_partition_K2_retained', plus(k2, d['retained'][label]) == d['full'][label], [m, variant, label])
                check('unchanged_complement', d['complement2436'][label] == sums[m]['original']['complement2436'][label], [m, variant, label])
                if m != 'OFF':
                    check('unchanged_alternative_mode', d['full'][label] == sums[m]['original']['full'][label], [m, variant, label])
            orig = sums[m]['original']
            hyb = sums[m]['hybrid']
            ow = width(orig['full'][label])
            nw = width(hyb['full'][label])
            remain = width(hyb['retained'][label])
            selected_w = width(orig['selected4'][label])
            comp_w = width(orig['complement2436'][label])
            k2_w = width(hyb['K2'].get(label, (F(0), F(0))))
            check('fixed_retained_floor', remain <= nw and nw - remain == k2_w, [m, label])
            check('gain_exact_identity', ow - nw == width(orig['K2'].get(label, (F(0), F(0)))) - k2_w, [m, label])
            diagnostics[m][label] = {'original_width': ow, 'hybrid_width': nw, 'selected4_original_width': selected_w, 'complement2436_width': comp_w, 'selected4_share_original': selected_w / ow if ow else None, 'complement_share_original': comp_w / ow if ow else None, 'removed_fraction_original': (ow - nw) / ow if ow else None, 'retained_width_floor': remain, 'max_further_gain_only_K2': k2_w, 'max_further_fraction_hybrid': k2_w / nw if nw else None, 'original_sign': classify(orig['full'][label]), 'hybrid_sign': classify(hyb['full'][label])}
            rankings[m][label] = {}
            for variant, column, fw in (('original', 1, ow), ('hybrid', 2, nw)):
                ranked = sorted(ranking_inputs[m][label], key=lambda r: (-r[column], r[0]))
                check('ranking_width_sum', sum((r[column] for r in ranked), F(0)) == fw, [m, label, variant])
                rankings[m][label][variant] = {'top_nodes': [r[0] for r in ranked[:100]], 'top_widths': [r[column] for r in ranked[:100]], 'topk_fraction': {str(k): sum((r[column] for r in ranked[:k]), F(0)) / fw if fw else None for k in (1, 2, 4, 10, 100)}, 'zero_width': fw == 0}
    full = json.loads(INPUTS['full_results'].read_text())
    for m in MODES:
        oldP = sums[m]['original']['full']['absolute/P_final']
        check('full_P_saved_aggregate_encloses_exact_terms', contains(interval(full['all_node_per_step'][m]['2']['P_endpoint']), oldP), m)
    for name, p in INPUTS.items():
        if name != 'paths':
            check('small_source_unchanged', raw_sha(p) == before[name]['sha256'], name)
    # Independent route discrimination: ordinary interval subtraction is wider.
    oldtotal = (F(6), F(10))
    oldpart = (F(1), F(3))
    newpart = (F(2), F(5, 2))
    retained = (F(5), F(7))
    direct = plus(retained, newpart)
    naive = plus((oldtotal[0] - oldpart[1], oldtotal[1] - oldpart[0]), newpart)
    check('toy_interval_subtraction_rejected', width(naive) > width(direct) and direct == (F(7), F(19, 2)))
    check('toy_baseline_mapping', F(10) + F(3) == F(12) + (F(3) + F(10) - F(12)))
    check('toy_energy_unit_conversion_once', F(7) * EPS / EPS == F(7) and F(7) * EPS / EPS / EPS != F(7))
    check('toy_signed_rules', [classify(x) for x in [(F(1), F(2)), (F(-2), F(-1)), (F(0), F(0)), (F(0), F(1)), (F(-1), F(0))]] == ['STRICTLY_POSITIVE', 'STRICTLY_NEGATIVE', 'EXACT_ZERO', 'UNRESOLVED', 'UNRESOLVED'])
    result = {'schema': 'independent-exact-saved-reduction-v1', 'execution_kind': 'SAVED_INTERVAL_ARITHMETIC_ONLY', 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - began, 'max_rss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'stream_passes': 1, 'source_sha256': raw_sha(Path(__file__)), 'input_identities': before, 'paths_by_mode': dict(count), 'segments_by_mode': dict(segments), 'check_counts': dict(COUNTS), 'check_count': sum(COUNTS.values()), 'failed_count': len(FAILURES), 'failures': FAILURES, 'sums': sums, 'diagnostics': diagnostics, 'rankings': rankings, 'replacements': replacements, 'new_coefficient_evaluations': 0, 'new_physical_executions': 0, 'claim': 'Independent exact reduction only; inherited per-path enclosure validity remains conditional; no continuum or physical admission.'}
    dump('INDEPENDENT_ARITHMETIC.json', result)
    print(json.dumps({k: result[k] for k in ('elapsed_seconds', 'max_rss_KiB', 'check_count', 'failed_count', 'failures')}))

if __name__ == '__main__':
    main()
