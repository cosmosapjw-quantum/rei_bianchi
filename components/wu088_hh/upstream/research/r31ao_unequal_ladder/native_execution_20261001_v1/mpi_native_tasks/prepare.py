"""Create-only task selection for the fixed native primitive API, not an MPI launch."""
import argparse
import json
from pathlib import Path
import sys
import worker as w


def prepare(input_npz, plan_path, plan_sha256, build_dir, build_sha256, limits_path, indices, output):
    if type(indices) is not list or not 1 <= len(indices) <= 2592 or any(type(i) is not int or not 0 <= i < 2592 for i in indices) or len(set(indices)) != len(indices):
        raise w.Refusal('unique strict native2592 indices required')
    output = w.path_checked(output, existing=False)
    if output.exists() or not output.parent.is_dir(): raise w.Refusal('new bundle under an existing parent required')
    d = w.load_driver(w.sha(w.read(w.DRIVER)))
    build_path = w.path_checked(build_dir) / 'BUILD.json'
    plan = w.parse(w.read(plan_path)); build = w.parse(w.read(build_path))
    limits = d.limits_checked(w.parse(w.read(limits_path)))
    m = {'schema':w.SCHEMA, 'scope':'CONDITIONAL_NATIVE_COMPACT_INTERIOR',
        'driver_sha256':w.sha(w.read(w.DRIVER)), 'driver_source':d.source_identity(),
        'files':{k:w.identity(v) for k,v in {
            'input_npz':input_npz, 'plan':plan_path, 'build':build_path, 'limits':limits_path,
            'binary':build_path.parent/'primitive_worker', 'backend_provenance':build['backend_provenance']}.items()},
        'plan_sha256':w.checked_sha(plan_sha256), 'build_sha256':w.checked_sha(build_sha256),
        'native_limits':limits, 'output_root':str(output/'results'),
        'tasks':[{'ordinal':n, 'native_index':i, 'task_sha256':plan['tasks'][i]['task_sha256']} for n,i in enumerate(indices)],
        'core_worker_sha256':w.sha(w.read(w.HERE/'worker.py')), 'existing_output_policy':'REFUSE'}
    # No old output is overwritten. Failed preparation is left for inspection.
    output.mkdir(mode=0o700); (output/'results').mkdir(mode=0o700)
    w.authority(m)
    data = w.canonical(m) + b'\n'; manifest = output/'MANIFEST.json'
    with manifest.open('xb') as f: f.write(data)
    worklist = ('%d\n' % len(indices)) + ''.join('%d %d\n' % (i, limits['wall_seconds']+10) for i in range(len(indices)))
    with (output/'WORKLIST.txt').open('x') as f: f.write(worklist)
    # The launcher must independently pin this file. Its literal manifest SHA is
    # the external trust anchor, not a digest supplied by the manifest itself.
    bound = f'''"""Generated fixed-manifest worker; no arbitrary command arguments."""
import hashlib, importlib.util, pathlib, sys
sys.dont_write_bytecode = True
p = pathlib.Path({str(w.HERE/'worker.py')!r})
if hashlib.sha256(p.read_bytes()).hexdigest() != {m['core_worker_sha256']!r}:
    raise SystemExit('CORE_WORKER_CHANGED')
spec = importlib.util.spec_from_file_location('_bound_native_worker', p)
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
raise SystemExit(worker.main({w.sha(data)!r}, {str(manifest)!r}))
'''
    with (output/'bound_worker.py').open('x') as f: f.write(bound)
    result = {'schema':'WU088_NATIVE_DISPATCH_PREPARATION_V1', 'status':'PREPARED_NOT_EXECUTED',
        'manifest':w.identity(manifest), 'worklist':w.identity(output/'WORKLIST.txt'),
        'bound_worker':w.identity(output/'bound_worker.py'), 'selected_native_indices':indices,
        'old_synthetic_launcher_compatible':False, 'native_MPI_guard_implemented':False,
        'scientific_admission':False, 'production_admission':False}
    with (output/'PREPARATION.json').open('xb') as f: f.write(w.canonical(result)+b'\n')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('input-npz','plan','plan-sha256','build-directory','build-sha256','limits-json','output-directory'):
        p.add_argument('--'+name, required=True)
    p.add_argument('--native-indices', required=True, type=int, nargs='+')
    a = p.parse_args()
    try:
        r = prepare(a.input_npz,a.plan,a.plan_sha256,a.build_directory,a.build_sha256,a.limits_json,a.native_indices,a.output_directory)
        print(json.dumps(r,sort_keys=True)); return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('NATIVE_DISPATCH_PREPARATION_REFUSED: '+str(exc),file=sys.stderr); return 2


if __name__ == '__main__': raise SystemExit(main())
