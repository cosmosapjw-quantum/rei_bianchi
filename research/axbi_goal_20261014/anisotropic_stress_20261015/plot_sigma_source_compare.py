#!/usr/bin/env python3
"""Actual completed AX08 Sigma(z) versus new Pi-backreacted pilot Sigma(z).

Current user Sigma=sqrt3 abs(s)/H; legacy q_ref only used to pick frozen
source identity. Original HHe source/clock remains an independent historical run.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from coupled_pi import Solver,PhysicalScenario,sigma_init_from_legacy_signed_ratio,AREF,RHO_CRIT,H0,HREF,OM,OR,OL

HERE=Path(__file__).resolve().parent
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def make(owner):
    src=owner/"research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001"
    receipt=json.loads((src/"COMPOSITION_RECEIPT.json").read_text())
    assert receipt["status"]=="COMPOSED_COMPLETED_HISTORY_NOT_SCIENTIFIC_ADMISSION"
    assert receipt["row_counts"]["history.csv"]["composed_rows"]==312238
    assert digest(src/"history.csv")==receipt["output_sha256"]["history.csv"]
    assert digest(src/"feedback.csv")==receipt["output_sha256"]["feedback.csv"]
    actual=np.loadtxt(src/"history.csv",delimiter=",",skiprows=1,
                     usecols=(4,6,7,8),dtype=float)[::86]
    a,b,H,s=actual.T
    Sigma=np.sqrt(3)*abs(s)/H
    assert np.all(np.isfinite(Sigma))
    # Model uses same initial scalar as the historical negative-orientation source.
    init=math.sqrt(3)*abs(s[0])/H[0]
    assert abs(init-sigma_init_from_legacy_signed_ratio(-.01)[0])<2e-14
    modes={}
    for title,f,nu in (
      ("old-stress-free source and no Sigma feedback",0.,0.),
      ("new free-stream radiation Pi",1.,0.),
      ("new radiation Pi + phenomenological matter Pi",1.,.02)):
        model=PhysicalScenario(init,-1,f,nu)
        sol,info,_=Solver(model).solve(n=1101)
        vals={name:np.array([w[name] for w in info]) for name in
              ("Sigma","pi_r_J_m3","pi_m_J_m3")}
        modes[title]=(AREF*np.exp(sol.t),vals)
    fig,(ax,ay)=plt.subplots(2,1,figsize=(10,8.5),constrained_layout=True)
    ax.plot(1/a-1,Sigma,label="actual original saved AX08 Σ, no backreaction",
            lw=2,linestyle="--")
    for title,(ascale,v) in modes.items():
        ax.plot(1/ascale-1,v["Sigma"],label=title,alpha=.9)
        if title!="old-stress-free source and no Sigma feedback":
            ay.plot(1/ascale-1,v["pi_r_J_m3"]/RHO_CRIT,
                    label="radiation Π / ρcrit0 | "+title,alpha=.85)
            ay.plot(1/ascale-1,v["pi_m_J_m3"]/RHO_CRIT,
                    label="matter Π / ρcrit0 | "+title,linestyle="--",alpha=.85)
    ax.set_ylabel("User-defined Sigma = |sigma| / H")
    ax.set_title("Original frozen negative-orientation Sigma_ref=0.017319642 vs new coupled stress")
    ay.set_ylabel("Anisotropic stress scalar Π / rho_crit,0")
    ay.set_title("Trace-free spatial Pi tensor: diag(-Π,-Π,2Π)")
    for pane in (ax,ay):
        pane.set_xlabel("Mean redshift")
        pane.invert_xaxis()
        pane.grid(alpha=.25)
        pane.legend(fontsize=7)
    fig.suptitle("Real AX08 source overlay vs independent stress-coupled toy; ionizing photons & HHe not recoupled",fontsize=11)
    out=HERE/"results/source_vs_coupled_Sigma_and_Pi.png"
    fig.savefig(out,dpi=175)
    plt.close(fig)
    # Real source and independent toy stress-free near machine accuracy.
    # Source physical profile at exactly its own 3630+ saved scale points:
    # never quantify an interpolated 1101-plot-point curve as physical error.
    raw_signed_s_at_aref=float(s[0])
    s_background=raw_signed_s_at_aref*(AREF/a)**3
    h_flrw=H0*np.sqrt(OM/a**3+OR/a**4+OL)
    sig_exact=np.sqrt(3)*abs(s_background)/np.hypot(h_flrw,s_background)
    discrepancy=float(np.max(abs(Sigma-sig_exact)))
    print(json.dumps({"figure":str(out),
         "original_sha256":digest(src/"history.csv"),
         "initial_Sigma":init,
         "max_abs_old_source_vs_exact_density_fixed_Sigma":discrepancy,
         "source_scope":"legacy history, source-free model and optional viscosity are DISTINCT"},
         indent=2))
    return discrepancy
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--owner-root",type=Path,required=True)
    args=p.parse_args();make(args.owner_root)
