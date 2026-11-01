#!/usr/bin/env python3
"""Source-locked REI 26-event full/two-half finite parent-direction physics.

This tests nine *admissible points in the published marginal box*, not the
original joint reachable parent set and not a validated global D_h(X,theta).
Original kernel, IVP, source and gates are NEVER edited or substituted.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import math
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO_PROBE = HERE.parent / 'rei_igm_tick160_nonlinear_point_20261101' / 'probe.py'
STRESS_FRACTION = 0.8
CASES = ('center', 'logT_minus', 'logT_plus', 'HII_minus', 'HII_plus',
         'HeII_minus', 'HeII_plus', 'HeIII_minus', 'HeIII_plus')


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load source module: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def candidate(poplo, pophi, tlo, thi, total_h, total_he, case, frac=STRESS_FRACTION):
    """Return physical element-conserving candidate in source marginal box.

    One whole 46080-node *correlated direction* varies at a time; it is not a
    spanning set of the 276480-dimensional parent uncertainty domain.
    """
    if case not in CASES or not 0 < frac <= 1:
        raise ValueError('invalid candidate case or stress fraction')
    lo = np.asarray(poplo, dtype=float)
    hi = np.asarray(pophi, dtype=float)
    tlo, thi = np.asarray(tlo, dtype=float), np.asarray(thi, dtype=float)
    h, he = np.asarray(total_h, dtype=float), np.asarray(total_he, dtype=float)
    if lo.ndim != 2 or lo.shape[1] != 5 or hi.shape != lo.shape or tlo.shape != (len(lo),) or thi.shape != tlo.shape or h.shape != tlo.shape or he.shape != h.shape:
        raise ValueError('wrong source dimensions')
    if np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(~np.isfinite(tlo)) or np.any(~np.isfinite(thi)) or np.any(lo<=0) or np.any(lo>hi) or np.any(tlo>thi):
        raise ValueError('bad interval')
    p = lo + (hi - lo)/2
    p[:, 0] = h - p[:,1]
    p[:, 2] = he - p[:,3] - p[:,4]
    t = tlo+(thi-tlo)/2
    axis, _, sign = case.partition('_')
    if case.startswith('logT_'):
        t = t + (frac * (thi-t if sign == 'plus' else tlo-t))
    elif case != 'center':
        # target ion population adjusted with the unique reservoir in the
        # same element family. Other ion populations remain at the center.
        target, reservoir = {'HII': (1,0), 'HeII':(3,2), 'HeIII':(4,2)}[axis]
        total = h if axis == 'HII' else he
        other = np.zeros_like(total) if axis == 'HII' else p[:,4] if axis == 'HeII' else p[:,3]
        feasible_lo = np.maximum(lo[:,target], total - other - hi[:,reservoir])
        feasible_hi = np.minimum(hi[:,target], total - other - lo[:,reservoir])
        if np.any(feasible_hi + 1e-13*np.maximum(total,1) < feasible_lo):
            raise ValueError('empty physical conditional interval')
        c=p[:,target]
        chosen=c+frac*((feasible_hi-c) if sign=='plus' else (feasible_lo-c))
        p[:,target]=chosen
        p[:,reservoir]=total-other-chosen
    tol=128*np.finfo(float).eps*np.maximum(np.maximum(h[:,None],he[:,None]),1e-16)
    if np.any(~np.isfinite(p)) or np.any(p<=0) or np.any(p<lo-tol) or np.any(p>hi+tol):
        raise ValueError('candidate outside positive marginal parent')
    if np.any(t<tlo-1e-14) or np.any(t>thi+1e-14) or np.any(~np.isfinite(t)):
        raise ValueError('temperature outside parent')
    if np.max(abs((p[:,0]+p[:,1])-h))>2e-14 or np.max(abs(np.sum(p[:,2:5],axis=1)-he))>2e-14:
        raise ValueError('not conserving source H/He nuclei')
    return p,t


def observable_intervals(m, step, total_h, total_he):
    pop = step.population
    return dict(
        xHII = (pop.lo[:,1]/total_h, pop.hi[:,1]/total_h),
        xHeII = (pop.lo[:,3]/total_he, pop.hi[:,3]/total_he),
        xHeIII = (pop.lo[:,4]/total_he, pop.hi[:,4]/total_he),
        logT = (step.log_temperature.lo, step.log_temperature.hi),
    )


def difference_bounds(a, b):
    """Safe independent-output enclosing difference for ONE selected parent."""
    low = np.nextafter(np.asarray(a[0])-np.asarray(b[1]), -np.inf)
    high = np.nextafter(np.asarray(a[1])-np.asarray(b[0]), np.inf)
    if np.any(low>high):
        raise ValueError('empty full/half difference enclosure')
    upper = np.maximum(np.abs(low), np.abs(high))
    center = ((np.asarray(a[0])+np.asarray(a[1]))-(np.asarray(b[0])+np.asarray(b[1])))/2
    return low, high, upper, center


def run_one_map(m,model,base,tot_h,tot_he,pp,lt,t0,tm,t1):
    kw=dict(model=model,base=base,parent_pop=m._I(pp),parent_logt=m._I(lt),
            t0=t0,t1=t1,total_h=tot_h,total_he=tot_he)
    try:
        full=m.run_step(**kw)
        if not full.certified:return None, 'full',str(full.classification)
        kw['t1']=tm
        first=m.run_step(**kw)
        if not first.certified:return None,'half1',str(first.classification)
        kw.update(parent_pop=first.population,parent_logt=first.log_temperature,t0=tm,t1=t1)
        last=m.run_step(**kw)
        if not last.certified:return None,'half2',str(last.classification)
    except (ValueError,FloatingPointError,ArithmeticError) as e:
        return None,'exception', f'{type(e).__name__}: {str(e)[:600]}'
    return (full,last),None,None


def deterministic_gzip_writer(path):
    """Deterministic gzip independent of file name and wall-clock timestamp."""
    b=open(path,'wb')
    z=gzip.GzipFile(filename='',mode='wb',fileobj=b,mtime=0,compresslevel=6)
    return b,z,io.TextIOWrapper(z,encoding='utf-8',newline='')


def run(repo:Path,lane:str,out:Path):
    repo,out=Path(repo).resolve(),Path(out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    prior=load_module('prior_readonly_probe',repo/'research/rei_igm_tick160_nonlinear_point_20261101/probe.py')
    if lane not in prior.LANES:
        raise ValueError('invalid original lane')
    stage=repo/prior.REL_STAGE
    worker=load_module('original_tick160_worker',stage/'analysis/attempt_worker.py')
    if prior.sha256(worker.KERNEL_PATH)!=prior.SOURCE_KERNEL_SHA256:
        raise ValueError('original nonlinear kernel byte drift')
    if not worker.jax_guard.install_if_missing():
        raise RuntimeError('original JAX import-only guard failed')
    m=worker._kernel()
    decoded, source=prior.source_state(stage,lane,worker.state_io)
    base,y,lt_base,total_h,total_he=worker._context(m,lane)
    if y.shape != (prior.NODES,5):
        raise ValueError('not the full original physical source')
    t0=float(base.forcing.duration_seconds(0))*160/131072
    t1=float(base.forcing.duration_seconds(0))*161/131072
    tm=(t0+t1)/2
    model=m.rim.ReducedIntervalModel.from_repo(repo)
    result=dict(schema='REI_REAL_26EVENT_PARENT_DIRECTIONAL_STRESS_V1',lane=lane,
         original_archive_sha256=source['archive_sha256'],
         original_state_array_sha256=source['accepted_array_sha256'],
         original_kernel_sha256=prior.SOURCE_KERNEL_SHA256,
         source_state_member=source['state_member'],
         original_gate=prior.GATE, original_failed_cross_box=prior.OBSERVED_FROZEN_ONE_TICK,
         original_accepted_tick=160,original_total_ticks=131072,
         spatial_nodes=prior.NODES,stress_fraction=STRESS_FRACTION,
         selected_candidate_count=len(CASES),
         scope='9 admissible marginal-box point candidates along 4 global parent directions; NOT full-X or original source joint derivative enclosure',
         new_canonical_nodes=0,central_reported='28/88',working_reported='33/88',
         production='HOLD',no_new_IVP=True,distinct_author='NOT_RUN',
         cases=[])
    path=out/('REAL_26EVENT_PARENT_DIRECTIONS_'+lane+'.csv.gz')
    raw,z,writer=deterministic_gzip_writer(path)
    failed=False
    samples={}
    try:
        csvout=csv.writer(writer)
        obs=['xHII','xHeII','xHeIII','logT']
        csvout.writerow(['case','node','parent_xHII','parent_xHeII','parent_xHeIII','parent_T_K',
            *[f'{k}_{q}' for k in obs for q in ('D_lo','D_hi','D_absupper','D_center_est')]])
        for case in CASES:
            pp,pt=candidate(decoded.population_lower,decoded.population_upper,
                            decoded.log_temperature_lower,decoded.log_temperature_upper,
                            total_h,total_he,case)
            maps,phase,reason=run_one_map(m,model,base,total_h,total_he,pp,pt,t0,tm,t1)
            if maps is None:
                result['cases'].append(dict(name=case,status='UNSUCCESSFUL',phase=phase,reason=reason))
                failed=True
                continue
            a=observable_intervals(m,maps[0],total_h,total_he)
            b=observable_intervals(m,maps[1],total_h,total_he)
            diffs={k:difference_bounds(a[k],b[k]) for k in obs}
            info=dict(name=case,status='SCOPED_CANDIDATE_POINT_PHASES_CERTIFIED',nodes=prior.NODES,observables={})
            for k,(lo,hi,upper,centre) in diffs.items():
                info['observables'][k]=dict(max_independent_output_box_upper=float(np.max(upper)),
                    median_independent_output_box_upper=float(np.median(upper)),
                    max_abs_center_estimate=float(np.max(abs(centre))),
                    nodes_below_original_gate=int(np.count_nonzero(upper<prior.GATE)),
                    all_finite=bool(np.isfinite(upper).all()))
                if not np.isfinite(upper).all():raise ValueError('nonfinite real-source outputs')
            samples[case] = {k:(diffs[k][0],diffs[k][1],diffs[k][2],diffs[k][3]) for k in obs}
            samples[case]['parent']=(pp[:,1]/total_h,pp[:,3]/total_he,pp[:,4]/total_he,pt)
            for i in range(prior.NODES):
                vals=[pp[i,1]/total_h[i],pp[i,3]/total_he[i],pp[i,4]/total_he[i],math.exp(pt[i])]
                vals.extend(float(col[i]) for k in obs for col in diffs[k])
                csvout.writerow([case,i,*[format(float(v),'.17g') for v in vals]])
            result['cases'].append(info)
            writer.flush()
            print('REAL_CASE',lane,case, 'LOGT_MAX',info['observables']['logT']['max_independent_output_box_upper'],flush=True)
    finally:
        writer.close();z.close();raw.close()
    # A direction-wise finite secant of the *centers of independently bounded*
    # point-defect intervals. It is diagnostic, not an interval Jacobian.
    result['directional_secants']={}
    for ax,index in (('logT',3),('HII',0),('HeII',1),('HeIII',2)):
        lo_case,hi_case=ax+'_minus',ax+'_plus'
        if lo_case not in samples or hi_case not in samples:
            continue
        xlo=samples[lo_case]['parent'][index]
        xhi=samples[hi_case]['parent'][index]
        delta=xhi-xlo
        valid=np.abs(delta)>1e-14
        row={'nonzero_source_parent_nodes':int(np.count_nonzero(valid)),
             'max_perturbation_coordinate':float(np.max(abs(delta))),
             'observables':{}}
        for k in ('logT','xHII','xHeII','xHeIII'):
            bottom=samples[lo_case][k]
            top=samples[hi_case][k]
            # Compare two independent interval enclosures at two selected
            # inputs. The true D difference is enclosed but no intermediate
            # parents or source-parameter directions are covered.
            dl,dh,du,dc=difference_bounds((top[0],top[1]),(bottom[0],bottom[1]))
            cl=top[3]-bottom[3]
            slope=np.divide(cl,delta,out=np.zeros_like(cl),where=valid)
            row['observables'][k]={'max_difference_box_upper':float(np.max(du)),
                 'max_abs_center_secant':float(np.max(abs(cl))),
                 'max_abs_center_slope_noncertified':float(np.max(abs(slope[valid]))) if np.any(valid) else 0.,
                 'median_abs_center_secant':float(np.median(abs(cl)))}
        result['directional_secants'][ax]=row
    if samples:
        result['candidate_logT_max_envelope']=float(max(np.max(x['logT'][2]) for x in samples.values()))
        result['candidate_logT_gate_headroom']=float(2e-4-result['candidate_logT_max_envelope'])
    result['csv_file']=path.name
    result['csv_sha256']=prior.sha256(path)
    result['successful_candidate_points']=sum(x['status'].startswith('SCOPED') for x in result['cases'])
    result['new_model_rows']=prior.NODES*result['successful_candidate_points']
    result['overall']='SCOPED_POINT_SCIENCE_COMPLETE' if not failed and result['successful_candidate_points']==len(CASES) else 'PARTIAL_CANDIDATE_FAILURE_PRESERVED'
    (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--lane',choices=('LOCAL_NEUTRAL_HAZARD_PRIMARY','RECOMBINATION_WEIGHTED_AUDITOR','SCRIPT_SELF_SHIELDING_AUDITOR'),required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    v=run(args.repo,args.lane,args.output)
    print(json.dumps(dict(lane=args.lane,status=v['overall'],points=v['successful_candidate_points'],rows=v['new_model_rows'],canonical_delta=0)),flush=True)
    if v['overall']!='SCOPED_POINT_SCIENCE_COMPLETE':raise SystemExit(3)
