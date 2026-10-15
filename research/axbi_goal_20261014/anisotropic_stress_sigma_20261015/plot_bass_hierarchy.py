"""Reproducible plain scientific figures of actual coupled BASS-seeded histories."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def figure(csvpath:Path,out:Path):
    data=list(csv.DictReader(csvpath.open()))
    if len(data)!=7260:
        raise ValueError("physical campaign has not generated required 60x121 rows")
    configs=[
        (0.,0.,0.,"initial isotropic reference"),
        (.2,0.,0.,"radiation A=+0.2"),
        (-.2,0.,0.,"radiation A=-0.2"),
        (0.,.4,0.,"matter A=+0.4"),
        (.2,.4,0.,"radiation A=+0.2, matter A=+0.4"),
    ]
    for field,ylab,filename in [
        ("Sigma","Sigma = |sigma|/H","BASS_SIGMA_SEED_EVOLUTION.png"),
        ("Pi_rad_J_m3","Radiation Pi_parallel-minus-perp [Pa]",
         "BASS_RADIATION_HIERARCHY_STRESS.png"),
        ("Pi_matter_J_m3","Matter Pi_parallel-minus-perp [Pa]",
         "BASS_MATTER_HIERARCHY_STRESS.png"),
    ]:
        fig,ax=plt.subplots(figsize=(8,4.5))
        for ar,am,orientation,label in configs:
            subset=[r for r in data if
                 r["gas"]=="donor" and float(r["Sigma_ref"])==0.
                 and float(r["A_rad"])==ar and float(r["A_matter"])==am
                 and int(r["orientation_seed"])==orientation]
            if len(subset)!=121:
                raise ValueError(f"expected 121 actual history rows {label}")
            z=[float(row["zbar"]) for row in subset]
            val=[float(row[field]) for row in subset]
            ax.plot(z,val,lw=1.3,label=label)
        ax.set_xlabel("Mean redshift zbar")
        ax.set_xlim(20,4)
        ax.set_ylabel(ylab)
        ax.grid(alpha=.18)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out/filename,dpi=160)
        plt.close(fig)

    # Compare exact kinetic hierarchy to its clearly identified l=2
    # linear expansion, which was *not* used in the Einstein solver.
    for field,linear,denom,filename in [
        ("Pi_rad_J_m3","pi_rad_l2_linear","epsilon_rad_J_m3",
         "BASS_RADIATION_L2_TRUNCATION_ERROR.png"),
        ("Pi_matter_J_m3","pi_matter_l2_linear","u_matter_kin_J_m3",
         "BASS_MATTER_L2_TRUNCATION_ERROR.png"),
    ]:
        fig,ax=plt.subplots(figsize=(8,4.5))
        for ar,am,_,label in configs[1:]:
            subset=[r for r in data if
                    r["gas"]=="donor" and float(r["Sigma_ref"])==0.
                    and float(r["A_rad"])==ar and float(r["A_matter"])==am]
            z=[float(r["zbar"]) for r in subset]
            values=[(float(r[field])-float(r[linear]))/float(r[denom])
                    for r in subset]
            ax.plot(z,values,lw=1.3,label=label)
        ax.set_xlabel("Mean redshift zbar")
        ax.set_xlim(20,4)
        ax.set_ylabel("Exact kinetic minus linear l=2, / sector energy")
        ax.legend(fontsize=7)
        ax.grid(alpha=.18)
        fig.tight_layout()
        fig.savefig(out/filename,dpi=160)
        plt.close(fig)
    return 5


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--history",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    v=ap.parse_args()
    print("generated_figures",figure(v.history,v.output_dir))
