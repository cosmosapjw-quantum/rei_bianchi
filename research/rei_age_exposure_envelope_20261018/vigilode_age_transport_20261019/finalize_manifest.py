"""Record the implementation's concrete owned files, identities and executions."""
from pathlib import Path
import datetime
import hashlib
import json

HERE=Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text())


def main():
    source_map=load(HERE/'inputs/SOURCE_MAP.json')
    source_map['baseline_pr_head']='0ae749e9fdb179729c018706dbd59c4f61732b6a'
    (HERE/'inputs/SOURCE_MAP.json').write_text(json.dumps(source_map,indent=2)+'\n')
    failures=load(HERE/'results/FAILED_ATTEMPTS.json')
    for failure in failures:
        if failure['name']=='offline_vendor_reused_registry_target':
            failure['fix']='Authorized deletion of only task-owned regenerable target; clean vendor-only rebuild passed, followed by offline locked test with no Cargo registry.'
    (HERE/'results/FAILED_ATTEMPTS.json').write_text(json.dumps(failures,indent=2)+'\n')
    study=load(HERE/'results/STUDY.json')
    export=load(HERE/'inputs/EXPORT_RECEIPT.json')
    final_commands=load(HERE/'results/RUN_COMMANDS.json')
    initial_commands=load(HERE/'results/global_min_before_grouping/RUN_COMMANDS.json')
    initial_test=load(HERE/'results/CARGO_TEST_RECEIPT.json')
    vendor_failed=load(HERE/'results/failed_attempts/offline_vendor_source_switch/OFFLINE_VENDOR_TEST_RECEIPT.json')
    vendor_final=load(HERE/'results/VENDOR_ONLY_FINAL_TEST_RECEIPT.json')
    explicit_names={'README.md','prepare_export.py','run_study.py','verify.py',
                    'summarize.py','finalize_manifest.py','ship_artifacts.py'}
    files={}
    for path in sorted(HERE.rglob('*')):
        if not path.is_file(): continue
        rel=path.relative_to(HERE)
        if rel.parts[0] not in {'rust','inputs','results','intake','reviews'} and str(rel) not in explicit_names: continue
        if '__pycache__' in rel.parts: continue
        files[str(rel)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                         'bytes':path.stat().st_size}
    outputs=[]
    for pair in study['paired_bounds']:
        outputs.append({'coarse':pair['coarse'],'fine':64,
                        'signed_difference_central':pair['central_N_difference'],
                        'global_min_prefix_upper':pair['affine_prefix_final_upper'],
                        'sharp_per_node_upper':pair['sharp_per_node_final_upper'],
                        'grouped_prefix_upper':pair['grouped_affine']['final_upper'],
                        'grouped_rate_groups':pair['grouped_affine']['groups'],
                        'grouped_leaves':pair['grouped_affine']['total_leaves'],
                        'grouped_compositions_per_thread_count_evaluation':pair['grouped_affine']['total_compositions']})
    record={'schema':'rei.vigilode_age_transport.implementation.v1',
            'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'baseline_pr_number':199,'baseline_pr_head':source_map['baseline_pr_head'],
            'native_input_sha':export['prepared_identity']['native_sha'],
            'vigilode_revision':'ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406',
            'integration':'Unmodified vendored affine_transport.rs and directed.rs with a thin local compatible error layer; not the full nonlinear VigilODE solver.',
            'PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED',
            'native_time_HOLD_resolved':False,'existing_age32_NCP_READY_modified':False,
            'existing_source_modified':False,'git_state_changed':False,'git_push_performed':False,
            'native_original_files_independently_rehashed':153,
            'unique_source_templates':64,'unique_prepared_node_rows':57344,
            'unique_scientific_birth_group_settings':[8,16,32,64],
            'unique_rate_tuples':1113,'sensitive_grouped_prefix_rate_groups':1112,
            'passive_nodes':4096,'native_coefficient_export_invocations':1,
            'native_history_or_transformed_rhs_invocations':0,
            'full_fixed_dataset_diagnostic_invocations':2,
            'diagnostic_invocation_explanation':'Same immutable four settings first with global minimum hazard, then with evidence-driven exact-rate grouped prefixes. These are not eight unique scientific cases.',
            'unique_rust_unit_tests':4,'task_rust_unit_tests':3,'unmodified_upstream_rust_unit_tests':1,
            'successful_rust_unit_test_command_invocations':4,
            'failed_rust_compile_test_command_invocations':1,
            'decimal_exp_fixtures':17,'decimal_precision':100,
            'decimal_full_labelled_D_settings':4,
            'rayon_thread_counts':[1,2,4],
            'thread_parity_scope':'Every global prefix radius, and each fixed-order grouped final-radius vector; reused workspace agrees with allocating global API.',
            'tests_are_repeated_not_additional_unique_cases':True,
            'budgets_seconds':{'native_export':120,'rust_tests_and_diagnostic_each':240},
            'cargo_build_jobs':2,'public_dependency_packages_locked_and_vendored':22,
            'wall_seconds':{'native_export_compile_and_run':export['wall_seconds'],
                            'initial_clean_rust_test_build':initial_test['wall_seconds'],
                            'initial_fixed_data_kernel':load(HERE/'results/global_min_before_grouping/STUDY.json')['wall_seconds'],
                            'final_grouped_fixed_data_kernel':study['wall_seconds']},
            'actual_commands':{'native_export':{k:export[k] for k in ['command','exit_code','wall_seconds']},
                               'initial_rust_tests':initial_test,'initial_diagnostic_runner':initial_commands,
                               'offline_vendor_failed_before_cache_reset':vendor_failed,
                               'final_diagnostic_runner':final_commands,'offline_vendor_final':vendor_final},
            'results':outputs,
            'verification_receipt':'results/VERIFICATION.json',
            'input_source_map':'inputs/SOURCE_MAP.json',
            'preparation_preservation_audit':'inputs/PREPARATION_AUDIT.json',
            'failed_attempts_preserved':'results/FAILED_ATTEMPTS.json',
            'runtime_maintenance_receipts':['results/VENDOR_TARGET_CLEANUP_RECEIPT.json'],
            'limitations':['Fixed endpoint geometry and opacity; no expanding-history or nonlinear state feedback solve.',
                           'Exact-real certificate begins at imported binary64 model coefficients, not at the earlier native atomic coefficient calculation.',
                           'Photon affine bounds do not certify age-moment differences; zero hazard does not imply zero age-moment error.',
                           'Global minimum hazard prefix is valid but loose; grouped hazard prefixes retain spectrum information.',
                           'Decimal100 is an independent high precision numerical check, not an additional formal transcendental proof.'],
            'owned_file_count':len(files),'owned_file_bytes':sum(f['bytes'] for f in files.values()),
            'owned_files':files,
            'manifest_excludes_itself':True,
            'root_authored_theory_and_publication_documents_not_claimed':True,
            'curated_intake_and_review_copies_recorded_as_collected_evidence':True,
            'passive_sensitive_reporting_reaggregation':'results/PASSIVE_SPLIT_REAGGREGATION_RECEIPT.json',
            'independent_root_review_required_before_publication':True}
    (HERE/'IMPLEMENTATION.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'status':'IMPLEMENTED','owned_files':len(files),
                      'owned_bytes':record['owned_file_bytes'],
                      'native_exports':1,'unique_settings':4,'diagnostic_invocations':2}))


if __name__=='__main__':main()
