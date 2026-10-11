"""Single full selective-C02 source/redshift/absorption/gas split step."""
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
UNIT=Path(__file__).resolve().parent;BASE=UNIT.parent;ROOT=UNIT.parents[2]
sys.path.insert(0,str(BASE/'q1b_threshold_positive09'))
import validate as v
from threshold_positive import fit_threshold_positive
from positive_entry import source_integrals,incident
from opacity_native import EV_ERG
from source_cells import CellSource,table_cell_moments
sys.path.insert(0,str(BASE/'q1b_selective_native_bind03'))
from caller import Caller
from fullfield_value import FullFieldValue,admissible,norm
RESULT={'unit':'Q1B10_SAME_N1_FULL_C02_ONE_SUBSTEP01','checks':[], 'points':[], 'iterations':[],
 'execution':{'native_processes':0,'SIGMA':0,'SIGMA_energies':0,'CELL_RHS_V1':0,'positive_maps':0,'source_evaluations':0,'event_roots':0,'time_panels':0,'coupled_substeps':0,'gas_solve':0,'freshUVB':0,'build':0,'Jacobian':0,'Newton':0,'full_history':0},
 'executor':'controller_direct_owner_authorized','observed_runtime_model':'NOT_INDEPENDENTLY_OBSERVED','global_admission':'HOLD'}
v.RESULT=RESULT
check,need,digest,dump=v.check,v.need,v.digest,v.dump

def point(e,y,order):
    row=e.evaluate(y,order);RESULT['points'].append(row)
    need(np.isfinite(row['residual']).all(),'NONFINITE_GAS_RESIDUAL')
    identity=row['energy_identity'];check('gas_energy_residual_identity',identity['lhs'],identity['rhs'],1e-12,identity['termwise_scale'])
    check('native_local_residual',row['native'][12:14],0.,1e-12,1.)
    work=row['work'];check('native_work_split',work['pairing_residual'],0.,1e-12,work['termwise_scale'])
    for pair in row['photon_pairs']:
        check('photon_number_pair',pair['number_after_abs'],pair['number_before'],1e-12)
        check('photon_energy_pair',pair['energy_after_abs'],pair['energy_before'],1e-12)
    need(np.all(np.asarray(row['cells'])[:,5:7]==0),'SOURCE_DOUBLE_COUNT')
    return row

def run():
    bindpath=BASE/'q1b_selective_native_bind03/evidence/attempt1/RESULT.json'
    prev=BASE/'q1b_threshold_positive09/evidence/attempt1/RESULT.json'
    need(digest(bindpath)=='482d800301726ae01a713f4dfc06db9a3227f38abf15fe7a3ee06a5042b08593','B3_RESULT_IDENTITY')
    need(digest(prev)=='d4e4d6ac776f213aea013731b3e8d889ab8bee2dec673ab21e45387eb145bc16','Q1B9_RESULT_IDENTITY')
    need(json.loads((BASE/'q1b_threshold_positive09/INDEPENDENT_REVIEW.json').read_text())['decision']=='PASS_MOVING_THRESHOLD_POSITIVE_QUADRATURE_SCOPED','Q1B9_REVIEW')
    pins=json.loads(prev.read_text())['input_sha256'].copy()
    additions={'q1b_threshold_positive09/threshold_positive.py':'0525c34d874b2f24fca61cee34a7071a5c75566fe40cd9171fe3ab25c56ec55c',
      'q1b_coupled_refinement08/run_refinement.py':'4dcdcc231928bfb20dd74a5a4dbba648e4c73382bba56eec18ade3849a1c7566',
      'q1b/c10/source_entry.py':'56ed274e76e4cea832d70271764534ba54b89c3d37365a0ae83e4f9ddc20db64',
      'q1b_work_gas_jvp05/adapter.py':'c7f1cac3ecbb4a8dc8edfc62f1c7458fff77e9ff6633cadb0cfb1c8e4c15f3c5',
      'q1b_gas_residual06/residual.py':'68ed824baf025d821f001253fcfd2be81682b98e0c4c8893873d00696d809107',
      'q1b_selective_native_bind03/caller.py':'a78c05c12133f05bda80251b2e8d339bfc3afeb97f4f228a7c5af1d60ea057df'}
    for p,s in additions.items():pins[str((BASE/p).relative_to(ROOT))]=s
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'FROZEN_INPUT_IDENTITY');RESULT['input_sha256']=pins
    bind=json.loads(bindpath.read_text());grid=json.loads((BASE/'q1b_selective_native_bind03/GRID_SELECTIVE_C02.json').read_text())
    edges=np.asarray(grid['q_edges_eV']);mu=np.asarray(grid['initial_mu']);weights=np.asarray(grid['angular_weights'])
    initial=np.asarray(bind['initial_cells']);need(initial.shape==(176,13) and len(edges)==89,'FULLFIELD_GRID_SHAPE')
    N0=initial[:,3].copy();U0=initial[:,4].copy();provider=v.HistoryProvider(r=0.);y0=provider.initial_gas.copy()
    need(np.array_equal(y0,np.asarray(bind['initial_gas'])),'SAVED_GAS_IDENTITY')
    h=2827462976819.2324;g0=provider.geometry(0.);g=provider.geometry(h);bg=provider.background
    need(h==2.**-12/g0['H'],'FROZEN_TIME_IDENTITY')
    def logR(t):return -math.log1p(bg._relative_volume_increment(t))/3
    def R(t):return math.exp(logR(t))
    r=R(h);_,raymu,rayR=provider.ray(np.ones(2),mu,h)
    check('ray_R',rayR,r,1e-11);check('ray_mu',raymu,mu,1e-11)
    check('reference_nuclei',np.array([g['nH'],g['nHe']])*g['a_rel']**3,[g0['nH'],g0['nHe']],1e-12)
    cs=CellSource(provider,grid);table=provider.tables['emissivity']
    spec=importlib.util.spec_from_file_location('fullfield_frozen_C10_events',BASE/'q1b/c10/source_entry.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    energies=np.unique(np.r_[table.energies_eV,10.,50000.]);energies=energies[(energies>=10.)&(energies<=50000.)]
    roots=sum(int(np.count_nonzero((energies/q<R(0.))&(energies/q>r))) for q in edges)*2
    need(roots<=127,'EVENT_ROOT_CAP');RESULT['execution']['event_roots']=roots
    events=helper.provider_event_times(cs,0.,h);panels=[0.,*events,h]
    need(len(panels)-1<=128,'TIME_PANEL_CAP');RESULT['execution']['time_panels']=len(panels)-1
    RESULT['event_times_s']=events;RESULT['source_provider_identity']=provider.identity
    def source(t):
        need(RESULT['execution']['source_evaluations']<6144,'SOURCE_CALL_CAP');RESULT['execution']['source_evaluations']+=1
        gt=provider.geometry(t);rt=R(t);val=table_cell_moments(table,gt['z'],edges,np.full(2,rt),weights)
        return np.stack([val['N'].ravel(),val['Q_eV'].ravel()],axis=1)
    coarse_source=source_integrals(source,logR,0.,h,panels,16)
    source_fine=source_integrals(source,logR,0.,h,panels,32)
    RESULT['source_GL16']=coarse_source;RESULT['source_GL32']=source_fine
    check('fullfield_source_GL16_32',coarse_source,source_fine,1e-10)
    nn,uu,work=incident(N0,U0,logR(0.),logR(h),source_fine)
    check('fullfield_source_energy_work',uu-U0+work,source_fine[:,2],1e-12,np.maximum.reduce([uu,U0,source_fine[:,2],abs(work)]))
    caps=np.maximum(edges[:-1],np.minimum(edges[1:],50000./r))
    before_pop=int(np.count_nonzero(N0));active=int(np.count_nonzero(nn));birth=(N0==0)&(nn>0)
    need(before_pop==158 and active==160 and np.count_nonzero(birth)==2 and np.count_nonzero(nn==0)==16,'FULLFIELD_BIRTH_DOMAIN')
    need(np.all(nn>=0) and np.all(uu>=0) and np.array_equal(nn==0,uu==0),'INCIDENT_POSITIVITY')
    RESULT['fixed']={'h_s':h,'geometry':g,'R':r,'mu':mu,'weights':weights,'initial_gas':y0,'initial_N':N0,'initial_U_eV':U0,'incident_N':nn,'incident_U_eV':uu,'radiation_work_eV':work,'active_caps':caps,'initial_populated':before_pop,'initial_empty':18,'birth_indices':np.flatnonzero(birth),'incident_active':active,'dormant_indices':np.flatnonzero(nn==0)}
    caller=Caller();nodes={64:[],128:[]};RESULT['fits']=[]
    try:
        for order in [64,128]:
            for k in range(176):
                i=k%88;RESULT['active_stage']={'stage':'positive_quadrature','row':k,'order':order}
                q,p,fit=fit_threshold_positive(nn[k],uu[k],r,edges[i],caps[i],order)
                if len(q):
                    need(np.all(r*q>0) and np.all(r*q<=50000.),'NATIVE_ENERGY_DOMAIN')
                    need(caller.counts['SIGMA']<352 and caller.counts['SIGMA_energies']+len(q)<=65536,'SIGMA_CAP')
                    sigma=caller.opacity.sigma(r*q)
                else:sigma=np.zeros((0,3))
                nodes[order].append((q,p,sigma));RESULT['fits'].append({'order':order,'row':k,'fit':fit})
        e=FullFieldValue(caller,g,y0,h,h,r,mu,edges,caps,nodes,RESULT['execution'])
        gradient=e.energy_gradient;scale=float(np.dot(gradient,y0)+EV_ERG*math.fsum(uu))
        need(scale>0 and np.isfinite(scale),'SOLVE_ENERGY_SCALE')
        RESULT['fixed']['energy_gradient']=gradient;RESULT['fixed']['solve_energy_scale_erg']=scale
        RESULT['execution']['gas_solve']=1
        base=point(e,y0,128);previous_y=y0.copy();previous_native=base['native'];previous_norm=base['norm']
        for k in range(1,7):
            RESULT['active_stage']={'stage':'Picard','iteration':k}
            y=y0+h*previous_native[:4];admissible(y,g);fine=point(e,y,128);update=y-previous_y
            en=float(np.dot(abs(gradient),abs(fine['residual']))/scale);eu=float(np.dot(abs(gradient),abs(update))/scale);un=norm(update,y0)
            converged=fine['norm']<=1e-12 and un<=1e-12 and en<=1e-12 and eu<=1e-12
            ratio=fine['norm']/previous_norm if previous_norm!=0 else (0. if fine['norm']==0 else None)
            RESULT['iterations'].append({'iteration':k,'y':y.copy(),'residual_norm':fine['norm'],'update_norm':un,'energy_residual':en,'energy_update':eu,'ratio':ratio,'converged':converged})
            if converged:break
            need(ratio is not None and ratio<=.5,'PICARD_NONCONTRACTION_HOLD')
            previous_y=y.copy();previous_native=fine['native'];previous_norm=fine['norm']
        else:raise ArithmeticError('PICARD_CAP_HOLD')
        RESULT['active_stage']={'stage':'same_gas_coarse_point'}
        coarse=point(e,y,64);check('fullfield_final_GL_values',coarse['values'],fine['values'],1e-7)
        check('fullfield_final_GL_sums',coarse['values'].sum(axis=0),fine['values'].sum(axis=0),1e-7)
        need(coarse['norm']<=1e-12 and np.dot(abs(gradient),abs(coarse['residual']))/scale<=1e-12,'COARSE_NONLINEAR_BUDGET_HOLD')
        vals=np.asarray(fine['values']);N=vals[:,0];U=vals[:,1];count=vals[:,2:5].sum(axis=0);binding=vals[:,5:8].sum(axis=0);heat=vals[:,8:11].sum(axis=0)
        photonscale=math.fsum(N0)+math.fsum(source_fine[:,0])
        number=math.fsum(N)-math.fsum(N0)+math.fsum(count)-math.fsum(source_fine[:,0])
        wg=h*fine['work']['gas_work_rate'];escape=h*fine['native'][4];cmb=h*fine['native'][14]
        energy=float(np.dot(gradient,y-y0))+EV_ERG*(math.fsum(U)-math.fsum(U0)+math.fsum(work)-math.fsum(source_fine[:,2]))+wg+escape-cmb
        ledger_scale=float(np.dot(gradient,y0))+EV_ERG*(math.fsum(U0)+math.fsum(source_fine[:,2]))+abs(cmb)
        RESULT['final']={'gas':y,'N':N,'U_eV':U,'count':count,'binding_eV':binding,'heat_eV':heat,'gas_work_erg':wg,'escape_energy_erg':escape,'CMB_energy_erg':cmb,'fine':fine,'coarse':coarse}
        RESULT['ledger']={'number_defect':number,'number_scale':photonscale,'energy_defect_erg':energy,'energy_scale_erg':ledger_scale,'gas_residual_erg':float(np.dot(gradient,fine['residual']))}
        check('fullfield_number_ledger',number,0.,1e-9,photonscale)
        check('fullfield_energy_ledger',energy,0.,1e-9,ledger_scale)
        check('fullfield_energy_vs_gas_residual',energy,np.dot(gradient,fine['residual']),1e-12,ledger_scale)
        RESULT['execution']['coupled_substeps']=1
    finally:RESULT['execution'].update(caller.counts);caller.close()
    need(all(digest(ROOT/p)==s for p,s in pins.items()),'FROZEN_INPUT_CHANGED')
    RESULT.pop('active_stage',None)
    RESULT['outcome']='PASS_FULL_C02_SINGLE_SUBSTEP_SCOPED'
    RESULT['next']='IndependentreviewthenfullC021/2/4refinement,reusingthisone-step'
    RESULT['claim']='Onefirstordersplitstep; time/spectralconvergence,history,CR-firstandglobaladmissionHOLD'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=a.output.resolve()
    if a.worker:
        t=time.monotonic();status=0
        try:run()
        except Exception as exc:traceback.print_exc();RESULT['outcome']='HOLD_FULLFIELD_STEP10_FIRST_FAILURE';RESULT['first_failure']={'type':type(exc).__name__,'message':str(exc)};status=1
        RESULT['wall_s']=time.monotonic()-t;dump(out/'RESULT.json',RESULT);print(json.dumps({'outcome':RESULT['outcome'],'execution':RESULT['execution']}));return status
    out.mkdir(parents=True,exist_ok=False)
    cmd=['env','OMP_NUM_THREADS=1','OPENBLAS_NUM_THREADS=1','MKL_NUM_THREADS=1','timeout','--signal=TERM','--kill-after=5s','180s','prlimit','--as=2147483648','--cpu=180','--fsize=67108864','/usr/bin/python3','-B',str(Path(__file__).resolve()),'--worker','--output',str(out)]
    dump(out/'STARTED.json',{'command':cmd,'cwd':str(ROOT),'implementation_sha256':{p.name:digest(p) for p in UNIT.iterdir() if p.is_file()},'prior_cumulative':json.loads((UNIT/'CONTRACT.json').read_text())['prior_cumulative']})
    t=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/'stdout.txt').open('x') as stdout,(out/'stderr.txt').open('x') as stderr:r=subprocess.run(cmd,cwd=ROOT,stdout=stdout,stderr=stderr)
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={'exit':r.returncode,'wall_s':time.monotonic()-t,'child_CPU_s':c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,'CPU_limit_semantics':'perprocess; measuredaggregatechildCPUseparate','files':{p.name:{'sha256':digest(p),'bytes':p.stat().st_size} for p in out.iterdir() if p.is_file()}}
    receipt['output_cap_pass']=sum(x['bytes'] for x in receipt['files'].values())<=67108864;dump(out/'EXECUTION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())
