#!/usr/bin/env python3
"""Opt-in R31V B192 adapter. Legacy arithmetic/evidence files are unchanged.

Modes: describe (no native import), prepare (explicit serial references), and
benchmark (cache-only references; native work in every timed batch). This is
not a host scheduler and does not assert an exclusive cgroup was installed.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'research/r31s_ncp/m3_throughput.py': '99d4f0b72b1a6f999d994845e5f8249093b425d2',
    'research/r31s_ncp/m3_full_pair_screen.py': 'd6781e9a66202a6cb3b456f69b8bff7913394939',
    'research/r31s_ncp/authority_m3/m3_h0_authority.py': '233a9be2893bc92c8ccb18cbcbe4ae2dbf3c97b4',
    'src/wu088_hh/native_candidate.py': 'bc9c92bb19da8f3f2c95d2b4d3193b4d2348d0e6',
}


def perform_measured_batches(measure, recheck, checkpoint, processes):
    """Exactly three real backend calls, each bracketed by a live grant check."""
    rows = []
    for _ in range(3):
        recheck()
        row = measure()
        try:
            recheck()
        except BaseException as exc:
            row['measurement_status'] = 'POSTCHECK_FAILED'
            row['postcheck_failure'] = {'type': type(exc).__name__, 'message': str(exc)}
            checkpoint(row)
            raise
        if not row['all_exact'] or row['nr_throttled_delta'] != 0:
            row['measurement_status'] = 'EXACTNESS_OR_THROTTLING_FAILED'
            checkpoint(row)
            raise RuntimeError('exactness/throttling gate failed')
        try:
            _validate_measurement_row(row, processes)
        except RuntimeError as exc:
            row['measurement_status'] = 'MEASUREMENT_VALIDATION_FAILED'
            row['validation_failure'] = str(exc)
            checkpoint(_failure_checkpoint(row))
            raise
        row['parallelism_engaged'] = None
        if processes >= 16:
            row['parallelism_engaged'] = (
                row['active_worker_count'] >= max(8, int(.75*processes))
                and row['worker_cpu_parallelism'] > 4
                and row['effective_cpu_parallelism'] is not None
                and row['effective_cpu_parallelism'] > 4)
            if not row['parallelism_engaged']:
                row['measurement_status'] = 'WORKER_ENGAGEMENT_FAILED'
                checkpoint(row)
                raise RuntimeError('worker engagement gate failed')
        row['cgroup_cpu_scope'] = 'SHARED_ANCESTOR_UNLESS_SEPARATELY_VERIFIED'
        row['measurement_status'] = 'RESOURCE_CHECKS_PASSED_REVIEW_REQUIRED'
        rows.append(row)
        checkpoint(row)
    return rows


def _blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def _runtime():
    # Set thread controls before NumPy/native imports, not inside running workers.
    if any(os.environ.get(k) for k in ('LD_PRELOAD', 'LD_LIBRARY_PATH')):
        raise RuntimeError('unset loader overrides before trusted native setup')
    for k in ('OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[k] = '1'
    os.environ['OMP_DYNAMIC'] = 'FALSE'
    for path, expected in PINS.items():
        if _blob(ROOT/path) != expected:
            raise RuntimeError('legacy interface/source pin drift: '+path)
    sys.path[:0] = [str(ROOT), str(ROOT/'src')]
    return importlib.import_module('research.r31s_ncp.m3_throughput')


def _numeric_context(c, m3, h0mod, h0, seed, built, grid):
    np = m3.np
    fegetround = ctypes.CDLL(None).fegetround
    fegetround.restype = ctypes.c_int
    rounding = fegetround()
    if rounding != 0:
        raise RuntimeError('FE_TONEAREST required for this reference context')
    array_ids = []
    for a in grid:
        a = np.ascontiguousarray(a)
        array_ids.append({'dtype': a.dtype.str, 'shape': list(a.shape),
                          'sha256': hashlib.sha256(a.tobytes()).hexdigest()})
    return {'schema': 'WU088_R31V_NUMERIC_CONTEXT_V1', 'legacy_blobs': PINS,
            'authority_sources': h0mod.verify_sources(),
            'h0_binary_sha256': h0.manifest['binary_sha256'],
            'h0_compile_spec': h0.manifest['spec'],
            'foreign_binary_sha256': {k:c.sha256(Path(built['libraries'][k]['path'])) for k in ('reference','candidate')},
            'seed_sha256': c.sha256(Path(seed.__file__)), 'grid_arrays': array_ids,
            'n':192, 'g':80, 'z_hex':float(2).hex(),
            'normalization':'legacy m3_full_pair.full_pair unchanged',
            'numpy_version':np.__version__, 'python':platform.python_version(),
            'machine':platform.machine(), 'libc':list(platform.libc_ver()),
            'byteorder':sys.byteorder, 'longdouble_nmant':np.finfo(np.longdouble).nmant,
            'longdouble_itemsize':np.dtype(np.longdouble).itemsize, 'fegetround':rounding}


def _require_existing_h0_cache(h0mod, cache):
    """Prevent the benchmark's ordinary setup path from compiling a missing H0."""
    compiler_name = shutil.which('g++')
    if compiler_name is None:
        raise RuntimeError('system compiler identity cannot be checked')
    compiler = str(Path(compiler_name).resolve())
    spec = {'sources': h0mod.verify_sources(), 'flags': h0mod.FLAGS,
            'compiler_version':subprocess.run([compiler,'--version'],capture_output=True,text=True,check=True).stdout}
    key = hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()
    folder = Path(cache).resolve()/key
    if not (folder/'h0.so').is_file() or not (folder/'BUILD.json').is_file():
        raise RuntimeError('H0 build cache missing; perform explicit preparation first')


def _verify_foreign_build(c, built):
    for relative, recorded in built['identity']['sources'].items():
        if c.sha256(ROOT/'native'/relative) != recorded:
            raise RuntimeError('foreign build source drift: '+relative)
    for name in ('reference', 'candidate'):
        library = built['libraries'][name]
        if c.sha256(Path(library['path'])) != library['sha256']:
            raise RuntimeError('foreign build binary drift: '+name)


def _finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _positive_integer(value):
    return type(value) is int and value > 0


def _validate_pilot_receipt(pilot):
    """Check the recorded B192/G80/z2 memory estimate, not a peak-memory proof."""
    if not isinstance(pilot, dict):
        raise ValueError('pilot receipt must be an object')
    private = pilot.get('pilot_private_worker_bytes')
    configs = pilot.get('configurations')
    if (pilot.get('stage') != 'pilot'
        or type(pilot.get('n')) is not int or pilot['n'] != 192
        or type(pilot.get('g')) is not int or pilot['g'] != 80
        or not _finite_number(pilot.get('z')) or pilot['z'] != 2.0
        or pilot.get('status') != 'PASS_BOUNDED_PERSISTENT_WORKER_SCREEN'
        or not _positive_integer(private)
        or not isinstance(configs, list) or len(configs) != 1):
        raise ValueError('verified B192/G80/z2 private-memory pilot receipt required')
    cfg = configs[0]
    if not isinstance(cfg, dict):
        raise ValueError('pilot configuration must be an object')
    warm = cfg.get('warmup')
    if (type(cfg.get('processes')) is not int or cfg['processes'] != 1
        or type(cfg.get('threads_per_process')) is not int or cfg['threads_per_process'] != 1
        or cfg.get('status') != 'PASS_EXACT_RESOURCE_GATES'
        or cfg.get('memory_gate_pass') is not True
        or not isinstance(warm, dict) or warm.get('all_exact') is not True):
        raise ValueError('pilot receipt lacks the admitted 1x1 exact resource screen')
    observed = [cfg.get('private_worker_bytes'), warm.get('sum_pss_bytes')]
    if any(not _positive_integer(v) for v in observed) or private < max(observed):
        raise ValueError('pilot memory observations missing, malformed, or exceed estimate')
    return private


def _validate_exactness_receipt(exact, context, built, samples):
    """Check identities, geometry and component records; do not recompute arrays."""
    if (not isinstance(exact, dict) or not samples
        or exact.get('status') != 'PASS_SAME_HOST_FULL_PAIR_EXACT_NOT_PRODUCTION'
        or exact.get('all_exact') is not True
        or exact.get('h0_binary_sha256') != context['h0_binary_sha256']
        or exact.get('h0_source_sha256') != context['authority_sources']
        or exact.get('foreign_build_key') != built['build_key']
        or exact.get('grid_seed_sha256') != context['seed_sha256']):
        raise RuntimeError('full-pair exactness receipt is not bound to current setup')
    rows = exact.get('rows')
    if not isinstance(rows, list):
        raise RuntimeError('full-pair receipt rows must be a list')
    required = {(n, tuple(pair)) for n, pairs in samples.items() for pair in pairs}
    expected_components = {'H0': ('complex256', [2, 7, 3]),
        'H0_sumabs': ('float128', [2, 7, 3]),
        'foreign': ('complex256', [2, 2, 3]),
        'foreign_sumabs': ('float128', [2, 2, 3])}
    seen = set()
    for row in rows:
        if (not isinstance(row, dict) or type(row.get('n')) is not int
            or type(row.get('g')) is not int or row['g'] != 80
            or not _finite_number(row.get('z')) or row['z'] != 2.0):
            raise RuntimeError('full-pair receipt lacks required n/g/z sample rows')
        pair = row.get('pair')
        if (not isinstance(pair, (list, tuple)) or len(pair) != 2
            or any(type(v) is not int or v < 0 for v in pair)):
            raise RuntimeError('malformed full-pair sample index')
        key = (row['n'], tuple(pair))
        if key not in required or key in seen or row.get('all_exact') is not True:
            raise RuntimeError('duplicate, unexpected, or non-exact full-pair sample')
        components = row.get('components')
        if not isinstance(components, dict) or set(components) != set(expected_components):
            raise RuntimeError('missing full-pair component evidence')
        for name, (dtype, shape) in expected_components.items():
            comp = components[name]
            if (not isinstance(comp, dict) or comp.get('exact') is not True
                or comp.get('dtype') != dtype or comp.get('shape') != shape
                or not _finite_number(comp.get('max_abs_delta'))
                or comp['max_abs_delta'] != 0):
                raise RuntimeError('inconsistent full-pair component evidence: '+name)
        seen.add(key)
    if seen != required:
        raise RuntimeError('full-pair receipt lacks required n/g/z sample rows')


def _validate_measurement_row(row, processes):
    """Fail closed on malformed or adverse fixed-workload observations."""
    if (row.get('all_exact') is not True
        or type(row.get('tasks_completed')) is not int or row['tasks_completed'] != 132
        or type(row.get('unique_pair_count')) is not int or row['unique_pair_count'] != 12
        or not _positive_integer(row.get('active_worker_count'))
        or row['active_worker_count'] > processes):
        raise RuntimeError('invalid fixed-workload count, exactness, or worker observation')
    wall = row.get('batch_wall_seconds')
    rate = row.get('steady_state_pairs_per_second')
    if (not _finite_number(wall) or wall <= 0
        or not _finite_number(rate) or rate <= 0
        or not math.isclose(rate, 132/wall, rel_tol=1e-12, abs_tol=0)):
        raise RuntimeError('invalid or inconsistent measured wall time/throughput')
    for key in ('worker_cpu_parallelism', 'effective_cpu_parallelism'):
        if not _finite_number(row.get(key)) or row[key] <= 0:
            raise RuntimeError('invalid CPU observation: '+key)
    for key in ('nr_throttled_delta', 'throttled_usec_delta', 'swap_before', 'swap_after'):
        if type(row.get(key)) is not int or row[key] != 0:
            raise RuntimeError('missing or adverse resource observation: '+key)
    events = row.get('memory_events_delta')
    if (not isinstance(events, dict)
        or not {'high', 'max', 'oom', 'oom_kill'} <= set(events)
        or any(type(v) is not int or v != 0 for v in events.values())):
        raise RuntimeError('missing, malformed, or adverse memory events')
    ancestors = row.get('ancestor_cpu_deltas')
    if not isinstance(ancestors, dict) or not ancestors:
        raise RuntimeError('missing ancestor CPU observations')
    for path, counters in ancestors.items():
        if (not isinstance(counters, dict)
            or any(type(counters.get(k)) is not int or counters[k] != 0
                   for k in ('nr_throttled', 'throttled_usec'))):
            raise RuntimeError('missing or adverse ancestor throttling: '+str(path))


def _failure_checkpoint(row):
    """Preserve nonfinite observations explicitly without creating JSON NaN."""
    def safe(value):
        if isinstance(value, float) and not math.isfinite(value):
            return {'__nonfinite_float__': repr(value)}
        if isinstance(value, dict):
            return {k: safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [safe(v) for v in value]
        return value
    result = safe(row)
    result['failure_serialization'] = 'EXPLICIT_NONFINITE_TAGS_V1_NOT_NUMERIC_RESULT'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('describe','prepare','benchmark'), default='describe')
    for name in ('build','h0-cache','grant','reference-cache','exactness','pilot','out'):
        parser.add_argument('--'+name, type=Path)
    parser.add_argument('--configs',default='64x1,32x2,30x2,4x16')
    args = parser.parse_args(argv)
    if args.phase == 'describe':
        print(json.dumps({'phase':'DESCRIBE_ONLY','native_calls':0,'fixed_workload':'12 pairs x 11 repeats',
              'benchmark_repetitions':3,'production_admitted':False,'new_scientific_nodes':0,
              'required_next':'review adapter, verify source/build/pilot and current exclusive grant'},indent=2))
        return 0
    required = ('build','h0_cache','grant','reference_cache','exactness','pilot','out')
    if any(getattr(args,k) is None for k in required):
        parser.error('all file arguments are required for prepare/benchmark')
    if args.out.exists():
        raise FileExistsError(args.out)
    # No native module or old script is imported until the allocation is admitted.
    for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[k] = '1'
    import controls as c
    state = {'schema':'WU088_R31V_POSTIDLE_V1','status':'IN_PROGRESS','phase':args.phase,
             'configs':[],'reference_events':[], 'new_scientific_nodes':0,
             'production_admitted':False,'host_isolation_independently_verified':False}
    c.atomic_json(args.out,state,create_only=True)
    stage = 'preflight'
    try:
        layouts = [tuple(int(v) for v in token.split('x')) for token in args.configs.split(',')]
        grant = json.loads(args.grant.read_text())
        initial = c.live_resources()
        allocation = c.validate_grant(grant, initial, layouts)
        pilot = json.loads(args.pilot.read_text())
        private = _validate_pilot_receipt(pilot)
        if any(2*p*private > allocation['memory_available_bytes'] for p,t in layouts):
            raise ValueError('memory gate failed before reference/native/pool preparation')
        state.update(grant_sha256=c.sha256(args.grant),pilot_sha256=c.sha256(args.pilot),
                     exactness_sha256=c.sha256(args.exactness),initial_resources=initial)
        c.atomic_json(args.out,state)
        stage = 'setup'
        m3 = _runtime()
        h0mod = m3.load_module(ROOT/'research/r31s_ncp/authority_m3/m3_h0_authority.py','r31v_h0')
        seed = m3.load_module(ROOT/'research/r31s_ncp/authority_seed/grid_seed.py','r31v_seed')
        pairmod = m3.load_module(ROOT/'research/r31s_ncp/m3_full_pair_screen.py','r31v_pairs')
        seed.verify_authority()
        model = h0mod.inputs()
        dm,t,W,gs,gw = seed.grid(192,80)
        for k in ('C','exponents','v'):
            if not m3.np.array_equal(model[k],dm[k]):
                raise RuntimeError('model/grid identity mismatch: '+k)
        grid = (t,W,gs,gw)
        built = json.loads(args.build.read_text())
        if built['identity']['flags'][-3:] != ['-fno-fast-math','-ffp-contract=off','-fopenmp']:
            raise RuntimeError('strict foreign flags absent')
        _verify_foreign_build(c,built)
        if args.phase == 'benchmark':
            _require_existing_h0_cache(h0mod,args.h0_cache)
        h0 = h0mod.H0Authority(args.h0_cache)
        context = _numeric_context(c,m3,h0mod,h0,seed,built,grid)
        exact = json.loads(args.exactness.read_text())
        _validate_exactness_receipt(exact, context, built, pairmod.SAMPLES)
        profile = json.loads((ROOT/'data/pair_cost_profile.json').read_text())
        m3.verify_profile(profile,driver_sha=c.sha256(ROOT/'vendor/orchestration/wide_hybrid_run.py'),
                          model_sha=c.sha256(h0mod.FROZEN),g=80,gamma_scale='unit')
        costs,prediction = m3.predict_costs(profile,n=192,z=2.0)
        pairs = m3.select_pairs(costs,12);tasks = c.balanced_workload(pairs)
        state.update(numeric_context=context,reference_context_sha256=c.digest_json(context),
                     workload=c.workload_identity(tasks),pair_cost_prediction_scope=prediction,
                     pair_set=[list(p) for p in pairs])
        store = c.ReferenceCache(args.reference_cache,context)
        expected = {'pairmod':pairmod}
        refkernel = None
        def recheck():
            fresh = c.live_resources()
            a = c.validate_grant(json.loads(args.grant.read_text()),fresh,layouts)
            if c.sha256(args.grant) != state['grant_sha256'] or fresh['cgroup_path'] != initial['cgroup_path']:
                raise RuntimeError('allocation/cgroup changed during epoch')
            if any(2*p*private > a['memory_available_bytes'] for p,t in layouts):
                raise RuntimeError('live memory gate failed')
            return a
        stage = 'reference_preparation' if args.phase=='prepare' else 'reference_readonly'
        for pair in pairs:
            recheck()
            started = time.perf_counter()
            try:
                expected[pair] = store.read(pair);event='CACHE_READ'
            except FileNotFoundError:
                if args.phase != 'prepare':
                    raise RuntimeError('reference missing; benchmark never computes expected outputs')
                if refkernel is None:
                    refkernel=m3.ForeignKernel(Path(built['libraries']['reference']['path']));refkernel.set_threads(1)
                expected[pair] = pairmod.full_pair(h0,refkernel,model,*grid,pair)
                store.write(pair,expected[pair]);event='EXPLICIT_REFERENCE_COMPUTE'
            state['reference_events'].append({'pair':list(pair),'event':event,'wall_seconds':time.perf_counter()-started})
            c.atomic_json(args.out,state)
        if args.phase == 'prepare':
            state['status']='REFERENCE_PREPARATION_COMPLETE_NOT_BENCHMARK'
            c.atomic_json(args.out,state)
            return 0
        ctx = m3.mp.get_context('spawn')
        stage = 'bounded_native_measurement'
        for processes,threads in layouts:
            available = recheck()
            groups = m3.affinity_groups(available['cpus'],processes,threads)
            counter,lock,barrier = ctx.Value('i',0),ctx.Lock(),ctx.Barrier(processes)
            rec = {'processes':processes,'threads_per_process':threads,'repetitions':[],'status':'IN_PROGRESS'}
            state['configs'].append(rec);c.atomic_json(args.out,state)
            begin = time.perf_counter()
            with m3.ProcessPoolExecutor(max_workers=processes,mp_context=ctx,initializer=m3.init_worker,
                initargs=(groups,counter,lock,barrier,str(args.h0_cache),built['libraries']['candidate']['path'],model,grid,192)) as pool:
                infos = list(pool.map(m3.worker_info,range(processes),chunksize=1))
                if len({r['pid'] for r in infos}) != processes or any(r['observed_affinity']!=groups[r['slot']] for r in infos):
                    raise RuntimeError('worker startup identity/affinity mismatch')
                observed_private=max(max(r['pss_bytes'] or r['rss_bytes'] or 0 for r in infos),private)
                if not m3.memory_safe(processes,observed_private,recheck()['memory_available_bytes']):
                    raise RuntimeError('post-startup memory gate failed')
                rec.update(startup_seconds=time.perf_counter()-begin,startup_workers=infos,planned_affinity=groups)
                warm_tasks=[pairs[i%len(pairs)] for i in range(processes)]
                recheck()
                rec['warmup']=m3.batch(pool,warm_tasks,expected,groups,threads,Path(initial['cgroup_path']))
                recheck();c.atomic_json(args.out,state)
                def measure():
                    ancestors = [Path(a['path']) for a in initial['ancestors']]
                    before = {str(path):m3.cgroup_snapshot(path)['cpu_stat'] for path in ancestors}
                    row = m3.batch(pool,tasks,expected,groups,threads,Path(initial['cgroup_path']))
                    after = {str(path):m3.cgroup_snapshot(path)['cpu_stat'] for path in ancestors}
                    row['ancestor_cpu_deltas'] = {path:m3.delta(before[path],after[path]) for path in before}
                    row['ancestor_cpu_scope'] = 'VISIBLE_ANCESTORS_SHARED_WITH_OTHER_SESSIONS'
                    return row
                def checkpoint(row):
                    rec['repetitions'].append(row);c.atomic_json(args.out,state)
                perform_measured_batches(measure,recheck,checkpoint,processes)
                rec['median_pairs_per_second']=m3.statistics.median(r['steady_state_pairs_per_second'] for r in rec['repetitions'])
                rec['status']='EXACT_RESOURCE_CHECKS_COMPLETE_REVIEW_REQUIRED'
            c.atomic_json(args.out,state)
        state['status']='BOUNDED_COMPARISON_COMPLETE_REVIEW_REQUIRED_NOT_PRODUCTION'
        c.atomic_json(args.out,state)
        return 0
    except BaseException as exc:
        state.update(status='BLOCKED',failure_stage=stage,
                     failure={'type':type(exc).__name__,'message':str(exc)},
                     failure_classification='REQUIRES_REVIEW_NOT_AUTOMATIC_SCIENTIFIC_FAILURE')
        c.atomic_json(args.out,state)
        raise


if __name__=='__main__':
    raise SystemExit(main())
