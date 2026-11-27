from pathlib import Path
import csv,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
with (ROOT/'data/FASTD_INTEGRATED_50.csv').open() as f: rows=list(csv.DictReader(f))
# Fix rendering reproducibility metadata SVG random hashes.
matplotlib.rcParams['svg.hashsalt']='BASS_HE_20261031_FASTD_NRL'
matplotlib.rcParams['font.family']='DejaVu Sans'
def out(filename):
 plt.tight_layout(); plt.savefig(FIG/(filename+'.png'),dpi=130,metadata={'Software':'BASS_HE_PR139'})
 plt.savefig(FIG/(filename+'.svg'),metadata={'Date':'2026-10-31','Creator':'BASS_HE_PR139'})
 plt.close()
fig,ax=plt.subplots(figsize=(7,4.3));
for z in [1e4,1e5,1e6]:
 rr=[r for r in rows if float(r['z'])==z]
 rr.sort(key=lambda r:float(r['K0_MeV']))
 ax.loglog([float(r['K0_MeV']) for r in rr],[float(r['t_stop_s']) for r in rr],marker='.',label=f'z={z:.0e}')
ax.set(xlabel='Fast deuteron initial kinetic energy [MeV]',ylabel='Stopping time to max(1 keV,30 kBT) [s]',title='NRL Maxwellian H/He plasma: FastD stopping time');ax.legend();out('FASTD_STOPPING_TIME')
fig,ax=plt.subplots(figsize=(7,4.3));
for z in [1e4,1e5,1e6]:
 rr=[r for r in rows if float(r['z'])==z];rr.sort(key=lambda r:float(r['K0_MeV']))
 ax.semilogx([float(r['K0_MeV']) for r in rr],[100*float(r['Q_ion_MeV'])/float(r['deltaK_MeV']) for r in rr],marker='.',label=f'z={z:.0e}')
ax.set(xlabel='Fast deuteron birth energy [MeV]',ylabel='Ion share of traced Coulomb energy transfer [%]',title='Maxwellian temperature changes ion/electron partition');ax.legend();out('FASTD_ION_TRANSFER_FRACTION')
fig,ax=plt.subplots(figsize=(7,4.3));
for z in [1e4,1e5,1e6]:
 rr=[r for r in rows if float(r['z'])==z];rr.sort(key=lambda r:float(r['K0_MeV']))
 ax.loglog([float(r['K0_MeV']) for r in rr],[float(r['exposure_p_cm2']) for r in rr],marker='.',label=f'z={z:.0e}')
ax.set(xlabel='Initial deuteron energy [MeV]',ylabel='Integrated proton target column [cm^-2]',title='Cross-section-independent in-flight exposure');ax.legend();out('FASTD_PROTON_COLUMN_EXPOSURE')
fig,ax=plt.subplots(figsize=(7,4.3));
for z in [1e4,1e5,1e6]:
 rr=[r for r in rows if float(r['z'])==z];rr.sort(key=lambda r:float(r['K0_MeV']))
 ax.loglog([float(r['K0_MeV']) for r in rr],[float(r['stop_over_Hubble']) for r in rr],marker='.',label=f'z={z:.0e}')
ax.axhline(1.,ls='--',lw=.8,label='Hubble time');ax.set(xlabel='FastD initial energy [MeV]',ylabel='Stopping time / Hubble time',title='Quasistatic FLRW consistency');ax.legend();out('FASTD_HUBBLE_RATIO')
