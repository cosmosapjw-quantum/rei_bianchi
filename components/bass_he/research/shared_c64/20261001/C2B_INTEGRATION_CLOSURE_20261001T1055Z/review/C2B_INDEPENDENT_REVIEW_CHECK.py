"""Read-only independent scalar audit; no scientific evaluator is imported."""
from pathlib import Path
import collections, hashlib, json, math, zipfile

ROOT = Path(__file__).resolve().parents[1]
def read(rel): return json.loads((ROOT / rel).read_bytes())
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def maximum_difference(a, b, keys): return max(abs(a[k] - b[k]) for k in keys)
def near(a, b): assert abs(a-b) <= 2e-15 * max(1., abs(a), abs(b)), (a, b)

contract = read('CONTRACT.json'); limits = contract['criteria']
author = read('evidence/INITIAL_AUDIT.json')
assert author['contract_sha256'] == digest(ROOT/'CONTRACT.json')
expected = {t['task_id']: t for t in read('inputs/MAIN_TASKS.json')['tasks']}
docs, results, reviewed_files = {}, {}, {}
snapshot = zipfile.ZipFile(ROOT/'provenance/MAIN_ATTEMPT_CODE_SNAPSHOT.zip')
source_changes = {}
for batch, summary_name in [('MAIN_MPI','RECOVERY_ACCEPTED_TASKS.json'), ('MAIN_REMAINDER_MPI','BATCH_SUMMARY.json')]:
    base = ROOT/'evidence'/batch
    summary = json.loads((base/summary_name).read_bytes())
    assert summary['status'] == ('PARTIAL_EXECUTION_RECOVERED_PASS' if batch=='MAIN_MPI' else 'ALL_WORKER_RESULTS_PASS')
    run = json.loads((base/'RUN_IDENTITY.json').read_bytes())
    source_changes[batch] = []
    for rel, sha in run['code']['files'].items():
        if digest(ROOT/rel) != sha:
            assert hashlib.sha256(snapshot.read(rel)).hexdigest() == sha
            source_changes[batch].append(rel)
    for entry in summary['tasks']:
        task_id = entry['task_id']; folder = base/task_id
        assert task_id not in docs
        task = json.loads((folder/'TASK_INPUT.json').read_bytes())
        assert task == expected[task_id]
        result = json.loads((folder/'RESULT.json').read_bytes())
        execution = json.loads((folder/'TASK_EXECUTION.json').read_bytes())
        data_path = folder/result['evidence_file']; data = json.loads(data_path.read_bytes())
        assert result['status']=='PASS' and execution['status']=='WORKER_RESULT_PASS'
        assert result['code_identity_sha256']==run['code']['sha256']==execution['code_sha256']
        assert result['selected_backend']==run['selected_backend']==execution['selected_backend']
        assert digest(folder/'RESULT.json') == execution['worker_result_sha256']
        assert digest(folder/'TASK_INPUT.json') == result['input_sha256']
        assert digest(data_path)==result['evidence_sha256'] and data_path.stat().st_size==result['evidence_bytes']
        assert result['parameters']==data['parameters']==task['parameters']
        assert data['task_id']==result['task_id']==task_id
        assert data['new_eigensolves']==result['new_eigensolves']==0
        for name, pin in data['frozen_state_identities'].items():
            path=ROOT/'frozen'/name/'STATE.npz'
            assert digest(path)==pin['sha256'] and path.stat().st_size==pin['bytes']
        for path in folder.iterdir():
            if path.is_file(): reviewed_files[str(path.relative_to(ROOT))]=digest(path)
        docs[task_id]=data; results[task_id]=result
    for name in [summary_name,'RUN_IDENTITY.json','MANIFEST_INPUT.json']:
        reviewed_files[str((base/name).relative_to(ROOT))]=digest(base/name)
assert set(docs)==set(expected) and len(docs)==55
def sequence(kind, names, method, sector=0):
    out = sorted([d['value'] for d in docs.values() if d['parameters']['kind']==kind and d['parameters']['states']==names and d['parameters']['method']==method and d['parameters']['sector']==sector], key=lambda v:v['order'])
    assert len({v['order'] for v in out})==len(out)
    return out

force_keys=('T_A','T_B','L_O_bar','L_B_bar')
overlap_keys=('left_domain_overlap','right_domain_overlap','normalized_overlap','self_norm_left','self_norm_right')
force=[]
for name in contract['force']['targets']+[contract['force']['control']]:
    records=sequence('force',[name],'balanced'); assert [v['order'] for v in records]==[12,20,28]
    direct=read('frozen/'+name+'/RESULT.json')['operators']['direct']['24']
    increments=[maximum_difference(a,b,force_keys) for a,b in zip(records,records[1:])]
    mismatches=[max(abs(v[k]-direct[k]) for k in ('L_O_bar','L_B_bar')) for v in records]
    for v,e in zip(records,mismatches): near(e,max(v['direct_force_O_abs'],v['direct_force_B_abs']))
    passed=max(increments)<=limits['force_quadrature_abs'] and max(mismatches)<=limits['direct_force_abs']
    assert passed
    authored=next(x for x in author['force'] if x['state']==name)
    assert authored['increments_abs']==increments and authored['max_terminal_direct_force_abs']==max(mismatches) and authored['pass']==passed
    force.append({'state':name,'increments_abs':increments,'direct_force_max_abs':max(mismatches),'selected_direct_force_abs':mismatches[-1],'pass':passed})
overlap=[]
for lo,hi,m in contract['overlap']['failed_edges']+contract['overlap']['controls']:
    records=sequence('overlap',[f'R{lo}_base',f'R{hi}_base'],'resolved',m)
    assert [v['order'] for v in records]==[16,24,32]
    for v in records:
        near(v['normalized_overlap'],(v['left_domain_overlap']+v['right_domain_overlap'])/2/math.sqrt(v['self_norm_left']*v['self_norm_right']))
        near(v['directional_difference_abs'],abs(v['left_domain_overlap']-v['right_domain_overlap']))
        near(v['max_self_norm_error_abs'],max(abs(v['self_norm_left']-1),abs(v['self_norm_right']-1)))
    increments=[maximum_difference(a,b,overlap_keys[:3]) for a,b in zip(records,records[1:])]
    consistency=max(max(v['directional_difference_abs'],v['max_self_norm_error_abs']) for v in records)
    passed=max(increments)<=limits['overlap_increment_abs'] and consistency<=limits['overlap_direction_abs'] and limits['overlap_magnitude_min']<=abs(records[-1]['normalized_overlap'])<=1+limits['overlap_increment_abs']
    assert passed
    authored=next(x for x in author['overlap'] if x['edge']==[lo,hi,m])
    assert authored['audit']['quadrature_increments_abs']==increments and authored['audit']['max_consistency_error_abs']==consistency and authored['audit']['transport_pass']==passed
    overlap.append({'edge':[lo,hi,m],'increments_abs':increments,'consistency_max_abs':consistency,'selected_overlap':records[-1]['normalized_overlap'],'selected_direction_abs':records[-1]['directional_difference_abs'],'pass':passed})
ref_f=sequence('force',['R16_h'],'original'); assert [v['order'] for v in ref_f]==[40,56]
f_delta=maximum_difference(ref_f[-2],ref_f[-1],force_keys)
f_agreement=maximum_difference(ref_f[-1],sequence('force',['R16_h'],'balanced')[-1],force_keys)
assert max(f_delta,f_agreement)<=limits['independent_force_abs']
ref_o=sequence('overlap',['R15_base','R16_base'],'original'); assert [v['order'] for v in ref_o]==[64]
old=next(x for x in read('provenance/C2A_CONTINUATION_AUDIT.json')['rows'] if (x['R_left'],x['R_right'],x['m'])==(15,16,0))['orders']['48']
o_delta=maximum_difference(old,ref_o[-1],overlap_keys)
o_agreement=maximum_difference(ref_o[-1],sequence('overlap',['R15_base','R16_base'],'resolved')[-1],overlap_keys)
assert max(o_delta,o_agreement,ref_o[-1]['directional_difference_abs'],ref_o[-1]['max_self_norm_error_abs'])<=limits['overlap_independent_abs']
parity=[]
for task_id,d in docs.items():
    p=d['parameters']
    if not p['method'].endswith('_python'):continue
    native=next(v for v in sequence(p['kind'],p['states'],p['method'].replace('_python',''),p['sector']) if v['order']==p['order'])
    difference=maximum_difference(native,d['value'],force_keys if p['kind']=='force' else overlap_keys)
    assert difference<=limits['native_python_abs'];parity.append({'task_id':task_id,'max_abs':difference})
assert len(parity)==4 and author['all_registered_integration_gates_pass'] is True and not author['registered_fallback_needed']
counts=collections.Counter((d['parameters']['kind'],d['parameters']['method']) for d in docs.values())
anomaly=read('provenance/EXECUTION_ANOMALY.json')
assert len(anomaly['incomplete_started_tasks'])==3
assert counts[('force','balanced')]==27<=contract['operational_limits']['force_new_method_evaluations_max']
assert counts[('overlap','resolved')]+3==24<=contract['operational_limits']['overlap_new_method_edge_orders_max']
assert counts[('force','original')]==2<=contract['operational_limits']['force_original_reference_evaluations_max']
assert counts[('overlap','original')]==1<=contract['operational_limits']['overlap_original_reference_evaluations_max']
pref=read('evidence/REMAINDER_PREFLIGHT.json'); assert pref['layout']['workers']==1 and pref['layout']['maximum_workers_from_memory']>=1
assert max(r['elapsed_seconds'] for r in results.values())<contract['operational_limits']['per_task_wall_seconds']
assert max(r['max_rss_kib'] for r in results.values())*1024<contract['operational_limits']['per_worker_address_space_gib']*2**30
grid=read('evidence/RECONCILED_GRID.json'); oldgrid=read('provenance/C2A_GRID_AUDIT.json')
assert len(grid['rows'])==7 and grid['all_pointwise_gates_pass'] and not grid['full_C2_closed']
for row,prior in zip(grid['rows'],oldgrid['rows']):
    assert row['R']==prior['R'] and row['pass'] and not row['failed_gates']
    for key in ('energies','direct','refinements','scaled_diagnostics'):
        assert row[key]==prior[key]
    if row['R'] in (8.,16.):
        for kind in ('base','h','p','tail'):
            selected=sequence('force',[f"R{row['R']:g}_{kind}"],'balanced')[-1]
            checks=row['configuration_checks'][kind]
            assert checks['direct_torque_O_abs']==selected['direct_force_O_abs']
            assert checks['direct_torque_B_abs']==selected['direct_force_B_abs']
            independent=next(x for x in force if x['state']==f"R{row['R']:g}_{kind}")
            assert checks['force_quadrature_max_abs']==max(independent['increments_abs'])
            for key,value in checks.items():
                if key not in ('direct_torque_O_abs','direct_torque_B_abs','force_quadrature_max_abs'):
                    assert value==prior['configuration_checks'][kind][key]
        assert row['original_failed_gates']==prior['failed_gates']
    else:
        assert row['configuration_checks']==prior['configuration_checks']
chain=read('evidence/RECONCILED_CONTINUATION.json'); oldchain=read('provenance/C2A_CONTINUATION_AUDIT.json')
assert chain['edge_count']==34 and len(chain['rows'])==34 and chain['status']=='PASS_FIXED_M_CONTINUATION'
assert chain['C2b_recomputed_edges']==7 and chain['reused_C2a_edges']==27
phases={0:1,1:1}; seen=set(); min_overlap=1.
for row,prior in zip(chain['rows'],oldchain['rows']):
    key=(row['R_left'],row['R_right'],row['m']); assert key==(prior['R_left'],prior['R_right'],prior['m']) and key not in seen; seen.add(key)
    new=next((v for v in author['overlap'] if v['edge']==list(key)),None)
    if new:
        assert row['normalized_overlap']==new['selected']['normalized_overlap'] and row['audit']==new['audit']
    else:
        high=prior['orders'][str(max(map(int,prior['orders'])))]; assert row['normalized_overlap']==high['normalized_overlap'] and row['audit']==prior['audit']
    assert row['audit']['transport_pass'] and row['phase_left']==phases[row['m']]
    phases[row['m']]*=row['audit']['phase_factor']; assert row['phase_right']==phases[row['m']]
    near(row['transported_overlap'],row['phase_left']*row['phase_right']*row['normalized_overlap'])
    assert row['transported_overlap']>=.5; min_overlap=min(min_overlap,row['transported_overlap'])
assert chain['terminal_phase']=={str(k):v for k,v in phases.items()}
assert not chain['hidden_crossing_certificate'] and chain['rank5_cluster']=='NOT_VERIFIED'
complete_wall_sum=sum(json.loads((ROOT/'evidence'/batch/task_id/'TASK_EXECUTION.json').read_bytes())['wall_seconds'] for batch in ('MAIN_MPI','MAIN_REMAINDER_MPI') for task_id in docs if (ROOT/'evidence'/batch/task_id/'TASK_EXECUTION.json').exists())
wall_upper_bound=complete_wall_sum+3*contract['operational_limits']['per_task_wall_seconds']
assert wall_upper_bound < contract['operational_limits']['total_active_science_wall_seconds']
out={'status':'INDEPENDENT_SCALAR_AND_IDENTITY_CHECK_PASS','execution_compliance':'INITIAL_PREFLIGHT_CONTROL_DEVIATION_PRESERVED; RECOVERY_LAYOUT_PREFLIGHT_PASS','science_scope':'empirical frozen-state integration only','new_eigensolves':0,'complete_unique_tasks':55,'interrupted_extra_overlap_attempts':3,'source_changes_since_execution':source_changes,'force':force,'overlap':overlap,'independent_force':{'increment_abs':f_delta,'agreement_abs':f_agreement},'independent_overlap':{'increment_abs':o_delta,'agreement_abs':o_agreement},'native_python_parity':parity,'task_counts':{k[0]+':'+k[1]:v for k,v in counts.items()},'max_completed_task_seconds':max(r['elapsed_seconds'] for r in results.values()),'max_completed_rss_kib':max(r['max_rss_kib'] for r in results.values()),'read_only_scalar_audit_no_scientific_evaluation':True,'files':reviewed_files}
out['merged_evidence']={'pointwise_pass_count':7,'continuation_pass_count':34,'new_continuation_edges':7,'reused_continuation_edges':27,'minimum_transported_overlap':min_overlap,'terminal_phase':phases,'full_C2_closed':False}
out['active_science_wall_bound']={'complete_task_wall_sum_seconds':complete_wall_sum,'incomplete_attempts_cap_seconds':720,'conservative_upper_bound_seconds':wall_upper_bound,'contract_cap_seconds':1800,'parallelism_not_used_to_shrink_bound':True}
print(json.dumps(out,sort_keys=True,indent=2))
