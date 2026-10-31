"""Scientific plots from the original FS2010 tables and PR302/303 saved data."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from compute import ROOT,FS2010
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
D=pd.read_csv(ROOT/'results'/'FS2010_NATIVE_CROSSWALK_192.csv')
fs=FS2010()
# 1: original table dependence near threshold; plot only true interpolation results.
fig,ax=plt.subplots(figsize=(8,5))
e=np.linspace(10,64,250)
for xi in [1e-4,1e-3,1e-2,0.1,0.5,0.9]:
 y=fs.interp(e,xi)[:,1]
 ax.plot(e,y,label=f'$x_i={xi:g}$')
ax.set(xlabel='Electron kinetic energy $E_e$ (eV)',ylabel=r'$f_{\mathrm{heat}}(E_e,x_i)$',title='FS2010 author tables: low-energy heating response')
ax.set_ylim(0,1.02);ax.legend(ncol=2,fontsize=9);ax.grid(alpha=.3)
fig.tight_layout();fig.savefig(OUT/'PLOT01_FS2010_TRUE_LOWENERGY.png',dpi=160);plt.close(fig)
# 2: original 192 saved arrival energy budgets, valid domain only, not time evolution.
fig,ax=plt.subplots(figsize=(8,5))
z=D.z_low.to_numpy()
ax.plot(z,D.primary_kinetic_eV_per_b,label='Original primary electron energy')
ax.plot(z,D.terminal_eV_per_b,label='FS terminal E<10.2 eV')
valid=D.FS_xi_in_native_domain.to_numpy(bool)
ax.plot(z[valid],D.fheat_moment.to_numpy()[valid],label='FS 1-xi M1 closure (conditional)')
ax.fill_between(z[valid],D.fheat_lower.to_numpy()[valid],D.fheat_upper.to_numpy()[valid],alpha=.23,label='FS bilinear-envelope range')
ax.set_yscale('log');ax.set(xlabel='Arrival redshift $z$',ylabel='eV per original baryon per bin',title='Original 192-bin primary source and conditional FS response')
ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(OUT/'PLOT02_192_ARRIVAL_ENERGY_AND_FS_BOUNDS.png',dpi=160);plt.close(fig)
# 3: cumulative with x rising / z decreasing; exterior x>0.999 remains unassigned.
fig,ax=plt.subplots(figsize=(8,5))
ax.plot(z,np.cumsum(D.primary_kinetic_eV_per_b),label='All primary electron kinetic energy')
ax.plot(z,np.cumsum(D.terminal_eV_per_b),label='Sub-10.2 eV terminal convention')
ax.plot(z,np.cumsum(D.fheat_moment.where(D.FS_xi_in_native_domain,0)),label='FS surrogate M1 on valid $x_i$')
ax.fill_between(z,np.cumsum(D.fheat_lower.where(D.FS_xi_in_native_domain,0)),np.cumsum(D.fheat_upper.where(D.FS_xi_in_native_domain,0)),alpha=.22,label='Admissible within-band ranges')
ax.set(xlabel='Arrival redshift $z$ (decreasing forward)',ylabel='Cumulative eV per original baryon',title='Frozen-source energy-accounting integrals, not $T(t)$')
ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(OUT/'PLOT03_CUMULATIVE_CONDITIONAL_ENERGY.png',dpi=160);plt.close(fig)
# 4: source weights and FS chemical mismatch, not native F/J.
fig,ax=plt.subplots(figsize=(8,5))
co=pd.read_csv(ROOT/'input'/'BASS193_FS2010_SPECIES_COMPAT_192.csv')
ax.plot(z,co.xHII_end,label='$x_{HII}$')
ax.plot(z,co.xHeII_end,label='$x_{HeII}$')
ax.plot(z,co.xHeIII_end,label='$x_{HeIII}$')
ax.axhline(0.999,ls='--',lw=1,label='FS table upper ionization boundary')
ax.set(xlabel='Arrival redshift $z$',ylabel='Fraction (per element)',title='BASS193 chemistry != FS single-ionization-fraction model')
ax.grid(alpha=.3);ax.legend(fontsize=9)
fig.tight_layout();fig.savefig(OUT/'PLOT04_BASS_MULTI_ION_COMPATIBILITY.png',dpi=160);plt.close(fig)
print('SCIENCE_FIGURES=4')
