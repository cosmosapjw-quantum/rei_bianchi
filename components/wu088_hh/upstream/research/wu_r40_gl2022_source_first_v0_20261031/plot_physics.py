#!/usr/bin/env python3
"""Source-conditional physical plots; every plotted point is a generated CSV row."""
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
ROOT=Path(__file__).resolve().parent
out=ROOT/'results'
b=pd.read_csv(out/'FIRST_V0_HIT_BRANCHES_1680.csv')
s=pd.read_csv(out/'FIRST_V0_HIT_SUMMARY_140.csv')
g=pd.read_csv(out/'PAIR_ISOLATED_SENSITIVITY_490.csv')
t=pd.read_csv(out/'TABLE11_RECONSTRUCTION_10.csv')
# 1: branch source contrast at exact biggest case
fig,ax=plt.subplots(figsize=(8,4.8))
for source,v in b[(b.T_K==55)&(b.initial_J==6)].groupby('source_lane'):
    ax.plot(v.final_v0_J,v.P_first_v0_hit,marker='o',label=source)
ax.set(xlabel="First landing HD(v=0, J')",ylabel='Conditional first-passage probability',title='H+ + HD(v=1,J=6), Tgas=55 K')
ax.legend();ax.grid(alpha=.25);fig.tight_layout()
fig.savefig(out/'FIG01_55K_V1J6_BRANCH_SOURCE.png',dpi=180)
fig.savefig(out/'FIG01_55K_V1J6_BRANCH_SOURCE.svg');plt.close(fig)
# 2 max vs source choice all temps
p=b.pivot_table(index=['T_K','initial_J','final_v0_J'],columns='source_lane',values='P_first_v0_hit').reset_index();p['absdiff']=(p.GL_printed_hybrid-p.EMAA_primary).abs()
v=p.groupby(['T_K','initial_J'])['absdiff'].sum().reset_index()
fig,ax=plt.subplots(figsize=(8,4.8))
for j,subset in v.groupby('initial_J'):
    ax.plot(subset.T_K,subset.absdiff,marker='.',label=f'initial v1 J={j}')
ax.set(xlabel='Tgas (K), original source nodes',ylabel='L1 difference in first-v0 hitting distribution',title='GL printed hybrid versus EMAA original');ax.set_xscale('log');ax.grid(alpha=.2);ax.legend(ncol=2,fontsize=8);fig.tight_layout()
fig.savefig(out/'FIG02_SOURCE_SENSITIVITY_ATLAS.png',dpi=180)
fig.savefig(out/'FIG02_SOURCE_SENSITIVITY_ATLAS.svg');plt.close(fig)
# 3 group isolation for original R36 50 cells, initial J6 55 K
q=g[(g.T_K==55)&(g.initial_J==6)].sort_values('only_that_pair_printed_vs_EMAA_P_L1')
fig,ax=plt.subplots(figsize=(8.3,4.8))
ax.barh(q.GL_discrepant_transition,q.only_that_pair_printed_vs_EMAA_P_L1)
ax.set(xlabel='Isolated source-pair L1 change (not additive)',title='Attribution, initial HD(v=1,J=6), Tgas=55 K');ax.grid(axis='x',alpha=.2);fig.tight_layout()
fig.savefig(out/'FIG03_PAIR_ISOLATED_55K.png',dpi=180)
fig.savefig(out/'FIG03_PAIR_ISOLATED_55K.svg');plt.close(fig)
# 4 supplement Table11 reconstruction; explicitly restricted 7-state comparator
fig,ax=plt.subplots(figsize=(8,4.8))
ax.plot(t.T_K,t.Table11_printed_cm3_s,marker='o',label='GL2022 printed Table 11')
ax.plot(t.T_K,t.reconstruction_j0to6_cm3_s,marker='x',linestyle='--',label='Reconstructed, printed j=0..6')
ax.set(xlabel='Temperature (K)',ylabel=r'Rate coefficient (cm$^3$ s$^{-1}$)',title='Table 11 restricted-source consistency (not owner reconciliation)');ax.set_yscale('log');ax.grid(alpha=.2);ax.legend();fig.tight_layout()
fig.savefig(out/'FIG04_TABLE11_RECONSTRUCTION.png',dpi=180)
fig.savefig(out/'FIG04_TABLE11_RECONSTRUCTION.svg');plt.close(fig)
print('4 PNG and 4 SVG generated')
