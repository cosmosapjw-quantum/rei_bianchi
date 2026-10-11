"""Six new coupled diagnostic steps; stored source integration and one-step reuse."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time
import traceback
import numpy as np
UNIT=Path(__file__).resolve().parent;BASE=UNIT.parent;PREV=BASE/'q1b_gas_residual06'
sys.path.insert(0,str(PREV))
spec=importlib.util.spec_from_file_location('refinement_frozen_validation06',PREV/'validate.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
from residual import Residual, admissible, norm
from positive_entry import incident
from opacity_native import EV_ERG
RESULT=v.RESULT
RESULT.update({'unit':'Q1B8_COUPLED_SOURCE_ENTRY_TIME_DIAGNOSTIC01','runs':[],'comparisons':[],
               'scope':'SINGLE_BIRTH_CELL_CONDITIONAL_R0','production_history_checkpoint':False})
RESULT['execution'].update({'new_coupled_substeps':0,'accepted_diagnostic_steps':0,'one_step_replays':0,'source_evaluations':0,'gas_solve':0,'full_history':0})

class StepCaller:
    """Local view only. Underlying global native counts never reset."""
    def __init__(self,caller):self.caller=caller;self.counts={'CELL_RHS_V1':0}
    def submit(self,*args):
        v.need(self.caller.counts['CELL_RHS_V1']<48,'GLOBAL_CELL_CAP')
        self.counts['CELL_RHS_V1']+=1;return self.caller.submit(*args)

def counters():
    return {'injected_N':0.,'injected_eV':0.,'radiation_work_eV':0.,'count':np.zeros(3),'binding_eV':np.zeros(3),'heat_eV':np.zeros(3),'gas_work_erg':0.,'escape_erg':0.,'CMB_erg':0.,'abs_CMB_erg':0.,'nonlinear_defect_erg':0.}
def accumulate(c,source,work,fine,h):
    values=np.asarray(fine['values']);c['injected_N']+=float(np.sum(source[:,0]));c['injected_eV']+=float(np.sum(source[:,2]));c['radiation_work_eV']+=float(np.sum(work))
    for key,sl in [('count',slice(2,5)),('binding_eV',slice(5,8)),('heat_eV',slice(8,11))]:c[key]+=np.sum(values[:,sl],axis=0)
    c['gas_work_erg']+=h*fine['work']['gas_work_rate'];c['escape_erg']+=h*fine['native'][4];c['CMB_erg']+=h*fine['native'][14];c['abs_CMB_erg']+=abs(h*fine['native'][14])
    c['nonlinear_defect_erg']+=float(np.dot(fine['energy_gradient'],fine['residual']))

def finish_run(row,gradient,y_initial,initial_energy):
    c=row['counters'];y=np.asarray(row['gas']);N=np.asarray(row['N']);U=np.asarray(row['U_eV'])
    number=float(sum(N)+sum(c['count'])-c['injected_N'])
    energy=float(np.dot(gradient,y-y_initial)+EV_ERG*(sum(U)+c['radiation_work_eV']-c['injected_eV'])+c['gas_work_erg']+c['escape_erg']-c['CMB_erg'])
    scale=initial_energy+EV_ERG*c['injected_eV']+c['abs_CMB_erg']
    row['ledger']={'number_defect':number,'energy_defect_erg':energy,'energy_scale_erg':scale,'accumulated_gas_residual_erg':c['nonlinear_defect_erg']}
    v.check('partition_number_ledger',number,0.,1e-12,c['injected_N'])
    v.check('partition_combined_energy',energy,0.,1e-9,scale)
    v.check('partition_energy_vs_residual',energy,c['nonlinear_defect_erg'],1e-12,scale)

def solve_step(caller,provider,ta,tb,y_start,N,U,source,mu):
    h=tb-ta;g=provider.geometry(tb);bg=provider.background
    logra=-math.log1p(bg._relative_volume_increment(ta))/3;logrb=-math.log1p(bg._relative_volume_increment(tb))/3;R=math.exp(logrb)
    nn,uu,work=incident(N,U,logra,logrb,source)
    v.check('new_incident_energy_work',uu-U+work,source[:,2],1e-12)
    nodes={64:[],128:[]}
    for order in [64,128]:
        for j in range(2):
            q,p,fit=v.fit_positive(nn[j],uu[j],R,50000.,50000./R,order)
            v.need(caller.counts['SIGMA']<24 and caller.counts['SIGMA_energies']+len(q)<=2304,'GLOBAL_SIGMA_CAP')
            nodes[order].append((q,p,caller.opacity.sigma(R*q)))
    local={'positive_maps':0};view=StepCaller(caller);e=Residual(view,g,y_start,tb,h,R,mu,nodes,local)
    def point(y,order):
        v.need(RESULT['execution']['positive_maps']+2<=96,'GLOBAL_MAP_CAP')
        before=local['positive_maps']
        try:return v.point(e,y,order)
        finally:RESULT['execution']['positive_maps']+=local['positive_maps']-before
    row={'ta':ta,'tb':tb,'initial_gas':y_start.copy(),'geometry':g,'incident_N':nn,'incident_U_eV':uu,'radiation_work_eV':work,'iterations':[]}
    RESULT['active_substep']=row
    base=point(y_start,128);previous_y=y_start.copy();previous_native=base['native'];previous_norm=base['norm']
    scale=float(np.dot(e.energy_gradient,y_start)+EV_ERG*sum(uu));v.need(scale>0 and np.isfinite(scale),'ENERGY_SCALE')
    row['energy_scale_erg']=scale;row['baseline']=base
    RESULT['execution']['gas_solve']+=1
    for k in range(1,7):
        y=y_start+h*previous_native[:4];admissible(y,g);fine=point(y,128);update=y-previous_y
        en=float(np.dot(abs(e.energy_gradient),abs(fine['residual']))/scale);eu=float(np.dot(abs(e.energy_gradient),abs(update))/scale);un=norm(update,y_start)
        converged=fine['norm']<=1e-12 and un<=1e-12 and en<=1e-12 and eu<=1e-12
        ratio=fine['norm']/previous_norm if previous_norm!=0 else (0. if fine['norm']==0 else None)
        row['iterations'].append({'iteration':k,'y':y.copy(),'residual_norm':fine['norm'],'update_norm':un,'energy_residual':en,'energy_update':eu,'ratio':ratio,'converged':converged})
        if converged:break
        v.need(ratio is not None and ratio<=.5,'PICARD_NONCONTRACTION_HOLD')
        previous_y=y.copy();previous_native=fine['native'];previous_norm=fine['norm']
    else:raise ArithmeticError('PICARD_CAP_HOLD')
    coarse=point(y,64);v.check('substep_GL_values',coarse['values'],fine['values'],1e-7)
    v.need(coarse['norm']<=1e-12 and np.dot(abs(e.energy_gradient),abs(coarse['residual']))/scale<=1e-12,'COARSE_RESIDUAL_BUDGET_HOLD')
    row.update({'fine':fine,'coarse':coarse,'local_counts':{'CELL_RHS_V1':view.counts['CELL_RHS_V1'],'positive_maps':local['positive_maps']}})
    RESULT['execution']['accepted_diagnostic_steps']+=1
    return y.copy(),np.asarray(fine['cells'])[:,3].copy(),np.asarray(fine['cells'])[:,4].copy(),work,fine,row

def compare(co,fi,initial_energy,initial_thermal,nh,ne,w0):
    c,f=co['counters'],fi['counters'];row={'coarse':co['partitions'],'fine':fi['partitions'],'channel_diagnostics':[]};RESULT['comparisons'].append(row)
    v.check('temporal_gas_primary',np.asarray(co['gas']),np.asarray(fi['gas']),2e-6,[1.,1.,1.,w0])
    v.check('temporal_photon_N',co['N'],fi['N'],2e-6,f['injected_N'])
    for label,a,b in [('photon_U',co['U_eV'],fi['U_eV']),('binding',c['binding_eV'],f['binding_eV']),('heat',c['heat_eV'],f['heat_eV']),('radiation_work',c['radiation_work_eV'],f['radiation_work_eV'])]:v.check('temporal_'+label,a,b,2e-6,f['injected_eV'])
    for key in ['gas_work_erg','escape_erg','CMB_erg']:v.check('temporal_'+key,c[key],f[key],2e-6,initial_energy)
    row['source_counter_relative_difference']={key:abs(c[key]-f[key])/abs(f[key]) for key in ['injected_N','injected_eV']}
    for i,name in enumerate(['HI','HeI','HeII']):
        for kind in ['count','heat_eV']:
            cv,fv=float(c[kind][i]),float(f[kind][i]);delta=abs(cv-fv)
            own=delta/abs(fv) if fv!=0 else None
            effect=delta/([nh,ne,ne][i]) if kind=='count' else delta*EV_ERG/initial_thermal
            row['channel_diagnostics'].append({'species':name,'kind':kind,'coarse':cv,'fine':fv,'own_relative':own,'zero_reference_status':None if fv!=0 else ('EXACT_ZERO' if cv==0 else 'NONZERO_OVER_ZERO'),'affected_state_difference':effect,'above_local_2e_7_screen':effect>2e-7,'relative_convergence':'CHANNEL_RELATIVE_TEMPORAL_UNRESOLVED'})

def run():
    entrypath=BASE/'q1b_source_entry04/evidence/attempt1/RESULT.json';endpath=BASE/'q1b_endpoint_picard07/evidence/attempt1/RESULT.json'
    v.need(v.digest(entrypath)=='6dffb2891b0146ddb7f5774da238f2f38c864780cd4f72ee71782e6b9ef8b418','ENTRY_IDENTITY')
    v.need(v.digest(endpath)=='1ea9b74f1f7d56bafe9deed1070e0fd852761be0575e47fe76fb22a496beae8f','ENDPOINT_IDENTITY')
    entry=json.loads(entrypath.read_text());endpoint=json.loads(endpath.read_text());pins=endpoint['input_sha256'].copy()
    pins[str((BASE/'q1b_endpoint_picard07/validate.py').relative_to(v.ROOT))]='ea522a46a265f0ee11b31ee95e807bd6bf53ec9c5e174cadbffb707953000047'
    v.need(all(v.digest(v.ROOT/p)==s for p,s in pins.items()),'FROZEN_SOURCE_IDENTITY');RESULT['input_sha256']=pins
    v.need(json.loads((BASE/'q1b_endpoint_picard07/INDEPENDENT_REVIEW.json').read_text())['decision']=='PASS_SINGLE_CELL_ENDPOINT_PICARD_SCOPED','PRIOR_REVIEW')
    RESULT['reused_RESULT_sha256']={'entry04':v.digest(entrypath),'endpoint07':v.digest(endpath)}
    provider=v.HistoryProvider(r=0.);y_initial=provider.initial_gas.copy();T=entry['T_s'];g0=provider.geometry(0.);nh,ne=g0['nH'],g0['nHe'];gradient=np.asarray(endpoint['fixed']['energy_gradient'])
    initial_energy=float(np.dot(gradient,y_initial));thermal=EV_ERG*nh*y_initial[3]
    RESULT['fixed']={'T_s':T,'initial_gas':y_initial,'reference_nH':nh,'reference_nHe':ne,'gas_energy_gradient':gradient,'initial_gas_energy_erg':initial_energy,'initial_thermal_energy_erg':thermal,'source_evaluations':0,'interior_events_observed':False}
    fine=endpoint['local_endpoint_solution']['fine'];source=np.asarray(entry['actual_runs'][0]['steps'][0]['source_GL32']);work=np.asarray(entry['actual_runs'][0]['steps'][0]['work_eV']);c=counters();accumulate(c,source,work,fine,T)
    one={'partitions':1,'execution':'REUSED_NOT_REPLAYED','gas':np.asarray(fine['y']),'N':np.asarray(fine['cells'])[:,3],'U_eV':np.asarray(fine['cells'])[:,4],'counters':c};RESULT['runs'].append(one);finish_run(one,gradient,y_initial,initial_energy)
    caller=v.Caller()
    try:
        for partitions in [2,4]:
            saved=next(row for row in entry['actual_runs'] if row['partitions']==partitions)
            N=np.zeros(2);U=np.zeros(2);y=y_initial.copy();c=counters();run={'partitions':partitions,'steps':[],'counters':c};RESULT['runs'].append(run)
            for k,source_row in enumerate(saved['steps']):
                ta,tb=T*k/partitions,T*(k+1)/partitions
                v.need(source_row['ta']==ta and source_row['tb']==tb,'SAVED_SOURCE_EPOCH_IDENTITY')
                source=np.asarray(source_row['source_GL32']);coarse_source=np.asarray(source_row['source_GL16'])
                v.need(source.shape==coarse_source.shape==(2,4),'SOURCE_SHAPE');v.check('saved_source_GL_pair',coarse_source,source,1e-10)
                g=provider.geometry(tb);v.check('reference_nuclei',np.array([g['nH'],g['nHe']])*g['a_rel']**3,[nh,ne],1e-12)
                v.need(RESULT['execution']['new_coupled_substeps']<6,'SUBSTEP_CAP');RESULT['execution']['new_coupled_substeps']+=1
                y,N,U,work,fine,step=solve_step(caller,provider,ta,tb,y,N,U,source,entry['cell']['mu']);run['steps'].append(step);accumulate(c,source,work,fine,tb-ta)
            run.update({'gas':y.copy(),'N':N.copy(),'U_eV':U.copy()});finish_run(run,gradient,y_initial,initial_energy)
    finally:RESULT['execution'].update(caller.counts);caller.close()
    RESULT.pop('active_substep',None)
    for co,fi in zip(RESULT['runs'][:-1],RESULT['runs'][1:]):compare(co,fi,initial_energy,thermal,nh,ne,y_initial[3])
    v.need(all(v.digest(v.ROOT/p)==s for p,s in pins.items()),'FROZEN_SOURCE_CHANGED')
    effect_hold=any(d['above_local_2e_7_screen'] for row in RESULT['comparisons'] for d in row['channel_diagnostics'])
    RESULT['decisions']={'execution_operator':'PASS_SCOPED','local_primary_temporal':'PASS_SCOPED','local_effect_screen':'MANDATORY_TEMPORAL_ERROR_UNRESOLVED' if effect_hold else 'BELOW_LOCAL_NUMERICAL_SCREEN','channel_relative_temporal':'CHANNEL_RELATIVE_TEMPORAL_UNRESOLVED','combined_physical_budget':'NOT_ADOPTED'}
    RESULT['outcome']='COUPLED_SOURCE_ENTRY_SCOPED_DIAGNOSTIC_COMPLETE'
    RESULT['next']='Check already-adopted full-field/CR-first/physical uncertainty contracts once; no implicit model expansion'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_COUPLED_REFINEMENT08_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;v.dump(out/'RESULT.json',RESULT);print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}));return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','180s','prlimit','--as=2147483648','--cpu=180','--fsize=33554432','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    v.dump(out/'STARTED.json',{'command':cmd,'cwd':str(v.ROOT),'source_sha256':{p.name:v.digest(p) for p in UNIT.iterdir() if p.is_file()},'prior_cumulative':json.loads((UNIT/'CONTRACT.json').read_text())['prior_cumulative']})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=v.ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'perprocess; childCPU measured separately','files':{p.name:{'sha256':v.digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(z['bytes'] for z in receipt['files'].values())<=33554432;v.dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode

if __name__=='__main__':raise SystemExit(main())
