#!/usr/bin/env python3
"""R41 source-row scientific figures, not illustrations; only generated real-source data."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent/'results'
s=pd.read_csv(r/'R41_FIRST_V0_MECHANISM_SUMMARY_3500.csv')
h=pd.read_csv(r/'R41_HALF_RADIATIVE_DENSITY_700.csv')
c=pd.read_csv(r/'R41_SOURCE_CONTRAST_1750.csv')
l=pd.read_csv(r/'R41_PHOTON_LINE_EVENTS_4704.csv')
# 1: physical competition at T55K, initial v1J6, OFF
fig,ax=plt.subplots(figsize=(7.5,4.6))
q=s[(s.T_gas_K==55)&(s.initial_HD_J==6)&(s.z_boundary=='OFF')&(s.source_lane=='EMAA_primary')]
ax.plot(q.n_Hplus_cm_minus3,q.P_first_v0_by_collision,'o-',label='collision first-v0')
ax.plot(q.n_Hplus_cm_minus3,q.P_first_v0_by_radiative,'s-',label='radiative first-v0')
ax.axhline(.5,ls=':',lw=1);ax.set_xscale('log');ax.set(xlabel='Prescribed n(H+) [cm$^{-3}$]',ylabel='Probability',title='Tgas 55 K, HD(v1,J6), radiation OFF (spontaneous kept)');ax.legend();fig.tight_layout();fig.savefig(r/'FIG01_MECHANISM_55K.png',dpi=175);fig.savefig(r/'FIG01_MECHANISM_55K.svg');plt.close(fig)
# 2 n_half by initial J and sources at 55, z off
fig,ax=plt.subplots(figsize=(7.5,4.6))
q=h[(h.T_gas_K==55)&(h.z_boundary=='OFF')]
for lane,g in q.groupby('source_lane'):ax.plot(g.initial_HD_J,g.nHplus_radiative_collision_equal_cm_minus3,'o-',label=lane)
ax.set(xlabel='Initial HD(v=1, J)',ylabel=r'$n_{1/2}$ [cm$^{-3}$]',title='Source-dependent first-event radiative/collision crossover, 55 K');ax.legend();fig.tight_layout();fig.savefig(r/'FIG02_HALF_DENSITY_55K.png',dpi=175);fig.savefig(r/'FIG02_HALF_DENSITY_55K.svg');plt.close(fig)
# 3 Source mismatch across density, 55 J6
fig,ax=plt.subplots(figsize=(7.5,4.6))
q=c[(c.T_gas_K==55)&(c.initial_HD_J==6)]
for z,grp in q.groupby('z_boundary'):ax.plot(grp.n_Hplus_cm_minus3,grp.P_first_v0_destination_L1_GL_minus_EMAA,'o-',label=z)
ax.set_xscale('log');ax.set(xlabel=r'Prescribed n(H+) [cm$^{-3}$]',ylabel=r'$L_1$ source difference (first-v0 destination)',title='GL-printed hybrid vs EMAA first-v0, 55 K, J6');ax.legend(title='Blackbody z');fig.tight_layout();fig.savefig(r/'FIG03_SOURCE_SENSITIVITY_55K.png',dpi=175);fig.savefig(r/'FIG03_SOURCE_SENSITIVITY_55K.svg');plt.close(fig)
# 4 photon path gross emissions minus absorptions at 55 K j6 1e3 under z=300
fig,ax=plt.subplots(figsize=(7.8,4.7))
q=l[(l.T_gas_K==55)&(l.initial_HD_J==6)&(l.n_Hplus_cm_minus3==1000.)&(l.z_boundary=='300')&(l.source_lane=='EMAA_primary')].copy()
q['net']=q.count_spontaneous+q.count_stimulated-q.count_absorbed
q=q.sort_values('net',ascending=False).head(12)
ax.bar(range(len(q)),q['net']);ax.set_xticks(range(len(q)),[f'{u}→{d}' for u,d in zip(q.line_up,q.line_low)],rotation=45,ha='right');ax.set(ylabel='Expected net photon count per initial HD',title='12 dominant source-owned HD lines, Tgas55 K, z300, n(H+)=10³');fig.tight_layout();fig.savefig(r/'FIG04_SOURCE_PHOTON_EVENTS_55K.png',dpi=175);fig.savefig(r/'FIG04_SOURCE_PHOTON_EVENTS_55K.svg');plt.close(fig)
print('Generated 4 real-data PNG and 4 SVG')
