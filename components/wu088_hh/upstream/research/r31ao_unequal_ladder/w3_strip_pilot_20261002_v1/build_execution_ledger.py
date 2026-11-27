"""Source references for this completed pilot; no solver or endpoint execution."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
LADDER=HERE.parent
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    with p.open('x')as f:json.dump(o,f,indent=2,sort_keys=True);f.write('\n')
def ref(p,ns='continuation'):
    return {'namespace':ns,'path':str(p.relative_to(HERE if ns=='continuation'else LADDER)),'sha256':sha(p)}

def main():
    runtime=HERE/'runtime';session=read(runtime/'SESSION_RESULT.json');coverage=read(runtime/'COVERAGE.json')
    if session['status']!='PILOT_COMPLETE' or session['accepted_new_cells']!=4 or coverage['accepted_cell_count']!=20 or len(coverage['missing_cell_ids'])!=269:
        raise ValueError('this delivery ledger requires the actual completed four-cell pilot')
    directory=runtime/'ledger_wrappers';directory.mkdir(exist_ok=False);records=[]
    fields=('record_id','kind','tile_id','primitive_index','accepted','status','actual_worker_observed','native_integration_invocations','candidate_polynomial_evaluations')
    for n in read(runtime/'REUSED_W1.json'):
        origin=n['origin'];old=origin['old_W1_tile_id'];raw=Path(origin['receipt_path']);r=read(raw)
        if sha(raw)!=n['native_receipt_sha256'] or r['status']!='RADIUS_MET' or not r['accepted']:raise ValueError('historical receipt changed')
        wrapper={'schema':'WU088_W3_STRIP_LEDGER_WRAPPER_V1','record_id':f'REUSED_W1_{old:02d}',
            'kind':'REUSED_ACCEPTED_W1_TILE','tile_id':f'{old:02d}','mapped_new_cell_id':n['cell_id'],'primitive_index':0,
            'accepted':True,'status':r['status'],'actual_worker_observed':False,'native_integration_invocations':0,'candidate_polynomial_evaluations':0,
            'output':ref(raw,'inherited'),'rebound_records':ref(runtime/'REUSED_W1.json'),'normalized_record_sha256':n['record_sha256'],
            'original_requested_radius_exp':-52,'required_actual_radius_exp':-57,'original_time_execution_reused':True,'new_global_plan_sha256':n['global_plan_sha256'],
            'scientific_admission':False,'production_admission':False}
        p=directory/f'REUSED_W1_{old:02d}.json';write(p,wrapper);records.append({**{k:wrapper[k]for k in fields},'receipt':ref(p)})
    for result in session['returns']:
        cell=result['cell_id'];p_raw=runtime/'raw'/f'{cell:03d}.json';r=read(p_raw)
        if not result['accepted'] or result['worker_returncode']!=0 or result['native_receipt']!=ref(p_raw) or r['wrapper']['native_execution_observed']is not True:
            raise ValueError('current successful source-bound native execution required')
        wrapper={'schema':'WU088_W3_STRIP_LEDGER_WRAPPER_V1','record_id':f'ACTUAL_PILOT_{cell:03d}',
            'kind':'ACTUAL_NATIVE_PILOT','tile_id':str(cell),'primitive_index':0,'accepted':True,'status':r['status'],
            'actual_worker_observed':True,'native_integration_invocations':1,'candidate_polynomial_evaluations':0,
            'output':ref(p_raw),'terminal_return':ref(runtime/'attempts'/f'{cell:03d}'/'RETURN.json'),
            'normalized':ref(runtime/'normalized'/f'{cell:03d}.json'),'worker_pid':result['worker_pid'],
            'native_elapsed_wall_ns':r['wrapper']['elapsed_wall_ns'],'native_nested_integration_calls':r['integration_calls'],
            'native_dispatched_evaluations':r['dispatched_evaluations'],'source_bound_stdout':ref(Path(str(p_raw)+'.stdout')),
            'scientific_admission':False,'production_admission':False}
        p=directory/f'ACTUAL_PILOT_{cell:03d}.json';write(p,wrapper);records.append({**{k:wrapper[k]for k in fields},'receipt':ref(p)})
    events=read(HERE/'HOST_EVENTS.json')['events']
    out={'schema':'WU088_W3_STRIP_EXECUTION_LEDGER_V1','base_commit':'48443cd754329cd6b76c99f6e9e887081df1e29e',
        'original_prompt_sha256':'70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e',
        'prior_database_sha256':'73558531543754826eaf7cfe27f6960a055ac17a865509de469f148d3ab84e7c',
        'records':records,'host_events':events,'counts':{'native_dispatch_attempts':4,'observed_native_integrations':4,
            'accepted_current_pilots':4,'rejected_current_pilots':0,'reused_W1_tiles':16,'candidate_polynomial_evaluations':0,'host_events_not_invocations':len(events)},
        'scientific_admission':False,'production_admission':False}
    write(HERE/'EXECUTION_LEDGER.json',out);print(json.dumps(out['counts']))

if __name__=='__main__':main()
