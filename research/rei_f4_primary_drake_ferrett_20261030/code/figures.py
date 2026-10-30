from pathlib import Path
import csv
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
with (R/'LAB_FERRETT_TABLEIV_13.csv').open() as f: labs=list(csv.DictReader(f))
E=np.array([float(r['energy_eV']) for r in labs]);
fig,ax=plt.subplots(figsize=(7.3,4.6))
for name,label in [('sigma_n2_Mb','measured n=2'),('sigma_1s2s_3S_Mb','measured Li+ 1s2s 3S'),('sigma_unresolved_1S_plus_3P_Mb','measured unresolved 1S+3P')]:
 ax.plot(E,[float(r[name]) for r in labs],marker='.',label=label)
ax.set(xlabel='Photon energy (eV)',ylabel='Photoionization partial cross-section (Mb)',title='Ferrett et al. (1987), printed Table IV (absolute scale systematic 20%)')
ax.legend(fontsize=8);fig.tight_layout();fig.savefig(R/'FERRETT_MEASURED_PARTIALS.png',dpi=180);plt.close(fig)
with (R/'BASS_EPOCH_SPIN_193.csv').open() as f: epoch=list(csv.DictReader(f))
z=np.array([float(r['z']) for r in epoch]);
fig,ax=plt.subplots(figsize=(7.3,4.6))
for k,label in [('K_75_99_per_baryon_s','Original K, Ferrett 75-99 eV'),('K_80_99_per_baryon_s','Original K, 80-99 eV'),('triplet3S_n2n3_per_baryon_s','3S conditional n2+n3 normalization'),('singlet1S_upper_n2n3_per_baryon_s','1S bound conditional n2+n3')]:
 ax.semilogy(z,np.maximum([float(r[k]) for r in epoch],1e-42),label=label)
ax.set(xlabel='Original BASS saved redshift z',ylabel='Rate per baryon per second',title='Measured-energy-window Li 1s spin source response, conditional K normalization')
ax.legend(fontsize=7);fig.tight_layout();fig.savefig(R/'BASS_FERRETT_SPIN_WINDOW_193.png',dpi=180);plt.close(fig)
print('PLOTS_2_READY')
