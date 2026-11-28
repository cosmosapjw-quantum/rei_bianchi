"""Execute only the four already authorized frozen producer argv, once."""
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRE = REPO / 'research/r31ao_unequal_ladder/ncp_preflight_20260930'
RUNTIME = Path('/root/WU088_R31AL_Z075_RUNTIME_20260930')
STATE = Path('/root/WU088_R31AO_ORDER_STUDY_STATE_20260930.json')
GUARD = Path('/root/WU088_R31AO_ORDER_STUDY_ONESHOT_20260930.lock')
SCOPE_SHA = 'b0abd297847c17741b29a67fae02b9cfd5ddb3fbbe676163867675928cf54a4c'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def durable(path, obj):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    fd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def recheck():
    if sha(PRE / 'AUTHORIZATION_SCOPE_CANONICAL.json') != SCOPE_SHA:
        raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: canonical scope')
    scope = json.loads((PRE / 'ORDER_STUDY_SCOPE.json').read_text())
    canonical = json.dumps(scope, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    if canonical != (PRE / 'AUTHORIZATION_SCOPE_CANONICAL.json').read_bytes():
        raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: scope representation')
    for pin in json.loads((HERE / 'PRE_OUTPUT_VERIFICATION.json').read_text())['file_pins']:
        if sha(pin['path']) != pin['sha256']:
            raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: ' + pin['path'])
    return scope


def consume(folder, stage, state):
    if state['authorization_consumed']:
        return
    pairs = list(folder.glob('pair_*.npz'))
    if not pairs:
        return
    first = min(pairs, key=lambda p: p.stat().st_mtime_ns)
    identity = {'path': str(first), 'sha256': sha(first), 'bytes': first.stat().st_size,
                'stage': stage, 'output_mtime_ns': first.stat().st_mtime_ns,
                'observed_utc': now()}
    durable(HERE / 'FIRST_SCIENTIFIC_OUTPUT_IDENTITY.json', identity)
    state.update(authorization_consumed=True, first_scientific_output_identity=identity,
                 authorization_consumed_utc=now())
    durable(STATE, state)


def main():
    with GUARD.open('a') as guard:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = json.loads(STATE.read_text())
        if state['status'] != 'AUTHORIZED_PRE_OUTPUT' or state['producer_commands_started'] or state['authorization_consumed']:
            raise RuntimeError('Transaction already started or consumed; rerun forbidden')
        if state['wrapper_sha256'] != sha(__file__) or state['pre_output_verification_sha256'] != sha(HERE / 'PRE_OUTPUT_VERIFICATION.json'):
            raise RuntimeError('execution wrapper / pre-output verification drift')
        envelope = json.loads((HERE / 'ACTUAL_USER_AUTHORIZATION.json').read_text())
        if envelope != {'schema': 'WU088_R31AO_Z075_B128_B160_ORDER_STUDY_AUTHORIZATION_V1', 'authorize': True,
                        'action': 'AUTHORIZE_R31AO_Z075_B128_B160_ORDER_STUDY', 'scope_sha256': SCOPE_SHA, 'one_shot': True}:
            raise RuntimeError('authorization envelope drift')
        scope = recheck()
        for n in (128, 160):
            for rel in (f'completion/mixed_h/od/B{n}_z0.75', f'completion/mixed_derivative/B{n}_z0.75'):
                if (RUNTIME / rel).exists():
                    raise RuntimeError('pre-existing direct folder: ' + rel)
        env = dict(state['environment'], OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   PYTHONDONTWRITEBYTECODE='1', PYTHONPYCACHEPREFIX='/tmp/WU088_R31AO_ORDER_PYCACHE_20260930')
        durable(HERE / 'ACTUAL_STAGE_ENVIRONMENT.json', {'inherited_environment': state['environment'],
                'overrides': {k: env[k] for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'PYTHONDONTWRITEBYTECODE', 'PYTHONPYCACHEPREFIX')},
                'cwd': str(RUNTIME)})
        for command in scope['commands']:
            recheck()
            n, kind = command['n'], command['stage']
            stage = f'B{n}_{kind}'
            folder = RUNTIME / (f'completion/mixed_h/od/B{n}_z0.75' if kind == 'OD' else f'completion/mixed_derivative/B{n}_z0.75')
            if folder.exists():
                raise RuntimeError('Existing stage output; no overwrite: ' + str(folder))
            state.update(status='RUNNING_' + stage, current_stage=stage,
                         producer_commands_started=state['producer_commands_started'] + 1)
            entry = {'stage': stage, 'argv': command['argv'], 'cwd': str(RUNTIME), 'started_utc': now()}
            state['stages'].append(entry)
            durable(STATE, state)
            durable(HERE / (stage + '.argv.json'), command['argv'])
            start = time.monotonic()
            with (HERE / (stage + '.stdout')).open('xb') as stdout, (HERE / (stage + '.stderr')).open('xb') as stderr:
                proc = subprocess.Popen(command['argv'], cwd=RUNTIME, env=env, stdout=stdout, stderr=stderr)
                entry['pid'] = proc.pid
                durable(STATE, state)
                while proc.poll() is None:
                    consume(folder, stage, state)
                    time.sleep(0.10)
                code = proc.wait()
            consume(folder, stage, state)
            (HERE / (stage + '.exit')).write_text(str(code) + '\n')
            entry.update(exit_code=code, completed_utc=now(), wall_seconds=time.monotonic() - start)
            files = [{'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(folder.glob('*')) if p.is_file()]
            durable(HERE / (stage + '.RAW_CHECKPOINT_MANIFEST.json'), {'stage': stage, 'files': files})
            destination = HERE / 'raw' / stage
            destination.mkdir(parents=True, exist_ok=False)
            for pin in files:
                source = Path(pin['path'])
                shutil.copy2(source, destination / source.name)
                if sha(destination / source.name) != pin['sha256']:
                    raise RuntimeError('raw checkpoint copy byte drift')
            assembled = folder / ('ASSEMBLED_OD.npz' if kind == 'OD' else 'ASSEMBLED.npz')
            if code != 0 or not assembled.exists():
                raise RuntimeError(stage + ': partial failure; no automatic restart')
            identity = json.loads((folder / 'IDENTITY.json').read_text())
            result = json.loads((folder / 'RESULTS.json').read_text())
            if identity['n'] != n or result['sha256'] != sha(assembled):
                raise RuntimeError(stage + ': direct metadata/result identity mismatch')
            if kind == 'OD' and (result['Hamiltonian_included'] is not False or result['independent_dotO_included'] is not False):
                raise RuntimeError('OD export scope mismatch')
            if kind == 'JVP' and result['status'] != 'COMPUTED_INDEPENDENT_DERIVATIVE':
                raise RuntimeError('JVP contract mismatch')
            entry.update(assembled_path=str(assembled), assembled_sha256=sha(assembled), assembled_bytes=assembled.stat().st_size,
                         pair_checkpoint_count=len(list(folder.glob('pair_*.npz'))))
            if kind == 'JVP':
                state['new_order_nodes_completed'] += 1
            durable(STATE, state)
            print(json.dumps(entry), flush=True)
        state.update(status='CONSUMED_FOUR_STAGES_COMPLETE', completed_utc=now(), geometries=1)
        durable(STATE, state)
        durable(HERE / 'ONE_SHOT_LEDGER.json', state)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        if STATE.exists():
            state = json.loads(STATE.read_text())
            if state.get('producer_commands_started', 0) and state.get('status') != 'CONSUMED_FOUR_STAGES_COMPLETE':
                state.update(status='PARTIAL_FAILURE_NO_AUTOMATIC_RESTART', failure=str(exc), failed_utc=now())
                durable(STATE, state)
                durable(HERE / 'ONE_SHOT_LEDGER.json', state)
        raise
