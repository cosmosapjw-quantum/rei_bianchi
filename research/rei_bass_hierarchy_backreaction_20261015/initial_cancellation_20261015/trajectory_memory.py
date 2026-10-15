"""Quantified shear-memory: instantaneous s_end=0 need not imply b_end=0.

The photon directional energy redshift ratio only depends on the integrated
axis scale b and is independent of a cancellation in endpoint H shear.
Original source-locked physical b,s,H,Pis retained in machine-readable CSV.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
import numpy as np
from initial_cancellation import new_model,source_identity

FIELDS=("scenario","q_ref","a","zbar","proper_elapsed_s","signed_s_over_H","Sigma",
        "b","H_per_s","Pi_gamma_J_m3","Pi_nu_J_m3","Pi_matter_J_m3",
        "gamma_J2","nu_J2","massive_J0_0","massive_J2_0")

def run(result_json:Path,outcsv:Path):
    source_identity()
    data=json.loads(result_json.read_text())
    rootq=next(x["q_ref_internal"] for x in data["signed_initial_shear_cancellation_roots"]
               if x["tag"]=="rad_plus_massive_positive")
    kwargs=dict(kappa_gamma=.2,kappa_nu=.2,Am=.5,fm=.1,mass=30.,nrad=96,nmu=32)
    rows=[];summary=[]
    for name,q in [("stress_seed_s0",0.),("cancelled_end_s",rootq),
                   ("overcancelled_end_s",-0.001)]:
        m=new_model(q,**kwargs)
        sol,vals,_=m.integrate(n=401,rtol=2e-11,atol=1e-13)
        N=m.imax+1
        for i,x in enumerate(sol.t):
            w=vals[i]
            row=dict(scenario=name,q_ref=q,a=w["a"],zbar=1/w["a"]-1,
                 proper_elapsed_s=float(sol.y[0,i]/m.source.href),
                 signed_s_over_H=w["s"]/w["H"],Sigma=w["Sigma"],b=float(sol.y[1,i]),
                 H_per_s=w["H"],Pi_gamma_J_m3=w["Pi_gamma_J_m3"],
                 Pi_nu_J_m3=w["Pi_nu_J_m3"],Pi_matter_J_m3=w["Pi_matter_J_m3"],
                 gamma_J2=w["E_gamma"][2],nu_J2=w["E_nu"][2],
                 massive_J0_0=sol.y[m.main_size,i],
                 massive_J2_0=sol.y[m.main_size+N,i])
            rows.append(row)
        w=vals[-1];b=float(sol.y[1,-1])
        summary.append({
            "scenario":name,"q_ref":q,
            "Sigma_initial":float(m.Sigma_ref),
            "s_over_H_end":float(w["s"]/w["H"]),
            "b_end":b,
            "cross_direction_log_energy_gap":float(-3*b),
            "cross_direction_energy_ratio_transverse_over_axial":float(np.exp(-3*b)),
            "last_metric_not_isotropic":abs(b)>1e-6,
            "massive_Pi_s_end_J_m3":float(w["Pi_matter_J_m3"])
        })
    if not (len(rows)==3*401 and
            abs(summary[1]["s_over_H_end"])<3e-11 and
            summary[1]["last_metric_not_isotropic"]):
        raise RuntimeError("NO_INSTANTANEOUS_CANCELLATION_MEMORY")
    if outcsv.exists():raise FileExistsError(outcsv)
    with outcsv.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    return {
      "schema":"rei.BASS_initial_pi_Cauchy_memory.v1",
      "physical_source":"PR140 exact sourced gamma/nu plus positive finite-mass FD Vlasov",
      "physical_initial_stress_inputs":{"kappa_gamma":.2,"kappa_nu":.2,"A_massive":.5,
         "mass_fraction":.1,"m_over_T_ref":30},
      "n_cases":3,"total_history_rows":len(rows),
      "mean_redshift":[20,4],
      "summary":summary,
      "CSV_data_path":str(outcsv),
      "stellar_ionizing_history":"NOT_RECOMPUTED",
      "radiation_directional_log_energy":"collisionless Killing photons only, no opacity, not observed CMB"
    }
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--csv",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    j=run(a.input,a.csv)
    a.output.write_text(json.dumps(j,indent=2)+"\n")
    print(json.dumps(j["summary"],indent=2))
