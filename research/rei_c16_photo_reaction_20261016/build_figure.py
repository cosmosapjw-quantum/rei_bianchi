from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'study_results.json').read_text())
a=r['refinements']
steps=np.array([x['reaction_substeps'] for x in a],dtype=float)
errors=np.array([x['max_state_abs_difference'] for x in a])
fit=np.polyfit(np.log(steps[-4:]),np.log(errors[-4:]),1)
fig,ax=plt.subplots(figsize=(7.2,4.6),dpi=170)
ax.loglog(steps,errors,'o-',label='Independent DOP853 state difference')
ax.loglog(steps,errors[-1]*(steps[-1]/steps)**2,'--',label=r'$\propto N_{\mathrm{sub}}^{-2}$ reference')
ax.set(xlabel='Symmetric pair-subflow subdivisions',ylabel='Maximum absolute state difference',
       title='Conditional H/He photoionization: time refinement')
ax.grid(True,which='both',alpha=.25)
ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(ROOT/'reaction_refinement.png')
plt.close(fig)
print('log_slope_last_four',fit[0])
report=json.loads((ROOT/'study_results.json').read_text());report['measured_loglog_slope_last_four']=float(fit[0]);(ROOT/'study_results.json').write_text(json.dumps(report,indent=2)+'\n')
