#!/usr/bin/env python3
"""Three create-only isolated solves; --preflight performs no ODE.

State: 21 abundance/reference-H1 coordinates plus thermal eV/reference-H1.
Independent oracle: D/H closed-energy scalar equilibrium, not another ODE.
Source, vendor, actual IC, numerical settings and dependencies bind identity.
A failed or partial identity is preserved and cannot be retried automatically.
"""
from __future__ import annotations
import os
for _thread_var in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                    'NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[_thread_var]='1'
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import tempfile
import time
import traceback
import uuid
from datetime import datetime, timezone
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import collisional as collisions
from phys78_bridge import atomic, lease_module, PROVENANCE

ROOT=Path(__file__).resolve().parents[1]
PLAN_PATH=ROOT/'inputs/CONTROL_PLAN.json'
SCHEMA='PHYS79_ISOLATED_SCIENCE_ID_V1'


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def publish_bytes(path,data):
    """Atomic and create-only: a pre-existing destination is never overwritten."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.phys79-publish-',dir=path.parent)
    tmp=Path(name)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.link(tmp,path)
    finally:tmp.unlink(missing_ok=True)


def publish_json(path,value):
    publish_bytes(path,canonical(value)+b'\n')


def write_case_receipt(output,key,record):
    target=Path(output)/'cases'/f'{key}.json'
    data=canonical(record)+b'\n'
    publish_bytes(target,data)
    publish_bytes(target.with_suffix('.json.sha256'),hashlib.sha256(data).hexdigest().encode()+b'\n')


def source_manifest():
    files=['source/collisional.py','source/phys78_bridge.py','source/run_controls.py',
           'inputs/CONTROL_PLAN.json','vendor/PHYS78_PROVENANCE.json']
    for relative,entry in PROVENANCE['files'].items():
        p=ROOT/relative
        if p.stat().st_size!=entry['bytes'] or sha_file(p)!=entry['sha256']:
            raise ValueError('VENDORED_PARENT_IDENTITY_CHANGED:'+relative)
        files.append(relative)
    payload={relative:{'bytes':(ROOT/relative).stat().st_size,'sha256':sha_file(ROOT/relative)}
             for relative in sorted(set(files))}
    return {'files':payload,'sha256':digest(payload),
            'parent_commit':PROVENANCE['parent_commit']}


def load_plan():
    plan=json.loads(PLAN_PATH.read_text())
    if plan['schema']!='PHYS79_ISOLATED_CONTROL_PLAN_V1':raise ValueError('PLAN_SCHEMA')
    expected=[('C01_BASE','C01','baseline'),('C02_BASE','C02','baseline'),
              ('C01_REFINED','C01','refinement')]
    if [(r['id'],r['control'],r['numerics']) for r in plan['tasks_in_order']]!=expected:
        raise ValueError('PLAN_MUST_CONTAIN_EXACTLY_TWO_CONTROLS_AND_ONE_REFINEMENT')
    if plan['solver']['method']!='DOP853' or plan['solver']['samples']!=161:
        raise ValueError('CONTROL_SOLVER_CONTRACT')
    return plan


def prepare_task(task,plan,manifest):
    control=next(v for v in plan['controls'] if v['id']==task['control'])
    net=collisions.CollisionNetwork(ci_rows=tuple(control['ci_rows']),d_cx=control['d_cx'],
                                  d_cx_closure=plan['physics']['d_cx_closure'])
    T=float(control['T_initial_K']);nH=float(control['nH_cm3'])
    y=atomic.neutral_abundances();ix=atomic.SPECIES_INDEX
    for isotope,inventory in atomic.DEFAULT_INVENTORY.items():
        if isotope=='n' or inventory==0:continue
        if isotope=='H1':fraction=float(control['H_initial_ion_fraction'])
        elif isotope=='D':
            chosen=control['D_initial_ion_fraction']
            if isinstance(chosen,str):
                xh=float(control['H_initial_ion_fraction']);ratio=math.exp(-collisions.D_DEFECT_K/T)
                fraction=ratio*xh/(1-xh+ratio*xh)
            else:fraction=float(chosen)
        else:fraction=float(control['other_populated_initial_singly_ion_fraction'])
        if not 0<=fraction<=1:raise ValueError('INITIAL_CHARGE_FRACTION')
        y[ix[isotope+'_I']]=inventory*(1-fraction)
        y[ix[isotope+'_II']]=inventory*fraction
    u=net.thermal_energy(T,y)
    totals=atomic.ISOTOPE_SUM@y
    ionic_scale=atomic.ISOTOPE_SUM.T@totals
    ionic_scale=np.where(ionic_scale>0,ionic_scale,1.)
    scale=np.r_[ionic_scale,u]
    kf,kr=collisions.d_cx_rates(T,plan['physics']['d_cx_closure'])
    if control['reference_rate']=='HI_CI_at_initial_T':
        kref=collisions.ci_rate(0,T)
        step=.05*min(1.,kref/kr)
    elif control['reference_rate']=='D_CX_reverse_at_initial_T':
        kref=kr;step=float(control['max_step_theta'])
    else:raise ValueError('UNKNOWN_REFERENCE_RATE')
    settings=dict(plan['solver'][task['numerics']])
    step*=float(settings.get('max_step_factor',1.))
    numerical={'method':'DOP853','rtol':float(settings['rtol']),
               'atol_scaled':float(settings['atol_scaled']),'max_step_theta':step,
               'saved_samples':161,'scale_vector':scale.tolist()}
    physics={'control_id':control['id'],'ci_rows':list(net.ci_rows),'d_cx':net.d_cx,
             'd_cx_closure':net.d_cx_closure,'T_initial_K':T,'nH_cm3':nH,
             'initial_Y_per_H':y.tolist(),'initial_u_eV_per_H':u,
             'isotope_inventory_per_H':{k:float(v) for k,v in atomic.DEFAULT_INVENTORY.items()},
             'ionic_potential_eV':net.binding_eV.tolist(),'theta_end':float(control['theta_end']),
             'k_ref_cm3_s':kref,'theta_per_proper_second':nH*kref,
             'initial_CX_forward_cm3_s':kf,'initial_CX_reverse_cm3_s':kr,
             'frame':'isotropic nonrelativistic gas in one orthonormal rest frame',
             'proper_volume_and_density':'fixed','H_per_s':0.,'external_heat_bath':False,
             'PI':False,'RR':False,'gas_anisotropic_stress':0.,
             'units':'K,cm^-3,cm^3/s,eV,proper_s,per_reference_H1'}
    binding={'schema':SCHEMA,'source':manifest,'physics':physics,'numerics':numerical,
             'dependencies':{'Python':platform.python_version(),'NumPy':np.__version__,
                             'SciPy':scipy.__version__}}
    return {'task_id':task['id'],'science_id':digest(binding),'binding':binding,
            'physics_id':digest(physics),'network':net,'initial_state':np.r_[y,u],
            'scale':scale,'isotope_totals':totals}


def serial_task(task):
    return {key:task[key] for key in ('task_id','science_id','physics_id','binding')}


def existing_status(output,task):
    key=task['science_id'];folder=Path(output)/'cases'
    receipt=folder/f'{key}.json';npz=folder/f'{key}.npz'
    check=receipt.with_suffix('.json.sha256')
    if receipt.exists():
        if not check.exists() or check.read_text().strip()!=sha_file(receipt):
            raise RuntimeError('CASE_RECEIPT_BYTE_CHECK_FAILED:'+key)
        record=json.loads(receipt.read_text())
        if record.get('science_id')!=key or record.get('binding')!=task['binding']:
            raise RuntimeError('CASE_IDENTITY_MISMATCH:'+key)
        if record['status']=='COMPLETE':
            meta=record['npz']
            if not npz.exists() or npz.stat().st_size!=meta['bytes'] or sha_file(npz)!=meta['sha256']:
                raise RuntimeError('COMPLETED_CASE_BYTES_CHANGED:'+key)
            with np.load(npz,allow_pickle=False) as saved:
                for name in saved.files:
                    if saved[name].dtype.kind in 'fc' and not np.isfinite(saved[name]).all():
                        raise RuntimeError('COMPLETED_CASE_NONFINITE:'+key+':'+name)
            return 'COMPLETE',record
        return 'BLOCKED_FAILED_PREVIOUS_IDENTITY',record
    if npz.exists() or check.exists() or (Path(output)/'claims'/f'{key}.json').exists():
        return 'BLOCKED_INCOMPLETE_PREVIOUS_IDENTITY',None
    if (Path(output)/'attempts'/key).exists():
        return 'BLOCKED_INCOMPLETE_PREVIOUS_IDENTITY',None
    return 'READY',None


def d_cx_equilibrium_oracle(task):
    """Independent one-extent equilibrium plus integrated energy, no ODE."""
    p=task['binding']['physics'];y0=task['initial_state'][:-1];u0=float(task['initial_state'][-1])
    ix=atomic.SPECIES_INDEX
    h0,hp0,d0,dp0=(float(y0[ix[k]]) for k in ('H1_I','H1_II','D_I','D_II'))
    N=float(y0.sum()+atomic.CHARGE@y0);T0=p['T_initial_K']
    # delta is the actually stored rounded potential difference; the DB
    # exponent retains the declared43K model. Their float difference is saved.
    eps=np.asarray(p['ionic_potential_eV']);delta=float(eps[ix['D_II']]-eps[ix['H1_II']])
    lo=max(-h0,-dp0);hi=min(hp0,d0)
    def temperature(xi):
        return T0-2*delta*xi/(3*collisions.KB_EV_K*N)
    def balance(xi):
        T=temperature(xi)
        if not 2.7<=T<=2e5:raise ValueError('ORACLE_TEMPERATURE_OUTSIDE_DCX_DOMAIN')
        K=math.exp(-collisions.D_DEFECT_K/T)
        return K*(d0-xi)*(hp0-xi)-(dp0+xi)*(h0+xi)
    eq=brentq(balance,lo,hi,xtol=1e-18,rtol=4*np.finfo(float).eps)
    Ye=y0.copy();Ye[ix['H1_I']]+=eq;Ye[ix['H1_II']]-=eq
    Ye[ix['D_I']]-=eq;Ye[ix['D_II']]+=eq
    return {'method':'brentq root of scalar ground-state DB extent with closed-energy T(xi)',
            'extra_ODE_calls':0,'extent_bracket_per_H':[lo,hi],'extent_equilibrium_per_H':eq,
            'equilibrium_Y_per_H':Ye.tolist(),'equilibrium_T_K':temperature(eq),
            'equilibrium_u_eV_per_H':u0-delta*eq,'root_balance_per_H_squared':balance(eq),
            'Delta_eV_from_stored_global_potential':delta,
            'declared_43kB_eV':collisions.D_DEFECT_EV,
            'Delta_roundoff_eV':delta-collisions.D_DEFECT_EV,
            'root_xtol':1e-18,'root_rtol':4*np.finfo(float).eps}


def saved_arrays_and_checks(task,theta,physical_states,plan):
    net=task['network'];p=task['binding']['physics'];y=physical_states[:,:-1];u=physical_states[:,-1]
    if physical_states.shape!=(161,atomic.N_SPECIES+1) or not np.isfinite(physical_states).all():
        raise ArithmeticError('SAVED_STATE_SHAPE_OR_NONFINITE')
    if np.any(y<0) or np.any(u<=0):raise ArithmeticError('SAVED_STATE_NONNEGATIVE_DOMAIN')
    T=np.array([net.temperature(ui,yi) for ui,yi in zip(u,y)])
    # Every sampled state independently enters all active source domains.
    for ti in T:net.rate_coefficients(float(ti))
    binding=y@net.binding_eV;energy=u+binding;totals=y@atomic.ISOTOPE_SUM.T
    initial=task['isotope_totals'];active=initial>0
    rel=np.zeros_like(totals)
    rel[:,active]=(totals[:,active]-initial[active])/initial[active]
    absent_abs=float(np.max(np.abs(totals[:,~active]))) if np.any(~active) else 0.
    isoerr=float(np.max(abs(rel)))
    energyerr=float(np.max(abs(energy/energy[0]-1)))
    gates=plan['acceptance_fixed_before_execution']
    checks={'isotope_relative_max':isoerr,'absent_isotope_absolute_max':absent_abs,
            'total_u_plus_binding_relative_max':energyerr,'minimum_saved_species':float(y.min()),
            'minimum_thermal_energy_eV_per_H':float(u.min()),'temperature_range_K':[float(T.min()),float(T.max())],
            'source_domains_all_saved_states':'PASS','state_projection':'NONE'}
    checks['passed']=(isoerr<=gates['isotope_relative'] and absent_abs<=gates['absent_isotope_absolute']
                      and energyerr<=gates['total_u_plus_binding_relative'])
    oracle=None
    if p['control_id']=='C02':
        oracle=d_cx_equilibrium_oracle(task)
        Dtotal=float(atomic.DEFAULT_INVENTORY['D']);ix=atomic.SPECIES_INDEX
        equilibrium=np.array(oracle['equilibrium_Y_per_H'])
        dist=abs(float(y[-1,ix['D_II']]-equilibrium[ix['D_II']]))/Dtotal
        xe=y@atomic.CHARGE
        checks['D_final_equilibrium_distance_over_inventory']=dist
        checks['electron_abundance_variation_abs']=float(np.max(abs(xe-xe[0])))
        extent=y[:,ix['D_II']]-task['initial_state'][ix['D_II']]
        N0=float(task['initial_state'][:-1].sum()+atomic.CHARGE@task['initial_state'][:-1])
        expected_T=p['T_initial_K']-2*oracle['Delta_eV_from_stored_global_potential']*extent/(3*collisions.KB_EV_K*N0)
        thermal_error=float(np.max(abs(T-expected_T)))
        checks['D_extent_temperature_absolute_error_K']=thermal_error
        checks['passed']=bool(checks['passed'] and dist<=gates['C02_final_equilibrium_distance_over_D_inventory']
                              and thermal_error<=gates['C02_extent_temperature_absolute_error_K'])
        oracle['final_sample_distance_over_D_inventory']=dist
        oracle['finite_duration_interpretation']='final approach to equilibrium; no claim of exact finite-time equality'
    arrays={'theta':np.asarray(theta),'proper_time_s':np.asarray(theta)/p['theta_per_proper_second'],
            'Y':y,'u_eV_per_H':u,'T_K':T,'binding_eV_per_H':binding,
            'total_u_plus_binding_eV_per_H':energy,'isotope_totals_per_H':totals,
            'electron_abundance_per_H':y@atomic.CHARGE,'raw_states':physical_states,
            'scaled_states':physical_states/task['scale'][None,:],
            'species_names':np.array(atomic.SPECIES_NAMES),'isotope_names':np.array(atomic.ISOTOPES)}
    return arrays,checks,oracle


def execute_one(output,task,plan,lease,observation):
    output=Path(output);key=task['science_id'];run_attempt=uuid.uuid4().hex
    attempt=output/'attempts'/key/run_attempt;claims=output/'claims'/f'{key}.json'
    called=False;claimed=False;started=now();wall=time.monotonic();rhs_count=0
    try:
        status,record=existing_status(output,task)
        if status!='READY':return {'task_id':task['task_id'],'science_id':key,'status':status,'new_ODE_calls':0}
        if source_manifest()!=task['binding']['source']:raise RuntimeError('SOURCE_CHANGED_BEFORE_SOLVE')
        publish_json(claims,{'science_id':key,'attempt':str(attempt.relative_to(output)),
                             'started_utc':started,'pid':os.getpid(),'lease':lease})
        claimed=True;attempt.mkdir(parents=True)
        publish_json(attempt/'STARTED.json',{'task':serial_task(task),'started_utc':started,'resources':observation})
        net=task['network'];physics=task['binding']['physics'];solver=task['binding']['numerics']
        scale=task['scale'];clock=physics['theta_per_proper_second'];theta=np.linspace(0.,physics['theta_end'],161)
        def rhs(theta_value,scaled):
            nonlocal rhs_count
            rhs_count+=1
            state=np.asarray(scaled)*scale;y=state[:-1];u=float(state[-1])
            T=net.temperature(u,y)
            point=net.rhs(T,physics['nH_cm3'],y,H_per_s=0.)
            derivative=np.r_[point.d_species_per_H_dt,point.heat_eV_per_H_s]
            return derivative/(clock*scale)
        # This durable marker precedes the single actual solve_ivp call.
        publish_json(attempt/'SOLVE_IVP_CALL_0001.json',
                     {'call_index':1,'utc':now(),'method':'DOP853','new_ODE':True,
                      'old_completed_identity_replay':False,'theta_span':[0.,physics['theta_end']]})
        called=True
        sol=solve_ivp(rhs,(0.,physics['theta_end']),task['initial_state']/scale,method='DOP853',
                      rtol=solver['rtol'],atol=solver['atol_scaled'],t_eval=theta,max_step=solver['max_step_theta'])
        publish_json(attempt/'SOLVE_IVP_RETURNED.json',{'success':bool(sol.success),'message':sol.message,
                     'nfev':int(sol.nfev),'njev':int(sol.njev),'nlu':int(sol.nlu),'saved_samples':len(sol.t),
                     'rhs_calls':rhs_count,'wall_s':time.monotonic()-wall})
        physical=sol.y.T*scale[None,:]
        # Preserve even an unsuccessful solver's available raw values.
        with (attempt/'RAW_SOLVER_RESULT.npz').open('xb') as stream:
            np.savez_compressed(stream,theta=sol.t,raw_states=physical)
        if not sol.success or len(sol.t)!=161:raise RuntimeError('SOLVER_INCOMPLETE:'+sol.message)
        arrays,checks,oracle=saved_arrays_and_checks(task,sol.t,physical,plan)
        raw=attempt/'RESULT.npz'
        with raw.open('xb') as stream:np.savez_compressed(stream,**arrays)
        publish_json(attempt/'POSTFLIGHT.json',{'checks':checks,'oracle':oracle})
        if not checks['passed']:raise ArithmeticError('ISOLATED_SCIENTIFIC_ACCEPTANCE_FAILED')
        if source_manifest()!=task['binding']['source']:raise RuntimeError('SOURCE_CHANGED_DURING_SOLVE')
        final=output/'cases'/f'{key}.npz';final.parent.mkdir(parents=True,exist_ok=True)
        os.link(raw,final)
        record={'status':'COMPLETE','science_id':key,'physics_id':task['physics_id'],
                'task_id':task['task_id'],'binding':task['binding'],'attempt':str(attempt.relative_to(output)),
                'started_utc':started,'completed_utc':now(),'wall_s':time.monotonic()-wall,
                'solver':{'nfev':int(sol.nfev),'njev':int(sol.njev),'nlu':int(sol.nlu),'rhs_calls':rhs_count,
                          'message':sol.message,'new_ODE_calls':1},'checks':checks,'oracle':oracle,
                'npz':{'path':str(final.relative_to(output)),'bytes':final.stat().st_size,'sha256':sha_file(final)},
                'provenance':{'new_isolated_ODE':True,'old_completed_replays':0,'new_cosmological_ODE':0,
                              'NCP':0,'benchmark':0,'lease':lease,'resources':observation},
                'HH_R10':'OFF','production_admission':'NOT_ISSUED'}
        write_case_receipt(output,key,record)
        return {'task_id':task['task_id'],'science_id':key,'status':'COMPLETE','new_ODE_calls':1,
                'checks':checks,'npz':record['npz']}
    except Exception as error:
        failure={'status':'FAILED','science_id':key,'task_id':task['task_id'],'binding':task['binding'],
                 'attempt':str(attempt.relative_to(output)),'failed_utc':now(),'error':repr(error),
                 'traceback':traceback.format_exc(),'new_ODE_calls':int(called),'rhs_calls':rhs_count,
                 'automatic_retry':False,'wall_s':time.monotonic()-wall}
        # Do not overwrite or add an attempt under a competing owner's claim.
        if claimed:
            attempt.mkdir(parents=True,exist_ok=True);publish_json(attempt/'FAILED.json',failure)
            if not (output/'cases'/f'{key}.json').exists():write_case_receipt(output,key,failure)
        return {'task_id':task['task_id'],'science_id':key,'status':'FAILED','new_ODE_calls':int(called),
                'error':repr(error),'attempt_preserved':claimed}


def refinement_check(output,tasks,plan):
    byid={t['task_id']:t for t in tasks};base=byid['C01_BASE'];fine=byid['C01_REFINED']
    bs,br=existing_status(output,base);fs,fr=existing_status(output,fine)
    if bs!='COMPLETE' or fs!='COMPLETE':return {'status':'NOT_AVAILABLE','baseline':bs,'refinement':fs}
    if base['physics_id']!=fine['physics_id']:raise RuntimeError('REFINEMENT_PHYSICAL_IDENTITY_MISMATCH')
    with np.load(Path(output)/br['npz']['path'],allow_pickle=False) as a,np.load(Path(output)/fr['npz']['path'],allow_pickle=False) as b:
        if not np.array_equal(a['theta'],b['theta']):raise RuntimeError('REFINEMENT_SAVED_GRID_MISMATCH')
        difference=float(np.max(abs((a['raw_states']-b['raw_states'])/base['scale'][None,:])))
    threshold=plan['acceptance_fixed_before_execution']['C01_refinement_max_scaled_state_difference']
    return {'status':'PASS' if difference<=threshold else 'FAIL','maximum_scaled_state_difference':difference,
            'fixed_threshold':threshold,'baseline_science_id':base['science_id'],'refinement_science_id':fine['science_id'],
            'same_physics_id':base['physics_id'],'continuum_certificate':False}


def run(output,*,execute=False,lease_dir='/tmp/rei-bianchi-cooperative-leases'):
    output=Path(output).resolve();plan=load_plan();manifest=source_manifest()
    tasks=[prepare_task(t,plan,manifest) for t in plan['tasks_in_order']]
    statuses=[{'task_id':t['task_id'],'science_id':t['science_id'],'status':existing_status(output,t)[0]} for t in tasks]
    if not execute:
        return {'status':'PREFLIGHT_NO_ODE','tasks':[serial_task(t) for t in tasks],
                'existing':statuses,'source':manifest,'new_ODE_calls':0,
                'command_to_execute':'python source/run_controls.py --execute --output '+str(output)}
    run_id=uuid.uuid4().hex;start=now();wall=time.monotonic()
    request={'schema':SCHEMA,'run_id':run_id,'started_utc':start,'plan':plan,
             'tasks':[serial_task(t) for t in tasks],'existing':statuses,'lease_dir':str(lease_dir),
             'site':'local','workers':1,'threads_per_process':1,'automatic_retry':False}
    publish_json(output/'requests'/f'{run_id}.json',request)
    leases=lease_module();pool=leases.LeasePool(path=lease_dir,site='local')
    results=[];stopped=False
    for task in tasks:
        if stopped:
            results.append({'task_id':task['task_id'],'science_id':task['science_id'],
                            'status':'NOT_LAUNCHED_AFTER_PRIOR_STOP','new_ODE_calls':0});continue
        state,record=existing_status(output,task)
        if state=='COMPLETE':
            results.append({'task_id':task['task_id'],'science_id':task['science_id'],
                            'status':'SKIPPED_COMPLETE_BYTE_VERIFIED','new_ODE_calls':0});continue
        if state!='READY':
            results.append({'task_id':task['task_id'],'science_id':task['science_id'],
                            'status':state,'new_ODE_calls':0});stopped=True;continue
        lease,obs=pool.acquire('PHYS79:'+task['task_id']+':'+task['science_id'])
        if lease is None:
            results.append({'task_id':task['task_id'],'science_id':task['science_id'],'status':'WAITING_FOR_SHARED_LEASE',
                            'resources':obs,'new_ODE_calls':0});stopped=True;continue
        try:
            result=execute_one(output,task,plan,lease,obs);results.append(result)
            if result['status']!='COMPLETE':stopped=True
        finally:leases.release_lease(lease)
    refinement=refinement_check(output,tasks,plan)
    all_complete=all(existing_status(output,t)[0]=='COMPLETE' for t in tasks)
    new_count=sum(r['new_ODE_calls'] for r in results)
    markers=list((output/'attempts').glob('*/*/SOLVE_IVP_CALL_*.json'))
    summary={'schema':'PHYS79_ISOLATED_RUN_RECEIPT_V1','run_id':run_id,
             'status':'COMPLETE' if all_complete and refinement['status']=='PASS' else ('WAITING' if any(r['status']=='WAITING_FOR_SHARED_LEASE' for r in results) else 'INCOMPLETE_OR_FAILED'),
             'started_utc':start,'completed_utc':now(),'wall_s':time.monotonic()-wall,
             'request_path':str((output/'requests'/f'{run_id}.json').relative_to(output)),
             'results':results,'refinement':refinement,'new_ODE_calls_this_invocation':new_count,
             'total_durable_solve_ivp_call_markers_in_output':len(markers),
             'completed_exact_identity_replays':0,'completed_skips_this_invocation':sum(r['status']=='SKIPPED_COMPLETE_BYTE_VERIFIED' for r in results),
             'new_cosmological_ODE':0,'NCP':0,'benchmark':0,'source_manifest':manifest,
             'HH_R10':'OFF','production_admission':'NOT_ISSUED'}
    publish_json(output/'runs'/f'{run_id}.json',summary)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/isolated')
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--execute',action='store_true')
    modes.add_argument('--preflight',action='store_true')
    parser.add_argument('--lease-dir',default='/tmp/rei-bianchi-cooperative-leases')
    args=parser.parse_args();result=run(args.output,execute=args.execute,lease_dir=args.lease_dir)
    print(json.dumps(result,indent=2,allow_nan=False))
    if args.execute and result['status'] not in ('COMPLETE','WAITING'):raise SystemExit(2)


if __name__=='__main__':main()
