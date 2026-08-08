#!/usr/bin/env python3
"""Run the locked four-corner branch propagation preflight."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Mapping

import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parent
REPO=STAGE.parents[1]
R2A=REPO/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/analysis'
DATA=STAGE/'data'
LOCAL_ERROR_GATE=2.0e-4
UNCERTAINTY_GATE=2.0e-3
LANES=(
    'LOCAL_NEUTRAL_HAZARD_PRIMARY',
    'RECOMBINATION_WEIGHTED_AUDITOR',
    'SCRIPT_SELF_SHIELDING_AUDITOR',
)


def _load(name: str,path: Path):
    if name in sys.modules:return sys.modules[name]
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ImportError(path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module


policy_mod=_load('r2b_r2a_r1a_run_policy',HERE/'uncertainty_policy.py')
trial_mod=_load('r2b_r2a_r1a_run_trial',HERE/'uncertainty_trial.py')
picard=_load('r2b_r2a_r1a_run_picard',R2A/'globalized_picard.py')


def classify_enclosure(*,widths: Mapping[str,float],all_numerical_gates_pass: bool,
                       continuous_parameter_certified: bool) -> dict[str,Any]:
    normalized={name:float(widths[name]) for name in ('x_HII','x_HeII','x_HeIII','log_T')}
    if not all_numerical_gates_pass:
        classification='HARD_GATE_FAILURE';authorized=False
    elif any((not math.isfinite(value)) or value>UNCERTAINTY_GATE for value in normalized.values()):
        classification='SOURCE_EXTENSION_CALIBRATION_REQUIRED_WIDE_ENCLOSURE';authorized=False
    elif not continuous_parameter_certified:
        classification='CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED';authorized=False
    else:
        classification='UNCERTAINTY_QUALIFIED_FIRST_INTERVAL_AUTHORIZED';authorized=True
    return {
        'classification':classification,
        'production_authorized':authorized,
        'widths':normalized,
        'uncertainty_gate':UNCERTAINTY_GATE,
        'continuous_parameter_certified':bool(continuous_parameter_certified),
    }


def state_observables(state) -> dict[str,np.ndarray]:
    values=np.asarray(state.values,dtype=np.float64)
    nh=values[0]+values[1]
    nhe=values[2]+values[3]+values[4]
    return {
        'x_HII':np.ascontiguousarray(values[1]/nh),
        'x_HeII':np.ascontiguousarray(values[3]/nhe),
        'x_HeIII':np.ascontiguousarray(values[4]/nhe),
        'log_T':np.ascontiguousarray(np.log(state.temperature_K)),
    }


def state_sha256(state) -> str:
    digest=hashlib.sha256()
    digest.update(np.ascontiguousarray(state.values,dtype='<f8').tobytes())
    digest.update(np.ascontiguousarray(state.temperature_K,dtype='<f8').tobytes())
    return digest.hexdigest()


def _gate_trial(result) -> bool:
    return bool(
        result.converged
        and result.hydrogen_residual<=1e-11
        and result.helium_residual<=1e-11
        and result.owner_residual<=1e-11
        and result.photon_residual<=1e-8
        and result.thermal_residual<=1e-10
        and result.pds_reconstruction_residual<=1e-11
        and result.minimum_species>0.0
        and float(result.certificate.get('max_augmented_energy_residual',math.inf))<=1e-10
        and int(result.certificate.get('branch_domain_failure_count',1))==0
        and int(result.certificate.get('legacy_rhs_calls',1))==0
    )


def run_policy(*,base_solver,lane: str,policy) -> tuple[dict[str,Any],Any|None]:
    solver=trial_mod.UncertaintySecondOrderTrial(
        base=base_solver,lane=lane,v_policy=policy.v_policy,f_value=policy.f_value)
    parent=base_solver.inputs.state0.mutable_copy()
    duration=base_solver.forcing.duration_seconds(0)
    t0=0.0;t1=duration/2048.0;mid=0.5*(t0+t1)
    full=solver.solve(state=parent.mutable_copy(),t0=t0,t1=t1,partition=2048,trial_kind='FULL')
    half1=solver.solve(state=parent.mutable_copy(),t0=t0,t1=mid,partition=4096,trial_kind='FIRST_HALF')
    half2=(solver.solve(state=half1.state.mutable_copy(),t0=mid,t1=t1,partition=4096,trial_kind='SECOND_HALF')
           if half1.converged and half1.state is not None else None)
    converged=full.converged and half1.converged and half2 is not None and half2.converged
    local_error=(picard.state_residual(full.state,half2.state) if converged else math.inf)
    trials=[full,half1]+([] if half2 is None else [half2])
    hard=bool(converged and local_error<LOCAL_ERROR_GATE and all(_gate_trial(item) for item in trials))
    endpoint=None if half2 is None else half2.state
    row={
        'lane':lane,'policy_id':policy.policy_id,'v_policy':policy.v_policy,
        'f_value':float(policy.f_value),'load_bearing':bool(policy.load_bearing),
        'full_converged':bool(full.converged),'first_half_converged':bool(half1.converged),
        'second_half_converged':bool(half2 is not None and half2.converged),
        'local_error':float(local_error),'local_error_gate':LOCAL_ERROR_GATE,'hard_gates_pass':hard,
        'max_H_residual':float(max(item.hydrogen_residual for item in trials)),
        'max_He_residual':float(max(item.helium_residual for item in trials)),
        'max_owner_residual':float(max(item.owner_residual for item in trials)),
        'max_photon_residual':float(max(item.photon_residual for item in trials)),
        'max_thermal_residual':float(max(item.thermal_residual for item in trials)),
        'max_PDS_residual':float(max(item.pds_reconstruction_residual for item in trials)),
        'max_OTS_energy_residual':float(max(float(item.certificate.get('max_augmented_energy_residual',math.inf)) for item in trials)),
        'minimum_species':float(min(item.minimum_species for item in trials)),
        'elapsed_s':float(sum(item.elapsed_s for item in trials)),
        'endpoint_sha256':None if endpoint is None else state_sha256(endpoint),
        'failure_classifications':[str(item.certificate.get('classification')) for item in trials if not item.converged],
    }
    return row,endpoint


CSV_FIELDS=(
    'lane','policy_id','v_policy','f_value','load_bearing','full_converged',
    'first_half_converged','second_half_converged','local_error','local_error_gate',
    'hard_gates_pass','max_H_residual','max_He_residual','max_owner_residual',
    'max_photon_residual','max_thermal_residual','max_PDS_residual',
    'max_OTS_energy_residual','minimum_species','elapsed_s','endpoint_sha256',
    'failure_classifications',
)


def _write_csv(path: Path,rows: list[dict[str,Any]]) -> None:
    with path.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=CSV_FIELDS);writer.writeheader()
        for row in rows:
            out=dict(row);out['failure_classifications']=json.dumps(out['failure_classifications'])
            writer.writerow(out)


def run_all() -> dict[str,Any]:
    DATA.mkdir(parents=True,exist_ok=True)
    rows=[];strict_envelopes={};lane_widths={};endpoint_hashes={}
    started=time.perf_counter()
    for lane in LANES:
        base_solver=trial_mod.fast.base.physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane)
        strict_states=[]
        for policy in policy_mod.policy_registry():
            row,state=run_policy(base_solver=base_solver,lane=lane,policy=policy)
            rows.append(row);endpoint_hashes[f'{lane}/{policy.policy_id}']=row['endpoint_sha256']
            if policy.load_bearing and state is not None and row['hard_gates_pass']:
                strict_states.append(state_observables(state))
        if len(strict_states)==4:
            lane_arrays={}
            widths={}
            for field in ('x_HII','x_HeII','x_HeIII','log_T'):
                stack=np.stack([item[field] for item in strict_states],axis=0)
                lower=np.min(stack,axis=0);upper=np.max(stack,axis=0)
                lane_arrays[f'{field}_lower']=lower;lane_arrays[f'{field}_upper']=upper
                widths[field]=float(np.max(upper-lower))
            strict_envelopes[lane]=lane_arrays;lane_widths[lane]=widths
        else:
            lane_widths[lane]={field:math.inf for field in ('x_HII','x_HeII','x_HeIII','log_T')}
    _write_csv(DATA/'policy_trial_summary.csv',rows)
    npz={}
    for lane,lane_arrays in strict_envelopes.items():
        token=lane.lower()
        for name,array in lane_arrays.items():npz[f'{token}__{name}']=array
    np.savez_compressed(DATA/'strict_corner_envelopes.npz',**npz)
    (DATA/'endpoint_hashes.json').write_text(json.dumps(endpoint_hashes,indent=2,sort_keys=True)+'\n')
    all_numerical=all(bool(row['hard_gates_pass']) for row in rows)
    overall={field:max(lane_widths[lane][field] for lane in LANES) for field in ('x_HII','x_HeII','x_HeIII','log_T')}
    decision=classify_enclosure(widths=overall,all_numerical_gates_pass=all_numerical,
                                continuous_parameter_certified=False)
    verdict={
        'HARD_GATE_FAILURE':'DURABLE_FAIL_CLOSED_R2_R1A_HARD_GATE_FAILURE',
        'SOURCE_EXTENSION_CALIBRATION_REQUIRED_WIDE_ENCLOSURE':'DURABLE_FAIL_CLOSED_R2_R1A_BRANCH_UNCERTAINTY_ENCLOSURE_TOO_WIDE_SOURCE_EXTENSION_REQUIRED',
        'CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED':'DURABLE_FAIL_CLOSED_R2_R1A_CORNERS_NARROW_BUT_CONTINUOUS_PARAMETER_ENCLOSURE_UNCERTIFIED',
        'UNCERTAINTY_QUALIFIED_FIRST_INTERVAL_AUTHORIZED':'DURABLE_PASS_R2_R1A_UNCERTAINTY_QUALIFIED_FIRST_INTERVAL_AUTHORIZED',
    }[decision['classification']]
    results={
        'stage':'P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-FOUR-CORNER-BRANCH-AND-UNRESOLVED-OTS-ENERGY-PROPAGATION-PREFLIGHT',
        'verdict':verdict,'completed':True,'production_history_authorized':bool(decision['production_authorized']),
        'production_node_chemistry_authorized':False,'R2C_R2_authorized':False,'B2C2B_authorized':False,
        'state_realization_count':len(rows),'load_bearing_realization_count':sum(bool(r['load_bearing']) for r in rows),
        'adapter_auditor_realization_count':sum(not bool(r['load_bearing']) for r in rows),
        'all_numerical_gates_pass':all_numerical,'lane_widths':lane_widths,'overall_widths':overall,
        'decision':decision,'local_error_gate':LOCAL_ERROR_GATE,'uncertainty_gate':UNCERTAINTY_GATE,
        'continuous_parameter_certificate':'NOT_AVAILABLE_NONLINEAR_MONOTONICITY_NOT_PROVED',
        'elapsed_s':float(time.perf_counter()-started),
        'max_metrics':{
            'local_error':float(max(r['local_error'] for r in rows)),
            'H_residual':float(max(r['max_H_residual'] for r in rows)),
            'He_residual':float(max(r['max_He_residual'] for r in rows)),
            'owner_residual':float(max(r['max_owner_residual'] for r in rows)),
            'photon_residual':float(max(r['max_photon_residual'] for r in rows)),
            'thermal_residual':float(max(r['max_thermal_residual'] for r in rows)),
            'PDS_residual':float(max(r['max_PDS_residual'] for r in rows)),
            'OTS_energy_residual':float(max(r['max_OTS_energy_residual'] for r in rows)),
            'minimum_species':float(min(r['minimum_species'] for r in rows)),
        },
    }
    (STAGE/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    return results


if __name__=='__main__':
    print(json.dumps(run_all(),indent=2,sort_keys=True))
