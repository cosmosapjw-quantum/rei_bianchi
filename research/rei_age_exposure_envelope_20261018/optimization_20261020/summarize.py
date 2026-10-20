"""Assemble observed optimization measurements; does not rerun a calculation."""
import hashlib
import json
from pathlib import Path
import statistics
import csv
from bench import mode_activation_failures

HERE = Path(__file__).resolve().parent
RESULTS = HERE/'results'


def main():
    groups = {
        'baseline_2': ['BASELINE', 'BASELINE_rep2', 'BASELINE_rep3'],
        'integer_taylor_A_2': ['A', 'A_rep2', 'A_rep3'],
        'preload_B_2': ['B2', 'B2_rep2', 'B2_rep3'],
        'shared_oracle_C_2': ['C2', 'C2_rep2', 'C2_rep3'],
        'shared_oracle_C_8': ['C8', 'C8_rep2', 'C8_rep3'],
    }
    all_runs = {p.stem[:-4]: json.loads(p.read_text()) for p in RESULTS.glob('*_RUN.json')}
    mode_checks={}
    for label,r in all_runs.items():
        actual=json.loads((RESULTS/(label+'_STUDY.json')).read_text())
        failures=mode_activation_failures(actual,r.get('preload',False),r.get('reuse_oracle',False),r.get('reference_parity',False))
        mode_checks[label]={'pass':not failures,'failures':failures,
                            'expected_negative_control':label.startswith('NEGATIVE_')}
    records = {}
    for name, labels in groups.items():
        rows = [all_runs[label] for label in labels]
        records[name] = {'labels': labels, 'wall_seconds': [r['wall_seconds'] for r in rows],
                         'median_wall_seconds': statistics.median(r['wall_seconds'] for r in rows),
                         'median_total_cpu_seconds': statistics.median(r['user_cpu_seconds']+r['system_cpu_seconds'] for r in rows),
                         'peak_rss_kb': [r['peak_rss_kb'] for r in rows],
                         'all_exit_zero': all(r['exit_code']==0 for r in rows),
                         'numeric_parity_to_baseline': all(r.get('numeric_byte_parity', label=='BASELINE') for label, r in zip(labels, rows))}
    baseline = records['baseline_2']['median_wall_seconds']
    for record in records.values():
        record['speedup_vs_baseline_2'] = baseline/record['median_wall_seconds']
    study = json.loads((RESULTS/'C8_STUDY.json').read_text())
    counters = [p['grouped_affine']['optimization'] for p in study['paired_bounds']]
    parity = json.loads((RESULTS/'B8_REFERENCE_STUDY.json').read_text())
    summary = {
        'contract': 'OPT20261020-A plus authorized B and C',
        'skill_context_used': {'version':'physmath-research-loop 1.3.0',
                              'read': ['SKILL.md', 'references/POLICY_INTEGRATION.md', 'references/SUBAGENT_MODE.md', 'references/CODING_LOOP.md'],
                              'selected_scope': ['C1 inventory', 'C5 implementation', 'C6-C8 bounded validation and measurement'],
                              'behavior': 'Frozen inputs/model maintained; sequential bounded runs; one diagnosed compile repair; raw outcomes retained; C9 decision belongs to parent.'},
        'measurements': records,
        'scaling_B': {str(n): all_runs['B'+str(n)]['wall_seconds'] for n in [1,2,4,8]},
        'scaling_C': {str(n): all_runs['C'+str(n)]['wall_seconds'] for n in [1,2,4,8]},
        'measurement_run_count': len(all_runs),
        'cumulative_measurement_wall_seconds': sum(r['wall_seconds'] for r in all_runs.values()),
        'measurement_budget_seconds': 600,
        'certified_exp_evaluations': study['certified_exp_evaluations'],
        'full_input_reference_exp_endpoint_checks': parity['optimization']['reference_exp_endpoint_checks'],
        'grouped_oracle_recurrences_C': sum(r['oracle_recurrences'] for r in counters),
        'grouped_oracle_leaf_inequalities_C': sum(r['oracle_prefix_checks'] for r in counters),
        'grouped_thread_prefix_bit_comparisons_C': sum(r['thread_prefix_bit_comparisons'] for r in counters),
        'C8_phase_profile': study['optimization'],
        'current_source_identities': {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [HERE.parent/'vigilode_age_transport_20261019/rust/src/main.rs', HERE.parent/'vigilode_age_transport_20261019/rust/src/certified.rs']},
        'comparison_scope': 'Same 57344 nodes, four clock settings, fixed source/opacity/endpoint geometry. B repeats original exact oracles; C proves canonical prefixes once and transfers inequalities through all-prefix bit equality for other thread counts.',
        'scientific_campaigns_added': 0,
        'PRODUCTION_SCIENTIFIC_ADMISSION': 'NOT_ISSUED',
        'performance_scope': 'Warm executable kernel wall time; cold compiler download, install and builds are reported separately. B keeps repeated original oracle work. C uses one exact oracle per group and all-prefix thread equality to transfer the same inequalities.',
        'memory_scope': 'RUSAGE_CHILDREN peak RSS in a fresh launcher process with one executable child includes the launch high-water mark. Standard-harness baseline 27648 KiB and C 27776 KiB do not establish a kernel-memory reduction. First manually launched baseline 20616 KiB has a different launch floor.',
        'headline_comparisons': {'B_2_vs_baseline_2_same_audit_work':records['preload_B_2']['speedup_vs_baseline_2'],
                                 'C_2_vs_baseline_2_shared_oracle_validation':records['shared_oracle_C_2']['speedup_vs_baseline_2'],
                                 'C_8_vs_baseline_2_shared_oracle_and_different_thread_count':records['shared_oracle_C_8']['speedup_vs_baseline_2']},
        'raw_run_receipts': all_runs,
        'post_review_mode_checks_from_preserved_actual_outputs':mode_checks,
    }
    (RESULTS/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    (RESULTS/'BENCHMARK.json').write_text(json.dumps(summary,indent=2)+'\n')
    fields=['label','purpose','threads','preload','reuse_oracle','reference_parity','wall_seconds','user_cpu_seconds','system_cpu_seconds','peak_rss_kb','exit_code','numeric_byte_parity','binary_sha256']
    with (RESULTS/'BENCHMARK.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for label,r in all_runs.items():
            purpose='negative activation control' if label.startswith('NEGATIVE_') else 'reference validation' if 'REFERENCE' in label else 'entrypoint validation' if 'WRAPPER' in label else 'performance'
            row={k:r.get(k,'') for k in fields};row.update(label=label,purpose=purpose,threads=r['RAYON_NUM_THREADS']);writer.writerow(row)
    print(json.dumps({k: v for k,v in summary.items() if k in ['measurements','cumulative_measurement_wall_seconds','full_input_reference_exp_endpoint_checks']},indent=2))


if __name__ == '__main__':
    main()
