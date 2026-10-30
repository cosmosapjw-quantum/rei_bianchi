import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/PAIR_EPOCH_193.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
z=[float(r['z']) for r in rows]

fig,ax=plt.subplots(figsize=(7.0,4.4))
for k,n in [('P_zero_absorbed','zero'),('P_one_absorbed','one'),('P_two_absorbed','two')]:
    ax.plot(z,[float(r[k]) for r in rows],label=n)
ax.set(xlabel='BASS21 original saved redshift z',ylabel='Probability per conditional singlet pair',title='Correlated 2E1 pair: zero / one / two first absorptions',ylim=(-.03,1.03))
ax.legend();fig.tight_layout();fig.savefig(ROOT/'results/PAIR_ABSORBED_COUNT.png',dpi=160);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.0,4.4))
ax.plot(z,[float(r['event_correlation_covariance']) for r in rows],label='Covariance: P2 − P(low)P(high)')
ax.axhline(0,linestyle='--',linewidth=.9)
ax.set(xlabel='BASS21 original saved redshift z',ylabel='Covariance',title='Two-photon absorption correlation vs independent marginals')
ax.legend();fig.tight_layout();fig.savefig(ROOT/'results/PAIR_ABSORPTION_COVARIANCE.png',dpi=160);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.0,4.4))
ax.plot(z,[float(r['two_photon_joint_TV_vs_marginal_independence']) for r in rows],label='TV(Joint, independent marginals)')
ax.set(xlabel='BASS21 original saved redshift z',ylabel='Total variation distance',title='Joint H/He/Li/escape outcomes: energy-pair coupling')
ax.legend();fig.tight_layout();fig.savefig(ROOT/'results/PAIR_CHANNEL_TV.png',dpi=160);plt.close(fig)
print('FIGURES_3_SUCCESS')
