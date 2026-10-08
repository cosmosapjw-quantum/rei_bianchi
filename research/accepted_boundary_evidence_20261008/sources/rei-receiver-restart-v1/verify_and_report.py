#!/usr/bin/env python3
import pathlib,json,hashlib,difflib
r=pathlib.Path(__file__).resolve().parent
base=json.loads((r/'evidence/BASE_PINS.json').read_text())
fail=[]
for name,digest in base.items():
 p=pathlib.Path(name)
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:fail.append(name)
assert not fail,fail
sources={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and (p.suffix=='.rs' or p.name in ['Cargo.toml','Cargo.lock']) and 'target' not in p.parts}
(r/'evidence/DERIVATIVE_SOURCE_MANIFEST.json').write_text(json.dumps({'base_files_unchanged':len(base),'changed_derivative_files':sources,'old_hashes_identify_only_immutable_predecessors':True,'runtime_dependency':'../rei-species-energy-sidecar-v1 (accepted ZIP SHA4700d68ffda7204656fbd57d80c56a60278afb9bf0d03d1cd9c697298e0acd3f)','model':'MODEL_UNRESOLVED'},indent=2)+'\n')
old=pathlib.Path('implementation/rei-ledger-admission-v1/src/ledger_sidecar.rs')
(r/'evidence/ledger_derivative.patch').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),(r/'ledger/src/ledger_sidecar.rs').read_text().splitlines(True),fromfile=str(old),tofile='rei-receiver-restart-v1/ledger/src/ledger_sidecar.rs')))
measurements=[json.loads(p.read_text()) for p in sorted((r/'results').glob('*.json'))]
cpu=sum(j['cpu_s'] for j in measurements);wall=sum(j['wall_s'] for j in measurements)
reports=[]
for p in sorted((r/'logs').glob('process-*.stdout')):
 text=p.read_text();j=json.loads(text[:text.index('\nALL_CHANGED_PATH_PROCESS_CONTROLS_GREEN')]);reports.append({'log':str(p.relative_to(r)),**j})
aggregate={'campaigns':len(reports),'campaign_details':reports,'all_real_native_trials':sum(j['actual_native_trials'] for j in reports),'all_real_native_rhs':sum(j['actual_native_rhs'] for j in reports),'provider_values_reported':sum(j['actual_provider_calls'] for j in reports),'provider_calls_directly_observed':sum(j['actual_provider_calls'] for j in reports)-117,'early_case0_pending_provider_calls_structurally_inferred':117,'inference_note':'Initial case-0 stop injection used (observed RHS+3)*3 for the one-node fixture; subsequent campaigns persist actual observed provider counters. Retained honestly, not upgraded to direct measurement.','prior_old15_controls_not_rerun':True}
(r/'evidence/ALL_EXECUTION_CAMPAIGNS.json').write_text(json.dumps(aggregate,indent=2)+'\n')
report={'new_allocation_cpu_s':180,'new_allocation_execution_wall_s':300,'measured_CPU_s':cpu,'measured_execution_wall_s':wall,'reserved_CPU_s':20,'reserved_execution_wall_s':35,'total_with_reserves_CPU_s':cpu+20,'total_with_reserves_wall_s':wall+35,'remaining_CPU_s':160-cpu,'remaining_wall_s':265-wall,'prior_remaining_CPU_s_untouched':52.918577,'prior_remaining_wall_s_untouched':66.00694260899763,'dispatch_model_elapsed_excluded':True,'numeric_max_sampled_group_RSS_bytes':max(j['sampled_group_peak_rss_bytes'] for j in measurements if j['command'][:1]==['python3']),'new_disk_bytes':sum(p.stat().st_size for p in r.rglob('*') if p.is_file()),'immutable_pins_verified':len(base)}
(r/'evidence/RESOURCE_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'pins_unchanged':len(base),'latest_controls':len(reports[-1]['controls_passed']),'all_native_trials':aggregate['all_real_native_trials'],'resources':report},indent=2))
