from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"results/REMAP_OPACITY_EXACT_V1.json").read_text())
cols=data["signed_column_contributions"]
parts=[float(cols[0]["weighted_opacity_defect"]["midpoint_decimal"]),
       float(cols[1]["weighted_opacity_defect"]["midpoint_decimal"]),
       sum(float(x["weighted_opacity_defect"]["midpoint_decimal"]) for x in cols[2:])]
total=float(data["functionals"]["HI_opacity"]["defect_two_minus_full"]["midpoint_decimal"])
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"svg.hashsalt":"HH_PHYS04_REMAP_V1"})
fig,ax=plt.subplots(figsize=(9,4.8),layout="constrained")
values=parts+[total]
colors=["#23787d","#a84343","#23787d","#334b73"]
bars=ax.bar(range(4),[x/1e-24 for x in values],color=colors,width=.60)
ax.axhline(0,color="#454545",linewidth=.8)
ax.set_xticks(range(4),["Threshold node 16\n13.6000 eV","Neighbor node 17\n13.6125 eV",
                       "Nodes 18–24\ncombined","Spectrum sum"])
ax.set_ylabel(r"Two-half minus full opacity weight  [$10^{-24}$ cm$^2$ photons/H]")
ax.set_title("Signed remap contributions cancel across the cutoff",loc="left",fontweight="bold",pad=17)
ax.set_ylim(-1.5,1.5)
for bar,value in zip(bars,values):
    height=value/1e-24
    label=f"{value:+.6e}"
    ax.annotate(label,(bar.get_x()+bar.get_width()/2,height),
                xytext=(0,9 if height>=0 else -17),textcoords="offset points",
                ha="center",fontsize=10,color="#242424")
ax.spines[["top","right"]].set_visible(False)
ax.grid(axis="y",alpha=.18)
ax.set_axisbelow(True)
fig.text(.02,-.05,"Selected 25-group preBE spectrum; FLRW H=10⁻¹⁴ s⁻¹, h=1.25×10⁹ s.\n"
                  "Pure remap operator diagnostic. No BE evolution or finite gas-error claim.",
         fontsize=9,color="#4b4b4b")
(ROOT/"figures").mkdir(exist_ok=True)
fig.savefig(ROOT/"figures/remap_opacity_contributions.svg",metadata={"Date":None},bbox_inches="tight")
out=ROOT.parent/"delivery";out.mkdir(exist_ok=True)
fig.savefig(out/"WU088_HH_PHYS04_REMAP_OPACITY.png",dpi=170,bbox_inches="tight")
print("Figure written from stored exact-result summaries; no scientific recomputation.")
