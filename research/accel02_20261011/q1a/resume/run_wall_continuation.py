#!/usr/bin/env python3
"""OPTIONAL exact-artifact single wall-only continuation; no tolerance changes.

The coefficient function and BDF event loop are copied verbatim from the pinned
original driver except start position, accumulated evidence, and phase budget.
This is a fresh BDF initialization, NOT a bitwise restoration of BDF internals.
"""
from __future__ import annotations
import argparse,hashlib,json,sys,time,traceback,types,importlib.util,shutil
from pathlib import Path
import numpy as np
from scipy.integrate import BDF
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import checkpoint as cp

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value
class NoNativeBeforeValidation:
    def __getattr__(self,name):raise RuntimeError('NATIVE_FORBIDDEN_BEFORE_VALIDATION:'+name)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--manifest-sha',required=True)
    parser.add_argument('--n1',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--additional-wall-seconds',type=float,required=True)
    args=parser.parse_args()
    cp.require(np.isfinite(args.additional_wall_seconds) and 0<args.additional_wall_seconds<=600.,'ADDITIONAL_PHASE_LIMIT_600_SECONDS')
    manifest,(original_identity,prior,event_record,saved,last,decision)=cp.load_manifest(args.manifest,args.manifest_sha)
    original=Path(manifest['original_directory'])
    cp.require(not args.output.exists(),'CREATE_ONLY_OUTPUT_REQUIRED')
    cp.require(not args.output.resolve().is_relative_to(original.resolve()),'OUTPUT_MUST_BE_OUTSIDE_ORIGINAL_DIRECTORY')
    cp.require(sha(args.n1/'provider.py')==original_identity['n1_sha'],'N1_IDENTITY_MISMATCH')
    binary=args.n1/'native/target/release/rei_n1_native'
    cp.require(sha(binary)==original_identity['native_sha'],'NATIVE_IDENTITY_MISMATCH')
    base=module('q1a_resume_base',original/'base_driver_as_run.py')
    original_characteristics=module('characteristics',original/'characteristics_as_run.py')
    factory=module('q1a_resume_factory',original/'fixed_grid_as_run.py')
    events=module('q1a_resume_events',original/'events_as_run.py')
    characteristics=factory.FixedCharacteristics(original/'GRID.json',original_characteristics)
    n1=module('q1a_resume_n1',args.n1/'provider.py')
    provider=n1.HistoryProvider(original_identity['args']['shear'])
    cp.require(provider.identity==original_identity['input_identity']==characteristics.record['input_identity'],'SOURCE_IDENTITY_MISMATCH')
    cp.require(provider.r==characteristics.record['construction']['r'],'GRID_SHEAR_MISMATCH')
    p=base.Coupled(provider,NoNativeBeforeValidation(),characteristics,original_identity['args']['energy'],original_identity['args']['angle'],coordinate='energy')
    cp.require(np.array_equal(p.scales,saved['scales']),'RECONSTRUCTED_SCALES_MISMATCH')
    cp.require(np.array_equal(saved['scaled_states'][0],p.y0/p.scales),'ORIGINAL_CAUCHY_STATE_MISMATCH')
    cp.require(all(np.array_equal(saved[k],v) for k,v in [('q',p.q),('mu',p.mu),('weights',p.weights)]),'RECONSTRUCTED_GRID_MISMATCH')
    cp.require(np.array_equal(saved['u']*p.end,[r['time_s'] for r in prior['history']]),'SAVED_PREFIX_TIMES_MISMATCH')
    cp.require(all(np.isfinite(r[k]) for r in prior['history'] for k in r),'NONFINITE_SAVED_JSON_HISTORY')
    knots=np.array(sorted(set([10.,13.60,24.59,54.42,50000.]+events.native_jump_energies(provider.tables['emissivity']))))
    eventlist=events.crossing_events(p.q,p.mu,provider.geometry,p.end,knots)
    boundaries=events.restart_boundaries(eventlist)
    ztimes=[provider.background.time_of_redshift(float(z))/p.end for z in provider.tables['emissivity'].redshifts if provider.z_final<z<provider.z_initial]
    boundaries=np.unique(np.r_[boundaries,ztimes])
    cp.require(eventlist==event_record['events'] and np.array_equal(boundaries,event_record['boundaries']),'RECONSTRUCTED_EVENT_SCHEDULE_MISMATCH')
    args.rtol=original_identity['args']['rtol'];args.max_step=original_identity['args']['max_step']
    resume_u=decision['resume_u'];start_segment=decision['resume_segment']
    full=last['scaled_y'].copy();samples=np.linspace(0,1,129)
    si=len(saved['u']);rows=list(prior['history']);sample_u=list(saved['u']);sample_v=list(saved['scaled_states'].copy())
    accepted_min=prior['min_accepted_photon_energy'];accepted_energy=prior['max_endpoint_energy_ledger'];accepted_number=prior['max_endpoint_number_ledger']
    completed_segments=prior['completed_segments']
    gas_lo=np.array([prior['accepted_gas_min'][k] for k in cp.GAS_KEYS]);gas_hi=np.array([prior['accepted_gas_max'][k] for k in cp.GAS_KEYS])
    accepted_finite=prior['checks']['accepted_finite'];accepted_gas_valid=prior['checks']['accepted_gas_domain']
    p.calls=prior['rhs_calls'];p.jcalls=prior['jac_calls'];p.max_local_number=prior['max_local_number'];p.max_local_energy=prior['max_local_energy']
    args.output.mkdir(parents=True,exist_ok=False);pred=args.output/'predecessor';pred.mkdir()
    for name in cp.FILES:shutil.copyfile(original/name,pred/name)
    for name in [*cp.AS_RUN,'EVENTS.json']:shutil.copyfile(original/name,args.output/name)
    shutil.copyfile(__file__,args.output/'resume_driver_as_run.py')
    shutil.copyfile(cp.__file__,args.output/'resume_checkpoint_as_run.py')
    shutil.copyfile(args.manifest,args.output/'CONTINUATION_MANIFEST.json')
    chain=dict(schema='rei.q1a.executed_continuation_chain.v1',original_files_sha256=manifest['original_files_sha256'],
      manifest_sha256=args.manifest_sha,original_driver_sha256=original_identity['driver_sha'],
      resume_driver_sha256=sha(__file__),resume_validator_sha256=sha(cp.__file__),
      start_u=resume_u,start_segment=start_segment,prefix_samples=si,additional_wall_budget_s=args.additional_wall_seconds,
      extra_bdf_initializations=1,solver_internal_state_restored=False,tolerance_changes=False,physics_changes=False,
      original_phase_status=prior['status'],original_failure=prior['failure'],comparison_status='UNSUPPORTED_UNTIL_INDEPENDENT_CONTINUATION_CHAIN_REVIEW')
    (args.output/'CONTINUATION.json').write_text(json.dumps(chain,indent=2,allow_nan=False)+'\n')
    identity=dict(original_identity)
    identity['continuation']=dict(chain_file='CONTINUATION.json',chain_sha256=sha(args.output/'CONTINUATION.json'),
      operator_driver_sha256=original_identity['driver_sha'],resume_driver_sha256=sha(__file__),
      resume_validator_sha256=sha(cp.__file__),actual_output=str(args.output),actual_n1=str(args.n1),
      execution='ORIGINAL_OPERATOR_PLUS_EXPLICIT_RESUME_DRIVER',comparison_supported=False)
    (args.output/'IDENTITY.json').write_text(json.dumps(identity,indent=2,allow_nan=False)+'\n')
    cp.verify_hashes(pred,manifest['original_files_sha256'])
    native=n1.Native(binary);p.native=native
    context={};max_shift=prior['max_one_sided_relative_energy_shift']
    def coefficients(self,t):
        nonlocal max_shift
        if t!=self.cache_t:
            g=self.provider.geometry(t);e,mu,ratio=self.char.geometry_nodes(self.q,self.mu,g)
            ee=e.copy();lower=context['lower'];upper=context['upper']
            lo=ee<=lower;hi=ee>=upper
            ee[lo]=np.nextafter(lower[lo],np.inf);ee[hi]=np.nextafter(upper[hi],0.)
            relative=np.max(abs(ee-e)/e)
            if relative>64*np.finfo(float).eps:raise ValueError(f'EVENT_SPECTRAL_CELL_MISMATCH:{relative}')
            max_shift=max(max_shift,float(relative))
            inside=context['source_inside'];source=np.zeros(self.n)
            source[inside]=self.provider.tables['emissivity'].photon_emission_log(ee[inside],g['z'])*self.weights[inside]/ratio[inside]**3
            sigma=np.zeros((self.n,3));active=context['active']
            sigma[active]=self.native.call('SIGMA',ee[active]).reshape(-1,3)
            self.cache=(g,ee,mu,source,sigma);self.cache_t=t
        return self.cache
    p.coefficients=types.MethodType(coefficients,p)
    started=time.monotonic();p.started=started;p.last_progress=started;failure=None;solver=None;status='RUNNING'
    try:
        for segment in range(start_segment,len(boundaries)-1):
            u0,u1=boundaries[segment:segment+2]
            restart_u=resume_u if segment==start_segment else float(u0)
            em=characteristics.geometry_nodes(p.q,p.mu,provider.geometry(float(.5*(u0+u1)*p.end)))[0]
            cell=np.searchsorted(knots,em,side='right')
            extended=np.r_[0.,knots,np.inf]
            context.update(lower=extended[cell],upper=extended[cell+1],active=np.flatnonzero(em<50000.),
                           source_inside=(em>10.)&(em<50000.))
            p.cache_t=None
            active=context['active']
            keep=np.r_[np.arange(4),4+active,np.arange(4+p.n,10+p.n)]
            # Omitted variables have analytic N=0 on this whole segment. Newly
            # entering nodes inherit their untouched exact-zero initial state.
            dormant=np.setdiff1d(np.arange(p.n),active)
            if np.any(full[4+dormant]!=0):raise ValueError('NONZERO_DORMANT_STATE_NOT_DISCARDED')
            def expand(reduced):
                out=np.zeros_like(full);out[keep]=reduced;return out
            def rhs(u,v):return p.rhs(u,expand(v))[keep]
            def jac(u,v):return p.jac(u,expand(v))[keep][:,keep]
            if segment==start_segment:
                start_row=p.output(resume_u,full)
                start_evidence=dict(u=resume_u,segment=segment,row=start_row,
                    scaled_state_sha256=hashlib.sha256(np.asarray(full,dtype='<f8').tobytes()).hexdigest(),
                    scope='Extra continuation boundary; not an added common sample epoch')
                (args.output/'CONTINUATION_START.json').write_text(json.dumps(start_evidence,indent=2,allow_nan=False)+'\n')
                accepted_energy=max(accepted_energy,abs(start_row['energy_ledger_scaled']))
                accepted_number=max(accepted_number,abs(start_row['number_ledger_scaled']))
                if not all(np.isfinite(v) for v in start_row.values()) or start_row['min_N_ref']<0:
                    raise ValueError('INVALID_CONTINUATION_START_DOMAIN')
                if accepted_energy>1e-9 or accepted_number>1e-9:
                    raise ValueError('CONTINUATION_START_LEDGER_GATE')
            solver=BDF(rhs,restart_u,full[keep],float(u1),rtol=args.rtol,atol=args.rtol*1e-8,
                       jac=jac,max_step=args.max_step)
            while solver.status=='running':
                if time.monotonic()-started>args.additional_wall_seconds:raise TimeoutError('DECLARED_WALL_BUDGET_EXCEEDED')
                msg=solver.step()
                if solver.status=='failed':raise RuntimeError(msg)
                current=expand(solver.y)
                physical=current*p.scales
                accepted_finite=accepted_finite and bool(np.isfinite(physical).all())
                h,he1,he2,w=physical[:4];fhe=p.g0['nHe']/p.g0['nH']
                temperature=2*w*base.EV/(3*base.KB*(1+fhe+h+fhe*(he1+2*he2)))
                gas_values=np.array([h,he1,he2,1-he1-he2,temperature])
                gas_lo=np.minimum(gas_lo,gas_values);gas_hi=np.maximum(gas_hi,gas_values)
                accepted_gas_valid=accepted_gas_valid and bool(accepted_finite and
                    0<=h<=1 and he1>=0 and he2>=0 and he1+he2<=1 and 1<=temperature<=1e6)
                if not accepted_gas_valid:raise ValueError('ACCEPTED_GAS_OR_FINITE_DOMAIN')
                accepted_min=min(accepted_min,float(physical[4:4+p.n].min()))
                # All full numerical states are retained in restart artifacts;
                # strict accepted positivity is a gate, never a clip operation.
                if physical[4:4+p.n].min()<0:raise ValueError('ACCEPTED_NEGATIVE_ACTIVE_PHOTON')
                dense=solver.dense_output()
                while si<len(samples) and samples[si]<=solver.t:
                    u=float(samples[si]);v=expand(dense(u));row=p.output(u,v)
                    rows.append(row);sample_u.append(u);sample_v.append(v);si+=1
                # Assess accepted ledger at each segment endpoint below, and
                # retain requested common epochs without extra native calls.
            full=expand(solver.y);completed_segments+=1
            endpoint=p.output(float(u1),full)
            accepted_energy=max(accepted_energy,abs(endpoint['energy_ledger_scaled']))
            accepted_number=max(accepted_number,abs(endpoint['number_ledger_scaled']))
            progress=dict(completed_segments=completed_segments,total_segments=len(boundaries)-1,
                          u=float(u1),z=endpoint['z'],rhs_calls=p.calls,elapsed_s=prior['elapsed_s']+time.monotonic()-started,
                          continuation_elapsed_s=time.monotonic()-started,
                          energy_ledger_max=accepted_energy,number_ledger_max=accepted_number)
            (args.output/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
            if segment%16==0:
                np.savez_compressed(args.output/'RESTART.npz',u=u1,scaled_y=full,scales=p.scales)
        status='COMPUTED_NOT_REVIEWED'
    except Exception as exc:
        status='FAILED_PRESERVED'
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
                     completed_segments=completed_segments,last_accepted_u=None if solver is None else float(solver.t))
        (args.output/'FIRST_FAILURE.json').write_text(json.dumps(failure,indent=2)+'\n')
        if solver is not None:np.savez_compressed(args.output/'LAST_ACCEPTED.npz',u=solver.t,scaled_y=expand(solver.y),scales=p.scales)
    finally:native.close()
    np.savez_compressed(args.output/'history.npz',u=sample_u,scaled_states=np.array(sample_v),scales=p.scales,q=p.q,mu=p.mu,weights=p.weights)
    energy_max=max(accepted_energy,max(abs(row['energy_ledger_scaled']) for row in rows))
    number_max=max(accepted_number,max(abs(row['number_ledger_scaled']) for row in rows))
    checks=dict(whole_interval=status=='COMPUTED_NOT_REVIEWED',sampled_positive=all(row['min_N_ref']>=0 for row in rows),
                accepted_positive=accepted_min>=0,energy_ledger=energy_max<=1e-9,number_ledger=number_max<=1e-9,
                accepted_finite=accepted_finite,accepted_gas_domain=accepted_gas_valid)
    result=dict(status=status,checks=checks,completed_segments=completed_segments,elapsed_s=prior['elapsed_s']+time.monotonic()-started,
                rhs_calls=p.calls,jac_calls=p.jcalls,n_nodes=p.n,max_local_number=p.max_local_number,max_local_energy=p.max_local_energy,
                max_endpoint_energy_ledger=accepted_energy,max_endpoint_number_ledger=accepted_number,
                max_energy_ledger=energy_max,max_number_ledger=number_max,
                accepted_gas_min=dict(zip(['xHII','xHeII','xHeIII','xHeI','T_K'],gas_lo.tolist())),
                accepted_gas_max=dict(zip(['xHII','xHeII','xHeIII','xHeI','T_K'],gas_hi.tolist())),
                min_accepted_photon_energy=accepted_min,max_one_sided_relative_energy_shift=max_shift,history=rows,failure=failure)
    result['continuation']=dict(chain_sha256=sha(args.output/'CONTINUATION.json'),
        phase_elapsed_s=time.monotonic()-started,original_elapsed_s=prior['elapsed_s'],
        phase_rhs_calls=p.calls-prior['rhs_calls'],phase_jac_calls=p.jcalls-prior['jac_calls'],
        original_failure_preserved='predecessor/FIRST_FAILURE.json',extra_bdf_initializations=1,
        start_evidence_sha256=sha(args.output/'CONTINUATION_START.json') if (args.output/'CONTINUATION_START.json').exists() else None,
        previous_prefix_samples=decision['prefix_samples'],comparison_supported=False,
        original_raw_files_unchanged=all(sha(original/name)==value for name,value in manifest['original_files_sha256'].items()))
    (args.output/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['history','failure']},indent=2),flush=True)
    return 0 if all(checks.values()) and result['continuation']['original_raw_files_unchanged'] else 1

if __name__=='__main__':raise SystemExit(main())
