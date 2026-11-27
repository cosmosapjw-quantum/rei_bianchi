#!/usr/bin/env python3
"""Visualize rigorously bounded Coulomb barrier action vs numerical H+ diagnostic."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cert",type=Path,required=True)
    p.add_argument("--oracle",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    cert=json.loads(a.cert.read_text())
    ref=json.loads(a.oracle.read_text())
    if cert["original_source_sha256"]!=ref["source_SHA256"]:
        raise ValueError("different original source identity")
    rows=cert["action_enclosures"]
    if [z["ell"] for z in rows]!=[z["ell"] for z in ref["rows"]]:
        raise ValueError("unmatched source partial waves")
    ell=np.array([d["ell"] for d in rows])
    low=np.array([float(d["action_lower"]) for d in rows])
    high=np.array([float(d["action_upper"]) for d in rows])
    action_numeric=np.array([float(d["forbidden_action_numeric"]) for d in ref["rows"]])
    logH=np.array([float(d["log_outgoing_Hplus_B_numeric"]) for d in ref["rows"]])
    if np.any(action_numeric<low-1e-9) or np.any(action_numeric>high+1e-9):
        raise ArithmeticError("noncert numerical samples outside rigorous action enclosure")
    fig,ax=plt.subplots(figsize=(8,5))
    ax.fill_between(ell,low,high,alpha=.25,label="Certified action interval")
    ax.plot(ell,action_numeric,"o-",label="Independent 55-digit action integral")
    ax.plot(ell,logH,"s--",label="Numerical log |Coulomb H+ at r=20|")
    ax.set(xlabel="Angular momentum ell",ylabel="Dimensionless positive magnitude",
           title="Coulomb centrifugal forbidden action and outgoing irregular amplitude")
    ax.grid(alpha=.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(a.out,dpi=160)
    plt.close(fig)
    print(json.dumps({"figure":str(a.out),"source_SHA":cert["original_source_sha256"],
      "interpretation":"Action is rigorously enclosed; H+ amplitude and comparison are numerical only; no certified tunneling law"}))
if __name__=="__main__":
    main()
