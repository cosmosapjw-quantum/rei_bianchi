"""Plot saved scientific data only. Never integrates a photon history."""
import csv, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=pathlib.Path(__file__).resolve().parents[1]
with (P/'results/M1_ABSORPTION_EPOCH_193.csv').open() as f:R=list(csv.DictReader(f))
z=np.array([float(r['z']) for r in R]);tau=np.array([float(r['tau_one_frozen_Hubble_length']) for r in R]);
fig,ax=plt.subplots(figsize=(7,4.5));ax.semilogy(z,tau,label=r'$c\kappa_{\rm photo}/H$');ax.axhline(1,linestyle='--',label='unity (local)')
ax.set(xlabel='Original BASS saved redshift z',ylabel='Frozen local attenuation index',title='59.0207 eV Li II M1 photoabsorption')
ax.legend();fig.tight_layout();fig.savefig(P/'results/M1_LOCAL_TAUH_193.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
for ch in ('H_I','He_I','He_II','Li_I'):
 ax.plot(z,[float(r['first_photoabsorption_'+ch+'_fraction']) for r in R],label=ch.replace('_',' '))
ax.set(xlabel='Original BASS saved redshift z',ylabel='Conditional first photoabsorption fraction',ylim=(0,1.025),title='Native 59.0207 eV photon absorber branching')
ax.legend();fig.tight_layout();fig.savefig(P/'results/M1_ABSORBER_BRANCH_193.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5));ax.plot(z,[float(r['mean_primary_photoelectron_eV']) for r in R],label='Initial electron')
ax.plot(z,[float(r['mean_ion_binding_eV']) for r in R],label='Ionization threshold')
ax.set(xlabel='Original BASS saved redshift z',ylabel='Conditional energy / absorbed photon [eV]',title='Original BASS one-electron threshold ledger')
ax.legend();fig.tight_layout();fig.savefig(P/'results/M1_PHOTOELECTRON_ENERGY_193.png',dpi=170);plt.close(fig)
print('FIGURES=3 | 193 input rows | NO_IVP')
