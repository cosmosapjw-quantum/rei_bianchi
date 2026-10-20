#!/usr/bin/env python3
"""Fresh recovery R1 direct-time path audit on original or Rust birth CSVs."""
import argparse
import csv
import datetime
import json
import math
from pathlib import Path
import time
import numpy as np
from independent_birth_reference import Fixture,PathGrid,SPECIES,EDGES,EV_J,VERSION,sha,first_step,aggregate,reduce_template,write_template_csv


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--births',type=Path);p.add_argument('--case',default='SIGNED_MINUS')
    p.add_argument('--event',type=int,default=64);p.add_argument('--opacity',type=int,default=16)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    f=Fixture(a.parent,a.case);original=a.births is None
    path=f.files['BIRTHS'] if original else a.births
    if original: births=first_step(path)
    else:
        with path.open(newline='') as stream:births=list(csv.DictReader(stream))
    time_key='actual_birth_time_s' if original else 'birth_time_s'
    weight_key='born_count_com3' if original else 'born_com3'
    label_key='template_id' if original else 'template'
    q=np.array([float(r[time_key])/f.dt for r in births]);born=np.array([float(r[weight_key]) for r in births])
    labels=np.array([int(r[label_key]) for r in births])
    K=np.array([[float(r['K'+str(i)+('_ev_scale' if original else '')]) for i in (1,2,3)] for r in births])
    templates={int(r['template_id']):r for r in f.templates}
    if not original:
        for r in births:
            tid=int(r['template']);en=float(r['birth_energy_ev'])
            if tid not in templates or float(templates[tid]['energy_ev'])!=en:
                templates[tid]={'template_id':str(tid),'energy_ev':str(en)}
    if np.any(~np.isfinite(born)) or np.any(born<0):raise ValueError('invalid emitted weights')
    e0=np.array([float(templates[t]['energy_ev']) for t in labels])
    aend=f.geometry.at(np.ones(len(q)))[0]
    eend=np.sqrt(np.sum((K/aend)**2,axis=-1))
    crossings=int(np.count_nonzero((EDGES[None,:]<e0[:,None])&(EDGES[None,:]>eend[:,None])))
    if crossings:raise ValueError('use split edge oracle for crossing births')
    batches={}
    for lo in range(0,len(q),256):
        hi=min(len(q),lo+256)
        result=PathGrid(f,q[lo:hi],a.event,a.opacity).evaluate(K[lo:hi])
        for key,value in result.items():batches.setdefault(key,[]).append(value)
    all_path={k:np.concatenate(v,axis=0) for k,v in batches.items()}
    rows=[]
    for label in sorted(set(labels)):
        mask=labels==label
        rows.append(reduce_template(f,templates[label],q[mask],born[mask],{k:v[mask] for k,v in all_path.items()}))
    result=aggregate(rows)
    totals={k:result[k] for k in ('survival','age','age2','energy','q2','work','mean_age_s','mean_age2_s2','energy_weighted_q2')}
    totals.update({'absorbed':result['absorbed_energy'],'chemical':math.fsum(result['binding'].values()),
                  'heat':math.fsum(result['heat'].values()),**result['events']})
    maxima={'max_number_residual_per_birth':float(np.max(np.abs(all_path['P']+np.sum(all_path['events'],axis=1)-1))),
      'max_energy_residual_over_birth_energy':float(np.max(np.abs(all_path['P']*all_path['end_energy_ev']*EV_J+
            all_path['absorbed_energy']-e0*EV_J-all_path['work'])/(e0*EV_J)))}
    native_comparison=None
    if original:
        accepted=math.fsum(float(r['accepted_count_com3']) for r in births)
        native_comparison={'actual_original_survived_sum':accepted,'independent_matched_survival':result['survival'],
          'native_minus_matched_relative':(accepted-result['survival'])/result['survival']}
    receipt={'version':VERSION,'status':'COMPLETED_FRESH_RECOVERY_EXECUTION','historical_pass_inherited':False,
      'scope':'Exactly represented emitted birth/Killing measure; direct-time path only; no new gas history',
      'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case':a.case,
      'birth_rows':len(births),'templates':len(rows),'threshold_crossings':crossings,
      'controls':{'event':a.event,'opacity':a.opacity,'chunk_size':256},'wall_s':time.perf_counter()-start,
      'input':{'path':str(path),'sha256':sha(path)},'source_sha256':sha(__file__),
      'integrator_source_sha256':sha(Path(__file__).with_name('independent_birth_reference.py')),
      'totals':totals,'result':result,'maxima':maxima,'original_comparison':native_comparison}
    write_template_csv(a.output/'MATCHED_TEMPLATES.csv',rows)
    out=a.output/'MATCHED_PATH_REFERENCE.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'wall_s':receipt['wall_s'],'totals':totals,'original_comparison':native_comparison}))


if __name__=='__main__':main()
