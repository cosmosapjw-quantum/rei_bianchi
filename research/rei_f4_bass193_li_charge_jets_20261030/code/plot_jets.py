from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'results'/'NATIVE_193_LI_CHARGE_JET_ROWS.csv').open()))
z=np.array([float(r['z']) for r in rows]); a=np.array([float(r['det_frozen']) for r in rows]);b=np.array([float(r['det_nonautonomous']) for r in rows]);
fig,ax=plt.subplots(figsize=(10,5));ax.plot(z,a,label='Frozen-rate 2-jet determinant',lw=1.7);ax.plot(z,b,label='Nonautonomous source 2-jet determinant',lw=1.7);ax.axhline(0,color='k',lw=.8);ax.set_xlim(20,2);ax.set_xlabel('Saved BASS redshift z (original 193 epochs)');ax.set_ylabel('Dimensionless charge-jet determinant');ax.legend();fig.tight_layout();fig.savefig(ROOT/'results'/'LI_CHARGE_JET_DETERMINANT.png',dpi=145);fig.savefig(ROOT/'results'/'LI_CHARGE_JET_DETERMINANT.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4));m=np.array([abs(float(r['delta_electron_source_per_baryon_s'])) for r in rows]);ax.semilogy(z,np.maximum(m,1e-60),label='Electron-source sensitivity to positive q-neutral Li6 perturbation');ax.set_xlim(20,2);ax.set_xlabel('Saved BASS redshift z');ax.set_ylabel('Absolute electron source / baryon / s');ax.legend();fig.tight_layout();fig.savefig(ROOT/'results'/'LI_CHARGE_BLIND_ELECTRON_SOURCE.png',dpi=145);plt.close(fig)
print('WROTE_PLOTS',len(z))
