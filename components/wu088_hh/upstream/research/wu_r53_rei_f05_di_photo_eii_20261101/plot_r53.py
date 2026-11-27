#!/usr/bin/env python3
"""Optional visual inspection of real original REI R53 physical source outcomes."""
import csv,gzip
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
R=ROOT/"results"
P=ROOT/"plots"
P.mkdir(exist_ok=True)
def load(name,fields):
 with gzip.open(R/name,"rt") as f:
  c=csv.DictReader(f)
  rr=list(c)
  return {k:np.asarray([float(x[k]) for x in rr]) for k in fields}
base=load("R53_ORIGINAL_REI_F05_D_PHOTO_CX_46080.csv.gz",
 ["nH_cm3","source_T160_K","caseB_photo_y_final_neutral",
 "cx_only_R52_y_final_neutral"])
eii=load("R53_REI_F05_EII_SOURCE_SENSITIVITY_46080.csv.gz",
 ["caseB_withEII_neutral_y","EII_sink_over_original_native_F05_thermal_abs_neutral"])
ix=np.arange(0,len(base["nH_cm3"]),12)
fig,ax=plt.subplots(figsize=(8.4,5.2))
ax.scatter(base["nH_cm3"][ix],base["cx_only_R52_y_final_neutral"][ix],
 s=3,alpha=.37,label="R52 source CX only")
ax.scatter(base["nH_cm3"][ix],base["caseB_photo_y_final_neutral"][ix],
 s=3,alpha=.37,label="R53 CX + HI-cloned DI photo + case-B RR")
ax.scatter(base["nH_cm3"][ix],eii["caseB_withEII_neutral_y"][ix],
 s=3,alpha=.37,label="R53 plus native-H EII cloned to DI")
ax.set_xscale("log")
ax.set_xlabel("Original F05 proper nH (cm^-3)")
ax.set_ylabel("DI ionized fraction after one original tick, y0=0")
ax.set_title("46,080 real REI cells: source-conditional isotope transient")
ax.legend(fontsize=7);ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(P/"R53_ORIGINAL_REI_D_PHOTO_CX_EII_TRANSIENT.png",dpi=180)
plt.close(fig)
fig,ax=plt.subplots(figsize=(8.4,5.1))
ax.scatter(base["source_T160_K"][ix],100*abs(eii["EII_sink_over_original_native_F05_thermal_abs_neutral"][ix]),
s=4,alpha=.4,label="DI electron-impact threshold energy / |original F05 thermal increment|")
ax.axhline(1.,ls=":",label="1% native thermal materiality")
ax.set_xscale("log");ax.set_yscale("log")
ax.set_xlabel("Original F05 source T160 (K)")
ax.set_ylabel("Conditional DI EII threshold thermal sink / |native F05 ΔU| (%)")
ax.set_title("Original REI real-source DI electron-impact energy risk")
ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(P/"R53_REI_F05_DI_EII_ENERGY_MATERIALITY.png",dpi=180)
plt.close(fig)
print("REAL_SOURCE_PHYSICS_PLOTS_2")
if __name__=="__main__":pass
