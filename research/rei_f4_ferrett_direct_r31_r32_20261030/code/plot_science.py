from pathlib import Path
import csv, importlib.util, sys
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('direct_r31',p/'code/direct_r31.py');mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
fig,ax=plt.subplots(figsize=(8,5))
a=[mod.branch_enclosure(e) for e in mod.R31[:,0]]
xs=mod.R31[:,0]
ax.plot(xs,[r['triplet_fraction'] for r in a],marker='o',label='Triplet 3S: direct R31/R32')
ax.fill_between(xs,[r['triplet_fraction_min'] for r in a],[r['triplet_fraction_max'] for r in a],alpha=.22,label='Marginal statistical rectangles')
ax.plot(xs,[r['n2_rest_fraction'] for r in a],marker='s',label='Unresolved n2 rest (singlet upper)')
ax.plot(xs,[r['n3_fraction'] for r in a],marker='^',label='Measured n3/n2 fraction')
ax.set(xlabel='Source photon energy [eV]',ylabel='Fraction of measured n2+n3 subset',title='Original Ferrett 1987 direct R31 / R32 branching')
ax.grid(alpha=.3);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(p/'results/FERRETT_DIRECT_BRANCH_FRACTIONS.png',dpi=160);plt.close(fig)
rows=list(csv.DictReader((p/'results/FERRETT_DIRECT_R31_R32_EPOCH_193.csv').open()))
rows=sorted(rows,key=lambda r:float(r['z']))
fig,ax=plt.subplots(figsize=(8,5))
ax.plot([float(r['z']) for r in rows],[float(r['triplet_rate']) for r in rows],label='Conditionally weighted triplet production')
ax.plot([float(r['z']) for r in rows],[float(r['rest_upper_rate']) for r in rows],label='Potential pure-singlet upper source')
ax.set(xlabel='Original redshift z',ylabel='Events / baryon / s',title='Frozen original BASS193 Li I K-shell event rates')
ax.grid(alpha=.3);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(p/'results/FERRETT_BASS193_DIRECT_EVENT_HISTORY.png',dpi=160);plt.close(fig)
print('Physical figures: 2 files')
