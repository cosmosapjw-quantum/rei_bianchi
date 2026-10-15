"""Actual scientific plot generation, one physical quantity per figure."""
import argparse
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def plot(source:Path,out:Path):
    rows=list(csv.DictReader(source.open()))
    assert len(rows)==1127
    for key,ylabel,name in [
      ("Sigma","Normalized shear Sigma = sqrt(3)|s|/H",
        "SIGMA_MASSIVE_REI_THOMSON.png"),
      ("Pi_massive_Jm3","Massive Vlasov Pi = (p_parallel-p_perp)/3 [Pa]",
        "PI_MASSIVE_RADIAL_EVOLUTION.png"),
      ("J0_0_integrated","Massive normalized energy J0^(0)",
        "MASSIVE_RADIAL_J0_EVOLUTION.png"),
    ]:
        fig,ax=plt.subplots(figsize=(8,4.8))
        for k in ["gamma_nu_no_matter","massive_positive",
                  "massive_negative","massive_no_thomson",
                  "massive_cold"]:
            subset=[r for r in rows if r["case"]==k]
            assert len(subset)==161
            ax.plot([float(r["zbar"]) for r in subset],
                    [float(r[key]) for r in subset],label=k,lw=1.2)
        ax.set_xlim(20,4)
        ax.set_xlabel("Mean scale redshift zbar")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(out/name,dpi=165)
        plt.close(fig)
    return 3

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True,type=Path)
    a.add_argument("--output",required=True,type=Path)
    v=a.parse_args()
    print("figures",plot(v.source,v.output))
