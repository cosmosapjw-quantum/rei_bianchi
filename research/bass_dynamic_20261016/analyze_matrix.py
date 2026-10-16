#!/usr/bin/env python3
"""Independent comparison of NCP receipts at matched initial state and endpoint."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import sys

root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name("ncp_evidence")
prefix=sys.argv[2] if len(sys.argv)>2 else "corrected"
def result(name): return json.loads((root/name/"result.json").read_text())
def paired(a,b,fields):
    a,b=result(a),result(b)
    assert a["case"]==b["case"]
    assert abs(a["a"]-b["a"])/a["a"]<1e-12
    return {k:abs(a[k]-b[k]) for k in fields}
fields=("time_s","b","h_per_s","s_per_s","temperature_k","x_hii","x_heii","source_n_per_h")
summary={"schema":"bass.rei.dynamic_convergence.v1","basis":"matched case, initial state, source and final log-scale; independent geometry or chemistry refinement","fields_units":{"time_s":"s","b":"dimensionless","h_per_s":"s^-1","s_per_s":"s^-1","temperature_k":"K","x_hii":"fraction","x_heii":"fraction","source_n_per_h":"H^-1"},"cases":{}}
for tag in ("cold","signed"):
    case={}
    for span in ("long","short"):
        names=[f"{prefix}_{tag}_{span}_g{n}" for n in (121,241,481)]
        d1=paired(names[0],names[1],fields);d2=paired(names[1],names[2],fields)
        case[f"{span}_geometry"]={"grids":[121,241,481],"step_dln_a":result(names[0])["dln_a"],"steps":result(names[0])["steps"],"delta_121_241":d1,"delta_241_481":d2,
            "difference_ratio":{k:d1[k]/d2[k] if d2[k] else None for k in fields}}
        names=[f"{prefix}_{tag}_{span}_g481",f"{prefix}_{tag}_{span}_t8",f"{prefix}_{tag}_{span}_t16"]
        if span=="short":names.append(f"{prefix}_{tag}_{span}_t32")
        changes=[paired(a,b,fields) for a,b in zip(names,names[1:])]
        case[f"{span}_chemistry"]={"fixed_grid":481,"step_dln_a":[result(n)["dln_a"] for n in names],"steps":[result(n)["steps"] for n in names],
            "consecutive_absolute_differences":changes,
            "difference_ratios":[{k:changes[i][k]/changes[i+1][k] if changes[i+1][k] else None for k in fields} for i in range(len(changes)-1)],
            "classification":"NUMERICALLY_CHECKED_FIRST_ORDER_TREND" if span=="short" else "HOLD_NO_STABLE_TIMESTEP_CONVERGENCE"}
    summary["cases"][tag]=case
all_results=[result(p.name) for p in root.glob(f"{prefix}_*") if (p/"result.json").exists()]
assert len(all_results)==22,len(all_results)
summary["run_count"]=len(all_results)
summary["max_abs_photon_residual_per_h"]=max(abs(x["photon_residual_per_h"]) for x in all_results)
summary["max_abs_energy_residual_ev_per_h"]=max(abs(x["energy_residual_ev_per_h"]) for x in all_results)
summary["max_hamiltonian_normalized"]=max(x["max_hamiltonian_normalized"] for x in all_results)
summary["max_raychaudhuri_normalized"]=max(x["max_raychaudhuri_normalized"] for x in all_results)
summary["max_newton_residual"]=max(x["newton_residual"] for x in all_results)
summary["all_restart_exact"]=all(x["restart_max_abs"]==0 for x in all_results)
summary["all_adaptive_trial_accepted"]=all(x["adaptive_status"]=="ACCEPTED" and x["adaptive_accepted"]==1 for x in all_results)
summary["max_adaptive_rejects"]=max(x["adaptive_rejects"] for x in all_results)
summary["source_time"]={}
for tag in ("cold","signed"):
    name=f"{prefix}_{tag}_long_g481"
    rows=list(csv.DictReader((root/name/"step_trace.csv").open()))
    rates=[float(r["emissivity_per_h_s"]) for r in rows]
    residuals=[float(r["source_residual_per_h"]) for r in rows]
    summary["source_time"][tag]={"first_rate_per_h_s":rates[0],"last_rate_per_h_s":rates[-1],"changed":rates[0]!=rates[-1],
        "max_abs_step_source_residual_per_h":max(map(abs,residuals))}
print(json.dumps(summary,indent=2,sort_keys=True))
