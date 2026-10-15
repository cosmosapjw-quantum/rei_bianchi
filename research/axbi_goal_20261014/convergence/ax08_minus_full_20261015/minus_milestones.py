#!/usr/bin/env python3
"""Actual AX08 HII upward milestone crossing in ln(a)-monotone histories.

The entire saved computational data are original and signed -0.01 completion.
First upward crossings, slope and interpolation method are explicit.
This is an exploratory fixed-redshift statistic, not AX11 discretization error.
"""
import argparse
import csv
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"ax08_clock_census_20261015"))
import clock_census as cc
import minus_full_diagnostic as md

LEVELS=(.01,.1,.5,.9,.99,.999)

def crossing(a,t,x,y):
    assert len(a)==len(t)==len(x)
    if not all(np.all(np.isfinite(v)) for v in (a,t,x)):
        raise ValueError("INVALID_NONFINITE")
    if np.any(np.diff(a)<=0) or np.any(np.diff(t)<=0):
        raise ValueError("CLOCK_NOT_STRICTLY_MONOTONE")
    pairs=np.flatnonzero((x[:-1]<y)&(x[1:]>=y))
    if not len(pairs):
        raise ValueError("NO_UPWARD_CROSSING")
    i=int(pairs[0]);dd=x[i+1]-x[i]
    if dd<=0:raise ValueError("NONUPWARD_SELECTED_CROSSING")
    alpha=(y-x[i])/dd
    ai=a[i]+alpha*(a[i+1]-a[i])
    ti=t[i]+alpha*(t[i+1]-t[i])
    return {
      "zbar":float(1/ai-1),"a":float(ai),"proper_time_s":float(ti),
      "bracketing_scale_width":float(a[i+1]-a[i]),
      "bracketing_time_width_s":float(t[i+1]-t[i]),
      "all_upward_crossings":int(len(pairs)),
      "sample_left_row":i,
      "linear_fraction":float(alpha)
    }

def evaluate(owner):
    minus_metadata,_=md.bind_minus(owner)
    known=cc.bindings(owner)
    paths={
      "ZERO":Path(known["ZERO"]["history"]["path"]),
      "SHEAR_HALF_PLUS":Path(known["SHEAR_HALF_PLUS"]["history"]["path"]),
      "SHEAR_MINUS":owner/minus_metadata["history"]["path"]
    }
    h={k:cc.history(p)[0] for k,p in paths.items()}
    r={}
    for level in LEVELS:
        c={name:crossing(v[:,1],v[:,0],v[:,4],level) for name,v in h.items()}
        base=c["ZERO"]
        mn=c["SHEAR_MINUS"];hp=c["SHEAR_HALF_PLUS"]
        r[str(level)]={
          "cases":c,
          "minus_minus_zero_redshift":mn["zbar"]-base["zbar"],
          "half_plus_minus_zero_redshift":hp["zbar"]-base["zbar"],
          "minus_minus_zero_proper_s":mn["proper_time_s"]-base["proper_time_s"],
          "half_plus_minus_zero_proper_s":hp["proper_time_s"]-base["proper_time_s"],
          "unequal_amp_q_squared_ratio":
              (mn["zbar"]-base["zbar"])/(hp["zbar"]-base["zbar"])
              if hp["zbar"]!=base["zbar"] else None
        }
    return {
      "schema":"rei.axbi.minus_hii_milestone_crossing.v1",
      "status":"EXPLORATORY_THREE_ACTUAL_FULL_CASES",
      "crossing":"first upward linear interpolation in fixed physical accepted samples; full source case at every point",
      "source_relation":"ZERO original, PLUS_HALF and MINUS reviewed resource-only 4096MiB output arm",
      "levels":LEVELS,"results":r,
      "interpretation":"Mean-redshift shift of HII crossing, not observational inference; physical numerical solver error UNKNOWN",
      "scientific_admission":"NOT_ISSUED"
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--owner-root",type=Path,required=True)
    args=ap.parse_args()
    result=evaluate(args.owner_root)
    dest=HERE/"results_001"/"MINUS_MILESTONES.json"
    dest.write_text(json.dumps(result,indent=2)+"\n")
    for level,v in result["results"].items():
        print(level,"minus_dz",v["minus_minus_zero_redshift"],
              "halfplus_dz",v["half_plus_minus_zero_redshift"],
              "ratio",v["unequal_amp_q_squared_ratio"])
