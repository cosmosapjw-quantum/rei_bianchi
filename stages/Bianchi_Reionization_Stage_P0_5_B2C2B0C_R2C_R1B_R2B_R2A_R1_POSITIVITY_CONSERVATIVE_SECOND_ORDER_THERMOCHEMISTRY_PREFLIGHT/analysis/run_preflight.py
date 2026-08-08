#!/usr/bin/env python3
"""Run the sealed R2B-R2A-R1 second-order first-segment preflight."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import pandas as pd

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parents[1]
R2A=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK'
LANES=(
    'LOCAL_NEUTRAL_HAZARD_PRIMARY',
    'RECOMBINATION_WEIGHTED_AUDITOR',
    'SCRIPT_SELF_SHIELDING_AUDITOR',
)
PARTITIONS=(512,1024,2048)
LOCAL_ERROR_TOL=2.0e-4


def _load(name: str,path: Path):
    if name in sys.modules: return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise ImportError(path)
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m


def classify(rows: list[dict[str,Any]]) -> dict[str,Any]:
    lane_pass={}
    for lane in LANES:
        candidates=[r for r in rows if r['lane']==lane and int(r['partition']) in (1024,2048)]
        lane_pass[lane]=any(
            bool(r['candidate_converged']) and bool(r['all_gates_pass'])
            and r['local_error'] is not None and float(r['local_error'])<LOCAL_ERROR_TOL
            for r in candidates
        )
    return {'lane_pass':lane_pass,'science_pass':all(lane_pass.values())}


def block_errors(full,half) -> dict[str,float]:
    a=full.values; b=half.values
    nh=a[0]+a[1]; nhe=a[2]+a[3]+a[4]
    return {
        'x_HII':float(np.max(np.abs(a[1]/nh-b[1]/nh))),
        'x_HeII':float(np.max(np.abs(a[3]/nhe-b[3]/nhe))),
        'x_HeIII':float(np.max(np.abs(a[4]/nhe-b[4]/nhe))),
        'log_T':float(np.max(np.abs(np.log(full.temperature_K)-np.log(half.temperature_K)))),
    }


def trial_gates(*trials) -> tuple[bool,dict[str,float]]:
    metrics={
        'max_H_residual':max(t.hydrogen_residual for t in trials),
        'max_He_residual':max(t.helium_residual for t in trials),
        'max_owner_residual':max(t.owner_residual for t in trials),
        'max_photon_residual':max(t.photon_residual for t in trials),
        'max_thermal_residual':max(t.thermal_residual for t in trials),
        'max_PDS_residual':max(t.pds_reconstruction_residual for t in trials),
        'minimum_species':min(t.minimum_species for t in trials),
    }
    passed=(all(t.converged for t in trials) and metrics['max_H_residual']<=1e-11
            and metrics['max_He_residual']<=1e-11 and metrics['max_owner_residual']<=1e-11
            and metrics['max_photon_residual']<=1e-8 and metrics['max_thermal_residual']<=1e-10
            and metrics['max_PDS_residual']<=1e-11 and metrics['minimum_species']>0.0)
    return passed,metrics


def candidate_rows() -> list[dict[str,Any]]:
    trialmod=_load('r2b_r2a_r1_preflight_trial',STAGE/'analysis/second_order_trial.py')
    rows=[]
    for lane in LANES:
        solver=trialmod.SecondOrderPhysicalTrial.from_repo(repo_root=REPO,lane=lane)
        parent=solver.inputs.state0.mutable_copy(); duration=solver.forcing.duration_seconds(0)
        parent_bytes=(parent.values.tobytes(),parent.temperature_K.tobytes())
        for p in PARTITIONS:
            a=0.0; b=duration/p; mid=0.5*b
            started=time.perf_counter()
            full=solver.solve(state=parent,t0=a,t1=b,partition=p,trial_kind='FULL')
            half1=solver.solve(state=parent,t0=a,t1=mid,partition=2*p,trial_kind='FIRST_HALF')
            half2=(solver.solve(state=half1.state,t0=mid,t1=b,partition=2*p,trial_kind='SECOND_HALF')
                   if half1.converged else half1)
            elapsed=time.perf_counter()-started
            converged=full.converged and half1.converged and half2.converged
            errors=block_errors(full.state,half2.state) if converged else {k:None for k in ('x_HII','x_HeII','x_HeIII','log_T')}
            local=max(v for v in errors.values() if v is not None) if converged else None
            gates,metrics=trial_gates(full,half1,half2)
            rows.append({
                'lane':lane,'partition':p,'candidate_converged':converged,
                'local_error':local,'passes_local_error':bool(local is not None and local<LOCAL_ERROR_TOL),
                'all_gates_pass':gates,'elapsed_s':elapsed,
                **{f'error_{k}':v for k,v in errors.items()},**metrics,
                'full_certificate':json.dumps(full.certificate,sort_keys=True),
                'half1_certificate':json.dumps(half1.certificate,sort_keys=True),
                'half2_certificate':json.dumps(half2.certificate,sort_keys=True),
            })
            if parent_bytes!=(parent.values.tobytes(),parent.temperature_K.tobytes()):
                raise RuntimeError('candidate trials mutated the parent state')
    return rows


def inherited_be_rows() -> list[dict[str,Any]]:
    source=json.loads((R2A/'results.json').read_text())
    rows=[]
    for lane in LANES:
        r=source['lanes'][lane]
        rows.append({'lane':lane,'partition':1024,'method':'BACKWARD_EULER_INHERITED',
                     'local_error':r['terminal_attempt']['local_error'],
                     'elapsed_context_s':r['elapsed_s'],'load_bearing':False})
    for r in source['extension_auditor']['rows']:
        rows.append({'lane':'LOCAL_NEUTRAL_HAZARD_PRIMARY','partition':int(r['partition']),
                     'method':'BACKWARD_EULER_INHERITED_EXTENSION','local_error':r['local_error'],
                     'elapsed_context_s':None,'load_bearing':False})
    return rows


def main() -> int:
    parser=argparse.ArgumentParser(); parser.parse_args()
    rows=candidate_rows(); disposition=classify(rows)
    frame=pd.DataFrame(rows); (STAGE/'data').mkdir(exist_ok=True)
    frame.to_csv(STAGE/'data/preflight_results.csv',index=False)
    be=inherited_be_rows(); pd.DataFrame(be).to_csv(STAGE/'data/backward_euler_reference.csv',index=False)
    result={
        'classification':'R2B_R2A_R1_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT',
        'stage':'P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R1-POSITIVITY-CONSERVATIVE-SECOND-ORDER-THERMOCHEMISTRY-PREFLIGHT',
        'candidate_method':'NONAUTONOMOUS_MPRK22_ALPHA1_PLUS_POSITIVE_IMPLICIT_TRAPEZOID_THERMAL',
        'partitions':list(PARTITIONS),'rows':rows,'backward_euler_reference':be,**disposition,
        'production_history_integrated':False,
    }
    (STAGE/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'science_pass':disposition['science_pass'],'lane_pass':disposition['lane_pass'],
                      'local_errors':{f"{r['lane']}:{r['partition']}":r['local_error'] for r in rows}},indent=2))
    return 0

if __name__=='__main__': raise SystemExit(main())
