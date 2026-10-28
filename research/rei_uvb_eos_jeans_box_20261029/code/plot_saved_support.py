"""Presentation-only: the 2D affine image of the source-bounded box.
Does not execute scientific exact-arithmetic core, old IGM/ODE code or UVB rates.
"""
from pathlib import Path
from itertools import product
import json,matplotlib
matplotlib.use('Agg')
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'source/FROZEN_BB13_SUPPORT_INPUT.json').read_text())
S=json.loads((R/'results/EXACT_SUPPORT.json').read_text())
z=np.array(D['z']);C=np.array(D['covariance_dex_squared']);X=np.column_stack((np.ones(7),z-3.6))
L=np.linalg.cholesky(C);W=np.linalg.solve(L.T,np.linalg.solve(L,X));A=np.linalg.solve(X.T@W,W.T)
r=np.array(D['observed_dex'])-np.array(D['template_dex']);v=np.array(D['eos_response_dex'])
lo=np.array(D['jeans_smoothing_lower_dex']);hi=np.array(D['jeans_smoothing_upper_dex'])
verts=np.asarray([A@(r+t*v+np.where(bits,hi,lo)) for t in (-1,1) for bits in product((0,1),repeat=7)])
hull=ConvexHull(verts)
nominal=A@r;seg=np.stack((nominal-A@v,nominal+A@v),axis=0)
fig,ax=plt.subplots(figsize=(9.0,5.8),dpi=140)
ax.fill(verts[hull.vertices,0],verts[hull.vertices,1],alpha=.16,label='EOS + per-bin Jeans outer zonotope')
closed=np.r_[hull.vertices,hull.vertices[0]]
ax.plot(verts[closed,0],verts[closed,1],linewidth=1.7)
ax.plot(seg[:,0],seg[:,1],marker='s',linewidth=2,label='EOS-only line (Jeans fixed at 0)')
ax.scatter([nominal[0]],[nominal[1]],marker='o',s=55,zorder=5,label='PR252 nominal GLS')
ax.set_xlabel('beta: log10 HI rate amplitude [dex]')
ax.set_ylabel('kappa: redshift slope [dex / unit z]')
ax.set_title('Conditional BB13 redshift-tilt: exact-envelope vertices')
ax.axhline(0,linewidth=.7,linestyle=':')
ax.grid(True,alpha=.24)
ax.legend(loc='upper left',fontsize=8)
fig.text(.01,.005,'Printed BB13 Jeans intervals treated as independent bounds; no joint prior, no physical Bianchi tilt / L4 / model-fit uncertainty.',fontsize=8)
fig.tight_layout(rect=[0,.04,1,1])
P=R/'results/ZONOTOPE_SUPPORT.png';fig.savefig(P);plt.close(fig)
print(json.dumps({'image':str(P.relative_to(R)),'bytes':P.stat().st_size,'n_corners':len(verts),'n_hull_vertices':len(hull.vertices),'bounds_source':S['nuisance_support']['kappa_min']+'..'+S['nuisance_support']['kappa_max']}))
