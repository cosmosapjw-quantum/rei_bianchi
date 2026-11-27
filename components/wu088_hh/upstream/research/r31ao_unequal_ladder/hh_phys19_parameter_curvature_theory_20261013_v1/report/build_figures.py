#!/usr/bin/env python3
"""Display certified interval formulae; no physical-function sample is generated."""
from pathlib import Path
import json, hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
source=HERE.parent/"checks/application/readout02/results/CURVATURE_GEOMETRY.json"
r=json.loads(source.read_text())
def dec(x): return [float(v) for v in x["outward_decimal"]]
A=dec(r["hessian"]["lambda_lambda_K"])
D=dec(r["hessian"]["b_b_K"])
M=dec(r["hessian"]["lambda_b_K"])
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,
 "axes.spines.top":False,"axes.spines.right":False,"axes.labelcolor":"#253a50",
 "text.color":"#253a50","axes.edgecolor":"#64748b","savefig.facecolor":"white"})

fig,ax=plt.subplots(figsize=(8.8,3.5),layout="constrained")
s=np.linspace(0,0.10,501)
lo=A[0]-2*s*M[1]+s*s*D[0]
hi=A[1]-2*s*M[0]+s*s*D[1]
ax.fill_between(s,lo/1e-13,hi/1e-13,color="#c6dbe9",label="Certified Hessian enclosure")
ax.plot(s,lo/1e-13,color="#236583",lw=1.2)
ax.plot(s,hi/1e-13,color="#236583",lw=1.2)
ax.axhline(0,color="#334155",lw=.8)
ax.axvline(1/24,color="#ad5427",ls="--",lw=1.2)
ax.text(1/24+0.001,0.13,r"$r=1/24$",color="#ad5427")
ax.set(xlabel=r"Opposite parameter direction $(1,-r)$: slope $r$",
 ylabel=r"Directional curvature / $10^{-13}$ K",xlim=(0,.1))
ax.legend(frameon=False,loc="upper right",fontsize=9)
fig.savefig(HERE/"figures/hessian_directions.png",dpi=220)
fig.savefig(HERE/"figures/hessian_directions.svg")
plt.close(fig)

fig,(ax,bx)=plt.subplots(1,2,figsize=(9.6,3.35),layout="constrained",
 gridspec_kw={"width_ratios":[1.45,1]})
b=np.linspace(0,1,401)
el=-A[1]/8-D[1]*b*(1-b)/2
eu=-A[0]/8-D[0]*b*(1-b)/2
ax.fill_between(b,el*1e12,eu*1e12,color="#c6dbe9")
ax.plot(b,el*1e12,color="#236583",lw=1.1)
ax.plot(b,eu*1e12,color="#236583",lw=1.1)
ax.set(xlabel=r"Birth amplitude $b$ (at $\lambda=1/2$)",
 ylabel=r"$F-\mathcal{L}F$ enclosure / $10^{-12}$ K",xlim=(0,1),ylim=(0,6.65))
vals=[dec(r["interpolation"]["bilinear_abs_bound_K"])[1]*1e12,
      dec(r["interpolation"]["pure_midpoint_abs_bound_K"])[1]*1e12]
bars=bx.bar([0,1],vals,color=["#236583","#ad5427"],width=.55)
bx.set(xticks=[0,1],xticklabels=["Bilinear","Curvature\ncorrected"],
 ylabel=r"Uniform error bound / $10^{-12}$ K",ylim=(0,7))
for bar,val in zip(bars,vals):
 bx.text(bar.get_x()+bar.get_width()/2,val+.14,f"{val:.4f}",ha="center",fontsize=10)
bx.text(.5,5.6,"21.24× smaller bound",ha="center",color="#ad5427",fontsize=10)
fig.savefig(HERE/"figures/interpolation_error.png",dpi=220)
fig.savefig(HERE/"figures/interpolation_error.svg")
plt.close(fig)
meta={"source":str(source.relative_to(HERE.parent)),"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
 "meaning":"Plots of certified interval formulae, using outward decimal endpoints as display inputs; no source, root, history, or F samples.",
 "figures":["hessian_directions.png","hessian_directions.svg","interpolation_error.png","interpolation_error.svg"]}
(HERE/"figures/PROVENANCE.json").write_text(json.dumps(meta,indent=2)+"\n")
