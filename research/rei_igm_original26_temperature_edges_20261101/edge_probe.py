#!/usr/bin/env python3
"""Source-authentic 26-event tick160 T-edge parent-point MPRK22/SDIRK2 diagnostic.


This removes *parent state width* by evaluating one common midpoint in the
sealed nonlinear map; it DOES NOT establish a joint uncertainty enclosure of
F_h(X)-H_h(X), nor authorize acceptance of the rejected interval.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, importlib.util, io, json, math, struct, sys, tarfile
from pathlib import Path
import numpy as np


REL_STAGE = ('stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_'
             'R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY')
ARCHIVE_NAME = 'first_interval_r2_blocked_minimum_step.tar.gz'
ARCHIVE_SHA256 = 'a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b'
SOURCE_KERNEL_SHA256 = '579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644'
PARENT_TICK = 160
TOTAL_TICKS = 131072
NODES = 46080
SOURCE_ACCEPTED_ARRAY_SHA256 = 'cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01'
LANES = ('LOCAL_NEUTRAL_HAZARD_PRIMARY', 'RECOMBINATION_WEIGHTED_AUDITOR',
         'SCRIPT_SELF_SHIELDING_AUDITOR')
GATE = 2e-4
OBSERVED_FROZEN_ONE_TICK = 2.1245050576368385e-4




def sha256(path):
    dig = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            dig.update(block)
    return dig.hexdigest()




def interval_difference(a_lo, a_hi, b_lo, b_hi):
    """Independent-output enclosure A-B; pointwise parental identity is separate."""
    a_lo, a_hi = np.asarray(a_lo), np.asarray(a_hi)
    b_lo, b_hi = np.asarray(b_lo), np.asarray(b_hi)
    if np.any(a_lo > a_hi) or np.any(b_lo > b_hi):
        raise ValueError('inverted box')
    low, high = np.nextafter(a_lo-b_hi, -np.inf), np.nextafter(a_hi-b_lo, np.inf)
    upper = np.maximum(np.abs(low), np.abs(high))
    lower = np.where(low > 0, low, np.where(high < 0, -high, 0))
    return low, high, lower, upper




def source_state(stage, lane, io):
    archive = stage / 'local_results' / ARCHIVE_NAME
    digest = sha256(archive)
    if digest != ARCHIVE_SHA256:
        raise ValueError('IMMUTABLE_SOURCE_ARCHIVE_HASH_MISMATCH:'+digest)
    with tarfile.open(archive, 'r:gz') as tar:
        matches = [m for m in tar if m.isfile() and m.name.endswith('/'+lane+'.state')
                   and 'g-00000003-tick-000160' in m.name]
        if len(matches) != 1:
            raise ValueError('SOURCE_ACCEPTED_STATE_NOT_UNIQUE:'+lane)
        data = tar.extractfile(matches[0]).read()
    if not data.startswith(b'REIADP1\x00'):raise ValueError('IMMUTABLE_ACCEPTED_STATE_MAGIC')
    headerlen = struct.unpack_from('<Q',data,8)[0]
    raw_array_sha = hashlib.sha256(data[16+headerlen:]).hexdigest()
    if raw_array_sha != SOURCE_ACCEPTED_ARRAY_SHA256:
        raise ValueError('IMMUTABLE_ACCEPTED_46080_ARRAY_DRIFT observed='+raw_array_sha+' expected='+SOURCE_ACCEPTED_ARRAY_SHA256+' member='+matches[0].name+' headerlen='+str(headerlen)+' bytes='+str(len(data)))
    decoded = io.decode_state(data)
    md = decoded.metadata
    if md.get('endpoint_tick') != PARENT_TICK or md.get('accepted_index') != 3 or md.get('lane') != lane:
        raise ValueError('SOURCE_STATE_METADATA_OWNER_MISMATCH')
    if md.get('predecessor_kernel_sha256') != SOURCE_KERNEL_SHA256:
        raise ValueError('PREDECESSOR_KERNEL_LOCK_DRIFT')
    if decoded.population_lower.shape != (NODES, 5) or decoded.log_temperature_lower.shape != (NODES,):
        raise ValueError('SOURCE_NODE_COUNT_DRIFT')
    return decoded, {'archive_sha256':digest,'source_state_sha256':hashlib.sha256(data).hexdigest(),
                     'state_member':matches[0].name,'accepted_array_sha256':raw_array_sha,'metadata':md}




def element_conserving_parent_candidate(lo, hi, total_h, total_he):
    """One coupled point inside the original interval and exact element totals.


    The raw coordinate midpoints generally violate linear H/He conservation
    because interval component bounds are not a correlated state. Select HII,
    HeII, HeIII midpoints and reconstruct their complement reservoirs. This is
    a candidate point, NOT a proof that it belongs to the full nonlinear parent
    uncertainty set or that all source-owner correlations are preserved.
    """
    lo=np.asarray(lo);hi=np.asarray(hi)
    if lo.shape!=(NODES,5) or hi.shape!=lo.shape:
        raise ValueError('SOURCE_PARENT_POPULATION_SHAPE')
    x=0.5*lo+0.5*hi
    x[:,0]=total_h-x[:,1]
    x[:,2]=total_he-x[:,3]-x[:,4]
    if not np.all(np.isfinite(x)) or np.any(x<=0):
        raise ValueError('NONPHYSICAL_MIDPOINT_SOURCE')
    # Lo/hi are previously outward rounded f64 bounds. A handful of ulps are
    # permitted for reconstructed sums, never clip to satisfy this test.
    tol=64*np.finfo(float).eps*np.maximum(np.maximum(total_h[:,None],total_he[:,None]),1e-12)
    if np.any(x<lo-tol) or np.any(x>hi+tol):
        raise ValueError('POINT_NOT_IN_RETAINED_INTERVAL')
    if not np.allclose(x[:,0]+x[:,1],total_h,atol=3e-15,rtol=3e-15):
        raise ValueError('H_TOTAL_NOT_CLOSED')
    if not np.allclose(x[:,2]+x[:,3]+x[:,4],total_he,atol=3e-15,rtol=3e-15):
        raise ValueError('HE_TOTAL_NOT_CLOSED')
    return x




def coordinates(m, pop, logt, total_h, total_he):
    coords={'x_HII':m._I(pop.lo[:,1]/total_h,pop.hi[:,1]/total_h),
            'x_HeII':m._I(pop.lo[:,3]/total_he,pop.hi[:,3]/total_he),
            'x_HeIII':m._I(pop.lo[:,4]/total_he,pop.hi[:,4]/total_he),
            'log_T':logt}
    yhe=m._I(total_he/total_h)
    xe=coords['x_HII']+yhe*(coords['x_HeII']+2*coords['x_HeIII'])
    coords['xe_per_H']=xe
    coords['binding_eV_per_H']=(m.rim.CHI_H_EV*coords['x_HII']
         +yhe*(m.rim.CHI_HEI_EV*coords['x_HeII']
         +(m.rim.CHI_HEI_EV+m.rim.CHI_HEII_EV)*coords['x_HeIII']))
    coords['thermal_erg_per_H']=1.5*m.KB*m.iv.exp(logt)*(1+yhe+xe)
    return coords




def run(repo:Path,lane:str,out:Path,temperature_edge:str):
    if temperature_edge not in ('lower','upper'):raise ValueError('INVALID_PARENT_T_EDGE')
    if lane not in LANES:raise ValueError('unknown source lane')
    stage=repo/REL_STAGE
    a=stage/'analysis/attempt_worker.py'
    spec=importlib.util.spec_from_file_location('genuine_tick160_worker',a)
    if not spec or not spec.loader:raise ImportError(a)
    worker=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=worker
    spec.loader.exec_module(worker)
    worker.jax_guard.install_if_missing()
    m=worker._kernel()
    kernel_hash=sha256(worker.KERNEL_PATH)
    if kernel_hash!=SOURCE_KERNEL_SHA256:raise ValueError('ORIGINAL_26_EVENT_KERNEL_DRIFT')
    decoded,src=source_state(stage,lane,worker.state_io)
    base,y,logt,total_h,total_he=worker._context(m,lane)
    if y.shape!=(NODES,5) or np.any(total_h<=0) or np.any(total_he<=0):
        raise ValueError('INCORRECT_46K_PHYSICAL_OWNER')
    halfpop=element_conserving_parent_candidate(decoded.population_lower, decoded.population_upper,total_h,total_he)
    halft=(decoded.log_temperature_lower if temperature_edge=='lower' else decoded.log_temperature_upper)
    point_pop=m._I(halfpop)
    point_logt=m._I(halft)
    T=float(base.forcing.duration_seconds(0))
    t0=T*PARENT_TICK/TOTAL_TICKS;t1=T*(PARENT_TICK+1)/TOTAL_TICKS;tm=t0+(t1-t0)/2
    kw={'model':m.rim.ReducedIntervalModel.from_repo(repo),'base':base,
        'parent_pop':point_pop,'parent_logt':point_logt,
        't0':t0,'t1':t1,'total_h':total_h,'total_he':total_he}
    phases=[]
    for name in ['full','half1','half2']:
        if name=='half1':kw['t1']=tm
        if name=='half2':
            kw.update(parent_pop=phases[-1][1].population,
                      parent_logt=phases[-1][1].log_temperature,t0=tm,t1=t1)
        result=m.run_step(**kw)
        phases.append((name,result))
        if not result.certified:
            out.mkdir(parents=True,exist_ok=True)
            record={'status':'POINT_PARENT_NONLINEAR_MAP_UNCERTIFIED','failed_phase':name,
                    'classification':result.classification,'diagnostics':result.diagnostics,
                    'source':src,'lane':lane,'temperature_edge':temperature_edge,'central_DAG':'28/88','canonical_delta':0}
            (out/'RESULT.json').write_text(json.dumps(record,indent=2,sort_keys=True,default=str)+'\n')
            return record
    full=phases[0][1];last=phases[-1][1]
    A=coordinates(m,full.population,full.log_temperature,total_h,total_he)
    B=coordinates(m,last.population,last.log_temperature,total_h,total_he)
    summary={}
    for k in A:
        dl,dh,dmin,dmax=interval_difference(A[k].lo,A[k].hi,B[k].lo,B[k].hi)
        summary[k]={'max_independent_output_box_upper':float(np.max(dmax)),
                    'max_strict_difference_lower':float(np.max(dmin)),
                    'nodes_upper_below_gate':int(np.count_nonzero(dmax<GATE)),
                    'max_full_box_width':float(np.max(A[k].hi-A[k].lo)),
                    'max_twohalf_box_width':float(np.max(B[k].hi-B[k].lo))}
    out.mkdir(parents=True,exist_ok=True)
    csv_path=out/('REAL_26EVENT_PARENT_TEDGE_'+temperature_edge+'_'+lane+'_46080.csv.gz')
    import gzip
    with csv_path.open('wb') as binary, gzip.GzipFile(filename='',mode='wb',fileobj=binary,mtime=0,compresslevel=9) as compressed, io.TextIOWrapper(compressed,encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['node','parent_x_HII','parent_x_HeII','parent_x_HeIII','parent_T_K',
            *[k+'_D_lo' for k in A],*[k+'_D_hi' for k in A],*[k+'_D_abs_upper' for k in A]])
        ds={k:interval_difference(A[k].lo,A[k].hi,B[k].lo,B[k].hi) for k in A}
        for i in range(NODES):
            w.writerow([i,format(halfpop[i,1]/total_h[i],'.17g'),
              format(halfpop[i,3]/total_he[i],'.17g'),
              format(halfpop[i,4]/total_he[i],'.17g'),format(math.exp(halft[i]),'.17g'),
              *[format(ds[k][0][i],'.17g') for k in A],
              *[format(ds[k][1][i],'.17g') for k in A],
              *[format(ds[k][3][i],'.17g') for k in A]])
    record={'status':'SOURCE_AUTHENTIC_PARENT_TEDGE_NONLINEAR_MAP_CERTIFIED',
      'parent_temperature_edge':temperature_edge,
      'parent_temperature_uncertainty_log_width_max':float(np.max(decoded.log_temperature_upper-decoded.log_temperature_lower)),
      'original_binding_thresholds_eV':[float(m.rim.CHI_H_EV),float(m.rim.CHI_HEI_EV),float(m.rim.CHI_HEII_EV)],
      'interpretation':'ONE_ELEMENT_CONSERVING_COMPOSITION_POINT_PLUS_ONE_TEMPERATURE_EDGE_FROM_PARENT_BOX_NOT_FULL_PARENT_JOINT_ENCLOSURE',
      'source':src,'source_kernel_sha256':kernel_hash,'lane':lane,'nodes':NODES,
      'original_FROZEN_1TICK_cross_box_error':OBSERVED_FROZEN_ONE_TICK,
      'frozen_local_error_threshold':GATE,'time_seconds':{'t0':t0,'mid':tm,'t1':t1},
      'mapping':'Original 26-event MPRK22(1) plus Alexander SDIRK2 preserved without modifications',
      'summary':summary,'csv':csv_path.name,'csv_sha256':sha256(csv_path),
      'central_DAG':'28/88','working_DAG':'33/88','canonical_delta':0,
      'original_full_parent_interval': 'BLOCKED_MINIMUM_STEP_NOT_OVERRIDDEN',
      'distinct_author':'NOT_RUN'}
    (out/'RESULT.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    return record




def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--lane',choices=LANES,required=True)
    ap.add_argument('--temperature-edge',choices=('lower','upper'),required=True)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()
    r=run(z.repo.resolve(),z.lane,z.output,z.temperature_edge)
    print(json.dumps({'lane':z.lane,'temperature_edge':z.temperature_edge,'status':r['status'],
                      'summary':r.get('summary',{}),'csv_sha256':r.get('csv_sha256'),
                      'canonical_delta':0},sort_keys=True))
    if r['status']!='SOURCE_AUTHENTIC_PARENT_TEDGE_NONLINEAR_MAP_CERTIFIED':raise SystemExit(3)
if __name__=='__main__':main()