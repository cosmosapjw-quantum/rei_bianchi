import csv, pathlib, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1]
with (ROOT/'results/FERRETT_TABLE_IV_EXPERIMENT.csv').open() as f: t=list(csv.DictReader(f))
energy=np.array([float(x['E_eV']) for x in t]);a=np.array([float(x['ratio_triplet_1s2s_to_measured_core']) for x in t]);b=np.array([float(x['ratio_singlet_1s2s_upper_to_measured_core']) for x in t]);c=np.array([float(x['ratio_n3_satellite_to_measured_core']) for x in t])
fig,ax=plt.subplots(figsize=(8,4.5));ax.plot(energy,a,'o-',label='measured triplet 1s2s 3S ratio');ax.plot(energy,b,'s-',label='singlet 1s2s upper (unresolved + 3P)');ax.plot(energy,c,'^-',label='n=3 satellite ratio');ax.axvline(92.5,linestyle='--',label='higher-E author model beyond 92.5 eV');ax.set(xlabel='incident photon energy [eV]',ylabel='relative to tabulated n2 + n3 channels',ylim=(0,0.8));ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'results/FERRETT_BRANCH_FRACTIONS.png',dpi=155);plt.close(fig)
with (ROOT/'results/FERRETT_BASS_EPOCH_193.csv').open() as f: e=list(csv.DictReader(f))
z=np.array([float(v['z']) for v in e]);v1=np.array([float(v['triplet_weighted_rate']) for v in e]);v2=np.array([float(v['singlet_upper_weighted_rate']) for v in e]);
fig,ax=plt.subplots(figsize=(8,4.5));ax.semilogy(z,np.maximum(v1,1e-90),label='BASS K events x measured triplet ratio');ax.semilogy(z,np.maximum(v2,1e-90),label='BASS K events x singlet upper');ax.set(xlabel='archived redshift z',ylabel='conditional native rates [baryon$^{-1}$ s$^{-1}$]',xlim=(20,2));ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'results/FERRETT_BASS193_RATE_HISTORY.png',dpi=155);plt.close(fig)
