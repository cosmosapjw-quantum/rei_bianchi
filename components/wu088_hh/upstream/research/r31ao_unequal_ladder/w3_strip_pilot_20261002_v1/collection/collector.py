"""Source-bound W1 reuse and exact partial collection for the fixed W3 pilot.

No worker is launched here. Normalization reads original evidence. Collection
accepts trusted normalized records; their SHA seals provide integrity, not
cryptographic authentication. Missing-cell contributions are never set to zero.
"""
from __future__ import annotations
import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
NEW = HERE.parent
LADDER = NEW.parent
W1 = LADDER / 'w1_parallel_20261002_v1'
DESIGN = LADDER / 'w3_design_20261002_v1'
W1_ROOT = W1 / 'runtime/W1_CAMPAIGN'
RUNNER = W1 / 'tile_runner/runner.py'
HOST = W1 / 'process_host/host.py'
GEOMETRY = DESIGN / 'FUTURE_INTERIOR_DESIGN.json'
GLOBAL = DESIGN / 'runtime/CROSSCHECK_PLAN.json'
ENDPOINT = DESIGN / 'runtime/CROSSCHECK_RESULT.json'
SCOPE = NEW / 'SCOPE.json'
RUNNER_SHA = '37f2b99abb6d2f6951243c88feccfb16225cc109eb70748221c905a8c8d9fe29'
HOST_SHA = '1274f166132e0fed8af61b71db00f1f4bacae2e9fea1b8c97ba33599dd808c5e'
GEOMETRY_SHA = '7ae97c0069ae4e773a7c22d832065feb12bef417640c3ead6c70caf373e54b10'
GLOBAL_FILE_SHA = 'aaf73408a4f694b9d567c8f26cab445bcb0baa1b263cd74a5e5b18f981ac6a63'
GLOBAL_SHA = '3a257feb7b65ba78d6c68671a0bb38bd0182e8c8180977811843eaa570151e89'
ENDPOINT_SHA = '1114701c5c1a8da61dca99f70d22e1c73df2306dea55986010f2509ced5ad760'
W1_PREPARED_FILE_SHA = 'bea1218aab8ce9cb618a0bf404f4ba0f2247d53f546dfe7a28d6a7bf8963e7bc'
W1_PREPARED_SHA = 'e85c2fa451d00a32f7d129d55e82f45ffee71342af0fd39d1b9ac81b4d84a4a9'
W1_COLLECTED_SHA = '8d2f8aa59612251cac7df5c718f2f3ec19c1b8fbaaf1dc1a413ec3b16aa0a96b'
INPUT_SHA = '8482d2854ab620c58bb1d7a7a45cf88eb71fd75081242263a9ef48927f0a282c'
RECORD_SHA = '2439151399b049bb83597eb9a80ea7ea0c2922c4a8b9a3c8e0b0f2ba22efee18'
BUILD_SHA = '13965d2210e976f0d7a190fba58f8c3c1bf366521e8dd1bd5e9a28cdae9e9342'
SOURCE_SHA = 'de1e32d8a68146a49d269614c2259ec06f10a5294ffa05b15d375239518bcae1'
AXIS = [-9, -6, -4, -1, 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 40]
WINDOW_KEYS = ('l_t', 'T_t', 'l_u', 'T_u')
GLOBAL_WINDOW = {'l_t': '1/512', 'T_t': '1099511627776', 'l_u': '1/512', 'T_u': '1099511627776'}
PILOT_IDS = [20, 52, 105, 57]
LIMITS = {'precision_bits': 128, 'radius_exp': -57, 'relative_goal': 128,
          'max_evaluations': 200000, 'max_integration_calls': 1024,
          'wall_seconds': 120, 'queued_panels': 64, 'degree_limit': 64, 'memory_mib': 1024}
MAX_BYTES = 16 * 1024 * 1024


class CollectionError(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def sealed(value, key):
    if type(value) is not dict or key in value:
        raise CollectionError('unsealed dictionary required')
    return {**copy.deepcopy(value), key: digest(canonical(value))}


def source_sha():
    return digest(read(__file__))


def read(path):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise CollectionError('bounded nonsymlink regular file required: ' + str(p))
    data = p.read_bytes()
    if len(data) > MAX_BYTES:
        raise CollectionError('file grew past cap')
    return data


def write_new(path, value):
    with Path(path).open('xb') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True).encode() + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def fixed(path, sha):
    data = read(path)
    if digest(data) != sha:
        raise CollectionError('fixed source/artifact bytes changed: ' + str(path))
    return data


def import_fixed(path, name, sha):
    fixed(path, sha)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def checked_hash(value):
    if type(value) is not str or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise CollectionError('canonical SHA-256 required')
    return value


def selfhash(value, key):
    if type(value) is not dict or checked_hash(value.get(key)) != digest(canonical({k: v for k, v in value.items() if k != key})):
        raise CollectionError('envelope digest mismatch: ' + key)


def checked_scope():
    scope = json.loads(read(SCOPE))
    required = {'schema': 'WU088_W3_STRIP_PILOT_SCOPE_V1', 'global_window': GLOBAL_WINDOW,
                'primitive_index': 0, 'precision_bits': 128, 'planned_total_cells': 289,
                'reused_W1_cells': 16, 'pilot_cell_ids': PILOT_IDS, 'native_limits': LIMITS,
                'max_new_native_invocations': 4, 'max_concurrent_workers': 2,
                'worker_wall_seconds': 180, 'worker_memory_mib': 1024,
                'native_hard_wall_seconds': 125, 'max_aggregate_native_wall_cap_seconds': 500,
                'max_aggregate_native_evaluation_cap': 800000, 'stop_on_first_rejection': True,
                'drain_already_running_on_rejection': True, 'automatic_retry': False,
                'completed_W1_rerun': False, 'prior_endpoint_recalculation': False,
                'native_kernel_or_backend_change': False, 'NCP_or_MPI_execution': False,
                'scientific_admission': False, 'production_admission': False}
    if type(scope) is not dict or any(canonical(scope.get(k)) != canonical(v) for k, v in required.items()):
        raise CollectionError('fixed pilot execution scope changed')
    return scope


def context():
    """Validate fixed input/native/backend and read endpoint evidence; no science run."""
    runner = import_fixed(RUNNER, 'wu088_w3_old_w1_runner', RUNNER_SHA)
    host = import_fixed(HOST, 'wu088_w3_old_process_host', HOST_SHA)
    host.identity()
    old = runner.context()
    d, planner = old['d'], old['planner']
    global_plan = d.parse_json(fixed(GLOBAL, GLOBAL_FILE_SHA))
    planner.validate_plan(global_plan, source_archive_bytes=old['raw'])
    if global_plan['plan_sha256'] != GLOBAL_SHA or global_plan['window'] != GLOBAL_WINDOW or global_plan['input_record'] != old['record']:
        raise CollectionError('fixed W3 endpoint plan/input mismatch')
    endpoint = d.parse_json(fixed(ENDPOINT, ENDPOINT_SHA))
    planner.validate_result(global_plan, endpoint)
    if endpoint['index'] != 0 or endpoint['status'] != 'CONDITIONAL_TAIL_BOUND':
        raise CollectionError('fixed primitive-zero endpoint evidence required')
    checked_scope()
    return {'d': d, 'planner': planner, 'raw': old['raw'], 'record': old['record'],
            'manifest': old['manifest'], 'global_plan': global_plan, 'endpoint': endpoint,
            'w1_ctx': old, 'w1_runner': runner, 'host': host}


def _plan_payload():
    geometry = json.loads(fixed(GEOMETRY, GEOMETRY_SHA))
    checked_scope()
    cells = []
    for i in range(17):
        for j in range(17):
            logs = dict(zip(WINDOW_KEYS, (AXIS[i], AXIS[i + 1], AXIS[j], AXIS[j + 1])))
            old_id = (i - 2) * 4 + j - 2 if 2 <= i < 6 and 2 <= j < 6 else None
            cells.append({'cell_id': len(cells), 'window': {k: str(Fraction(2) ** v) for k, v in logs.items()},
                          'log2_window': logs, 'existing_W1_tile_id': old_id})
    actual = [{k: cell[k] for k in ('cell_id', 'window', 'log2_window', 'existing_W1_tile_id')} for cell in geometry['cells']]
    if actual != cells or geometry['global_window'] != GLOBAL_WINDOW or geometry['log2_t_axis'] != AXIS or geometry['log2_u_axis'] != AXIS or geometry['tile_count'] != 289:
        raise CollectionError('source geometry is not the exact fixed Cartesian partition')
    return {'schema': 'WU088_W3_PARTIAL_COLLECTION_PLAN_V1', 'primitive_index': 0,
            'global_window': copy.deepcopy(GLOBAL_WINDOW), 'precision_bits': 128,
            'global_radius_exp': -48, 'new_cell_radius_exp': -57,
            'log2_t_axis': list(AXIS), 'log2_u_axis': list(AXIS), 'cell_count': 289,
            'cells': cells, 'pilot_cell_ids': list(PILOT_IDS), 'native_limits': dict(LIMITS),
            'bindings': {'geometry_file_sha256': GEOMETRY_SHA, 'global_endpoint_plan_file_sha256': GLOBAL_FILE_SHA,
                         'global_endpoint_plan_sha256': GLOBAL_SHA, 'endpoint_result_file_sha256': ENDPOINT_SHA,
                         'archive_sha256': INPUT_SHA, 'input_record_sha256': RECORD_SHA,
                         'build_manifest_sha256': BUILD_SHA, 'build_source_sha256': SOURCE_SHA,
                         'old_W1_validator_sha256': RUNNER_SHA, 'process_host_source_sha256': HOST_SHA,
                         'old_W1_prepared_file_sha256': W1_PREPARED_FILE_SHA,
                         'old_W1_collected_file_sha256': W1_COLLECTED_SHA,
                         'scope_file_sha256': digest(read(SCOPE)), 'validator_source_sha256': source_sha()},
            'endpoint_included': False, 'full_domain_integral': False,
            'scientific_admission': False, 'production_admission': False}


def make_plan(ctx):
    if ctx['global_plan']['plan_sha256'] != GLOBAL_SHA or ctx['manifest']['manifest_sha256'] != BUILD_SHA or ctx['record']['canonical_record_sha256'] != RECORD_SHA:
        raise CollectionError('context does not bind fixed W3/source')
    return sealed(_plan_payload(), 'plan_sha256')


def checked_plan(plan):
    selfhash(plan, 'plan_sha256')
    if canonical(plan) != canonical(sealed(_plan_payload(), 'plan_sha256')):
        raise CollectionError('fixed W3 collection plan changed')
    return plan


def checked_cell(plan, cell_id):
    if type(cell_id) is not int or not 0 <= cell_id < 289:
        raise CollectionError('bounded integer cell ID required')
    return plan['cells'][cell_id]


def local_plan(ctx, plan, cell_id):
    checked_plan(plan)
    cell = checked_cell(plan, cell_id)
    glob = ctx['global_plan']
    if glob['plan_sha256'] != GLOBAL_SHA or glob['input_record'] != ctx['record']:
        raise CollectionError('changed W3 global source')
    return ctx['planner'].build_plan(glob['input_record'], cell['window'], precision_bits=128,
                                    panels=glob['panels'], caps=glob['caps'], source_archive_bytes=ctx['raw'])


def _record(plan, cell_id, rectangle, radii, native_plan_sha, receipt_sha, origin):
    cell = checked_cell(plan, cell_id)
    value = {'schema': 'WU088_W3_TRUSTED_NORMALIZED_CELL_V1', 'cell_id': cell_id,
             'primitive_index': 0, 'global_plan_sha256': plan['plan_sha256'],
             'window': copy.deepcopy(cell['window']), 'precision_bits': 128,
             'required_actual_radius_exp': -57, 'status': 'RADIUS_MET', 'accepted': True,
             'endpoint_included': False, 'normalization_applied': False,
             'full_domain_integral': False, 'scientific_admission': False, 'production_admission': False,
             'bindings': copy.deepcopy(plan['bindings']), 'origin': copy.deepcopy(origin),
             'native_plan_sha256': checked_hash(native_plan_sha), 'native_receipt_sha256': checked_hash(receipt_sha),
             'rectangle': copy.deepcopy(rectangle), 'reported_radius': copy.deepcopy(radii)}
    return sealed(value, 'record_sha256')


def import_w1(ctx, plan):
    """Revalidate all sixteen raw W1 receipts and terminal states before rebinding."""
    checked_plan(plan)
    fixed(W1_ROOT / 'PREPARED.json', W1_PREPARED_FILE_SHA)
    expected_collected = ctx['d'].parse_json(fixed(W1_ROOT / 'COLLECTED.json', W1_COLLECTED_SHA))
    old, prepared, locals_ = ctx['w1_runner'].load_prepared(W1_ROOT, W1_PREPARED_SHA, ctx=ctx['w1_ctx'])
    records, failures, attempted = ctx['w1_runner'].load_state(W1_ROOT, old, prepared, locals_)
    if failures or attempted != list(range(1, 16)) or set(records) != set(range(16)):
        raise CollectionError('complete raw-verified W1 campaign required')
    if old['c'].collect(prepared['grid'], [records[i] for i in range(16)]) != expected_collected:
        raise CollectionError('raw W1 evidence disagrees with pinned collected result')
    result = []
    for cell in plan['cells']:
        i = cell['existing_W1_tile_id']
        if i is None:
            continue
        r = records[i]
        if r['window'] != cell['window'] or r['primitive_index'] != 0 or r['precision_bits'] != 128 or r['requested_radius_exp'] != -52:
            raise CollectionError('old W1 primitive/window/precision/request mismatch')
        for key in ('archive_sha256', 'input_record_sha256', 'build_manifest_sha256', 'build_source_sha256'):
            if r['bindings'][key] != plan['bindings'][key]:
                raise CollectionError('old/new source identity mismatch: ' + key)
        rp = ctx['w1_runner'].IMPORTED if i == 0 else W1_ROOT / 'raw' / ('%02d.json' % i)
        origin = {'kind': 'REUSED_W1_RAW_EVIDENCE', 'old_W1_tile_id': i,
                  'requested_radius_exp': -52, 'new_native_execution': False,
                  'prepared_sha256': W1_PREPARED_SHA, 'old_normalized_record_sha256': r['record_sha256'],
                  'receipt_path': str(rp.resolve())}
        result.append(_record(plan, cell['cell_id'], r['rectangle'], r['reported_radius'],
                              r['native_plan_sha256'], r['native_receipt_sha256'], origin))
    # Checks the tighter actual-radius requirement; the old request is unchanged.
    collect_partial(plan, result)
    return result


def normalize_new(ctx, plan, cell_id, receipt_path):
    checked_plan(plan)
    cell = checked_cell(plan, cell_id)
    if cell_id not in PILOT_IDS or cell['existing_W1_tile_id'] is not None:
        raise CollectionError('only fixed new pilot cells may be normalized')
    lp = local_plan(ctx, plan, cell_id)
    d, m = ctx['d'], ctx['manifest']
    limits = d.limits_checked(checked_scope()['native_limits'])
    path = Path(receipt_path).resolve()
    receipt_bytes = read(path)
    record = d.parse_json(receipt_bytes)
    selfhash(record, 'result_sha256')
    if 'wrapper' not in record:
        raise CollectionError('source-bound wrapper required')
    wrapper = record['wrapper']
    native = {k: v for k, v in record.items() if k not in ('wrapper', 'result_sha256')}
    task = lp['tasks'][0]
    d.validate_result(native, plan=lp, task=task, manifest=m, limits=limits)
    command = [str((ctx['w1_runner'].BUILD / 'primitive_worker').resolve()), str(task['index']),
               *[lp['window'][k] for k in WINDOW_KEYS],
               *[str(limits[k]) for k in ('precision_bits', 'radius_exp', 'relative_goal', 'max_evaluations',
                                           'max_integration_calls', 'wall_seconds', 'queued_panels', 'degree_limit')],
               task['task_sha256'], lp['plan_sha256']]
    expected = {'schema': 'WU088_LOG2_NATIVE_INTERIOR_WRAPPER_V1', 'build_manifest_sha256': BUILD_SHA,
                'binary_sha256': m['binary_sha256'], 'build_source': m['source'], 'archive_sha256': INPUT_SHA,
                'input_record_sha256': RECORD_SHA, 'native_limits': limits, 'command': command,
                'coordinate_map': 'LOG2_EXACT_POWER_ENDPOINTS_V1', 'physical_window': lp['window'],
                'log2_window': d.log2_window(lp['window']), 'backend_provenance_sha256': m['backend_provenance_sha256'],
                'linkage': m['linkage'], 'native_execution_observed': True,
                'scope': 'CONDITIONAL_COMPACT_INTERIOR_ONLY',
                'evidence_contract': 'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
                'validation_level': 'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY',
                'endpoint_plan_module_sha256': digest(read(d.PLAN_MODULE)),
                'historical_abi_admission': False, 'independent_scientific_review': False, 'returncode': 0}
    extras = {'elapsed_wall_ns', 'native_stdout_sha256', 'native_stderr_sha256', 'process_host'}
    if type(wrapper) is not dict or set(wrapper) != set(expected) | extras:
        raise CollectionError('exact wrapper keys required')
    for key, value in expected.items():
        if canonical(wrapper[key]) != canonical(value):
            raise CollectionError('native wrapper mismatch: ' + key)
    if type(wrapper['elapsed_wall_ns']) is not int or wrapper['elapsed_wall_ns'] < 0:
        raise CollectionError('elapsed nonnegative integer ns required')
    ctx['host'].validate_receipt(wrapper['process_host'], command=command, limits=limits, output_path=path)
    if wrapper['process_host']['timed_out'] is not False or wrapper['process_host']['native_execution_evidence'] != 'SOURCE_BOUND_NATIVE_STDOUT':
        raise CollectionError('positive native execution and no timeout required')
    stdout, stderr = read(str(path) + '.stdout'), read(str(path) + '.stderr')
    if digest(stdout) != wrapper['native_stdout_sha256'] or digest(stderr) != wrapper['native_stderr_sha256'] or canonical(d.parse_json(stdout)) != canonical(native):
        raise CollectionError('raw native stream identity mismatch')
    rectangle, radii = {}, {}
    for part in ('real', 'imag'):
        lo, hi = d.dyadic_interval(native['rectangle'][part])
        rectangle[part] = {'lower': str(lo), 'upper': str(hi)}
        radii[part] = str((hi - lo) / 2)
    origin = {'kind': 'NEW_PILOT_RAW_EVIDENCE', 'old_W1_tile_id': None,
              'requested_radius_exp': -57, 'new_native_execution': True,
              'prepared_sha256': None, 'old_normalized_record_sha256': None, 'receipt_path': str(path)}
    result = _record(plan, cell_id, rectangle, radii, lp['plan_sha256'], digest(receipt_bytes), origin)
    collect_partial(plan, [result])
    return result


def rational(token):
    if type(token) is not str or len(token) > 5000 or not re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?', token):
        raise CollectionError('bounded canonical rational required')
    if any(len(s.lstrip('-')) > 2467 for s in token.split('/')):
        raise CollectionError('dyadic integer bit cap')
    value = Fraction(token)
    if str(value) != token or max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 8192 or value.denominator & (value.denominator - 1):
        raise CollectionError('bounded canonical dyadic required')
    return value


def collect_partial(plan, records):
    """Exact accepted-union sum. Trusted normalization is a caller precondition."""
    checked_plan(plan)
    if type(records) is not list or len(records) > 289:
        raise CollectionError('bounded normalized record list required')
    totals = {part: [Fraction(0), Fraction(0)] for part in ('real', 'imag')}
    seen, receipts, items = set(), set(), []
    for r in records:
        if type(r) is not dict:
            raise CollectionError('normalized record object required')
        selfhash(r, 'record_sha256')
        cell_id = r.get('cell_id')
        cell = checked_cell(plan, cell_id)
        if cell_id in seen or r.get('native_receipt_sha256') in receipts:
            raise CollectionError('duplicate cell or native receipt')
        old_id = cell['existing_W1_tile_id']
        if old_id is None and cell_id not in PILOT_IDS:
            raise CollectionError('new cell outside this bounded pilot')
        origin = r.get('origin')
        if type(origin) is not dict or set(origin) != {'kind', 'old_W1_tile_id', 'requested_radius_exp', 'new_native_execution', 'prepared_sha256', 'old_normalized_record_sha256', 'receipt_path'}:
            raise CollectionError('exact evidence origin required')
        is_old = old_id is not None
        expected_origin = {'kind': 'REUSED_W1_RAW_EVIDENCE' if is_old else 'NEW_PILOT_RAW_EVIDENCE',
                           'old_W1_tile_id': old_id, 'requested_radius_exp': -52 if is_old else -57,
                           'new_native_execution': not is_old, 'prepared_sha256': W1_PREPARED_SHA if is_old else None}
        if any(canonical(origin[k]) != canonical(v) for k, v in expected_origin.items()):
            raise CollectionError('origin/requested precision contract changed')
        if type(origin['receipt_path']) is not str or not Path(origin['receipt_path']).is_absolute():
            raise CollectionError('absolute evidence path required')
        if is_old:
            checked_hash(origin['old_normalized_record_sha256'])
        elif origin['old_normalized_record_sha256'] is not None:
            raise CollectionError('new cell cannot claim prior normalization')
        expected = _record(plan, cell_id, r.get('rectangle'), r.get('reported_radius'),
                           r.get('native_plan_sha256'), r.get('native_receipt_sha256'), origin)
        if canonical(r) != canonical(expected):
            raise CollectionError('exact normalized cell contract changed')
        if type(r['rectangle']) is not dict or set(r['rectangle']) != set(totals) or type(r['reported_radius']) is not dict or set(r['reported_radius']) != set(totals):
            raise CollectionError('exact rectangle and radius components required')
        for part in totals:
            interval = r['rectangle'][part]
            if type(interval) is not dict or set(interval) != {'lower', 'upper'}:
                raise CollectionError('exact interval endpoints required')
            lo, hi = rational(interval['lower']), rational(interval['upper'])
            radius = rational(r['reported_radius'][part])
            if lo > hi or radius != (hi - lo) / 2 or not 0 <= radius <= Fraction(2) ** -57:
                raise CollectionError('actual serialized radius fails tighter W3 allocation')
            totals[part][0] += lo
            totals[part][1] += hi
        seen.add(cell_id)
        receipts.add(r['native_receipt_sha256'])
        items.append({'cell_id': cell_id, 'window': copy.deepcopy(cell['window']),
                      'origin_kind': origin['kind'], 'native_plan_sha256': r['native_plan_sha256'],
                      'native_receipt_sha256': r['native_receipt_sha256'], 'normalized_record_sha256': r['record_sha256']})
    missing = sorted(set(range(289)) - seen)
    radius = {part: (v[1] - v[0]) / 2 for part, v in totals.items()}
    if any(v > Fraction(2) ** -48 for v in radius.values()):
        raise CollectionError('accepted subset exceeds global component radius budget')
    return sealed({'schema': 'WU088_W3_EXACT_PARTIAL_COMPACT_INTERIOR_V1',
                   'status': 'PARTIAL_COMPACT_INTERIOR' if missing else 'COMPLETE_COMPACT_INTERIOR_RADIUS_MET',
                   'primitive_index': 0, 'precision_bits': 128, 'global_plan_sha256': plan['plan_sha256'],
                   'global_window': copy.deepcopy(GLOBAL_WINDOW), 'bindings': copy.deepcopy(plan['bindings']),
                   'accepted_cell_ids': sorted(seen), 'missing_cell_ids': missing,
                   'accepted_cell_count': len(seen), 'planned_cell_count': 289,
                   'coverage_complete': not missing, 'global_complete': not missing,
                   'domain': 'UNION_OF_LISTED_ACCEPTED_CELLS_ONLY', 'missing_domain_contribution': 'NOT_BOUNDED_OR_INCLUDED',
                   'rectangle': {p: {'lower': str(v[0]), 'upper': str(v[1])} for p, v in totals.items()},
                   'component_radius': {p: str(v) for p, v in radius.items()},
                   'accepted_component_radius_exp': -48, 'cells': sorted(items, key=lambda x: x['cell_id']),
                   'endpoint_included': False, 'normalization_applied': False, 'full_domain_integral': False,
                   'scientific_admission': False, 'production_admission': False,
                   'validation_scope': 'RAW_EVIDENCE_NORMALIZATION_THEN_EXACT_ACCEPTED_UNION_SUM'}, 'result_sha256')
