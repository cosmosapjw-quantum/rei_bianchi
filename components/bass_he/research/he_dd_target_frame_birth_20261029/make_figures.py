"""Diagnostic only: exact kinematic daughter support, no measured rate."""
from pathlib import Path
import math,sys
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from birth_ledger import event_ledger,threshold
Es=np.linspace(float(threshold())+1e-8,350,301)
means=[]; splits=[]
for E in Es:
 a=event_ledger(str(E))
 means.append(float(a['single_D_pair_mean_kinetic_MeV']))
 splits.append(math.sqrt(float(a['splitting_coefficient_squared_MeV2'])))
means=np.asarray(means);splits=np.asarray(splits)
fig,ax=plt.subplots(figsize=(7.6,4.6))
ax.plot(Es,means,label='Two-D marginal mean per event')
ax.plot(Es,means+splits,ls='--',label='Kinematic upper K')
ax.plot(Es,means-splits,ls='--',label='Kinematic lower K')
ax.fill_between(Es,means-splits,means+splits,alpha=.15)
for e in (213,330):ax.axvline(e,alpha=.35,ls=':')
ax.set(xlabel=r'$E_\gamma$ (MeV), in alpha-target rest frame',ylabel=r'$K_D$ (MeV)',title='Correlated two-D birth: kinematics, not event rate')
ax.legend(loc='upper left',fontsize=8);ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(ROOT/'figures/daughter_kinematic_support.png',dpi=190)
plt.close(fig)
