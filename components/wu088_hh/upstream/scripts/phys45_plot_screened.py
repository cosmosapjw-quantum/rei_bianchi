#!/usr/bin/env python3
"""PHYS45 scientific figures of already-certified intervals (visualization only)."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--exact",type=Path,required=True)
 p.add_argument("--outdir",type=Path,required=True)
 a=p.parse_args()
 d=json.loads(a.exact.read_bytes())
 matrix=np.array([[(float(v[0])+float(v[1]))/2 for v in row]
                  for row in d["certified_V_matrix_interval"]])
 a.outdir.mkdir(parents=True,exist_ok=True)
 fig,ax=plt.subplots(figsize=(7.1,5.9))
 im=ax.imshow(1e18*matrix,origin="lower",aspect="equal")
 ax.set(xlabel="Input partial wave l'",ylabel="Output partial wave l",
        title="Screened H(1s)+H(1s) angular coupling at r = 20 a0")
 cb=fig.colorbar(im,ax=ax)
 cb.set_label("V_l l' (1e-18 in original atomic units)")
 fig.tight_layout()
 fig.savefig(a.outdir/"PHYS45_COUPLED_21x21.png",dpi=160)
 plt.close(fig)
 x=np.linspace(10,35,300)
 rr=0.7
 delta=x-rr
 ss=(1+1/delta)*np.exp(-2*delta)
 central=(1+1/x)*np.exp(-2*x)
 difference=ss-central
 fig,ax=plt.subplots(figsize=(7.6,4.8))
 ax.semilogy(x,ss,label="Full screened operator envelope")
 ax.semilogy(x,difference,label="Off-central operator envelope")
 ax.set(xlabel="Reference radius B / a0",
        ylabel="Rigorous analytic pointwise envelope (plot in float64)",
        title="Exterior screened potential vs noncentral remainder")
 ax.legend()
 ax.grid(alpha=.25)
 fig.tight_layout()
 fig.savefig(a.outdir/"PHYS45_EXTERIOR_ANALYTIC_ENVELOPES.png",dpi=160)
 plt.close(fig)
 print(json.dumps({"figures":[str(a.outdir/"PHYS45_COUPLED_21x21.png"),
                                str(a.outdir/"PHYS45_EXTERIOR_ANALYTIC_ENVELOPES.png")],
                   "plot_scope":"Float visualizations of exact rational certificate midpoints and analytic upper formulas, not new numeric proofs"}))
if __name__=="__main__":
 main()
