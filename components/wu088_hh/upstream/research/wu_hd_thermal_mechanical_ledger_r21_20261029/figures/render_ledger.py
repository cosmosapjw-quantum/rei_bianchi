"""Synthetic source-locked caloric/pressure-work diagnostics; never plot physical Q."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from research.wu_hd_source_bound_r18_20261029.src.native_rates import load_native_grid
from research.wu_hd_source_grid_r20_20261029.src.grid_exposure import Segment
from research.wu_hd_thermal_mechanical_ledger_r21_20261029.src.thermal_ledger import build_ledger, K_B_J_PER_K

root=Path(__file__).resolve().parents[1]
pdf=Path(__file__).resolve().parents[3]/'ORIGINAL_SOURCES/GL2022_CSIC_supplement.pdf'
grid=load_native_grid(pdf)
source=(1e6,1e6,0,0)
rows=[]
for theta in np.linspace(-2e-11,2e-11,101):
    flow,l=build_ledger(grid,source,[Segment(105,1e10,float(theta))])
    rows.append([float(theta), l.reaction_extent_events_per_ref_m3,
                 l.bath_known_intercept_J_per_ref_m3,
                 l.pressure_work_by_material_J_per_ref_m3])
a=np.array(rows)
fig,ax=plt.subplots(figsize=(5.7,3.5))
ax.plot(a[:,0]*1e11,a[:,1]/1e6,linewidth=1.6)
ax.set(xlabel=r'Prescribed expansion $\Theta$ ($10^{-11}\,{\rm s}^{-1}$)',
       ylabel=r'Formal $Q$ coefficient $\xi$ ($10^6$ events/ref. m$^3$)',
       title='105 K source-grid one-channel exposure (synthetic)')
fig.tight_layout()
p1=root/'figures'/'R21_EXTENT_COEFFICIENT.png';fig.savefig(p1,dpi=180)
plt.close(fig)
fig,ax=plt.subplots(figsize=(5.7,3.5))
bnorm=a[:,2]/(2e6*K_B_J_PER_K*105)
ax.plot(a[:,0]*1e11,bnorm,linewidth=1.6)
ax.axhline(0,linestyle='--',linewidth=.8)
ax.set(xlabel=r'Prescribed expansion $\Theta$ ($10^{-11}\,{\rm s}^{-1}$)',
       ylabel=r'Known bath coefficient / $N_{\rm tot}k_B T$',
       title='Isothermal pressure work, not physical reaction heat')
fig.tight_layout()
p2=root/'figures'/'R21_BATH_INTERCEPT.png';fig.savefig(p2,dpi=180)
plt.close(fig)
res={'schema':'wu.r21.figure_data.v1','points':len(rows),'source_pdf_sha256':grid.source_sha256,
     'theta_s_range':[-2e-11,2e-11],'extent_at_middle':a[50,1],
     'bath_intercept_at_middle':a[50,2], 'normalized_bath_min_max':[float(bnorm.min()),float(bnorm.max())],
     'normalizer_J_ref_m3':2e6*K_B_J_PER_K*105,
     'physical_Q_J':None,'figure_files':[p1.name,p2.name]}
(root/'results'/'FIGURE_AUDIT.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
