#!/usr/bin/env python3
"""Create a private HPC child without evaluating any numerical map.

Historical JSON is never rewritten. The caller supplies its restored repository
explicitly; relative historical dependencies resolve there. Structural byte and
transaction checks inherit completed scientific checks instead of replaying them.
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
Q1B = HERE.parent
REPO = Q1B.parents[2]
REL = Q1B.relative_to(REPO)
sys.path.insert(0, str(Q1B / 'c11/integration/production'))
sys.path.insert(0, str(Q1B / 'c13/allocation'))
from production_journal import AttemptJournal, durable_json, reconcile_output_records, validate_cursor
from prepare_runtime_allocation import allocation_controls, committed_head, canonical_sha

SCHEMA = 'rei.hpc.runtime_allocation.v1'
HPC_FILES = ('prepare_hpc_run.py', 'run_hpc_chunk.py', 'ordered_cell_pool.py',
             'native_step_hpc.py', 'segmented_checkpoint.py', 'resource_plan.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def resolve_historical(path, repo):
    """Resolve portable paths, including old absolute paths rooted at research/.

    Absolute historical workstation prefixes are provenance, not authority to
    open arbitrary paths. A matching research suffix is resolved in repo only.
    """
    repo = Path(repo).resolve(strict=True)
    value = Path(path)
    if value.is_absolute():
        if value.is_relative_to(repo):
            value = value.relative_to(repo)
        else:
            require('research' in value.parts, 'UNRESOLVABLE_HISTORICAL_ABSOLUTE_PATH')
            value = Path(*value.parts[value.parts.index('research'):])
    require('..' not in value.parts, 'HISTORICAL_PATH_TRAVERSAL')
    result = (repo / value).resolve(strict=True)
    require(result.is_relative_to(repo), 'HISTORICAL_PATH_OUTSIDE_PARENT_REPO')
    return result


def verify_closure(mapping, repo):
    require(isinstance(mapping, dict) and mapping, 'EMPTY_FROZEN_DEPENDENCY_CLOSURE')
    for key, expected in mapping.items():
        require(key.startswith('dependency:'), 'DEPENDENCY_KEY')
        path = resolve_historical(key.removeprefix('dependency:'), repo)
        require(sha(path) == expected, 'FROZEN_DEPENDENCY_DRIFT:' + key)


def read_legacy_checkpoint(directory, reference, identity):
    """Integrity-only restore; no completed domain/ledger calculation is repeated."""
    import numpy as np
    path = Path(directory) / f'gen-{reference["generation"]:08d}'
    require(path.is_dir() and not path.is_symlink(), 'LEGACY_CHECKPOINT_DIRECTORY')
    require(sha(path / 'manifest.json') == reference['manifest_sha256'], 'PARENT_MANIFEST_HASH')
    manifest = json.loads((path / 'manifest.json').read_text())
    require(manifest['generation'] == reference['generation'] and
            set(manifest['files']) == {'arrays.npz', 'metadata.json', 'identity.json'}, 'PARENT_MANIFEST_SCHEMA')
    require({p.name for p in path.iterdir()} == set(manifest['files']) | {'manifest.json'},
            'TORN_OR_UNEXPECTED_PARENT_CHECKPOINT')
    for name, record in manifest['files'].items():
        member = path / name
        require(member.is_file() and not member.is_symlink() and
                member.stat().st_size == record['bytes'] and sha(member) == record['sha256'],
                'PARENT_MEMBER_HASH:' + name)
    actual = json.loads((path / 'identity.json').read_text())
    require(actual == identity, 'PARENT_IDENTITY')
    metadata = json.loads((path / 'metadata.json').read_text())
    with np.load(path / 'arrays.npz', allow_pickle=False) as saved:
        arrays = {key: saved[key].copy() for key in saved.files}
    cursor = metadata['adaptive_cursor']
    validate_cursor(cursor)
    require(len(arrays['prefix_clock']) == cursor['accepted_boundaries'] + 1 and
            float(arrays['prefix_clock'][-1]) == cursor['accepted_clock_s'] and
            arrays['state'].tobytes() == arrays['prefix_state'][-1].tobytes(), 'PARENT_PREFIX_STRUCTURE')
    require(canonical_sha(metadata['restart_binding']) == metadata['restart_binding_sha256'] == identity['control'],
            'PARENT_RESTART_BINDING_IDENTITY')
    return dict(arrays=arrays, metadata=metadata, identity=actual, manifest=manifest,
                current_validation={'scope': 'INHERITED_SCIENTIFIC_CHECKS_BYTE_INTEGRITY_ONLY',
                                    'scientific_checks_replayed': 0})


def inspect_private_parent(parent_repo, parent_root):
    repo = Path(parent_repo).resolve(strict=True)
    parent = resolve_historical(parent_root, repo)
    bundle = json.loads((parent / 'TRANSITION_RESULT.json').read_text())
    seed = dict(generation=bundle['generation'], manifest_sha256=bundle['manifest_sha256'])
    head, journals = committed_head(parent / 'RUN/JOURNAL', bundle['cursor'], seed)
    checkpoint = head['checkpoint']
    for path in (parent / 'CHECKPOINTS').glob('gen-*'):
        require(path.is_dir() and int(path.name[4:]) <= checkpoint['generation'], 'UNCOMMITTED_PARENT_CHECKPOINT')
    require(not list((parent / 'CHECKPOINTS').glob('.tmp-*')), 'INCOMPLETE_PARENT_CHECKPOINT')
    loaded = read_legacy_checkpoint(parent / 'CHECKPOINTS', checkpoint, bundle['identity'])
    metadata = loaded['metadata']
    require(metadata['adaptive_cursor'] == head['cursor'], 'UNSAVED_PARENT_REJECTION_TAIL')
    binding = metadata['restart_binding']
    require(binding['controls'] == bundle['controls'] and binding['dependency_closure'] == bundle['dependency_closure'],
            'PARENT_BUNDLE_BINDING')
    verify_closure(binding['dependency_closure'], repo)
    schedule = json.loads((parent / 'SCHEDULE.json').read_text())
    require(binding['end_time_s'] == schedule['target_time_s'] == bundle['target_time_s'] and
            binding['hard_events_s'] == schedule['hard_events_s'], 'PARENT_TARGET_SCHEDULE')
    require(head['cursor']['accepted_clock_s'] < bundle['target_time_s'], 'PARENT_TARGET_ALREADY_REACHED')
    for row in metadata['production_output_records']:
        require(row['time_s'] == schedule['output_epochs_s'][row['epoch_index']], 'PARENT_OUTPUT_EPOCH')
        require(json.loads((parent / 'RUN/OUTPUT24' / f'epoch-{row["epoch_index"]:03d}.json').read_text()) == row,
                'PARENT_OUTPUT_CONTENT')
    for failure in bundle['allocation']['failed_lanes']:
        lane = repo / REL / 'c12/evidence' / failure['run'] / 'RUN/JOURNAL'
        require(not (lane / f'attempt-{failure["attempt"]:08d}.commit.json').exists(), 'PRIOR_FAILURE_MUTATED')
        for kind in ('begin', 'failure'):
            path = lane / f'attempt-{failure["attempt"]:08d}.{kind}.json'
            require(binding['dependency_closure'].get('dependency:' + str(path.relative_to(repo))) == sha(path),
                    'PRIOR_FAILURE_DEBIT_EVIDENCE')
    return dict(repo=repo, parent=parent, bundle=bundle, checkpoint=checkpoint, cursor=head['cursor'],
                loaded=loaded, schedule=schedule, journal_paths=journals)


def validate_runtime_config(config):
    require(set(config) == {'schema', 'cell_workers', 'worker_timeout_s', 'native_thread_count',
                           'map_execution', 'closure_verification', 'checkpoint_format',
                           'resource_estimates'}, 'HPC_CONFIG_FIELDS')
    require(config['schema'] == 'rei.hpc.runtime_config.v1' and type(config['cell_workers']) is int and
            1 <= config['cell_workers'] <= 48 and math.isfinite(config['worker_timeout_s']) and
            config['worker_timeout_s'] > 0, 'HPC_WORKER_CONFIG')
    require(config['native_thread_count'] == 1 and config['map_execution'] == 'SERIAL_ORIGINAL_THREE_MAP_CONTROLLER' and
            config['closure_verification'] == 'STARTUP_AND_EXIT_SINGLE_OWNER_IMMUTABLE_INPUTS' and
            config['checkpoint_format'] == 'IMMUTABLE_SEED_PLUS_ACCEPTED_PAIRS', 'HPC_CONFIG_CONTRACT')
    resource = config['resource_estimates']
    require(set(resource) == {'coordinator_gib', 'worker_gib', 'reserve_gib', 'reserve_cores',
                              'memory_estimates_measured'}, 'HPC_RESOURCE_FIELDS')
    require(type(resource['reserve_cores']) is int and resource['reserve_cores'] >= 0 and
            resource['memory_estimates_measured'] is False, 'HPC_RESOURCE_ESTIMATE_CONTRACT')
    require(all(type(resource[key]) in (int, float) and math.isfinite(resource[key]) and resource[key] > 0
                for key in ('coordinator_gib', 'worker_gib', 'reserve_gib')), 'HPC_MEMORY_ESTIMATE_DOMAIN')


def check_resources(config, *, affinity_cpus=None, available_bytes=None):
    """Fail closed if the pinned worker count does not fit; never resize it.

    The optional observations support manufactured tests. Runtime callers use
    live affinity and host/cgroup available memory on every chunk startup.
    """
    from resource_plan import plan, memory_limit_bytes
    validate_runtime_config(config)
    if affinity_cpus is None:
        affinity_cpus = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count()
    if available_bytes is None:
        available_bytes = memory_limit_bytes()
    estimates = config['resource_estimates']
    result = plan(affinity_cpus=affinity_cpus, available_bytes=available_bytes,
                  requested_workers=config['cell_workers'], reserve_cores=estimates['reserve_cores'],
                  coordinator_gib=estimates['coordinator_gib'], worker_gib=estimates['worker_gib'],
                  reserve_gib=estimates['reserve_gib'])
    require(result['workers'] == config['cell_workers'],
            'HPC_CONFIG_EXCEEDS_RESOURCE_PLAN:' + json.dumps(result, sort_keys=True))
    return result


def execution_pins(frozen):
    """Pin every executable historical leaf available in this checkout, plus HPC."""
    pins = {}
    for key, digest in frozen.items():
        relative = Path(key.removeprefix('dependency:'))
        if relative.is_absolute() or '..' in relative.parts:
            continue
        candidate = REPO / relative
        if candidate.is_file() and candidate.suffix in ('.py', '.json', '.rs', '.out'):
            require(sha(candidate) == digest, 'PUBLIC_FROZEN_LEAF_DRIFT:' + str(relative))
            pins[str(relative)] = digest
    for name in HPC_FILES:
        path = HERE / name
        pins[str(path.relative_to(REPO))] = sha(path)
    return pins


def verify_runtime_bundle(bundle):
    require(bundle.get('schema') == SCHEMA, 'HPC_BUNDLE_SCHEMA')
    validate_cursor(bundle['cursor'])
    validate_runtime_config(bundle['runtime_config'])
    require(canonical_sha(bundle['runtime_binding']) == bundle['runtime_binding_sha256'], 'HPC_BINDING_HASH')
    binding = bundle['runtime_binding']
    for key in ('controls', 'allocation', 'runtime_config', 'frozen_dependency_closure', 'execution_pins',
                'target_time_s', 'schedule', 'parent_checkpoint', 'cursor', 'private_pins',
                'parent_identity', 'source_module_path', 'absorption_module_path', 'absorption_sha256', 'shape'):
        require(binding[key] == bundle[key], 'HPC_BINDING_FIELD:' + key)
    allocation, controls, cursor = bundle['allocation'], bundle['controls'], bundle['cursor']
    require(controls['max_attempts'] == allocation['child_completed_attempt_cap'] and
            controls['max_attempts'] + allocation['external_failed_attempt_debit'] == allocation['all_physical_attempt_cap'] and
            controls['max_accepted_macros'] == allocation['child_accepted_macro_cap'] and
            allocation['parent_completed_attempts'] == cursor['attempts'] and allocation['counters_reset'] is False,
            'HPC_CUMULATIVE_ALLOCATION')
    require(bundle['seed_checkpoint']['generation'] == cursor['accepted_macros'], 'HPC_SEED_GENERATION')


def verify_runtime_inputs(bundle):
    verify_runtime_bundle(bundle)
    verify_closure(bundle['frozen_dependency_closure'], bundle['parent_repo'])
    for relative, digest in bundle['execution_pins'].items():
        require(sha(resolve_historical(relative, REPO)) == digest, 'EXECUTED_LEAF_DRIFT:' + relative)
    for name in HPC_FILES:
        relative = str((HERE / name).relative_to(REPO))
        require(bundle['execution_pins'].get(relative) == sha(HERE / name), 'UNPINNED_HPC_LEAF:' + name)
    for path, digest in bundle['private_pins'].items():
        require(sha(resolve_historical(path, bundle['parent_repo'])) == digest, 'PRIVATE_PARENT_PIN_DRIFT:' + path)


def prepare(parent_repo, parent_root, work_root, *, additional_attempts=10000, cell_workers=8, worker_timeout_s=120.,
            coordinator_gib=8., worker_gib=1., reserve_gib=8., reserve_cores=2):
    import numpy as np
    from segmented_checkpoint import SegmentedStore
    parent = resolve_historical(parent_root, parent_repo)
    # Restore packages may omit this zero-byte administrative lock. Creating it
    # does not replace parent evidence; it preserves the original writer lock.
    with (parent / 'RUN/RUN.lock').open('a+b') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('PARENT_WRITER_RUNNING') from None
        old = inspect_private_parent(parent_repo, parent_root)
        config = dict(schema='rei.hpc.runtime_config.v1', cell_workers=cell_workers,
                      worker_timeout_s=float(worker_timeout_s), native_thread_count=1,
                      map_execution='SERIAL_ORIGINAL_THREE_MAP_CONTROLLER',
                      closure_verification='STARTUP_AND_EXIT_SINGLE_OWNER_IMMUTABLE_INPUTS',
                      checkpoint_format='IMMUTABLE_SEED_PLUS_ACCEPTED_PAIRS',
                      resource_estimates=dict(coordinator_gib=coordinator_gib, worker_gib=worker_gib,
                                              reserve_gib=reserve_gib, reserve_cores=reserve_cores,
                                              memory_estimates_measured=False))
        validate_runtime_config(config)
        resource_observation = check_resources(config)
        controls, allocation = allocation_controls(old['bundle']['controls'], old['cursor'],
                                                  old['bundle']['allocation'], additional_attempts)
        frozen = copy.deepcopy(old['bundle']['dependency_closure'])
        pins = execution_pins(frozen)
        input_path = old['repo'] / REL / 'evidence/SOURCE_C2.npz'
        with np.load(input_path, allow_pickle=False) as saved:
            shape = saved['initial_N'].shape
        private_files = [old['parent'] / 'TRANSITION_RESULT.json', old['parent'] / 'SCHEDULE.json',
                         input_path, *old['journal_paths']]
        private_files += list((old['parent'] / 'CHECKPOINTS' / f'gen-{old["checkpoint"]["generation"]:08d}').iterdir())
        private_pins = {str(p.relative_to(old['repo'])): sha(p) for p in private_files}
        binding = dict(schema='rei.hpc.bound_execution.v1', controls=controls, allocation=allocation,
                       runtime_config=config, frozen_dependency_closure=frozen, execution_pins=pins,
                       parent_checkpoint=old['checkpoint'], cursor=old['cursor'],
                       target_time_s=old['bundle']['target_time_s'], schedule=old['schedule'],
                       private_pins=private_pins, parent_identity=old['bundle']['identity'], shape=list(shape),
                       source_module_path=old['bundle']['source_module_path'],
                       absorption_module_path=old['bundle']['absorption_module_path'],
                       absorption_sha256=old['bundle']['absorption_sha256'])
        out = Path(work_root).resolve()
        require(not out.exists(), 'CREATE_ONLY_NEW_HPC_WORK_ROOT_REQUIRED')
        out.mkdir(parents=True, exist_ok=False)
        meta = out / 'HPCMETA'
        durable_json(meta / 'RUNTIME_CONFIG.json', config)
        durable_json(meta / 'PREPARATION_RESOURCE_PLAN.json', resource_observation)
        durable_json(meta / 'CONTROLS.json', controls)
        durable_json(meta / 'SCHEDULE.json', old['schedule'])
        store = SegmentedStore(out / 'CHECKPOINTS')
        seed = store.initialize(old['parent'] / 'CHECKPOINTS', old['checkpoint'], old['loaded'],
                                shape=shape, runtime_binding=binding)
        bundle = dict(schema=SCHEMA, parent_repo=str(old['repo']), parent_root=str(old['parent']),
                      work_root=str(out), checkpoint_directory=str(out / 'CHECKPOINTS'),
                      runtime_binding=binding, runtime_binding_sha256=canonical_sha(binding),
                      seed_checkpoint=seed,
                      scientific_admission=False, speedup_claim=None, completed_scientific_checks_replayed=0,
                      **{key: copy.deepcopy(value) for key, value in binding.items() if key != 'schema'})
        verify_runtime_bundle(bundle)
        output = old['loaded']['metadata']['production_output_records']
        reconcile_output_records(out / 'RUN/OUTPUT24', output)
        durable_json(out / 'RUN/INITIAL_OUTPUT_DONE.json',
                     json.loads((old['parent'] / 'RUN/INITIAL_OUTPUT_DONE.json').read_text()))
        AttemptJournal(out / 'RUN/JOURNAL', old['cursor'], seed)
        durable_json(meta / 'TRANSITION_RESULT.json', bundle)
        return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent-repo', type=Path, required=True)
    parser.add_argument('--parent-root', type=Path, required=True)
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--additional-attempts', type=int, default=10000)
    parser.add_argument('--cell-workers', type=int, default=8)
    parser.add_argument('--worker-timeout-s', type=float, default=120.)
    parser.add_argument('--coordinator-gib', type=float, default=8.)
    parser.add_argument('--worker-gib', type=float, default=1.)
    parser.add_argument('--reserve-gib', type=float, default=8.)
    parser.add_argument('--reserve-cores', type=int, default=2)
    args = parser.parse_args()
    result = prepare(**vars(args))
    print(json.dumps(dict(status='PREPARED_NO_NATIVE_CALLS', transition_bundle=str(Path(result['work_root']) /
                     'HPCMETA/TRANSITION_RESULT.json'), cursor=result['cursor'], allocation=result['allocation'],
                     runtime_binding_sha256=result['runtime_binding_sha256'], native_calls=0), sort_keys=True))


if __name__ == '__main__':
    main()
