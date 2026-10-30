#!/usr/bin/env python3
"""Reproducible original-source scientific figures; no data or parameter mutation."""
import csv,pathlib,json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from causal_firstflight import ROOT

def cols(name):
 with (ROOT/'results'/name).open(newline='') as f:return list(csv.DictReader(f))

def draw():
 a=cols('EMISSIONS_193.csv');z=[float(r['z_emission']) for r in a]
 fig,ax=plt.subplots(figsize=(7.2,4.4));ax.plot(z,[float(r['mean_absorptions_per_pair']) for r in a],label='Causal first flight')
 ax.plot(z,[float(r['P2'])*2 for r in a],label='2 × both-absorption probability')
 ax.set(xlabel='Emission redshift z',ylabel='Photons per conditional 2E1 pair',title='BASS193 passive redshifting first absorption')
 ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(ROOT/'results/CAUSAL_BY_EMISSION.png',dpi=150);plt.close(fig)
 b=cols('ABSORPTION_ARRIVALS_192.csv');za=[float(r['arrival_z_low']) for r in b]
 fig,ax=plt.subplots(figsize=(7.2,4.4))
 for c in ['H_I','He_I','He_II']:
  ax.plot(za,[float(r[f'incoming_integrated_{c}_per_baryon']) for r in b],label=c)
 ax.set(xlabel='First-absorption interval lower redshift z',ylabel='Events / baryon / saved interval',title='Source-weighted causal absorption arrivals')
 ax.set_yscale('symlog',linthresh=1e-20);ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(ROOT/'results/CAUSAL_ARRIVAL_HHE.png',dpi=150);plt.close(fig)
 print('PLOTS_2_DONE')
if __name__=='__main__':draw()
