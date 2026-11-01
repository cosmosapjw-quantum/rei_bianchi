#!/usr/bin/env python3
"""Read-only original 26-event common-point-parent thermal-path study at tick 160.

The three-parent one-dimensional slice is NOT an all-X correlated Jacobian or
rigorous truncation certificate. Every point inherits one original T bracket.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,sys
from pathlib import Path
import numpy as np

N=46080
LANES=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR')
ALPHAS=(0.05,0.5,0.95)
KB_ERG_K=1.380649e-16
ORIGINAL_ARCHIVE_SHA='a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b'
ORIGINAL_ARRAY_SHA='cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01'
ORIGINAL_KERNEL_SHA='579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644'
GATE=2e-4
WIDTH_GATE=2e-3
ORIGINAL_FAILURE=2.1245050576368385e-4
TICK=160
TOTAL_TICKS=131072
STAGE=('Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_'
       'R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY')
BASE_CODE='research/rei_igm_original_26event_tick160_20261101/source_26events.py'

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def import_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(str(path))
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m)
    return m

def endpoint(alpha,lower,upper):
    if not 0<=alpha<=1:raise ValueError('alpha outside parent T interval')
    a=np.asarray(lower,dtype=np.float64);b=np.asarray(upper,dtype=np.float64)
    if a.shape!=b.shape or np.any(~np.isfinite(a)) or np.any(~np.isfinite(b)) or np.any(a>b):
        raise ValueError('invalid source parent T enclosure')
    return (1-alpha)*a+alpha*b

def ratio_safe(x,y):
    a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
    if np.any(b<=0):raise ValueError('zero original nuclear total')
    return a/b

def source_coordinates(p,logt,nh,nhe):
    xh=ratio_safe(p[:,1],nh);xh2=ratio_safe(p[:,3],nhe);xh3=ratio_safe(p[:,4],nhe)
    xe=ratio_safe(p[:,1]+p[:,3]+2*p[:,4],nh)
    yhe=ratio_safe(nhe,nh)
    T=np.exp(logt)
    U=1.5*KB_ERG_K*T*(1+yhe+xe)
    return dict(xHII=xh,xHeII=xh2,xHeIII=xh3,xe=xe,T_K=T,U_th_erg_per_H=U,logT=logt)

def interval_separation(A,B):
    al=np.asarray(A.lo);ah=np.asarray(A.hi);bl=np.asarray(B.lo);bh=np.asarray(B.hi)
    if any(np.any(~np.isfinite(v)) for v in (al,ah,bl,bh)) or np.any(al>ah) or np.any(bl>bh):
        raise ValueError('invalid nonlinear map interval')
    return dict(center=0.5*((al+ah)-(bl+bh)),
        upper=np.maximum(np.abs(al-bh),np.abs(ah-bl)),
        lower=np.maximum(0,np.maximum(al-bh,bl-ah)),
        full_width=ah-al,half_width=bh-bl)

def quantiles(x):
    a=np.asarray(x,dtype=float)
    if a.size!=N or not np.isfinite(a).all():raise ValueError('invalid nodewise physical data')
    return {str(i):float(np.percentile(a,i)) for i in (0,5,50,95,99,100)}

def write_gz_csv(path,columns):
    lens={len(np.asarray(v)) for v in columns.values()}
    if lens!={N}:raise ValueError('expected original 46080 nodes')
    with path.open('wb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=6) as gz, io.TextIOWrapper(gz,encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['node',*columns])
        for i in range(N):writer.writerow([i,*[format(float(columns[k][i]),'.17g') for k in columns]])
    return sha256(path)

def dimensions_by_map(m,step,nh,nhe):
    p=step.population;logt=step.log_temperature
    return {
      'xHII':m._I(ratio_safe(p.lo[:,1],nh),ratio_safe(p.hi[:,1],nh)),
      'xHeII':m._I(ratio_safe(p.lo[:,3],nhe),ratio_safe(p.hi[:,3],nhe)),
      'xHeIII':m._I(ratio_safe(p.lo[:,4],nhe),ratio_safe(p.hi[:,4],nhe)),
      'logT':logt,
    }

def physical_output_from_step(step,nh,nhe):
    p=0.5*(step.population.lo+step.population.hi)
    logt=0.5*(step.log_temperature.lo+step.log_temperature.hi)
    return source_coordinates(p,logt,nh,nhe)

def verify_stage_owner(step):
    if not step.certified:return False
    for ev in (step.stage_event,step.final_event):
        # Necessary source-owner conservation inclusion, not global 1st-interval closure.
        energy=ev.resolved_heat+ev.unresolved_energy+ev.escaped_energy+ev.chemical_energy
        if not(np.all(energy.lo<=0)&np.all(energy.hi>=0)&np.all(ev.photon_identity.lo<=0)&np.all(ev.photon_identity.hi>=0)):
            raise ValueError('original photon/energy owner failed')
    return True

def setup(repo,lane):
    if lane not in LANES:raise ValueError('lane mismatch')
    repo=Path(repo)
    stage=repo/'stages'/STAGE
    z=stage/'local_results/first_interval_r2_blocked_minimum_step.tar.gz'
    if sha256(z)!=ORIGINAL_ARCHIVE_SHA:raise ValueError('ORIGINAL_SOURCE_ARCHIVE_DRIFT')
    guard=import_module('source_path_guard',stage/'analysis/jax_import_guard.py')
    if not guard.install_if_missing():raise RuntimeError('JAX source guard unavailable')
    src=import_module('original_26_event_source_thermal_path',repo/BASE_CODE)
    m=import_module('original_26_event_interval_map_thermal_path',repo/'stages'/(
       'Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_'
       'CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK')/'analysis/interval_discrete_map.py')
    if sha256(repo/'stages'/('Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_'
            'R1A_R1_R1_R1_R1_R1_CROSS_SITE_STATE_FEEDBACK_REMAINDER_AND_TABLE_EVENT_LOCK')/'analysis/interval_discrete_map.py')!=ORIGINAL_KERNEL_SHA:
        raise ValueError('IMMUTABLE_26_EVENT_KERNEL_DRIFT')
    states=src.archived_tick160(z)
    if set(states)!=set(LANES) or {state['array_sha'] for state in states.values()}!={ORIGINAL_ARRAY_SHA}:
        raise ValueError('ORIGINAL_PARENT_STATE_DRIFT')
    base=m.trial.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=repo,lane=lane)
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    ini=base.inputs.state0.mutable_copy()
    y=np.asarray(ini.values[:5].T,dtype=np.float64)
    nh=y[:,0]+y[:,1];nhe=np.sum(y[:,2:5],axis=1)
    state=states[lane]
    pop=src.representative(state['lo'],state['hi'],nh,nhe)
    if pop.shape!=(N,5) or np.any(pop<state['lo']-1e-12) or np.any(pop>state['hi']+1e-12):
        raise ValueError('original population point outside interval')
    if np.max(np.abs(pop[:,0]+pop[:,1]-nh))>1e-12 or np.max(np.abs(pop[:,2:5].sum(axis=1)-nhe))>1e-12:
        raise ValueError('original nuclei mismatch')
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*TICK/TOTAL_TICKS;t1=duration*(TICK+1)/TOTAL_TICKS
    return dict(stage=stage,src=src,m=m,base=base,model=model,pop=pop,
                nh=nh,nhe=nhe,tl=state['tl'],th=state['th'],
                t0=t0,t1=t1,lane=lane)

def run_path(ctx,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    m=ctx['m'];p=ctx['pop'];nh=ctx['nh'];nhe=ctx['nhe'];t0=ctx['t0'];t1=ctx['t1']
    model=ctx['model'];base=ctx['base'];tm=0.5*(t0+t1)
    rows=[];scores=[]
    receipt=dict(schema='REI_IGM_TICK160_ORIGINAL_26EVENT_PARENT_T_SLICE_V1',lane=ctx['lane'],
      original_archive_sha256=ORIGINAL_ARCHIVE_SHA,original_accepted_array_sha256=ORIGINAL_ARRAY_SHA,
      original_kernel_sha256=ORIGINAL_KERNEL_SHA,
      tested_tick=[160,161],alpha_values=list(ALPHAS),
      nodes=N,strict_local_error=GATE,strict_public_width=WIDTH_GATE,
      historical_full_parent_error=ORIGINAL_FAILURE,
      first_canonical_interval='BLOCKED_MINIMUM_STEP',
      all_X_joint_remainder_certified=False,
      source_realization='conditioned one-dimensional T slice; not original 26-event correlated parent-set certificate',
      source_owner_mutated=False,central_dag='28/88_REPORTED',canonical_delta=0,
      runs=[],status='RUNNING_OR_PARTIAL')
    result=out/'RESULT.json'
    def save():result.write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n')
    save()
    try:
      for alpha in ALPHAS:
        logt=endpoint(alpha,ctx['tl'],ctx['th'])
        parent=source_coordinates(p,logt,nh,nhe)
        kw=dict(model=model,base=base,parent_pop=m._I(p),parent_logt=m._I(logt),
                t0=t0,t1=t1,total_h=nh,total_he=nhe)
        phases={}
        for name in ('full','half1','half2'):
            if name=='half1':kw['t1']=tm
            elif name=='half2':kw.update(parent_pop=phases['half1'].population,
                parent_logt=phases['half1'].log_temperature,t0=tm,t1=t1)
            phase=m.run_step(**kw);phases[name]=phase
            if not verify_stage_owner(phase):
                raise RuntimeError(f'ORIGINAL_NONLINEAR_MAP_NOT_CERTIFIED:{alpha}:{name}:{phase.classification}')
        full=dimensions_by_map(m,phases['full'],nh,nhe)
        half=dimensions_by_map(m,phases['half2'],nh,nhe)
        fullphys=physical_output_from_step(phases['full'],nh,nhe)
        halfphys=physical_output_from_step(phases['half2'],nh,nhe)
        cols={'parent_T_K':parent['T_K'],'parent_xHII':parent['xHII'],
              'parent_xHeII':parent['xHeII'],'parent_xHeIII':parent['xHeIII'],
              'parent_xe':parent['xe'],'parent_U_th_erg_per_H':parent['U_th_erg_per_H'],
              'half_xHII':halfphys['xHII'],'half_xHeII':halfphys['xHeII'],
              'half_xHeIII':halfphys['xHeIII'],'half_T_K':halfphys['T_K'],
              'half_U_th_erg_per_H':halfphys['U_th_erg_per_H'],
              'delta_half_xHII':halfphys['xHII']-parent['xHII'],
              'delta_half_xHeII':halfphys['xHeII']-parent['xHeII'],
              'delta_half_xHeIII':halfphys['xHeIII']-parent['xHeIII'],
              'delta_half_T_K':halfphys['T_K']-parent['T_K'],
              'delta_half_U_th_erg_per_H':halfphys['U_th_erg_per_H']-parent['U_th_erg_per_H']}
        allscores=[]
        for k in ('xHII','xHeII','xHeIII','logT'):
            score=interval_separation(full[k],half[k]);allscores.append(score)
            cols[f'{k}_point_center_defect']=score['center']
            cols[f'{k}_independent_upper']=score['upper']
            cols[f'{k}_independent_lower']=score['lower']
            if k=='logT':cols['logT_independent_half_width']=score['half_width']
        assert all(len(v)==N for v in cols.values())
        path=out/f'PATH_ALPHA_{alpha:.2f}_N{N}.csv.gz'
        digest=write_gz_csv(path,cols)
        summary={
          'alpha':alpha,'rows':N,'filename':path.name,'sha256':digest,
          'max_independent_upper':max(float(np.max(z['upper'])) for z in allscores),
          'max_point_center_abs_defect':max(float(np.max(np.abs(z['center']))) for z in allscores),
          'max_logT_independent_upper':float(np.max(allscores[3]['upper'])),
          'max_logT_center_abs_defect':float(np.max(np.abs(allscores[3]['center']))),
          'physical_ionization_change_xHII':quantiles(cols['delta_half_xHII']),
          'physical_temperature_change_K':quantiles(cols['delta_half_T_K']),
          'physical_thermal_energy_change_erg_per_H':quantiles(cols['delta_half_U_th_erg_per_H']),
          'H_nuclei_interval_includes_initial':bool(np.all(phases['half2'].population.lo[:,0]+phases['half2'].population.lo[:,1]<=nh+1e-14) and np.all(phases['half2'].population.hi[:,0]+phases['half2'].population.hi[:,1]>=nh-1e-14)),
          'He_nuclei_interval_includes_initial':bool(np.all(np.sum(phases['half2'].population.lo[:,2:5],axis=1)<=nhe+1e-14) and np.all(np.sum(phases['half2'].population.hi[:,2:5],axis=1)>=nhe-1e-14)),
          'strict_local_error_pass_for_point_only':bool(all(float(np.max(z['upper']))<GATE for z in allscores))
        }
        receipt['runs'].append(summary);save()
        print('ONE_THERMAL_PARENT_POINT',json.dumps({k:summary[k] for k in ('alpha','max_logT_independent_upper','max_logT_center_abs_defect','max_independent_upper','physical_temperature_change_K')},sort_keys=True),flush=True)
      receipt['status']='THREE_SOURCE_CONDITIONAL_POINT_PARENTS_EXECUTED_NOT_ALL_X_CERTIFIED'
    except Exception as exc:
      receipt['status']='STOPPED_UNCERTIFIED_OR_RUNTIME_FAILURE';receipt['failure']={'type':type(exc).__name__,'message':str(exc)}
      save()
      raise
    save()
    print('FINAL_PARENT_PATH_RESULT',json.dumps(receipt,sort_keys=True),flush=True)
    return receipt

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);parser.add_argument('--lane',choices=LANES,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();context=setup(args.repo.resolve(),args.lane);run_path(context,args.out)

if __name__=='__main__':main()
