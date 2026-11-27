#!/usr/bin/env python3
"""Held-out timing-trace simulation; never reports modeled time as measured speedup."""
from pathlib import Path
import argparse,copy,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from wu088_hh.scheduler import predict_costs,order_tasks

def wave_time(order,costs,workers=12):
    return sum(max(costs[k] for k in order[i:i+workers]) for i in range(0,len(order),workers))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    profile=json.loads((ROOT/'data/pair_cost_profile.json').read_text());traces={(s['z'],s['n']):{(i,j):c for i,j,c in s['costs']} for s in profile['states']}
    rows=[]
    train=copy.deepcopy(profile);train['states']=[s for s in train['states'] if s['n']==160]
    for z in [0,16,32,48,64]:
        actual=traces[z,192];pred,meta=predict_costs(train,n=192,z=z)
        ordered=[tuple(t) for t in order_tasks(sorted(actual),pred)]
        old=wave_time(sorted(actual),actual);new=wave_time(ordered,actual)
        rows.append(dict(z=z,training_basis=160,heldout_basis=192,baseline_trace_wave_s=old,
                         heldout_cost_sorted_wave_s=new,modeled_compute_speedup=old/new,
                         old_compute_slot_utilization=sum(actual.values())/(12*old),
                         modeled_new_utilization=sum(actual.values())/(12*new)))
    geometry=[]
    for z in [16,32,48]:
        p=copy.deepcopy(profile);p['states']=[s for s in p['states'] if s['z']!=z]
        actual=traces[z,192];pred,_=predict_costs(p,n=192,z=z)
        order=order_tasks(sorted(actual),pred)
        geometry.append(dict(z=z,heldout_geometry=True,modeled_speedup=wave_time(sorted(actual),actual)/wave_time(order,actual)))
    result=dict(evidence_type='HELD_OUT_TRACE_SIMULATION_NOT_NEW_WALL_BENCHMARK',basis_holdout=rows,
                geometry_holdout=geometry,backup_barrier_changed=False,max_new_pairs=12,
                assumptions=['Archived pair durations held constant under changed ordering.',
                'Network, initialization, clock-frequency, SMT and cache interactions are not predicted.'])
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
