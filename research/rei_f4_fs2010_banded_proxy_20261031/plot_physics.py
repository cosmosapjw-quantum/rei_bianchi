"""Scientific plots from fresh physical CSV (no synthetic proxy data)."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
D=pd.read_csv(ROOT/'BASS193_FS2010_BAND_DEPOSITION_ENVELOPE_192.csv')
R=json.loads((ROOT/'SCIENTIFIC_RESULT.json').read_text())
fig=ROOT/'figures';fig.mkdir(exist_ok=True)
# Arrival source energy and projected heat envelope (eV/baryon), no evolving gas temperature
f,ax=plt.subplots(figsize=(9,5))
ax.plot(D.z_end,D.primary_eV_per_b,label='Original primary electron energy',lw=2)
ax.fill_between(D.z_end,D.xHII_heat_lo_eV_per_b,D.xHII_heat_hi_eV_per_b,alpha=.3,label='FS one-xi projected heating envelope')
ax.set_xlabel('Arrival redshift z');ax.set_ylabel('Conditional energy per original baryon [eV]')
ax.set_yscale('symlog',linthresh=1e-24)
ax.invert_xaxis();ax.legend(fontsize=8);ax.grid(alpha=.2);f.tight_layout();f.savefig(fig/'ORIGINAL_SOURCE_FS2010_HEAT_ENVELOPE.png',dpi=180);plt.close(f)
# Counterfactual one-xi models xHII vs electron-pool-matched. Fractional totals are intervals, not a simplex point.
f,ax=plt.subplots(figsize=(8,5))
labels=['heat','ion','exc'];ys=[0,1,2]
for q,k in enumerate(['xHII','electron_matched']):
 d=R['scenarios'][k]; low=np.array([d[z+'_lo_fraction_of_primary'] for z in labels]);high=np.array([d[z+'_hi_fraction_of_primary'] for z in labels]);center=(low+high)/2
 ax.errorbar(center*100,np.array(ys)+(q-.5)*.2,xerr=np.vstack([center-low,high-center])*100,fmt='o',capsize=2,label=k)
ax.set_yticks(ys,labels);ax.set_xscale('symlog',linthresh=.01);ax.grid(alpha=.2)
ax.set_xlabel('Percent of original primary energy (separate intervals, not simultaneous)')
ax.legend(fontsize=8);f.tight_layout();f.savefig(fig/'FS2010_PROJECTED_DEPOSITION_CHANNEL_INTERVALS.png',dpi=180);plt.close(f)
print('FIGURES',[(p.name,p.stat().st_size) for p in fig.glob('*.png')])
