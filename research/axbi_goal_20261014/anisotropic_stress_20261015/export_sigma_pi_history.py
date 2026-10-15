#!/usr/bin/env python3
"""Machine-readable Sigma, orientation, radiation/matter Pi full coupled pilot grid.

15 actual full ODE trajectories at 501 log(a) samples. Source parameters
remain frozen; no HHe radiation transport or photoheating is claimed.
"""
import csv
import json
from pathlib import Path
import math
import numpy as np
from coupled_pi import AREF, RHO_CRIT
from run_experiments import scenario_runs
HERE=Path(__file__).resolve().parent
HEADER=(
    "Sigma_ref","epsilon_sigma_ref","f_free_radiation","nu_matter_viscosity",
    "a","mean_zbar","elapsed_proper_s","b_signed",
    "Sigma","Sigma_WE","epsilon_sigma_local",
    "s_per_s","H_per_s",
    "rho_r_J_m3","rho_dust_J_m3","u_th_J_m3","p_th_J_m3",
    "Pi_rad_J_m3","Pi_matter_J_m3","Pi_total_J_m3",
    "Sigma_Hamiltonian_fraction_s2_over_H2"
)
def run():
    all_cases=scenario_runs()
    outfile=HERE/"results/coupled_full_Sigma_Pi_history.csv"
    with outfile.open("w",newline="") as fh:
        csvwriter=csv.writer(fh,lineterminator="\n")
        csvwriter.writerow(HEADER)
        for model,sol,info,wall,evals in all_cases:
            for i,point in enumerate(info):
                vals=(
                    model.Sigma_ref,model.orientation,
                    model.free_radiation_fraction,model.matter_viscosity_strength,
                    point["a"],1/point["a"]-1,
                    sol.y[3,i]/__import__("coupled_pi").HREF,
                    float(sol.y[0,i]),
                    point["Sigma"],point["Sigma_WE"],point["orientation"],
                    point["signed_s_per_s"],point["H_per_s"],
                    RHO_CRIT*point["rad_energy_over_rhocrit"],
                    RHO_CRIT*point["rho_dust_over_rhocrit"],
                    RHO_CRIT*point["rho_thermal_over_rhocrit"],
                    RHO_CRIT*point["pressure_th_over_rhocrit"],
                    point["pi_r_J_m3"],point["pi_m_J_m3"],point["pi_total_J_m3"],
                    point["shear_energy_per_H2"]
                )
                csvwriter.writerow([int(v) if j in (1,10) else format(v,".17g") for j,v in enumerate(vals)])
    with outfile.open(newline="") as fh:
        rows=list(csv.DictReader(fh))
    if len(rows)!=15*501 or any(not(0<=float(x["Sigma"])<math.sqrt(3)) for x in rows):
        raise RuntimeError("INVALID_EXPORTED_TENSOR_SCALAR_HISTORY")
    if any(abs(float(x["Pi_rad_J_m3"])+float(x["Pi_matter_J_m3"])-float(x["Pi_total_J_m3"]))>1e-24 for x in rows):
        raise RuntimeError("PI_TOTAL_NOT_EIGENVALUE_SUM")
    if any(abs(float(x["Sigma"])/math.sqrt(3)-float(x["Sigma_WE"]))>2e-16 for x in rows):
        raise RuntimeError("SIGMA_NORMALIZATION_NOT_EXPLICIT")
    result={
        "schema":"rei.axbi.actual_sourcefree_Sigma_Pi_history.v1",
        "status":"ALL_15_SCOPED_RADIATION_MATTER_PI_COUPLED_SOLUTIONS_EXPORTED",
        "file":str(outfile.relative_to(HERE)),
        "rows":len(rows),
        "scenarios":15,
        "samples_per_scenario":501,
        "physical_scope":"source-free initially isotropic radiation envelope plus optional phenomenological viscous matter; not original HHe photoionization",
        "primary_shear":"Sigma>=0 + epsilon_sigma orientation",
        "pi_tensor":"diag(-Pi_total,-Pi_total,2 Pi_total)",
        "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/coupled_Sigma_Pi_HISTORY_STATUS.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":run()
