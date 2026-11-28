"""Independent stdlib-only receipt/arithmetic readback; no endpoint engine import."""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json

HERE=Path(__file__).resolve().parent
NEW=HERE.parent
LADDER=NEW.parent
PRIOR=LADDER/'production_solver_20261001_v1'
CHECKS=[]

def check(condition,label):
    if not condition: raise ValueError(label)
    CHECKS.append(label)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out: raise ValueError('duplicate JSON key')
            out[key]=value
        return out
    return json.loads(path.read_bytes(),object_pairs_hook=pairs)

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')

def sealed(obj,key):
    check(hashlib.sha256(canonical({k:v for k,v in obj.items() if k!=key})).hexdigest()==obj[key],key+' canonical identity')

def ceil128(q):
    """Positive dyadic ceiling via an independently formed Fraction grid."""
    q=F(q)
    check(q>=0,'nonnegative quantity')
    if q==0:return q
    e=q.numerator.bit_length()-q.denominator.bit_length()
    power=F(2)**e
    while power>q:e-=1;power/=2
    while power*2<=q:e+=1;power*=2
    quantum=F(2)**(e-127)
    scaled=q/quantum
    answer=((scaled.numerator+scaled.denominator-1)//scaled.denominator)*quantum
    check(answer>=q and answer<q*(1+F(1,2**127)),'outward grid error')
    return answer

def main():
    selection=read(NEW/'runtime/SELECTION_RESULT.json')
    cross=read(NEW/'runtime/CROSSCHECK_RESULT.json')
    plan=read(NEW/'runtime/CROSSCHECK_PLAN.json')
    baseline=read(PRIOR/'runtime/endpoint_cutoff_probe_capped/W3_RESULT.json')
    oldplan=read(PRIOR/'runtime/endpoint_cutoff_probe_capped/W3_PLAN.json')
    for obj in [selection,cross,baseline]:sealed(obj,'result_sha256')
    for obj in [plan,oldplan]:sealed(obj,'plan_sha256')
    check(sha(NEW/'runtime/SELECTION_RESULT.json')=='04e629adf75a5a051571e429b80dbec8edc6cfb90e48bfdee9e34d8fd45a10b7','selection expected bytes')
    check(sha(NEW/'runtime/CROSSCHECK_RESULT.json')=='1114701c5c1a8da61dca99f70d22e1c73df2306dea55986010f2509ced5ad760','crosscheck expected bytes')
    check(selection['selector_source_sha256']==sha(NEW/'tail_bound/select_cutoff.py'),'selector source binding')
    for relative,identity in selection['source_identities'].items():
        path=PRIOR/relative
        check(sha(path)==identity['sha256'] and path.stat().st_size==identity['bytes'],'source bytes '+relative)
    for relative,digest in selection['source_hashes'].items():
        root=PRIOR if relative=='endpoint_tasks/planner.py' else LADDER/'gap_closure_20261001_g0_g6_v1'
        check(sha(root/relative)==digest,'transitive source '+relative)
    for key in ['archive_sha256','input_record_sha256']:
        check(selection[key]==cross[key]==baseline[key]==plan[key]==oldplan[key],'common '+key)
    check(selection['baseline_plan_sha256']==oldplan['plan_sha256'] and selection['baseline_result_sha256']==baseline['result_sha256'],'baseline semantic identities')
    check(selection['baseline_endpoint_radius']==baseline['endpoint_radius'],'baseline exact radius')
    check(plan['terms']==oldplan['terms'],'new plan preserves original signed term list')
    check(plan['input_record']==oldplan['input_record'],'new plan preserves original canonical input record')
    check(len(plan['tasks'])==len(oldplan['tasks'])==2592,'canonical task plan count')
    for left,right in zip(plan['tasks'],oldplan['tasks']):
        for key in ['index','indices','parameters']:
            check(left[key]==right[key],'task physical parameters '+key)
    check(selection['parameters']==plan['tasks'][0]['parameters'],'selector primitive-zero parameters')
    check(selection['baseline_task_sha256']==oldplan['tasks'][0]['task_sha256'],'baseline primitive-zero identity')
    check(cross['task_sha256']==plan['tasks'][0]['task_sha256'] and cross['plan_sha256']==plan['plan_sha256'],'crosscheck task/plan identity')
    check(selection['primitive_index']==cross['index']==0,'primitive zero only')
    check(selection['precision_bits']==plan['precision_bits']==128,'precision unchanged')
    check(selection['lower_cutoffs']=={'l_t':'1/512','l_u':'1/512'},'fixed lower endpoints')
    budget=F(selection['endpoint_budget'])
    check(budget==F(1,2**21) and budget<F(baseline['endpoint_radius']),'strict old-radius budget comparison')
    check(selection['term_count']==len(selection['terms'])==len(cross['terms'])==len(plan['terms'])==107,'107 ordered term coverage')
    lower=F(0);coefficients={};cross_total=F(0);density_maps={};mass_maps={}
    for original,row,oldproof,proof in zip(plan['terms'],selection['terms'],baseline['terms'],cross['terms']):
        for key in ['i','j','k']:
            check(original[key]==row[key]==oldproof[key]==proof[key],'term index order '+key)
        check(row['coefficient']==original['coefficient'],'signed coefficient retained')
        c=abs(F(original['coefficient']));C=F(row['C_F'])
        check(F(row['c_abs'])==c==F(proof['coefficient_abs']),'absolute coefficient bound')
        check(C==F(oldproof['field_majorant'])==F(proof['field_majorant']),'same original field majorant')
        factor=ceil128(c*C)
        lt,wt,lu,wu=[F(row[k]) for k in ['L_t','W_t','L_u','W_u']]
        for which,index,L,W in [('t',row['i'],lt,wt),('u',row['j'],lu,wu)]:
            key=(which,index)
            if key in mass_maps:check(mass_maps[key]==(L,W),'invocation-local mass consistency')
            mass_maps[key]=(L,W)
        left={int(k):F(v) for k,v in row['U_t'].items()}
        right={int(k):F(v) for k,v in row['U_u'].items()}
        for index,mapping in [(row['i'],left),(row['j'],right)]:
            expected={index+2-r for r in range((index+1)//2+1)}
            check(set(mapping)==expected and all(v>=0 for v in mapping.values()),'density polynomial source exponents')
            if index in density_maps:check(density_maps[index]==mapping,'same density coefficient map')
            density_maps[index]=mapping
        value=ceil128(factor*ceil128(lt*wu+wt*lu))
        check(value==F(row['lower_contribution']),'lower contribution reconstruction')
        lower=ceil128(lower+value)
        powers=sorted(set(left)|set(right))
        check(set(map(int,row['upper_coefficients']))==set(powers),'per-term upper power coverage')
        for power in powers:
            value=ceil128(factor*ceil128(left.get(power,F(0))*wu+wt*right.get(power,F(0))))
            check(value==F(row['upper_coefficients'][str(power)]),'upper contribution reconstruction')
            coefficients[power]=ceil128(coefficients.get(power,F(0))+value)
        cross_term=ceil128(c*C*F(proof['complement_mass_bound']))
        check(cross_term==F(proof['contribution']),'original-engine term arithmetic')
        cross_total=ceil128(cross_total+cross_term)
    check(lower==F(selection['lower_radius']),'aggregate lower radius')
    check(coefficients=={int(k):F(v) for k,v in selection['upper_coefficients'].items()},'aggregate positive polynomial')
    check(cross_total==F(cross['endpoint_radius']),'original-engine ordered radius sum')
    check([x['upper_exponent'] for x in selection['candidates']]==[32,40,48,56,64],'five fixed candidate exponents')
    previous=None;first=None
    for row in selection['candidates']:
        exponent=row['upper_exponent'];T=F(2**exponent)
        check(F(row['T'])==T,'exact candidate T')
        upper=F(0)
        for power in sorted(coefficients):upper=ceil128(upper+ceil128(coefficients[power]/T**power))
        combined=ceil128(lower+upper)
        check(upper==F(row['upper_radius']) and combined==F(row['combined_radius']),'candidate exact reconstruction')
        check(row['meets_endpoint_budget']==(combined<=budget),'candidate exact predicate')
        if previous is not None:check(combined<=previous,'candidate monotonicity')
        previous=combined
        if combined<=budget and first is None:first=exponent
    check(first==selection['selected_upper_exponent']==40,'first tested passing cutoff')
    check(selection['selection_is_global_optimum'] is False,'no global optimum claim')
    selected=next(x for x in selection['candidates'] if x['upper_exponent']==first)
    selected_radius=F(selected['combined_radius'])
    check(cross_total<=budget and selected_radius<=budget,'both actual bounds meet fixed budget')
    check(plan['window']=={'l_t':'1/512','l_u':'1/512','T_t':str(2**40),'T_u':str(2**40)},'crosscheck selected identical window')
    check(plan['caps']['memory_bytes']==512*1024**2 and plan['caps']['wall_seconds']==30,'crosscheck plan hard limits')
    check(selection['native_integrations']==selection['hh_callback_evaluations']==selection['archived_B192_recomputations']==0,'zero native/callback/archive recomputation counters')
    receipt_hashes={}
    for phase,cap,result in [('SELECTION',60,selection),('CROSSCHECK',30,cross)]:
        receipt_path=NEW/f'runtime/{phase}_RECEIPT.json';receipt=read(receipt_path)
        start=read(NEW/f'runtime/{phase}_STARTED.json')
        for name in ['output','started','stdout','stderr']:
            ref=receipt[name]
            check(ref['namespace']=='continuation' and sha(NEW/ref['path'])==ref['sha256'],'receipt reference '+phase+' '+name)
        check(receipt['accepted'] and receipt['actual_worker_observed'] and receipt['returncode']==0 and receipt['wait_completed'],'completed actual worker '+phase)
        check(receipt['timed_out'] is False and receipt['launch_error'] is None,'no timeout/launch failure '+phase)
        check(receipt['wall_seconds']==receipt['cpu_seconds']==cap and receipt['memory_mib']==512,'receipt hard limits '+phase)
        check(receipt['native_integration_invocations']==0 and receipt['NCP_or_MPI_execution'] is False,'no HH/NCP/MPI '+phase)
        check(start['controller_sha256']==sha(NEW/'run_bounded.py'),'controller source '+phase)
        check(start['worker_sha256']==sha(Path(start['command'][2])),'worker source '+phase)
        check(start['host_identity']==receipt['host_identity'],'same pinned host '+phase)
        check(receipt['PDEATHSIG']=='SIGKILL' and receipt['creation_syscalls_denied'] is True,'lifetime guard '+phase)
        check(receipt['elapsed_ns']<cap*10**9,'observed wall below cap '+phase)
        receipt_hashes[phase]=sha(receipt_path)
    retained=max(selected_radius,cross_total)
    improvement=F(baseline['endpoint_radius'])/retained
    result={'schema':'WU088_W3_INDEPENDENT_ACTUAL_READBACK_V1','status':'PASS_SOURCE_BOUND_ENDPOINT_COMPONENT','checks_executed':len(CHECKS),'unique_check_labels':sorted(set(CHECKS)),
      'source_sha256':sha(Path(__file__)),'selection_file_sha256':sha(NEW/'runtime/SELECTION_RESULT.json'),'crosscheck_file_sha256':sha(NEW/'runtime/CROSSCHECK_RESULT.json'),'receipt_sha256':receipt_hashes,
      'selected_T':str(2**40),'selected_lower_cutoff':'1/512','selected_candidate_radius':str(selected_radius),'original_engine_radius':str(cross_total),'retained_conservative_endpoint_radius':str(retained),
      'crosscheck_minus_selector_exact':str(cross_total-selected_radius),'rounding_difference_interpretation':'Different positive upward summation stages; both independently preserve enclosure. Equality or crosscheck<=selector is not required.',
      'prior_radius':baseline['endpoint_radius'],'endpoint_budget':str(budget),'old_to_retained_bound_ratio_exact':str(improvement),'old_to_retained_bound_ratio_decimal_diagnostic':str(float(improvement)),
      'ordered_terms_verified':107,'source_field_majorants_unchanged':True,'candidate_count':5,'selected_first_tested_not_global_optimum':True,
      'reviewer_endpoint_engine_executions':0,'reviewer_HH_integrations':0,'actual_root_endpoint_invocations':2,'actual_native_integrations':0,
      'new_window_interior_integrated':False,'normalization_applied':False,'full_D_epsilon':None,'scientific_admission':False,'production_admission':False,
      'evidence_limit':'Reported engine-generated mass/majorant constants remain conditional on the pinned previously reviewed engine. This readback independently recomputes positive arithmetic and bindings, not physical adequacy or the engine itself.'}
    out=HERE/'ACTUAL_RESULT_REVIEW.json'
    with out.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({key:result[key] for key in ['status','checks_executed','retained_conservative_endpoint_radius','old_to_retained_bound_ratio_decimal_diagnostic']}))

if __name__=='__main__':main()
