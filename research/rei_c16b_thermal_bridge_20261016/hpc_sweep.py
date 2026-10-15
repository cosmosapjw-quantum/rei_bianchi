"""Deterministic independent manufactured-rate state sweep for NCP.

Multi-process orchestration, not host-native subagents and not production EoR.
Output is sorted by case ID independent of worker count. Timing is separate.
"""
import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from time import perf_counter
import source_aware as s
from src.thermal_bridge import (FrozenCoefficients,ThermalReservoir,
                                evolve_coupled_photo_thermal)


def case(index, substeps):
    # Fixed inputs/outputs per index. Keep rates explicitly manufactured.
    mu=[-.87,-.31,.22,.91]
    ph=tuple(s.Node(q,mu[j],.10+.008*((index+j*7)%9))
             for j,q in enumerate([17.,33.,68.,120.]))
    hii=.05+.005*(index%32)
    heii=.005+.001*((index//3)%19)
    heiii=.001+.0005*((index//11)%11)
    gas=s.Gas(1-hii,hii,.08-heii-heiii,heii,heiii)
    initial=s.State(ph,gas)
    scale=0.1+0.15*((index*13)%21)
    rates=FrozenCoefficients(tuple(scale*v for v in [9e-10,7e-10,6e-10]),
                            tuple(scale*v for v in [3e-9,2e-9,1e-9]),
                            (.15,.25,.35))
    before=ThermalReservoir(170.)
    end,res,ledger=evolve_coupled_photo_thermal(initial,before,4e10,1e-3,
                                                 rates,reaction_substeps=substeps)
    return {'index':index,'photon_n_final':[p.n_per_h for p in end.photons],
            'gas_final':list(end.gas.__dict__.values()),
            'thermal_ev_per_h':res.thermal_ev_per_h,'escape_ev_per_h':res.escape_ev_per_h,
            'photo_events':list(ledger.photo_events),'RR_events':list(ledger.rr_events),
            'CI_events':list(ledger.ci_events),
            'energy_abs_residual':abs(ledger.total_energy_residual_ev_per_h),
            'photon_number_abs_residual':abs(ledger.photon_number_residual),
            'h_abs_residual':abs(ledger.h_nuclei_residual),
            'he_abs_residual':abs(ledger.he_nuclei_residual),
            'electron_abs_residual':abs(ledger.electron_charge_residual)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cases',type=int,default=32)
    p.add_argument('--jobs',type=int,default=1)
    p.add_argument('--substeps',type=int,default=16)
    p.add_argument('--out',type=Path,default=Path('evidence/hpc_small'))
    a=p.parse_args()
    if a.cases<1 or a.cases>100000 or a.jobs<1 or a.jobs>64 or a.substeps<1 or a.substeps>2048:
        raise ValueError('bounded sweep limits')
    a.out.mkdir(parents=True,exist_ok=True)
    t=perf_counter()
    if a.jobs==1:
        rows=[case(i,a.substeps) for i in range(a.cases)]
    else:
        with ProcessPoolExecutor(max_workers=a.jobs) as pool:
            rows=list(pool.map(case,range(a.cases),[a.substeps]*a.cases,
                               chunksize=max(1,a.cases//(a.jobs*8))))
    elapsed=perf_counter()-t
    assert all(row['index']==i for i,row in enumerate(rows))
    assert max(row['energy_abs_residual'] for row in rows)<5e-10
    assert max(row['photon_number_abs_residual'] for row in rows)<5e-12
    assert max(row['electron_abs_residual'] for row in rows)<5e-12
    output={'schema':'rei.synthetic_RR_CI_parallel_sweep.v1','cases':a.cases,
            'substeps':a.substeps,'source_model':'MANUFACTURED_RATE_ONLY',
            'rows':rows}
    (a.out/'results.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    (a.out/'timing.json').write_text(json.dumps({'jobs':a.jobs,'wall_seconds':elapsed,
                  'host_cpu_count':os.cpu_count()},indent=2)+'\n')
    print('SWEEP_PASS',a.cases,'JOBS',a.jobs,'WALL',round(elapsed,6))
if __name__=='__main__':
    main()
