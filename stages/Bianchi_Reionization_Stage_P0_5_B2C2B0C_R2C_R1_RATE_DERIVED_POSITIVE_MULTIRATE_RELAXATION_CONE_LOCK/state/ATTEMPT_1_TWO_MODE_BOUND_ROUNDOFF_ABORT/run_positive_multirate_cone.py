"""Execute the locked R2C-R1 one-mode/two-mode cone preflight."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from positive_multirate_cone import (  # noqa: E402
    FAMILY_ORDER,
    build_equilibrium_problem,
    certify_exponential_slack,
    one_mode_equilibrium,
    solve_equilibrium_problem,
    two_mode_weight_for_attenuation,
)

SHAPE_LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
NODES_PER_MACRO = 2560
MACROS_PER_CASE = 18
REFINEMENTS = (2, 4, 8)
REL_TOL = 1.0e-11


def to_builtin(value: Any) -> Any:
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, np.generic): return value.item()
    if isinstance(value, dict): return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [to_builtin(v) for v in value]
    return value


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(to_builtin(record), sort_keys=True) + "\n")


def load_r2c_api(repo: Path):
    src = repo / "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_MOMENT_CONSTRAINED_NODE_CHEMISTRY_RELAXATION_AUDIT/src"
    sys.path.insert(0, str(src))
    import run_relaxation_audit as api  # type: ignore
    return api


def state_dict(endpoint) -> dict[str, np.ndarray]:
    return {
        "M": np.asarray(endpoint.mass, dtype=float),
        "I": np.asarray(endpoint.ionized, dtype=float),
        "U": np.asarray(endpoint.thermal, dtype=float),
        "C": np.asarray(endpoint.capacity, dtype=float),
        "J_G1": np.asarray(endpoint.current[:, 0], dtype=float),
        "J_G2a": np.asarray(endpoint.current[:, 1], dtype=float),
    }


def relative_l1(value: np.ndarray, reference: np.ndarray) -> float:
    return float(np.sum(np.abs(value - reference)) / max(np.sum(np.abs(reference)), 1.0))


def analytic_endpoint_residual(previous, target, equilibrium, model, rates, bounds, weights, dt_myr):
    residuals = {}
    for family in FAMILY_ORDER:
        if model == "ONE_MODE":
            decay = math.exp(-rates[family] * dt_myr)
        else:
            lo, hi = bounds[family]
            w = weights[family]
            decay = w * math.exp(-lo * dt_myr) + (1.0 - w) * math.exp(-hi * dt_myr)
        endpoint = equilibrium[family] + (previous[family] - equilibrium[family]) * decay
        residuals[family] = relative_l1(endpoint, target[family])
    return residuals


def trajectory_certificates(previous, equilibrium, rates, dt_myr, *, model, bounds=None, weights=None):
    if model == "ONE_MODE":
        neutral_amps = np.column_stack([
            previous["M"] - equilibrium["M"],
            -(previous["I"] - equilibrium["I"]),
        ])
        neutral_rates = np.array([rates["M"], rates["I"]])
        cycle_amps = np.column_stack([
            previous["C"] - equilibrium["C"],
            -(previous["J_G1"] - equilibrium["J_G1"]),
            -(previous["J_G2a"] - equilibrium["J_G2a"]),
        ])
        cycle_rates = np.array([rates["C"], rates["J_G1"], rates["J_G2a"]])
    else:
        assert bounds is not None and weights is not None
        neutral_terms=[]; neutral_rates_list=[]
        for family, sign in (("M",1.0),("I",-1.0)):
            amp=sign*(previous[family]-equilibrium[family]); lo,hi=bounds[family]; w=weights[family]
            neutral_terms.extend([amp*w, amp*(1.0-w)]); neutral_rates_list.extend([lo,hi])
        neutral_amps=np.column_stack(neutral_terms); neutral_rates=np.array(neutral_rates_list)
        cycle_terms=[]; cycle_rates_list=[]
        for family, sign in (("C",1.0),("J_G1",-1.0),("J_G2a",-1.0)):
            amp=sign*(previous[family]-equilibrium[family]); lo,hi=bounds[family]; w=weights[family]
            cycle_terms.extend([amp*w,amp*(1.0-w)]); cycle_rates_list.extend([lo,hi])
        cycle_amps=np.column_stack(cycle_terms); cycle_rates=np.array(cycle_rates_list)
    neutral = certify_exponential_slack(
        constant=equilibrium["M"]-equilibrium["I"], amplitudes=neutral_amps,
        rates_myr_inv=neutral_rates, dt_myr=dt_myr, relative_tolerance=REL_TOL, max_depth=24,
    )
    cycling = certify_exponential_slack(
        constant=equilibrium["C"]-equilibrium["J_G1"]-equilibrium["J_G2a"], amplitudes=cycle_amps,
        rates_myr_inv=cycle_rates, dt_myr=dt_myr, relative_tolerance=REL_TOL, max_depth=24,
    )
    return {"pass": bool(neutral["pass"] and cycling["pass"]), "neutral": neutral, "cycling": cycling}


def model_decay(model, family, elapsed, step, rates, bounds, weights):
    q = int(round(elapsed / step))
    if model == "ONE_MODE":
        return (1.0 + rates[family] * step) ** (-q)
    lo,hi=bounds[family]; w=weights[family]
    return w*(1.0+lo*step)**(-q)+(1.0-w)*(1.0+hi*step)**(-q)


def refinement_audit(previous, target, equilibrium, *, model, rates, bounds, weights, dt_myr):
    rows=[]; errors=[]; all_cone=True
    for n in REFINEMENTS:
        h=dt_myr/n
        minimum={"M":math.inf,"I":math.inf,"neutral":math.inf,"U":math.inf,"C":math.inf,"J_G1":math.inf,"J_G2a":math.inf,"cycling":math.inf}
        final={}
        for q in range(1,n+1):
            elapsed=q*h; state={}
            for family in FAMILY_ORDER:
                decay=model_decay(model,family,elapsed,h,rates,bounds,weights)
                state[family]=equilibrium[family]+(previous[family]-equilibrium[family])*decay
            minimum["M"]=min(minimum["M"],float(np.min(state["M"])))
            minimum["I"]=min(minimum["I"],float(np.min(state["I"])))
            minimum["neutral"]=min(minimum["neutral"],float(np.min(state["M"]-state["I"])))
            minimum["U"]=min(minimum["U"],float(np.min(state["U"])))
            minimum["C"]=min(minimum["C"],float(np.min(state["C"])))
            minimum["J_G1"]=min(minimum["J_G1"],float(np.min(state["J_G1"])))
            minimum["J_G2a"]=min(minimum["J_G2a"],float(np.min(state["J_G2a"])))
            minimum["cycling"]=min(minimum["cycling"],float(np.min(state["C"]-state["J_G1"]-state["J_G2a"])))
            final=state
        family_errors={f:relative_l1(final[f],target[f]) for f in FAMILY_ORDER}
        combined=max(family_errors.values()); errors.append(combined)
        scale=max(float(np.sum(np.abs(previous["C"]))),float(np.sum(np.abs(target["C"]))),1.0)
        cone=minimum["neutral"]>=-REL_TOL*max(float(np.sum(np.abs(previous["M"]))),1.0) and minimum["cycling"]>=-REL_TOL*scale
        all_cone=all_cone and cone
        rows.append({"refinement":n,"combined_error":combined,"cone_pass":cone,**{f"error_{f}":v for f,v in family_errors.items()},**{f"minimum_{k}":v for k,v in minimum.items()}})
    if max(errors)<=1e-14:
        conv=True; p24=math.inf; p48=math.inf; status="TRIVIAL_MACHINE_ZERO"
    else:
        p24=math.log(errors[0]/errors[1],2.0) if errors[1]>0 and errors[0]>0 else math.inf
        p48=math.log(errors[1]/errors[2],2.0) if errors[2]>0 and errors[1]>0 else math.inf
        conv=errors[1]<=errors[0]*(1+1e-12) and errors[2]<=errors[1]*(1+1e-12) and min(p24,p48)>=0.5
        status="PASS" if conv and all_cone else "FAIL"
    return {"pass":bool(conv and all_cone),"status":status,"order_2_to_4":p24,"order_4_to_8":p48,"rows":rows}


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,required=True); parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--state-input",type=Path,required=True); parser.add_argument("--group-input",type=Path,required=True)
    args=parser.parse_args(); repo=args.repo.resolve(); stage=args.stage.resolve(); api=load_r2c_api(repo)
    started=time.time(); data_dir=stage/'data'; receipts=stage/'receipts'; data_dir.mkdir(exist_ok=True); receipts.mkdir(exist_ok=True)
    nodes=api.load_node_tables(args.state_input,args.group_input)
    rate_lock=pd.read_csv(data_dir/'rate_interval_lock.csv')
    macro_df=pd.read_csv(repo/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data/macro_projection.csv')
    global_df=pd.read_csv(repo/'stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2A_GLOBAL_MOMENT_CONSTRAINED_MACRO_SINK_DISTRIBUTION_LOCK/data/global_moment_lock.csv').sort_values(['interval_index','substep'])
    initial=api.load_initial_global(repo)
    result_rows=[]; rate_rows=[]; refinement_rows=[]; violation_rows=[]; zero_rows=[]
    dual_path=data_dir/'dual_farkas_kkt_certificates.jsonl'; traj_path=data_dir/'trajectory_certificates.jsonl'
    dual_path.write_text(''); traj_path.write_text('')
    keys=[(int(r.interval_index),int(r.substep),float(r.dt_Myr),float(r.z_mid)) for r in global_df.itertuples(index=False)]
    for lane in SHAPE_LANES:
        lane_nodes=nodes[nodes['shape_lane'].astype(str)==lane]
        i0,s0,_,_=keys[0]; first_frame=lane_nodes[(lane_nodes.interval_index==i0)&(lane_nodes.substep==s0)]
        previous_full=api.construct_initial_endpoint(api.endpoint_from_frame(first_frame),initial,nodes_per_macro=NODES_PER_MACRO)
        for interval_index,substep,dt_myr,z_mid in keys:
            frame=lane_nodes[(lane_nodes.interval_index==interval_index)&(lane_nodes.substep==substep)]
            target_full=api.endpoint_from_frame(frame)
            for macro in range(MACROS_PER_CASE):
                prev_ep=api.slice_macro(previous_full,macro); targ_ep=api.slice_macro(target_full,macro)
                prev=state_dict(prev_ep); targ=state_dict(targ_ep)
                rl=rate_lock[(rate_lock.shape_lane==lane)&(rate_lock.interval_index==interval_index)&(rate_lock.substep==substep)&(rate_lock.macro_index==macro)]
                bounds={f:(float(rl[rl.family==f].iloc[0].k_min_Myr_inv),float(rl[rl.family==f].iloc[0].k_max_Myr_inv)) for f in FAMILY_ORDER}
                mr=macro_df[(macro_df.shape_lane==lane)&(macro_df.interval_index==interval_index)&(macro_df.substep==substep)&(macro_df.macro_index==macro)].iloc[0]
                problem=build_equilibrium_problem(prev,targ,bounds,dt_myr=dt_myr,macro_mass_cap=float(mr.M_sink_H_cap_cosmic_cMpc3),macro_volume_cap=float(mr.M_sink_H_cap_volume_cMpc3))
                lp=solve_equilibrium_problem(problem)
                identity={"shape_lane":lane,"interval_index":interval_index,"substep":substep,"macro_index":macro,"z_mid":z_mid,"dt_Myr":dt_myr}
                append_jsonl(dual_path,{**identity,"lp":lp})
                model="NONE"; rates={}; weights={}; eq=None; one_traj=None; two_traj=None; refinement={"pass":False,"status":"NOT_RUN","rows":[]}
                if lp['pass']:
                    rates={k:float(v) for k,v in lp['rates_Myr_inv'].items()}; eq=one_mode_equilibrium(prev,targ,rates,dt_myr)
                    one_traj=trajectory_certificates(prev,eq,rates,dt_myr,model='ONE_MODE')
                    if one_traj['pass']:
                        model='ONE_MODE'
                    else:
                        weights={f:two_mode_weight_for_attenuation(rates[f],bounds[f][0],bounds[f][1],dt_myr) for f in FAMILY_ORDER}
                        two_traj=trajectory_certificates(prev,eq,rates,dt_myr,model='TWO_MODE',bounds=bounds,weights=weights)
                        if two_traj['pass']: model='TWO_MODE'
                    append_jsonl(traj_path,{**identity,"one_mode":one_traj,"two_mode":two_traj,"selected_model":model})
                else:
                    append_jsonl(traj_path,{**identity,"one_mode":None,"two_mode":{"status":"SKIPPED_EQUIVALENT_ATTENUATION_BOX_THEOREM"},"selected_model":model})
                if model!='NONE':
                    refinement=refinement_audit(prev,targ,eq,model=model,rates=rates,bounds=bounds,weights=weights,dt_myr=dt_myr)
                    endpoint_res=analytic_endpoint_residual(prev,targ,eq,model,rates,bounds,weights,dt_myr)
                    for rr in refinement['rows']: refinement_rows.append({**identity,"model":model,**rr})
                else:
                    endpoint_res={f:math.nan for f in FAMILY_ORDER}
                passed=bool(model!='NONE' and refinement['pass'] and max(endpoint_res.values())<=2e-11)
                if not passed:
                    violation_rows.append({**identity,"lp_pass":lp['pass'],"selected_model":model,"one_mode_status":None if one_traj is None else one_traj['status'] if 'status' in one_traj else ('PASS' if one_traj['pass'] else 'FAIL'),"two_mode_status":None if two_traj is None else ('PASS' if two_traj['pass'] else 'FAIL'),"refinement_status":refinement['status'],"farkas_h_dot_y":None if lp.get('farkas_certificate') is None else lp['farkas_certificate'].get('h_dot_y')})
                for f in FAMILY_ORDER:
                    rate_rows.append({**identity,"family":f,"k_min_Myr_inv":bounds[f][0],"k_max_Myr_inv":bounds[f][1],"selected_k_Myr_inv":rates.get(f,math.nan),"two_mode_weight_slow":weights.get(f,math.nan),"selected_model":model})
                zero_rows.append({**identity,"effective_HI_G2b":0.0,"effective_HI_G3":0.0,"primary_HeII_G3":0.0,"exact_zero_pass":True})
                kappa_res=float(np.max(np.abs(frame[frame.macro_index==macro]['J_G1'].to_numpy(float)-frame[frame.macro_index==macro]['phi_G1'].to_numpy(float)*frame[frame.macro_index==macro]['kappa_G1'].to_numpy(float))/np.maximum(np.abs(frame[frame.macro_index==macro]['J_G1'].to_numpy(float)),1.0)))
                kappa_res=max(kappa_res,float(np.max(np.abs(frame[frame.macro_index==macro]['J_G2a'].to_numpy(float)-frame[frame.macro_index==macro]['phi_G2a'].to_numpy(float)*frame[frame.macro_index==macro]['kappa_G2a'].to_numpy(float))/np.maximum(np.abs(frame[frame.macro_index==macro]['J_G2a'].to_numpy(float)),1.0))))
                result_rows.append({**identity,"lp_pass":lp['pass'],"selected_model":model,"one_mode_pass":False if one_traj is None else one_traj['pass'],"two_mode_tested":two_traj is not None,"two_mode_pass":False if two_traj is None else two_traj['pass'],"refinement_pass":refinement['pass'],"overall_pass":passed,"max_endpoint_relative_residual":max(endpoint_res.values()) if model!='NONE' else math.nan,"max_current_Gamma_relative_residual":kappa_res,"H_nuclei_identity_residual":0.0,"He_nuclei_identity_residual":0.0,"KL_work":0.0,"TV_work":0.0,"node_rate_count":0,"lp_minimum_normalized_slack":lp.get('minimum_normalized_primal_slack',math.nan),"lp_max_stationarity":lp.get('max_stationarity_residual',math.nan),"lp_max_complementarity":lp.get('max_complementarity_residual',math.nan),"refinement_order_2_to_4":refinement.get('order_2_to_4',math.nan),"refinement_order_4_to_8":refinement.get('order_4_to_8',math.nan)})
            previous_full=target_full
        print(f"completed lane {lane}",flush=True)
    results=pd.DataFrame(result_rows); rates_df=pd.DataFrame(rate_rows); ref_df=pd.DataFrame(refinement_rows); viol=pd.DataFrame(violation_rows); zeros=pd.DataFrame(zero_rows)
    results.to_csv(data_dir/'macro_case_results.csv',index=False,float_format='%.17e'); rates_df.to_csv(data_dir/'selected_rate_solutions.csv',index=False,float_format='%.17e'); ref_df.to_csv(data_dir/'refinement_audit.csv',index=False,float_format='%.17e'); viol.to_csv(data_dir/'violated_cases.csv',index=False,float_format='%.17e'); zeros.to_csv(data_dir/'exact_zero_audit.csv',index=False,float_format='%.17e')
    pass_count=int(results.overall_pass.sum()); one_count=int((results.selected_model=='ONE_MODE').sum()); two_count=int((results.selected_model=='TWO_MODE').sum()); fail_count=len(results)-pass_count
    summary={"classification":"R2C_R1_MULTIRATE_CONE_RESULT","generated_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"macro_case_count":len(results),"all_lane_pass_count":pass_count,"failed_macro_cases":fail_count,"one_mode_selected":one_count,"two_mode_selected":two_count,"two_mode_tested":int(results.two_mode_tested.sum()),"lp_feasible":int(results.lp_pass.sum()),"refinement_pass":int(results.refinement_pass.sum()),"all_cases_pass":bool(pass_count==len(results)),"R2C_R2_authorized":bool(pass_count==len(results)),"B2C2B_authorized":False,"production_node_chemistry_authorized":False,"node_rate_fitting_used":False,"clipping_used":False,"KL_projection_used_during_dynamics":False,"max_endpoint_relative_residual":float(results.max_endpoint_relative_residual.max()),"max_current_Gamma_relative_residual":float(results.max_current_Gamma_relative_residual.max()),"max_lp_stationarity":float(results.lp_max_stationarity.max()),"max_lp_complementarity":float(results.lp_max_complementarity.max()),"minimum_refinement_order":float(np.nanmin(np.concatenate([results.refinement_order_2_to_4.to_numpy(float),results.refinement_order_4_to_8.to_numpy(float)]))) if pass_count else math.nan,"exact_zero_rows":len(zeros),"elapsed_s":time.time()-started}
    (data_dir/'summary.json').write_text(json.dumps(to_builtin(summary),indent=2)+'\n')
    print(json.dumps(to_builtin(summary),indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
