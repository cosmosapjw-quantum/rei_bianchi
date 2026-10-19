import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
root=Path(__file__).resolve().parent.parent
j=json.loads((root/"postloss_diagnostic/FIXED_GAS_OPTICAL_RESPONSE.json").read_text())
y=np.array([c["relative_change_using_right_denominator"]["all_below_H_fit"] for c in j["comparisons"]])
fig,ax=plt.subplots(figsize=(10,6.1),layout="constrained")
fig.set_constrained_layout_pads(h_pad=.08,w_pad=.1,hspace=.06)
x=np.arange(4)
ax.bar(x,np.abs(y),width=.58,color=["#237A94"]*3+["#C36D38"],zorder=3)
ax.set_yscale("log");ax.set_ylim(5e-18,5e-6)
ax.set_xticks(x,["Energy GL\n6 → 8","Energy GL\n8 → 12","Time GL\n16 → 24","Gas PCHIP\n13 → 18 knots"],fontsize=11)
ax.set_ylabel("Absolute relative change in core survivor",fontsize=11)
ax.set_title("Fixed-gas spectral response: finite comparisons",loc="left",fontsize=16,pad=35)
ax.text(0,1.035,"Preserved physical source · 160 births · GL8 · first-cell energy only",transform=ax.transAxes,fontsize=10,color="#495560")
for i,v in enumerate(y):ax.text(i,abs(v)*1.55,f"{v:+.3e}",ha="center",fontsize=11,fontweight="bold")
ax.grid(axis="y",which="major",alpha=.24,zorder=0)
ax.spines[["top","right"]].set_visible(False)
fig.supxlabel("Finite changes are not certified error bounds. Gas-path comparison combines knot-grid and stored-path changes.",fontsize=9,color="#495560")
fig.savefig(root/"figures/FIXED_GAS_FINITE_DIFFERENCES.png",dpi=180)
fig.savefig(root/"figures/FIXED_GAS_FINITE_DIFFERENCES.svg")
