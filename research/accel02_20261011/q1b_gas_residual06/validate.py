"""One bounded endpoint residual/trial experiment; no committed time step."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import numpy as np
from residual import Residual, admissible, BASE
from positive_entry import fit_positive
sys.path.insert(0,str(BASE/'q1b_selective_native_bind03'))
from caller import Caller
from provider import HistoryProvider
UNIT=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
RESULT={'unit':'Q1B6_GAS_RESIDUAL_VALUE_TRIAL01','checks':[],'points':[],'trials':[],
        'execution':{'native_processes':0,'SIGMA':0,'SIGMA_energies':0,'CELL_RHS_V1':0,'positive_maps':0,'trial_candidates':0,'source_integrations':0,'build':0,'Jacobian':0,'Newton':0,'gas_solve':0,'committed_timestep':0,'history':0},
        'executor':'controller_direct_owner_authorized','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED','global_admission':'HOLD'}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj):
    def cv(x):
        if isinstance(x,np.ndarray):return x.tolist()
        if isinstance(x,np.generic):return x.item()
        raise TypeError(type(x).__name__)
    with Path(p).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False,default=cv)
def need(ok,label):
    if not ok:raise AssertionError(label)
def check(label,a,b,tol,scale=None):
    a,b=np.broadcast_arrays(np.asarray(a,float),np.asarray(b,float));s=abs(b) if scale is None else np.broadcast_to(np.asarray(scale),a.shape)
    d=abs(a-b);err=np.divide(d,s,out=np.zeros_like(d),where=s!=0)
    ok=bool(np.isfinite(a).all() and np.isfinite(b).all() and np.all(d[s==0]==0) and np.all(err<=tol))
    RESULT['checks'].append({'label':label,'maximum':float(np.max(err)),'tolerance':tol,'pass':ok});need(ok,'HOLD_'+label)
def point(e,y,order,zero=False):
    row=e.evaluate(y,order,zero);RESULT['points'].append(row)
    need(np.isfinite(row['residual']).all(),'NONFINITE_RESIDUAL')
    ei=row['energy_identity'];check('gas_energy_residual_identity',ei['lhs'],ei['rhs'],1e-12,ei['termwise_scale'])
    check('native_local_residual',row['native'][12:14],0.,1e-12,1.)
    for pair in row['photon_pairs']:
        check('photon_number_pair',pair['number_after_abs'],pair['number_before'],1e-12)
        check('photon_energy_pair',pair['energy_after_abs'],pair['energy_before'],1e-12)
    return row
def pair(e,y):
    fine=point(e,y,128);coarse=point(e,y,64)
    check('GL_value_map',coarse['values'],fine['values'],1e-7)
    RESULT.setdefault('GL_gas_residual_differences',[]).append({'y':y.copy(),'difference':coarse['residual']-fine['residual'],'fine_norm':fine['norm'],'coarse_norm':coarse['norm']})
    return fine,coarse

def run():
    entrypath=BASE/'q1b_source_entry04/evidence/attempt1/RESULT.json'
    workpath=BASE/'q1b_work_gas_jvp05/evidence/attempt1/RESULT.json'
    need(digest(entrypath)=='6dffb2891b0146ddb7f5774da238f2f38c864780cd4f72ee71782e6b9ef8b418','ENTRY_IDENTITY')
    need(digest(workpath)=='9b5f1d4190f67207b72df3e59d869c0dd07b86f47793336d38b850201f6731f1','WORK_IDENTITY')
    entry=json.loads(entrypath.read_text());pins=json.loads(workpath.read_text())['input_sha256'].copy()
    pins[str((BASE/'q1b_work_gas_jvp05/adapter.py').relative_to(ROOT))]='c7f1cac3ecbb4a8dc8edfc62f1c7458fff77e9ff6633cadb0cfb1c8e4c15f3c5'
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'FROZEN_INPUT_IDENTITY');RESULT['input_sha256']=pins
    for p,decision in [(BASE/'q1b_source_entry04/INDEPENDENT_REVIEW.json','PASS_SOURCE_ENTRY_FIXED_BATH_SCOPED'),(BASE/'q1b_work_gas_jvp05/INDEPENDENT_REVIEW.json','PASS_WORK_SPLIT_GAS_ABSORPTION_JVP_SCOPED')]:
        need(json.loads(p.read_text())['decision']==decision,'REVIEW_REQUIRED')
    provider=HistoryProvider(r=0.);T=entry['T_s'];g=provider.geometry(T);y0=provider.initial_gas.copy()
    need(T==2827462976819.2324 and T==2.**-12/provider.geometry(0.)['H'],'FROZEN_TIME_IDENTITY')
    R=math.exp(-math.log1p(provider.background._relative_volume_increment(T))/3)
    g0=provider.geometry(0.);check('reference_nuclei',np.array([g['nH'],g['nHe']])*g['a_rel']**3,[g0['nH'],g0['nHe']],1e-12)
    for bad in [np.array([-1.,0.,0.,y0[3]]),np.array([.2,.7,.4,y0[3]]),np.array([.2,.3,.1,0.])]:
        before=bad.copy()
        try:admissible(bad,g)
        except ValueError:pass
        else:raise AssertionError('PRE_NATIVE_DOMAIN_ACCEPTED')
        need(np.array_equal(before,bad),'DOMAIN_CHECK_MUTATED_INPUT')
    step=entry['actual_runs'][0]['steps'][0];nodes={64:[],128:[]};fit_records=[]
    caller=Caller()
    try:
        for order in [64,128]:
            for j in range(2):
                q,p,fit=fit_positive(step['incident_N'][j],step['incident_U_eV'][j],R,50000.,50000./R,order)
                need(caller.counts['SIGMA']<4 and caller.counts['SIGMA_energies']+len(q)<=384,'SIGMA_CAP')
                sigma=caller.opacity.sigma(R*q);nodes[order].append((q,p,sigma));fit_records.append({'order':order,'angle':j,'fit':fit})
        RESULT['frozen']={'T_s':T,'geometry':g,'y0':y0,'R':R,'mu':entry['cell']['mu'],'fit_records':fit_records,
                          'saved_source_GL32':step['source_GL32'],'saved_radiation_work_eV':step['work_eV'],'saved_counters_reexecuted':False}
        e=Residual(caller,g,y0,T,T,R,entry['cell']['mu'],nodes,RESULT['execution'])
        zero=point(e,y0,128,True)
        need(np.all(zero['residual']==0) and zero['energy_absorbed_erg']==0 and np.all(zero['energy_identity']['terms']==0),'ZERO_STEP_NOT_EXACT')
        baseline,_=pair(e,y0);direction=T*baseline['native'][:4];RESULT['frozen_direction']=direction.copy()
        for theta in [1.,.5,.25]:
            RESULT['execution']['trial_candidates']+=1;y=y0+theta*direction
            trial={'theta':theta,'y':y.copy(),'accepted':False};RESULT['trials'].append(trial)
            try:trial['temperature']=admissible(y,g)
            except ValueError as exc:trial['rejected_before_native']=str(exc);continue
            fine,coarse=pair(e,y);limit=(1-theta/4)*baseline['norm']
            trial.update({'norm':fine['norm'],'required_upper_bound':limit,'accepted':fine['norm']<=limit})
            if trial['accepted']:
                RESULT['admissible_residual_decreasing_trial']=trial
                break
        else:raise ArithmeticError('NO_ADMISSIBLE_RESIDUAL_DECREASING_TRIAL')
    finally:RESULT['execution'].update(caller.counts);caller.close()
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'FROZEN_INPUT_CHANGED')
    RESULT['outcome']='PASS_GAS_RESIDUAL_VALUE_AND_ADMISSIBLE_TRIAL_SCOPED'
    RESULT['next']='Single-endpoint bounded nonlinear correction contract'
    RESULT['claim']='Residual value and admissible decreasing trial only; NOT converged solution or committed timestep; history/global HOLD'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_GAS_RESIDUAL06_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;dump(out/'RESULT.json',RESULT);print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}));return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','120s','prlimit','--as=2147483648','--cpu=120','--fsize=16777216','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'source_sha256':{p.name:digest(p) for p in UNIT.iterdir() if p.is_file()},'prior_cumulative':json.loads((UNIT/'CONTRACT.json').read_text())['prior_cumulative']})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'per process; child CPU measured separately','files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(z['bytes'] for z in receipt['files'].values())<=16777216;dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode

if __name__=='__main__':raise SystemExit(main())
