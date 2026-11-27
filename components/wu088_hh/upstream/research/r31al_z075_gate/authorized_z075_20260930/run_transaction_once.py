"""One authorized geometry: unchanged OD followed by independent JVP producer."""
from __future__ import annotations

import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME = Path('/root/WU088_R31AL_Z075_RUNTIME_20260930')
LEDGER = HERE / 'ONE_SHOT_LEDGER.json'
GLOBAL_GUARD = Path('/root/WU088_R31AL_Z075_ONESHOT_STATE_20260930.lock')
STARTED_THIS_INVOCATION = False


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def durable(path, value):
    tmp = path.with_suffix('.json.tmp')
    with tmp.open('w') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def recheck(lock):
    for root, files in ((REPO, lock['frozen_files']), (RUNTIME, lock['producer_source_sha256'])):
        for rel, expected in files.items():
            if sha(root / rel) != expected:
                raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: ' + rel)
    for rel, expected in lock['execution_scripts_sha256'].items():
        if sha(HERE / rel) != expected:
            raise RuntimeError('execution wrapper drift: ' + rel)


def consume_if_output(folder, stage, ledger):
    if ledger['authorization_consumed']:
        return
    pairs = sorted(folder.glob('pair_*.npz')) if folder.exists() else []
    if pairs:
        first = pairs[0]
        identity = {'first_scientific_output_identity_utc': datetime.datetime.fromtimestamp(first.stat().st_mtime, datetime.timezone.utc).isoformat(),
                    'identity_observed_utc': now(), 'stage': stage,
                    'path': str(first), 'sha256': sha(first), 'bytes': first.stat().st_size}
        if (HERE / 'FIRST_OUTPUT_IDENTITY.json').exists():
            raise RuntimeError('existing first output identity')
        durable(HERE / 'FIRST_OUTPUT_IDENTITY.json', identity)
        ledger.update(authorization_consumed=True, science_node_count=1,
                      first_scientific_output_identity=identity,
                      one_shot_state='CONSUMED_' + stage + '_IN_PROGRESS')
        durable(LEDGER, ledger)


def main():
    global STARTED_THIS_INVOCATION
    with GLOBAL_GUARD.open('a') as guard:
        fcntl.flock(guard.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock = json.loads((HERE / 'PRE_OUTPUT_LOCK.json').read_text())
        ledger = json.loads(LEDGER.read_text())
        if ledger['one_shot_state'] != 'AUTHORIZED_PRE_OUTPUT' or ledger['science_commands_started'] != 0 or ledger['authorization_consumed']:
            raise RuntimeError('one-shot already started or consumed; rerun forbidden')
        if sha(HERE / 'PRE_OUTPUT_LOCK.json') != ledger['pre_output_lock_sha256']:
            raise RuntimeError('pre-output lock drift')
        recheck(lock)
        folders = {'OD': RUNTIME / 'completion/mixed_h/od/B192_z0.75',
                   'JVP': RUNTIME / 'completion/mixed_derivative/B192_z0.75'}
        if any(p.exists() for p in folders.values()):
            raise RuntimeError('pre-existing z0.75 direct output; refusing execution')
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX='/tmp/wu088_z075_pycache_20260930')
        for name in ('OD', 'JVP'):
            recheck(lock)
            argv = lock['commands'][name]
            STARTED_THIS_INVOCATION = True
            ledger.update(one_shot_state=name + '_IN_PROGRESS', current_stage=name,
                          current_stage_started_utc=now(), science_commands_started=ledger['science_commands_started'] + 1)
            durable(LEDGER, ledger)
            durable(HERE / (name + '.argv.json'), argv)
            with (HERE / (name + '.stdout')).open('x') as stdout, (HERE / (name + '.stderr')).open('x') as stderr:
                proc = subprocess.Popen(argv, cwd=RUNTIME, env=env, stdout=stdout, stderr=stderr)
                while proc.poll() is None:
                    consume_if_output(folders[name], name, ledger)
                    time.sleep(0.25)
                code = proc.wait()
            consume_if_output(folders[name], name, ledger)
            (HERE / (name + '.exit')).write_text(str(code) + '\n')
            ledger[name + '_exit'] = code
            ledger[name + '_completed_utc'] = now()
            assembled = folders[name] / ('ASSEMBLED_OD.npz' if name == 'OD' else 'ASSEMBLED.npz')
            if code or not assembled.exists():
                ledger.update(one_shot_state='PARTIAL_FAILURE_NO_AUTOMATIC_RERUN', failed_stage=name)
                durable(LEDGER, ledger)
                raise RuntimeError(name + ' partial failure; whole-node rerun forbidden')
            ident = json.loads(assembled.with_name('IDENTITY.json').read_text())
            report = json.loads(assembled.with_name('RESULTS.json').read_text())
            if ident.get('n') != 192 or report.get('sha256') != sha(assembled):
                raise RuntimeError(name + ' direct source identity mismatch')
            if name == 'OD' and (report.get('Hamiltonian_included') is not False or report.get('independent_dotO_included') is not False):
                raise RuntimeError('OD scope mismatch')
            ledger[name + '_assembled_identity'] = {'path': str(assembled), 'sha256': sha(assembled), 'bytes': assembled.stat().st_size}
            durable(LEDGER, ledger)
            print(json.dumps({'stage': name, 'exit': code, 'sha256': sha(assembled), 'authorization_consumed': ledger['authorization_consumed']}), flush=True)
        adapter_path = REPO / 'research/r31ak_eight_node/metadata_adapter.py'
        import importlib.util
        spec = importlib.util.spec_from_file_location('frozen_z075_adapter', adapter_path)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        if not adapter.identities_match((folders['OD'] / 'IDENTITY.json').read_bytes(), (folders['JVP'] / 'IDENTITY.json').read_bytes(), '0.75'):
            raise RuntimeError('direct Decimal geometry identity mismatch')
        ledger.update(one_shot_state='CONSUMED_OUTPUTS_COMPLETE', direct_geometry_identity_verified=True,
                      outputs_complete_utc=now(), science_node_count=1)
        durable(LEDGER, ledger)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        if STARTED_THIS_INVOCATION and LEDGER.exists():
            ledger = json.loads(LEDGER.read_text())
            if ledger.get('science_commands_started', 0) and ledger.get('one_shot_state') != 'CONSUMED_OUTPUTS_COMPLETE':
                ledger.update(one_shot_state='PARTIAL_FAILURE_NO_AUTOMATIC_RERUN', failure=str(exc), failed_utc=now())
                durable(LEDGER, ledger)
        raise
