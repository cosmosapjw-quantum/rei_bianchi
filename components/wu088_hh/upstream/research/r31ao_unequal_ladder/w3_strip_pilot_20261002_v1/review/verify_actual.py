"""Read-only source/receipt validation and independent exact rectangle summation.

Does not call native run_task, endpoint evaluation, or any scientific callback.
The collector context verifies existing executable/library identities via ldd.
"""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import sys

NEW=Path(__file__).resolve().parent.parent
ROOT=NEW/'runtime'
IDS=[20,52,105,57]
PINS={'pilot_runner.py':'1a0b0b35499d5091fb58415043d3426fcafc257a769cae0e5d0a79f310e46af1',
      'collection/collector.py':'8f5fc994726fbd3ef0daf289278a8ec4ceff20a59278a6a755dd2bc7cadbe50d'}

def require(value,message):
    if not value:raise ValueError(message)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
def selfhash(value,key):require(hashlib.sha256(canonical({k:v for k,v in value.items()if k!=key})).hexdigest()==value[key],key+' mismatch')
def check_ref(ref):require(ref['namespace']=='continuation'and sha(NEW/ref['path'])==ref['sha256'],'evidence reference changed')

def main():
    for name,pin in PINS.items():require(sha(NEW/name)==pin,'implementation changed')
    spec=importlib.util.spec_from_file_location('independent_strip_actual_validator',NEW/'collection/collector.py')
    c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
    context=c.context()
    plan=read(ROOT/'GRID_PLAN.json');prepared=read(ROOT/'PREPARED.json')
    session=read(ROOT/'SESSION_RESULT.json');coverage=read(ROOT/'COVERAGE.json')
    require(c.make_plan(context)==plan,'fresh source-bound grid differs')
    selfhash(prepared,'prepared_sha256');selfhash(coverage,'result_sha256')
    require(prepared['prepared_sha256']==session['prepared_sha256']=='8754c55599db81518438c2a2b72aa5728136ba1bf82fbefb8ef055f421bc5d33','actual prepared identity')
    require(session['status']=='PILOT_COMPLETE' and session['dispatched_cell_ids']==IDS,'fixed pilot completed')
    require(session['native_dispatch_attempts']==4 and session['accepted_new_cells']==4 and session['reused_W1_tiles']==16,'actual execution counts')
    require(session['native_evaluation_cap_charged']==800000,'charged budget')
    check_ref(session['coverage'])
    records=read(ROOT/'REUSED_W1.json')
    require(len(records)==16,'sixteen previously verified W1 records')
    returns={r['cell_id']:r for r in session['returns']}
    require(set(returns)==set(IDS)and len(session['returns'])==4,'exact terminal record coverage')
    evidence=[];claims=[];claim_snapshots=[];evaluations=0;integrations=0;callbacks=0
    for cell in IDS:
        path=ROOT/'raw'/f'{cell:03d}.json'
        norm=c.normalize_new(context,plan,cell,path)
        require(norm==read(ROOT/'normalized'/f'{cell:03d}.json'),'fresh native normalization differs')
        records.append(norm)
        raw=read(path);selfhash(raw,'result_sha256')
        ret=returns[cell]
        require(ret==read(ROOT/'attempts'/f'{cell:03d}'/'RETURN.json'),'session terminal differs')
        require(ret['accepted']and ret['status']=='RADIUS_MET'and ret['worker_returncode']==0 and ret['timed_out']is False and ret['error']is None,'worker not accepted cleanly')
        for key in ['native_receipt','normalized','worker_started_file']:check_ref(ret[key])
        start=read(NEW/ret['worker_started_file']['path'])
        require(start['pid']==ret['worker_pid'] and start['cell_id']==cell and start['prepared_sha256']==prepared['prepared_sha256'],'worker identity')
        dispatch=read(ROOT/'attempts'/f'{cell:03d}'/'DISPATCH.json')
        require(dispatch['cell_id']==cell and dispatch['prepared_sha256']==prepared['prepared_sha256']and dispatch['native_execution_requested']and dispatch['native_evaluation_cap_charged']==200000,'dispatch contract')
        wrapper=raw['wrapper'];host=wrapper['process_host']
        require(host['native_wait_completed']and not host['timed_out']and wrapper['returncode']==0,'native terminal wait')
        require(host['native_descendant_creation']=='SECCOMP_DENY_FORK_VFORK_CLONE_CLONE3' and host['pdeath_signal']=='SIGKILL','native lifetime boundary')
        require(host['cpu_cap_seconds']==host['wall_cap_seconds']==125 and host['memory_mib']==1024,'native hard caps')
        require(raw['dispatched_evaluations']<=200000 and raw['integration_calls']<=1024,'native counters cap')
        require(raw['accepted_component_radius_exp']==-57 and raw['precision_bits']==128 and raw['index']==0 and raw['flint_status']==0,'native numeric contract')
        require(wrapper['elapsed_wall_ns']<=125*10**9 and ret['elapsed_wall_ns']<=180*10**9,'observed elapsed caps')
        radii={}
        for part in ['real','imag']:
            d=raw['rectangle'][part]
            lo=Q(int(d['lower_mantissa']))*Q(2)**int(d['exponent2'])
            hi=Q(int(d['upper_mantissa']))*Q(2)**int(d['exponent2'])
            radius=(hi-lo)/2
            require(norm['rectangle'][part]=={'lower':str(lo),'upper':str(hi)}and Q(norm['reported_radius'][part])==radius and 0<=radius<=Q(2)**-57,'independent dyadic radius')
            radii[part]=str(radius)
        claim=Path(str(path)+'.claim')
        require(ret['root_removed_residual_claim']is False,'root claim preservation policy')
        claim_snapshots.append({'cell_id':cell,'terminal_return_claim_observed':ret['residual_native_claim_observed'],
                                'review_readback_claim_exists':claim.exists(),
                                'observations_differ':ret['residual_native_claim_observed']!=claim.exists()})
        if claim.exists():claims.append({'cell_id':cell,'path':str(claim.relative_to(NEW)),'sha256':sha(claim),'bytes':claim.stat().st_size,'contents_pid_text':claim.read_text(),'root_cause':'UNDETERMINED','removed':False})
        evaluations+=raw['dispatched_evaluations'];integrations+=raw['integration_calls'];callbacks+=raw['callback_calls']
        evidence.append({'cell_id':cell,'raw_sha256':sha(path),'normalized_sha256':sha(ROOT/'normalized'/f'{cell:03d}.json'),
                         'worker_pid':ret['worker_pid'],'native_process_pid':host['native_process_pid'],
                         'dispatched_evaluations':raw['dispatched_evaluations'],'integration_calls':raw['integration_calls'],
                         'callback_calls':raw['callback_calls'],'callback_refusals':raw['callback_refusals'],'analytic_box_refusals':raw['analytic_box_refusals'],
                         'native_elapsed_ns':wrapper['elapsed_wall_ns'],'serialized_component_radius':radii,'residual_claim':claim.exists()})
    # This sum does not invoke the collector: independent exact rational arithmetic.
    seen=set();totals={part:[Q(0),Q(0)]for part in ['real','imag']}
    for record in records:
        selfhash(record,'record_sha256')
        cell=record['cell_id'];require(cell not in seen,'duplicate accepted cell');seen.add(cell)
        require(record['global_plan_sha256']==plan['plan_sha256']and record['window']==plan['cells'][cell]['window'],'accepted exact cell binding')
        for part in totals:
            lo=Q(record['rectangle'][part]['lower']);hi=Q(record['rectangle'][part]['upper'])
            require(0<=hi-lo<=2*Q(2)**-57 and Q(record['reported_radius'][part])==(hi-lo)/2,'accepted exact radius')
            totals[part][0]+=lo;totals[part][1]+=hi
    require(len(seen)==coverage['accepted_cell_count']==20 and coverage['accepted_cell_ids']==sorted(seen),'twenty accepted cells')
    missing=sorted(set(range(289))-seen)
    require(coverage['missing_cell_ids']==missing and len(missing)==269,'269 missing cells')
    for part,(lo,hi)in totals.items():
        require(coverage['rectangle'][part]=={'lower':str(lo),'upper':str(hi)}and Q(coverage['component_radius'][part])==(hi-lo)/2,'exact accepted-union sum')
        require((hi-lo)/2<=Q(2)**-48,'partial component radius')
    require(coverage['domain']=='UNION_OF_LISTED_ACCEPTED_CELLS_ONLY'and coverage['missing_domain_contribution']=='NOT_BOUNDED_OR_INCLUDED','partial-domain meaning')
    for key in ['coverage_complete','global_complete','endpoint_included','normalization_applied','full_domain_integral','scientific_admission','production_admission']:require(coverage[key]is False,'unsupported complete/admission flag')
    output={'schema':'WU088_W3_STRIP_INDEPENDENT_ACTUAL_REVIEW_V1','status':'PASS_SCOPED_PARTIAL_INTERIOR_WITH_OPEN_HOST_EVENT',
            'source_sha256':sha(Path(__file__)),'reviewed_implementation_sources':PINS,
            'prepared_sha256':prepared['prepared_sha256'],'session_sha256':sha(ROOT/'SESSION_RESULT.json'),'coverage_sha256':sha(ROOT/'COVERAGE.json'),
            'actual_new_native_calls':4,'accepted_new_native_calls':4,'reused_W1_calls_not_reexecuted':16,
            'source_bound_strict_normalization_replayed':4,'independent_exact_union_cells':20,'missing_cells':269,
            'native_evaluations':evaluations,'native_integration_calls':integrations,'callback_calls':callbacks,
            'campaign_wall_ns':session['elapsed_wall_ns'],'measured_runtime_speedup':None,'NCP_or_MPI_execution':False,
            'new_call_evidence':evidence,'partial_component_radius':coverage['component_radius'],
            'residual_claim_evidence':claims,'claim_observation_snapshots':claim_snapshots,'host_event_root_cause':'UNDETERMINED',
            'numerical_acceptance_scope':'Pinned source-bound native output, strict validator and exact serialized interval radius; no whole-runtime cleanup or production claim.',
            'host_event_interpretation':'Successful guarded native wait, worker terminal exit, preserved exact stdout and matching source/input/plan support scoped numerical acceptance. Unexplained residual claim files and any changed visibility since terminal RETURN are separately preserved; cleanup/lifecycle bookkeeping is unresolved. No claim deletion, retry or causal attribution is made.',
            'reviewer_native_integrations':0,'reviewer_endpoint_evaluations':0,'full_new_window_integral_complete':False,'endpoint_added_to_partial_sum':False,
            'normalization_applied':False,'full_D_epsilon':None,'scientific_admission':False,'production_admission':False}
    path=NEW/'review/ACTUAL_REVIEW.json'
    with path.open('x')as stream:json.dump(output,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({key:output[key]for key in ['status','actual_new_native_calls','independent_exact_union_cells','missing_cells','native_evaluations','native_integration_calls','callback_calls']}))

if __name__=='__main__':main()
