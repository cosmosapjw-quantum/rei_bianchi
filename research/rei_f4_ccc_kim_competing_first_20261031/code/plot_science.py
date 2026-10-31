#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.hashsalt']='REI_F4_CCC_KIM_COMPETING_FIRST_20261031'
R=Path(__file__).resolve().parents[1]
a=pd.read_csv(R/'results/ORIGINAL_BASS193_FIRST_EVENT_SPECTRUM.csv')
b=pd.read_csv(R/'results/FIRST_EVENT_ARRIVAL_192.csv')
out=R/'figures';out.mkdir(exist_ok=True)
Emax=a.initial_E_eV.max()
q=a[np.isclose(a.initial_E_eV,Emax)].sort_values('z')
fig,ax=plt.subplots(figsize=(9,5))
for key,label in [('CCC6_first_total','CCC six-channel first event'),('CCC6_first_HI_ion','CCC H I first ionization'),('CCC6_first_HI_exc_n2','CCC H I first n=2 excitation'),('Kim3_first_ion_total','Kim92 ionization-only')]:
 ax.plot(q.z,q[key],label=label)
ax.set_yscale('log');ax.set_ylim(1e-10,2);ax.set_xlabel('Saved BASS193 redshift z');ax.set_ylabel('First-event probability before 13.7 eV');ax.legend(fontsize=8);ax.grid(alpha=0.2)
fig.tight_layout();fig.savefig(out/'FIRST_EVENT_VS_Z.png',dpi=150);fig.savefig(out/'FIRST_EVENT_VS_Z.svg', metadata={'Date':None});plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
sel=b[b.source_photoelectron_N_per_b>0].sort_values('z')
ax.plot(sel.z,sel.CCC6_first_total_mean_per_b,label='CCC6 mean-energy collocation')
ax.fill_between(sel.z,sel.CCC6_first_total_lower_per_b,sel.CCC6_first_total_upper_per_b,alpha=.22,label='Same source N,M envelope')
ax.plot(sel.z,sel.Kim3_first_ion_total_mean_per_b,label='Kim92 ionization-only')
ax.set_xlabel('Source arrival redshift z');ax.set_ylabel('Source-weighted first event / original baryon');ax.set_yscale('log');ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(out/'FIRST_EVENT_SOURCE_192.png',dpi=150);fig.savefig(out/'FIRST_EVENT_SOURCE_192.svg', metadata={'Date':None});plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
for key,label in [('CCC6_Coulomb_loss_before_first_eV','Continuous Coulomb loss before first event/cutoff'),('CCC6_first_event_energy_eV','Electron kinetic energy at first event')]:
 ax.plot(q.z,q[key],label=label)
ax.plot(q.z,13.7*q.CCC6_survivor_to_13p7,label='Unresolved electron energy at 13.7 eV cutoff')
ax.axhline(Emax,linestyle=':',label='Input electron kinetic energy')
ax.set_xlabel('Saved BASS193 redshift z');ax.set_ylabel('eV per initial electron (E0 = 60.92256 eV)')
ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(out/'FIRST_EVENT_ENERGY_LEDGER.png',dpi=150);fig.savefig(out/'FIRST_EVENT_ENERGY_LEDGER.svg', metadata={'Date':None});plt.close(fig)
print('PHYSICAL_PLOTS=3PNG_3SVG')
