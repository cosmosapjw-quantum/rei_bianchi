#!/usr/bin/env python3
"""Bounded same-target refinement of four captured OFF paths.

Only the selection/validation/execution harness is new. The three inherited
interval/coefficient/path kernels are byte-pinned and unmodified. No ODE,
native, gas, full-first2, or previous full-budget job is invoked.
"""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
NODES = (101, 102, 410, 413)
SPECIES = ('HI', 'HeI', 'HeII')
UNITS = {(32, 60), (128, 60), (512, 60), (32, 80)}
VENDOR = {
    'directed_interval.py': 'ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5',
    'local_enclosure.py': 'fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370',
    'path_enclosure.py': 'c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def save(path, obj):
    path = Path(path)
    raw = (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('xb') as stream:
        if stream.write(raw) != len(raw):
            raise OSError('short write')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def read(path):
    return json.loads(Path(path).read_text())


def captured(value):
    # The physical capture is binary64. Decimal strings are transport text.
    v = float(value)
    if not __import__('math').isfinite(v):
        raise ValueError('nonfinite captured input')
    return F.from_float(v)


def bounds(obj):
    lo, hi = F(obj['lo']), F(obj['hi'])
    if lo > hi:
        raise ValueError('inverted interval')
    return lo, hi


def inside(obj, value):
    lo, hi = bounds(obj)
    return lo <= value <= hi


def check(condition, name, record):
    record[name] = bool(condition)
    if not condition:
        raise ValueError('input gate failed: ' + name)


def validate_inputs():
    data = read(ROOT / 'inputs/PATH_CONTROLS.json')
    controls = data['controls']
    keys = [('OFF', step, node, 0) for node in NODES for step in (1, 2)]
    audit = {}
    check([tuple(c['key']) for c in controls] == keys, 'eight_ordered_keys', audit)
    rows = list(csv.DictReader((ROOT / 'inputs/source/OFF_SEGMENTS.csv').open()))
    selected = [r for r in rows if int(r['step']) in (1, 2) and int(r['node']) in NODES]
    selected_keys = [(r['mode'], int(r['step']), int(r['node']), int(r['segment'])) for r in selected]
    check(len(selected_keys) == len(set(selected_keys)) == 8 and set(selected_keys) == set(keys), 'raw_row_uniqueness_and_selection', audit)
    row_map = dict(zip(selected_keys, selected))
    stages_list = list(csv.DictReader((ROOT / 'inputs/source/OFF_STAGES.csv').open()))
    stages = {int(r['step']): r for r in stages_list}
    check(len(stages) == len(stages_list), 'stage_unique', audit)
    node_list = list(csv.DictReader((ROOT / 'inputs/source/OFF_NODES.csv').open()))
    node_map = {(int(r['step']), int(r['node'])): r for r in node_list}
    check(len(node_map) == len(node_list), 'node_row_unique', audit)
    old_lines = (ROOT / 'inputs/OLD_PATHS_OFF4.jsonl').read_bytes().splitlines(keepends=True)
    old_paths = [json.loads(x) for x in old_lines]
    check([(p['mode'], p['node']) for p in old_paths] == [('OFF', n) for n in NODES], 'old_path_keys', audit)
    old = {p['node']: p for p in old_paths}
    prov = read(ROOT / 'INPUT_PROVENANCE.json')
    path_record = next(x for x in prov['source_records'] if x['member'].endswith('/PATHS.jsonl'))
    check([hashlib.sha256(x).hexdigest() for x in old_lines] == path_record['selected_line_sha256'], 'original_selected_line_bytes', audit)
    for rec in prov['source_records']:
        if 'local_file' in rec:
            p = ROOT / rec['local_file']
            check(p.stat().st_size == rec['bytes'] and sha(p) == rec['sha256'], 'source_member_' + p.name, audit)
    source_pins = read(ROOT / 'inputs/source/PR20_START.json')['hashes']
    for name, tail in [('OFF_SEGMENTS.csv', '/evidence/capture/OFF/SEGMENTS.csv'), ('OFF_NODES.csv', '/evidence/capture/OFF/NODES.csv'), ('OFF_STAGES.csv', '/inputs/OFF_STAGES.csv')]:
        check([v for k, v in source_pins.items() if k.endswith(tail)] == [sha(ROOT / 'inputs/source' / name)], 'pr20_pin_' + name, audit)
    row_checks = []
    eps = captured(1.602176634e-12)
    chi = [captured(x) for x in (13.598434599702, 24.587389011, 54.41776)]
    for control in controls:
        key = tuple(control['key'])
        r, s = control['row'], control['stage']
        a = {}
        check(r == row_map[key], 'exact_raw_row', a)
        check(s == stages[key[1]] and s['mode'] == 'OFF', 'exact_stage', a)
        check(control['node_row'] == node_map[key[1], key[2]], 'exact_node_row', a)
        check(control['source_on'] is True and captured(r['source_on']) == 1, 'source_on', a)
        check(control['mask'] == {'HI': True, 'HeI': False, 'HeII': False}, 'HI_only', a)
        check(tuple(captured(r['e_mid']) >= captured(x) for x in (13.6, 24.59, 54.42)) == (True, False, False), 'captured_mask_rule', a)
        check(captured(r['lambda_HeI']) == captured(r['lambda_HeII']) == 0, 'inactive_exact_zero', a)
        check(captured(r['lambda_HI']) >= 0 and captured(r['q']) >= 0, 'captured_nonnegative_rates', a)
        check(captured(r['a']) + captured(r['h']) == captured(r['b']) and captured(r['h']) > 0, 'exact_width', a)
        check(captured(s['s0']) <= captured(r['a']) < captured(r['b']) <= captured(s['s1']), 'stage_domain', a)
        check(captured(r['outn']) == captured(r['oute']) == 0, 'no_outflow', a)
        check(captured(r['anchored']) == 0, 'ordinary_captured_segment', a)
        check(captured(r['weight']) > 0, 'positive_weight', a)
        old_path = old[key[2]]
        check(len(old_path['segments']) == 2, 'same_two_segment_path', a)
        oldseg = old_path['segments'][key[1] - 1]
        check(oldseg['key'] == control['key'] and oldseg['mask'] == control['mask'] and oldseg['source_on'] == control['source_on'], 'old_branch_identity', a)
        check(bounds(old_path['weight']) == (captured(r['weight']),) * 2, 'old_weight_identity', a)
        exact_moments = {'QN': captured(r['qn']), 'QE_eV': captured(r['qe']) / eps, 'Z_eV': captured(r['red']) / eps}
        for species, threshold in zip(SPECIES, chi):
            exact_moments['A_' + species] = captured(r['A_' + species])
            exact_moments['B_' + species + '_eV'] = captured(r['B_' + species]) / eps
            exact_moments['H_' + species + '_eV'] = captured(r['B_' + species]) / eps - threshold * captured(r['A_' + species])
        check(all(inside(oldseg['captured'][k], v) for k, v in exact_moments.items()), 'old_captured_moment_reference', a)
        check(all(r[x] == control['node_row'][x] for x in ('eta', 'weight', 'n', 'u', 'qn', 'qe', 'outn', 'oute')), 'ordinary_node_capture_bridge', a)
        row_checks.append({'key': list(key), 'checks': a})
    seams = []
    for start in range(0, 8, 2):
        left, right = controls[start:start + 2]
        r, s = left['row'], right['row']
        a = {}
        check(captured(r['f0']) == 0, 'initial_photon_and_incoming_zero', a)
        for name, x, y in [('time', 'b', 'a'), ('photon', 'n', 'f0'), ('eta', 'eta', 'eta'), ('weight', 'weight', 'weight')]:
            check(captured(r[x]) == captured(s[y]), name + '_stitch', a)
        seams.append({'node': left['key'][2], 'checks': a})
    budget = read(ROOT / 'inputs/PREDECESSOR_BUDGET.json')
    bridges = 0
    for kind, values in budget['budgets'].items():
        for k, v in values.items():
            x, y, z = [bounds(v[t]) for t in ('predecessor_full', 'retained_outside_K4', 'old_selected_K4')]
            check(x == (y[0] + z[0], y[1] + z[1]), 'bridge_' + kind + '_' + k, audit)
            bridges += 1
    check(bridges == 34, 'exact_34_budget_bridges', audit)
    return controls, {'general': audit, 'rows': row_checks, 'seams': seams}


def verify_lock():
    lock = read(ROOT / 'SOURCE_LOCK.json')
    for name, rec in lock['files'].items():
        path = ROOT / name
        if path.stat().st_size != rec['bytes'] or sha(path) != rec['sha256']:
            raise ValueError('source lock mismatch: ' + name)
    return {name: rec['sha256'] for name, rec in lock['files'].items()}


def projection(result):
    # Versioned explicit numerical projection; only host, timing, paths and
    # start/finish receipts are excluded. Track scientific fields stay intact.
    keys = ('schema', 'work_unit', 'input_checks', 'new_coefficient_evaluations',
            'new_local_enclosures', 'reused_local_enclosures', 'rounding_operation_counts',
            'source_unchanged_during_run', 'source_lock_sha256', 'forbidden_invocations')
    p = {k: result[k] for k in keys}
    p['tracks'] = [{k: v for k, v in t.items() if k != 'elapsed_seconds'} for t in result['tracks']]
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--subdivisions', type=int, required=True)
    ap.add_argument('--precision', type=int, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    if (args.subdivisions, args.precision) not in UNITS:
        raise ValueError('undeclared N/P work unit')
    for name, expected in VENDOR.items():
        if sha(ROOT / 'code/vendor' / name) != expected:
            raise ValueError('immutable kernel mismatch: ' + name)
    # Never import an unverified replacement scientific module.
    sys.path.insert(0, str(ROOT / 'code/vendor'))
    import directed_interval as di
    import path_enclosure as pe
    from local_enclosure import Coefficients
    di.configure(args.precision)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    tracks = []
    completed_segments = 0
    solver_entered = False
    forbidden = dict(ODE_solves=0, native_runs=0, gas_advances=0, full_first2_reruns=0, old_budget_reruns=0)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
        before = verify_lock()
        controls, checks = validate_inputs()
        # Coefficient construction performs no integrand evaluation. This binds
        # the *entire* energy trajectory to the same ordinary source/mask branch.
        domain = []
        for control in controls:
            c = Coefficients(control)
            if not (c.endpoint_E.lo > Decimal.from_float(13.7) and c.e0.hi < Decimal.from_float(24.59)):
                raise ValueError('source/mask threshold crossed by actual segment')
            domain.append({'key': control['key'], 'minimum_endpoint_energy_eV': str(c.endpoint_E.lo), 'maximum_initial_energy_eV': str(c.e0.hi), 'same_source_and_mask_on_entire_segment': True})
        checks['whole_segment_branch'] = domain
        identity = {
            'started_utc': datetime.now(timezone.utc).isoformat(), 'argv': sys.argv,
            'hostname': platform.node(), 'platform': platform.platform(), 'python': sys.version,
            'decimal_libmpdec_version': __import__('decimal').__libmpdec_version__,
            'cpu_affinity': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
            'provider_attestation': 'NOT_ASSERTED',
            'source_sha256_before_run': before, 'source_lock_sha256': sha(ROOT / 'SOURCE_LOCK.json'),
            'limits': {'processes': 1, 'threads': 1, 'memory_bytes': 1024 ** 3, 'seconds': 300, 'automatic_retries': 0},
            'work_unit': {'N': args.subdivisions, 'precision': args.precision, 'nodes': list(NODES), 'mode': 'OFF'},
        }
        save(out / 'START.json', identity)
        def checkpoint(rows, seams):
            nonlocal completed_segments
            completed_segments = 2 * len(tracks) + len(rows)
            save(out / 'CHECKPOINT.json', pe.pack({'status': 'RUNNING', 'completed_tracks': len(tracks), 'completed_segments': completed_segments, 'active_rows': rows, 'active_seams': seams, 'elapsed_seconds': time.perf_counter() - started}))
            if time.perf_counter() - started > 300:
                raise TimeoutError('declared 300-second work-unit budget exceeded')
        solver_entered = True
        for start in range(0, 8, 2):
            t = pe.run_track(controls[start:start + 2], args.subdivisions, {'controls': []}, checkpoint)
            tracks.append(t)
            print(json.dumps(pe.pack({'node': t['track']['node'], 'seconds': t['elapsed_seconds'], 'photon_radius': t['final_photon']['radius'], 'heat_species_sum_radius_eV': sum((t['cumulative_moment_corrections']['H_' + s + '_eV']['radius'] for s in SPECIES), Decimal(0))})), flush=True)
        after = verify_lock()
        if before != after:
            raise RuntimeError('source changed during work unit')
        packed_tracks = pe.pack(tracks)
        def finite_boxes(v):
            if isinstance(v, dict):
                if set(v) == {'lo', 'hi'}:
                    a, b = Decimal(v['lo']), Decimal(v['hi'])
                    if not a.is_finite() or not b.is_finite() or a > b:
                        raise ArithmeticError('invalid scientific interval')
                else:
                    for x in v.values(): finite_boxes(x)
            elif isinstance(v, list):
                for x in v: finite_boxes(x)
        finite_boxes(packed_tracks)
        evaluations = sum(r['local']['new_coefficient_evaluations'] for t in tracks for r in t['segments'])
        if evaluations != 16 * args.subdivisions:
            raise RuntimeError('coefficient evaluation budget mismatch')
        result = {
            'schema': 'bass-he-e13c6-off4-enclosure-v1', 'status': 'PASS_MECHANICAL_PENDING_INDEPENDENT_ADMISSION',
            'work_unit': identity['work_unit'], 'identity': identity, 'input_checks': checks,
            'tracks': packed_tracks, 'new_coefficient_evaluations': evaluations,
            'new_local_enclosures': 8, 'reused_local_enclosures': 0,
            'rounding_operation_counts': di.COUNTS, 'source_unchanged_during_run': True,
            'source_lock_sha256': identity['source_lock_sha256'], 'source_sha256_after_run': after,
            'forbidden_invocations': forbidden,
            'elapsed_seconds': time.perf_counter() - started,
            'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'finished_utc': datetime.now(timezone.utc).isoformat(),
            'claim_ceiling': 'four fixed captured two-step OFF targets; inherited conditional arithmetic and analytic enclosures; finite species-sum reduction only',
            'physical': 'HOLD', 'continuum': 'HOLD', 'production': 'HOLD', 'receiver': 'HOLD',
        }
        save(out / 'RESULTS.json', result)
        proj = projection(result)
        save(out / 'NUMERICAL_PROJECTION.json', proj)
        semantic = hashlib.sha256(b'bass-he-e13c6-off4-semantic-v1\n' + canonical(proj)).hexdigest()
        save(out / 'NUMERICAL_IDENTITY.json', {'projection_version': 1, 'semantic_sha256': semantic, 'canonical_object_sha256': hashlib.sha256(canonical(proj)).hexdigest(), 'projection_file_sha256': sha(out / 'NUMERICAL_PROJECTION.json'), 'result_file_sha256': sha(out / 'RESULTS.json'), 'exclusions': ['host/start/finish/argv/paths/resource receipts', 'each track elapsed_seconds'], 'includes': 'all scientific track fields, input checks, fixed source-lock identity, resolution, precision and arithmetic counters'})
        save(out / 'RESOURCE_RECEIPT.json', {'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'], 'peak_RSS_KiB': result['peak_RSS_KiB'], 'scientific_work_unit_invocations': 1, 'new_local_enclosures': 8, 'new_coefficient_evaluations': evaluations, **forbidden, 'automatic_retries': 0})
        save(out / 'CHECKPOINT.json', {'status': 'COMPLETE', 'completed_tracks': 4, 'completed_segments': 8, 'source_unchanged': True})
        print(json.dumps({'status': result['status'], 'semantic_sha256': semantic, 'seconds': result['elapsed_seconds']}), flush=True)
        return 0
    except BaseException as exc:
        save(out / 'FAILURE.json', {'status': 'FAIL_PRESERVED_NO_RETRY', 'error_type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc(), 'scientific_work_unit_entered': solver_entered, 'completed_tracks': len(tracks), 'completed_segments': completed_segments, 'forbidden_invocations': forbidden, 'elapsed_seconds': time.perf_counter() - started, 'automatic_retries': 0})
        raise


if __name__ == '__main__':
    raise SystemExit(main())
