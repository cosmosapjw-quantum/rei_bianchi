#!/usr/bin/env python3
"""A source-bound, independently schedulable OFF path; inherited kernels unchanged."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback

from common import (F, SP, EPS, add, box, canonical, capture, compare_metrics, enc,
                    encode_metrics, new_metrics, old_metrics, read, save, sha)

KERNEL_PINS = {
    'directed_interval.py': 'ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5',
    'local_enclosure.py': 'fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370',
    'path_enclosure.py': 'c424c8b980ece05618e427e4373f13a41fe7b4d02a8ddd4a0b3fa7da30109d73',
}

def numerical_projection(result):
    p = {k: result[k] for k in ('schema', 'work', 'path_input_sha256', 'source_lock_sha256',
        'input_checks', 'new_local_enclosures', 'new_coefficient_evaluations',
        'rounding_operation_counts', 'forbidden_invocations')}
    p['track'] = {k: v for k, v in result['track'].items() if k != 'elapsed_seconds'}
    return p

def semantic_sha(result):
    return hashlib.sha256(b'bass-he-e13c7-path-numerical-v1\n' + canonical(numerical_projection(result))).hexdigest()

def assert_finite_boxes(x):
    if isinstance(x, dict):
        if set(x) == {'lo', 'hi'}:
            box(x)
        else:
            for v in x.values():
                assert_finite_boxes(v)
    elif isinstance(x, list):
        for v in x:
            assert_finite_boxes(v)

class Context:
    """One immutable input view per worker process; no mutable cross-path state."""
    def __init__(self, package):
        self.root = Path(package).resolve()
        self.lock = read(self.root / 'SOURCE_LOCK.json')
        self.source_lock_sha256 = sha(self.root / 'SOURCE_LOCK.json')
        required = {'code/common.py', 'code/off_path_worker.py', 'RESEARCH_CONTRACT.json',
                    'inputs/INPUT_INDEX.json', 'inputs/OFF_OLD_PATHS.jsonl'}
        required.update('code/vendor/' + n for n in KERNEL_PINS)
        if not required <= set(self.lock['files']):
            raise ValueError('source lock omits required scientific/input files')
        for name, rec in self.lock['files'].items():
            p = (self.root / name).resolve()
            if not p.is_relative_to(self.root) or not p.is_file() or p.stat().st_size != rec['bytes'] or sha(p) != rec['sha256']:
                raise ValueError('source lock mismatch: ' + name)
        for n, pin in KERNEL_PINS.items():
            if sha(self.root / 'code/vendor' / n) != pin:
                raise ValueError('inherited scientific kernel changed: ' + n)
        self.contract = read(self.root / 'RESEARCH_CONTRACT.json')
        self.plan = read(self.root / 'inputs/WORK_PLAN.json')
        self.index = read(self.root / 'inputs/INPUT_INDEX.json')['records']
        self.stages = {int(r['step']): r for r in csv.DictReader((self.root / 'inputs/source/OFF_STAGES.csv').open())}
        node_rows = list(csv.DictReader((self.root / 'inputs/source/OFF_NODES.csv').open()))
        self.node_rows = {(int(r['step']), int(r['node'])): r for r in node_rows}
        if len(self.node_rows) != len(node_rows):
            raise ValueError('duplicate captured node row')
        self.controls = {}
        seen = set()
        for r in csv.DictReader((self.root / 'inputs/source/OFF_SEGMENTS.csv').open()):
            if int(r['step']) not in (1, 2):
                continue
            k = ('OFF', int(r['step']), int(r['node']), int(r['segment']))
            if r['mode'] != 'OFF' or k in seen:
                raise ValueError('duplicate/wrong mode captured segment')
            seen.add(k)
            self.controls.setdefault(k[2], []).append({'key': list(k), 'row': r, 'stage': self.stages[k[1]],
                'node_row': self.node_rows[k[1], k[2]],
                'mask': {s: float(r['e_mid']) >= cut for s, cut in zip(SP, (13.6, 24.59, 54.42))},
                'source_on': float(r['source_on']) == 1.0})
        if set(self.controls) != set(range(2440)) or len(seen) != 4884:
            raise ValueError('captured full OFF coverage mismatch')
        for controls in self.controls.values():
            controls.sort(key=lambda c: tuple(c['key']))
        # Defer scientific imports until all corresponding byte identities pass.
        sys.path.insert(0, str(self.root / 'code/vendor'))
        import directed_interval as di
        import path_enclosure as pe
        import local_enclosure as le
        for module, name in [(di, 'directed_interval.py'), (pe, 'path_enclosure.py'), (le, 'local_enclosure.py')]:
            if Path(module.__file__).resolve() != self.root / 'code/vendor' / name:
                raise ValueError('foreign scientific module already imported')
        self.di, self.pe, self.le = di, pe, le

    def inputs(self, node):
        rec = self.index[str(node)]
        with (self.root / 'inputs/OFF_OLD_PATHS.jsonl').open('rb') as f:
            f.seek(rec['offset'])
            raw = f.read(rec['bytes'])
        if len(raw) != rec['bytes'] or hashlib.sha256(raw).hexdigest() != rec['old_line_sha256']:
            raise ValueError('original path line bytes changed')
        old = json.loads(raw)
        controls = self.controls[node]
        digest = hashlib.sha256(b'bass-he-e13c7-path-input-v1\n' + canonical({'controls': controls, 'old_path': old})).hexdigest()
        if digest != rec['path_input_sha256']:
            raise ValueError('original source/path semantic identity mismatch')
        return controls, old, rec

    def allowed(self, node, n, precision, purpose):
        if node in self.plan['prior_admitted_nodes'] or node in self.plan['zero_nodes']:
            raise ValueError('consumed or exact-zero path must not enter a new kernel')
        if purpose in ('ncp', 'ncp_batch'):
            ok = (self.plan['status'] == 'SEALED_FOR_HEAVY_NCP' and node in self.plan['ncp_nodes']
                  and n == self.plan['primary_N'] and precision == self.plan['precision'])
        else:
            if purpose not in ('local', 'local_primary', 'resolution_diagnostic', 'branch_control', 'precision_control'):
                raise ValueError('undeclared purpose')
            ok = ((node in self.contract['local_primary_nodes'] and (n, precision) == (512, 60))
                  or (node in self.contract['local_resolution_diagnostic_nodes'] and (n, precision) == (1024, 60))
                  or (node in self.contract['local_branch_control_nodes'] and (n, precision) in ((32, 60), (32, 80), (128, 60))))
        if not ok:
            raise ValueError('work item is outside the declared local or sealed heavy plan')

    def validate_inputs(self, node, controls, old):
        checks = []
        def check(name, value, key=None):
            checks.append({'check': name, 'key': key, 'pass': bool(value)})
            if not value:
                raise ValueError('same-target input gate failed: ' + name)
        check('mode_and_node', old['mode'] == 'OFF' and old['node'] == node)
        check('same_ordered_path', [c['key'] for c in controls] == [s['key'] for s in old['segments']])
        check('same_index_keys', [c['key'] for c in controls] == self.index[str(node)]['keys'])
        check('initial_photon_zero', capture(controls[0]['row']['f0']) == 0)
        w = capture(controls[0]['row']['weight'])
        check('original_positive_point_weight', w > 0 and box(old['weight']) == (w, w))
        for c, prior in zip(controls, old['segments']):
            r, s, key = c['row'], c['stage'], c['key']
            check('mask_and_source_frozen_identity', prior['mask'] == c['mask'] and prior['source_on'] == c['source_on'], key)
            check('anchored_flag_identity', prior['anchored'] == bool(capture(r['anchored'])), key)
            check('positive_exact_time_width', capture(r['a']) + capture(r['h']) == capture(r['b']) and capture(r['h']) > 0, key)
            check('same_gas_stage_domain', s['mode'] == 'OFF' and capture(s['s0']) <= capture(r['a']) < capture(r['b']) <= capture(s['s1']), key)
            check('no_outflow', capture(r['outn']) == capture(r['oute']) == 0, key)
            check('same_weight', capture(r['weight']) == w, key)
            check('nonnegative_frozen_data', all(capture(r[k]) >= 0 for k in ['f0', 'q'] + ['lambda_' + sp for sp in SP]), key)
            check('inactive_rates_exact_zero', all(c['mask'][sp] or capture(r['lambda_' + sp]) == 0 for sp in SP), key)
            exact = {'QN': capture(r['qn']), 'QE_eV': capture(r['qe']) / EPS, 'Z_eV': capture(r['red']) / EPS}
            for sp, chi in zip(SP, (13.598434599702, 24.587389011, 54.41776)):
                exact['A_' + sp] = capture(r['A_' + sp])
                exact['B_' + sp + '_eV'] = capture(r['B_' + sp]) / EPS
                exact['H_' + sp + '_eV'] = exact['B_' + sp + '_eV'] - capture(chi) * exact['A_' + sp]
            check('old_captured_reference_contains_exact_binary64_lifts', all(box(prior['captured'][k])[0] <= v <= box(prior['captured'][k])[1] for k, v in exact.items()), key)
            # Event rows are the captured branch definition; do not silently
            # reevaluate source/mask at a realified threshold endpoint.
        for left, right in zip(controls, controls[1:]):
            a, b = left['row'], right['row']
            check('exact_time_photon_eta_weight_stitch', all(capture(a[k]) == capture(b[l]) for k, l in
                  [('b', 'a'), ('n', 'f0'), ('eta', 'eta'), ('weight', 'weight')]), [left['key'], right['key']])
        if node in self.plan['ncp_nodes']:
            check('bulk_ordinary_two_source_on_segments', len(controls) == 2 and all(c['source_on'] and capture(c['row']['anchored']) == 0 for c in controls))
            check('bulk_mask_constant', controls[0]['mask'] == controls[1]['mask'])
        return checks

    def run(self, node, subdivisions, precision, output_dir, purpose):
        node, n, precision = int(node), int(subdivisions), int(precision)
        self.allowed(node, n, precision, purpose)
        out = Path(output_dir).resolve()
        out.mkdir(parents=True, exist_ok=False)
        started = time.perf_counter()
        entered = False
        complete_segments = 0
        forbidden = {'ODE_solves': 0, 'native_runs': 0, 'gas_advances': 0, 'full_first2_reruns': 0, 'old_budget_reruns': 0, 'reused_local_enclosures': 0}
        def timeout_handler(signum, frame):
            raise TimeoutError('declared per-path wall budget exceeded')
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, self.plan['limits']['seconds_per_path'])
        try:
            memory = self.plan['limits']['memory_bytes_per_process']
            current = resource.getrlimit(resource.RLIMIT_AS)
            cap = memory if current[1] == resource.RLIM_INFINITY else min(memory, current[1])
            resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
            controls, old, rec = self.inputs(node)
            checks = self.validate_inputs(node, controls, old)
            self.di.configure(precision)  # resets directed contexts and counters per path
            work = {'mode': 'OFF', 'node': node, 'N': n, 'precision': precision}
            save(out / 'START.json', {'work': work, 'purpose': purpose, 'source_lock_sha256': self.source_lock_sha256,
                'path_input_sha256': rec['path_input_sha256'], 'started_utc': datetime.now(timezone.utc).isoformat(),
                'host': platform.node(), 'python': sys.version, 'platform': platform.platform(),
                'decimal_libmpdec_version': __import__('decimal').__libmpdec_version__,
                'cpu_affinity': sorted(os.sched_getaffinity(0)), 'provider_attestation': 'NOT_ASSERTED',
                'memory_address_space_limit_bytes': cap, 'wall_seconds_limit': self.plan['limits']['seconds_per_path'],
                'automatic_retries': 0})
            def checkpoint(rows, seams):
                nonlocal complete_segments
                complete_segments = len(rows)
                # Each progress record is fresh; prior failed evidence is retained.
                save(out / ('SEGMENT_%02d_COMPLETE.json' % len(rows)), {'completed_segments': len(rows), 'seams': len(seams),
                     'last_key': rows[-1]['key'], 'elapsed_seconds': time.perf_counter() - started})
            entered = True
            track = self.pe.pack(self.pe.run_track(controls, n, {'controls': []}, checkpoint))
            assert_finite_boxes(track)
            evaluations = sum(s['local']['new_coefficient_evaluations'] for s in track['segments'])
            if evaluations != 2 * n * len(controls):
                raise ArithmeticError('fresh coefficient evaluation count mismatch')
            result = {'schema': 'bass-he-e13c7-off-path-v1', 'status': 'PASS_MECHANICAL_PENDING_INDEPENDENT_ADMISSION',
                'work': work, 'path_input_sha256': rec['path_input_sha256'], 'source_lock_sha256': self.source_lock_sha256,
                'input_checks': checks, 'track': track, 'new_local_enclosures': len(controls),
                'new_coefficient_evaluations': evaluations, 'rounding_operation_counts': dict(self.di.COUNTS),
                'forbidden_invocations': forbidden, 'elapsed_seconds': time.perf_counter() - started,
                'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'finished_utc': datetime.now(timezone.utc).isoformat(),
                'claim_ceiling': 'conditional finite fixed-captured-branch enclosure; no continuum, physical, production or receiver promotion'}
            oldm = old_metrics(old)
            newm = new_metrics(track, capture(controls[0]['row']['weight']))
            comparisons = compare_metrics(oldm, newm)
            if not all(x['overlap'] for x in comparisons):
                save(out / 'RAW_COMPARISON_FAILURE.json', {'rows': comparisons, 'intersection_used': False})
                raise ArithmeticError('same-target old/new interval non-overlap')
            admission = {'schema': 'bass-he-e13c7-path-admission-v1', 'work': work,
                'source_lock_sha256': self.source_lock_sha256, 'path_input_sha256': rec['path_input_sha256'],
                'old_weighted': encode_metrics(oldm), 'new_raw_weighted': encode_metrics(newm),
                'comparisons': comparisons, 'count': 34, 'overlap_count': sum(x['overlap'] for x in comparisons),
                'nested_count': sum(x['nested'] for x in comparisons),
                'nonincreasing_count': sum(x['width_nonincreasing'] for x in comparisons),
                'mechanically_admissible': all(x['nested'] and x['width_nonincreasing'] for x in comparisons),
                'intersection_used': False, 'independent_decision': 'PENDING'}
            save(out / 'RESULT.json', result)
            save(out / 'ADMISSION.json', admission)
            summary = {'node': node, 'N': n, 'precision': precision, 'semantic_sha256': semantic_sha(result),
                'elapsed_seconds': result['elapsed_seconds'], 'peak_RSS_KiB': result['peak_RSS_KiB'],
                'new_coefficient_evaluations': evaluations, 'new_local_enclosures': len(controls),
                'mechanically_admissible': admission['mechanically_admissible'],
                'source_lock_sha256': self.source_lock_sha256, 'path_input_sha256': rec['path_input_sha256'],
                'result_sha256': sha(out / 'RESULT.json'), 'admission_sha256': sha(out / 'ADMISSION.json')}
            save(out / 'COMPLETE.json', {'schema': 'bass-he-e13c7-path-complete-v1', 'status': 'COMPLETE', **summary})
            return summary
        except BaseException as exc:
            save(out / 'FAILURE.json', {'status': 'FAIL_PRESERVED_NO_AUTOMATIC_RETRY', 'error_type': type(exc).__name__,
                'error': str(exc), 'traceback': traceback.format_exc(), 'node': node, 'N': n, 'precision': precision,
                'source_lock_sha256': self.source_lock_sha256, 'scientific_path_entered': entered,
                'completed_segments': complete_segments, 'elapsed_seconds': time.perf_counter() - started,
                'forbidden_invocations': forbidden, 'automatic_retries': 0})
            raise
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)

def validate_completed(ctx, node, n, precision, path):
    """Read and verify saved bytes and exact relations; no numerical rerun."""
    p = Path(path)
    if (p / 'FAILURE.json').exists() or (p / 'RAW_COMPARISON_FAILURE.json').exists():
        raise ValueError('failed path cannot be reused as complete')
    receipt, result, admission = [read(p / f) for f in ('COMPLETE.json', 'RESULT.json', 'ADMISSION.json')]
    work = {'mode': 'OFF', 'node': int(node), 'N': int(n), 'precision': int(precision)}
    controls, old, rec = ctx.inputs(int(node))
    if receipt['status'] != 'COMPLETE' or result['work'] != work or admission['work'] != work:
        raise ValueError('saved work identity mismatch')
    for obj in (receipt, result, admission):
        if obj['source_lock_sha256'] != ctx.source_lock_sha256 or obj['path_input_sha256'] != rec['path_input_sha256']:
            raise ValueError('saved source/input identity mismatch')
    if receipt['result_sha256'] != sha(p / 'RESULT.json') or receipt['admission_sha256'] != sha(p / 'ADMISSION.json'):
        raise ValueError('saved result/admission byte mismatch')
    if receipt['semantic_sha256'] != semantic_sha(result):
        raise ValueError('saved numerical semantic mismatch')
    if any(result['forbidden_invocations'].values()) or result['new_coefficient_evaluations'] != 2 * n * len(controls):
        raise ValueError('saved invocation count mismatch')
    assert_finite_boxes(result['track'])
    oldm = old_metrics(old)
    newm = new_metrics(result['track'], capture(controls[0]['row']['weight']))
    if admission['old_weighted'] != encode_metrics(oldm) or admission['new_raw_weighted'] != encode_metrics(newm):
        raise ValueError('saved exact weighted definitions mismatch')
    comparisons = compare_metrics(oldm, newm)
    if comparisons != admission['comparisons'] or not all(x['overlap'] for x in comparisons):
        raise ValueError('saved interval comparison mismatch')
    if admission['intersection_used'] or admission['mechanically_admissible'] != all(x['nested'] and x['width_nonincreasing'] for x in comparisons):
        raise ValueError('saved mechanical admission mismatch')
    return {k: receipt[k] for k in ('node', 'N', 'precision', 'semantic_sha256', 'elapsed_seconds', 'peak_RSS_KiB',
            'new_coefficient_evaluations', 'new_local_enclosures', 'mechanically_admissible', 'source_lock_sha256',
            'path_input_sha256', 'result_sha256', 'admission_sha256')}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--node', type=int, required=True)
    p.add_argument('--subdivisions', type=int, required=True)
    p.add_argument('--precision', type=int, default=60)
    p.add_argument('--purpose', default='local')
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    ctx = Context(a.package)
    print(json.dumps(ctx.run(a.node, a.subdivisions, a.precision, a.output_dir, a.purpose), sort_keys=True), flush=True)

if __name__ == '__main__':
    main()
