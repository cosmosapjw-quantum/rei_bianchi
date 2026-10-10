from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
fig,axs=plt.subplots(2,2,figsize=(10,7),constrained_layout=False)
for n,color,style in [(400,'#d97706','--'),(800,'#3b82a0',':'),(1600,'#243b67','-')]:
    d=json.loads((ROOT/f'loop2/evidence/peebles_{n}.json').read_text())
    z=np.array(d['z_edges']);zm=np.array(d['midpoint_z']);dt=np.diff(d['time_edges_seconds'])
    axs[0,0].plot(z,d['x_edges'],style,color=color,lw=1.5,label=f'{n} cells')
    axs[0,1].plot(zm,np.array(d['midpoint_ne_m3'])/1e8,style,color=color,lw=1.5)
    axs[1,0].plot(z,np.array(d['optical_depth'])-.2,style,color=color,lw=1.5)
    axs[1,1].plot(zm,np.array(d['interval_probability'])/dt*1e13,style,color=color,lw=1.5)
ref=np.genfromtxt(ROOT/'loop2/evidence/peebles_1600.csv',delimiter=',',names=True)
axs[0,0].plot(ref['z'][::40],ref['x_reference'][::40],'o',ms=2.8,mfc='white',mec='#121826',label='Independent DOP853')
axs[0,0].set_ylabel(r'Hydrogen ionized fraction $x_{\rm HII}$')
axs[0,1].set_ylabel(r'Proper $n_e$ [$10^8\,\mathrm{m}^{-3}$]')
axs[1,0].set_ylabel(r'Remaining depth $\tau(z)-\tau_{\rm tail}$')
axs[1,1].set_ylabel(r'Cell mean $P_i/\Delta t_i$ [$10^{-13}\,\mathrm{s}^{-1}$]')
for ax in axs.flat:
    ax.set_xlim(1200,1000);ax.set_xlabel('Redshift z (time increases to the right)');ax.grid(alpha=.17)
axs[0,0].legend(frameon=False,fontsize=9)
fig.suptitle('REC → REI → BASS: expanding Peebles / visibility benchmark',fontsize=15,y=.985)
fig.text(.5,.925,'Prescribed matter-only FLRW • pure H • one temperature • source profile: HYREC2 TLA, fudge = 1',ha='center',fontsize=10)
fig.text(.075,.018,'Validation result, not an EoR prediction. Initial x = 0.8; observer tail = 0.2; RCT OFF.\n'
         'Finest x error = 1.96×10⁻¹¹; relative depth error = 3.58×10⁻⁷. No continuum or finite-T certificate.',fontsize=9,color='#485260')
fig.subplots_adjust(left=.09,right=.98,top=.87,bottom=.14,hspace=.34,wspace=.30)
for ext in ['png','pdf']:fig.savefig(OUT/f'REC_REI_BASS_EXPANDING_VALIDATION.{ext}')
