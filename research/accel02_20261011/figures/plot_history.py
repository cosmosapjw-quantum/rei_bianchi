#!/usr/bin/env python3
"""Render saved actual native outputs; never execute a solver or certify convergence."""
import json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
source=HERE.parent/'n2/evidence/EVENT_COUPLED002/RESULT.json'
d=json.loads(source.read_text());h=d['history'];z=np.array([r['z'] for r in h])
def col(k):return np.array([r[k] for r in h])
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.22,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,2,figsize=(11,7.7),sharex=True)
colors=['#186FAF','#E48B1C','#8A52A1']
for key,label,c in zip(['xHII','xHeII','xHeIII'],['H II','He II','He III'],colors):axs[0,0].plot(z,col(key),label=label,color=c,lw=2)
axs[0,0].set(ylabel='Ionic fraction',ylim=(-.015,1.035));axs[0,0].legend(frameon=False,ncol=3)
axs[0,1].plot(z,col('T_K'),color='#B64241',lw=2);axs[0,1].set(ylabel='Gas temperature [K]')
for key,label,c in zip(['GammaHI_s','GammaHeI_s','GammaHeII_s'],['H I','He I','He II'],colors):axs[1,0].semilogy(z,col(key),color=c,lw=1.8,label=label)
axs[1,0].set(ylabel=r'Photoionization rate $\Gamma$ [s$^{-1}$]');axs[1,0].legend(frameon=False,ncol=3)
for key,label,c in [('energy_ledger_scaled','Energy / initial energy','#197E69'),('number_ledger_scaled','Photon number / initial H density','#D36A30')]:
 v=np.abs(col(key));axs[1,1].semilogy(z,np.ma.masked_equal(v,0),label=label,color=c,lw=1.6)
axs[1,1].axhline(1e-9,color='#3E4248',ls='--',lw=1,label='Frozen bound: $10^{-9}$')
axs[1,1].set(ylabel='Absolute conservation residual',ylim=(1e-16,3e-9));axs[1,1].legend(frameon=False,fontsize=8,loc='lower right')
for ax in axs.flat:ax.set_xlim(15.9,4)
for ax in axs[1]:ax.set_xlabel(r'Mean-scale-factor redshift $z_a$')
fig.suptitle('Native H/He + thermal + photon evolution over 1.27 Gyr',fontsize=16,x=.07,ha='left',y=.99)
fig.text(.07,.938,'Conditional FLRW | HM12 10–50,000 eV | Case A | 128 energy × 2 angular nodes',fontsize=10)
fig.text(.07,.018,'Temporal refinement and conservation accepted for this finite grid. Spectral convergence pending.\nHomogeneous ionic fractions; CR/RCT/secondary cascades OFF; prescribed isotropic CMB bath.',fontsize=9,color='#50545A')
fig.tight_layout(rect=(0,.07,1,.925));fig.savefig(HERE/'NATIVE_GRID_DIAGNOSTIC_128.png',dpi=170);fig.savefig(HERE/'NATIVE_GRID_DIAGNOSTIC_128.svg');plt.close(fig)
svg=HERE/'NATIVE_GRID_DIAGNOSTIC_128.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
meta={'source':str(source.relative_to(HERE.parent)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sample_count':len(h),'plotter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'finite-grid conditional history; not a continuum-converged prediction','solver_executions':0,'masked_zeros':'exact-zero residuals omitted only from log plot; original data unchanged','last_epoch':h[-1]}
(HERE/'FIGURE_PROVENANCE.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'rendered':str(HERE/'NATIVE_GRID_DIAGNOSTIC_128.png'),'source_sha256':meta['sha256'],'sample_count':len(h)}))
