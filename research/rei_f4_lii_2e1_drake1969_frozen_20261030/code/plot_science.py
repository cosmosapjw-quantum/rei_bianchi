#!/usr/bin/env python3
"""Scientific figures from validated source-owned 2E1 output (not transport)."""
import csv, pathlib, sys
import numpy as np
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import two_e1_source as s
out=ROOT/'figures';out.mkdir(exist_ok=True)
# Spectrum one figure per source-scientific concept.
y=np.linspace(0,.5,1001)
fig,ax=plt.subplots(figsize=(8.5,4.3))
ax.plot(y,np.interp(y,s.Y_TAB,s.A_TAB)/s.PAIR_NORM,linewidth=2,label='Drake et al. Li II 1969 Table II (linear interpolation)')
for group,chi in s.THRESH.items():
    yf=1-chi/s.E_SINGLET_EV if chi>s.E_SINGLET_EV/2 else chi/s.E_SINGLET_EV
    ax.axvline(yf,alpha=.6,ls='--',linewidth=1.2,label=f'{group} cutoff y={yf:.3f}')
ax.set(xlabel=r'Low-energy photon share $y=E_{\rm low}/\Delta E$',ylabel='Pair PDF per unit y',title='Source-calibrated Li II 1s2s singlet E1E1 pair spectrum')
ax.legend(fontsize=7,loc='upper left'); ax.grid(alpha=.24)
fig.tight_layout();fig.savefig(out/'LI_2E1_DRAKE1969_SPECTRUM.png',dpi=165);plt.close(fig)
with (ROOT/'results/LI_2E1_SOURCE_EPOCH_193.csv').open(newline='') as f:a=list(csv.DictReader(f))
z=np.array([float(x['z']) for x in a]);
for name,columns,ylabel in [('LI_2E1_FROZEN_FIRST_ABSORBER',[
 ('H I','conditional_all_singlet_2E1_absorption_H_I_per_baryon_s'),('He I','conditional_all_singlet_2E1_absorption_He_I_per_baryon_s'),('He II','conditional_all_singlet_2E1_absorption_He_II_per_baryon_s')],r'Conditional frozen local first absorption [baryon$^{-1}$ s$^{-1}$]'),
 ('LI_2E1_ENERGY_PARTITION',[
 ('primary electron','conditional_all_singlet_2E1_primary_electrons_eV_per_baryon_s'),('ionization binding','conditional_all_singlet_2E1_ion_binding_eV_per_baryon_s'),('unabsorbed photons','conditional_all_singlet_2E1_unabsorbed_photon_eV_per_baryon_s')],r'Conditional frozen energy rate [eV baryon$^{-1}$ s$^{-1}$]')]:
    fig,ax=plt.subplots(figsize=(8.5,4.3))
    for lbl,k in columns:
        v=np.array([float(x[k]) for x in a]);ax.plot(z,np.maximum(v,1e-68),label=lbl)
    ax.set(yscale='log',xlabel='Original BASS saved redshift z',ylabel=ylabel,title='Original 193-epoch BASS21, all-singlet conditional (NOT actual transport)')
    ax.invert_xaxis();ax.grid(alpha=.24);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/(name+'.png'),dpi=165);plt.close(fig)
print('source scientific figures:',[p.name for p in sorted(out.glob('*.png'))])
