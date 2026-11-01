"""Plot source-owned finite 46,080-node diagnostic figures, no inferred spatial weighting."""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--csv',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
d=pd.read_csv(a.csv,compression='gzip')
fig,ax=plt.subplots(figsize=(7.7,5.0))
ax.plot(d.T_K.to_numpy(),d.E_ion_over_U_thermal.to_numpy(),'.',markersize=1.2,alpha=.25)
ax.set_xscale('log');ax.set_yscale('log')
ax.set_xlabel('Original accepted-parent $T_\\mathrm{gas}$ (K)')
ax.set_ylabel(r'$u_{\rm ion}/u_{\rm th}$ per H nucleus')
ax.set_title('Source-owned tick 160, 46,080 nodes; not an evolved new interval')
fig.tight_layout()
for ext in ('png','svg'):fig.savefig(a.out/('SOURCE_THERMOCHEMICAL_ENERGY_RATIO.'+ext),dpi=170)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7.7,5.0))
s=d.parent_logT_width_from_source.to_numpy();m=d.parent_logT_width_independent_U_xe.to_numpy()
ax.plot(s,m,'.',markersize=1.1,alpha=.18)
lo=np.min(s[s>0]);hi=max(np.max(m),np.max(s))
ax.plot([lo,hi],[lo,hi],linestyle='--',linewidth=1,label='Equal widths')
ax.set_xscale('log');ax.set_yscale('log');ax.legend()
ax.set_xlabel('Parent $\\Delta\\ln T$, direct stored interval')
ax.set_ylabel('Parent $\\Delta\\ln T$, independent $U$ and $x_e$ interval reconstruction')
ax.set_title('Correlation-loss diagnostic, not the local-error acceptance test')
fig.tight_layout()
for ext in ('png','svg'):fig.savefig(a.out/('SOURCE_CORRELATION_LOSS_WIDTH.'+ext),dpi=170)
plt.close(fig)
