"""Three source-readback visualizations: nonlinear degeneracy and Jacobian."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
EV=HERE/"evidence"
def run():
    a=json.loads((EV/"RESPONSE_INITIAL.json").read_text())
    d=json.loads((EV/"NONLINEAR_DEGENERACY.json").read_text())
    x=np.asarray(d["x"])
    z=21*np.exp(-x)-1
    base=np.asarray(d["base"]);other=np.asarray(d["distinct"])
    fig,ax=plt.subplots(figsize=(8.4,5.2))
    ax.plot(z,base[:,0],label="A: q=0, kg=.2")
    ax.plot(z,other[:,0],"--",label="B: q=5e-5, kg=0.166901...",alpha=.85)
    ax.invert_xaxis()
    ax.set(xlabel="Mean redshift zbar",ylabel="Signed shear s/H",
           title="Distinct initial Σ–π produce the same endpoint shear")
    ax.legend()
    fig.tight_layout()
    fig.savefig(EV/"SHEAR_DEGENERACY_HISTORY.png",dpi=170)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4.6))
    axes[0].plot(z,base[:,1],label="A")
    axes[0].plot(z,other[:,1],"--",label="B")
    axes[0].invert_xaxis();axes[0].set(xlabel="Mean redshift",ylabel="Metric anisotropy b",
            title="Different background histories")
    axes[1].plot(z,base[:,2],label="A gamma E2")
    axes[1].plot(z,other[:,2],"--",label="B gamma E2")
    axes[1].invert_xaxis();axes[1].set(xlabel="Mean redshift",ylabel="Photon E2 quadrupole",
            title="Different radiation signature")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(EV/"DEGENERATE_STRESS_OBSERVABLES.png",dpi=170)
    plt.close(fig)
    r=a["cases"]["actual_zero_HHe_oneway_thomson"]
    J=np.asarray(r["coarse"]["J_final_S"])
    # Use all five physically separated endpoints and explicitly declared units.
    x=np.asarray(r["coarse"]["J_final_S"])
    M=np.array([r["coarse"]["J_final_S"],r["coarse"]["J_final_b"],
                r["coarse"]["J_final_Egamma2"],r["coarse"]["J_final_Enu2"],
                r["coarse"]["J_final_massive_pi"]])
    scale=np.array(a["scalar_inputs"]["observable_scales"])
    dp=np.array(list(a["scalar_inputs"]["finite_difference_halfstep"].values()))
    mat=M*dp[None,:]/scale[:,None]
    fig,ax=plt.subplots(figsize=(8,4.8))
    img=ax.imshow(np.sign(mat)*np.log10(1+np.abs(mat)),cmap="coolwarm",aspect="auto")
    ax.set_xticks(range(4),["signed q","kappa gamma","kappa nu","A massive"],rotation=15)
    ax.set_yticks(range(5),["signed s/H","b","photon E2","neutrino E2","massive Pi"])
    ax.set_title("Signed scaled response, log10(1+absolute value)")
    fig.colorbar(img,ax=ax)
    fig.tight_layout()
    fig.savefig(EV/"SIGMA_PI_RESPONSE_JACOBIAN.png",dpi=170)
    plt.close(fig)
    print("PLOTS",*[str(q) for q in EV.glob("*.png")],sep="\n")
if __name__=="__main__":run()
