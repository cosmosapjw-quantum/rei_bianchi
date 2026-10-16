"""Replot deterministic saved study using matplotlib defaults, no style/color locks."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]
s=json.loads((p/'results/duhamel_diagnostics.json').read_text())
rows=s['fixed_work_comparison'];xs=[q['total_slab_evaluations'] for q in rows]
fig,ax=plt.subplots(figsize=(8.7,5.2))
for key,label in [
('cut_relative_survival_error','Event-aligned positive $\\phi_1$'),
('undivided_relative_survival_error','Unsplit positive $\\phi_1$'),
('midpoint_birth_impulse_relative_error','Instantaneous midpoint births')]:
    ax.loglog(xs,[x[key] for x in rows],marker='o',label=label)
ax.set_xlabel('Total source/opacity evaluations (fixed work)')
ax.set_ylabel('Relative survivor error vs analytic-depth Duhamel reference')
ax.set_title('Manufactured HI/HeI/HeII absorption, HeII event at x=0.73')
ax.legend();ax.grid(True,which='both',alpha=.22)
fig.tight_layout();(p/'figures').mkdir(exist_ok=True)
fig.savefig(p/'figures/duhamel_refinement.png',dpi=165)
plt.close(fig)
