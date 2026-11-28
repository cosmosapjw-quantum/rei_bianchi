#!/usr/bin/env python3
"""Compare actual 52-level spectroscopic escape with 19-level closed-graph first hit."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent/'results'
a=pd.read_csv(p/'R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv')
b=pd.read_csv(p/'R41_FIRST_V0_MECHANISM_SUMMARY_3500.csv')
fig,ax=plt.subplots(figsize=(7.5,4.7))
q=a[(a.T_gas_K==55)&(a.initial_HD_J==6)&(a.source_lane=='EMAA_primary')]
for z in ('OFF','30','100','300'):
 c=q[q.z_boundary==z]
 ax.plot(c.n_Hplus_cm_minus3,c.P_first_radiative_exit_outside_HD19,'o-',label=z)
ax.set_xscale('log');ax.set(xlabel=r'Prescribed $n(\mathrm{H}^+)$ [cm$^{-3}$]',ylabel='Probability of known radiative exit outside HD19',title='Source-identified higher-level absorption before first v0, Tgas=55 K, J6');ax.legend(title='Blackbody boundary z');fig.tight_layout();fig.savefig(p/'FIG05_OUTSIDE_HD19_LEAKAGE.png',dpi=175);fig.savefig(p/'FIG05_OUTSIDE_HD19_LEAKAGE.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,4.7))
q=a[(a.T_gas_K==55)&(a.initial_HD_J==6)&(a.source_lane=='EMAA_primary')&(a.n_Hplus_cm_minus3==1000.)]
ax.plot(q.z_boundary,q.P_first_v0_any,'o-',label='v0 first with known radiative external exit')
ax.plot(q.z_boundary,q.P_first_radiative_exit_outside_HD19,'s-',label='outside HD19 first escape')
closed=b[(b.T_gas_K==55)&(b.initial_HD_J==6)&(b.source_lane=='EMAA_primary')&(b.n_Hplus_cm_minus3==1000.)]
ax.plot(closed.z_boundary,closed.P_sum,'x--',label='closed HD19 total first v0 (=1)')
ax.set(xlabel='Fixed blackbody boundary z (OFF means zero external photons)',ylabel='First-event probability',title='Known spectral leakage changes HD19 first-v0 interpretation');ax.legend();fig.tight_layout();fig.savefig(p/'FIG06_OPEN_VS_CLOSED_HD19.png',dpi=175);fig.savefig(p/'FIG06_OPEN_VS_CLOSED_HD19.svg');plt.close(fig)
print('2 additional real source-data PNG + SVG')
