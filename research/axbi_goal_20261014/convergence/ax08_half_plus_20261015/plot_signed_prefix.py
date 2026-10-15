#!/usr/bin/env python3
"""Chronologically matched AX08 signed partial-history morphology, no admission."""
import importlib.util
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("signed_prefix_parity",HERE/"signed_prefix_parity.py")
s=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(s)
allcases={k:s.load_case(k,v) for k,v in s.REL.items()}
a0=1/21
a1=min(d["last_a"] for d in allcases.values())
agrid=np.exp(np.linspace(math.log(a0),math.log(a1),501))
agrid[0]=a0;agrid[-1]=a1
z=1/agrid-1
values={}
for k,v in allcases.items():
    a=v["arr"][:,0]
    values[k]=[np.interp(agrid,a,v["arr"][:,j]) for j in (1,2,3)]
parts={}
for j,name in enumerate(s.COLUMNS[1:]):
    zero=values["ZERO"][j]
    p=values["SHEAR_PLUS"][j];m=values["SHEAR_MINUS"][j]
    hp=values["SHEAR_HALF_PLUS"][j];hm=values["SHEAR_HALF_MINUS"][j]
    parts[name]={"even_large":.5*(p+m)-zero,
                 "odd_large":.5*(p-m),
                 "even_half":.5*(hp+hm)-zero,
                 "odd_half":.5*(hp-hm)}
fig,axes=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
settings=[
    (0,0,"x_HII","even","HII even [number fraction]"),
    (0,1,"temperature_K","even","Tgas even [K]"),
    (1,0,"J2_photon_u_eV_per_H","odd","J2 odd [eV/H]"),
    (1,1,"x_HII","odd","HII odd [number fraction]")
]
for i,j,name,k,label in settings:
    ax=axes[i,j]
    ax.plot(z,parts[name][k+"_large"],label="q=0.01")
    ax.plot(z,parts[name][k+"_half"],linestyle="--",label="q=0.005")
    ax.axhline(0,color="gray",lw=.8)
    if i==0 and j==1:
        for sign in (1,-1):
            ax.axhline(sign*.01,color="gray",lw=.6,linestyle=":")
    ax.set_xlabel("Common mean redshift zbar")
    ax.set_ylabel(label)
    ax.invert_xaxis()
    ax.legend(fontsize=8)
fig.suptitle("AX08 original five-case signed PREFIX, zbar≈20→10.2693; no numerical error bound",fontsize=11)
fig.savefig(HERE/"signed_prefix_even_odd.png",dpi=175)
plt.close(fig)
print("SIGNED_PREFIX_ACTUAL_501_SAMPLED_PLOT_WRITTEN")
