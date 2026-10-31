#!/usr/bin/env python3
"""Scientific figures from actual BASS193+CCC6 first-event output, not illustrative.
Matplotlib deterministic SVG fixed hashsalt; no styling explicitly assigned.
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
plt.rcParams['svg.hashsalt']='REI_F4_CCC6_FIRST_EVENT_20261031'
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'results';F=ROOT/'figures';F.mkdir(exist_ok=True)
A=pd.read_csv(D/'BASS_CCC6_FIRST_EVENT_ARRIVAL_192.csv')
B=pd.read_csv(D/'BASS193_CCC6_MONO_1351.csv')
K=pd.read_csv(ROOT/'source'/'PR310_KIM92_SOURCE_BANDS_3840.csv')

# 1. Fixed-energy first-event with actual BASS 21-ion ne
fig,ax=plt.subplots(figsize=(8.8,5.0))
x=B[np.isclose(B.initial_E_eV,55.)].sort_values('z',ascending=False)
for name,label in [('P_any_six_channel','Any of six CCC'),('HI_2p_P','HI 2p excitation'),('HI_2s_P','HI 2s excitation'),('HI_ion_P','HI impact ionization'),('HeI_ion_P','He I impact ionization')]:
 ax.semilogy(x.z,np.maximum(x[name],1e-25),label=label)
ax.invert_xaxis();ax.set_xlabel('Original BASS redshift z (cosmic time →)');ax.set_ylabel('P(first selected inelastic event before 13.7 eV)');ax.set_ylim(1e-11,1.3);ax.legend(loc='lower left',fontsize=8);fig.tight_layout();fig.savefig(F/'01_FIRST_EVENT_CCC6_PROB_Z.png',dpi=180);fig.savefig(F/'01_FIRST_EVENT_CCC6_PROB_Z.svg',metadata={'Date':'2026-10-31T00:00:00Z'});plt.close(fig)

# 2. Arrival physical band moment-constrained first-event envelope
fig,ax=plt.subplots(figsize=(8.8,5.0))
x=A.sort_values('z_low',ascending=False)
ax.semilogy(x.z_low,np.maximum(x.six_any_mean,1e-34),label='Source-band mean-energy collocation')
ax.fill_between(x.z_low,np.maximum(x.six_any_lower,1e-34),np.maximum(x.six_any_upper,1e-34),alpha=.22,label='Rigorous numerical model N,M envelope')
ax.invert_xaxis();ax.set_xlabel('Arrival redshift z (cosmic time →)');ax.set_ylabel('Selected first events / original baryon / arrival interval');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(F/'02_PHYSICAL_ARRIVAL_EVENT_ENVELOPE.png',dpi=180);fig.savefig(F/'02_PHYSICAL_ARRIVAL_EVENT_ENVELOPE.svg',metadata={'Date':'2026-10-31T00:00:00Z'});plt.close(fig)

# 3. Partial first-event cumulative budgets for actual original source
fig,ax=plt.subplots(figsize=(8.8,5.0))
exc=['HI_2p','HI_2s','HeI_2p','HeI_t2s'];ion=['HI_ion','HeI_ion']
xc=x.sort_values('z_low',ascending=False)
ax.plot(xc.z_low,np.cumsum(xc[[c+'_mean' for c in exc]].sum(axis=1)),label='Selected excitation first event')
ax.plot(xc.z_low,np.cumsum(xc[[c+'_mean' for c in ion]].sum(axis=1)),label='Selected ionization first event')
ax.plot(xc.z_low,np.cumsum(xc.six_any_mean),label='All six selected first event')
ax.invert_xaxis();ax.set_xlabel('Arrival redshift z');ax.set_ylabel('Accumulated selected first events / original baryon');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(F/'03_CUMULATIVE_FIRST_EXC_ION_EVENTS.png',dpi=180);fig.savefig(F/'03_CUMULATIVE_FIRST_EXC_ION_EVENTS.svg',metadata={'Date':'2026-10-31T00:00:00Z'});plt.close(fig)

# 4. Minimal obligatory atomic excitation / binding threshold energy per original baryon
fig,ax=plt.subplots(figsize=(8.8,5.0))
ax.semilogy(x.z_low,np.maximum(x.first_event_threshold_floor_eV_mean,1e-34),label='First-event excitation/binding threshold floor')
ax.semilogy(x.z_low,np.maximum(x.photoelectron_E_eV_per_b,1e-34),label='Original primary kinetic energy available')
ax.invert_xaxis();ax.set_xlabel('Arrival redshift z');ax.set_ylabel('Energy (eV / original baryon / arrival interval)');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(F/'04_FIRST_EVENT_THRESHOLD_ENERGY_FLOOR.png',dpi=180);fig.savefig(F/'04_FIRST_EVENT_THRESHOLD_ENERGY_FLOOR.svg',metadata={'Date':'2026-10-31T00:00:00Z'});plt.close(fig)

# 5. Matched original first-source comparison: 6CCC inelastic vs NIST Kim ionization alternative
ks=K.groupby('arrival_interval',sort=True)[['model_first_events_lower','model_first_events_upper']].sum().reset_index()
joined=A.merge(ks,on='arrival_interval',validate='one_to_one')
fig,ax=plt.subplots(figsize=(8.8,5.0))
xx=joined.sort_values('z_low',ascending=False)
ax.semilogy(xx.z_low,np.maximum(xx[['HI_ion_mean','HeI_ion_mean']].sum(axis=1),1e-34),label='CCC only H/He first ionization (6-channel competition)')
ax.semilogy(xx.z_low,np.maximum(xx.six_any_mean,1e-34),label='CCC any six-channel first inelastic')
ax.fill_between(xx.z_low,np.maximum(xx.model_first_events_lower,1e-34),np.maximum(xx.model_first_events_upper,1e-34),alpha=.18,label='NIST Kim92 + Coulomb ionization-only (separate model)')
ax.invert_xaxis();ax.set_xlabel('Arrival redshift z');ax.set_ylabel('First events / original baryon / arrival interval');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(F/'05_CCC_VS_KIM92_DISTINCT_MODELS.png',dpi=180);fig.savefig(F/'05_CCC_VS_KIM92_DISTINCT_MODELS.svg',metadata={'Date':'2026-10-31T00:00:00Z'});plt.close(fig)
print('Generated 5 PNG+SVG science figure pairs')
