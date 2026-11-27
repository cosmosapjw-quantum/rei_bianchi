#!/usr/bin/env python3
"""Plot saved exact width budgets. Display rounding only; no scientific solves."""
from pathlib import Path
from fractions import Fraction as F
import csv, gzip, hashlib, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root=Path(__file__).resolve().parent.parent
data=json.loads((root/"evidence/budget_control/EXEC01/RESULTS.json").read_text())
wanted={"P_final":[], "H_total_eV":[]}
with gzip.open(root/"evidence/budget_control/EXEC01/WIDTH_RANKINGS.csv.gz","rt",newline="") as stream:
    for row in csv.DictReader(stream):
        if row["mode"]=="OFF" and row["kind"]=="absolute" and row["quantity"] in wanted:
            wanted[row["quantity"]].append((int(row["node"]),F(row["hybrid_width_exact"])))
curves={}
for metric, rows in wanted.items():
    rows.sort(key=lambda x:(-x[1],x[0]))
    total=sum((w for _,w in rows),F(0));acc=F(0);curve=[]
    for _,w in rows:
        acc+=w;curve.append(float(100*acc/total))
    curves[metric]=curve

plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                     "axes.spines.right":False,"svg.fonttype":"none"})
fig,(a,b)=plt.subplots(1,2,figsize=(11.8,4.9),gridspec_kw={"width_ratios":[1,1.25]})
colors={"P_final":"#245F9C","H_total_eV":"#BA5A2D"}
labels={"P_final":"Final photon stock","H_total_eV":"Heat (sum of species)"}
for metric in wanted:
    d=data["budgets_by_mode"]["OFF"]["absolute"][metric]
    width=d["width"]
    old_two=100*F(width["further_K2_max_gain_at_zero_width"])/F(width["hybrid_full"])
    top2=100*F(d["concentration"]["hybrid"]["top_width_fractions"]["2"])
    top100=100*F(d["concentration"]["hybrid"]["top_width_fractions"]["100"])
    offset=-0.13 if metric=="P_final" else 0.13
    vals=[float(old_two),float(top2),float(top100)]
    a.scatter(vals,np.arange(3)+offset,s=55,color=colors[metric],label=labels[metric],zorder=3)
    for i,val in enumerate(vals):
        a.annotate(f"{val:.6g}%",(val,i+offset),xytext=(6,0),textcoords="offset points",
                   va="center",fontsize=8.5,color=colors[metric])
    b.plot(np.arange(1,2441),curves[metric],color=colors[metric],lw=2.4,label=labels[metric])
    b.scatter([100],[curves[metric][99]],color=colors[metric],s=32,zorder=4)
    b.annotate(f'{curves[metric][99]:.2f}%',(100,curves[metric][99]),xytext=(6,6 if metric=="P_final" else -14),
               textcoords="offset points",color=colors[metric],fontsize=9)
a.set_xscale("log");a.set_xlim(4e-6,160);a.set_yticks([0,1,2],["Current OFF 0 + 700","Largest 2 contributors","Largest 100 contributors"])
a.set_xticks([1e-5,1e-3,1e-1,10,100],["0.00001","0.001","0.1","10","100"])
a.invert_yaxis();a.set_xlabel("Maximum removable share of current width (%)")
a.set_title("A. Bounds on further improvement",loc="left",fontweight="bold",pad=15)
a.grid(axis="x",alpha=.18)
b.set_xscale("log");b.set_xlim(1,2440);b.set_ylim(0,101)
b.set_xticks([1,2,10,100,1000,2440],["1","2","10","100","1000","2440"])
b.set_xlabel("Number of largest contributors retained")
b.set_ylabel("Cumulative share of current interval width (%)")
b.axvline(100,color="#888888",lw=.8,ls=":",zorder=0);b.grid(alpha=.18)
b.set_title("B. Width spread across the finite grid",loc="left",fontweight="bold",pad=15)
b.legend(frameon=False,loc="upper left",fontsize=9)
fig.suptitle("BASS_HE: the full finite budget shifts beyond the two refined OFF paths",
             x=.03,y=.995,ha="left",fontsize=13,fontweight="bold")
fig.text(.03,.025,"Fixed captured model; exact per-path interval sums. Curves are width budgets, not probabilities.\n"
         "Panel A assumes selected widths could reach zero; it is an upper bound, not a forecast of an N512 run.",
         fontsize=9,color="#444444")
fig.subplots_adjust(left=.18,right=.98,bottom=.23,top=.85,wspace=.47)
for ext in ("png","svg"):
    fig.savefig(root/("figures/FULL_FINITE_WIDTH_BUDGET."+ext),dpi=190,bbox_inches="tight",
                metadata={"Creator":"BASS_HE saved-result budget postprocessing"})
evidence={"source":"evidence/budget_control/EXEC01/RESULTS.json",
          "rankings_sha256":data["ranking_artifact"]["sha256"],
          "quantity_definitions":{"P_final":"Final absolute photon stock; captured normalization.",
                                  "H_total_eV":"Absolute heat intervals summed across species and paths."},
          "plotted_series":{k:{"nodes":2440,"top2_percent":v[1],"top100_percent":v[99],"all_percent":v[-1]} for k,v in curves.items()},
          "new_physics_runs":0}
(root/"figures/FIGURE_DATA.json").write_text(json.dumps(evidence,indent=2)+"\n")

