"""Invoke frozen primary, then frozen secondary, then frozen R31AM policy once."""
from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np

from run_transaction_once import HERE, REPO, RUNTIME, LEDGER, GLOBAL_GUARD, durable, now, recheck, sha


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def comparison(label, argv, ledger):
    if ledger.get(label + '_started') or (HERE / (label + '.exit')).exists():
        raise RuntimeError('comparison already started; automatic repetition forbidden')
    ledger[label + '_started'] = now()
    durable(LEDGER, ledger)
    durable(HERE / (label + '.argv.json'), argv)
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1',
               PYTHONPYCACHEPREFIX='/tmp/wu088_z075_pycache_20260930')
    with (HERE / (label + '.stdout')).open('x') as stdout, (HERE / (label + '.stderr')).open('x') as stderr:
        proc = subprocess.run(argv, cwd=REPO, env=env, stdout=stdout, stderr=stderr)
    (HERE / (label + '.exit')).write_text(str(proc.returncode) + '\n')
    ledger[label + '_exit'] = proc.returncode
    durable(LEDGER, ledger)
    if proc.returncode:
        raise RuntimeError(label + ' comparator failure; no post-output repair or retry')


def main():
    with GLOBAL_GUARD.open('a') as guard:
        fcntl.flock(guard.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        ledger = json.loads(LEDGER.read_text())
        lock = json.loads((HERE / 'PRE_OUTPUT_LOCK.json').read_text())
        if ledger['one_shot_state'] != 'CONSUMED_OUTPUTS_COMPLETE' or not ledger['authorization_consumed']:
            raise RuntimeError('successful one-shot direct transaction required')
        if ledger.get('PRIMARY_started') or ledger.get('SECONDARY_started'):
            raise RuntimeError('comparisons already started; rerun forbidden')
        recheck(lock)
        adapter = module(REPO / 'research/r31ak_eight_node/metadata_adapter.py', 'z075_frozen_adapter')
        source_dirs = {'OD': RUNTIME / 'completion/mixed_h/od/B192_z0.75',
                       'JVP': RUNTIME / 'completion/mixed_derivative/B192_z0.75'}
        if not adapter.identities_match((source_dirs['OD'] / 'IDENTITY.json').read_bytes(),
                                        (source_dirs['JVP'] / 'IDENTITY.json').read_bytes(), '0.75'):
            raise RuntimeError('direct Decimal z identity mismatch before matrix access')
        raw_manifests = {}
        for stage, source in source_dirs.items():
            dest = HERE / (stage + '_RAW')
            if dest.exists():
                raise RuntimeError('existing evidence copy; refusing overwrite')
            shutil.copytree(source, dest)
            rows = []
            for original in sorted(source.rglob('*')):
                if original.is_file():
                    rel = original.relative_to(source)
                    copied = dest / rel
                    if sha(original) != sha(copied):
                        raise RuntimeError('raw evidence copy mismatch')
                    rows.append({'relative_path': str(rel), 'sha256': sha(copied), 'bytes': copied.stat().st_size})
            raw_manifests[stage] = {'runtime_path': str(source), 'evidence_copy_path': str(dest.relative_to(REPO)),
                                    'file_count': len(rows), 'pair_checkpoint_count': len(list(dest.glob('pair_*.npz'))),
                                    'all_file_bytes_match': True, 'files': rows}
        durable(HERE / 'RAW_IDENTITY_VERIFICATION.json', raw_manifests)
        # Frozen CLI scripts own all error metrics and both Pareto verdicts.
        comparison('PRIMARY', lock['commands']['PRIMARY'], ledger)
        primary = json.loads((HERE / 'PRIMARY_COMPARISON_RAW.json').read_text())
        comparison('SECONDARY', lock['commands']['SECONDARY'], ledger)
        secondary = json.loads((HERE / 'SECONDARY_REFINEMENT_COMPARISON.json').read_text())
        recheck(lock)
        aliases = json.loads((REPO / 'research/r31am_post_z075/ncp_followup_20260930/POLICY_REPLAY.json').read_text())['parent_primary_verdict_semantic_aliases']
        primary_verdict = aliases[primary['verdict']]
        secondary_verdict = secondary['secondary_verdict']
        policy_helper = module(REPO / 'research/r31am_post_z075/post_z075_policy.py', 'z075_frozen_policy')
        action = policy_helper.post_z075_action(primary_verdict, secondary_verdict)
        policy = json.loads((REPO / 'research/r31am_post_z075/POST_Z075_DECISION_POLICY.json').read_text())
        declared = [r for r in policy['action_matrix'] if r['primary'] == primary_verdict and r['secondary'] == secondary_verdict]
        if len(declared) != 1 or declared[0]['action'] != action['action']:
            raise RuntimeError('frozen action matrix mismatch')
        durable(HERE / 'POST_Z075_POLICY_ACTION.json', {'primary_verdict': primary_verdict, 'parent_primary_raw_verdict': primary['verdict'],
            'secondary_verdict': secondary_verdict, 'R31AM_policy_sha256': lock['R31AM_policy_sha256'], **action,
            'automatic_model_successor_created': False, 'z075_training_consumed': False})
        # Read raw precision-preserving direct diagnostics; never replace independent dotO.
        with np.load(HERE / 'OD_RAW/ASSEMBLED_OD.npz', allow_pickle=False) as f:
            od = {k: f[k] for k in f.files}
        with np.load(HERE / 'JVP_RAW/ASSEMBLED.npz', allow_pickle=False) as f:
            jvp = {k: f[k] for k in f.files}
        direct_info = {'raw_dtypes': {k: str(v.dtype) for k, v in {'O': od['O'], 'D_col': od['D_col'], 'D_row': od['D_row'], 'dotO': jvp['dotO']}.items()},
                       'shapes': {k: list(v.shape) for k, v in {'O': od['O'], 'D_col': od['D_col'], 'D_row': od['D_row'], 'dotO': jvp['dotO']}.items()},
                       'OD_JVP_O_gap_raw_max_abs_decimal': str(np.max(np.abs(jvp['O'] - od['O']))),
                       'metric_identity_raw_max_abs_decimal': str(np.max(np.abs(jvp['dotO'] - od['D_col'] - od['D_row'].conj().T))),
                       'independent_dotO_preserved': True, 'source_symmetrized': False,
                       'candidate_comparison_dtype': 'complex128 as frozen comparator; raw complex256 preserved'}
        durable(HERE / 'DIRECT_OUTPUT_IDENTITY.json', direct_info)
        if sha(Path(lock['runtime_file_baseline_path'])) != lock['runtime_file_baseline_sha256']:
            raise RuntimeError('runtime baseline inventory drift')
        baseline = set(json.loads(Path(lock['runtime_file_baseline_path']).read_text()))
        current = {str(p.relative_to(RUNTIME)) for p in RUNTIME.rglob('*') if p.is_file()}
        added = sorted(current - baseline)
        unexpected = [p for p in added if not p.startswith(('completion/mixed_h/od/B192_z0.75/', 'completion/mixed_derivative/B192_z0.75/'))]
        if unexpected:
            raise RuntimeError('unexpected runtime artifacts outside authorized node: ' + repr(unexpected))
        durable(HERE / 'NEW_RUNTIME_ARTIFACTS.json', {'new_paths': added, 'unexpected_new_paths': unexpected,
            'new_geometry_z_a0': ['0.75'], 'new_H_neutral_ionic_full49_trajectory_outputs': False})
        durable(HERE / 'POST_OUTPUT_LOCK_VERIFICATION.json', {'frozen_files_sha256': lock['frozen_files'],
            'producer_source_sha256': lock['producer_source_sha256'], 'unchanged_after_output': True,
            'post_output_model_rule_adapter_modification': False})
        result = {'schema': 'WU088_R31AL_AUTHORIZED_Z075_ONE_SHOT_RETURN_V1',
            'publication_branch': 'research/r31am-post-z075-stop-policy-20260930', 'draft_pr': 31,
            'reviewed_remote_identity': lock['remote_before_execution'],
            'pre_output_lock_publication': json.loads((HERE / 'PRE_OUTPUT_PUBLICATION.json').read_text()),
            'authorization': {'actual_envelope': json.loads((HERE / 'USER_AUTHORIZATION.json').read_text()),
                'evidence_path': 'USER_AUTHORIZATION_EVIDENCE_KO.md', 'consumed': True, 'same_envelope_rerun_allowed': False,
                'first_scientific_output_identity': ledger['first_scientific_output_identity']},
            'Z075_EXECUTION_STATUS': 'ONE_SHOT_EXECUTED_AND_CONSUMED', 'science_node_count': 1,
            'science_producer_command_count': ledger['science_commands_started'], 'z_a0': '0.75', 'radial_order': 192,
            'tau_ta_producer_decimal': lock['tau_ta_producer_decimal'], 'tau_source': 'unchanged producer z/velocity',
            'runtime': str(RUNTIME), 'environment': 'ENVIRONMENT.json', 'producer_source_sha256': lock['producer_source_sha256'],
            'producer_binary_identity': lock['producer_binary_identity'], 'source_contract': lock['source_contract'],
            'raw_checkpoints': 'RAW_IDENTITY_VERIFICATION.json', 'direct_output_identity': direct_info,
            'primary_comparison': primary, 'PRIMARY_VERDICT': primary_verdict,
            'secondary_comparison': secondary, 'SECONDARY_VERDICT': secondary_verdict,
            'frozen_R31AM_action': action, 'primary_secondary_independent_evidence_count': 1,
            'independent_single_point_validation_admitted': True,
            'independence_scope': 'One fresh z0.75 geometry; parent model/prereg/prediction/metadata/comparator identities fixed before truth access, unchanged producer, no post-output edits. Prior absence is limited to declared local/archive inventory scope.',
            'reference_error_upper_bound_status': 'SOURCE_ACCURACY_BOUND_UNAVAILABLE', 'reference_sensitivity_calculated': False,
            'automatic_z075_training_consumption': False, 'automatic_new_knot': False, 'automatic_next_node': False,
            'claim_ceiling': {k: False for k in ('interval_wide_accuracy', 'all_cell_refinement_gain', 'source_accuracy', 'transition_error',
                'full_cell', 'trajectory', 'H_skip', 'production')},
            'remaining_gates': {'full_cell': 'FULLCELL_AUTHORITY_INPUT_BLOCKED', 'fixed_Q_complete_HH_physical_invariance': False,
                'BR01': 'OPEN', 'BR02': 'OPEN', 'independent_project_review_admitted': False, 'production_admitted': False,
                'source_accuracy_bound': 'SOURCE_ACCURACY_BOUND_UNAVAILABLE', 'B_order_reference_certification': 'NOT_ADMITTED'},
            'raw_restore_performed': False, 'RESTORE_VERIFIED': False,
            'stop_condition': 'one direct geometry; frozen primary then secondary then R31AM action; ordinary publication and dual create-only backup; no successor'}
        durable(HERE / 'RETURN.json', result)
        ledger.update(one_shot_state='CONSUMED_COMPARISONS_AND_POLICY_COMPLETE', PRIMARY_VERDICT=primary_verdict,
                      SECONDARY_VERDICT=secondary_verdict, R31AM_action=action['action'], comparisons_complete_utc=now())
        durable(LEDGER, ledger)
        print(json.dumps({'PRIMARY': primary_verdict, 'SECONDARY': secondary_verdict, 'action': action['action'],
            'R31AK_errors': primary['R31AK_errors'], 'R31Z_errors': primary['R31Z_errors'],
            'R31AD_coarse_errors': secondary['coarse_R31AD_errors'],
            'improvement_fractions': secondary['improvement_fractions_refined_vs_coarse']}, indent=2))


if __name__ == '__main__':
    main()
