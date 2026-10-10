"""Replot published F08 curves; no private data, solver or scientific replay."""
from pathlib import Path
import argparse,gzip
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
parser=argparse.ArgumentParser();parser.add_argument('run_dir',type=Path);args=parser.parse_args();OUT=args.run_dir
data={label:np.loadtxt(gzip.open(OUT/'curves'/(label+'.csv.gz'),'rt'),delimiter=',',skiprows=1) for label in ['T0_FLRW','T0_BI','T0_EPS_HALF']}
fig,axes=plt.subplots(3,2,figsize=(11,10),sharex=True)
for geo,color in [('FLRW','#174A7E'),('BI','#B64624')]:
 a=data['T0_'+geo];t=a[:,0]/1e13
 for ax,column,title in [(axes[0,0],1,'H ionized fraction'),(axes[0,1],4,'Temperature (K)'),(axes[1,0],5,'Gamma HI (s^-1)'),(axes[1,1],8,'Photons per H')]:ax.plot(t,a[:,column],color=color,label=geo,lw=1.3);ax.set_title(title)
f=data['T0_FLRW'];b=data['T0_BI'];e=data['T0_EPS_HALF'];assert np.array_equal(f[:,0],b[:,0]) and np.array_equal(f[:,0],e[:,0]);t=f[:,0]/1e13
axes[2,0].plot(t,b[:,1]-f[:,1],label='epsilon=.01',color='#B64624');axes[2,0].plot(t,e[:,1]-f[:,1],label='epsilon=.005',color='#548C2F');axes[2,0].set_title('Bianchi - FLRW xHII (discrete)')
for label,color in [('T0_FLRW','#174A7E'),('T0_BI','#B64624')]:
 a=data[label];axes[2,1].plot(a[:,0]/1e13,a[:,21],label=label,color=color)
axes[2,1].axhline(1e-12,color='grey',ls='--',lw=.8);axes[2,1].set_yscale('log');axes[2,1].set_title('Per-step ledger residual (gate 1e-12)')
for ax in axes.flat:ax.grid(alpha=.2);ax.legend(fontsize=8);ax.ticklabel_format(axis='x',style='plain')
for ax in axes[-1]:ax.set_xlabel('Elapsed time / 1e13 s')
fig.suptitle('Prescribed homogeneous S0 - matched atomic realization\nCase A HG + DR + primary line source; HH/RCT/CR OFF; physical admission HOLD',fontsize=12);fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(OUT/'paired_history.png',dpi=180);fig.savefig(OUT/'paired_history.pdf');plt.close(fig)
