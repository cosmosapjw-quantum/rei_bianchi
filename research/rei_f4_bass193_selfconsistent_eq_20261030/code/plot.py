"""Model-data figures from immutable saved BASS trajectory and solved static equilibrium; no IVP."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'results'
with (OUT/'ELECTRON_FEEDBACK_193.csv').open() as f:e=list(csv.DictReader(f))
with (OUT/'EQUILIBRIUM_193x6.csv').open() as f:r=list(csv.DictReader(f))
zz=[float(x['z']) for x in e]
fig,ax=plt.subplots(figsize=(7.4,4.5))
ax.semilogy(zz,[float(x['xe_saved']) for x in e],label='Original saved BASS21 electron fraction')
ax.semilogy(zz,[float(x['xe_star']) for x in e],label='Self-consistent instantaneous equilibrium (counterfactual)')
ax.set(xlim=(20,2),xlabel='Stored mean redshift z',ylabel=r'$x_e=n_e/n_b$',title='BASS21 frozen 193-epoch chemistry vs instantaneous equilibrium')
ax.legend(fontsize=7,loc='lower left');fig.tight_layout();fig.savefig(OUT/'BASS_SAVED_VS_INSTANT_EQ.png',dpi=145);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.4,4.5))
for g in ['H1','He4','Li7']:
 a=[x for x in r if x['group']==g]
 ax.semilogy([float(x['z']) for x in a],[max(float(x['TV_distance']),1e-15) for x in a],label=g)
ax.set(xlim=(20,2),xlabel='Stored mean redshift z',ylabel='Total-variation distance to fixed-field equilibrium',title='Source-owned nonequilibrium charge-state distance')
ax.legend();fig.tight_layout();fig.savefig(OUT/'ISOTOPE_CHARGE_NON_EQUILIBRIUM.png',dpi=145);plt.close(fig)
