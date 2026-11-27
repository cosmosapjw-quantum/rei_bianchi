"""Pre-output authorization, immutable-source, binary and environment intake."""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNTIME = Path('/root/WU088_R31AL_Z075_RUNTIME_20260930')
ARCHIVE = Path('/root/WU088_R31Y_PRODUCER_INTAKE_20260929/WU088_HH_C21_TRANSFER_CP4_20260923.zip')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    with (HERE / name).open('x') as f:
        f.write(json.dumps(value, indent=2, allow_nan=False) + '\n')


def array_sha(arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.asarray(a, dtype='<c16', order='C').tobytes(order='C'))
    return h.hexdigest()


def main():
    al = REPO / 'research/r31al_z075_gate/ncp_followup_20260930'
    ak = REPO / 'research/r31ak_eight_node/ncp_followup_20260930'
    am = REPO / 'research/r31am_post_z075/ncp_followup_20260930'
    expected_envelope = {'schema': 'WU088_R31AL_Z075_MINIMAL_MIXED_AUTHORIZATION_V1', 'authorize': True,
        'action': 'AUTHORIZE_R31AL_Z075_MINIMAL_MIXED_NODE',
        'scope_sha256': '2f22f11f279b8d7f98efb2a4bff1fbfb79145f7f5010ce5081ca6ebfcc147357', 'one_shot': True}
    envelope = json.loads((HERE / 'USER_AUTHORIZATION.json').read_text())
    if envelope != expected_envelope or envelope['authorize'] is not True or envelope['one_shot'] is not True:
        raise RuntimeError('invalid affirmative authorization envelope')
    prelock = json.loads((al / 'Z075_REFINEMENT_PRE_OUTPUT_LOCK.json').read_text())
    frozen = {v['path']: v['sha256'] for v in prelock['locked_files'].values()}
    frozen.update({
        'research/r31al_z075_gate/ncp_followup_20260930/AUTHORIZATION_SCOPE_CANONICAL.json': expected_envelope['scope_sha256'],
        'research/r31al_z075_gate/ncp_followup_20260930/SECONDARY_REFINEMENT_PREREGISTRATION.json': '956bdbb6a4138f7f1117cbf98b47ce80d8c1cb76fcbf3401a76105cb4873612a',
        'research/r31al_z075_gate/ncp_followup_20260930/Z075_REFINEMENT_PRE_OUTPUT_LOCK.json': '93f895b7436ca4e4f82fb8a28d66acb2bd745fc39067571297292c62445b87c1',
        'research/r31am_post_z075/POST_Z075_DECISION_POLICY.json': 'b5253f441dd66bf6a2b7e313408083d434d97288e2f7b4754176dc7f3b7697fc',
        'research/r31am_post_z075/post_z075_policy.py': '36261b4fe71191827dd781b7f30f1e5578fa5884cda6b8a1abadc429d6aff42a',
        'research/r31am_post_z075/ncp_followup_20260930/POLICY_REPLAY.json': '7e9600dd89009711fe20d32e4455b4dc4d9473a0f3c862632bff36d6640d3b1b',
    })
    for rel, expected in frozen.items():
        if sha(REPO / rel) != expected:
            raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: ' + rel)
    scope = json.loads((al / 'AUTHORIZATION_SCOPE.json').read_text())
    canonical = json.dumps(scope, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    if canonical != (al / 'AUTHORIZATION_SCOPE_CANONICAL.json').read_bytes() or hashlib.sha256(canonical).hexdigest() != envelope['scope_sha256']:
        raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: canonical representation')
    with np.load(ak / 'FROZEN_HOLDOUT_PREDICTIONS.npz', allow_pickle=False) as f:
        for model, key in (('R31AK', 'R31AK_selected_prediction_arrays_sha256'), ('R31Z', 'R31Z_selected_prediction_arrays_sha256')):
            if array_sha([f[f'z0p75_{model}_{k}'] for k in ('O', 'dotO', 'Dcol', 'Drow', 'K')]) != scope[key]:
                raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: selected prediction arrays')
    with np.load(al / 'Z075_COARSE_PREDICTION.npz', allow_pickle=False) as f:
        if array_sha([f['z0p75_R31AD_' + k] for k in ('O', 'dotO', 'Dcol', 'Drow', 'K')]) != scope['R31AD_coarse_prediction_arrays_sha256']:
            raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: coarse arrays')
    prereg = json.loads((ak / 'NEXT_VALIDATION_PREREGISTRATION.json').read_text())
    components = prereg['R31AK_model_components']
    aggregate = hashlib.sha256(json.dumps(components, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    component_paths = {'engine_sha256': 'research/r31ad_five_node/unit_cell_model.py',
        'policy_sha256': 'research/r31ak_eight_node/MODEL_POLICY.json', 'helper_sha256': 'research/r31ak_eight_node/successor_policy.py',
        'eight_node_manifest_sha256': 'research/r31ak_eight_node/ncp_followup_20260930/EIGHT_NODE_INPUT_MANIFEST.json'}
    for key, rel in component_paths.items():
        if sha(REPO / rel) != components[key]:
            raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: model aggregate component')
        frozen[rel] = components[key]
    if aggregate != scope['R31AK_model_aggregate_sha256']:
        raise RuntimeError('AUTHORIZATION_SCOPE_DRIFT: model aggregate')
    adapter_path = REPO / 'research/r31ak_eight_node/metadata_adapter.py'
    spec = importlib.util.spec_from_file_location('preoutput_frozen_adapter', adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    if not adapter.identities_match(b'{"z":0.75,"n":192}', b'{"z":"0.75","n":192}', '0.75'):
        raise RuntimeError('frozen Decimal parser numerical/string mismatch')
    prior_lock = json.loads((REPO / 'research/r31aj_z25_validation/authorized_z25_20260930/PRE_OUTPUT_LOCK.json').read_text())
    producer = dict(prior_lock['producer_source_sha256'])
    if sha(ARCHIVE) != prior_lock['frozen_hashes']['archive']:
        raise RuntimeError('producer archive byte drift')
    with zipfile.ZipFile(ARCHIVE) as z:
        for rel, expected in producer.items():
            if sha(RUNTIME / rel) != expected or hashlib.sha256(z.read(rel)).hexdigest() != expected:
                raise RuntimeError('producer source drift: ' + rel)
        dependency_paths = [RUNTIME / 'completion/mixed_h/run.py', RUNTIME / 'completion/radial/radial_wide.cpp',
                            RUNTIME / 'completion/mixed_derivative/PILOT.json']
        for dirname in ('exact_weights', 'foreign_analytic', 'production/engineering'):
            dependency_paths += list((RUNTIME / dirname).rglob('*.py'))
        for path in sorted(set(dependency_paths)):
            rel = str(path.relative_to(RUNTIME))
            actual = sha(path)
            if hashlib.sha256(z.read(rel)).hexdigest() != actual:
                raise RuntimeError('archive dependency source drift: ' + rel)
            producer[rel] = actual
    for rel in ('completion/mixed_h/od/B192_z0.75', 'completion/mixed_derivative/B192_z0.75'):
        if (RUNTIME / rel).exists():
            raise RuntimeError('existing direct z0.75 output: no execution')
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1',
               PYTHONPYCACHEPREFIX='/tmp/wu088_z075_pycache_20260930')
    binary_info = {}
    probes = [('OD_NATIVE_PREP', RUNTIME / 'completion/mixed_h',
               'import json;from h0_backend import H0Fused;h=H0Fused();print(json.dumps({"identity":h.identity,"binary_path":h.lib._name}))'),
              ('JVP_NATIVE_PREP', RUNTIME / 'completion/mixed_derivative',
               'import json;from native import Native;n=Native();print(json.dumps({"identity":n.identity,"binary_path":str(n.folder/"analytic.so"),"build_manifest":n.manifest}))')]
    for label, cwd, code in probes:
        argv = [sys.executable, '-c', code]
        write(label + '.argv.json', argv)
        p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
        (HERE / (label + '.stdout')).write_text(p.stdout)
        (HERE / (label + '.stderr')).write_text(p.stderr)
        (HERE / (label + '.exit')).write_text(str(p.returncode) + '\n')
        if p.returncode:
            raise RuntimeError('native identity preparation failed: ' + label + ': ' + p.stderr)
        native = json.loads(p.stdout)
        native['binary_sha256'] = sha(native['binary_path'])
        binary_info[label] = native
        producer[str(Path(native['binary_path']).relative_to(RUNTIME))] = native['binary_sha256']
    if binary_info['OD_NATIVE_PREP']['identity'] != prior_lock['OD_native_identity'] or binary_info['JVP_NATIVE_PREP']['identity'] != prior_lock['JVP_native_identity']:
        raise RuntimeError('native source/binary identity differs from verified producer')
    with np.load(RUNTIME / 'inputs/extracted/WU088_HH_R10_FULL_MIXED_BLOCK_OHD_PARTIAL_20260922_v1/inputs/FROZEN_INPUTS.npz', allow_pickle=False) as f:
        velocity = np.longdouble(f['v'])
    tau = np.longdouble('0.75') / velocity
    if abs(float(tau) - float(scope['selected_time_ta'])) > 1e-14:
        raise RuntimeError('producer time contract drift')
    cpu_lines = Path('/proc/cpuinfo').read_text().splitlines()
    cpu_model = next(x.split(':', 1)[1].strip() for x in cpu_lines if x.startswith('model name'))
    compiler = subprocess.check_output(['g++', '--version'], text=True).splitlines()[0]
    write('ENVIRONMENT.json', {'python_executable': sys.executable, 'python_version': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
        'platform': platform.platform(), 'cpu_model': cpu_model, 'cpu_affinity': sorted(os.sched_getaffinity(0)), 'compiler_current': compiler,
        'precision': {'longdouble_itemsize': np.dtype(np.longdouble).itemsize, 'longdouble_significand_bits': np.finfo(np.longdouble).nmant + 1,
                      'clongdouble_itemsize': np.dtype(np.clongdouble).itemsize},
        'environment_overrides': {k: env[k] for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'PYTHONDONTWRITEBYTECODE', 'PYTHONPYCACHEPREFIX')},
        'runtime': str(RUNTIME), 'source_runtime_preserved': '/root/WU088_R31AJ_Z25_RUNTIME_20260930',
        'OD_flags': ['-O3', '-std=c++17', '-fPIC', '-shared', '-fno-fast-math', '-ffp-contract=off'],
        'JVP_build_manifest_flags': binary_info['JVP_NATIVE_PREP']['build_manifest']['identity']['flags'],
        'native_integral_calls_during_preparation': 0})
    baseline_path = Path('/root/WU088_R31AL_Z075_RUNTIME_BEFORE_20260930.json')
    with baseline_path.open('x') as f:
        json.dump(sorted(str(p.relative_to(RUNTIME)) for p in RUNTIME.rglob('*') if p.is_file()), f, indent=2)
        f.write('\n')
    remote_identity = json.loads((HERE / 'REMOTE_REVIEW.json').read_text())
    lock = {'schema': 'WU088_R31AL_Z075_AUTHORIZED_TRANSACTION_PRE_OUTPUT_LOCK_V1', 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'authorization': envelope, 'remote_before_execution': remote_identity,
        'frozen_files': frozen, 'R31AM_policy_sha256': frozen['research/r31am_post_z075/POST_Z075_DECISION_POLICY.json'],
        'producer_archive_sha256': sha(ARCHIVE), 'producer_source_sha256': producer, 'producer_binary_identity': binary_info,
        'execution_scripts_sha256': {n: sha(HERE / n) for n in ('run_transaction_once.py', 'compare_and_return_once.py', 'prepare_and_verify.py')},
        'runtime_file_baseline_path': str(baseline_path), 'runtime_file_baseline_sha256': sha(baseline_path),
        'tau_ta_producer_decimal': str(tau), 'velocity_producer_decimal': str(velocity),
        'source_contract': {'basis_order': 'CP4 B192 neutral rows centre0 24 then centre1 excited23; ionic columns2',
            'OD_source': 'completion/mixed_h/od_run.py:21-39; unchanged phase_E, tau=z/velocity, O/D only',
            'JVP_source': 'completion/mixed_derivative/run.py:17-31,50-53; independent analytic time derivative /t_a',
            'metadata_adapter': 'research/r31ak_eight_node/metadata_adapter.py; raw JSON Decimal numerical equality',
            'OD_internal_kernel_note': 'unchanged fused producer computes internal moment/T intermediates; no Hamiltonian matrix export'},
        'direct_output_accessed': False, 'science_commands_started': 0,
        'commands': {
            'OD': [sys.executable, 'completion/mixed_h/od_run.py', '--n', '192', '--z', '0.75', '--workers', '1'],
            'JVP': [sys.executable, 'completion/mixed_derivative/run.py', '--z', '0.75', '--n', '192'],
            'PRIMARY': [sys.executable, str(REPO / 'research/r31ak_eight_node/compare_future_holdout.py'), '--repo', str(REPO),
                '--od', str(HERE / 'OD_RAW/ASSEMBLED_OD.npz'), '--jvp', str(HERE / 'JVP_RAW/ASSEMBLED.npz'), '--out', str(HERE / 'PRIMARY_COMPARISON_RAW.json')],
            'SECONDARY': [sys.executable, str(REPO / 'research/r31al_z075_gate/compare_secondary_refinement.py'), '--repo', str(REPO),
                '--od', str(HERE / 'OD_RAW/ASSEMBLED_OD.npz'), '--jvp', str(HERE / 'JVP_RAW/ASSEMBLED.npz'),
                '--primary-result', str(HERE / 'PRIMARY_COMPARISON_RAW.json'), '--out', str(HERE / 'SECONDARY_REFINEMENT_COMPARISON.json')],
        }}
    write('PRE_OUTPUT_LOCK.json', lock)
    write('ONE_SHOT_LEDGER.json', {'schema': 'WU088_R31AL_Z075_ONE_SHOT_LEDGER_V1', 'one_shot_state': 'AUTHORIZED_PRE_OUTPUT',
        'pre_output_lock_sha256': sha(HERE / 'PRE_OUTPUT_LOCK.json'), 'authorization_scope_sha256': envelope['scope_sha256'],
        'authorization_consumed': False, 'science_commands_started': 0, 'science_node_count': 0})
    print(json.dumps({'status': 'AUTHORIZED_PREFLIGHT_PASSED', 'pre_output_lock_sha256': sha(HERE / 'PRE_OUTPUT_LOCK.json'),
                      'frozen_files_verified': len(frozen), 'producer_source_binary_files_verified': len(producer),
                      'tau_ta_producer_decimal': str(tau), 'science_commands_started': 0}, indent=2))


if __name__ == '__main__':
    main()
