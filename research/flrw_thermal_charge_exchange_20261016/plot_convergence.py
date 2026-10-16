#!/usr/bin/env python3
"""Render saved C7 arrays only; never import or execute thermal solver."""
import json
from pathlib import Path
import time

root=Path(__file__).resolve().parent
start=time.perf_counter()
receipt={'scientific_solver_runs':0,'input':'coding_evidence/C7_results.json'}
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data=json.loads((root/'coding_evidence/C7_results.json').read_text())
    rows=data['fixed_heun_refinement']
    dt=[r['step_s'] for r in rows]
    error=[r['absolute_error_cm3'] for r in rows]
    guide=[error[-1]*(x/dt[-1])**2 for x in dt]
    with plt.rc_context({'font.size':10,'axes.spines.top':False,'axes.spines.right':False}):
        fig,ax=plt.subplots(figsize=(6.4,4.4),layout='constrained')
        ax.loglog(dt,error,'o-',color='#175b8f',linewidth=1.7,markersize=6,label='Fixed Heun; cached exact reference')
        ax.loglog(dt,guide,'--',color='#777777',linewidth=1.3,label=r'$\Delta t^2$ guide')
        ax.set(xlabel=r'Time step $\Delta t$ (s)',ylabel=r'Endpoint extent error $|\xi-\xi_{exact}|$ (cm$^{-3}$)',
               title='Manufactured isolated H/D thermal CX')
        ax.grid(True,which='both',alpha=.18)
        ax.legend(frameon=False,fontsize=8.5)
        fig.savefig(root/'CONVERGENCE.png',dpi=220)
        fig.savefig(root/'CONVERGENCE.svg')
        plt.close(fig)
    receipt.update(status='RENDERED',matplotlib=matplotlib.__version__,outputs=['CONVERGENCE.png','CONVERGENCE.svg'],
        scope='Saved synthetic fixed-volume component fixture; no cosmological history')
except Exception as exc:
    receipt.update(status='OPTIONAL_RENDER_SKIPPED',error=repr(exc))
receipt['render_wall_seconds']=time.perf_counter()-start
(root/'coding_evidence/C10_PLOT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
