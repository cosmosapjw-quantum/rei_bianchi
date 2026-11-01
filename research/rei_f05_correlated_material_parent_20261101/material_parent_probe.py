#!/usr/bin/env python3
"""Original 26-event full/two-half at two nuclear/material-energy-correlated tick160 parent points.

Physical state is source-authentic; newly chosen points lie in coordinate boxes but
are NOT certified members of the original joint reachable parent/source set.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,importlib.util,io,json,math,sys
from pathlib import Path
import numpy as np

REPO_ROOT=Path(__file__).resolve().parents[2]
BASE=REPO_ROOT/'research/rei_igm_tick160_nonlinear_point_20261101/probe.py'
KB=1.380649e-16
EV=1.602176634e-12
CHI=np.array([13.598434599702,24.587389011,24.587389011+54.4177655282])
GATE=2e-4
EXPECTED_SOURCE_BODY_SHA='cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01'
def load_prior():
    spec=importlib.util.spec_from_file_location('source_owned_328_probe',BASE)
    if spec is None or spec.loader is None:raise ImportError(BASE)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module
def material(pop,T):
    ne=pop[:,1]+pop[:,3]+2*pop[:,4]
    E_kin=1.5*KB*T*(pop.sum(axis=1)+ne)
    E_ion=EV*(CHI[0]*pop[:,1]+CHI[1]*pop[:,3]+CHI[2]*pop[:,4])
    return E_kin+E_ion,ne,E_kin,E_ion
def fixed_material_T(pop,E):
    ne=pop[:,1]+pop[:,3]+2*pop[:,4]
    E_ion=EV*(CHI[0]*pop[:,1]+CHI[1]*pop[:,3]+CHI[2]*pop[:,4])
    return (E-E_ion)/(1.5*KB*(pop.sum(axis=1)+ne))
def correlated_points(lo,hi,loglo,loghi,H,He):
    """Two alpha=+/-1 points on one nuclei/energy-conserving curve inside X."""
    lo,hi=np.asarray(lo,float),np.asarray(hi,float)
    if lo.shape!=hi.shape or lo.ndim!=2 or lo.shape[1]!=5:
        raise ValueError('source population shape mismatch')
    Tlo,Thi=np.exp(loglo),np.exp(loghi)
    x0=.5*lo+.5*hi
    x0[:,0]=H-x0[:,1]
    x0[:,2]=He-x0[:,3]-x0[:,4]
    T0=np.exp(.5*(loglo+loghi))
    if np.any(x0<=0) or np.any(x0[:,0]<lo[:,0]-1e-10) or np.any(x0[:,2]<lo[:,2]-1e-10):
        raise ValueError('reference state outside original physical box')
    E0,_,_,_=material(x0,T0)
    d=np.zeros_like(x0)
    for col in (1,3,4):
        d[:,col]=.90*np.maximum(np.minimum(x0[:,col]-lo[:,col],hi[:,col]-x0[:,col]),0.)
    # Electron/ion-raising direction with exact neutral species compensation.
    d[:,0]=-d[:,1];d[:,2]=-d[:,3]-d[:,4]
    marginH=np.maximum(np.minimum(x0[:,0]-lo[:,0],hi[:,0]-x0[:,0]),0.)
    marginHe=np.maximum(np.minimum(x0[:,2]-lo[:,2],hi[:,2]-x0[:,2]),0.)
    shrink=np.minimum(1.,np.minimum(marginH/np.maximum(d[:,1],1e-300),
                                  marginHe/np.maximum(d[:,3]+d[:,4],1e-300)))
    d=d*np.maximum(shrink,0.)[:,None]
    lower=np.zeros(len(H));upper=np.ones(len(H))
    for _ in range(46):
        t=.5*(lower+upper)
        ok=np.ones(len(H),dtype=bool)
        for sign in (-1.,1.):
            x=x0+sign*t[:,None]*d
            Tk=fixed_material_T(x,E0)
            ok &= ((Tk>=Tlo)&(Tk<=Thi)&(Tk>0)&
                   (x[:,0]>0)&(x[:,2]>0)&np.all(x>=lo-1e-13,axis=1)&np.all(x<=hi+1e-13,axis=1))
        lower=np.where(ok,t,lower)
        upper=np.where(ok,upper,t)
    scale=.90*lower
    samples={}
    for name,sign in [('CHEM_MINUS',-1.),('CHEM_PLUS',1.)]:
        x=x0+sign*scale[:,None]*d
        T=fixed_material_T(x,E0)
        En,_,_,_=material(x,T)
        rel=np.abs((En-E0)/np.maximum(np.abs(E0),1e-300))
        tol=64*np.finfo(float).eps*np.maximum(H+He,1.)
        if (np.any(x[:,0]<=0) or np.any(x[:,2]<=0) or
            np.any(x<lo-tol[:,None]) or np.any(x>hi+tol[:,None]) or
            np.any(T<Tlo*(1-1e-14)) or np.any(T>Thi*(1+1e-14)) or
            np.max(rel)>4e-15):
            raise ValueError('nuclei, source box or material energy violated')
        if np.max(np.abs((x[:,0]+x[:,1])-H))>3e-14*np.max(H):
            raise ValueError('H nuclei conservation failure')
        if np.max(np.abs((x[:,2]+x[:,3]+x[:,4])-He))>3e-14*np.max(He):
            raise ValueError('He nuclei conservation failure')
        samples[name]=(x,np.log(T))
    return samples,{'node_count':len(H),
       'material_relative_error_max':max(float(np.max(np.abs((material(x,np.exp(lt))[0]-E0)/np.maximum(np.abs(E0),1e-300)))) for x,lt in samples.values()),
       'parent_path_scale_min':float(np.min(scale)),
       'parent_path_scale_median':float(np.median(scale)),
       'delta_electron_per_H_median':float(np.median(((samples['CHEM_PLUS'][0][:,1]+samples['CHEM_PLUS'][0][:,3]+2*samples['CHEM_PLUS'][0][:,4])-(samples['CHEM_MINUS'][0][:,1]+samples['CHEM_MINUS'][0][:,3]+2*samples['CHEM_MINUS'][0][:,4]))/H)),
       'delta_logT_median':float(np.median(samples['CHEM_PLUS'][1]-samples['CHEM_MINUS'][1])),
       'max_total_point_parent_logT_difference':float(np.max(np.abs(samples['CHEM_PLUS'][1]-samples['CHEM_MINUS'][1])))}
def step_one(module,model,base,x,tlog,H,He,t0,t1):
    mid=t0+(t1-t0)/2
    kw=dict(model=model,base=base,parent_pop=module._I(x),parent_logt=module._I(tlog),t0=t0,t1=t1,total_h=H,total_he=He)
    f=module.run_step(**kw)
    if not f.certified:return {'status':'PHYSICS_UNCERTIFIED','phase':'full','classification':f.classification},None
    kw.update(t1=mid)
    g0=module.run_step(**kw)
    if not g0.certified:return {'status':'PHYSICS_UNCERTIFIED','phase':'half1','classification':g0.classification},None
    kw.update(t0=mid,t1=t1,parent_pop=g0.population,parent_logt=g0.log_temperature)
    g1=module.run_step(**kw)
    if not g1.certified:return {'status':'PHYSICS_UNCERTIFIED','phase':'half2','classification':g1.classification},None
    return {'status':'CERTIFIED_MAP_IMAGES_ONLY','phase':'all'},(f,g1)
def calculate(repo,lane,out):
    repo=Path(repo).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    prior=load_prior()
    if lane not in prior.LANES:raise ValueError('unsupported lane')
    stage=repo/prior.REL_STAGE
    worker=prior.importlib.util.module_from_spec(prior.importlib.util.spec_from_file_location('foo',stage/'analysis/attempt_worker.py'))
    # The original source is loaded by an independent, checked module name.
    spec=prior.importlib.util.spec_from_file_location('original_worker_correlated',stage/'analysis/attempt_worker.py')
    worker=prior.importlib.util.module_from_spec(spec);sys.modules[spec.name]=worker;spec.loader.exec_module(worker)
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    if prior.sha256(worker.KERNEL_PATH)!=prior.SOURCE_KERNEL_SHA256:
        raise ValueError('immutable original 26-event source kernel drift')
    dec,locked=prior.source_state(stage,lane,worker.state_io)
    if locked['accepted_array_sha256']!=prior.SOURCE_ACCEPTED_ARRAY_SHA256:raise ValueError('source parent byte drift')
    base,_,_,H,He=worker._context(m,lane)
    samples,path_info=correlated_points(dec.population_lower,dec.population_upper,
                   dec.log_temperature_lower,dec.log_temperature_upper,H,He)
    duration=float(base.forcing.duration_seconds(0))
    t0=duration*prior.PARENT_TICK/prior.TOTAL_TICKS
    t1=duration*(prior.PARENT_TICK+1)/prior.TOTAL_TICKS
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    rows=[];details={}
    for name,(x,tlog) in samples.items():
        state,result=step_one(m,model,base,x,tlog,H,He,t0,t1)
        details[name]=state
        if result is None:continue
        f,g1=result
        full=prior.coordinates(m,f.population,f.log_temperature,H,He)
        half=prior.coordinates(m,g1.population,g1.log_temperature,H,He)
        dd={k:prior.interval_difference(full[k].lo,full[k].hi,half[k].lo,half[k].hi) for k in full}
        for i in range(prior.NODES):
            row={'lane':lane,'name':name,'node':i,'parent_xHII':x[i,1]/H[i],
                 'parent_xHeII':x[i,3]/He[i],'parent_xHeIII':x[i,4]/He[i],
                 'parent_T_K':math.exp(tlog[i])}
            for k in dd:
                row[k+'_D_lower']=dd[k][0][i]
                row[k+'_D_upper']=dd[k][1][i]
                row[k+'_D_center']=(dd[k][0][i]+dd[k][1][i])/2.
                row[k+'_D_abs_upper']=dd[k][3][i]
            rows.append(row)
        details[name]['max_logT_independent_box_upper']=float(np.max(dd['log_T'][3]))
        details[name]['max_logT_center_defect']=float(np.max(np.abs((dd['log_T'][0]+dd['log_T'][1])/2)))
        details[name]['max_xHII_independent_box_upper']=float(np.max(dd['x_HII'][3]))
        details[name]['max_xHeII_independent_box_upper']=float(np.max(dd['x_HeII'][3]))
        details[name]['max_xHeIII_independent_box_upper']=float(np.max(dd['x_HeIII'][3]))
    if rows:
        name=out/('ORIGINAL_26EVENT_MATERIAL_PARENT_'+lane+'.csv.gz')
        with name.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=7) as z:
                with io.TextIOWrapper(z,encoding='utf-8',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
                    for row in rows:w.writerow({k:format(float(v),'.17g') if isinstance(v,(float,np.floating)) else v for k,v in row.items()})
        digest=prior.sha256(name)
    else:digest=None
    summary={'schema':'rei.f05.source_conditional_correlated_material_parent.v1',
       'lane':lane,'source_archive_sha256':locked['archive_sha256'],
       'source_parent_array_sha256':locked['accepted_array_sha256'],
       'source_kernel_sha256':prior.SOURCE_KERNEL_SHA256,
       'source_origin_PR':328,'parent_tick':160,'original_interval_ticks':131072,
       'time_s_start':t0,'time_s_end':t1,'path':path_info,
       'samples':details,'new_data_rows':len(rows),
       'csv_sha256':digest,'strict_logT_local_error_limit_unchanged':GATE,
       'old_full_parent_box_error_unchanged':prior.OBSERVED_FROZEN_ONE_TICK,
       'all_parent_joint_Dh_certificate':False,'original_first_full_interval_completed':False,
       'central_DAG':'28/88','working_DAG':'33/88','rec_physical_H5':'0/313',
       'new_canonical_nodes':0,'production':'HOLD','auto_next':False}
    (out/'SCIENTIFIC_RESULT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    return summary
if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--repo',type=Path,default=REPO_ROOT)
    cli.add_argument('--lane',required=True)
    cli.add_argument('--out',type=Path,required=True)
    a=cli.parse_args()
    s=calculate(a.repo,a.lane,a.out)
    print(json.dumps({'lane':a.lane,'samples':s['samples'],'new_data_rows':s['new_data_rows'],'canonical':'28/88'},sort_keys=True))
    if s['new_data_rows']!=2*46080:raise SystemExit(3)
