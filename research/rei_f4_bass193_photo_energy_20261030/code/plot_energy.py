from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
with open(ROOT/'results/PHOTO_ENERGY_193_EPOCHS.csv') as f: rows=list(csv.DictReader(f))
z=np.array([float(q['z']) for q in rows]); y={name:np.array([float(q[name]) for q in rows]) for name in ['absorption_eV_per_baryon_s','ionization_threshold_eV_per_baryon_s','primary_electron_eV_per_baryon_s','unresolved_core_eV_per_baryon_s']}
fig,ax=plt.subplots(figsize=(8,4.9))
for k,name in [('absorption_eV_per_baryon_s','Absorbed photon energy'),('ionization_threshold_eV_per_baryon_s','Ionization threshold'),('primary_electron_eV_per_baryon_s','Primary electron energy')]:ax.semilogy(z,y[k],lw=1.8,label=name)
ax.set(xlabel='Redshift z (original BASS saved history)',ylabel='Source energy [eV baryon$^{-1}$ s$^{-1}$]',title='BASS21 source-owned photon energy ledger (no new IVP)')
ax.legend(fontsize=8);ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(ROOT/'results/photo_energy_by_redshift.png',dpi=165);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4.9))
ax.semilogy(z,np.maximum(y['unresolved_core_eV_per_baryon_s'],1e-50),lw=1.7)
ax.set(xlabel='Redshift z',ylabel='Li I unresolved-core source [eV baryon$^{-1}$ s$^{-1}$]',title='Source-only Li 1s unresolved energy (not deposited heat)')
ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(ROOT/'results/li1s_unresolved_core_energy.png',dpi=165);plt.close(fig)
print('Two saved-data plots written')
