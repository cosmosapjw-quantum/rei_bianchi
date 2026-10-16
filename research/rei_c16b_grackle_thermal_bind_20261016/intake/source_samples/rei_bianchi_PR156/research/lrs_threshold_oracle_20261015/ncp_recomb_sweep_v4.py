"""Deterministic bounded NCP parameter sweep for the source-free V4 oracle.

Does not modify production repos, services or other NCP runs.
Recombination coefficients are *dimensionless toy inputs*, not physical
atomic rate tables. Medium-resource executable with deterministic output.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from dynamic_chemistry import Gas
from lrs_threshold_oracle import Ray, GAUSS8
from recomb_thermal import PhotoRecombRates,evolve_thermal

GAS=Gas(.37,.03,.085,.012,.003)
# Bound to 12 workers by default to leave CPU headroom on shared 64-vCPU NCP.
SMOKE_LIMIT=12


def make_grid():
    cases=[]
    for shear_index in range(17):
        signed=-.08+.01*shear_index
        for p in (0.,.5,2.,8.):
            for r in (0.,.1,.32,1.28):
                for T0 in (3000.,8000.,15000.):
                    cases.append((len(cases),signed,p,r,T0))
    return cases


def rays(s):
    return tuple(Ray(e,float(mu),.5*float(w)*count,s)
                 for e,count in ((110.,.12),(72.,.08),(43.,.06))
                 for mu,w in GAUSS8)


def work(case):
    idx,s,p,krec,T0=case
    rr=rays(s)
    rates=PhotoRecombRates(p,(krec,.47*krec,.375*krec),10000.,(.7,.7,.7))
    coarse=evolve_thermal(rr,GAS,.65,rates=rates,
                          temperature_initial_K=T0,max_step=.01)
    fine=evolve_thermal(rr,GAS,.65,rates=rates,
                        temperature_initial_K=T0,max_step=.005)
    for result in (coarse,fine):
        if abs(result.energy_residual_ev)>1e-9 or abs(result.photon_reaction_residual)>1e-10 or abs(result.electron_reaction_residual)>1e-10:
            raise AssertionError(f'case {idx} conservation failure')
        if result.final_temperature_K<=0 or min(result.final.as_tuple())<0:
            raise AssertionError(f'case {idx} positivity failure')
    return {
      'case':idx,'s_over_h':s,'photo_per_mb':p,
      'recomb_HII_at_tref':krec,'initial_T_K':T0,
      'steps_coarse':coarse.steps,'steps_fine':fine.steps,
      'final_T_K':fine.final_temperature_K,'ne':fine.final.electrons,
      'HII_frac':fine.final.HII/GAS.hydrogen,
      'HeII_frac':fine.final.HeII/GAS.helium,
      'HeIII_frac':fine.final.HeIII/GAS.helium,
      'photon_survival':sum(fine.photons_final),
      'recomb_energy_escaped_ev':fine.escaped_recomb_energy_ev,
      'T_step_discrepancy_K':abs(fine.final_temperature_K-coarse.final_temperature_K),
      'ne_step_discrepancy':abs(fine.final.electrons-coarse.final.electrons),
      'max_energy_residual_ev':max(abs(coarse.energy_residual_ev),abs(fine.energy_residual_ev)),
      'max_photon_count_residual':max(abs(coarse.photon_reaction_residual),abs(fine.photon_reaction_residual)),
      'max_electron_count_residual':max(abs(coarse.electron_reaction_residual),abs(fine.electron_reaction_residual)),
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workers',type=int,default=12)
    ap.add_argument('--limit',type=int,default=0,help='0 means all 816 cases')
    ap.add_argument('--output',default='evidence/v4_recomb_thermal/ncp_sweep_v4.csv')
    args=ap.parse_args()
    if not 1<=args.workers<=16:
        raise ValueError('worker count must be 1..16')
    if args.limit<0:
        raise ValueError('limit must be nonnegative')
    cases=make_grid()
    if args.limit:
        cases=cases[:args.limit]
    if not cases:
        raise ValueError('no cases')
    start=time.perf_counter()
    if args.workers==1:
        rows=list(map(work,cases))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            # Executor.map preserves order, even if completion order differs.
            rows=list(pool.map(work,cases,chunksize=8))
    rows.sort(key=lambda r:r['case'])
    out=Path(args.output)
    out.parent.mkdir(exist_ok=True,parents=True)
    with out.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    info={
      'status':'NUMERICALLY_EXECUTED_TOY_SWEEP',
      'claims_excluded':['real astrophysical recombination fit','production EoR','native Rust solver'],
      'cases':len(rows),'workers':args.workers,
      'source':'recomb_thermal.py; fixed donor Verner1996 original, prescribed H/H0=1',
      'table_filename':out.name,
      'comparison':'two max-step values .01/.005 are self-consistency diagnostics, not independent ODE error',
      'max_T_step_difference_K':max(r['T_step_discrepancy_K'] for r in rows),
      'max_ne_step_difference':max(r['ne_step_discrepancy'] for r in rows),
      'max_energy_residual_ev':max(r['max_energy_residual_ev'] for r in rows),
      'max_electron_residual':max(r['max_electron_count_residual'] for r in rows),
    }
    out.with_suffix('.summary.json').write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
    print('SWEEP_CASES',len(rows))
    print('WORKERS',args.workers)
    print('RUN_SECONDS',round(time.perf_counter()-start,3))
    print('MAX_ENERGY_RESIDUAL',info['max_energy_residual_ev'])
    print('MAX_T_STEP_DIFFERENCE_K',info['max_T_step_difference_K'])
    print('MAX_NE_STEP_DIFFERENCE',info['max_ne_step_difference'])
    print('OUTPUT_CSV',out)

if __name__=='__main__':main()
