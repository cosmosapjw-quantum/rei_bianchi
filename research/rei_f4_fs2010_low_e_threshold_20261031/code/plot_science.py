#!/usr/bin/env python3
"""Scientific figures for independently computed conditional energy-resolved source."""
from pathlib import Path
import numpy as np,pandas as pd,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'results';D=pd.read_csv(O/'FS2010_THRESHOLD_SELECTED_ARRIVAL_192.csv')
R=json.loads((O/'RESULT.json').read_text())['physics']
z=D.z_high.to_numpy()

def save(name):
 plt.grid(alpha=.2);plt.tight_layout();plt.savefig(O/name,dpi=150,metadata={'Software':'REI_F4_FS2010_THRESHOLD'});plt.close()

# 1: absolute bounded heating and absorbed energy on original causal redshift grid
plt.figure(figsize=(8.4,4.5))
plt.plot(z,np.cumsum(D.FS_low_e_heat_kinematic_eV_per_b),label='E_e < 10.2 eV: FS-model heat-assigned lower')
plt.plot(z,np.cumsum(D.total_primary_e_eV_per_b),label='All photoelectron kinetic energy, computed 30 epochs')
plt.gca().invert_xaxis();plt.xlabel('Redshift z');plt.ylabel('Cumulative eV / original baryon');plt.title('Threshold-classified original LiII 2E1 first-flight energy');plt.legend(fontsize=8);save('FIG01_ThresholdHeating_Cumulative.png')

# 2: energy partition by four kinematic bands and ultra-high tail
bands=['e0_10p2','e10p2_13p6','e13p6_24p59','e24p59_54p42','e54p42_plus']
labels=['<10.2','10.2–13.60','13.60–24.59','24.59–54.42','>=54.42']
vals=[sum(D[f'{g}_{s}_primary_e_eV_per_b'].sum() for g in ['H_I','He_I','He_II','Li_I']) for s in bands]
plt.figure(figsize=(8.4,4.5));plt.bar(labels,vals);plt.yscale('symlog',linthresh=1e-25)
plt.ylabel('Primary kinetic energy eV / baryon');plt.xlabel('Photoelectron kinetic energy bin [eV]');plt.title('Source-resolved primary-electron energy spectrum (5 physical bins)');save('FIG02_PrimaryEnergyBands.png')

# 3: interval counts and actual low-energy heat assignments (no 3 keV table)
plt.figure(figsize=(8.4,4.5))
plt.plot(z,np.cumsum(D.FS_sub_excitation_primary_count_per_b),label='photoelectrons E<10.2eV')
plt.plot(z,np.cumsum(D.FS_excitation_no_ionization_count_per_b),label='10.2<=E<13.598eV')
plt.plot(z,np.cumsum(D.FS_H_secondary_ionization_energetic_count_per_b),label='E>=13.598eV')
plt.gca().invert_xaxis();plt.xlabel('Redshift z');plt.ylabel('Cumulative first-absorption events / baryon');plt.title('Energy-resolved primary electrons from archived BASS source');plt.legend(fontsize=8);save('FIG03_ThresholdPhotoelectronCount.png')

# 4: source-weighted selection and omitted true owner remainder
sel=json.loads((ROOT/'evidence'/'SELECTION.json').read_text())
plt.figure(figsize=(8.4,4.5))
labels=['Included original source','Omitted source']
plt.bar(labels,[sel['coverage_fraction'],1-sel['coverage_fraction']]);plt.ylabel('Fraction of original LiII 2E1 pair source');plt.ylim(0,1.05)
plt.title('Source-mass adaptive evidence coverage: 30 / 193 emission epochs');save('FIG04_SourceCoverage.png')

# 5: corrected discrete energetic ionization ceiling
plt.figure(figsize=(8.4,4.5))
labels=['Primary H/He photons','New discrete sec. cap','Old relaxed E/chi bound']
vals=[R['PR297_total_absorbed_events_per_b'],R['global_discrete_H_ionization_secondary_ceiling_per_b'],R['global_continuous_secondary_ceiling_PR297_per_b']]
plt.bar(labels,vals);plt.ylabel('Events / original baryon');plt.title('New photoelectron-by-photoelectron secondary H ionization ceiling');save('FIG05_SecondaryBoundTightening.png')

# 6: source denominator conservation by absorber
plt.figure(figsize=(8.4,4.5))
counts=[sum(D[f'{g}_{s}_counts_per_b'].sum() for s in bands) for g in ['H_I','He_I','He_II','Li_I']]
plt.bar(['H I','He I','He II','Li I'],counts);plt.yscale('log');plt.ylabel('First photoabsorption count / baryon');plt.title('Independent PR287 source reproduction in resolved energy bins');save('FIG06_AbsorberInventory.png')
print('PLOTS=6')
