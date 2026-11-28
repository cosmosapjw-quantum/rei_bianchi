"""Compose immutable C2a evidence with C2b integration repairs; no physical solves."""
import copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from mpi_batch import atomic_create,json_bytes

def read(rel): return json.loads((ROOT/rel).read_text())
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def write(rel,data): atomic_create(ROOT/rel,json_bytes(data))

def main():
    a=read('evidence/INITIAL_AUDIT.json')
    assert a['all_registered_integration_gates_pass']
    parent=read('provenance/C2A_GRID_AUDIT.json')
    criteria=read('provenance/C2A_CONTRACT.json')['criteria']
    force={x['state']:x for x in a['force']}
    rows=copy.deepcopy(parent['rows'])
    for row in rows:
        row['evidence_origin']='unchanged C2a PASS'
        if row['R'] not in (8,16):
            assert row['pass']
            continue
        row['evidence_origin']='C2a state/direct/spatial evidence + C2b force integration'
        row['original_failed_gates']=list(row['failed_gates'])
        row['force_repair_paths']={}
        for config in ('base','h','p','tail'):
            repair=force[f'R{row["R"]:g}_{config}']; selected=repair['selected']
            check=row['configuration_checks'][config]
            check['force_quadrature_max_abs']=max(repair['increments_abs'])
            check['direct_torque_O_abs']=selected['direct_force_O_abs']
            check['direct_torque_B_abs']=selected['direct_force_B_abs']
            row['force_repair_paths'][config]=repair['data_paths']
            row['gates'][config+'_operators']=(repair['max_terminal_direct_force_abs']<=criteria['direct_torque_abs']
                and check['momentum_commutator_abs']<=criteria['momentum_gap_dipole_abs']
                and check['origin_identity_abs']<=criteria['origin_identity_abs'])
            row['gates'][config+'_quadrature']=max(check['direct_quadrature_max_abs'],
                check['force_quadrature_max_abs'])<=criteria['operator_quadrature_abs']
            if config=='base':
                row['invariants']['direct_torque_O_abs']=selected['direct_force_O_abs']
                row['invariants']['direct_torque_B_abs']=selected['direct_force_B_abs']
        row['pass']=all(row['gates'].values())
        row['failed_gates']=[k for k,v in row['gates'].items() if not v]
    grid={'scope':'same seven registered finite R points only','rows':rows,
          'all_pointwise_gates_pass':all(x['pass'] for x in rows),
          'input_sha256':{'provenance/C2A_GRID_AUDIT.json':sha('provenance/C2A_GRID_AUDIT.json'),
                          'evidence/INITIAL_AUDIT.json':sha('evidence/INITIAL_AUDIT.json')},
          'parent_failures_preserved':True,'new_eigensolves':0,'continuum_certificate':False,
          'full_C2_closed':False}
    write('evidence/RECONCILED_GRID.json',grid)

    old=read('provenance/C2A_CONTINUATION_AUDIT.json')
    replacements={tuple(x['edge']):x for x in a['overlap']}
    phases={0:1,1:1}; chain=[]
    for original in sorted(old['rows'],key=lambda x:(x['R_left'],x['m'])):
        key=(original['R_left'],original['R_right'],original['m']);m=key[2]
        if key in replacements:
            repair=replacements[key];audit=repair['audit'];selected=repair['selected']
            source='C2b resolved coordinates';paths=repair['data_paths']
        else:
            audit=original['audit'];selected=original['orders'][str(max(map(int,original['orders'])))];
            source='unchanged C2a passed local edge';paths=['provenance/C2A_CONTINUATION_AUDIT.json']
        assert audit['transport_pass']
        left=phases[m]; right=left*audit['phase_factor'];phases[m]=right
        chain.append({'R_left':key[0],'R_right':key[1],'m':m,'evidence_origin':source,
            'source_paths':paths,'audit':audit,'selected_order':selected['order'],
            'normalized_overlap':selected['normalized_overlap'],'phase_left':left,'phase_right':right,
            'transported_overlap':left*right*selected['normalized_overlap'],
            'phase_applied_to':'coefficient multiplier only; archived states immutable'})
    assert len(chain)==34 and all(x['transported_overlap']>=.5 for x in chain)
    continuation={'status':'PASS_FIXED_M_CONTINUATION','rows':chain,
        'edge_count':len(chain),'reused_C2a_edges':len(chain)-len(replacements),
        'C2b_recomputed_edges':len(replacements),'terminal_phase':phases,
        'state_sha256':old['state_sha256'],'new_eigensolves':0,
        'rank5_cluster':'NOT_VERIFIED','hidden_crossing_certificate':False,
        'input_sha256':{'provenance/C2A_CONTINUATION_AUDIT.json':sha('provenance/C2A_CONTINUATION_AUDIT.json'),
                        'evidence/INITIAL_AUDIT.json':sha('evidence/INITIAL_AUDIT.json')},
        'claim_scope':'34 local overlaps on 18 points of two lowest fixed-m branches; no global-R spectral certification'}
    write('evidence/RECONCILED_CONTINUATION.json',continuation)

    records=[]
    for batch,summary in [('MAIN_MPI','RECOVERY_ACCEPTED_TASKS.json'),('MAIN_REMAINDER_MPI','BATCH_SUMMARY.json')]:
        for task in read(f'evidence/{batch}/{summary}')['tasks']:
            folder=f'evidence/{batch}/'+task['task_id'];r=read(folder+'/RESULT.json');d=read(folder+'/DATA.json')
            records.append({'task_id':r['task_id'],'parameters':d['parameters'],
                'elapsed_seconds':r['elapsed_seconds'],'max_rss_kib':r['max_rss_kib'],
                'data_path':folder+'/DATA.json','data_sha256':sha(folder+'/DATA.json'),
                'source_identity':r['code_identity_sha256']})
    assert len(records)==55 and len({x['task_id'] for x in records})==55
    budget={'new_eigensolves':0,'completed_original_tasks':55,'incomplete_preserved_attempts':3,
        'force_new_method_evaluations':27,'force_original_reference_evaluations':2,
        'overlap_new_method_edge_orders_completed':21,'overlap_new_method_attempts_including_interrupted':24,
        'overlap_original_reference_evaluations':1,'native_python_parity_evaluations':4,
        'fallback_evaluations':0,'warm_timing_repeats':0,'mpi_layout_replay_evaluations':0,
        'mpi_layout_replay_status':'NOT_RUN_RESOURCE_PREFLIGHT; optional preflight failed before launch',
        'initial_launch_resource_policy':'NONCOMPLIANT; stopped, partial numerics identity-verified',
        'remainder_launch_resource_policy':'PREFLIGHT_PASS; ranks2/workers1/threads1, local binding none',
        'completed_task_max_seconds':max(x['elapsed_seconds'] for x in records),
        'completed_task_sum_seconds':sum(x['elapsed_seconds'] for x in records),
        'completed_task_max_rss_kib':max(x['max_rss_kib'] for x in records),
        'remainder_batch_wall_seconds':read('evidence/MAIN_REMAINDER_MPI/BATCH_SUMMARY.json')['wall_seconds'],
        'science_wall_bound_seconds':1800,
        'initial_attempt_wall_upper_bound_seconds':165,
        'total_active_batch_wall_upper_bound_seconds':165+read('evidence/MAIN_REMAINDER_MPI/BATCH_SUMMARY.json')['wall_seconds'],
        'initial_upper_bound_basis':'EXECUTION_SCOPE start11:07:41.556Z to recovery record11:10:25.454Z; includes recovery overhead',
        'NCP64_actual_scaling':'NOT_RUN','same_workload_speedup_claim':False,
        'all_records':records}
    write('evidence/EXECUTION_ACCOUNTING.json',budget)
    print(json.dumps({'grid_pass':grid['all_pointwise_gates_pass'],'edges':len(chain),
        'force_increment_max':max(max(x['increments_abs']) for x in a['force']),
        'overlap_increment_max':max(max(x['audit']['quadrature_increments_abs']) for x in a['overlap']),
        'max_rss_kib':budget['completed_task_max_rss_kib']}))

if __name__=='__main__':main()
