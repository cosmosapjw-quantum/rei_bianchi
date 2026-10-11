"""Frozen endpoint Picard only; baseline and seed native results are reused."""
import argparse
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import numpy as np

UNIT=Path(__file__).resolve().parent;BASE=UNIT.parent;PREV=BASE/'q1b_gas_residual06'
sys.path.insert(0,str(PREV))
spec=importlib.util.spec_from_file_location('q1b_frozen_residual_validation06',PREV/'validate.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
from residual import Residual, admissible, norm
from opacity_native import EV_ERG
RESULT=v.RESULT
RESULT.update({'unit':'Q1B7_SINGLE_ENDPOINT_PICARD01','iterations':[],'scope':'Single birth cell only; no full UVB field or cosmological interval','history_checkpoint':False})
RESULT['execution'].update({'gas_solve':0,'history_steps':0,'fresh_GL128':0,'final_GL64':0})

def run():
    priorpath=PREV/'evidence/attempt1/RESULT.json'
    v.need(v.digest(priorpath)=='33e9220d587b7e73b1f58f3dda24f338c80d21dcd88415eb915d749f06459bc1','SEED_RESULT_IDENTITY')
    prior=json.loads(priorpath.read_text());pins=prior['input_sha256'].copy()
    pins.update({str((PREV/'residual.py').relative_to(v.ROOT)):'68ed824baf025d821f001253fcfd2be81682b98e0c4c8893873d00696d809107',str((PREV/'validate.py').relative_to(v.ROOT)):'95bfb33f7720e205e38559e43290af2d926d923b14ed0e5c6a1b3d1a2788257d'})
    v.need(all(v.digest(v.ROOT/p)==s for p,s in pins.items()),'FROZEN_SOURCE_IDENTITY')
    v.need(json.loads((PREV/'INDEPENDENT_REVIEW.json').read_text())['decision']=='PASS_GAS_RESIDUAL_VALUE_AND_ADMISSIBLE_TRIAL_SCOPED','PRIOR_REVIEW_REQUIRED')
    RESULT['input_sha256']=pins;RESULT['seed_result_sha256']=v.digest(priorpath)
    frozen=prior['frozen'];T=frozen['T_s'];g=frozen['geometry'];y0=np.array(frozen['y0']);R=frozen['R'];mu=frozen['mu']
    trial=prior['admissible_residual_decreasing_trial'];v.need(trial['theta']==1.,'FROZEN_THETA_SEED')
    seed=[p for p in prior['points'] if p['order']==128 and p['h']==T and p['y']==trial['y']]
    v.need(len(seed)==1,'UNIQUE_SAVED_SEED');seed=seed[0]
    entry=json.loads((BASE/'q1b_source_entry04/evidence/attempt1/RESULT.json').read_text())
    v.need(v.digest(BASE/'q1b_source_entry04/evidence/attempt1/RESULT.json')=='6dffb2891b0146ddb7f5774da238f2f38c864780cd4f72ee71782e6b9ef8b418','INCIDENT_IDENTITY')
    incident=entry['actual_runs'][0]['steps'][0];nodes={64:[],128:[]};caller=v.Caller()
    try:
        for order in [64,128]:
            for j in range(2):
                q,p,fit=v.fit_positive(incident['incident_N'][j],incident['incident_U_eV'][j],R,50000.,50000./R,order)
                v.need(caller.counts['SIGMA']<4 and caller.counts['SIGMA_energies']+len(q)<=384,'SIGMA_CAP')
                nodes[order].append((q,p,caller.opacity.sigma(R*q)))
        e=Residual(caller,g,y0,T,T,R,mu,nodes,RESULT['execution'])
        E_scale=float(np.dot(e.energy_gradient,y0)+EV_ERG*sum(incident['incident_U_eV']))
        v.need(E_scale>0 and np.isfinite(E_scale),'FIXED_ENERGY_SCALE')
        RESULT['fixed']={'T_s':T,'geometry':g,'R':R,'y0':y0,'seed_y':seed['y'],'seed_native':seed['native'],'seed_norm':seed['norm'],'energy_scale_erg':E_scale,'energy_gradient':e.energy_gradient,'source_radiation_work_eV_reference':incident['work_eV'],'baseline_and_seed_replayed':False}
        previous_y=np.array(seed['y']);previous_native=np.array(seed['native']);previous_norm=seed['norm']
        RESULT['execution']['gas_solve']=1
        for k in range(1,7):
            y=y0+T*previous_native[:4];admissible(y,g)
            v.need(caller.counts['CELL_RHS_V1']<7 and RESULT['execution']['positive_maps']+2<=14,'CORRECTION_CAP')
            RESULT['execution']['fresh_GL128']+=1
            fine=v.point(e,y,128);update=y-previous_y
            energy_res=float(np.dot(abs(e.energy_gradient),abs(fine['residual']))/E_scale)
            energy_update=float(np.dot(abs(e.energy_gradient),abs(update))/E_scale)
            update_norm=norm(update,y0);converged=fine['norm']<=1e-12 and update_norm<=1e-12 and energy_res<=1e-12 and energy_update<=1e-12
            ratio=fine['norm']/previous_norm if previous_norm!=0 else (0. if fine['norm']==0 else None)
            row={'iteration':k,'y':y.copy(),'residual_norm':fine['norm'],'update_norm':update_norm,'energy_residual':energy_res,'energy_update':energy_update,'observed_ratio':ratio,'converged':converged,'ionic_own_relative':[{'component':i,'absolute_residual':float(abs(fine['residual'][i])),'own_relative':float(abs(fine['residual'][i]/y[i])) if y[i]!=0 else None,'zero_state':bool(y[i]==0)} for i in range(3)]}
            RESULT['iterations'].append(row)
            if converged:break
            v.need(ratio is not None and ratio<=.5,'PICARD_OBSERVED_NONCONTRACTION_HOLD')
            previous_y=y.copy();previous_native=fine['native'].copy();previous_norm=fine['norm']
        else:raise ArithmeticError('PICARD_ITERATION_CAP_HOLD')
        RESULT['execution']['final_GL64']+=1
        v.need(caller.counts['CELL_RHS_V1']<7 and RESULT['execution']['positive_maps']+2<=14,'FINAL_COARSE_CAP')
        coarse=v.point(e,y,64)
        v.check('final_GL_value_opacity',coarse['values'],fine['values'],1e-7)
        coarse_energy=float(np.dot(abs(e.energy_gradient),abs(coarse['residual']))/E_scale)
        v.need(coarse['norm']<=1e-12 and coarse_energy<=1e-12,'ENDPOINT_QUADRATURE_RESIDUAL_BUDGET_HOLD')
        RESULT['final_coarse']={'norm':coarse['norm'],'energy_defect':coarse_energy}
        RESULT['local_endpoint_solution']={'y':y.copy(),'fine':fine,'coarse':coarse,'prospective_counters_erg':{'gas_work':T*fine['work']['gas_work_rate'],'escape':T*fine['native'][4],'CMB_to_gas':T*fine['native'][14],'absorbed':fine['energy_absorbed_erg']},'history_checkpoint':False}
    finally:RESULT['execution'].update(caller.counts);caller.close()
    v.need(all(v.digest(v.ROOT/p)==s for p,s in pins.items()),'FROZEN_SOURCE_CHANGED')
    RESULT['outcome']='PASS_SINGLE_CELL_ENDPOINT_PICARD_SCOPED';RESULT['next']='COUPLED_SOURCE_ENTRY_TIME_BUDGET01: same interval1/2/4; reuse1 and run6newsubsteps'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_ENDPOINT_PICARD07_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;v.dump(out/'RESULT.json',RESULT);print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}));return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','120s','prlimit','--as=2147483648','--cpu=120','--fsize=16777216','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    v.dump(out/'STARTED.json',{'command':cmd,'cwd':str(v.ROOT),'source_sha256':{p.name:v.digest(p) for p in UNIT.iterdir() if p.is_file()},'prior_cumulative':json.loads((UNIT/'CONTRACT.json').read_text())['prior_cumulative']})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=v.ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'perprocess; childCPU measured separately','files':{p.name:{'sha256':v.digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(z['bytes'] for z in receipt['files'].values())<=16777216;v.dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode

if __name__=='__main__':raise SystemExit(main())
