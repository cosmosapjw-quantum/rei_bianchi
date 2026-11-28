from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent/'src'))
from conditional_pressure_trace import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
m0=F(24377,71485)
xs=[F(j,400) for j in range(401)]
gap=[1000*float(moment_trace_bounds(m)['gap_MeV_per_event']) for m in xs]
g0=1000*float(moment_trace_bounds(m0)['gap_MeV_per_event'])
fig,ax=plt.subplots(figsize=(8,4.65))
ax.plot([float(x) for x in xs],gap,label='Jensen-secant gap, universal even-law class')
ax.scatter([float(m0)],[g0],marker='o',zorder=4,label='frozen FULL witness m2')
ax.set(xlabel=r'$m_2=\mathbb{E}[\mu^2]$',ylabel='Event pressure trace gap (10$^{-3}$ MeV)',title='Finite-mass pressure trace is not fixed by angular m2')
ax.legend(loc='lower center',fontsize=9)
ax.grid(alpha=0.25)
fig.tight_layout()
p=Path(__file__).parent/'results'/'pressure_trace_moment_gap.png'
fig.savefig(p,dpi=170)
print('PLOT_CHECK',p,'sample_gap_mMeV',g0,'max_mMeV',max(gap))
