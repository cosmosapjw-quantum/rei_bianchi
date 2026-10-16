"""Plot saved B/C outputs only; does not integrate or change scientific evidence."""
import time,json
from pathlib import Path
start=time.perf_counter()
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
h=np.genfromtxt(ROOT/'evidence/be_kinetics_history.csv',delimiter=',',names=True,deletechars='')
p=np.genfromtxt(ROOT/'evidence/decay_neutrino_profile.csv',delimiter=',',names=True,deletechars='')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
fig,ax=plt.subplots(1,2,figsize=(10.8,4.3))
for name,label,color in [('x_Be4',r'$^7$Be$^{4+}$','#27619d'),('x_Be3',r'$^7$Be$^{3+}$','#b76b18'),('x_Li3',r'$^7$Li$^{3+}$ (daughter)','#2a7f62')]:
    ax[0].plot(h['z'],np.ma.masked_less_equal(h[name],0),label=label,color=color,lw=1.7)
ax[0].set(xscale='log',yscale='log',xlim=(100000,10000),ylim=(1e-10,1.4),xlabel='Redshift z',ylabel='Fraction of initial donor $^7$Be',title='(a) Early-epoch conversion')
ax[0].legend(loc='lower left',frameon=False); ax[0].grid(alpha=.2,which='major')
for name,label,color in [('ground','Ground-state branch (0.896)','#7546a0'),('excited','Excited-state branch (0.104)','#bf563c')]:
    ax[1].plot(p[name+'_E_eV'],p[name+'_q_cm-3_eV-1'],label=label,color=color,lw=1.7)
ax[1].set(xlim=(5,45),xlabel='Present neutrino energy (eV)',ylabel=r'$dn_\nu/dE$ (cm$^{-3}$ eV$^{-1}$)',title='(b) Rate-derived neutrino spectra')
ax[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0)); ax[1].legend(frameon=False); ax[1].grid(alpha=.2)
fig.subplots_adjust(left=.085,right=.985,wspace=.29,bottom=.24,top=.88)
fig.text(.085,.065,'Specified FLRW trace-kinetic model; frozen ionized donor bath and approximate bound EC rates.\nPaper-line, freely streaming ultrarelativistic neutrinos; all propagated flavors summed. No heat-deposition prediction.',fontsize=9)
for ext in ('png','pdf'): fig.savefig(ROOT/f'evidence/BE_DECAY_SPECTRA.{ext}')
plt.close(fig)
(ROOT/'code/laneC/raw/plot_timing.json').write_text(json.dumps({'plot_only_wall_time_s':time.perf_counter()-start,'matplotlib':matplotlib.__version__,'new_numerical_run':False},indent=2)+'\n')
