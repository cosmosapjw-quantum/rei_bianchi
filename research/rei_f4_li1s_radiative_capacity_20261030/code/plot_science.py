"""Figures for frozen BASS193 photon capacity; no fitted radiation transfer."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_simpson

ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/LI1S_PHOTON_CAPACITY_EPOCH_193.csv').open() as f:
    rows=list(csv.DictReader(f))

def v(n): return np.array([float(r[n]) for r in rows])
z=v('z');x=v('x');H=v('H_s')
out=ROOT/'figures';out.mkdir(exist_ok=True)
for key,filename,title in [
  ('He_II','HEII_POTENTIAL_IONIZING_PHOTON_CUMULATIVE.png','Li II radiative photon capacity: He II threshold'),
  ('H_I','HI_POTENTIAL_IONIZING_PHOTON_CUMULATIVE.png','Li II radiative photon capacity: H I threshold')]:
    ylo=v('potential_'+key+'_photons_min_per_baryon_s')/H
    yhi=v('potential_'+key+'_photons_max_per_baryon_s')/H
    lo=cumulative_simpson(ylo,x=x,initial=0)
    hi=cumulative_simpson(yhi,x=x,initial=0)
    fig,ax=plt.subplots(figsize=(8.5,5.5))
    ax.plot(z,lo,label='min (vacuum, conditional)')
    ax.plot(z,hi,label='max (vacuum, conditional)')
    ax.fill_between(z,lo,hi,alpha=0.15)
    ax.invert_xaxis()
    ax.set_xlabel('redshift z (original saved epochs)')
    ax.set_ylabel('cumulative threshold-capable photons / baryon')
    ax.set_title(title)
    ax.legend(); fig.tight_layout();fig.savefig(out/filename,dpi=150);plt.close(fig)
