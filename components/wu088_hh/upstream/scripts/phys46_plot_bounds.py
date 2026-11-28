#!/usr/bin/env python3
"""Plot source-locked exact rational PHYS46 finite-channel contraction certificates."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--certificate",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 v=json.loads(a.certificate.read_bytes())
 rows=v["all_candidates_sorted_original_order"]
 T=np.array([d["T_a0"] for d in rows])
 q=np.array([float(d["q_upper"]) for d in rows])
 M=np.array([d["M_integer"] for d in rows])
 best=v["T_energy_patch_a0"]
 fig,ax=plt.subplots(figsize=(8,5.2))
 ax.semilogy(T,q,"o-",label="Certified finite-21 Volterra upper")
 ax.axhline(1,color="gray",ls=":",alpha=.6,label="Contraction threshold")
 ax.axvline(best,color="gray",ls="--",alpha=.5)
 ax.set(xlabel="Outgoing energy patch radius T / a0",
        ylabel="Rigorous weighted Volterra norm upper",
        title="Finite 21-channel outgoing Green contraction optimization")
 ax.grid(alpha=.25,which="both")
 ax.legend()
 ax2=ax.twinx()
 ax2.plot(T,M,marker="s",color="tab:orange",alpha=.4,label="Certified amplitude M")
 ax2.set_ylabel("Outward integer Coulomb amplitude envelope M")
 fig.tight_layout()
 a.out.parent.mkdir(parents=True,exist_ok=True)
 fig.savefig(a.out,dpi=170)
 plt.close(fig)
 print(json.dumps({"png":str(a.out),"bestT":best,"bestq":v["selected_q_strict_upper"],
                   "figure_scope":"visualization of already certified exact rational patch q; not an independent proof"}))
if __name__=="__main__":main()
