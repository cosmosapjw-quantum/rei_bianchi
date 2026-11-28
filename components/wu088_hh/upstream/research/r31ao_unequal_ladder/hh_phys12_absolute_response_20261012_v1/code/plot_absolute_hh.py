#!/usr/bin/env python3
"""Plot saved bounds only; no recomputation of source or response."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parents[1]
data=json.loads((root/"results/absolute_v1/ABSOLUTE_RESULTS.json").read_text())
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.titlesize":13,
                     "axes.labelsize":11,"savefig.facecolor":"white"})
fig,axes=plt.subplots(2,2,figsize=(12.0,7.3),layout="constrained")
panels=[("absolute","x_HII",1e-10,r"Absolute $D_{\rm HH}x_{\rm HII}(1)$",r"HII fraction / $10^{-10}$"),
        ("absolute","w",1e-9,r"Absolute $D_{\rm HH}w(1)$",r"Thermal energy / $10^{-9}$ eV per H"),
        ("mixed_reused","x_HII",1e-16,r"Mixed $I_{x_{\rm HII}}$ (reused)",r"HII fraction / $10^{-16}$"),
        ("mixed_reused","w",1e-15,r"Mixed $I_w$ (reused)",r"Thermal energy / $10^{-15}$ eV per H")]
colors={"full":"#17618e","first_half":"#ba5b22"}
for ax,(kind,obs,scale,title,label) in zip(axes.flat,panels):
    endpoints=[]
    for y,row in zip([1,0],data["rows"]):
        lo,hi=[float(v)/scale for v in row[kind][obs]["outward_decimal"]]
        color=colors[row["stage"]]
        ax.hlines(y,lo,hi,color=color,lw=5,zorder=3)
        ax.vlines([lo,hi],y-.09,y+.09,color=color,lw=1.5)
        endpoints.extend([lo,hi])
    low,high=min(0,*endpoints),max(0,*endpoints)
    gap=(high-low)*.08
    ax.set_xlim(low-gap,high+gap)
    ax.axvline(0,color="#777777",lw=.8,ls="--")
    ax.set_yticks([1,0],["full\n1.25 × 10⁹ s","first_half\n6.25 × 10⁸ s"])
    ax.set_ylim(-.55,1.55)
    ax.set_title(title,loc="left",pad=11)
    ax.set_xlabel(label)
    ax.grid(axis="x",alpha=.2)
    ax.spines[["top","right"]].set_visible(False)
fig.suptitle("Future H–H source: finite on/off and photon-birth interaction\n"
             "Fixed source coefficients within each stage; same initial COMMON",fontsize=16)
fig.supxlabel("Segments are conditional inclusion bounds, not confidence intervals.\n"
              "Both durations are separate first stages; b = 0 retains pre-existing photons.",fontsize=10)
fig.savefig(root/"figures/HH_PHYS12_ABSOLUTE_AND_MIXED.png",dpi=180)
fig.savefig(root/"figures/HH_PHYS12_ABSOLUTE_AND_MIXED.pdf")
plt.close(fig)
