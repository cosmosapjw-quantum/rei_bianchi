#!/usr/bin/env python3
"""Generate selected scoped diagnostics from actually saved CSV runs."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((HERE/'evidence/p3_positive_campaign_matched.csv').open()))
rows=[r for r in rows if r['case']=='flrw']
data={(int(r['nsteps']),r['representation']):r for r in rows}
fig,ax=plt.subplots(figsize=(8.7,5.3))
for tag,key in [('HI','HI_photo_m3'),('HeI','HeI_photo_m3'),('HeII','HeII_photo_m3'),('D','D_photo_m3'),('survivors','photons_com_m3')]:
 vals=[]
 for n in (8,16,32,64):
  p=float(data[(n,'positive_384')][key]);g=float(data[(n,'projected_64')][key]);vals.append(100*abs(p-g)/abs(p))
 ax.plot([8,16,32,64],vals,marker='o',label=tag)
ax.set_xscale('log',base=2);ax.set_xticks([8,16,32,64],['8','16','32','64'])
ax.set_xlabel('Accepted source-age / chemistry intervals');ax.set_ylabel('Grey 64-bin difference relative to owner 384-cell reference (%)')
ax.set_title('Prescribed MD14/BB50k FLRW short interval: species vs survivors')
ax.grid(True,alpha=.2);ax.legend(ncols=3);fig.tight_layout();fig.savefig(HERE/'evidence/p3_positive_vs_grey.png',dpi=175);plt.close(fig)
rows=list(csv.DictReader((HERE/'evidence/p3_geometric_age.csv').open()))
fig,ax=plt.subplots(figsize=(8.5,5))
for case in ('flrw','shear_plus','shear_minus'):
 sub=[r for r in rows if r['geometry']==case and int(r['n_mu'])==8]
 ax.plot([int(r['n_age']) for r in sub],[float(r['q2_energy']) for r in sub],marker='o',label=case)
ax.set_xscale('log',base=2);ax.set_xlabel('Number of source birth intervals');ax.set_ylabel('Normalized observed energy P2')
ax.set_title('Source-only exact Killing propagation, prescribed off-shell Bianchi I')
ax.grid(True,alpha=.2);ax.legend();fig.tight_layout();fig.savefig(HERE/'evidence/p3_collisionless_q2.png',dpi=175)
print('PLOTS_SAVED',2)
