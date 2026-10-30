#!/usr/bin/env python3
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
D=pd.read_csv(OUT/'LI2E1_HHE_CAUSAL_SOURCE_192.csv')
R=json.loads((OUT/'RESULT.json').read_text())['physical_outputs']
z=D.z_high.to_numpy()

def save(name):
    plt.xlabel('Redshift z (original BASS193 intervals)');plt.gca().invert_xaxis()
    plt.grid(alpha=.2);plt.tight_layout()
    plt.savefig(OUT/name,dpi=150,metadata={'Software':'REI F4 source-bound science'})
    plt.close()

plt.figure(figsize=(8.4,4.5))
for c,s in [('directwindow_LiII_2E1_HI_counts_upper_per_b','H I'),('directwindow_LiII_2E1_HeI_counts_upper_per_b','He I'),('directwindow_LiII_2E1_HeII_counts_upper_per_b','He II')]:
 x=D[c].to_numpy();plt.plot(z,np.where(x>0,x,np.nan),label=s)
plt.yscale('log');plt.ylabel('Conditional absorbed photons / baryon / interval');plt.title('Measured-window upper: 2E1 causal H/He first absorption');plt.legend();save('PLOT01_CAUSAL_ABSORPTION_CHANNELS.png')

plt.figure(figsize=(8.4,4.5))
a=D.conditional_primary_upper_erg_per_Href_s.to_numpy();b=D.native_BASS_original_HHe_photoheat_erg_per_Href_s.to_numpy()
plt.plot(z,np.where(a>0,a,np.nan),label='LiII 2E1 primary electron cap')
plt.plot(z,np.where(b>0,b,np.nan),label='Original BASS photon primary heat (REI point input)')
plt.yscale('log');plt.ylabel('Primary kinetic power [erg / Href / s]');plt.title('Source-scale separation: conditional secondary line vs original UV');plt.legend(fontsize=8);save('PLOT02_ENERGY_PORT_SCALE.png')

plt.figure(figsize=(8.4,4.5))
for key,label in [('delta_Tdot_primary_K_s_if_all_primary_to_heat_upper','Unit-deposition heating upper coefficient'),('delta_Tdot_HHe_electron_loading_K_s','Electron loading, primary only'),('delta_Tdot_conservative_lower_K_s','Conservative lower (secondary energy ceiling)')]:
 plt.plot(z,D[key],label=label)
plt.yscale('symlog',linthresh=1e-28);plt.ylabel('Conditional instantaneous dT/dt [K/s]')
plt.title('Thermal RHS envelope, no gas evolution solved');plt.legend(fontsize=7);save('PLOT03_TEMPERATURE_RHS_COEFFICIENTS.png')

plt.figure(figsize=(8.4,4.5))
for key,label in [('directwindow_LiII_2E1_HI_counts_upper_per_b','H I primary'),('directwindow_LiII_2E1_HeI_counts_upper_per_b','He I primary'),('directwindow_LiII_2E1_HeII_counts_upper_per_b','He II primary'),('maximum_additional_HHe_secondary_ionizations_per_b_energy_cap','secondary, energy cap')]:
 plt.plot(z,np.cumsum(D[key]),label=label)
plt.ylabel('Cumulative conditional events / baryon');plt.title('Primary species partition and model-independent secondary energy ceiling');plt.legend(fontsize=7);save('PLOT04_CUMULATIVE_PHOTO_AND_SECONDARY.png')

plt.figure(figsize=(8.4,4.5))
q=-D.delta_REI_binding_minus_BASS_HHe_erg_per_Href_s.to_numpy()
plt.plot(z,np.where(q>0,q,np.nan));plt.yscale('log')
plt.ylabel('BASS minus REI binding-energy defect [erg / Href / s]')
plt.title('Independent threshold owner mismatch for 2E1-absorbed photons');save('PLOT05_HHE_THRESHOLD_SOURCE_DEFECT.png')

plt.figure(figsize=(8.4,4.5))
chi=13.598434599702
E=R['all_conditional_primary_e_eV_per_baryon_upper'];n=R['secondary_HHe_ionizations_energy_ceiling_per_baryon']
x=np.linspace(0,n,301)
plt.plot(x, E-chi*x,label='No-external-energy allowed boundary')
plt.fill_between(x,0,E-chi*x,alpha=.18,label='Allowed energy-only region')
plt.xlabel('Additional H/He secondary ionizations / baryon');plt.ylabel('Remaining heat budget [eV / baryon]')
plt.title('Secondary-ionization vs heat: conditional primary-electron energy cone')
plt.legend(fontsize=8);plt.grid(alpha=.2);plt.tight_layout();plt.savefig(OUT/'PLOT06_ENERGY_SIMPLEX_FRONTIER.png',dpi=150,metadata={'Software':'REI F4 source-bound science'});plt.close()
print('PLOTS=6; source rows=',len(D))
