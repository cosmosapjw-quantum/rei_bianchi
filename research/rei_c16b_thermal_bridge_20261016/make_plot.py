"""Create one reproducible observed convergence plot from raw JSON."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
records=json.loads((r/'evidence'/'study_results.json').read_text())['refinement']
fig,ax=plt.subplots(figsize=(8,5))
xs=np.array([v['substeps'] for v in records])
ys=np.array([v['error_max_abs'] for v in records])
ax.loglog(xs,ys,'o-',label='Split vs. independent DOP853')
ax.loglog(xs,ys[-1]*(xs[-1]/xs)**2,ls=':',label='Second-order reference')
ax.set_xlabel('Reaction substeps')
ax.set_ylabel('Max absolute state difference')
ax.set_title('H/He photo + synthetic RR/CI: time refinement')
ax.grid(True,which='both',alpha=.3)
ax.legend(loc='best')
fig.tight_layout()
fig.savefig(r/'figures'/'manufactured_reaction_refinement.png',dpi=170)
plt.close(fig)
print(r/'figures'/'manufactured_reaction_refinement.png')