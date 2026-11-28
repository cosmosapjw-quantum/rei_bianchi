"""Conditional invariant-kinematic figures, not physical rate plots."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from reciprocity import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

E=np.linspace(150,360,300)
T=np.array([float(T_matching(format(x,'.12g'))) for x in E])
fig,ax=plt.subplots(figsize=(8.2,4.8))
ax.plot(E,T,label=r'Invariant $s$ matching $T_d(E_\gamma)$')
for energy in [213,330]:
 ax.plot([energy],[float(T_matching(energy))],'o')
 ax.annotate(f'{energy} MeV photon  ↔  {float(T_matching(energy)):.3f} MeV d',
             (energy,float(T_matching(energy))),
             xytext=((8,10) if energy==213 else (-12,-23)),
             textcoords='offset points',ha=('left' if energy==213 else 'right'),fontsize=9)
ax.axhline(376,linestyle=':',label='Silverman inverse measurement: $T_d=376$ MeV')
ax.set(xlabel=r'$E_\gamma$ in $^4$He target rest (MeV)',ylabel=r'$T_d$ on stationary d (MeV)',
       title='Same-invariant-energy mapping, not an interpolated cross section')
ax.legend(loc='upper left',fontsize=8);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(ROOT/'results/energy_matching.png',dpi=175);plt.close(fig)

R1=np.array([float(reciprocity_ratio(format(x,'.12g'),ORDERED)) for x in E])
fig,ax=plt.subplots(figsize=(8.2,4.8))
ax.plot(E,R1,label='Inverse / forward ordered or inclusive-D')
ax.plot(E,2*R1,label='Inverse / forward full-sphere event density')
for energy in [213,330]:ax.axvline(energy,linestyle=':',alpha=.5)
ax.set(xlabel=r'$E_\gamma$ in $^4$He target rest (MeV)',ylabel='Reciprocal differential cross-section ratio',
       title='Time-reversal kinematics: two explicit, unadmitted conventions')
ax.legend(fontsize=8);ax.grid(alpha=.25)
fig.tight_layout();fig.savefig(ROOT/'results/reciprocity_factors.png',dpi=175);plt.close(fig)
