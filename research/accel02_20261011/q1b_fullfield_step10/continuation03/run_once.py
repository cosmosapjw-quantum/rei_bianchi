"""Exact-state saved-source continuation; immutable original full-field driver."""
import argparse
import ast
import hashlib
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

HERE=Path(__file__).resolve().parent;UNIT=HERE.parent;BASE=UNIT.parent;ROOT=UNIT.parents[2]
sys.path.insert(0,str(UNIT))
spec=importlib.util.spec_from_file_location('frozen_fullfield_step10',UNIT/'run_once.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
RESULT={'unit':'Q1B10_CONTINUATION03_SAVED_SOURCE_POSTFIT_VALUE_GATE','checks':[],'points':[],'iterations':[],'fits':[],
 'execution':{'native_processes':0,'SIGMA':0,'SIGMA_energies':0,'CELL_RHS_V1':0,'positive_maps':0,
 'source_evaluations':0,'event_roots':0,'time_panels':0,'coupled_substeps':0,'gas_solve':0,'freshUVB':0,'build':0,'Jacobian':0,'Newton':0,'full_history':0},
 'executor':'controller_direct_owner_authorized','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED','global_admission':'HOLD'}
original.RESULT=RESULT;original.v.RESULT=RESULT
check,need,digest,dump=original.check,original.need,original.digest,original.dump
from opacity_native import C_CM_S,CHEMICAL_CHI_EV
from reconstruction import reconstruct
from threshold_positive import fit_threshold_positive

def heat_gates(K0,KE,direct,label):
    abi=KE-CHEMICAL_CHI_EV*K0
    need(np.isfinite([K0,KE,direct,abi]).all() and np.all(np.asarray([K0,KE,direct,abi])>=0),'NONFINITE_OR_NEGATIVE_'+label)
    check(label+'_ABI_direct_cells',abi,direct,1e-7)
    check(label+'_ABI_direct_sum',abi.sum(axis=0),direct.sum(axis=0),1e-7)
    return abi

old_point=original.point
def checked_point(e,y,order):
    row=old_point(e,y,order);values=np.asarray(row['values']);V=e.g['a_rel']**3
    RESULT['active_stage']['heat_order']=order
    direct=V*values[:,20:23]
    abi=heat_gates(values[:,11:14],values[:,14:17],direct,'attenuated_'+str(len(RESULT['points']))+'_'+str(order))
    row['native_consumed_heat_direct']=direct;row['native_consumed_heat_ABI']=abi
    return row
original.point=checked_point

def inherited_coupled_tail():
    """Reuse the untouched Picard/ledger AST after incident-node construction."""
    tree=ast.parse((UNIT/'run_once.py').read_text())
    run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    idx=next(i for i,n in enumerate(run.body) if isinstance(n,ast.Try))
    block=run.body[idx]
    need(isinstance(block.body[0],ast.For) and ast.unparse(block.body[0].target)=='order','COUPLED_AST_PREFIX')
    need(isinstance(block.body[1],ast.Assign) and ast.unparse(block.body[1].targets[0])=='e','COUPLED_AST_BODY')
    params='caller nodes g y0 h r mu edges caps source_fine N0 U0 nn uu work pins'.split()
    run.args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=p) for p in params],kwonlyargs=[],kw_defaults=[],defaults=[])
    run.body=block.body[1:]+run.body[idx+1:]
    module=ast.fix_missing_locations(ast.Module(body=[run],type_ignores=[]))
    scope=vars(original).copy();exec(compile(module,'<unchanged_picard_and_ledger_tail>','exec'),scope)
    RESULT['coupled_tail_reuse']={'source_sha256':digest(UNIT/'run_once.py'),
      'AST_sha256':hashlib.sha256(ast.dump(module,include_attributes=False).encode()).hexdigest(),
      'scope':'Original e construction, bounded Picard, same-y coarse, all residual/ledger checks and outcome; only prefix/caller cleanup externalized'}
    return scope['run']

def saved_fit(diagnostic,order,k,N,U,R,a,b):
    fixed=diagnostic['fixed'];need([N,U,R,a,b]==[fixed[p] for p in ('N','U','R','a','b')],'SAVED_POSTFIT_SCOPE_MISMATCH')
    candidate=next(x for x in diagnostic['candidates'] if x['order']==order)
    q,p=np.asarray(candidate['q']),np.asarray(candidate['fitted_weights'])
    need(q.shape==p.shape==(order,) and np.isfinite(q).all() and np.isfinite(p).all() and np.all(p>0),'SAVED_POSITIVE_MEASURE_SHAPE')
    need(np.all(q>a) and np.all(q<b),'SAVED_NODE_SUPPORT')
    cell=reconstruct(N,U,R,a,b);need(cell.status=='INTERIOR','SAVED_INTERIOR')
    coordinate=32*math.ulp(b)/min(cell.mean_q-a,b-cell.mean_q)
    check('saved_coordinate_'+str(k)+'_'+str(order),coordinate,0.,1e-7,1.)
    splits=sorted(set(float(E/R) for E in original.v.THRESHOLDS_EV if a<E/R<b))
    need(not splits and candidate['fit']['panels'][0]['q_bounds']==[a,b],'SAVED_THRESHOLD_PANEL_SCOPE')
    for E in original.v.THRESHOLDS_EV:
        boundary=float(E/R)
        if b<=boundary:need(np.all(R*q<E),'SAVED_THRESHOLD_NODE_SIDE')
        if a>=boundary:need(np.all(R*q>E),'SAVED_THRESHOLD_NODE_SIDE')
    check('saved_N_'+str(k)+'_'+str(order),math.fsum(p),N,1e-12)
    check('saved_Q_'+str(k)+'_'+str(order),math.fsum(q*p),U/R,1e-12)
    residual=abs(float((p/N)@((q-a)/(b-a)))-(cell.mean_q-a)/(b-a))
    check('saved_cell_mean_'+str(k)+'_'+str(order),residual,0.,1e-7,1.)
    return q,p,dict(candidate['fit'],reuse='EXACT_SAVED_INCIDENT_STATE_ONLY')

def run():
    contract=json.loads((HERE/'CONTRACT.json').read_text());savedpath=UNIT/'evidence/attempt1/RESULT.json'
    diagpath=UNIT/'evidence/diagnostic02_attempt1/RESULT.json';reviewpath=UNIT/'diagnostic02/INDEPENDENT_REVIEW.json'
    need(digest(savedpath)==contract['source_reuse_result_sha256'] and digest(diagpath)==contract['diagnostic_result_sha256'] and digest(reviewpath)==contract['diagnostic_review_sha256'],'SAVED_EVIDENCE_IDENTITY')
    need(json.loads(reviewpath.read_text())['decision']=='PASS_PRETILT_GATE_VERSUS_POSTFIT_MEAN_SEPARATED_SCOPED','DIAGNOSTIC_REVIEW')
    first=json.loads(savedpath.read_text());diagnostic=json.loads(diagpath.read_text());fixed=first['fixed']
    pins=first['input_sha256'].copy()
    started=json.loads((UNIT/'evidence/attempt1/STARTED.json').read_text())
    for name,sha in started['implementation_sha256'].items():
        if name in ('CONTRACT.json','run_once.py','fullfield_value.py'):
            pins[str((UNIT/name).relative_to(ROOT))]=sha
    need(all(digest(ROOT/p)==sha for p,sha in pins.items()),'FROZEN_INPUT_IDENTITY');RESULT['input_sha256']=pins
    bindpath=BASE/'q1b_selective_native_bind03/evidence/attempt1/RESULT.json'
    need(digest(bindpath)=='482d800301726ae01a713f4dfc06db9a3227f38abf15fe7a3ee06a5042b08593','B3_RESULT_IDENTITY')
    bind=json.loads(bindpath.read_text());g0=bind['initial_geometry'];g=fixed['geometry'];h=fixed['h_s'];r=fixed['R']
    grid=json.loads((BASE/'q1b_selective_native_bind03/GRID_SELECTIVE_C02.json').read_text())
    edges=np.asarray(grid['q_edges_eV']);caps=np.asarray(fixed['active_caps']);mu=np.asarray(fixed['mu']);y0=np.asarray(fixed['initial_gas'])
    N0,U0=np.asarray(fixed['initial_N']),np.asarray(fixed['initial_U_eV']);nn,uu=np.asarray(fixed['incident_N']),np.asarray(fixed['incident_U_eV']);work=np.asarray(fixed['radiation_work_eV'])
    source_fine=np.asarray(first['source_GL32']);coarse_source=np.asarray(first['source_GL16'])
    need(np.array_equal(y0,bind['initial_gas']) and np.array_equal(N0,np.asarray(bind['initial_cells'])[:,3]) and np.array_equal(U0,np.asarray(bind['initial_cells'])[:,4]),'SAVED_IC_IDENTITY')
    need(h==2827462976819.2324 and h==2.**-12/g0['H'] and len(edges)==89 and nn.shape==(176,),'FROZEN_GRID_TIME')
    check('saved_R_geometry',r,1/g['a_rel'],1e-11)
    check('saved_reference_nuclei',np.array([g['nH'],g['nHe']])*g['a_rel']**3,[g0['nH'],g0['nHe']],1e-12)
    check('saved_source_GL16_32',coarse_source,source_fine,1e-10)
    check('saved_source_energy_work',uu-U0+work,source_fine[:,2],1e-12,np.maximum.reduce([uu,U0,source_fine[:,2],abs(work)]))
    need(np.count_nonzero(N0)==158 and np.count_nonzero(nn)==160 and np.count_nonzero((N0==0)&(nn>0))==2 and np.count_nonzero(nn==0)==16,'SAVED_BIRTH_DOMAIN')
    need(np.all(nn>=0) and np.all(uu>=0) and np.array_equal(nn==0,uu==0),'SAVED_INCIDENT_POSITIVITY')
    RESULT['fixed']=fixed;RESULT['source_GL16']=coarse_source;RESULT['source_GL32']=source_fine
    RESULT['source_reuse']={'result_sha256':digest(savedpath),'provider_identity':first['source_provider_identity'],'new_evaluations':0,'new_events':0,'legacy_failure_preserved':first['first_failure']}
    caller=original.Caller();nodes={64:[],128:[]};rates={64:[],128:[]}
    try:
        for order in (64,128):
            for k in range(176):
                i=k%88;RESULT['active_stage']={'stage':'positive_quadrature_and_native_sigma','row':k,'order':order}
                if k in (33,121):q,p,fit=saved_fit(diagnostic,order,k,nn[k],uu[k],r,edges[i],caps[i])
                else:q,p,fit=fit_threshold_positive(nn[k],uu[k],r,edges[i],caps[i],order)
                if len(q):
                    need(np.all(r*q>0) and np.all(r*q<=50000.),'NATIVE_ENERGY_DOMAIN')
                    need(caller.counts['SIGMA']<352 and caller.counts['SIGMA_energies']+len(q)<=65536,'SIGMA_CAP')
                    sigma=caller.opacity.sigma(r*q)
                else:sigma=np.zeros((0,3))
                nodes[order].append((q,p,sigma));RESULT['fits'].append({'order':order,'row':k,'fit':fit})
                cross=C_CM_S*sigma;E=r*q
                K0=np.sum(cross*p[:,None],axis=0);KE=np.sum(E[:,None]*cross*p[:,None],axis=0)
                direct=np.sum((E[:,None]-CHEMICAL_CHI_EV)*cross*p[:,None],axis=0);abi=KE-CHEMICAL_CHI_EV*K0
                rates[order].append(np.stack([K0,KE,direct,abi]))
                check('incident_N_'+str(order)+'_'+str(k),math.fsum(p),nn[k],1e-12)
                check('incident_U_'+str(order)+'_'+str(k),math.fsum(E*p),uu[k],1e-12)
            rates[order]=np.asarray(rates[order]);heat_gates(rates[order][:,0],rates[order][:,1],rates[order][:,2],'incident_'+str(order))
        RESULT['incident_rates']=rates
        RESULT['active_stage']={'stage':'incident_native_own_scale_gate'}
        for field,name in enumerate(('K0','KE','Hdirect','HABI')):
            check('incident_GL_'+name+'_cells',rates[64][:,field],rates[128][:,field],1e-7)
            check('incident_GL_'+name+'_sum',rates[64][:,field].sum(axis=0),rates[128][:,field].sum(axis=0),1e-7)
        RESULT['incident_gate']='PASS_BEFORE_GAS_SOLVE'
        RESULT['active_stage']={'stage':'gas_baseline'}
        coupled=inherited_coupled_tail()
        coupled(caller,nodes,g,y0,h,r,mu,edges,caps,source_fine,N0,U0,nn,uu,work,pins)
        final=RESULT['final'];coarse,fine=final['coarse'],final['fine']
        RESULT['active_stage']={'stage':'final_attenuated_heat_own_scale_gate'}
        for name in ('native_consumed_heat_direct','native_consumed_heat_ABI'):
            check('final_GL_'+name+'_cells',coarse[name],fine[name],1e-7)
            check('final_GL_'+name+'_sum',coarse[name].sum(axis=0),fine[name].sum(axis=0),1e-7)
        RESULT.pop('active_stage',None)
        RESULT['outcome']='PASS_FULL_C02_SINGLE_SUBSTEP_SCOPED'
        RESULT['next']='Independent review then same selective lane1/2/4, reuse thisone,new6steps; rowexception not automatically transferable'
    finally:RESULT['execution'].update(caller.counts);caller.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_CONTINUATION03_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;dump(out/'RESULT.json',RESULT);return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','180s','prlimit','--as=2147483648','--cpu=180','--fsize=67108864','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'implementation_sha256':{p.name:digest(p) for p in HERE.iterdir() if p.is_file()}})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'perprocess; aggregatechildCPUseparate',
       'files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(x['bytes'] for x in receipt['files'].values())<=67108864
    dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())
