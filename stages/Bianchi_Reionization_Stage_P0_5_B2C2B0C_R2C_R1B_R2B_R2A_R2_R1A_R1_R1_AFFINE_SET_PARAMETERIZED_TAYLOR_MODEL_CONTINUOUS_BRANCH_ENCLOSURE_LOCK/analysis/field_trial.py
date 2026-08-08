"""Branch-field controlled wrapper around the locked MPRK22/SDIRK2 trial."""
from __future__ import annotations
import importlib.util,sys,hashlib,math
from pathlib import Path
import numpy as np


def branch_fields(*,lo,hi,alpha=None,beta=None,v_selector=None,f_selector=None):
    lower=np.asarray(lo,dtype=np.float64);upper=np.asarray(hi,dtype=np.float64)
    if lower.shape!=upper.shape or np.any(lower>upper):raise ValueError('invalid v bounds')
    if v_selector is not None or f_selector is not None:
        sv=np.asarray(v_selector,dtype=np.float64);sf=np.asarray(f_selector,dtype=np.float64)
        if sv.shape!=lower.shape or sf.shape!=lower.shape:raise ValueError('selector shape mismatch')
        if np.any((sv<0)|(sv>1)|(sf<0)|(sf>1)):raise ValueError('selectors leave [0,1]')
        return np.ascontiguousarray(lower+sv*(upper-lower)),np.ascontiguousarray(0.1+0.9*sf)
    a=float(alpha);b=float(beta)
    if not (-1<=a<=1 and -1<=b<=1):raise ValueError('coherent coordinates leave [-1,1]')
    return np.ascontiguousarray(lower+0.5*(a+1)*(upper-lower)),np.full(lower.shape,0.55+0.45*b)


def _load(name,path):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


def load_parent_modules(repo_root:Path):
    repo=Path(repo_root).resolve()
    r1a=next(repo.glob('stages/*R2_R1A_FOUR_CORNER*'))
    r2a=next(repo.glob('stages/*R2A_ADAPTIVE_INTERNAL_MICROSTEP*'))
    trial=_load('affine_tm_parent_uncertainty_trial',r1a/'analysis/uncertainty_trial.py')
    policy=_load('affine_tm_parent_uncertainty_policy',r1a/'analysis/uncertainty_policy.py')
    picard=_load('affine_tm_parent_globalized_picard',r2a/'analysis/globalized_picard.py')
    return trial,policy,picard


def make_trial_class(repo_root:Path):
    trial_mod,policy_mod,_=load_parent_modules(repo_root)
    class BranchFieldTrial(trial_mod.UncertaintySecondOrderTrial):
        def __init__(self,*,base,lane,alpha=0.0,beta=0.0,v_selector=None,f_selector=None):
            super().__init__(base=base,lane=lane,v_policy='CELL_LOWER_STRICT',f_value=0.1)
            self.alpha=float(alpha);self.beta=float(beta)
            self.v_selector=None if v_selector is None else np.ascontiguousarray(v_selector,dtype=np.float64)
            self.f_selector=None if f_selector is None else np.ascontiguousarray(f_selector,dtype=np.float64)
        def _event_evaluation(self,state,owner,point):
            y=np.asarray(state.values,dtype=np.float64)
            volume=self.inputs.comoving_volume_cm3/(1.0+point.z)**3
            photo=self.backend.photo_fields(owner)
            lo=policy_mod.build_v_field_from_temperature('CELL_LOWER_STRICT',state.temperature_K)
            hi=policy_mod.build_v_field_from_temperature('CELL_UPPER_STRICT',state.temperature_K)
            v,f=branch_fields(lo=lo,hi=hi,alpha=self.alpha,beta=self.beta,
                              v_selector=self.v_selector,f_selector=self.f_selector)
            event=trial_mod.event_mod.evaluate_event_flux(
                populations=y[:5].T,temperature_K=state.temperature_K,
                proper_volume_cm3=volume,photo_hi=photo.HI,photo_hei=photo.HeI,
                photo_heii=photo.HeII,v=v,f=f)
            adjusted=trial_mod.fast.base.physical.PhotoFields(
                HI=photo.HI,HeI=photo.HeI,HeII=photo.HeII,
                heating=np.ascontiguousarray(photo.heating+event.resolved_ots_heating_erg_s),
                unresolved_heating=np.ascontiguousarray(photo.unresolved_heating+event.unresolved_ots_energy_erg_s))
            return event,adjusted,volume
    return BranchFieldTrial


def state_observables(state):
    y=np.asarray(state.values,dtype=np.float64);nh=y[0]+y[1];nhe=y[2]+y[3]+y[4]
    return np.ascontiguousarray(np.vstack([y[1]/nh,y[3]/nhe,y[4]/nhe,np.log(state.temperature_K)]))


def state_sha256(state):
    h=hashlib.sha256();h.update(np.ascontiguousarray(state.values,dtype='<f8').tobytes());h.update(np.ascontiguousarray(state.temperature_K,dtype='<f8').tobytes());return h.hexdigest()


def gate_trial(result):
    return bool(result.converged and result.hydrogen_residual<=1e-11 and result.helium_residual<=1e-11
                and result.owner_residual<=1e-11 and result.photon_residual<=1e-8
                and result.thermal_residual<=1e-10 and result.pds_reconstruction_residual<=1e-11
                and result.minimum_species>0 and float(result.certificate.get('max_augmented_energy_residual',math.inf))<=1e-10
                and int(result.certificate.get('branch_domain_failure_count',1))==0
                and int(result.certificate.get('legacy_rhs_calls',1))==0)


def run_endpoint(*,repo_root:Path,lane:str,alpha=0.0,beta=0.0,v_selector=None,f_selector=None,base_solver=None):
    repo=Path(repo_root).resolve();trial_mod,_,picard=load_parent_modules(repo);klass=make_trial_class(repo)
    base=base_solver or trial_mod.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=lane)
    solver=klass(base=base,lane=lane,alpha=alpha,beta=beta,v_selector=v_selector,f_selector=f_selector)
    parent=base.inputs.state0.mutable_copy();duration=base.forcing.duration_seconds(0);t0=0.0;t1=duration/2048.0;mid=0.5*t1
    full=solver.solve(state=parent.mutable_copy(),t0=t0,t1=t1,partition=2048,trial_kind='FULL')
    half1=solver.solve(state=parent.mutable_copy(),t0=t0,t1=mid,partition=4096,trial_kind='FIRST_HALF')
    half2=solver.solve(state=half1.state.mutable_copy(),t0=mid,t1=t1,partition=4096,trial_kind='SECOND_HALF') if half1.converged and half1.state is not None else None
    trials=[full,half1]+([] if half2 is None else [half2])
    converged=bool(full.converged and half1.converged and half2 is not None and half2.converged)
    local_error=float(picard.state_residual(full.state,half2.state)) if converged else math.inf
    hard=bool(converged and local_error<2e-4 and all(gate_trial(x) for x in trials))
    endpoint=None if half2 is None else half2.state
    return {
        'hard_gates_pass':hard,'local_error':local_error,'endpoint_sha256':None if endpoint is None else state_sha256(endpoint),
        'max_H_residual':float(max(x.hydrogen_residual for x in trials)),
        'max_He_residual':float(max(x.helium_residual for x in trials)),
        'max_owner_residual':float(max(x.owner_residual for x in trials)),
        'max_photon_residual':float(max(x.photon_residual for x in trials)),
        'max_thermal_residual':float(max(x.thermal_residual for x in trials)),
        'max_OTS_energy_residual':float(max(float(x.certificate.get('max_augmented_energy_residual',math.inf)) for x in trials)),
        'minimum_species':float(min(x.minimum_species for x in trials)),
        'observables':None if endpoint is None else state_observables(endpoint),
    }

__all__=['branch_fields','load_parent_modules','make_trial_class','run_endpoint','state_observables']


def _cli_main():
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--lane',required=True)
    p.add_argument('--mode',choices=('coherent','max-heii','min-heii'),required=True);p.add_argument('--alpha',type=float,default=0.0);p.add_argument('--beta',type=float,default=0.0)
    p.add_argument('--json-output',type=Path,required=True);p.add_argument('--npz-output',type=Path,required=True);a=p.parse_args()
    if a.mode=='coherent':result=run_endpoint(repo_root=a.repo,lane=a.lane,alpha=a.alpha,beta=a.beta)
    else:
        rank_path=Path(__file__).resolve().parent/'branch_rank.py';rank_mod=_load('affine_tm_field_cli_rank',rank_path)
        sv,sf=rank_mod.adversarial_selectors(a.repo)
        if a.mode=='min-heii':sv=1.0-sv;sf=np.zeros_like(sf)
        result=run_endpoint(repo_root=a.repo,lane=a.lane,v_selector=sv,f_selector=sf)
    obs=result.pop('observables')
    a.json_output.parent.mkdir(parents=True,exist_ok=True);a.npz_output.parent.mkdir(parents=True,exist_ok=True)
    a.json_output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    np.savez_compressed(a.npz_output,observables=obs)
    print(json.dumps({'lane':a.lane,'mode':a.mode,'hard':result['hard_gates_pass'],'local_error':result['local_error']}),flush=True)

if __name__=='__main__':
    _cli_main()
