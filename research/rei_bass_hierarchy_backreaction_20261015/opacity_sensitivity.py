#!/usr/bin/env python3
"""Explicitly separate actual-source ne interpolation and PSTF angular L truncation.

No unearned rigorous continuous-source accuracy. Compare source exact-saved
piecewise PCHIP with positive C2 log(ne) surrogate, alongside L truncation
at tight DOP853 tolerances in exactly the same background experiment.
"""
from __future__ import annotations
import json
from pathlib import Path
import time
import numpy as np
from lrs_boltzmann import HierarchyBackground,ElectronHistory,SmoothElectronHistory
from run_hierarchy import source_lock, actual_electrons,HERE

def main():
    root=Path.home()/"Dropbox/bianchi/rei_bianchi"
    src=root/"research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001/history.csv"
    h=np.loadtxt(src,delimiter=",",skiprows=1,usecols=(4,13),dtype=float)
    cols={}
    for label,source in (
       ("C2_8193",SmoothElectronHistory(h[:,0],h[:,1],nodes=8193)),
       ("C2_16385",SmoothElectronHistory(h[:,0],h[:,1],nodes=16385)),
       ("SOURCE_PCHIP_17",ElectronHistory(np.r_[h[::17,0],h[-1,0]],
                                          np.r_[h[::17,1],h[-1,1]])),
       ("SOURCE_PCHIP_ALL",ElectronHistory(h[:,0],h[:,1]))):
        ts=time.perf_counter()
        values=[]
        for L in (4,8,12):
            m=HierarchyBackground(source_lock(),L,1.,.2,0.,0,ne_source=source)
            s,wall=m.integrate(n=51,rtol=1e-13,atol=4e-15)
            last=m.diagnostic(s.t[-1],s.y[:,-1])
            values.append({"L":L,"Sigma_final":last["Sigma"],"J2_final":last["J2"],
                           "N0_final":last["N0"],"nfev":int(s.nfev),
                           "ODE_wall_s":wall})
        base=values[1]
        cols[label]={
          "C2_observed_max_relative_source_error_if_applicable":
            getattr(source,"max_relative_source_error",None),
          "C2_p999_relative_source_error_if_applicable":
            getattr(source,"p999_relative_source_error",None),
          "source_nodes":len(source.x),
          "solutions":values,
          "max_J2_L8_to_L12":abs(values[1]["J2_final"]-values[2]["J2_final"]),
          "max_Sigma_L8_to_L12":abs(values[1]["Sigma_final"]-values[2]["Sigma_final"]),
          "total_wall_s":time.perf_counter()-ts
        }
    target=cols["SOURCE_PCHIP_ALL"]["solutions"][1]
    for key,rec in cols.items():
        node=rec["solutions"][1]
        rec["relative_DeltaJ2_against_PCHIP_ALL"]= (node["J2_final"]-target["J2_final"])/target["J2_final"]
        rec["absolute_DeltaJ2_against_PCHIP_ALL"]=node["J2_final"]-target["J2_final"]
        rec["absolute_DeltaSigma_against_PCHIP_ALL"]=node["Sigma_final"]-target["Sigma_final"]
    result={
      "schema":"rei.crossrepo.true_original_ax08_electron_input_sensitivity.v1",
      "status":"ACTUAL_SOURCE_OPACITY_C2_AND_PCHIP_L_MOMENT_CONVERGENCE_CHECKED",
      "method":"same positive actual 312238 ne(a) points, optional C2 log-ne smooth positive reconstruction, PCHIP all points, DOP853 1e-13 and 4e-15, L4/8/12",
      "input_independent_source_error":"C2 max relative mismatch at original actual points is measured, not guaranteed between knots",
      "observed_energy_and_number_L0_ledger":"exact structural identities checked separately",
      "scope":"one-way historical electron donor to collision-only CMB moments, no sourced HHe cosmological refit",
      "comparison":cols,
      "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/opacity_source_sensitivity.json").write_text(json.dumps(result,indent=2)+"\n")
    for name,x in cols.items():
        print(name,"source_points",x["source_nodes"],"source_error",x["C2_observed_max_relative_source_error_if_applicable"],
           "L8_12_J2",x["max_J2_L8_to_L12"],"against_true_J2",x["absolute_DeltaJ2_against_PCHIP_ALL"],
           "Sigma_difference",x["absolute_DeltaSigma_against_PCHIP_ALL"],
           "time",x["total_wall_s"],flush=True)
if __name__=="__main__":main()
