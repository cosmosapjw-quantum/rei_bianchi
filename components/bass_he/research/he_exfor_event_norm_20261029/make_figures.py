"""Plot source-locked conditional sharp bounds; no physical event-rate curves."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from exfor_envelope import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractions import Fraction as F
p=rows330(load_source(ROOT/'source/M0475.x4')[0]); L=F(1,200)
xs=np.linspace(0,90,361)
fig,ax=plt.subplots(figsize=(8,4.7))
ax.plot(xs,[float(envelope(p,L,str(x),'lower')) for x in xs],label='Sharp lower envelope')
ax.plot(xs,[float(envelope(p,L,str(x),'upper')) for x in xs],label='Sharp upper envelope')
ax.errorbar([float(x.theta) for x in p],[float(x.value) for x in p],
            yerr=[float(x.stat) for x in p],fmt='o',capsize=3,label='EXFOR 330 MeV, ERR-S')
ax.set(xlabel='CM polar angle (degrees, one hemisphere)',ylabel='differential cross section (nb/sr)',
       title='Conditional 330 MeV angular envelopes (L = 0.005 nb/sr/degree)')
ax.set_xlim(0,90);ax.set_ylim(bottom=0);ax.legend(fontsize=9);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(ROOT/'figures/330MeV_angular_envelopes.png',dpi=180);plt.close(fig)

Lvals=np.linspace(float(F(1,700)),float(F(1,100)),75)
lo=[];hi=[]
for Lx in Lvals:
    # use a 15-digit decimal representation of L; sensitivity plot only.
    b=sharp_bounds(p,format(Lx,'.15g'),45)
    lo.append(float(b['full_sphere_I_lower_nb']));hi.append(float(b['full_sphere_I_upper_nb']))
fig,ax=plt.subplots(figsize=(8,4.7))
ax.plot(Lvals,lo,label='Sharp full-sphere integral lower (nb)')
ax.plot(Lvals,hi,label='Sharp full-sphere integral upper (nb)')
ax.axvline(float(F(3,350)),linestyle=':',label='Central-point minimum L')
ax.set(xlabel='Declared Lipschitz L (nb/sr/degree)',ylabel='Full-sphere angular integral I (nb)',
       title='EXFOR 330 MeV: shape-assumption sensitivity, not a measured total')
ax.set_xlim(min(Lvals),max(Lvals));ax.legend(fontsize=8);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(ROOT/'figures/sharp_total_vs_L.png',dpi=180);plt.close(fig)
