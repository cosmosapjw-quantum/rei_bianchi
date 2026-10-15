"""Source-result plots without interpolating uncomputed Einstein histories."""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
EV=HERE/"evidence"

def draw():
    original=json.loads((EV/"INITIAL_CANCELLATION_NO_THOMSON.json").read_text())
    scattered=json.loads((EV/"INITIAL_CANCELLATION_REAL_HHE_THOMSON.json").read_text())
    orig={k["tag"]:k for k in original["signed_initial_shear_cancellation_roots"]}
    scat={k["tag"]:k for k in scattered["signed_initial_shear_cancellation_roots"]}
    tags=["radiation_only","rad_plus_massive_positive",
          "rad_plus_massive_negative","massive_only_positive",
          "massive_only_negative","cold_massive_plus_rad",
          "photon_seed_only","neutrino_seed_only"]
    names=["gamma+nu","gamma+nu,mass A=+.5","gamma+nu,mass A=-.5",
           "mass A=+.5","mass A=-.5","gamma+nu,cold mass",
           "gamma only","nu only"]
    x=np.arange(len(tags))
    fig,ax=plt.subplots(figsize=(9.6,5.4))
    ax.barh(x-.2,[orig[z]["q_ref_internal"] for z in tags],height=.38,label="No Thomson")
    ax.barh(x+.2,[scat[z]["q_ref_internal"] for z in tags],height=.38,
            label="Original HHe n_e driven photon Thomson")
    ax.set_yticks(x,labels=names)
    ax.axvline(0,linewidth=.8)
    ax.set_xlabel("q_ref that cancels signed s/H at zbar=4 (internal signed input)")
    ax.set_title("LRS Einstein-Vlasov initial stress / initial shear compensation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"C8_INITIAL_PI_COMPENSATING_Q.png",dpi=185)
    plt.close(fig)

    with (EV/"TRAJECTORY_MEMORY_1203.csv").open() as f:
        rows=list(csv.DictReader(f))
    vals={}
    for row in rows:
        vals.setdefault(row["scenario"],[]).append(row)
    names={"stress_seed_s0":"Initial s=0, pi nonzero",
           "cancelled_end_s":"Fine-tuned initial signed shear",
           "overcancelled_end_s":"More negative initial shear"}
    for key,label,file,ylabel in [
      ("signed_s_over_H","s/H","C8_SIGNED_SHEAR_HISTORY.png","Signed s/H"),
      ("b","b","C8_ANISOTROPIC_METRIC_MEMORY.png","Integrated metric anisotropy b")
    ]:
        fig,ax=plt.subplots(figsize=(8.2,5))
        for name,sequence in vals.items():
            xs=[float(v["zbar"]) for v in sequence]
            ys=[float(v[key]) for v in sequence]
            ax.plot(xs,ys,label=names[name])
        ax.axhline(0,linewidth=.8)
        ax.invert_xaxis()
        ax.set(xlabel="Mean redshift zbar=1/a-1",ylabel=ylabel,
               title=f"Source-coupled Einstein-Boltzmann: {label} along zbar20->4")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(EV/file,dpi=185)
        plt.close(fig)
    print("SOURCE_PLOTS_SAVED",*[f.name for f in EV.glob("C8_*.png")])

if __name__=="__main__":
    draw()
