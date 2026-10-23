"""Finite segmented Radau execution; raw states saved after each segment."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from angular_model import BASE, END, Reduced, FullOracle, ATOM, CT, NN, VGRAD

CASES = {
  1:dict(name='grid044_M4_nominal',M=4),
  2:dict(name='grid022_M4_nominal',M=4,background='grid022'),
  3:dict(name='grid044_M4_tight',M=4,tight=True),
  4:dict(name='grid044_M4_oracle',M=4,oracle=True),
  5:dict(name='grid044_M4_reverse',M=4,sign=-1),
  6:dict(name='grid044_M4_zeroUV',M=4,zero_uv=True),
  7:dict(name='grid044_M4_ionized',M=4,ionized=True),
  8:dict(name='grid044_M8_tight',M=8,tight=True),
  9:dict(name='grid044_M16_tight',M=16,tight=True),
  10:dict(name='grid044_M4_mean_tight',M=4,tight=True,sign=0),
}
RESULTS = BASE/'results'


def dump(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def store_reporting_samples(sol,samples,mask,sample_t):
    if np.any(mask):
        samples[:,mask]=sol.sol(sample_t[mask])


def repair_regression():
    class Fake:
        calls=0
        def sol(self,t):
            self.calls+=1
            assert len(t)>0
            return np.ones((2,len(t)))
    fake=Fake();samples=np.zeros((2,3));t=np.arange(3.)
    store_reporting_samples(fake,samples,np.array([False,False,False]),t)
    assert fake.calls==0 and np.all(samples==0)
    store_reporting_samples(fake,samples,np.array([False,True,False]),t)
    assert fake.calls==1 and np.all(samples[:,1]==1) and np.all(samples[:,[0,2]]==0)
    dump(RESULTS/'targeted_repair_regression.json',{'pass':True,'new_IVPs':0,'empty_mask_calls':0,'nonempty_mask_calls':fake.calls})


def make(case_id):
    spec = CASES[case_id].copy()
    name = spec.pop('name')
    tight = spec.pop('tight',False)
    full = spec.pop('oracle',False)
    return name,(FullOracle if full else Reduced)(**spec),tight


def validate_history(h,model):
    maximum = {k:float(np.max(abs(h[k]))) for k in ['energy_residual','charge_residual','photon_residual','nucleus_residual']}
    limits = dict(energy_residual=2e-8,charge_residual=2e-9,photon_residual=2e-9,nucleus_residual=2e-9)
    checks = {k:maximum[k]<=limits[k] for k in limits}
    accepted=h.get('accepted_Y',h['Y'])
    minimum_fraction = min(float(np.min(h['fractions'])),float(np.min(accepted[model.ax])))
    checks['fraction_negativity'] = minimum_fraction >= -1e-10
    electrons=(ATOM.q*ATOM.scales)@accepted[model.ax] if model.oracle else VGRAD@accepted[model.ax]
    accepted_T=accepted[model.iu]/(CT*(NN+electrons))
    temperatures=np.r_[h['temperature_K'],accepted_T]
    checks['temperature_domain'] = bool(np.all((temperatures>=3)&(temperatures<=1e9)))
    zero_limit=64*np.finfo(float).eps if model.oracle else 0.
    zero_max=float(h['zero_face_scaled_max_abs'])
    if model.oracle:
        zero_max=max(zero_max,float(np.max(abs(accepted[[0,5,6]]))))
    checks['zero_face_numerical_bound' if model.oracle else 'structural_n_T_exact_zero'] = bool(zero_max<=zero_limit)
    # Photon sign is observed, including the direct oracle's possible tiny
    # negatives; the optical system reconstructs nonnegative counts.
    return {'checks':checks,'all_pass':all(checks.values()),'maxima':maximum,
            'limits':limits,'minimum_fraction':minimum_fraction,
            'minimum_photon':float(np.min(h['photon_groups'])),
            'zero_face_scaled_max_abs':zero_max,'zero_face_scaled_limit':zero_limit,
            'temperature_range_K':[float(np.min(temperatures)),float(np.max(temperatures))],
            'temperature_sample_range_K':[float(np.min(h['temperature_K'])),float(np.max(h['temperature_K']))],
            'temperature_accepted_range_K':[float(np.min(accepted_T)),float(np.max(accepted_T))],
            'energy_denominator_eV_per_Href':float(h['energy_scale_eV_per_Href']),
            'count_denominator_per_Href':float(h['count_scale_per_Href'])}


def run_case(case_id,resume=False):
    name,model,tight = make(case_id)
    final = RESULTS/f'{name}.json'
    if final.exists() and not resume:
        raise RuntimeError(f'CASE_ALREADY_HAS_OUTCOME: {name}; no automatic repeated IVP')
    started, cpu = time.perf_counter(),time.process_time()
    boundaries = model.boundaries()
    sample_t = np.linspace(0,END,201)
    samples = np.full((model.size,201),np.nan)
    samples[:,0] = model.y0
    times,states = [0.],[model.y0.copy()]
    y = model.y0.copy()
    segments=[]
    prior=None
    resume_eta=0.
    if resume:
        prior=json.loads(final.read_text())
        if prior['status']!='FAILED':
            raise RuntimeError('RESUME_REQUIRES_FAILED_OUTCOME')
        for path in [final,RESULTS/f'{name}_partial.json',RESULTS/f'{name}_partial.npz']:
            backup=path.with_name(path.stem+'_attempt1'+path.suffix)
            if backup.exists():
                raise RuntimeError('ORIGINAL_ATTEMPT_ALREADY_PRESERVED')
            shutil.copyfile(path,backup)
        saved_meta=json.loads((RESULTS/f'{name}_partial.json').read_text())
        with np.load(RESULTS/f'{name}_partial.npz',allow_pickle=False) as saved:
            times=saved['accepted_eta'].tolist()
            states=list(saved['accepted_Y'].T.copy())
            assert np.array_equal(saved['sample_eta'],sample_t)
            samples=saved['sample_Y'].copy()
        resume_eta=float(times[-1]);y=states[-1].copy()
        segments=saved_meta['segments']
        assert segments[-1]['hi']==resume_eta and resume_eta in boundaries
    if model.oracle:
        rtol=2e-10
        atol=np.full(model.size,2e-12)
        atol[model.gx]=2e-13
        atol[model.itau]=2e-13
    else:
        rtol=2e-11 if tight else 2e-9
        atol=np.full(model.size,2e-13 if tight else 2e-11)
        atol[model.itau]=2e-14 if tight else 2e-12
    metadata={'case_id':case_id,'name':name,'state_size':model.size,'M':model.M,
              'oracle':model.oracle,'rtol':rtol,'atol':atol.tolist(),
              'method':'Radau','Jacobian':'independent numerical' if model.oracle else 'analytic state Jacobian',
              'crossings':model.crossings,'background':model.bg.case,'background_sign':model.bg.sign,
              'endpoint_cross_sections':'interior eta offset min(1e-12,segmentwidth*1e-8); actual eta for geometry/work',
              'status':'RUNNING','segments':segments}
    if resume:
        metadata['resume']={'eta':resume_eta,'accepted_nodes':len(times),
                            'report_times_filled':int(np.sum(np.isfinite(samples).all(axis=0))),
                            'prior_attempt':final.stem+'_attempt1.json','earlier_intervals_repeated':0}
    dump(RESULTS/f'{name}_partial.json',metadata)
    try:
        for lo,hi in zip(boundaries[:-1],boundaries[1:]):
            if hi<=resume_eta:
                continue
            model.segment=(lo,hi)
            stamp=time.perf_counter()
            sol=solve_ivp(model.rhs,(lo,hi),y,method='Radau',jac=None if model.oracle else model.jacobian,
                          rtol=rtol,atol=atol,dense_output=True)
            y=sol.y[:,-1].copy()
            times.extend(sol.t[1:].tolist());states.extend(sol.y[:,1:].T.copy())
            mask=(sample_t>lo)&(sample_t<=sol.t[-1])
            store_reporting_samples(sol,samples,mask,sample_t)
            segments.append({'lo':lo,'hi':hi,'last_eta':float(sol.t[-1]),'success':bool(sol.success),
                             'message':sol.message,'accepted_nodes':len(sol.t),'nfev':sol.nfev,'njev':sol.njev,
                             'nlu':sol.nlu,'solver_wall_s':time.perf_counter()-stamp})
            metadata['solver_cpu_s_so_far']=time.process_time()-cpu
            metadata['wall_s_so_far']=time.perf_counter()-started
            np.savez(RESULTS/f'{name}_partial.npz',accepted_eta=np.array(times),accepted_Y=np.array(states).T,
                     sample_eta=sample_t,sample_Y=samples)
            dump(RESULTS/f'{name}_partial.json',metadata)
            if not sol.success:
                raise RuntimeError(f'IVP_FAILURE: {name}: {sol.message}')
        if not np.isfinite(samples).all():
            raise RuntimeError('MISSING_COMMON_SAMPLES')
        model.segment=None
        h=model.observables(sample_t,samples)
        h['accepted_eta'],h['accepted_Y']=np.array(times),np.array(states).T
        h['support_boundaries']=np.array(boundaries)
        np.savez_compressed(RESULTS/f'{name}.npz',**h)
        metadata['validation']=validate_history(h,model)
        metadata['status']='COMPLETED' if metadata['validation']['all_pass'] else 'COMPLETED_WITH_ACCEPTANCE_FAILURE'
    except BaseException as exc:
        metadata['status']='FAILED'
        metadata['exception']=repr(exc)
        metadata['traceback']=traceback.format_exc()
        raise
    finally:
        np.savez(RESULTS/f'{name}_partial.npz',accepted_eta=np.array(times),accepted_Y=np.array(states).T,
                 sample_eta=sample_t,sample_Y=samples)
        metadata['child_case_wall_s']=time.perf_counter()-started
        metadata['child_case_cpu_s']=time.process_time()-cpu
        if prior is not None:
            metadata['resumed_invocation_case_wall_s']=metadata['child_case_wall_s']
            metadata['resumed_invocation_case_cpu_s']=metadata['child_case_cpu_s']
            metadata['child_case_wall_s']+=prior['child_case_wall_s']
            metadata['child_case_cpu_s']+=prior['child_case_cpu_s']
        metadata['solver_wall_s']=sum(s['solver_wall_s'] for s in segments)
        metadata['accepted_nodes_total']=len(times)
        metadata['nfev_total']=sum(s['nfev'] for s in segments)
        metadata['njev_total']=sum(s['njev'] for s in segments)
        metadata['nlu_total']=sum(s['nlu'] for s in segments)
        dump(final,metadata)
    print(json.dumps({'case':name,'status':metadata['status'],'wall_s':metadata['child_case_wall_s'],
                      'cpu_s':metadata['child_case_cpu_s'],'nfev':metadata['nfev_total'],
                      'accepted_nodes':len(times),'validation':metadata['validation']},allow_nan=False),flush=True)
    if not metadata['validation']['all_pass']:
        raise RuntimeError(f'TRAJECTORY_ACCEPTANCE_FAILURE: {name}')


def finalize_saved_oracle():
    name,model,tight=make(4)
    path=RESULTS/f'{name}.json'
    metadata=json.loads(path.read_text())
    assert metadata['status']=='FAILED'
    for p in [path,RESULTS/f'{name}_partial.json',RESULTS/f'{name}_partial.npz']:
        backup=p.with_name(p.stem+'_attempt1'+p.suffix)
        if backup.exists():
            if backup.read_bytes()!=p.read_bytes():
                raise RuntimeError('PRESERVED_ORACLE_ATTEMPT_DIFFERS')
        else:
            shutil.copyfile(p,backup)
    with np.load(RESULTS/f'{name}_partial.npz',allow_pickle=False) as d:
        eta,Y=d['sample_eta'].copy(),d['sample_Y'].copy()
        accepted_t,accepted_Y=d['accepted_eta'].copy(),d['accepted_Y'].copy()
    assert accepted_t[-1]==END and np.isfinite(Y).all()
    model.segment=None
    h=model.observables(eta,Y)
    h['accepted_eta'],h['accepted_Y']=accepted_t,accepted_Y
    h['support_boundaries']=np.array(model.boundaries())
    np.savez_compressed(RESULTS/f'{name}.npz',**h)
    metadata['validation']=validate_history(h,model)
    metadata['status']='COMPLETED' if metadata['validation']['all_pass'] else 'COMPLETED_WITH_ACCEPTANCE_FAILURE'
    metadata['summary_only_repair']={'raw_states_changed':False,'IVPs_replayed':0,
        'zero_face_scaled_tolerance':64*np.finfo(float).eps,
        'original_failure_record':name+'_attempt1.json'}
    dump(path,metadata)
    print(json.dumps({'case':name,'summary_only_repair':True,'validation':metadata['validation']}),flush=True)
    if not metadata['validation']['all_pass']:
        raise RuntimeError('ORACLE_SUMMARY_ACCEPTANCE_FAILURE')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',type=int,nargs='*',default=[])
    parser.add_argument('--checks',action='store_true')
    parser.add_argument('--repair-regression',action='store_true')
    parser.add_argument('--resume-case1',action='store_true')
    parser.add_argument('--finalize-oracle-saved',action='store_true')
    args=parser.parse_args()
    RESULTS.mkdir(exist_ok=True)
    if args.repair_regression:
        repair_regression()
    if args.finalize_oracle_saved:
        finalize_saved_oracle()
    dump(RESULTS/'environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
         'threads':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
         'requested_executor':'gpt-6.1-sol/high','observed_executor':'runtime model identity unavailable',
         'commands':sys.argv,'scope':'prescribed background conditional trace experiment'})
    if args.checks:
        # Reuse the single authorized, already executed named check suite.
        # This avoids spending a new process on unchanged successful checks.
        checks=json.loads((BASE/'checks_pre_ivp.json').read_text())
        checks['reuse']='same frozen implementation; original pure-algebra execution, no repeated checks'
        dump(RESULTS/'algebra_checks.json',checks)
        if not checks.get('overall_pass',False):
            raise RuntimeError('ALGEBRA_CHECKS_FAILED')
    for case_id in args.cases:
        run_case(case_id,resume=case_id==1 and args.resume_case1)


if __name__=='__main__':
    main()
