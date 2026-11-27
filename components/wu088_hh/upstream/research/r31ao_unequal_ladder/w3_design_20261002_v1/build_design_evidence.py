"""Exact arithmetic readback and future grid design; never launches a solver."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json

HERE=Path(__file__).resolve().parent
W1=HERE.parent/'w1_parallel_20261002_v1'
def load(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,o):
    with (HERE/name).open('x') as f: json.dump(o,f,indent=2,sort_keys=True); f.write('\n')
def ref(p,ns='continuation'):
    return {'namespace':ns,'path':str(p.relative_to(HERE if ns=='continuation' else W1)),'sha256':sha(p)}
def pow2(n): return Q(1<<n) if n>=0 else Q(1,1<<-n)

def main():
    selection=load(HERE/'runtime/SELECTION_RESULT.json')
    cross=load(HERE/'runtime/CROSSCHECK_RESULT.json')
    if selection['selected_upper_exponent']!=40: raise ValueError('unexpected selected design')
    chosen=next(x for x in selection['candidates'] if x['upper_exponent']==40)
    conservative=max(Q(chosen['combined_radius']),Q(cross['endpoint_radius']))
    old=Q(selection['baseline_endpoint_radius']); budget=Q(selection['endpoint_budget'])
    if not conservative<=budget<old: raise ValueError('accuracy-preserving design not established')
    prepared=load(W1/'runtime/W1_CAMPAIGN/PREPARED.json')
    collected=load(W1/'runtime/W1_CAMPAIGN/COLLECTED.json')
    grid=prepared['grid']
    if grid['log2_t_axis']!=[-4,-1,2,5,8] or grid['log2_u_axis']!=grid['log2_t_axis']:
        raise ValueError('unexpected existing W1 geometry')
    if collected['status']!='COMPLETE_COMPACT_INTERIOR_RADIUS_MET' or collected['tile_count']!=16:
        raise ValueError('W1 collection not accepted')
    axis=[-9,-6,*grid['log2_t_axis'],*range(11,40,3),40]
    if axis!=sorted(set(axis)) or max(b-a for a,b in zip(axis,axis[1:]))>3:
        raise ValueError('axis does not exactly partition selected interval')
    old_cells={tuple(t['window'][k] for k in ('l_t','T_t','l_u','T_u')):t['tile_id'] for t in grid['tiles']}
    cells=[]; retained=[]; area=Q(0)
    for a,b in zip(axis,axis[1:]):
        for c,d in zip(axis,axis[1:]):
            w={'l_t':str(pow2(a)),'T_t':str(pow2(b)),'l_u':str(pow2(c)),'T_u':str(pow2(d))}
            old_id=old_cells.get(tuple(w[k] for k in ('l_t','T_t','l_u','T_u')))
            if old_id is not None: retained.append(old_id)
            cells.append({'cell_id':len(cells),'log2_window':{'l_t':a,'T_t':b,'l_u':c,'T_u':d},'window':w,'existing_W1_tile_id':old_id,'status':'GEOMETRY_ONLY_REUSE_REQUIRES_REBINDING' if old_id is not None else 'NOT_EXECUTED'})
            area+=(pow2(b)-pow2(a))*(pow2(d)-pow2(c))
    if len(cells)!=289 or sorted(retained)!=list(range(16)) or area!=(pow2(40)-pow2(-9))**2:
        raise ValueError('exact Cartesian coverage/reuse check failed')
    future_new=len(cells)-len(retained)
    old_radius=max(Q(v) for v in collected['component_radius'].values())
    future_cap=old_radius+future_new*pow2(-57)
    if future_cap>pow2(-48): raise ValueError('proposed future radius accounting failed')
    put('FUTURE_INTERIOR_DESIGN.json',{
        'schema':'WU088_W3_CUTOFF_INTERIOR_GEOMETRY_PROPOSAL_V1','status':'GEOMETRY_AND_CONDITIONAL_BUDGET_ONLY_NOT_EXECUTABLE_COLLECTOR_PLAN',
        'primitive_index':0,'precision_bits':128,'global_window':cross['window'],'log2_t_axis':axis,'log2_u_axis':axis,'max_log_step':3,
        'tile_count':len(cells),'exact_existing_W1_cells':len(retained),'new_cells_not_executed':future_new,'cells':cells,
        'prior_W3_uniform_step3_tile_count':4489,'tile_count_reduction_fraction':str(Q(4489-len(cells),4489)),
        'tile_count_ratio_old_to_new':str(Q(4489,len(cells))),'measured_runtime_speedup':None,
        'boundaries':'Cartesian cells share measure-zero boundaries; interiors disjoint; adjacent exact dyadic endpoints cover rectangle.',
        'exact_area':str(area),'retained_W1_ids':sorted(retained),
        'conditional_future_radius_allocation':{'component_global_radius_exp':-48,'new_cell_radius_exp':-57,'existing_W1_max_component_radius':str(old_radius),'sum_if_every_new_cell_accepted':str(future_cap),'satisfies_component_budget_exactly':True,'final_D_budget_established':False},
        'reuse_gate':'New source-bound collector must explicitly verify unchanged primitive/input/backend/windows and bind old accepted records into new coverage. Geometry matching alone is not reuse admission.',
        'evidence':[ref(W1/'runtime/W1_CAMPAIGN/PREPARED.json','prior'),ref(W1/'runtime/W1_CAMPAIGN/COLLECTED.json','prior'),ref(HERE/'runtime/CROSSCHECK_PLAN.json'),ref(HERE/'runtime/CROSSCHECK_RESULT.json')],
        'native_invocations':0,'scientific_admission':False,'production_admission':False})
    put('MEASUREMENTS.json',{
        'schema':'WU088_W3_DESIGN_MEASUREMENTS_V1','selected_window':cross['window'],'primitive_index':0,'precision_bits':128,
        'baseline_endpoint_radius':str(old),'endpoint_budget':str(budget),'selected_polynomial_radius':chosen['combined_radius'],'existing_engine_radius':cross['endpoint_radius'],
        'conservative_endpoint_radius':str(conservative),'conservative_endpoint_radius_decimal_display_only':format(float(conservative),'.16e'),
        'conservative_policy':'max(selector,existing_engine); different upward rounding stages need not order the two reported bounds',
        'crosscheck_minus_selector':str(Q(cross['endpoint_radius'])-Q(chosen['combined_radius'])),
        'baseline_to_new_bound_ratio_exact':str(old/conservative),'baseline_to_new_bound_ratio_decimal_display_only':float(old/conservative),
        'lower_radius':selection['lower_radius'],'candidates':selection['candidates'],'selected_is_first_tested_passing_not_global_optimum':True,
        'new_bound_le_budget_lt_old_bound_exact':True,'engine_calls':{'selection':selection['engine_calls'],'crosscheck':cross['engine_calls']},
        'native_integrations':0,'actual_endpoint_workers':2,'candidate_polynomial_evaluations':5,'old_W1_or_W3_recomputed':False,
        'endpoint_evidence_scope':'Primitive0 unnormalized positive-domain omitted mass only; same frozen signed107 source, no full interior or finalDcertificate.',
        'lower_engine_quantizer':'Pinned exp_neg_bounds uses absolute 128-bit quantization; no relative exp accuracy claim.',
        'scientific_admission':False,'production_admission':False})
    records=[]
    fields=('record_id','kind','primitive_index','accepted','status','actual_worker_observed','native_integration_invocations','candidate_polynomial_evaluations')
    for name in ('SELECTION','CROSSCHECK'):
        p=HERE/'runtime'/(name+'_RECEIPT.json');r=load(p)
        records.append({**{k:r[k] for k in fields},'receipt':ref(p)})
    put('EXECUTION_LEDGER.json',{
        'schema':'WU088_W3_DESIGN_EXECUTION_LEDGER_V1','base_commit':'b7e90411a155ce230d025871fc18e87e99fd9974',
        'original_prompt_sha256':'70071962a6b3dc3cfc0c01034c0d1b6f57711833957510a77b0bb6c4e453969e',
        'prior_database_sha256':'a27bc17b9406f5fe558376e552381a08fdfe836fdd3ed362d83ad26ae7572ce6','records':records,'host_events':[],
        'counts':{'actual_endpoint_selections':1,'actual_endpoint_crosschecks':1,'accepted_current_endpoint_records':2,'rejected_current_endpoint_records':0,'native_integration_invocations':0,'candidate_polynomial_evaluations':5,'host_events_not_invocations':0},
        'scientific_admission':False,'production_admission':False})
    print(json.dumps({'endpoint_bound':str(conservative),'tiles':len(cells),'preserved_W1':len(retained),'unexecuted_cells':future_new}))

if __name__=='__main__': main()
