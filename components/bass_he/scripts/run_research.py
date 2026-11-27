#!/usr/bin/env python3
"""Bounded audit-led numerical research runner.

This runner preserves legacy pilot/quadrature modes and adds DR8 support-split
adaptive Eq.54 integration. It is a research harness, not production CT2.
"""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,json,multiprocessing as mp,os,platform,sys,time,traceback
from pathlib import Path
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[name]='1'
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(SCRIPTS))
import numpy as np
from bass_he.geometry import EvidenceCache,atomic_json,contour_geometry,radial_quadrature,adaptive_vector_quadrature,AdaptiveQuadratureError,adaptive_seed_rhos
from bass_he.spectral import find_exceptional_point,monodromy
from bass_he.rotation import full_rotation_batch
from bass_he.transport import apply_eq50
from bass_he.eq54 import (support_cutoffs,assemble_initial_column_batch,decode_component_integral,
                          DeltaSurrogate,surrogate_geometry_mapping,validate_delta_surrogate)
from arseny_reimpl.eq50_scoped import ordered_scoped_branches,branch_state_indices
from arseny_reimpl.cross_section import projectile_velocity_au
from arseny_reimpl.rotational import full_rotational_probability
from run_contract import bind_run,run_lock,snapshot_geometry

REF_DELTA={'Q12':1.42615,'Q23':.32002,'Qother':.48038,'Qm1':.68560,'S23':.46940}
BRANCHES=ordered_scoped_branches()
_SOURCE_DEPENDENCIES={
    'ep':('src/bass_he/spectral.py','src/arseny_reimpl/term_complex.py','src/arseny_reimpl/term_real.py'),
    'geometry':('src/bass_he/geometry.py','src/bass_he/spectral.py','src/arseny_reimpl/term_complex.py','src/arseny_reimpl/term_real.py'),
    'transport':('src/bass_he/eq54.py','src/bass_he/rotation.py','src/bass_he/transport.py','src/arseny_reimpl/eq50_scoped.py','src/arseny_reimpl/cross_section.py','src/arseny_reimpl/rotational.py'),
}

def source_dependencies(kind):
    try:return _SOURCE_DEPENDENCIES[kind]
    except KeyError as exc:raise KeyError(f'unknown scientific dependency kind {kind!r}') from exc

def dependency_source_identity(kind):
    h=hashlib.sha256()
    for rel in source_dependencies(kind):
        p=ROOT/rel;h.update(rel.encode()+b'\0'+p.read_bytes())
    return h.hexdigest()

def source_identity():
    h=hashlib.sha256()
    paths=list(sorted((ROOT/'src').rglob('*.py')))+list(sorted((ROOT/'scripts').glob('*.py')))
    for p in paths:h.update(str(p.relative_to(ROOT)).encode()+b'\0'+p.read_bytes())
    return h.hexdigest()

def requested_branches(rho,names=None):
    selected=None if names is None else set(names)
    return [b for b in BRANCHES if rho<=b.support_cutoff and (selected is None or b.name in selected)]

def geometry_worker(job):
    name,ep,rho,panels=job;t=time.perf_counter()
    try:
        result=contour_geometry(ep,rho,panels=panels)
        return dict(branch=name,rho=rho,panels=panels,status='SUCCESS',result=result,elapsed_s=time.perf_counter()-t)
    except Exception:
        return dict(branch=name,rho=rho,panels=panels,status='FAILED',traceback=traceback.format_exc(),elapsed_s=time.perf_counter()-t)

def assembly(ep_map,geometry,energies,rhos,*,steps=32):
    E=np.array(energies,float);r=np.array(rhos,float);nr=len(r);ne=len(E)
    delta=np.zeros((nr,len(BRANCHES)));active=np.zeros_like(delta,dtype=bool)
    for i,rho in enumerate(r):
        for k,branch in enumerate(BRANCHES):
            active[i,k]=rho<=branch.support_cutoff
            if active[i,k]:delta[i,k]=geometry[(branch.name,float(rho))]['delta']
    batchE=np.tile(E,nr);batchR=np.repeat(r,ne)
    prot=full_rotation_batch(3,batchE,batchR,steps=steps)
    v=np.array([projectile_velocity_au(x) for x in batchE]);d=np.repeat(delta,ne,axis=0);mask=np.repeat(active,ne,axis=0)
    events=[]
    for b in BRANCHES:
        i,j=branch_state_indices(b);events.append((i-1,j-1,b.state_b[0]==3))
    initial=np.eye(10)[:,[2]]
    out={}
    for factor in (1,2):
        p=np.where(mask,np.exp(-factor*d/v[:,None]),0.)
        out[str(factor)]=apply_eq50(p,events,prot,initial)[...,0].reshape(nr,ne,10)
    return out

def _run_geometry_jobs(jobs,workers):
    if workers==1:return [geometry_worker(j) for j in jobs]
    ctx=mp.get_context('spawn')
    out=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers,mp_context=ctx) as pool:
        futures=[pool.submit(geometry_worker,j) for j in jobs]
        for f in concurrent.futures.as_completed(futures):out.append(f.result())
    return out

def execute_adaptive(args,out,cache,eps,env,depids):
    energies=np.array([.5,5.]);factors=(1,2);completed=[]
    def ensure_geometry(rhos,panels,branch_names=None):
        rhos=np.unique(np.asarray(rhos,float));geometry={};jobs=[];keys={}
        for rho in rhos:
            for b in requested_branches(float(rho),branch_names):
                key=dict(source=depids['geometry'],environment=env,kind='CONTOUR',name=b.name,rho=float(rho),panels=int(panels),depth=96)
                cached=cache.get(key)
                if cached is not None:
                    if cached.get('status')!='SUCCESS':raise RuntimeError(f'cached failed geometry {b.name} rho={rho}')
                    geometry[(b.name,float(rho))]=cached['result'];completed.append(cached)
                else:
                    job=(b.name,eps[b.name],float(rho),int(panels));jobs.append(job);keys[(b.name,float(rho),int(panels))]=key
        for result in _run_geometry_jobs(jobs,args.workers):
            completed.append(result);snapshot_geometry(out,completed,attempt=result)
            if result['status']!='SUCCESS':raise RuntimeError(f"geometry failure {result['branch']} rho={result['rho']}")
            key=keys[(result['branch'],result['rho'],result['panels'])];cache.put(key,result)
            geometry[(result['branch'],result['rho'])]=result['result']
        if jobs:snapshot_geometry(out,completed)
        return geometry

    nominal_cuts=support_cutoffs(rotation_cut_scale=1.0)
    surrogate=None;surrogate_report=None
    if args.geometry_mode=='surrogate':
        seeds=adaptive_seed_rhos(nominal_cuts,rule=args.rule)
        anchor_rhos=set(float(x) for x in seeds);anchor_rhos.add(0.0)
        for b in BRANCHES:anchor_rhos.add(float(b.support_cutoff))
        exact=ensure_geometry(sorted(anchor_rhos),args.panels)
        anchors={b.name:[] for b in BRANCHES}
        for b in BRANCHES:
            vals=[]
            for rho in sorted(x for x in anchor_rhos if x<=b.support_cutoff):
                rec=exact.get((b.name,float(rho)))
                if rec is not None:vals.append((float(rho),float(rec['delta'])))
            anchors[b.name]=vals
        surrogate=DeltaSurrogate(anchors)
        hold=[];hold_rhos=[]
        for b in BRANCHES:
            for frac in (.37,.79):hold_rhos.append(float(frac*b.support_cutoff))
        held=ensure_geometry(hold_rhos,args.panels)
        for b in BRANCHES:
            for frac in (.37,.79):
                rho=float(frac*b.support_cutoff);hold.append(dict(branch=b.name,rho=rho,delta=float(held[(b.name,rho)]['delta'])))
        surrogate_report=validate_delta_surrogate(surrogate,hold)
        surrogate_report['threshold']=float(args.surrogate_rtol)
        surrogate_report['status']='PASS' if surrogate_report['max_relative_error']<=args.surrogate_rtol else 'FAIL'
        atomic_json(out/'SURROGATE_VALIDATION.json',surrogate_report)
        if surrogate_report['status']!='PASS':raise RuntimeError('Delta surrogate held-out validation failed')

    def evaluator_for_scale(scale):
        def evaluate(rhos):
            r=np.asarray(rhos,float)
            if args.geometry_mode=='surrogate':geom=surrogate_geometry_mapping(surrogate,r)
            else:geom=ensure_geometry(r,args.panels)
            return assemble_initial_column_batch(geom,energies,r,exponent_factors=factors,
                   rotation_steps=args.rotation_steps,rotation_cut_scale=scale)['components']
        return evaluate

    def integrate_scale(scale,rtol):
        cuts=support_cutoffs(rotation_cut_scale=scale)
        result=adaptive_vector_quadrature(evaluator_for_scale(scale),cuts,rtol=rtol,atol=args.atol,
                                          max_intervals=args.max_intervals,rule=args.rule)
        decoded=decode_component_integral(result['integral'],energies,factors)
        return cuts,result,decoded

    cuts,q,decoded=integrate_scale(1.0,args.rtol)
    payload=dict(status='ADAPTIVE_PILOT_COMPLETE',geometry_mode=args.geometry_mode,energies_keV_u=energies,
                 exponent_factors=factors,cutoffs=cuts,labels=assemble_initial_column_batch(
                 surrogate_geometry_mapping(surrogate,[0.0]) if surrogate is not None else ensure_geometry([0.0],args.panels),
                 energies,[0.0],exponent_factors=factors,rotation_steps=args.rotation_steps)['labels'],
                 quadrature=q,lanes=decoded,surrogate_validation=surrogate_report,
                 claim='FINITE_INDEXED_STATE_ADAPTIVE_RESEARCH_INTEGRAL_NOT_PHYSICAL_PRODUCTION_CROSS_SECTION',
                 elastic_cross_section_computed=False,production=False)
    atomic_json(out/'ADAPTIVE_EQ54.json',payload)
    if args.with_sensitivities:
        scales={}
        for scale in (.9,1.1):
            c,qq,dd=integrate_scale(scale,args.sensitivity_rtol);scales[str(scale)]=dict(cutoffs=c,quadrature=qq,lanes=dd)
        s23=next(b for b in BRANCHES if b.name=='S23')
        s23_rhos=[0.0,.5*s23.support_cutoff,.9*s23.support_cutoff]
        coarse=ensure_geometry(s23_rhos,args.panels,{'S23'});fine=ensure_geometry(s23_rhos,2*args.panels,{'S23'})
        contour=[]
        for rho in s23_rhos:
            a=coarse[('S23',float(rho))]['delta'];b=fine[('S23',float(rho))]['delta']
            contour.append(dict(rho=float(rho),delta_panels=float(a),delta_double_panels=float(b),relative_change=abs(b-a)/max(abs(b),np.finfo(float).tiny)))
        atomic_json(out/'MODEL_SENSITIVITY.json',dict(rotation_cut_scales=scales,s23_contour_panel_sensitivity=contour))
    maxnorm=float(np.max(q['component_error_estimate']/np.maximum(q['component_tolerance'],np.finfo(float).tiny)))
    summary=dict(status='ADAPTIVE_PILOT_COMPLETE',stage='adaptive',geometry_mode=args.geometry_mode,
                 interval_count=q['interval_count'],evaluations=q['evaluations'],refinements=q['refinements'],
                 maximum_normalized_component_error=maxnorm,rtol=args.rtol,atol=args.atol,rule=args.rule,
                 surrogate_max_relative_error=None if surrogate_report is None else surrogate_report['max_relative_error'],
                 surrogate_threshold=None if surrogate_report is None else args.surrogate_rtol,
                 production_claim=False,physical_cross_section_claim=False,exponent_policy_resolved=False,
                 model_systematics_open=True)
    atomic_json(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True);return 0

def execute(args):
    out=Path(args.out);sid=source_identity();env=dict(numpy=np.__version__,python=platform.python_version(),machine=platform.machine())
    depids={k:dependency_source_identity(k) for k in _SOURCE_DEPENDENCIES}
    binding=dict(stage=args.stage,panels=args.panels,quadrature_order=args.order,rtol=args.rtol,atol=args.atol,
                 max_intervals=args.max_intervals,rule=args.rule,geometry_mode=args.geometry_mode,
                 surrogate_rtol=args.surrogate_rtol,rotation_steps=args.rotation_steps,with_sensitivities=args.with_sensitivities,
                 sensitivity_rtol=args.sensitivity_rtol,source_sha256=sid,dependency_sha256=depids,environment=env,
                 runner_sha256=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('run_contract.py').read_bytes()).hexdigest())
    bind_run(out,binding,resume=args.resume);cache=EvidenceCache(args.cache_dir or out/'cache');eps={};ep_details=[]
    atomic_json(out/'RUN_SPEC.json',dict(**binding,workers=args.workers,claimed_scope='audit-led bounded research pilot; no production'))
    for b in BRANCHES:
        key=dict(source=depids['ep'],environment=env,kind='EP_MONODROMY',name=b.name,depth=96)
        cached=cache.get(key)
        if cached is None:
            t=time.perf_counter()
            try:
                ep=find_exceptional_point(b.state_a,b.state_b,b.R,depth=96);mon=monodromy(ep,steps=64,radius=.01)
                if not mon['passed']:raise RuntimeError('monodromy failed')
                cached=dict(ep=ep,monodromy=mon,reference_distance=abs(ep['R']-b.R),elapsed_s=time.perf_counter()-t);cache.put(key,cached)
            except Exception:
                atomic_json(out/f'FAIL_EP_{b.name}.json',dict(status='FAILED',traceback=traceback.format_exc()));raise
        eps[b.name]=cached['ep'];ep_details.append(dict(branch=b.name,**cached));atomic_json(out/'EP_CERTIFICATES.json',ep_details)
        print('EP',b.name,'R=',cached['ep']['R'],'reference delta=',cached['reference_distance'],flush=True)
    if args.stage=='adaptive':return execute_adaptive(args,out,cache,eps,env,depids)
    if args.stage=='pilot':rhos=np.array([0.,.3]);weights=None
    else:
        cuts=support_cutoffs(rotation_cut_scale=1.0);rhos,weights=radial_quadrature(cuts,order=args.order)
        atomic_json(out/'QUADRATURE_NODES.json',dict(cutoffs=cuts,rhos=rhos,weights_a0sq=weights,order=args.order))
    jobs=[];geometry={};completed=[]
    for rho in rhos:
        for b in requested_branches(float(rho)):
            key=dict(source=depids['geometry'],environment=env,kind='CONTOUR',name=b.name,rho=float(rho),panels=args.panels,depth=96)
            cached=cache.get(key)
            if cached is not None:geometry[(b.name,float(rho))]=cached['result'];completed.append(cached)
            else:jobs.append((b.name,eps[b.name],float(rho),args.panels))
    def accept(result):
        completed.append(result)
        if result['status']=='SUCCESS':
            key=dict(source=depids['geometry'],environment=env,kind='CONTOUR',name=result['branch'],rho=result['rho'],panels=result['panels'],depth=96)
            cache.put(key,result);geometry[(result['branch'],result['rho'])]=result['result']
        snapshot_geometry(out,completed,attempt=result);print('CONTOUR',result['branch'],result['rho'],result['status'],round(result['elapsed_s'],3),flush=True)
    t=time.perf_counter()
    for result in _run_geometry_jobs(jobs,args.workers):accept(result)
    elapsed=time.perf_counter()-t;snapshot_geometry(out,completed);failed=[x for x in completed if x['status']!='SUCCESS']
    summary=dict(stage=args.stage,geometry_jobs=len(completed),new_geometry_jobs=len(jobs),failed_jobs=len(failed),geometry_wall_s=elapsed,workers=args.workers,source_sha256=sid,production_claim=False,exponent_policy_resolved=False)
    if failed:summary['status']='UNRESOLVED_GEOMETRY';atomic_json(out/'SUMMARY.json',summary);return 2
    values=assembly(eps,geometry,[.5,5.],rhos);cols={}
    for factor,ys in values.items():cols[factor]=dict(max_column_sum_defect=float(np.max(abs(ys.sum(-1)-1))),minimum=float(ys.min()),probabilities=ys)
    atomic_json(out/'INITIAL_COLUMN_OUTPUTS.json',dict(energies_keV_u=[.5,5.],rhos=rhos,lanes=cols,observable='indexed-state probabilities with inherited upper-shell absorbing rule; no disjoint physical channel assignment'))
    if args.stage=='pilot':
        summary['source_delta_errors']={b.name:abs(geometry[(b.name,0.)]['delta']-REF_DELTA[b.name])/REF_DELTA[b.name] for b in BRANCHES}
        energies=np.tile([.5,5.],3);rs=np.repeat([.1,.3,.5],2);times_old=[];times_new=[]
        for _ in range(3):
            t=time.perf_counter();old=np.array([full_rotational_probability(3,E,r,steps=512) for E,r in zip(energies,rs)]);times_old.append(time.perf_counter()-t)
            t=time.perf_counter();new=full_rotation_batch(3,energies,rs,steps=32);times_new.append(time.perf_counter()-t)
        finer=full_rotation_batch(3,energies,rs,steps=64)
        summary['rotation_benchmark']=dict(workload='six Nmax3 matrices',legacy_steps=512,new_steps=32,legacy_median_s=float(np.median(times_old)),new_batch_median_s=float(np.median(times_new)),median_speedup=float(np.median(times_old)/np.median(times_new)),max_difference_vs_legacy512=float(np.max(abs(new-old))),max_difference_new32_vs_new64=float(np.max(abs(new-finer))))
    else:
        sigma={}
        for factor,ys in values.items():
            off=ys.copy();off[:,:,2]=0.;area=np.einsum('r,rej->ej',weights,off);sigma[factor]=dict(indexed_transition_areas_a0sq=area,reaction_loss_area_a0sq=area.sum(-1))
        atomic_json(out/'SCOPED_EQ54_PILOT.json',dict(energies_keV_u=[.5,5.],lanes=sigma,quadrature_order=args.order,claim='FINITE_INDEXED_STATE_PILOT_NOT_CONVERGED_NOT_PHYSICAL_CHANNEL_CROSS_SECTION',elastic_cross_section_computed=False,production=False))
    summary['status']='BOUNDED_PILOT_COMPLETE';atomic_json(out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True);return 0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='runs/research_v2');ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--stage',choices=['pilot','quadrature','adaptive'],default='pilot');ap.add_argument('--resume',action='store_true')
    ap.add_argument('--order',type=int,default=1);ap.add_argument('--panels',type=int,default=32);ap.add_argument('--cache-dir',default=None)
    ap.add_argument('--rtol',type=float,default=.02);ap.add_argument('--atol',type=float,default=1e-8);ap.add_argument('--max-intervals',type=int,default=96)
    ap.add_argument('--rule',choices=['gk7','gk15'],default='gk7');ap.add_argument('--geometry-mode',choices=['exact','surrogate'],default='exact')
    ap.add_argument('--surrogate-rtol',type=float,default=2e-4);ap.add_argument('--rotation-steps',type=int,default=32)
    ap.add_argument('--with-sensitivities',action='store_true');ap.add_argument('--sensitivity-rtol',type=float,default=.03)
    args=ap.parse_args()
    if not(1<=args.workers<=32):ap.error('--workers must be in 1..32')
    if args.order<1 or args.order>32:ap.error('--order must be in 1..32')
    if args.panels<8 or args.panels%2:ap.error('--panels must be even and >=8')
    if args.rotation_steps<4:ap.error('--rotation-steps must be >=4')
    if args.rtol<=0 or args.atol<0 or args.surrogate_rtol<=0 or args.sensitivity_rtol<=0:ap.error('invalid tolerances')
    with run_lock(args.out):return execute(args)

if __name__=='__main__':raise SystemExit(main())
