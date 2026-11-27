#!/usr/bin/env python3
"""Plot ONLY source-owned and source-conditional 1965/1966 physics.
No invented target-frame photon density or plasma deposition plotted.
"""
from pathlib import Path
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/"results/SCIENTIFIC_RESULT.json").read_text())
plt.rcParams.update({"font.size":11})
fig,ax=plt.subplots(figsize=(8.5,5.8))
for target in ("H","He"):
    rows=sorted((r for r in json.loads((ROOT/"inputs/SOURCE_DATA.json").read_text())["cea"]["records"] if r["target"]==target),key=lambda x:x["E_MeV"])
    ax.plot([r["E_MeV"] for r in rows],[r["mass_stopping_MeV_cm2_g"] for r in rows],marker='o',label=f"CEA 1966 D on elemental {target} (calculated)")
for E in sorted({r["K_birth_MeV"] for r in d["daughter_bridge"]}):
    ax.axvline(E,linestyle=":",alpha=.35)
ax.set(xlabel="Deuteron kinetic energy [MeV]",ylabel="Mass stopping power [MeV cm² g⁻¹]",title="CEA-1966 elemental D stopping and Asbury nominal daughters")
ax.grid(alpha=.23);ax.legend(fontsize=8);fig.tight_layout()
for ext in ("png","svg"):fig.savefig(ROOT/"figures"/f"CEA_D_H_HE_STOPPING.{ext}",dpi=170)
plt.close(fig)

fig,ax=plt.subplots(figsize=(8.5,5.7))
rows=d["measured"]
ax.errorbar([x["Egamma_MeV"] for x in rows],[x["DA_nb_sr"] for x in rows],yerr=[x["DA_stat_plus_systematic_nb_sr"] for x in rows],
             fmt="o",capsize=5,label="1965 measured differential DA (nb/sr)")
ax.set(xlabel="Mean photon energy in alpha rest frame [MeV]",ylabel="Measured dσ/dΩ at experiment theta_cm [nb/sr]",
       title="Asbury & Loeffler 1965: two measured DA, one experiment")
for x in rows:
    ax.annotate(f'{x["theta_cm_deg"]}° CM',(x["Egamma_MeV"],x["DA_nb_sr"]),xytext=(7,8),textcoords="offset points")
ax.set_xlim(203,285);ax.set_ylim(0,10);ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout()
for ext in ("png","svg"):fig.savefig(ROOT/"figures"/f"ASBURY1965_MEASURED_DA.{ext}",dpi=170)
plt.close(fig)
print("PLOT source_owned 2x png + 2x svg, no plasma model")
