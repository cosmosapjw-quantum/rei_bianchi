#!/usr/bin/env python3
"""Plot source-frozen AX08 actual proper-time timestamp defect and q^2 clock drift."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from actual_clock_gl4 import load_one
from shortstep import Background, Family,gauss_batch,stable_dx
HERE=Path(__file__).resolve().parent
def run(root):
    hist={}
    stride=39
    fig,(ax0,ax1)=plt.subplots(2,1,figsize=(10,8.5),constrained_layout=True)
    for k in ("ZERO","SHEAR_HALF_PLUS","SHEAR_MINUS"):
        a,meta=load_one(root,k)
        hist[k]=a
        sample=np.unique(np.r_[np.arange(0,len(a),stride),len(a)-1])
        x=a[sample]
        t,scale,b=x.T
        bg=Background(Family(meta["q_ref"]))
        dt4,db4=gauss_batch(bg,scale[:-1],scale[1:],order=4)
        rel=abs(np.diff(t)-dt4)/dt4
        mids=(scale[:-1]+scale[1:])/2
        ax0.plot(1/mids-1,np.log10(np.maximum(rel,1e-17)),lw=1.1,label=k)
    reference=hist["ZERO"]
    a=np.exp(np.linspace(np.log(reference[0,1]),np.log(reference[-1,1]),1400))
    z=1/a-1
    t0=np.interp(a,reference[:,1],reference[:,0])
    for k in ("SHEAR_HALF_PLUS","SHEAR_MINUS"):
        y=hist[k]
        tq=np.interp(a,y[:,1],y[:,0])
        ax1.plot(z,(tq-t0)/1e9,lw=1.2,label=k)
    ax0.invert_xaxis();ax1.invert_xaxis()
    ax0.set_xlabel("Mean redshift")
    ax0.set_ylabel("log10 |(saved dt - independent GL4 dt)/GL4 dt|")
    ax0.set_title("Actual saved proper clock, every 39th accepted row, not ODE truncation bound")
    ax1.set_xlabel("Mean redshift")
    ax1.set_ylabel("t(q)-t(0) [10^9 proper seconds]")
    ax1.set_title("Physical signed background clock drift, different from local timestep error")
    for panel in (ax0,ax1):panel.grid(alpha=.25);panel.legend(fontsize=8)
    fig.suptitle("AX08 frozen density-fixed Bianchi-I; source-clock model only, AX11 not certified")
    dest=HERE/"results/ax08_saved_clock_error_and_q2_drift.png"
    fig.savefig(dest,dpi=170)
    plt.close(fig)
    # Reconstruct one strong REAL 1-step witness, identifying the numerical mechanism.
    z,meta=load_one(root,"ZERO")
    j=15
    a0,a1=z[j:j+2,1]
    t0,t1=z[j:j+2,0]
    bg=Background(Family(0.))
    dt4,_=gauss_batch(bg,np.array([a0]),np.array([a1]),order=4)
    stable=stable_dx(a0,a1)
    naive=math.log(float(a1)/bg.aref)-math.log(float(a0)/bg.aref)
    err=(t1-t0)-dt4[0]
    dxerr=(naive-stable)/bg.mean_hubble((a0+a1)/2)
    info={
      "schema":"rei.axbi.legacy_saved_proper_time_local_witness.v1",
      "status":"ACTUAL_SAVED_POSITIVE_ONE_ACCEPTED_STEP",
      "original_case":"ZERO","actual_row_indices":[j,j+1],
      "a0":float(a0),"a1":float(a1),
      "saved_clock_delta_s":float(t1-t0),"source_GL4_delta_s":float(dt4[0]),
      "saved_clock_minus_GL4_s":float(err),
      "relative_error":float(err/dt4[0]),
      "stable_dx_log1p":float(stable),
      "naive_dx_subtract_two_logarithms":float(naive),
      "approx_local_effect_of_dx_cancellation_s":float(dxerr),
      "interpretation":"timestamp and log-scale arithmetic show avoidable cancellation; does not by itself identify every source solver error.",
      "scientific_admission":"NOT_ISSUED"
    }
    (HERE/"results/clock_initial_step_witness.json").write_text(json.dumps(info,indent=2)+"\n")
    return info

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(run(args.owner_root),indent=2))
