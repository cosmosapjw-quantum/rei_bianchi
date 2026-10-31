#!/usr/bin/env python3
"""Science-only figures from immutable original physical outputs."""
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='REI_F4_CAUSAL_MEMORY_20261031_SOURCE_LOCKED'
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'results';F=ROOT/'figures';F.mkdir(exist_ok=True)
link=pd.read_csv(O/'CAUSAL_EMISSION_ARRIVAL_18528.csv')
a=pd.read_csv(O/'CAUSAL_ARRIVAL_CLOCK_SOURCE_192.csv')
e=pd.read_csv(O/'CAUSAL_EMISSION_SURVIVAL_193.csv')
def save(fig,stem):
 for ext in ['png','svg']:
  fig.savefig(F/(stem+'.'+ext),dpi=185,bbox_inches='tight',metadata=({'Date':None} if ext=='svg' else None))
 plt.close(fig)
# Physical source-weighted lower triangular memory matrix.
M=np.zeros((192,193))
M[link.arrival_interval.to_numpy(int),link.emission_epoch.to_numpy(int)]=link.first_absorption_events_per_b.to_numpy()
fig,ax=plt.subplots(figsize=(7.7,5.3))
valid=np.where(M>0,M,np.nan)
positive=valid[np.isfinite(valid)]
vmin=max(np.quantile(positive,0.08),np.min(positive));vmax=np.max(positive)
im=ax.imshow(valid[:,:192],origin='lower',interpolation='none',aspect='auto',norm=LogNorm(vmin=vmin,vmax=vmax))
ax.plot([0,191],[0,191],linewidth=.8,linestyle='--',label='same emission/arrival epoch')
ax.set(xlabel='Emission index k (z: 20 to 2)',ylabel='Arrival interval j',title='Original BASS193 Li II 2E1 first-flight causal transfer')
fig.colorbar(im,ax=ax,label='Absorbed photons / baryon / (k,j)')
ax.legend(loc='upper left',fontsize=8)
save(fig,'PLOT01_CAUSAL_TRANSFER_MATRIX')
# Global small but local significant, emphasize absolute source amplitudes.
fig,ax=plt.subplots(figsize=(8,4.6))
zz=a.z_low.to_numpy();absorption=a.absorption_events_per_b.to_numpy();delayed=a.delayed_events_per_b.to_numpy()
ax.plot(zz,np.maximum(absorption,1e-42),label='all first photoabsorptions / baryon')
ax.plot(zz,np.maximum(delayed,1e-42),label='emitted at earlier epochs / baryon')
ax.set_yscale('log');ax.set(xlabel='Arrival redshift z',ylabel='Events / original baryon / bin',title='First-flight event budget and nonlocal source support')
ax.invert_xaxis();ax.legend(loc='upper right',fontsize=9);ax.grid(alpha=.18)
save(fig,'PLOT02_CAUSAL_EVENTS_LOCAL_VS_DELAYED')
fig,ax=plt.subplots(figsize=(8,4.6))
frac=a.delayed_events_fraction.to_numpy()
ax.plot(zz,frac,label='Delayed fraction of arrivals')
ax.plot(zz,a.delayed_primary_energy_fraction.to_numpy(),label='Delayed fraction of primary e$^-$ energy')
ax.axhline(.5,linewidth=.8,linestyle=':')
ax.set(xlabel='Arrival redshift z',ylabel='Delayed share in a single bin',ylim=(-.05,1.05),title='Pointwise memory can dominate low-amplitude late arrivals')
ax.invert_xaxis();ax.legend(fontsize=9);ax.grid(alpha=.18)
save(fig,'PLOT03_LOCAL_DELAYED_FRACTION')
fig,ax=plt.subplots(figsize=(8,4.6))
z_em=e.z_emission.to_numpy()
ax.plot(z_em,e.injected_2E1_photons_per_b,label='2 photons × emitted pairs')
ax.plot(z_em,e.first_absorbed_photons_until_z2_per_b,label='first absorbed by z=2')
ax.plot(z_em,e.not_first_absorbed_by_z2_per_b,label='not first absorbed by z=2')
ax.set(xlabel='Emission redshift z',ylabel='Photon count / baryon / emission epoch',title='Conditional Li II 2E1 photon number balance')
ax.invert_xaxis();ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend(fontsize=8);ax.grid(alpha=.18)
save(fig,'PLOT04_EMISSION_PHOTON_BUDGET')
# FS2010 single xi model, only input-domain-valid rows.
valid=a.FS_xi_valid.to_numpy(bool)
fig,ax=plt.subplots(figsize=(8,4.6))
x=zz[valid];lo=a.loc[valid,'FS_conditional_heat_lower_eV_per_b'].to_numpy();hi=a.loc[valid,'FS_conditional_heat_upper_eV_per_b'].to_numpy()
loold=a.loc[valid,'FS_delayed_conditional_heat_lower_eV_per_b'].to_numpy();hiold=a.loc[valid,'FS_delayed_conditional_heat_upper_eV_per_b'].to_numpy()
ax.plot(x,hi,label='Conditional all-source heat upper')
ax.plot(x,lo,label='Conditional all-source heat lower',linestyle='--')
ax.plot(x,hiold,label='Conditional delayed-source heat upper')
ax.plot(x,loold,label='Conditional delayed-source heat lower',linestyle=':')
ax.set_yscale('log');ax.set(xlabel='Arrival redshift z',ylabel='Projected FS heat (eV / original baryon / bin)',title='FS2010 single-$x_i$ model-only causal heat memory (87 valid bins)')
ax.invert_xaxis();ax.legend(fontsize=8);ax.grid(alpha=.18)
save(fig,'PLOT05_FS2010_CONDITIONAL_THERMAL_MEMORY')
print('5 original-source science figures × PNG/SVG produced')
