#!/usr/bin/env python3
"""Original-source-data derived science figures; no decorative graphics."""
from pathlib import Path
import sys,numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).parent))
import compute_theory as t
root=Path(__file__).resolve().parents[1];fig=root/'figures';fig.mkdir(exist_ok=True)
with __import__('zipfile').ZipFile(t.CURTIN_ZIP) as z:
    data=[t.table(z,n+'.1') for n in t.SHELL_IDS]+[t.table(z,'TICS.1')]
E=np.linspace(39.5,61,1000)
plt.figure(figsize=(9,5.3))
for k in [0,1,2,3,9]:
 a=data[k]
 s=np.interp(E,a[:,0],a[:,1],left=0,right=np.nan)
 s=np.where(E<t.calc_thresholds()[k],0,s)
 plt.plot(E,np.maximum(s,1e-7),label=t.HEII_NAMES[k])
plt.yscale('log');plt.ylim(1e-6,1);plt.xlim(39.5,61)
plt.xlabel('Incident electron kinetic energy E [eV]')
plt.ylabel(r'Curtin CCC integrated cross section [$a_0^2$]')
plt.title('Ground-state He II: original published n-summed channels')
plt.legend(ncol=2,fontsize=8);plt.grid(True,alpha=.25)
plt.tight_layout()
for fmt in ['png','svg']:plt.savefig(fig/('HEII_GROUND_ORIGINAL_CCC_SIGMA.'+fmt),dpi=160)
plt.close()
df=pd.read_csv(root/'results/HeII_16CHANNEL_ARRIVAL_192.csv')
plt.figure(figsize=(9,5.3))
for k in ['high','mean','low']:
    v=df['HeII_any_'+k+'_per_b'].to_numpy()
    plt.plot(df.z_low,np.maximum(v,1e-39),label=f'He II first-event {k}',lw=1.7)
plt.yscale('log');plt.xlabel('Redshift z of frozen BASS interval end');plt.ylabel('First selected He II collision events / original baryon')
plt.title('Conditional 16-channel first event: source moment enclosure')
plt.legend(fontsize=8);plt.grid(True,alpha=.25)
plt.tight_layout()
for fmt in ['png','svg']:plt.savefig(fig/('HEII_SOURCE_FIRST_EVENT_192.'+fmt),dpi=160)
plt.close()
