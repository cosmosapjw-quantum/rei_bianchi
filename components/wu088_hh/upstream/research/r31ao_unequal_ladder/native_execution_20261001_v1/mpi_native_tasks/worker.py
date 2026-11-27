"""Fixed native primitive API adapter; requires a separately pinned bound worker.

This is not a native MPI host launcher. Never reuse an existing task output.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
DRIVER = HERE.parent / 'native_driver/driver.py'
MAX_BYTES = 16 * 1024 * 1024
SCHEMA = 'WU088_NATIVE_DISPATCH_MANIFEST_V1'


class Refusal(ValueError): pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def sha(data): return hashlib.sha256(data).hexdigest()


def checked_sha(value):
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}', value):
        raise Refusal('external lowercase SHA256 required')
    return value


def path_checked(value, existing=True):
    if type(value) not in (str, type(Path())): value = str(value)
    p = Path(value)
    if not p.is_absolute() or p != p.resolve(strict=existing):
        raise Refusal('absolute canonical path without symlinks required')
    return p


def read(path):
    p = path_checked(path)
    if not p.is_file() or p.stat().st_size > MAX_BYTES: raise Refusal('bounded regular file required')
    with p.open('rb') as f: data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES: raise Refusal('file byte cap')
    return data


def parse(data):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out: raise Refusal('duplicate JSON key')
            out[k] = v
        return out
    def refuse(_): raise Refusal('floating/nonfinite JSON forbidden')
    return json.loads(data, object_pairs_hook=pairs, parse_float=refuse, parse_constant=refuse)


def keys(obj, expected):
    if type(obj) is not dict or set(obj) != set(expected): raise Refusal('exact contract keys required')


def identity(path):
    data = read(path)
    return {'path': str(path_checked(path)), 'bytes': len(data), 'sha256': sha(data)}


def check_identity(record):
    keys(record, ('path', 'bytes', 'sha256'))
    checked_sha(record['sha256'])
    if type(record['bytes']) is not int or identity(record['path']) != record:
        raise Refusal('input/source file identity changed')


def load_driver(expected):
    if sha(read(DRIVER)) != checked_sha(expected): raise Refusal('fixed native driver changed')
    spec = importlib.util.spec_from_file_location('_wu088_native_dispatch_driver', DRIVER)
    d = importlib.util.module_from_spec(spec)
    prior = sys.dont_write_bytecode; sys.dont_write_bytecode = True
    try: spec.loader.exec_module(d)
    finally: sys.dont_write_bytecode = prior
    return d


def authority(manifest):
    keys(manifest, ('schema', 'scope', 'driver_sha256', 'driver_source', 'files',
                    'plan_sha256', 'build_sha256', 'native_limits', 'output_root', 'tasks',
                    'core_worker_sha256', 'existing_output_policy'))
    if manifest['schema'] != SCHEMA or manifest['scope'] != 'CONDITIONAL_NATIVE_COMPACT_INTERIOR':
        raise Refusal('native manifest scope/schema required')
    if manifest['existing_output_policy'] != 'REFUSE': raise Refusal('output reuse is not supported')
    if sha(read(HERE / 'worker.py')) != checked_sha(manifest['core_worker_sha256']):
        raise Refusal('core worker changed')
    files = manifest['files']; keys(files, ('input_npz', 'plan', 'build', 'limits', 'binary', 'backend_provenance'))
    for item in files.values(): check_identity(item)
    tasks = manifest['tasks']
    if type(tasks) is not list or not 1 <= len(tasks) <= 2592: raise Refusal('1..2592 selected tasks required')
    seen = set()
    for ordinal, task in enumerate(tasks):
        keys(task, ('ordinal', 'native_index', 'task_sha256'))
        i = task['native_index']
        if type(i) is not int or not 0 <= i < 2592 or i in seen:
            raise Refusal('unique strict native2592 indices required')
        if type(task['ordinal']) is not int or task['ordinal'] != ordinal: raise Refusal('ordinal mismatch')
        checked_sha(task['task_sha256']); seen.add(i)
    d = load_driver(manifest['driver_sha256'])
    if d.source_identity() != manifest['driver_source']: raise Refusal('native dependency source changed')
    limits = d.limits_checked(manifest['native_limits'])
    if parse(read(files['limits']['path'])) != limits: raise Refusal('limits identity mismatch')
    plan = parse(read(files['plan']['path'])); build = parse(read(files['build']['path']))
    if plan.get('plan_sha256') != checked_sha(manifest['plan_sha256']): raise Refusal('external plan identity mismatch')
    if (build.get('manifest_sha256') != checked_sha(manifest['build_sha256']) or
            sha(canonical({k:v for k,v in build.items() if k != 'manifest_sha256'})) != manifest['build_sha256']):
        raise Refusal('external build identity mismatch')
    adapter, _ = d.dependencies(); raw = read(files['input_npz']['path'])
    record = adapter.decode_npz(raw, expected_archive_sha256=adapter.FROZEN107_ARCHIVE_SHA256, scope='FROZEN107_PINNED')
    planner = d.module('_wu088_native_dispatch_plan', d.PLAN_MODULE)
    planner.validate_plan(plan, source_archive_bytes=raw)
    if plan['scope'] != 'FROZEN107_PINNED' or build['schema'] != 'WU088_NATIVE_DRIVER_BUILD_V1':
        raise Refusal('fixed input/build schema required')
    if build['source'] != manifest['driver_source']: raise Refusal('build native source mismatch')
    for k, expected in [('archive_sha256', record['archive_sha256']), ('input_record_sha256', record['canonical_record_sha256'])]:
        if build[k] != expected or plan[k] != expected: raise Refusal('mixed native input')
    configuration = d.build_configuration(build['callback_mode'])
    if build['callback_mode_flags'] != configuration['mode_flags'] or build['callback_sources'] != configuration['sources'] or build['flags'] != d.FLAGS:
        raise Refusal('native build configuration mismatch')
    build_dir = path_checked(files['build']['path']).parent
    if files['binary']['path'] != str(build_dir / 'primitive_worker') or files['binary']['sha256'] != build['binary_sha256']:
        raise Refusal('fixed primitive binary mismatch')
    if files['backend_provenance']['path'] != build['backend_provenance'] or files['backend_provenance']['sha256'] != build['backend_provenance_sha256']:
        raise Refusal('backend provenance mismatch')
    for task in tasks:
        p = plan['tasks'][task['native_index']]
        if p['index'] != task['native_index'] or p['task_sha256'] != task['task_sha256']:
            raise Refusal('selected native task identity mismatch')
    output = path_checked(manifest['output_root'])
    if not output.is_dir(): raise Refusal('existing output directory required')
    return d, plan, build, limits


def load_manifest(path, expected):
    raw = read(path)
    if sha(raw) != checked_sha(expected): raise Refusal('external manifest byte identity mismatch')
    m = parse(raw)
    return m, authority(m)


def validate_envelope(result, manifest, ordinal, context):
    if type(ordinal) is not int or not 0 <= ordinal < len(manifest['tasks']):
        raise Refusal('ordinal outside selected task list')
    d, plan, build, limits = context
    task = manifest['tasks'][ordinal]; native_task = plan['tasks'][task['native_index']]
    if type(result) is not dict or 'wrapper' not in result or 'result_sha256' not in result:
        raise Refusal('native envelope required')
    if sha(canonical({k:v for k,v in result.items() if k != 'result_sha256'})) != checked_sha(result['result_sha256']):
        raise Refusal('native envelope identity mismatch')
    d.validate_result({k:v for k,v in result.items() if k not in ('wrapper', 'result_sha256')},
                      plan=plan, task=native_task, manifest=build, limits=limits)
    expected = {'schema':'WU088_NATIVE_INTERIOR_WRAPPER_V1', 'build_manifest_sha256':manifest['build_sha256'],
        'native_limits':limits, 'native_execution_observed':True, 'scope':'CONDITIONAL_COMPACT_INTERIOR_ONLY',
        'endpoint_plan_module_sha256':sha(read(d.PLAN_MODULE)), 'historical_abi_admission':False,
        'independent_scientific_review':False, 'evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
        'validation_level':'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY'}
    wrapper = result['wrapper']; keys(wrapper, (*expected, 'command', 'native_stdout_sha256'))
    d.limits_checked(wrapper['native_limits'])
    for k, v in expected.items():
        if type(wrapper[k]) is not type(v) or wrapper[k] != v: raise Refusal('native wrapper binding mismatch: ' + k)
    checked_sha(wrapper['native_stdout_sha256'])
    command = [manifest['files']['binary']['path'], str(task['native_index']),
        *[plan['window'][k] for k in ('l_t', 'T_t', 'l_u', 'T_u')],
        *[str(limits[k]) for k in ('precision_bits', 'radius_exp', 'relative_goal', 'max_evaluations',
            'max_integration_calls', 'wall_seconds', 'queued_panels', 'degree_limit')],
        task['task_sha256'], manifest['plan_sha256']]
    if wrapper['command'] != command: raise Refusal('native command/task/caps binding mismatch')
    return result


def run(path, ordinal, expected_manifest_sha256):
    if os.getuid() == 0: raise Refusal('nonroot execution required; no MPI root bypass')
    m, context = load_manifest(path, expected_manifest_sha256)
    if type(ordinal) is not int or not 0 <= ordinal < len(m['tasks']): raise Refusal('ordinal outside selected task list')
    task = m['tasks'][ordinal]
    out = Path(m['output_root']) / ('primitive_%04d.json' % task['native_index'])
    if os.path.lexists(out) or os.path.lexists(str(out) + '.claim'):
        raise Refusal('existing output/claim refused; no automatic reuse or rerun')
    d, _, _, limits = context
    d.run_task(m['files']['input_npz']['path'], m['files']['plan']['path'], m['plan_sha256'],
               task['native_index'], str(Path(m['files']['build']['path']).parent), m['build_sha256'], limits, out)
    # Recheck input/source bindings after the backend returns, then read durable output.
    m2, context2 = load_manifest(path, expected_manifest_sha256)
    result = validate_envelope(parse(read(out)), m2, ordinal, context2)
    return {'status':'CONDITIONAL_NATIVE_INTERIOR_RECORDED', 'ordinal':ordinal, 'native_index':task['native_index'],
            'output':identity(out), 'result_sha256':result['result_sha256'], 'scientific_admission':False,
            'production_admission':False, 'MPI_runtime_admitted':False}


def main(expected_manifest_sha256=None, expected_manifest_path=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True); p.add_argument('--task-index', type=int, required=True)
    a = p.parse_args()
    try:
        if expected_manifest_path is None or a.manifest != expected_manifest_path:
            raise Refusal('use the separately pinned generated bound_worker.py')
        result = run(a.manifest, a.task_index, expected_manifest_sha256)
        print(json.dumps(result, sort_keys=True)); return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('NATIVE_DISPATCH_REFUSED: ' + str(exc), file=sys.stderr); return 2


if __name__ == '__main__': raise SystemExit(main())
