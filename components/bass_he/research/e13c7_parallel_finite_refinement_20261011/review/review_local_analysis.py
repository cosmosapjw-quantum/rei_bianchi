#!/usr/bin/env python3
"""Independent saved-data decision review. No candidate imports or kernel calls."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
from datetime import datetime, timezone
import csv
import hashlib
import heapq
import io
import json
import math
import statistics
import time
import review_inputs as ri
import review_saved_outputs as so

ROOT, HERE = ri.ROOT, ri.HERE
check = ri.check

def display(x):
    with localcontext() as c:
        c.prec = 22
        return str(Decimal(x.numerator) / Decimal(x.denominator))

def rows(a, b):
    return [so.comparison(a[k][q], b[k][q], k, q) for k in sorted(a) for q in sorted(a[k])]

def close(a, b):
    return math.isclose(a, b, rel_tol=2e-15, abs_tol=1e-12)

def main():
    started = time.perf_counter()
    saved_review_identities = {}
    evidence = {}
    index = ri.read(ROOT/'inputs/INPUT_INDEX.json')['records']
    for name in ('BRANCH_OUTPUT_REVIEW.json', 'PRIMARY_OUTPUT_REVIEW.json', 'RESOLUTION_OUTPUT_REVIEW.json'):
        prior = ri.read(HERE/name)
        saved_review_identities[name] = ri.h(HERE/name)
        check('prior_independent_output_review_pass', prior['checks_failed'] == 0 and prior['scientific_kernel_invocations'] == 0, name)
        for item in prior['paths']:
            directory = ROOT/item['relative_directory']
            result = ri.read(directory/'RESULT.json')
            admission = ri.read(directory/'ADMISSION.json')
            complete = ri.read(directory/'COMPLETE.json')
            tag = (result['work']['node'], result['work']['N'], result['work']['precision'])
            check('saved_review_bound_to_actual_result', ri.h(directory/'RESULT.json') == item['result_sha256'] == complete['result_sha256'], tag)
            check('saved_review_bound_to_actual_admission', ri.h(directory/'ADMISSION.json') == item['admission_sha256'] == complete['admission_sha256'], tag)
            check('saved_review_semantic_binding', complete['semantic_sha256'] == item['semantic_sha256'], tag)
            check('saved_review_unique_work', tag not in evidence, tag)
            rec = index[str(tag[0])]
            with (ROOT/'inputs/OFF_OLD_PATHS.jsonl').open('rb') as f:
                f.seek(rec['offset']); raw = f.read(rec['bytes'])
            check('old_weight_source_binding', hashlib.sha256(raw).hexdigest() == rec['old_line_sha256'], tag)
            old = json.loads(raw)
            weighted = so.new_metrics(result['track'], ri.pair(old['weight'])[0])
            check('saved_raw_weighted_definition', weighted == ri.decode(admission['new_raw_weighted']), tag)
            evidence[tag] = {'result':result, 'admission':admission, 'complete':complete,
                             'path':item['relative_directory'], 'metrics':weighted}
    contract = ri.read(ROOT/'RESEARCH_CONTRACT.json')
    expected = {(n,512,60) for n in contract['local_primary_nodes']}
    expected |= {(n,1024,60) for n in contract['local_resolution_diagnostic_nodes']}
    expected |= {(n,N,P) for n in contract['local_branch_control_nodes'] for N,P in ((32,60),(32,80),(128,60))}
    check('exact_24_completed_work_items', set(evidence) == expected and len(evidence) == 24)
    analysis_dir = ROOT/'analysis/LOCAL'
    analysis = ri.read(analysis_dir/'LOCAL_ANALYSIS.json')
    candidate = ri.read(analysis_dir/'LOCAL_ADMITTED_CANDIDATE.json')
    identity = ri.read(analysis_dir/'ANALYSIS_IDENTITY.json')
    check('analysis_file_sha256', ri.h(analysis_dir/'LOCAL_ANALYSIS.json') == identity['analysis_file_sha256'])
    check('candidate_file_sha256', ri.h(analysis_dir/'LOCAL_ADMITTED_CANDIDATE.json') == identity['candidate_sha256'])
    check('csv_file_sha256', ri.h(analysis_dir/'LOCAL_FULL_WIDTHS.csv') == identity['csv_sha256'])
    semantic = hashlib.sha256(b'bass-he-e13c7-local-analysis-v1\n' + ri.canon(analysis)).hexdigest()
    check('analysis_semantic_recomputed', semantic == identity['analysis_semantic_sha256'])
    check('source_scientific_lock_unchanged', ri.h(ROOT/'SOURCE_LOCK.json') == so.SOURCE == analysis['source_lock_sha256'] == candidate['source_lock_sha256'])
    check('candidate_raw_no_intersection', candidate['intersection_used'] is False and analysis['intersection_used'] is False)
    check('pending_review_status_truthful', candidate['decision'] == 'PENDING_INDEPENDENT_REVIEW' and analysis['status'] == 'PASS_MECHANICAL_PENDING_INDEPENDENT_REVIEW')
    selected = {n:(1024 if n in contract['local_resolution_diagnostic_nodes'] else 512) for n in contract['local_primary_nodes']}
    actual_selection = {p['node']:p['N'] for p in candidate['paths']}
    check('mixed_eight_selection', actual_selection == selected and len(candidate['paths']) == 8, actual_selection)
    for p in candidate['paths']:
        item = evidence[p['node'],p['N'],p['precision']]
        check('chosen_path_mechanically_admissible', item['admission']['mechanically_admissible'], p['node'])
        check('chosen_raw_interval_unmodified', ri.decode(p['new_raw_weighted']) == item['metrics'], p['node'])
        check('chosen_path_identity_exact', p['path'] == item['path'] and all(p[k] == item['complete'][k] for k in ('result_sha256','admission_sha256','semantic_sha256')), p['node'])
    resolution_rows = []
    resolution_summary = []
    for n in contract['local_resolution_diagnostic_nodes']:
        low, high = evidence[n,512,60], evidence[n,1024,60]
        comparison = rows(low['metrics'],high['metrics'])
        eligible = all(r['nested'] and r['width_nonincreasing'] and r['overlap'] for r in comparison) and high['admission']['mechanically_admissible']
        check('N1024_all34_raw_eligible_over_N512', len(comparison) == 34 and eligible, n)
        time_lo,time_hi = low['result']['elapsed_seconds'],high['result']['elapsed_seconds']
        resolution_rows.append({'node':n,'rows_N512_to_N1024':comparison,'raw_N1024_eligible_over_N512':eligible,
                               'seconds_N512':time_lo,'seconds_N1024':time_hi,'observed_time_ratio':time_hi/time_lo})
        ratios={q:F(next(r['new_width'] for r in comparison if r['kind']=='absolute' and r['quantity']==q))/F(next(r['old_width'] for r in comparison if r['kind']=='absolute' and r['quantity']==q)) for q in ('P_final','H_total_eV')}
        resolution_summary.append({'node':n,'metric_pairs':34,'admissible':eligible,'observed_time_ratio':time_hi/time_lo,
            'photon_width_ratio':str(ratios['P_final']),'heat_width_ratio':str(ratios['H_total_eV']),
            'photon_width_ratio_display':display(ratios['P_final']),'heat_width_ratio_display':display(ratios['H_total_eV'])})
    check('resolution_analysis_exact', resolution_rows == analysis['resolution_comparison'])
    pred = ri.read(ROOT/'inputs/PREDECESSOR_BUDGET.json')
    prior6, bulk, old_local, old_full = [ri.decode(pred[k]) for k in ('prior_six','old_ncp_2331','old_local_eight','E13C6_full')]
    new_local = ri.combine(evidence[n,N,60]['metrics'] for n,N in selected.items())
    primary_local = ri.combine(evidence[n,512,60]['metrics'] for n in contract['local_primary_nodes'])
    full = ri.combine([prior6,bulk,new_local])
    primary_full = ri.combine([prior6,bulk,primary_local])
    check('predecessor_direct_partition_bridge', ri.combine([prior6,bulk,old_local]) == old_full)
    check('retained_prior_six_direct_equality', ri.decode(candidate['retained_prior_six']) == prior6)
    check('unrun_bulk_old_intervals_retained', ri.decode(candidate['still_old_ncp_2331']) == bulk)
    check('selected_eight_direct_Fraction_sum', ri.decode(candidate['new_local_eight']) == new_local)
    check('full_direct_Fraction_sum', ri.decode(candidate['current_full_OFF']) == ri.decode(analysis['full_after_local_eight']) == full)
    check('N512_only_direct_Fraction_sum', ri.decode(analysis['full_after_N512_eight_only']) == primary_full)
    check('full_old_intervals_exact', ri.decode(analysis['full_old_E13C6']) == old_full)
    full_rows = rows(old_full,full)
    check('full_comparison_exact', analysis['full_comparison'] == full_rows and len(full_rows) == 34)
    for r in full_rows:
        check('full_raw_overlap_nested_nonincreasing', r['overlap'] and r['nested'] and r['width_nonincreasing'], (r['kind'],r['quantity']))
    precision_rows=[]
    negative_rows=[]
    for n in contract['local_branch_control_nodes']:
        a,b=evidence[n,32,60],evidence[n,32,80]
        for r in rows(a['metrics'],b['metrics']):
            u,v=ri.pair(r['old']),ri.pair(r['new_raw']);width=u[1]-u[0]
            shift=max(abs(x-y) for x,y in zip(u,v))
            precision_rows.append({'node':n,'kind':r['kind'],'quantity':r['quantity'],'overlap':r['overlap'],
                'max_endpoint_shift':str(shift),'shift_over_P60_width':str(shift/width) if width else None,'zero_width_equal':u==v if not width else None})
        same=evidence[n,128,60]['admission']
        check('same_N128_negative_control_not_admitted', not same['mechanically_admissible'], n)
        negative_rows.extend({'node':n,**r} for r in same['comparisons'])
    check('precision_diagnostics_exact', precision_rows == analysis['precision_comparison'] and len(precision_rows)==136)
    check('same_N128_negative_evidence_preserved', negative_rows == analysis['same_N128_comparison'] and analysis['same_N128_new_formula_advantage']=='NOT_ESTABLISHED')
    resource_rows=[]
    for tag,item in sorted(evidence.items()):
        r=item['result']
        resource_rows.append({**r['work'],'seconds':r['elapsed_seconds'],'peak_RSS_KiB':r['peak_RSS_KiB'],
            'segments':r['new_local_enclosures'],'coefficient_evaluations':r['new_coefficient_evaluations'],
            'path':item['path'],'semantic_sha256':item['complete']['semantic_sha256']})
    check('resource_records_are_actual_saved_observations', resource_rows == analysis['resource_rows'])
    expected_counts={'scientific_path_work_items':24,'fresh_local_enclosures':sum(r['segments'] for r in resource_rows),
                     'coefficient_evaluations':sum(r['coefficient_evaluations'] for r in resource_rows),
                     'prior_scientific_reruns':0,'ODE_solves':0,'gas_advances':0,'native_runs':0,'NCP_new_batch_paths':0}
    check('exact_actual_invocation_counts', analysis['actual_counts']==expected_counts and expected_counts['fresh_local_enclosures']==56 and expected_counts['coefficient_evaluations']==38656)
    check('heavy_and_general_claims_not_promoted', analysis['full_2331_refinement']=='NOT_RUN' and 'physical/continuum/production/receiver HOLD' in candidate['claim_ceiling'])
    radius=[]
    for n,N in [(n,512) for n in contract['local_primary_nodes']]+[(n,1024) for n in contract['local_resolution_diagnostic_nodes']]:
        t=evidence[n,N,60]['result']['track'];last=t['segments'][-1]
        total=F(t['final_photon']['radius']);numeric=F(t['final_photon']['numerical_and_representation_radius'])
        incoming=F(last['remainder']['incoming_upper']['P1']);coupling=F(last['remainder']['nonlinear_upper']['P1'])
        check('radius_component_budget',total>0 and min(numeric,incoming,coupling)>=0 and total>=numeric+incoming+coupling,(n,N))
        radius.append({'node':n,'N':N,'photon_radius':str(total),'numeric_representation':str(numeric),'incoming':str(incoming),
            'coupling':str(coupling),'numeric_fraction':str(numeric/total),'incoming_fraction':str(incoming/total),'coupling_fraction':str(coupling/total)})
    check('saved_radius_components_exact',radius==analysis['radius_components'])
    buf=io.StringIO(newline='');writer=csv.writer(buf)
    writer.writerow(['kind','quantity','old_width_exact','local_refined_width_exact','gain_percent','old_width_display','local_refined_width_display'])
    for r in full_rows:
        ow,nw=F(r['old_width']),F(r['new_width'])
        writer.writerow([r['kind'],r['quantity'],str(ow),str(nw),display(100*(ow-nw)/ow) if ow else 'EXACT_ZERO',display(ow),display(nw)])
    expected_csv=buf.getvalue().encode()
    check('all34_CSV_actual_bytes_parity',expected_csv==(analysis_dir/'LOCAL_FULL_WIDTHS.csv').read_bytes())
    plan=ri.read(ROOT/'inputs/WORK_PLAN.json');pre=ri.read(ROOT/'evidence/PRE_PILOT_WORK_PLAN.json')
    check('final_heavy_resolution_single_N1024',plan['status']=='SEALED_FOR_HEAVY_NCP' and plan['primary_N']==1024 and plan['precision']==60)
    check('final_plan_local_candidate_pin',plan['local_admission_candidate_sha256']==identity['candidate_sha256'] and plan['local_source_lock_sha256']==so.SOURCE)
    for k in ('ncp_nodes','zero_nodes','local_primary_nodes','prior_admitted_nodes','local_branch_control_nodes','local_resolution_diagnostic_nodes'):
        check('final_plan_preserves_declared_groups',plan[k]==pre[k],k)
    for node,rec in plan['input_records'].items():
        plain={k:v for k,v in rec.items() if k not in ('cost_status','estimated_cost_seconds')}
        check('final_plan_only_scheduling_metadata_changes',plain==pre['input_records'][node],node)
    bulk_nodes=plan['ncp_nodes']
    check('heavy_distinct_excluded_completed_paths',len(bulk_nodes)==len(set(bulk_nodes))==2331 and not set(bulk_nodes)&set(plan['local_primary_nodes']+plan['prior_admitted_nodes']+plan['zero_nodes']))
    check('heavy_frozen_coefficient_work_count',plan['ncp_new_segments']==4662 and plan['ncp_new_coefficient_evaluations']==sum(2*plan['primary_N']*plan['input_records'][str(n)]['segments'] for n in bulk_nodes)==9547776)
    check('heavy_only_not_global_budget',plan['ncp_global_fraction_reduction']=='NOT_RUN_RETURN_TO_CHAT' and plan['ncp_transport']=='mpi' and plan['computing_ranks_max']==64 and plan['controller_mpi_ranks']==0 and plan['threads_per_rank']==1)
    allocation=ri.read(ROOT/'analysis/RESOURCE_ALLOCATION.json')
    cal=allocation['same_work_host_calibration']
    baseline=ROOT.parents[1]/'e13c6_research_20261011/BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1/runs/N512_P60/RESULTS.json'
    remote=ROOT.parent/'intake/returned_abf524a50718/N512_P60/RESULTS.json'
    check('existing_same_work_timing_actual_bytes',ri.h(baseline)==cal['Chat_result_sha256'] and ri.h(remote)==cal['NCP_result_sha256'])
    bt,rt=ri.read(baseline)['elapsed_seconds'],ri.read(remote)['elapsed_seconds']
    check('calibration_is_saved_ratio_only',cal['Chat_E13C6_seconds']==bt and cal['recorded_NCP_E13C6_seconds']==rt and cal['ratio']==rt/bt)
    counts={str(s):sum(plan['input_records'][str(n)]['active_species']==s for n in bulk_nodes) for s in (1,2,3)}
    for scenario in allocation['scenarios']:
        N=scenario['N'];means={}
        for species in (1,2,3):
            times=[x['result']['elapsed_seconds'] for (n,nn,p),x in evidence.items() if nn==N and p==60 and plan['input_records'][str(n)]['segments']==2 and plan['input_records'][str(n)]['active_species']==species]
            means[str(species)]=statistics.mean(times)
        check('timing_class_means_from_actual_local_samples',all(close(means[k],scenario['class_local_seconds'][k]) for k in means) and scenario['class_counts']==counts,N)
        local_seconds=sum(means[k]*counts[k] for k in means);remote_seconds=local_seconds*cal['ratio']
        check('runtime_estimates_arithmetic_only',close(scenario['local_single_worker_equivalent_seconds_estimate'],local_seconds) and close(scenario['recorded_NCP_single_worker_equivalent_seconds_estimate'],remote_seconds) and close(scenario['NCP_single_worker_hours_estimate'],remote_seconds/3600) and close(scenario['ideal_64_computing_rank_minutes_estimate'],remote_seconds/64/60),N)
        for efficiency in (.5,.8):
            field=f'64_rank_{round(100*efficiency)}_percent_efficiency_minutes_scenario'
            check('conditional_efficiency_scenario_arithmetic',close(scenario[field],remote_seconds/64/60/efficiency),(N,efficiency))
    rss=max(r['peak_RSS_KiB'] for r in resource_rows)
    check('memory_observation_and_scenario_separated',allocation['max_measured_local_worker_RSS_KiB']==rss==50496 and allocation['64_times_max_local_RSS_GiB_scenario']==rss*64/(1024**2) and allocation['memory_fill_goal'] is False)
    check('performance_claim_ceiling_explicit','no actual64-rank speedup or bulk runtime measured' in allocation['performance_claim_ceiling'])
    preview=ri.read(ROOT/'analysis/NCP_SCHEDULE_64_PREVIEW.json')
    costs={n:F(str(plan['input_records'][str(n)]['estimated_cost_seconds'])) for n in bulk_nodes}
    check('cost_pins_equal_preview',set(preview['node_costs'])==set(map(str,bulk_nodes)) and all(F(preview['node_costs'][str(n)]['value'])==costs[n] and preview['node_costs'][str(n)]['source']=='estimated_cost_seconds' for n in bulk_nodes))
    queue=[(F(0),r) for r in range(64)];heapq.heapify(queue);shards=[[] for _ in range(64)]
    for n in sorted(bulk_nodes,key=lambda n:(-costs[n],n)):
        load,r=heapq.heappop(queue);shards[r].append(n);heapq.heappush(queue,(load+costs[n],r))
    loads=[sum((costs[n] for n in part),F(0)) for part in shards]
    check('deterministic_LPT_preview_exact',shards==preview['shards'] and loads==list(map(F,preview['predicted_rank_costs'])))
    summary={}
    for q in ('P_final','H_total_eV'):
        r=next(x for x in full_rows if x['kind']=='absolute' and x['quantity']==q)
        summary[q]={'old_width_exact':r['old_width'],'new_width_exact':r['new_width'],'old_width_display':display(F(r['old_width'])),'new_width_display':display(F(r['new_width'])),'gain_percent_display':display(100*F(r['gain_fraction']))}
    report={'schema':'bass-he-e13c7-independent-local-analysis-review-v1','reviewer':'e13c7_intake','observed_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS_EXACT_LOCAL_REFINEMENT_AND_HEAVY_WORK_SELECTION' if not ri.failures else 'HOLD','candidate_modules_imported':0,'scientific_kernel_invocations':0,
        'checks':ri.checks,'checks_passed':sum(x['passed'] for x in ri.checks.values()),'checks_failed':sum(x['failed'] for x in ri.checks.values()),'failures':ri.failures,
        'prior_review_file_sha256':saved_review_identities,'source_lock_sha256':so.SOURCE,'analysis_identity':identity,'selected_resolutions':actual_selection,
        'actual_local_counts':expected_counts,'all34_full_raw_comparisons_pass':all(r['nested'] and r['overlap'] and r['width_nonincreasing'] for r in full_rows),
        'full_width_summary':summary,'resolution_summary':resolution_summary,'frozen_heavy_scope':{'paths':2331,'N':1024,'precision':60,'new_segments':4662,'new_coefficient_evaluations':9547776,'executed':0},
        'resource_review':{'cost_model':'extrapolation from saved per-class local means and existing same-work host ratio','measured_64_rank_scaling':'NOT_RUN','predicted_shard_sizes':[len(x) for x in shards],'predicted_max_rank_seconds':display(max(loads)),'predicted_min_rank_seconds':display(min(loads))},
        'elapsed_seconds':time.perf_counter()-started,'claim_ceiling':'Promotable finite raw replacement for selected eight paths only. Heavy execution readiness still requires final wrapper and final execution lock review; full bulk science/actual MPI NOT_RUN; physical/continuum/production/receiver HOLD.'}
    (HERE/'LOCAL_ANALYSIS_REVIEW.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('status','checks_passed','checks_failed','elapsed_seconds','full_width_summary')},sort_keys=True))
    if ri.failures:print(json.dumps(ri.failures,indent=2))
    return 1 if ri.failures else 0

if __name__=='__main__':
    raise SystemExit(main())
