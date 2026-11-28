"""Four scientific figures from rebuilt R43 numerical rows; no illustrative/stock imagery."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent/'results'
a=pd.read_csv(R/'R43_CASES_324.csv');b=pd.read_csv(R/'R43_GRACKLE_REFERENCE_15.csv')
# All figures from source-derived physical outputs.
q=a[(a.T_gas_K==70)&(a.n_Hplus_cm_minus3==0)&(a.n_H_cm_minus3==1e4)]
fig,ax=plt.subplots(figsize=(7.5,4.5));ax.bar(range(len(q)),q.net_photon_J_s_per_HD*1e29);ax.set_xticks(range(len(q)),q.z_boundary);ax.set(xlabel='Prescribed blackbody z boundary',ylabel='Signed photon cooling [10^-29 J s^-1 HD^-1]',title='Original EMAA HD52, gas 70 K, n(H)=1e4 cm^-3');ax.axhline(0,lw=.8);fig.tight_layout();fig.savefig(R/'FIG01_R43_70K_SIGNED_COOLING.png',dpi=160);fig.savefig(R/'FIG01_R43_70K_SIGNED_COOLING.svg');plt.close(fig)
q=a[(a.n_Hplus_cm_minus3==0)&(a.n_H_cm_minus3==1e4)]
fig,ax=plt.subplots(figsize=(7.5,4.5));
for label,group in q.groupby('z_boundary'):ax.plot(group.T_gas_K,group.net_photon_J_s_per_HD,'o-',label=label)
ax.set(xscale='log',xlabel='Tgas [K] (original EMAA nodes)',ylabel='Signed net photon cooling [J s^-1 HD^-1]',title='Source-authentic HD52 radiative cooling/heating phase');ax.legend(title='blackbody z');ax.axhline(0,lw=.8);fig.tight_layout();fig.savefig(R/'FIG02_R43_SIGN_PHASE.png',dpi=160);fig.savefig(R/'FIG02_R43_SIGN_PHASE.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,4.5));ax.plot(b.T_gas_K,b.ratio_EMAA_over_Grackle_HDlow,'o-');ax.set(xscale='log',xlabel='Original EMAA gas temperature [K]',ylabel='EMAA / Grackle HDlow rate',title='State-to-state source versus original published Grackle fit');ax.axhline(1,ls=':',lw=.8);fig.tight_layout();fig.savefig(R/'FIG03_R43_EMAA_GRACKLE_RATIO.png',dpi=160);fig.savefig(R/'FIG03_R43_EMAA_GRACKLE_RATIO.svg');plt.close(fig)
c=pd.read_csv(R/'R43_POPULATIONS_16848.csv');q=c[(c.T_gas_K==100)&(c.n_H_cm_minus3==1e4)&(c.n_Hplus_cm_minus3==0)&(c.z_boundary=='30')];fig,ax=plt.subplots(figsize=(7.5,4.5));ax.plot(q.level_id,q.p_HD_level,'o',ms=3);ax.set(yscale='log',xlabel='EMAA energy-level ID',ylabel='Stationary HD population',title='Non-LTE HD52 distribution at Tgas=100 K, z=30');fig.tight_layout();fig.savefig(R/'FIG04_R43_HD52_LEVEL_POP.png',dpi=160);fig.savefig(R/'FIG04_R43_HD52_LEVEL_POP.svg');plt.close(fig)
print('Four source-derived figures PNG+SVG written')
