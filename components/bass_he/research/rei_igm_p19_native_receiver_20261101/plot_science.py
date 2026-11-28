#!/usr/bin/env python3
"""Real source-conditioned 46,080-node diagnostics, with no synthetic noise."""
from pathlib import Path
import csv,gzip,json,math
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["svg.hashsalt"]="bass_he_rei_p19_z5p95_source_only"
root=Path(__file__).resolve().parent
j=json.loads((root/'results/SCIENCE_RESULTS.json').read_text())
rows=[]
with gzip.open(root/'results'/j['source_data_csv'],'rt') as f:
    for r in csv.DictReader(f):rows.append([float(r[x]) for x in ('T_K','native_photoheat_erg_s','P19log_excess_heat_erg_s','P19linear_excess_heat_erg_s','N_H_all')])
a=np.asarray(rows)
ix=np.argsort(a[:,0]);chunks=np.array_split(ix,10)
Ts=[np.median(a[c,0]) for c in chunks]
fig,ax=plt.subplots(figsize=(10,5.5))
for k,label in [(1,'Original REI photon-owner'),(2,'Puchwein D1, log-linear'),(3,'Puchwein D1, rate-linear')]:
    rates=[float(np.median(a[c,k]/a[c,4])) for c in chunks]
    ax.plot(Ts,rates,marker='o',label=label)
ax.set_yscale('log')
ax.set_xscale('log')
ax.set_xlabel('Original frozen REI node temperature [K]')
ax.set_ylabel('Frozen-target excess photoheating [erg H$^{-1}$ s$^{-1}$]')
ax.set_title('BASS_HE → REI IGM | source-owner crosswalk, z = 5.95')
ax.legend(loc='best');fig.tight_layout()
fig.savefig(root/'figures/REI_P19_FROZEN_HEAT_TEMPERATURE_DECILES.png',dpi=170)
fig.savefig(root/'figures/REI_P19_FROZEN_HEAT_TEMPERATURE_DECILES.svg',metadata={'Date':None})
plt.close(fig)
# original group spectrum owner, compare event rates under source-only counterfactual
fig,ax=plt.subplots(figsize=(9,5))
sp=('HI','HeI','HeII');ind=np.arange(3);width=.24
sources=[j['native_source_events_per_s'][s] for s in sp]
p19l=[j['P19_log_counterfactual']['absorbed_events_per_s'][s] for s in sp]
p19a=[j['P19_linear_counterfactual']['absorbed_events_per_s'][s] for s in sp]
for shift,vals,label in [(-width,sources,'REI original'),(0,p19l,'P19 effective, log-linear'),(width,p19a,'P19 effective, rate-linear')]:
    ax.bar(ind+shift,[v if v>0 else np.nan for v in vals],width,label=label)
ax.set_yscale('log');ax.set_xticks(ind,sp)
ax.set_xlabel('Absorbing neutral species')
ax.set_ylabel('Frozen target ionization events [s$^{-1}$]')
ax.set_title('Original REI photon source vs effective P19 rate on same gas')
ax.legend(loc='best');fig.tight_layout()
fig.savefig(root/'figures/REI_P19_SOURCE_EVENTS_BY_SPECIES.png',dpi=170)
fig.savefig(root/'figures/REI_P19_SOURCE_EVENTS_BY_SPECIES.svg',metadata={'Date':None})
plt.close(fig)
print('PLOTS=2_PNG_2_SVG REAL_NODE_DECILES=10')