#!/usr/bin/env python3
"""Two source-conditioned scientific plots, not collision yields or gas temperature."""
from pathlib import Path
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
a=pd.read_csv(ROOT/'results'/'CCC_FIRST_COLLISION_ARRIVAL_192.csv')
c=['HI_ion','HI_2p','HI_2s','HeI_ion','HeI_2p','HeI_t2s'];nz=a.primary_electrons_per_b>0
plt.rcParams['svg.hashsalt']='rei_f4_ccc_six_20261031'
fig,ax=plt.subplots(figsize=(9.6,5.6),layout='constrained')
for k in c:
    val=a.loc[nz,k+'_source_nu_mean_per_b_s']/a.loc[nz,'primary_electrons_per_b']
    ax.plot(a.loc[nz,'z_low'],np.maximum(val,1e-40),lw=1.4,label=k)
ax.set(xlabel='Redshift z (saved BASS193 endpoint)', ylabel='Partial collision frequency per first electron [s$^{-1}$]',title='CCC six-channel inelastic collision rates on frozen BASS193')
ax.set_yscale('log');ax.invert_xaxis();ax.legend(ncol=2,fontsize=8);ax.grid(alpha=0.2)
fig.savefig(FIG/'CCC_PARTIAL_COLLISION_FREQ_192.png',dpi=175)
fig.savefig(FIG/'CCC_PARTIAL_COLLISION_FREQ_192.svg',metadata={'Date':None})
plt.close(fig)
fig,ax=plt.subplots(figsize=(9.6,5.6),layout='constrained')
rate=np.zeros(len(a));lo=np.zeros(len(a));hi=np.zeros(len(a))
for k in c:
    rate+=a[k+'_source_nu_mean_per_b_s'].values
    lo+=a[k+'_source_nu_min_per_b_s'].values
    hi+=a[k+'_source_nu_max_per_b_s'].values
rate=rate[nz]/a.loc[nz,'primary_electrons_per_b'].values
lo=lo[nz]/a.loc[nz,'primary_electrons_per_b'].values
hi=hi[nz]/a.loc[nz,'primary_electrons_per_b'].values
dt=a.loc[nz,'proper_interval_s'].values
x=a.loc[nz,'z_low'].values
ax.fill_between(x,np.maximum(lo*dt,1e-16),np.maximum(hi*dt,1e-16),alpha=.25,label='Moment-constrained range')
ax.plot(x,rate*dt,label='Mean-energy collocation of same piecewise-linear rate')
ax.axhline(1,ls=':',label=r'$\nu_{\mathrm{inelastic}}\Delta t=1$')
ax.set(xlabel='Redshift z (frozen saved background)',ylabel=r'Six-channel instantaneous rate $\nu\Delta t$ (not optical depth)',title='Six CCC inelastic rates against original BASS proper intervals')
ax.set_yscale('log');ax.invert_xaxis();ax.legend(fontsize=8);ax.grid(alpha=.2)
fig.savefig(FIG/'CCC_RATE_VS_PROPER_CLOCK_192.png',dpi=175)
fig.savefig(FIG/'CCC_RATE_VS_PROPER_CLOCK_192.svg',metadata={'Date':None})
plt.close(fig)
print('CREATED 2_PNG+2_SVG')
