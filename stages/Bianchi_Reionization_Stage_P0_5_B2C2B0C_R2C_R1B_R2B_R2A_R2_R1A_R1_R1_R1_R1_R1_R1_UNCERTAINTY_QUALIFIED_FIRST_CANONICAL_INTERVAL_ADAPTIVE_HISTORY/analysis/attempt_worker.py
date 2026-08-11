#!/usr/bin/env python3
"""One short-lived lane attempt around the unchanged sealed map."""
from __future__ import annotations
import argparse,importlib.util,json,sys,time,traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any,Iterable
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;REPO=STAGE.parents[1]
PREDECESSOR=REPO/'stages'/('Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_'
 'R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK')
KERNEL_PATH=PREDECESSOR/'analysis/interval_discrete_map.py'
def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
policy=_load('adaptive_history_worker_policy',HERE/'adaptive_policy.py')
state_io=_load('adaptive_history_worker_state_io',HERE/'state_io.py')
jax_guard=_load('adaptive_history_worker_jax_guard',HERE/'jax_import_guard.py')
runtime_contract=_load('adaptive_history_worker_runtime_contract',HERE/'runtime_contract.py')
@dataclass(frozen=True)
class ValidatedJob:raw:dict[str,Any];task:Any;parent_state_sha256:str
def _sha(v):
    try:return isinstance(v,str) and len(v)==64 and int(v,16)>=0
    except ValueError:return False
def validate_job(job):
    keys={'accepted_index','input_lock_sha256','interval','job_key','lane','parent','predecessor_kernel_sha256','runtime_contract_sha256','stage_id','worker_job_schema'}
    if not isinstance(job,dict) or set(job)!=keys or type(job.get('worker_job_schema')) is not int or job.get('worker_job_schema')!=1 or job.get('stage_id')!=policy.STAGE_ID:raise ValueError('unsupported job schema')
    lane=job.get('lane');interval=job.get('interval')
    if lane not in policy.LANE_ORDER or not isinstance(interval,dict) or set(interval)!={'depth','left_tick','right_tick'} or not all(type(interval[name]) is int for name in interval):raise ValueError('invalid lane or interval integers')
    try:task=policy.IntervalTask(interval['left_tick'],interval['right_tick'],interval['depth'])
    except Exception as error:raise ValueError('invalid job interval') from error
    if task.as_dict()!=interval:raise ValueError('noncanonical job interval')
    index=job.get('accepted_index');parent=job.get('parent')
    if type(index) is not int or index<=0 or not isinstance(parent,dict) or set(parent)!={'kind','path','sha256'} or parent.get('kind') not in {'INITIAL','STATE'}:raise ValueError('invalid parent/index')
    if parent['kind']=='INITIAL':
        if task.left_tick!=0 or index!=1 or parent.get('path') is not None or parent.get('sha256')!='INITIAL':raise ValueError('invalid initial parent')
        parent_sha='INITIAL'
    else:
        parent_sha=parent.get('sha256')
        if not _sha(parent_sha) or not isinstance(parent.get('path'),str):raise ValueError('invalid state parent')
    if not _sha(job.get('input_lock_sha256')) or not _sha(job.get('predecessor_kernel_sha256')) or not _sha(job.get('runtime_contract_sha256')):raise ValueError('invalid lock hash')
    expected=policy.job_key(lane=lane,task=task,accepted_index=index,parent_state_sha256=parent_sha,input_lock_sha256=job['input_lock_sha256'],predecessor_kernel_sha256=job['predecessor_kernel_sha256'],runtime_contract_sha256=job['runtime_contract_sha256'])
    if job.get('job_key')!=expected:raise ValueError('worker job key mismatch')
    return ValidatedJob(job,task,parent_sha)
def _json(v):
    if isinstance(v,dict):return {str(k):_json(x) for k,x in sorted(v.items())}
    if isinstance(v,(list,tuple)):return [_json(x) for x in v]
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    raise TypeError(type(v).__name__)
def summarize_events(events:Iterable[Any]):
    rows=[]
    for e in events:rows.append({'any_event':bool(e.any_event),'knot_indices':np.asarray(e.knot_indices,dtype=np.int64).tolist(),'minimum_distance':float(e.minimum_distance),'node_indices':np.asarray(e.node_indices,dtype=np.int64).tolist()})
    return {'any_event':any(x['any_event'] for x in rows),'events':rows,'minimum_distance':min((x['minimum_distance'] for x in rows),default=1e300),'node_count':sum(len(x['node_indices']) for x in rows)}
def make_envelope(*,job,classification,scientific_accept,widths,table_event,set_ledgers,diagnostics,candidate_state,duration_seconds,t0,t1,elapsed_s,jax_guard_installed):
    if scientific_accept!=(classification=='PASS') or scientific_accept!=(candidate_state is not None):raise ValueError('acceptance/state disagreement')
    return _json({'accepted_index':job['accepted_index'],'candidate_state':candidate_state,'classification':classification,'diagnostics':diagnostics,'duration_seconds_hex':float(duration_seconds).hex(),'input_lock_sha256':job['input_lock_sha256'],'interval':job['interval'],'job_key':job['job_key'],'lane':job['lane'],'parent_state_sha256':job['parent']['sha256'],'predecessor_kernel_sha256':job['predecessor_kernel_sha256'],'public_widths':widths,'runtime_contract_sha256':job['runtime_contract_sha256'],'scientific_accept':scientific_accept,'set_ledgers':set_ledgers,'stage_id':policy.STAGE_ID,'table_event':table_event,'telemetry':{'elapsed_s':elapsed_s,'jax_import_guard_installed':jax_guard_installed,'numpy_version':np.__version__,'python_version':sys.version.split()[0]},'time':{'t0_hex':float(t0).hex(),'t1_hex':float(t1).hex()},'transport_status':'OK','worker_envelope_schema':1})
def _kernel():return _load('adaptive_history_sealed_interval_map',KERNEL_PATH)
def _context(module,lane):
    base=module.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane);parent=base.inputs.state0.mutable_copy()
    y=np.asarray(parent.values[:5].T,dtype=np.float64);logt=np.log(np.asarray(parent.temperature_K,dtype=np.float64))
    return base,y,logt,y[:,0]+y[:,1],np.sum(y[:,2:5],axis=1)
def _parent(module,validated,y,logt):
    descriptor=validated.raw['parent']
    if descriptor['kind']=='INITIAL':return module._I(y,y),module._I(logt,logt)
    decoded=state_io.read_state(Path(descriptor['path']),expected_sha256=validated.parent_state_sha256)
    for k,v in {'accepted_index':validated.raw['accepted_index']-1,'endpoint_tick':validated.task.left_tick,'input_lock_sha256':validated.raw['input_lock_sha256'],'lane':validated.raw['lane'],'predecessor_kernel_sha256':validated.raw['predecessor_kernel_sha256'],'runtime_contract_sha256':validated.raw['runtime_contract_sha256'],'stage_id':policy.STAGE_ID}.items():
        if decoded.metadata.get(k)!=v:raise ValueError(f'parent metadata mismatch: {k}')
    if decoded.population_lower.shape[0]!=policy.STATE_NODE_COUNT:raise ValueError('parent node count mismatch')
    return module._I(decoded.population_lower,decoded.population_upper),module._I(decoded.log_temperature_lower,decoded.log_temperature_upper)
def _failure(job,step,events,diagnostics,duration,t0,t1,started,guard):
    table=summarize_events(events);classification='TABLE_EVENT_REQUIRES_RESTART' if table['any_event'] else str(step.classification);diagnostics=dict(diagnostics);diagnostics['kernel_classification']=str(step.classification)
    return make_envelope(job=job,classification=classification,scientific_accept=False,widths={},table_event=table,set_ledgers={},diagnostics=diagnostics,candidate_state=None,duration_seconds=duration,t0=t0,t1=t1,elapsed_s=time.perf_counter()-started,jax_guard_installed=guard)
def classify_scientific_exception(error):
    message=str(error)
    if isinstance(error,FloatingPointError):
        if message=='POPULATION_CONE':return 'POPULATION_CONE_FAILURE',False
        if message in {'implicit tangent solve failed','implicit tangent is nonfinite','midpoint matrix is singular'}:return 'IMPLICIT_CERTIFICATE_EXCEPTION',False
    if isinstance(error,ValueError):
        if message=='ABOVE_TABLE' or 'above-table' in message.lower():return 'TABLE_EVENT_ABOVE_TABLE_REQUIRES_RESTART',True
        interval_inputs=('matrix must be finite','vector must be finite','invalid matrix interval','invalid rhs interval')
        if message in interval_inputs:return 'INTERVAL_CERTIFICATE_INPUT_FAILURE',False
        cone_fragments=('strict physical cone','must remain strictly inside','fraction must remain inside','logit input must lie strictly')
        if any(fragment in message for fragment in cone_fragments):return 'PHYSICAL_CONE_FAILURE',False
    return None
def _exception_failure(job,error,phase,prior,duration,t0,t1,started,guard):
    mapped=classify_scientific_exception(error)
    if mapped is None:raise error
    classification,event=mapped
    events=[{'any_event':True,'knot_indices':[],'minimum_distance':0.0,'node_indices':[]}] if event else []
    table={'any_event':event,'events':events,'minimum_distance':0.0 if event else 1e300,'node_count':0}
    diagnostics={'exception_message':str(error),'exception_type':type(error).__name__,'failed_phase':phase,'prior_phase_diagnostics':prior}
    return make_envelope(job=job,classification=classification,scientific_accept=False,widths={},table_event=table,set_ledgers={},diagnostics=diagnostics,candidate_state=None,duration_seconds=duration,t0=t0,t1=t1,elapsed_s=time.perf_counter()-started,jax_guard_installed=guard)
def run_job(job,state_path):
    started=time.perf_counter();validated=validate_job(job)
    if state_io.sha256_file(STAGE/'INPUT_LOCK.json')!=job['input_lock_sha256']:raise ValueError('input lock hash mismatch')
    if state_io.sha256_file(KERNEL_PATH)!=job['predecessor_kernel_sha256']:raise ValueError('kernel hash mismatch')
    runtime_contract.verify(job['runtime_contract_sha256'],REPO,STAGE,numeric_fingerprint=runtime_contract.loaded_numeric_fingerprint())
    guard=jax_guard.install_if_missing();m=_kernel();base,y,logt,total_h,total_he=_context(m,job['lane']);parent_pop,parent_logt=_parent(m,validated,y,logt)
    model=m.rim.ReducedIntervalModel.from_repo(REPO);duration=float(base.forcing.duration_seconds(0))
    t0=duration*(validated.task.left_tick/policy.TOTAL_TICKS);t1=duration*(validated.task.right_tick/policy.TOTAL_TICKS);mid=t0+.5*(t1-t0)
    kw={'model':model,'base':base,'parent_pop':parent_pop,'parent_logt':parent_logt,'t0':t0,'t1':t1,'total_h':total_h,'total_he':total_he}
    try:full=m.run_step(**kw)
    except (FloatingPointError,ValueError) as error:return _exception_failure(job,error,'full_step',{},duration,t0,t1,started,guard)
    if not full.certified:return _failure(job,full,full.table_events,{'failed_phase':'full_step','full_step':full.diagnostics},duration,t0,t1,started,guard)
    kw.update(t1=mid)
    try:first=m.run_step(**kw)
    except (FloatingPointError,ValueError) as error:return _exception_failure(job,error,'first_half',{'full_step':full.diagnostics},duration,t0,t1,started,guard)
    if not first.certified:return _failure(job,first,full.table_events+first.table_events,{'failed_phase':'first_half','full_step':full.diagnostics,'first_half':first.diagnostics},duration,t0,t1,started,guard)
    kw.update(parent_pop=first.population,parent_logt=first.log_temperature,t0=mid,t1=t1)
    try:second=m.run_step(**kw)
    except (FloatingPointError,ValueError) as error:return _exception_failure(job,error,'second_half',{'full_step':full.diagnostics,'first_half':first.diagnostics},duration,t0,t1,started,guard)
    if not second.certified:return _failure(job,second,full.table_events+first.table_events+second.table_events,{'failed_phase':'second_half','full_step':full.diagnostics,'first_half':first.diagnostics,'second_half':second.diagnostics},duration,t0,t1,started,guard)
    pop=second.population;xf=second.log_temperature
    half={'x_HII':m._I(pop.lo[:,1]/total_h,pop.hi[:,1]/total_h),'x_HeII':m._I(pop.lo[:,3]/total_he,pop.hi[:,3]/total_he),'x_HeIII':m._I(pop.lo[:,4]/total_he,pop.hi[:,4]/total_he),'log_T':xf}
    widths={k:float(np.max(v.hi-v.lo)) for k,v in half.items()}
    fp=full.population;fullc={'x_HII':m._I(fp.lo[:,1]/total_h,fp.hi[:,1]/total_h),'x_HeII':m._I(fp.lo[:,3]/total_he,fp.hi[:,3]/total_he),'x_HeIII':m._I(fp.lo[:,4]/total_he,fp.hi[:,4]/total_he),'log_T':full.log_temperature}
    local={k:float(np.max(np.maximum(np.abs(half[k].lo-fullc[k].hi),np.abs(half[k].hi-fullc[k].lo)))) for k in ('x_HII','x_HeII','x_HeIII','log_T')};maximum=max(local.values())
    ledgers={'H_nuclei':(float(np.min((pop.lo[:,0]+pop.lo[:,1])-total_h)),float(np.max((pop.hi[:,0]+pop.hi[:,1])-total_h))),'He_nuclei':(float(np.min(np.sum(pop.lo[:,2:5],axis=1)-total_he)),float(np.max(np.sum(pop.hi[:,2:5],axis=1)-total_he)))}
    for prefix,event,pbox,ts in (('stage',second.stage_event,second.population,mid+m.sdirk.GAMMA*(t1-mid)),('final',second.final_event,second.population,t1)):
        ledgers[prefix+'_photon_identity']=(float(np.min(event.photon_identity.lo)),float(np.max(event.photon_identity.hi)));total=event.resolved_heat+event.unresolved_energy+event.escaped_energy+event.chemical_energy
        ledgers[prefix+'_total_energy']=(float(np.min(total.lo)),float(np.max(total.hi)))
        for gi,res in enumerate(m.group_photon_residuals(model,pbox,ts)):ledgers[f'{prefix}_group_{gi}_photon']=(float(np.asarray(res.lo)),float(np.asarray(res.hi)))
    audit=m.primitive.audit_set_ledgers(ledgers)
    classification='SET_LEDGER_EXCLUDES_ZERO' if not audit.all_include_zero else 'PUBLIC_WIDTH_GATE_FAILURE' if max(widths.values())>=.002 else 'VALIDATED_LOCAL_ERROR_GATE_FAILURE' if maximum>=2e-4 else 'PASS'
    events=full.table_events+first.table_events+second.table_events;diagnostics={'failed_ledgers':list(audit.failed),'first_half':first.diagnostics,'full_step':full.diagnostics,'map_enclosed':True,'maximum_validated_local_error':maximum,'second_half':second.diagnostics,'validated_local_error_bounds':local}
    candidate=None
    if classification=='PASS':
        metadata={'accepted_index':job['accepted_index'],'endpoint_tick':validated.task.right_tick,'input_lock_sha256':job['input_lock_sha256'],'job_key':job['job_key'],'lane':job['lane'],'parent_state_sha256':validated.parent_state_sha256,'predecessor_kernel_sha256':job['predecessor_kernel_sha256'],'runtime_contract_sha256':job['runtime_contract_sha256'],'stage_id':policy.STAGE_ID}
        digest=state_io.write_state(Path(state_path),metadata,pop.lo,pop.hi,xf.lo,xf.hi);candidate={'format':'REIADP1-deterministic-float64','node_count':int(pop.lo.shape[0]),'path':str(Path(state_path).resolve()),'sha256':digest,'size_bytes':Path(state_path).stat().st_size}
    return make_envelope(job=job,classification=classification,scientific_accept=classification=='PASS',widths=widths,table_event=summarize_events(events),set_ledgers=ledgers,diagnostics=diagnostics,candidate_state=candidate,duration_seconds=duration,t0=t0,t1=t1,elapsed_s=time.perf_counter()-started,jax_guard_installed=guard)
def main():
    p=argparse.ArgumentParser();p.add_argument('--job',required=True);p.add_argument('--result',required=True);p.add_argument('--state',required=True);a=p.parse_args();job=None
    try:
        job=json.loads(Path(a.job).read_text());row=run_job(job,Path(a.state));state_io.atomic_write_bytes(Path(a.result),state_io.canonical_json_bytes(row)+b'\n');print(json.dumps({'transport_status':'OK','job_key':row['job_key'],'classification':row['classification'],'scientific_accept':row['scientific_accept']},sort_keys=True),flush=True);return 0
    except Exception as error:
        failure={'error':f'{type(error).__name__}: {error}','job_key':job.get('job_key') if isinstance(job,dict) else None,'stage_id':policy.STAGE_ID,'traceback':traceback.format_exc(),'transport_status':'ERROR','worker_envelope_schema':1}
        try:state_io.atomic_write_bytes(Path(a.result),state_io.canonical_json_bytes(failure)+b'\n')
        except Exception:pass
        traceback.print_exc();return 2
if __name__=='__main__':raise SystemExit(main())
