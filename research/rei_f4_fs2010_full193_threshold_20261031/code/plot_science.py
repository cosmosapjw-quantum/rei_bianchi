#!/usr/bin/env python3
"""Six original physical-data figures from complete BASS193 first-flight threshold response."""
from pathlib import Path
import json,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];D=pd.read_csv(ROOT/'results'/'FS2010_FULL193_ARRIVAL_192.csv')
T=pd.read_csv(ROOT/'results'/'FS2010_FULL193_HHE_TERMINAL_THERMAL_192.csv')
P=json.loads((ROOT/'results'/'RESULT.json').read_text())['physics']
O=ROOT/'results';z=D.z_high.to_numpy()
B=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus'];G=['H_I','He_I','He_II','Li_I']
def save(name,reverse=True):
 if reverse:plt.gca().invert_xaxis();plt.xlabel('Original BASS193 redshift z')
 plt.grid(alpha=.2);plt.tight_layout()
 plt.savefig(O/name,dpi=150,metadata={'Software':'REI_F4_FS2010_FULL193_ORIGINAL_FROZEN_SOURCE'})
 plt.close()
# physical stored primary energies per baryon
plt.figure(figsize=(9,4.8));plt.plot(z,np.cumsum(D.FS_low_e_heat_kinematic_eV_per_b),label='Terminal E<10.2 eV model heat')
plt.plot(z,np.cumsum(D.total_primary_e_eV_per_b),label='All primary electron kinetic energy')
plt.ylabel('Cumulative energy [eV/baryon]');plt.legend();plt.title('Complete 193-source Li II 2E1 first absorption');save('FIG01_FULL193_TERMINAL_ENERGY.png')
plt.figure(figsize=(9,4.8));energy=[P['primary_electron_energy_by_bin_eV_per_baryon'][b] for b in B]
plt.bar(['0–10.2','10.2–13.6','13.6–24.59','24.59–54.42','≥54.42'],energy)
plt.ylabel('Primary electron energy [eV/baryon]');plt.title('Kinetic-energy partition of full first-flight source');save('FIG02_FULL193_ENERGY_BANDS.png',False)
plt.figure(figsize=(9,4.8));plt.plot(z,np.cumsum(D.FS_sub_excitation_primary_count_per_b),label='E<10.2 eV')
plt.plot(z,np.cumsum(D.FS_excitation_no_ionization_count_per_b),label='10.2≤E<13.6 eV')
plt.plot(z,np.cumsum(D.FS_H_secondary_ionization_energetic_count_per_b),label='E≥13.6 eV')
plt.ylabel('Cumulative electron events / baryon');plt.title('Actual energy-threshold-resolved primary electrons');plt.legend();save('FIG03_FULL193_PHOTOELECTRON_COUNTS.png')
plt.figure(figsize=(9,4.8))
tr=T.FS_model_terminal_temperature_rhs_coefficient_K_s.to_numpy()
plt.plot(z,np.where(tr>0,tr,np.nan),label='Idealized terminal-only dT/dt coefficient')
plt.yscale('log');plt.ylabel('Thermal source coefficient [K/s]')
plt.legend();plt.title('Frozen HHe EOS response to FS-model E<10.2 eV energy');save('FIG04_FULL193_THERMAL_PORT.png')
plt.figure(figsize=(9,4.8));c=[P['species_first_absorption_counts_per_baryon'][g] for g in G]
plt.bar(['H I','He I','He II','Li I'],c);plt.yscale('log');plt.ylabel('First photoabsorption / baryon')
plt.title('193-source first-absorption state inventory');save('FIG05_FULL193_ABSORBERS.png',False)
plt.figure(figsize=(9,4.8));old=4.963249567403269e-12;prev=2.953300056205549e-12;current=P['secondary_H_I_event_discrete_safe_ceiling_per_baryon']
plt.bar(['Old E/χ','Previous 30-epoch\nupper bound','Full 193-epoch\nupper bound'],[old,prev,current])
plt.ylabel('Possible H I collision-ionization events / baryon')
plt.title('Stronger source-complete kinematic secondary ceiling (not a yield)');save('FIG06_FULL193_SECONDARY_BOUND.png',False)
print('SIX_FIGURES',len(list(O.glob('FIG0*_FULL193_*.png'))))
